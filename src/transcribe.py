#!/usr/bin/env python3
"""
Transcription module using faster-whisper.
"""

import os
from faster_whisper import WhisperModel

# Use the configuration from src/faster-whisper.py
MODEL_SIZE = "medium"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"

# Initialize model at module level so it can be pre-loaded
_model = None


def get_model():
    """Lazy initialization of the Whisper model."""
    global _model
    if _model is None:
        # Check if CUDA is available, otherwise fallback to CPU
        # But per user request and snippet, we target CUDA/FP16
        try:
            _model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
        except Exception:
            # Fallback to CPU if CUDA fails (e.g. no GPU or driver issues)
            _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


def transcribe(audio_path: str) -> dict:
    """
    Transcribe audio file using faster-whisper and return the full text.
    Returns a dictionary to maintain compatibility with the rest of the project.
    """
    if not os.path.exists(audio_path):
        return {"error": f"Audio file not found: {audio_path}"}

    try:
        model = get_model()
        segments, info = model.transcribe(audio_path, beam_size=5)

        # Collect all segments and join them into a single string
        # segment.text usually contains leading/trailing whitespace
        full_text = "".join(segment.text for segment in segments).strip()

        return {"text": full_text}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <audio_file>")
        sys.exit(1)

    result = transcribe(sys.argv[1])
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(result["text"])
