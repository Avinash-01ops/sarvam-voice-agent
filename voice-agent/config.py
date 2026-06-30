"""
config.py
---------
Configuration management for the Sarvam Voice Agent.

This module handles:
- Loading environment variables from .env file
- Validating required configuration values
- Providing centralized configuration access to all other modules

The configuration uses the python-dotenv library to load secrets from a .env
file, keeping sensitive data like API keys out of the source code.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def load_config():
    """
    Load and validate all configuration from environment variables.

    This function:
    1. Loads the .env file from the project root
    2. Reads all required and optional configuration values
    3. Validates that required values are present
    4. Returns a dictionary with all configuration

    Returns:
        dict: A dictionary containing all configuration values.

    Raises:
        SystemExit: If required environment variables are missing.
    """
    # Load the .env file from the same directory as this script
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)

    # --- Required Configuration ---
    # The Sarvam API key is mandatory for all API calls
    sarvam_api_key = os.getenv("SARVAM_API_KEY")

    if not sarvam_api_key:
        print("=" * 60)
        print("ERROR: SARVAM_API_KEY is not set!")
        print("=" * 60)
        print("\nPlease create a .env file in the project root with:")
        print('  SARVAM_API_KEY="your-api-key-here"')
        print("\nYou can get an API key from: https://dashboard.sarvam.ai")
        print("=" * 60)
        sys.exit(1)

    # --- Optional Configuration with Defaults ---
    # These values have sensible defaults but can be overridden via .env

    config = {
        # Sarvam API Configuration
        "SARVAM_API_KEY": sarvam_api_key,
        "SARVAM_API_BASE_URL": os.getenv(
            "SARVAM_API_BASE_URL", "https://api.sarvam.ai"
        ),
        # Speech-to-Text (Saaras v3) Configuration
        "STT_MODEL": os.getenv("STT_MODEL", "saaras:v3"),
        "STT_LANGUAGE": os.getenv("STT_LANGUAGE", "unknown"),  # Auto-detect
        "STT_MODE": os.getenv("STT_MODE", "transcribe"),  # transcribe/translate
        # Text-to-Speech (Bulbul v3) Configuration
        "TTS_MODEL": os.getenv("TTS_MODEL", "bulbul:v3"),
        "TTS_LANGUAGE": os.getenv("TTS_LANGUAGE", "en-IN"),
        "TTS_SPEAKER": os.getenv("TTS_SPEAKER", "shubh"),
        "TTS_SAMPLE_RATE": int(os.getenv("TTS_SAMPLE_RATE", "24000")),
        # LLM (Sarvam-30B) Configuration
        "LLM_MODEL": os.getenv("LLM_MODEL", "sarvam-30b"),
        "LLM_TEMPERATURE": float(os.getenv("LLM_TEMPERATURE", "0.7")),
        "LLM_MAX_TOKENS": int(os.getenv("LLM_MAX_TOKENS", "1000")),
        "LLM_TOP_P": float(os.getenv("LLM_TOP_P", "1.0")),
        # Audio Recording Configuration
        "RECORD_SAMPLE_RATE": int(os.getenv("RECORD_SAMPLE_RATE", "16000")),
        "RECORD_CHANNELS": int(os.getenv("RECORD_CHANNELS", "1")),
        "RECORD_CHUNK_SIZE": int(os.getenv("RECORD_CHUNK_SIZE", "1024")),
        "RECORD_SECONDS": int(os.getenv("RECORD_SECONDS", "10")),
        "RECORD_SILENCE_THRESHOLD": int(
            os.getenv("RECORD_SILENCE_THRESHOLD", "500")
        ),
        "RECORD_SILENCE_DURATION": float(
            os.getenv("RECORD_SILENCE_DURATION", "2.0")
        ),
        # File Paths
        "INPUT_AUDIO_PATH": os.getenv("INPUT_AUDIO_PATH", "input.wav"),
        "OUTPUT_AUDIO_PATH": os.getenv("OUTPUT_AUDIO_PATH", "response.wav"),
        # Retry Configuration
        "MAX_RETRIES": int(os.getenv("MAX_RETRIES", "3")),
        "RETRY_DELAY_SECONDS": float(os.getenv("RETRY_DELAY_SECONDS", "2.0")),
        # Conversation Configuration
        "SYSTEM_PROMPT": os.getenv(
            "SYSTEM_PROMPT",
            "You are a helpful, friendly voice assistant. Keep your responses "
            "concise and conversational, as they will be spoken aloud. "
            "Be natural and engaging.",
        ),
        "MAX_CONVERSATION_HISTORY": int(
            os.getenv("MAX_CONVERSATION_HISTORY", "20")
        ),
    }

    return config
