# Audio-To-Text

[繁體中文](#繁體中文) | [English](#english)

---

## 繁體中文

這是一個基於 ChatGPT Web API 的高效語音轉文字工具，專為 Linux (GNOME) 環境設計。旨在讓使用者透過簡單的快捷鍵切換，即可實現「錄音 -> 轉錄 -> 美化 -> 複製到剪貼簿」的一鍵化流程。

### 前置作業

本專案使用 [uv](https://github.com/astral-sh/uv) 管理 Python 環境與依賴。

#### 1. 安裝系統依賴

確保系統已安裝 `portaudio` (用於錄音) 以及 `wl-clipboard` (用於 Wayland 下的剪貼簿操作)：

```bash
# 以 Debian/Ubuntu 為例
sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev wl-clipboard
```

#### 2. 設定 API Headers

為了呼叫 ChatGPT 的轉錄 API，你需要手動擷取登入後的 Request Headers：

1. 開啟瀏覽器並登入 [ChatGPT](https://chatgpt.com)。
2. 開啟開發者工具 (F12) 並切換至 **Network** 標籤。
3. 在網頁上隨便錄製一段語音指令以觸發 `transcribe` API。
4. 找到該 `transcribe` 請求，複製其 **Request Headers** 的內容。（不要複製開頭為 `:` 的部分）
5. 在專案根目錄建立 `.request-header.txt`，格式可參考專案中的模板，確保包含必要的 `Authorization` 與 `Cookie`。

#### 3. 安裝 Python 依賴

```bash
uv sync
```

### 使用方式

#### 直接運行

```bash
uv run src/main.py
```

- **第一次執行**：開始錄音，畫面會顯示通知。
- **第二次執行**：結束錄音，系統會開始執行轉錄與美化。
- **處理完成**：結果會自動儲存至 `output/output.txt` 並複製到你的剪貼簿。

#### 推薦：綁定 GNOME 快捷鍵

建議將 `uv run /path/to/Audio-To-Text/src/main.py` 綁定至系統快捷鍵（例如 `Ctrl + Alt + T`），即可享受最流暢的輸入體驗。

### 專案結構

- `src/main.py`: 主程式，負責錄音狀態切換與流程調度。
- `src/transcribe.py`: 負責與 ChatGPT API 通訊。
- `src/beautify.py`: 文字美化與標點校正邏輯。
- `src/record.py`: 底層錄音實作。
- `output/`: 存放暫存錄音檔與最後的轉錄成品。

---

## English

A highly efficient voice-to-text tool based on the ChatGPT Web API, specifically designed for Linux (GNOME) environments. It enables a seamless "Record -> Transcribe -> Beautify -> Copy to Clipboard" workflow with a simple hotkey toggle.

### Prerequisites

This project uses [uv](https://github.com/astral-sh/uv) for Python environment and dependency management.

#### 1. Install System Dependencies

Ensure your system has `portaudio` (for recording) and `wl-clipboard` (for clipboard operations on Wayland) installed:

```bash
# For Debian/Ubuntu
sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev wl-clipboard
```

#### 2. Configure API Headers

To call the ChatGPT transcription API, you need to manually capture the Request Headers after logging in:

1. Open your browser and log in to [ChatGPT](https://chatgpt.com).
2. Open Developer Tools (F12) and go to the **Network** tab.
3. Record a short voice command on the page to trigger the `transcribe` API.
4. Find the `transcribe` request and copy its **Request Headers** (excluding headers starting with `:`).
5. Create a file named `.request-header.txt` in the project root. You can use the provided template as a reference, ensuring it includes required fields like `Authorization` and `Cookie`.

#### 3. Install Python Dependencies

```bash
uv sync
```

### Usage

#### Run Directly

```bash
uv run src/main.py
```

- **First Run**: Starts recording; a notification will appear.
- **Second Run**: Stops recording; the system begins transcription and beautification.
- **Completion**: The result is automatically saved to `output/output.txt` and copied to your clipboard.

#### Recommended: Bind to GNOME Hotkey

It is recommended to bind `uv run /path/to/Audio-To-Text/src/main.py` to a system shortcut (e.g., `Ctrl + Alt + T`) for the smootmost experience.

### Project Structure

- `src/main.py`: Main script for toggling recording states and orchestration.
- `src/transcribe.py`: Handles communication with the ChatGPT API.
- `src/beautify.py`: Logic for text beautification and punctuation correction.
- `src/record.py`: Underlying recording implementation.
- `output/`: Directory for temporary audio files and final transcription results.
