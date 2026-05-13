#!/usr/bin/env python3
"""
Transcription module supporting both ChatGPT API and local faster-whisper fallback.
"""

import os
import sys
import time

import requests
from faster_whisper import WhisperModel

API_URL = "https://chatgpt.com/backend-api/transcribe"
HEADERS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".request-header.txt"
)

# Local model configuration
MODEL_SIZE = "medium"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"

# Initialize model at module level so it can be pre-loaded
_model = None


def load_headers(headers_file: str) -> tuple[dict[str, str], dict[str, str]]:
    """Load headers from request-header.txt."""
    if not os.path.exists(headers_file):
        return {}, {}

    with open(headers_file, "r") as f:
        lines = [line.rstrip() for line in f if line.strip()]

    headers = {}
    cookies = {}

    for i in range(0, len(lines) - 1, 2):
        name = lines[i].strip()
        value = lines[i + 1].strip()

        name_lower = name.lower()
        if name_lower == "cookie":
            for pair in value.split(";"):
                pair = pair.strip()
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    cookies[k.strip()] = v.strip()
        elif name_lower in ("content-length", "content-type"):
            continue
        else:
            headers[name] = value

    return headers, cookies


def get_content_type(filepath: str) -> str:
    """Guess audio MIME type from file extension."""
    ext = os.path.splitext(filepath)[1].lower()
    mime_map = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".webm": "audio/webm",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4",
        ".mp4": "audio/mp4",
        ".flac": "audio/flac",
    }
    return mime_map.get(ext, "audio/mpeg")


def transcribe_api(audio_path: str, max_retries: int = 5) -> dict:
    """Try transcribing via ChatGPT API with retries."""
    if not os.path.exists(HEADERS_FILE):
        return {"error": "Headers file not found"}

    headers, cookies = load_headers(HEADERS_FILE)
    content_type = get_content_type(audio_path)
    filename = os.path.basename(audio_path)

    for attempt in range(max_retries):
        try:
            print(f"API Attempt {attempt + 1}/{max_retries}...")
            with open(audio_path, "rb") as f:
                files = {"file": (filename, f, content_type)}
                response = requests.post(
                    API_URL,
                    headers=headers,
                    cookies=cookies,
                    files=files,
                    timeout=60,
                )

            if response.status_code == 200:
                return response.json()

            print(f"API error ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"API request failed: {e}")

        if attempt < max_retries - 1:
            time.sleep(1)

    return {"error": "API failed after all retries"}


def transcribe(audio_path: str) -> dict:
    """
    Main transcription entry point.
    Tries API first with retries, then falls back to local.
    """
    if not os.path.exists(audio_path):
        return {"error": f"Audio file not found: {audio_path}"}

    # Call API
    return transcribe_api(audio_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <audio_file>")
        sys.exit(1)

    result = transcribe(sys.argv[1])
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(result["text"])
