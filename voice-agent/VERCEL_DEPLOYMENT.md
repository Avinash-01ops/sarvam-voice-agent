# Vercel Deployment Guide

This guide explains how to deploy the Sarvam Voice Agent to Vercel for free hosting.

## Prerequisites

- [Vercel account](https://vercel.com) (free)
- [Sarvam AI API key](https://dashboard.sarvam.ai)
- [Git](https://git-scm.com/) installed
- [Node.js](https://nodejs.org/) installed (for Vercel CLI)

## Quick Deploy (One-Click)

### Step 1: Push to GitHub

```powershell
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub, then push
git remote add origin https://github.com/YOUR_USERNAME/sarvam-voice-agent.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Other
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
4. Add Environment Variable:
   - Key: `SARVAM_API_KEY`
   - Value: `your_actual_api_key_here`
5. Click **Deploy**

### Step 3: Access Your App

After deployment (1-2 minutes), you'll get a URL like:
```
https://sarvam-voice-agent-xyz123.vercel.app
```

## Deploy via CLI (Alternative)

```powershell
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Deploy
cd voice-agent
vercel

# 4. Add environment variable
vercel env add SARVAM_API_KEY

# 5. Deploy to production
vercel --prod
```

## Environment Variables

Required and optional environment variables for Vercel:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SARVAM_API_KEY` | ✅ Yes | - | Your Sarvam AI API key |
| `STT_LANGUAGE` | No | `unknown` | Speech-to-text language |
| `TTS_LANGUAGE` | No | `en-IN` | Text-to-speech language |
| `TTS_SPEAKER` | No | `shubh` | Voice name |
| `LLM_MODEL` | No | `sarvam-30b` | LLM model |
| `LLM_TEMPERATURE` | No | `0.7` | Response creativity |
| `SYSTEM_PROMPT` | No | Friendly assistant | AI personality |

## Project Structure for Vercel

```
voice-agent/
├── web_app.py          # Main Flask app (entry point)
├── vercel.json         # Vercel configuration
├── runtime.txt         # Python version
├── requirements.txt    # Dependencies
├── config.py           # Configuration loader
├── llm.py              # LLM API client
├── stt.py              # Speech-to-text client
├── tts.py              # Text-to-speech client
├── utils.py            # Utilities
├── templates/
│   ├── index.html      # Chat page
│   └── settings.html   # Settings page
└── .env                # Local config (not deployed)
```

## How It Works on Vercel

1. **Vercel receives** your code from GitHub
2. **Installs dependencies** from `requirements.txt`
3. **Runs** `web_app.py` using `@vercel/python` builder
4. **Provides** environment variables you set in dashboard
5. **Serves** your app at `*.vercel.app`

## Features That Work on Vercel

✅ **Web Chat Interface** - Type messages and get AI responses  
✅ **Voice Recording** - Uses browser microphone API  
✅ **Audio Playback** - AI responses spoken aloud  
✅ **Settings Page** - Configure voice, language, etc.  
✅ **Multiple Languages** - Support for 11+ Indian languages  
✅ **Multiple Voices** - 38 different voice options  
✅ **Mobile Responsive** - Works on all devices  

## Features That Don't Work on Vercel

❌ **Terminal Voice Mode** (`app.py`) - Requires local microphone  
❌ **Persistent Settings** - Settings reset on redeploy (stateless)  

## Troubleshooting

### Build Fails
- Check `requirements.txt` has valid packages
- Ensure `runtime.txt` has correct Python version
- Verify `web_app.py` has no syntax errors

### API Key Not Set
- Add `SARVAM_API_KEY` in Vercel dashboard
- Go to Project Settings → Environment Variables
- Redeploy after adding variables

### App Crashes
- Check Vercel logs: `vercel logs`
- Verify all dependencies are installed
- Ensure `SARVAM_API_KEY` is valid

### Slow Response
- First request may be cold start (5-10 seconds)
- Subsequent requests are faster
- Consider upgrading to Vercel Pro for better performance

## Updating Your App

### Automatic Updates (GitHub)
1. Push changes to GitHub
2. Vercel auto-deploys on every push
3. Changes live in 1-2 minutes

### Manual Updates (CLI)
```powershell
vercel --prod
```

## Custom Domain (Optional)

1. Buy a domain (e.g., from GoDaddy, Namecheap)
2. In Vercel: Project Settings → Domains
3. Add your domain (e.g., `voice.yourdomain.com`)
4. Update DNS records as instructed
5. SSL certificate is automatic

## Cost

**Free Tier Includes:**
- 100GB bandwidth/month
- 1000 serverless function invocations/day
- 100 deployments/month
- Unlimited team members

**For higher limits, upgrade to Pro ($20/month)**

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Sarvam AI Dashboard](https://dashboard.sarvam.ai)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**That's it! Your voice agent is now live on the internet! 🎉**
