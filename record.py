"""
record.py - Record audio from microphone using PyAudio.

Provides a `record()` function that records until a threading.Event is set,
then saves the audio as a WAV file.
"""

import wave
import threading
import pyaudio

# Audio parameters optimized for speech recognition
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


def record(output_path: str, stop_event: threading.Event) -> str:
    """Record audio from microphone until stop_event is set.

    Args:
        output_path: Path to save the WAV file.
        stop_event: Threading event — recording stops when this is set.

    Returns:
        The output_path of the saved WAV file.
    """
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

    frames: list[bytes] = []

    try:
        while not stop_event.is_set():
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))

    return output_path


if __name__ == "__main__":
    import signal
    import sys

    out = "recording.wav"
    ev = threading.Event()

    def _on_sigint(sig, frame):
        ev.set()

    signal.signal(signal.SIGINT, _on_sigint)

    print(f"Recording to {out} ... Press Ctrl+C to stop.")
    record(out, ev)
    print(f"Saved: {out}")
