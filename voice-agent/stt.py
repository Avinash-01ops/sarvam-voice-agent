"""
stt.py
------
Speech-to-Text module for the Sarvam Voice Agent.

This module handles communication with the Sarvam Speech-to-Text API
(Saaras v3 model). It converts audio files (WAV format) into text
transcriptions.

The Sarvam STT API supports:
- 23 languages (22 Indian languages + English)
- Multiple output modes: transcribe, translate, verbatim, translit, codemix
- Automatic language detection (when language is set to "unknown")

API Endpoint: POST https://api.sarvam.ai/speech-to-text
Authentication: api-subscription-key header

This module uses the `requests` library for HTTP communication,
implementing the REST API directly as specified in the Sarvam docs.

Dependencies:
    - requests: For HTTP API calls
"""

import requests

from config import load_config
from utils import retry_on_failure, setup_logger, validate_file_exists

# Initialize logger for this module
logger = setup_logger("stt")

# Load configuration
config = load_config()


class SpeechToText:
    """
    Communicates with the Sarvam Speech-to-Text API (Saaras v3).

    This class handles:
    - Sending audio files to the Sarvam STT API
    - Extracting transcribed text from the response
    - Handling API errors and retries
    - Supporting different transcription modes

    The Saaras v3 model supports multiple output modes:
    - "transcribe": Standard transcription in the original language
    - "translate": Translates speech to English
    - "verbatim": Word-for-word without normalization
    - "translit": Romanization to Latin script
    - "codemix": Mixed script output

    Attributes:
        api_key: Sarvam API key for authentication.
        base_url: Base URL for the Sarvam API.
        model: STT model to use (default: saaras:v3).
        language: Language code or "unknown" for auto-detection.
        mode: Transcription mode (transcribe/translate/etc.).
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        language: str = None,
        mode: str = None,
    ):
        """
        Initialize the SpeechToText client.

        Args:
            api_key: Sarvam API key. Defaults to config value.
            model: STT model name. Defaults to config value.
            language: Language code. Defaults to config value.
            mode: Transcription mode. Defaults to config value.
        """
        self.api_key = api_key or config["SARVAM_API_KEY"]
        self.base_url = config["SARVAM_API_BASE_URL"]
        self.model = model or config["STT_MODEL"]
        self.language = language or config["STT_LANGUAGE"]
        self.mode = mode or config["STT_MODE"]

        # Construct the full API endpoint URL
        self.endpoint = f"{self.base_url}/speech-to-text"

        logger.info(f"STT initialized with model={self.model}, mode={self.mode}")

    @retry_on_failure(
        max_retries=config["MAX_RETRIES"],
        delay_seconds=config["RETRY_DELAY_SECONDS"],
    )
    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribe an audio file to text using the Sarvam STT API.

        This method:
        1. Validates the audio file exists
        2. Sends the audio file to the Sarvam STT API
        3. Extracts and returns the transcribed text

        The API accepts audio files up to 30 seconds for the REST endpoint.
        Supported formats: WAV, MP3, AAC, FLAC, OGG, and more.

        Args:
            audio_file_path: Path to the audio file to transcribe.

        Returns:
            str: The transcribed text.

        Raises:
            FileNotFoundError: If the audio file doesn't exist.
            requests.HTTPError: If the API returns an error status.
            ValueError: If the API response is invalid.

        Example:
            >>> stt = SpeechToText()
            >>> text = stt.transcribe("input.wav")
            >>> print(text)
            "Hello, how are you today?"
        """
        # Step 1: Validate the audio file exists
        if not validate_file_exists(audio_file_path):
            raise FileNotFoundError(
                f"Audio file not found: {audio_file_path}"
            )

        logger.info(f"Transcribing audio file: {audio_file_path}")
        print("🔄 Converting speech to text...")

        # Step 2: Prepare the API request
        # The API uses multipart/form-data for file uploads
        with open(audio_file_path, "rb") as audio_file:
            # Form data includes the model and mode parameters
            files = {"file": (audio_file_path, audio_file, "audio/wav")}
            data = {
                "model": self.model,
                "mode": self.mode,
            }

            # Add language parameter if specified (not "unknown")
            if self.language and self.language != "unknown":
                data["language_code"] = self.language

            # Set up authentication header
            headers = {
                "api-subscription-key": self.api_key,
            }

            # Step 3: Send the request to the API
            response = requests.post(
                self.endpoint,
                files=files,
                data=data,
                headers=headers,
                timeout=60,  # 60 second timeout for large files
            )

        # Step 4: Check for HTTP errors
        response.raise_for_status()

        # Step 5: Parse the JSON response
        result = response.json()

        # Step 6: Extract the transcribed text
        transcript = result.get("transcript", "")

        if not transcript:
            logger.warning("API returned empty transcript")
            return ""

        # Log additional info if available
        detected_language = result.get("language_code")
        confidence = result.get("language_probability")
        if detected_language:
            logger.info(f"Detected language: {detected_language}")
        if confidence:
            logger.info(f"Language confidence: {confidence:.2f}")

        logger.info(f"Transcription successful: '{transcript[:50]}...'")
        return transcript


def transcribe_audio(audio_file_path: str) -> str:
    """
    Convenience function to transcribe audio without creating a class instance.

    This is the main entry point used by app.py. It creates a
    SpeechToText instance and transcribes the given audio file.

    Args:
        audio_file_path: Path to the audio file to transcribe.

    Returns:
        str: The transcribed text.

    Example:
        >>> text = transcribe_audio("input.wav")
        >>> print(f"You said: {text}")
    """
    stt = SpeechToText()
    return stt.transcribe(audio_file_path)
