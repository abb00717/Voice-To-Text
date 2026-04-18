#!/usr/bin/env python3
"""
main.py - GNOME hotkey toggle for voice-to-text.

Usage:
    Bind this script to a GNOME keyboard shortcut.
    Press the shortcut once to START recording.
    Press it again to STOP recording, transcribe, beautify, and copy to clipboard.

Toggle mechanism:
    - Uses a lock file (/tmp/audio-to-text.pid) to track state.
    - First invocation:  start recording, write PID.
    - Second invocation: send SIGUSR1, exit.
    - Runs the full pipeline, then cleans up.
"""

import os
import signal
import subprocess
import sys
import tempfile
import threading
from datetime import datetime

# Resolve paths relative to this script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
LOCK_FILE = os.path.join(tempfile.gettempdir(), "audio-to-text.pid")
RECORDING_PATH = os.path.join(PROJECT_ROOT, "output/recording.wav")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "output/output.txt")


def notify(message: str, urgency: str = "normal") -> None:
    """Send a desktop notification via notify-send."""
    subprocess.Popen(
        ["notify-send", "-u", urgency, "-a", "Audio-to-Text", message],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def copy_text(text: str) -> None:
    """Copy text to clipboard"""
    # Copy to Wayland clipboard
    proc = subprocess.Popen(
        ["wl-copy"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    proc.communicate(input=text.encode("utf-8"))


def create_lock(pid: int) -> None:
    """Write PID to lock file."""
    with open(LOCK_FILE, "w") as f:
        f.write(str(pid))


def read_lock() -> int | None:
    """Read PID from lock file. Returns None if file doesn't exist."""
    try:
        with open(LOCK_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def remove_lock() -> None:
    """Remove lock file."""
    try:
        os.remove(LOCK_FILE)
    except FileNotFoundError:
        pass


def is_process_alive(pid: int) -> bool:
    """Check if a process with the given PID is still running."""
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def run_pipeline() -> None:
    """transcribe -> beautify -> paste pipeline."""
    from beautify import beautify_file
    from transcribe import transcribe

    # Transcribe
    result = transcribe(RECORDING_PATH)

    if "error" in result:
        notify(f"Transcription failed: {result['error']}", urgency="critical")
        return

    text = result.get("text", "")
    if not text:
        notify(" No text recognized.", urgency="normal")
        return

    # Write raw transcription
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    # Beautify
    beautified = beautify_file(OUTPUT_PATH)

    # Paste at cursor
    copy_text(beautified)
    notify("Done!")


def start_recording() -> None:
    """Start mode: record audio and wait for SIGUSR1 to stop."""
    from record import record
    from transcribe import get_model

    # Pre-load the model in the background while user is recording
    threading.Thread(target=get_model, daemon=True).start()

    stop_event = threading.Event()

    def on_stop_signal(sig, frame):
        stop_event.set()

    signal.signal(signal.SIGUSR1, on_stop_signal)

    # Write lock file with our PID
    create_lock(os.getpid())
    notify("Recording...")

    try:
        record(RECORDING_PATH, stop_event)
        run_pipeline()
    except Exception as e:
        notify(f"Error: {e}", urgency="critical")
    finally:
        remove_lock()


def stop_recording() -> None:
    """Stop mode: send SIGUSR1 to the recording process."""
    pid = read_lock()
    if pid is None:
        return

    if not is_process_alive(pid):
        # Stale lock file — clean up
        remove_lock()
        notify("Stale lock file removed. Please try again.")
        return

    os.kill(pid, signal.SIGUSR1)


def main() -> None:
    pid = read_lock()
    global OUTPUT_PATH
    OUTPUT_PATH = os.path.join(
        PROJECT_ROOT, f"output/{datetime.isoformat(datetime.today())}.txt"
    )

    if pid is not None and is_process_alive(pid):
        # If lock file exists, it means the program is running in start mode.
        # So we should stop it.
        stop_recording()
    else:
        # No lock file or stale, so start recording
        if pid is not None:
            remove_lock()  # Clean up stale lock
        start_recording()


if __name__ == "__main__":
    main()
