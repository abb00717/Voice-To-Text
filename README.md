# Audio-To-Text

[繁體中文](docs/traditional-chinese.md) | [English](docs/english.md)

---

A highly efficient voice-to-text tool based on the ChatGPT Web API, specifically designed for Linux (GNOME) environments. It enables a seamless "Record -> Transcribe -> Beautify -> Copy to Clipboard" workflow with a simple hotkey toggle.

## Prerequisites

This project uses [uv](https://github.com/astral-sh/uv) for Python environment and dependency management.

### 1. Install System Dependencies

Ensure your system has `portaudio` (for recording) and `wl-clipboard` (for clipboard operations on Wayland) installed:

```bash
# For Debian/Ubuntu
sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev wl-clipboard
```

### 2. Configure API Headers

To call the ChatGPT transcription API, you need to manually capture the Request Headers after logging in:

1. Open your browser and log in to [ChatGPT](https://chatgpt.com).
2. Open Developer Tools (F12) and go to the **Network** tab.
3. Record a short voice command on the page to trigger the `transcribe` API.
4. Find the `transcribe` request and copy its **Request Headers** (excluding headers starting with `:`).
5. Create a file named `.request-header.txt` in the project root. You can use the provided template as a reference, ensuring it includes required fields like `Authorization` and `Cookie`.

### 3. Install Python Dependencies

```bash
uv sync
```

## Usage

### Run Directly

```bash
uv run src/main.py
```

- **First Run**: Starts recording; a notification will appear.
- **Second Run**: Stops recording; the system begins transcription and beautification.
- **Completion**: The result is automatically saved to `output/output.txt` and copied to your clipboard.

### Recommended: Bind to GNOME Hotkey

It is recommended to bind `uv run /path/to/Audio-To-Text/src/main.py` to a system shortcut (e.g., `Ctrl + Alt + T`) for the smootmost experience.

## Project Structure

- `src/main.py`: Main script for toggling recording states and orchestration.
- `src/transcribe.py`: Handles communication with the ChatGPT API.
- `src/beautify.py`: Logic for text beautification and punctuation correction.
- `src/record.py`: Underlying recording implementation.
- `output/`: Directory for temporary audio files and final transcription results.