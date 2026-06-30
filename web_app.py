"""
web_app.py
----------
Web UI for the Sarvam Voice Agent.

This module creates a simple Flask web application that provides:
- A settings page to view/update the API key
- A chat interface for text-based conversation
- Audio upload for speech-to-text
- Audio playback for text-to-speech responses

The UI is served at http://localhost:5000

Usage:
    python web_app.py
"""

import base64
import os
import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

from config import load_config
from llm import LanguageModel
from stt import SpeechToText
from tts import TextToSpeech
from utils import setup_logger

# Initialize logger
logger = setup_logger("web_app")

# Create Flask application (templates/ is at the project root)
app = Flask(__name__, template_folder=Path(__file__).parent / "templates")
app.secret_key = "sarvam-voice-agent-secret-key"

# Global instances (initialized on first use)
llm = None
stt = None
tts = None


def get_llm():
    """Get or create the LLM instance."""
    global llm
    if llm is None:
        config = load_config()
        llm = LanguageModel(
            api_key=config["SARVAM_API_KEY"],
            model=config["LLM_MODEL"],
            temperature=config["LLM_TEMPERATURE"],
            max_tokens=config["LLM_MAX_TOKENS"],
            system_prompt=config["SYSTEM_PROMPT"],
        )
    return llm


def get_stt():
    """Get or create the STT instance."""
    global stt
    if stt is None:
        config = load_config()
        stt = SpeechToText(
            api_key=config["SARVAM_API_KEY"],
            model=config["STT_MODEL"],
            language=config["STT_LANGUAGE"],
            mode=config["STT_MODE"],
        )
    return stt


def get_tts():
    """Get or create the TTS instance."""
    global tts
    if tts is None:
        config = load_config()
        tts = TextToSpeech(
            api_key=config["SARVAM_API_KEY"],
            model=config["TTS_MODEL"],
            language=config["TTS_LANGUAGE"],
            speaker=config["TTS_SPEAKER"],
            sample_rate=config["TTS_SAMPLE_RATE"],
        )
    return tts


@app.route("/")
def index():
    """Serve the main chat page."""
    return render_template("index.html")


@app.route("/settings")
def settings():
    """Serve the settings page."""
    return render_template("settings.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    """Get current configuration (excluding API key)."""
    try:
        config = load_config()
        # Return config without the API key for security
        safe_config = {
            "stt_model": config["STT_MODEL"],
            "stt_language": config["STT_LANGUAGE"],
            "stt_mode": config["STT_MODE"],
            "tts_model": config["TTS_MODEL"],
            "tts_language": config["TTS_LANGUAGE"],
            "tts_speaker": config["TTS_SPEAKER"],
            "tts_sample_rate": config["TTS_SAMPLE_RATE"],
            "llm_model": config["LLM_MODEL"],
            "llm_temperature": config["LLM_TEMPERATURE"],
            "llm_max_tokens": config["LLM_MAX_TOKENS"],
            "system_prompt": config["SYSTEM_PROMPT"],
            "has_api_key": bool(config["SARVAM_API_KEY"]),
        }
        return jsonify({"success": True, "config": safe_config})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/config", methods=["POST"])
def update_config():
    """Update configuration in .env file."""
    try:
        data = request.json
        env_path = Path(__file__).parent / ".env"

        # Read current .env content
        env_lines = {}
        if env_path.exists():
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and "=" in line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        env_lines[key.strip()] = value.strip()

        # Update with new values
        field_mapping = {
            "SARVAM_API_KEY": "api_key",
            "STT_LANGUAGE": "stt_language",
            "STT_MODE": "stt_mode",
            "TTS_LANGUAGE": "tts_language",
            "TTS_SPEAKER": "tts_speaker",
            "TTS_SAMPLE_RATE": "tts_sample_rate",
            "LLM_TEMPERATURE": "llm_temperature",
            "LLM_MAX_TOKENS": "llm_max_tokens",
            "SYSTEM_PROMPT": "system_prompt",
        }

        for env_key, json_key in field_mapping.items():
            if json_key in data and data[json_key]:
                env_lines[env_key] = str(data[json_key])

        # Write back to .env
        with open(env_path, "w") as f:
            f.write("# Sarvam Voice Agent Configuration\n")
            f.write("# Updated via Web UI\n\n")
            for key, value in env_lines.items():
                f.write(f"{key}={value}\n")

        # Reset instances to pick up new config
        global llm, stt, tts
        llm = None
        stt = None
        tts = None

        return jsonify({"success": True, "message": "Configuration updated"})
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Send a message to the LLM and get a response."""
    try:
        data = request.json
        message = data.get("message", "").strip()

        if not message:
            return jsonify({"success": False, "error": "Message is empty"}), 400

        # Get LLM response
        llm_instance = get_llm()
        response = llm_instance.chat(message)

        # Generate TTS audio
        tts_instance = get_tts()
        audio_path = tts_instance.synthesize(response)

        # Read audio file and encode as base64
        with open(audio_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")

        # Clean up temp file
        os.remove(audio_path)

        return jsonify(
            {
                "success": True,
                "response": response,
                "audio": audio_base64,
            }
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    """Transcribe uploaded audio to text."""
    try:
        if "audio" not in request.files:
            return jsonify({"success": False, "error": "No audio file"}), 400

        audio_file = request.files["audio"]

        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name

        # Transcribe
        stt_instance = get_stt()
        text = stt_instance.transcribe(tmp_path)

        # Clean up
        os.remove(tmp_path)

        return jsonify({"success": True, "text": text})
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/clear-history", methods=["POST"])
def clear_history():
    """Clear conversation history."""
    try:
        llm_instance = get_llm()
        llm_instance.clear_history()
        return jsonify({"success": True, "message": "History cleared"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  🤖 Sarvam Voice Agent - Web UI")
    print("=" * 50)
    print("\n  Open your browser and go to:")
    print("  → http://localhost:5000")
    print("\n  Settings page:")
    print("  → http://localhost:5000/settings")
    print("\n  Press Ctrl+C to stop")
    print("=" * 50 + "\n")

    app.run(debug=False, host="0.0.0.0", port=5000)
