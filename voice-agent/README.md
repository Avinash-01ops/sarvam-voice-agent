# 🤖 Sarvam Voice Agent

A voice AI assistant that talks to you in multiple Indian languages! Built with **Sarvam AI**.

---

## 🚀 Quick Start (3 Steps)

### 1️⃣ Get Your API Key

1. Visit [dashboard.sarvam.ai](https://dashboard.sarvam.ai)
2. Sign up or log in
3. Copy your API key (starts with `sk_`)

### 2️⃣ Install

Open **PowerShell** and run:

```powershell
# Go to project folder
cd "d:\Avi's-PROJECT\Sarvam voice agent\voice-agent"

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Configure & Run

**Create your config file:**
```powershell
notepad .env
```

Add this line (replace with your actual key):
```env
SARVAM_API_KEY=sk_your_key_here
```

Save and close. Then run:

```powershell
python web_app.py
```

Open **http://localhost:5000** in your browser. 🎉

---

## 💻 Two Ways to Use

### Option A: Web UI (Recommended) 🌐

```powershell
python web_app.py
```

Then open: **http://localhost:5000**

| Page | URL | What it does |
|------|-----|--------------|
| Chat | `http://localhost:5000` | Talk to the AI with text or voice |
| Settings | `http://localhost:5000/settings` | Change API key, voice, language |

**Features:**
- 💬 Type messages or use voice
- 🎤 Click mic to record
- 🔊 AI speaks back automatically
- 📱 Works on mobile

---

### Option B: Terminal (Voice Mode) 🎤

```powershell
python app.py
```

**How it works:**
1. App records your voice (10 seconds)
2. Converts speech to text
3. AI thinks and responds
4. Plays audio response
5. Repeats!

**Commands:**
- Just **speak** when it says "Recording..."
- Say **"exit"** or press **Ctrl+C** to stop

**Options:**
```powershell
python app.py --voice          # Voice-activated recording
python app.py --language hi-IN # Hindi language
python app.py --speaker priya  # Female voice
python app.py --duration 15    # Record for 15 seconds
```

---

## ⚙️ Settings

Edit your `.env` file to customize:

```env
SARVAM_API_KEY=your_key_here
VOICE_NAME=anupam             # Voice to use
LANGUAGE=hi-IN               # Language code
SYSTEM_PROMPT=You are a friendly assistant
```

---

## 🎤 Available Voices

| Male | Female |
|------|--------|
| shubh (default), aditya, rohan, anand, rahul, amit, dev, ratan, varun, manan, sumit, kabir, aayan, ashutosh, advait, tarun, sunny, mani, gokul, vijay, mohit, rehan, soham | ritu, priya, neha, pooja, simran, kavya, ishita, shreya, roopa, tanya, shruti, suhani, kavitha, rupali |

---

## 🌐 Supported Languages

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
| **Auto-detect** | `unknown` |

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key not set" | Make sure `.env` file exists with `SARVAM_API_KEY` |
| "Module not found" | Run `pip install -r requirements.txt` |
| No microphone | Check Windows privacy settings → Microphone |
| Port 5000 in use | Change port: `python web_app.py --port 8080` |

---

## 📦 Requirements

- Python 3.11+
- Microphone (for voice mode)
- Speakers/headphones
- Internet connection

---

## 🚀 Deploy to Vercel (Free Hosting)

Deploy this app to Vercel with one click!

### Option 1: Deploy with Vercel Button (Easiest)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/sarvam-voice-agent&env=SARVAM_API_KEY)

**Steps:**
1. Click the button above
2. Enter your `SARVAM_API_KEY` when prompted
3. Click "Deploy"
4. Done! You'll get a live URL like `https://your-app.vercel.app`

### Option 2: Deploy via Vercel CLI

```powershell
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy (follow prompts)
vercel

# Set environment variable
vercel env add SARVAM_API_KEY

# Deploy to production
vercel --prod
```

### Option 3: Deploy via GitHub

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com) → "Add New Project"
3. Import your GitHub repository
4. Add environment variable: `SARVAM_API_KEY=your_key_here`
5. Click "Deploy"

### Environment Variables for Vercel

In your Vercel dashboard, add these environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `SARVAM_API_KEY` | ✅ Yes | Your Sarvam AI API key |
| `STT_LANGUAGE` | No | Language code (default: `unknown`) |
| `TTS_LANGUAGE` | No | TTS language (default: `en-IN`) |
| `TTS_SPEAKER` | No | Voice name (default: `shubh`) |
| `LLM_MODEL` | No | LLM model (default: `sarvam-30b`) |

### Important Notes for Vercel

- ✅ **Web UI works perfectly** on Vercel
- ✅ **Audio recording & playback** works (uses browser APIs)
- ⚠️ **Terminal voice mode** (`app.py`) won't work (requires local microphone)
- 📁 **Settings page** updates are stored per-instance (reset on redeploy)
- 🔄 **Free tier**: 100GB bandwidth, 1000 requests/day

---
