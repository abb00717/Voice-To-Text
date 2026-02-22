#!/usr/bin/env python3
"""
main.py - GNOME hotkey toggle for voice-to-text.

Usage:
    Bind this script to a GNOME keyboard shortcut.
    Press the shortcut once to START recording.
    Press it again to STOP recording, transcribe, beautify, and paste at cursor.

Toggle mechanism:
    - Uses a lock file (/tmp/audio-to-text.pid) to track state.
    - First invocation:  no lock file  → start recording, write PID.
    - Second invocation: lock file exists → send SIGUSR1, exit.
    - Recording process catches SIGUSR1, runs the full pipeline, then cleans up.
"""

import os
import sys
import signal
import subprocess
import threading
import tempfile

# Resolve paths relative to this script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCK_FILE = os.path.join(tempfile.gettempdir(), "audio-to-text.pid")
RECORDING_PATH = os.path.join(SCRIPT_DIR, "recording.wav")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "output.txt")


def notify(message: str, urgency: str = "normal") -> None:
    """Send a desktop notification via notify-send."""
    subprocess.Popen(
        ["notify-send", "-u", urgency, "-a", "Audio-to-Text", message],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def paste_text(text: str) -> None:
    """Copy text to clipboard and simulate Ctrl+V to paste at cursor."""
    # Copy to Wayland clipboard
    proc = subprocess.Popen(
        ["wl-copy"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    proc.communicate(input=text.encode("utf-8"))

    # Small delay to ensure clipboard is ready, then simulate Ctrl+V
    import time
    time.sleep(0.1)

    subprocess.Popen(
        ["wtype", "-M", "ctrl", "-k", "v"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


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
    """Run transcribe -> beautify -> paste pipeline."""
    from transcribe import transcribe
    from beautify import beautify_file

    # Transcribe
    notify("Transcribing...")
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

    # Beautify (half-width → full-width punctuation)
    beautified = beautify_file(OUTPUT_PATH)

    # Paste at cursor
    paste_text(beautified)
    notify("Done!")


def start_recording() -> None:
    """Start mode: record audio and wait for SIGUSR1 to stop."""
    from record import record

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

    if pid is not None and is_process_alive(pid):
        # Lock file exists and process is alive -> stop mode
        stop_recording()
    else:
        # No lock file or stale -> start mode
        if pid is not None:
            remove_lock()  # Clean up stale lock
        start_recording()


if __name__ == "__main__":
    main()
