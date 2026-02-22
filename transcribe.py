#!/usr/bin/env python3
"""
ChatGPT Transcribe API client.

Usage:
    python3 transcribe.py <audio_file>

Reads headers (including Authorization Bearer token and cookies)
from request-header.txt in the same directory.
"""

import sys
import os
import json
import requests

API_URL = "https://chatgpt.com/backend-api/transcribe"
HEADERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".request-header.txt")

def load_headers(headers_file: str) -> tuple[dict[str, str], dict[str, str]]:
    """Load headers from request-header.txt.

    Format: alternating lines of header-name and header-value.
    Returns (headers_dict, cookies_dict).
    """
    if not os.path.exists(headers_file):
        print(f"Error: Headers file not found: {headers_file}")
        sys.exit(1)

    with open(headers_file, "r") as f:
        lines = [line.rstrip() for line in f if line.strip()]

    headers = {}
    cookies = {}

    for i in range(0, len(lines) - 1, 2):
        name = lines[i].strip()
        value = lines[i + 1].strip()

        if name == "cookie":
            # Parse cookie string into dict
            for pair in value.split(";"):
                pair = pair.strip()
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    cookies[k.strip()] = v.strip()
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


def transcribe(audio_path: str) -> dict:
    """Send audio file to ChatGPT transcribe API and return the result."""
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        sys.exit(1)

    headers, cookies = load_headers(HEADERS_FILE)
    content_type = get_content_type(audio_path)
    filename = os.path.basename(audio_path)

    print(f"Transcribing: {audio_path}")
    print(f"Content-Type: {content_type}")
    print(f"Loaded {len(headers)} headers, {len(cookies)} cookies")
    has_auth = any(k.lower() == "authorization" for k in headers)
    print(f"Authorization: {'Yes' if has_auth else 'MISSING!'}")
    print()

    with open(audio_path, "rb") as f:
        files = {
            "file": (filename, f, content_type),
        }
        response = requests.post(
            API_URL,
            headers=headers,
            cookies=cookies,
            files=files,
        )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        print(f"Error: {response.text}")
        return {"error": response.text, "status_code": response.status_code}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <audio_file>")
        print(f"Example: python3 {sys.argv[0]} Test/test.mp3")
        sys.exit(1)

    result = transcribe(sys.argv[1])
    print()
    # print("Full response:")
    # print(json.dumps(result, ensure_ascii=False, indent=2))
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(result["text"])
    print("Done, the result is written to output.txt")
