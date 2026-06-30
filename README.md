# 🤖 Sarvam Voice Agent

A complete Python voice AI assistant powered by **Sarvam AI**. This application enables natural voice conversations with an AI assistant that can listen, understand, and respond in multiple Indian languages.

## ✨ Features

- 🎙 **Speech Recognition** - Converts your speech to text using Sarvam's Saaras v3 model
- 🧠 **Intelligent Responses** - Powered by Sarvam-30B language model
- 🔊 **Natural Speech** - Responds with natural-sounding voices via Bulbul v3
- 🌐 **Multilingual** - Supports 11+ Indian languages with auto-detection
- 💬 **Continuous Conversation** - Maintains context across multiple turns
- 🔄 **Retry Logic** - Automatically retries failed API calls
- ⚙️ **Configurable** - Customize voices, languages, and behavior via `.env`
- 🎯 **Beginner-Friendly** - Clean, well-commented code

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         app.py                               │
│                   (Main Orchestrator)                        │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ record.py│→ │  stt.py  │→ │  llm.py  │→ │  tts.py  │    │
│  │          │  │          │  │          │  │          │    │
│  │ Microphone│  │  Saaras  │  │ Sarvam   │  │  Bulbul  │    │
│  │   Input   │  │   v3     │  │  30B     │  │   v3     │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│       ↑                                         │           │
│       └─────────────── Play Audio ←──────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Module Interactions

1. **`record.py`** captures audio from the microphone → saves as `input.wav`
2. **`stt.py`** sends `input.wav` to Sarvam STT API → returns text
3. **`llm.py`** sends text to Sarvam LLM API → returns AI response
4. **`tts.py`** sends response to Sarvam TTS API → saves as `response.wav`
5. **`app.py`** plays `response.wav` and loops back to step 1

### File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | Main entry point - orchestrates the conversation loop |
| `record.py` | Records audio from microphone using `sounddevice` |
| `stt.py` | Speech-to-Text via Sarvam Saaras v3 API |
| `llm.py` | Language model via Sarvam-30B chat completions API |
| `tts.py` | Text-to-Speech via Sarvam Bulbul v3 API |
| `config.py` | Loads and validates configuration from `.env` |
| `utils.py` | Shared utilities (logging, retries, file validation) |
| `requirements.txt` | Python package dependencies |
| `.env.example` | Template for environment variables |

## 📋 Prerequisites

- **Python 3.11** or higher
- **Sarvam AI API Key** - Get one free at [dashboard.sarvam.ai](https://dashboard.sarvam.ai)
- **Microphone** - A working microphone for audio input
- **Speakers/Headphones** - For hearing the AI's responses

## 🚀 Installation

### Step 1: Clone or Download

```bash
cd "d:\Avi's-PROJECT\Sarvam voice agent\voice-agent"
```

### Step 2: Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Sarvam API key
# On Windows, open with Notepad:
notepad .env
```

Edit the `.env` file and set your API key:

```env
SARVAM_API_KEY=sk_your_actual_api_key_here
```

### Step 5: Run the Application

```bash
python app.py
```

## 🎮 Usage

### Basic Usage

```bash
# Start with default settings (English, fixed 10s recording)
python app.py
```

### Advanced Options

```bash
# Use voice-activated recording (stops when you stop speaking)
python app.py --voice

# Use Hindi language
python app.py --language hi-IN

# Use a specific speaker voice
python app.py --speaker priya

# Set custom recording duration (seconds)
python app.py --duration 15

# Custom system prompt
python app.py --prompt "You are a helpful cooking assistant"

# Combine options
python app.py --voice --language ta-IN --speaker amit
```

### Available Voices

**Male voices:** shubh (default), aditya, rohan, anand, rahul, amit, dev, ratan, varun, manan, sumit, kabir, aayan, ashutosh, advait, tarun, sunny, mani, gokul, vijay, mohit, rehan, soham

**Female voices:** ritu, priya, neha, pooja, simran, kavya, ishita, shreya, roopa, tanya, shruti, suhani, kavitha, rupali

### Supported Languages

| Language | Code |
|----------|------|
| English (India) | `en-IN` |
| Hindi | `hi-IN` |
| Bengali | `bn-IN` |
| Tamil | `ta-IN` |
| Telugu | `te-IN` |
| Gujarati | `gu-IN` |
| Kannada | `kn-IN` |
| Malayalam | `ml-IN` |
| Marathi | `mr-IN` |
| Punjabi | `pa-IN` |
| Odia | `od-IN` |
| Auto-detect | `unknown` |

### In-Conversation Commands

- Say **"exit"**, **"quit"**, **"goodbye"**, or **"bye"** to end the session
- Say **"clear"** or **"reset"** to clear conversation history
- Press **Ctrl+C** at any time to force quit

## 🔧 Configuration

All configuration is done via the `.env` file. Key options:

```env
# API Key (Required)
SARVAM_API_KEY=your_key_here

# STT Settings
STT_LANGUAGE=unknown          # Language or "unknown" for auto-detect
STT_MODE=transcribe           # transcribe, translate, verbatim, translit, codemix

# TTS Settings
TTS_SPEAKER=shubh             # Voice to use
TTS_LANGUAGE=en-IN            # Output language
TTS_SAMPLE_RATE=24000         # Audio quality (8000-48000)

# LLM Settings
LLM_TEMPERATURE=0.7           # 0.0 (focused) to 2.0 (creative)
LLM_MAX_TOKENS=1000           # Maximum response length

# Recording Settings
RECORD_SECONDS=10             # Duration for fixed recording
RECORD_SILENCE_DURATION=2.0   # Silence before stopping (voice mode)

# Retry Settings
MAX_RETRIES=3                 # Number of retries on API failure
RETRY_DELAY_SECONDS=2.0       # Initial delay between retries
```

## 🐛 Troubleshooting

### Common Errors

#### 1. `SARVAM_API_KEY is not set!`

**Cause:** The `.env` file is missing or doesn't contain the API key.

**Solution:**
```bash
# Make sure .env exists in the project root
cp .env.example .env

# Edit .env and add your key
SARVAM_API_KEY=sk_your_actual_key
```

#### 2. `ModuleNotFoundError: No module named 'sounddevice'`

**Cause:** Dependencies are not installed or virtual environment is not activated.

**Solution:**
```bash
# Activate virtual environment first
venv\Scripts\activate    # Windows
source venv/bin/activate # macOS/Linux

# Then install dependencies
pip install -r requirements.txt
```

#### 3. `OSError: No Default Input Device Available`

**Cause:** No microphone is connected or system doesn't detect one.

**Solution:**
- Check that your microphone is plugged in
- Test microphone in system settings
- On Windows: Settings → System → Sound → Input

#### 4. `PortAudio not found` (Linux)

**Cause:** PortAudio library is missing on Linux.

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install portaudio19-dev

# Fedora
sudo dnf install portaudio-devel
```

#### 5. `401 Unauthorized` or `403 Forbidden`

**Cause:** Invalid or expired API key.

**Solution:**
- Verify your API key at [dashboard.sarvam.ai](https://dashboard.sarvam.ai)
- Make sure the key is correctly copied to `.env`
- Check if your API subscription is active

#### 6. `429 Too Many Requests`

**Cause:** You've hit the API rate limit.

**Solution:**
- Wait a minute and try again
- Check your rate limits on the Sarvam dashboard
- Consider upgrading your plan for higher limits

#### 7. `Could not understand audio` / Empty transcription

**Cause:** Audio quality issues or language mismatch.

**Solution:**
- Speak clearly and close to the microphone
- Reduce background noise
- Try setting a specific language instead of "unknown"
- Check that `input.wav` was created and has content

#### 8. `ConnectionError` or `Timeout`

**Cause:** Network issues or API downtime.

**Solution:**
- Check your internet connection
- Verify the API base URL in config
- Try again after a few minutes

### Debug Mode

To enable detailed logging, modify the log level in any module:

```python
# In any file, change:
logger = setup_logger("module_name", level=logging.DEBUG)
```

Or set the environment variable:
```bash
set LOG_LEVEL=DEBUG    # Windows
export LOG_LEVEL=DEBUG # macOS/Linux
```

## 📁 Project Structure

```
voice-agent/
│
├── app.py              # Main application - conversation loop orchestrator
├── record.py           # Audio recording from microphone
├── stt.py              # Speech-to-Text (Sarvam Saaras v3)
├── llm.py              # Language Model (Sarvam-30B)
├── tts.py              # Text-to-Speech (Sarvam Bulbul v3)
├── config.py           # Configuration management
├── utils.py            # Shared utility functions
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .env                # Your actual configuration (DO NOT COMMIT)
├── input.wav           # Recorded user audio (generated at runtime)
├── response.wav        # AI response audio (generated at runtime)
└── README.md           # This file
```

## 🔐 Security Notes

- **Never commit `.env`** to version control - it contains your API key
- Add `.env` to your `.gitignore` file
- Your API key grants access to your Sarvam account - keep it safe
- The `.env.example` file is safe to commit (it has no real values)

## 📚 API Reference

This project uses the following Sarvam AI APIs:

- **Speech-to-Text (Saaras v3):** `POST /speech-to-text`
- **Chat Completions (Sarvam-30B):** `POST /v1/chat/completions`
- **Text-to-Speech (Bulbul v3):** `POST /text-to-speech`

Full documentation: [https://docs.sarvam.ai](https://docs.sarvam.ai)

## 📄 License

This project is provided as-is for educational and development purposes.

## 🤝 Support

- **Sarvam AI Docs:** [https://docs.sarvam.ai](https://docs.sarvam.ai)
- **Sarvam Discord:** [Join the community](https://discord.com/invite/5rAsykttcs)
- **Email:** developer@sarvam.ai

---

Made with ❤️ using Sarvam AI
