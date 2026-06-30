"""
tts.py
------
Text-to-Speech module for the Sarvam Voice Agent.

This module handles communication with the Sarvam Text-to-Speech API
(Bulbul v3 model). It converts text responses into natural-sounding
speech audio files.

The Sarvam TTS API supports:
- 11 languages (10 Indian languages + English)
- 30+ speaker voices (male and female)
- Configurable speech rate (pace), pitch, and loudness
- Multiple sample rates (8kHz to 48kHz)
- Up to 2,500 characters per request

API Endpoint: POST https://api.sarvam.ai/text-to-speech
Authentication: api-subscription-key header

The API returns audio data in WAV format (base64-encoded in JSON),
which we decode and save to a file.

Dependencies:
    - requests: For HTTP API calls
    - base64: For decoding the audio data
"""

import base64
import json

import requests

from config import load_config
from utils import retry_on_failure, setup_logger

# Initialize logger for this module
logger = setup_logger("tts")

# Load configuration
config = load_config()


class TextToSpeech:
    """
    Communicates with the Sarvam Text-to-Speech API (Bulbul v3).

    This class handles:
    - Converting text to speech audio
    - Selecting speaker voices and languages
    - Configuring audio quality (sample rate)
    - Saving the generated audio to WAV files
    - Handling API errors and retries

    The Bulbul v3 model offers 30+ natural-sounding voices across
    11 languages. Each voice has unique characteristics suitable
    for different applications.

    Popular voices:
    - Male: shubh (default), aditya, rohan, anand
    - Female: priya, simran, kavya, ishita

    Attributes:
        api_key: Sarvam API key for authentication.
        base_url: Base URL for the Sarvam API.
        model: TTS model to use (default: bulbul:v3).
        language: Target language code (e.g., "en-IN").
        speaker: Speaker voice name (e.g., "shubh").
        sample_rate: Audio sample rate in Hz.
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        language: str = None,
        speaker: str = None,
        sample_rate: int = None,
    ):
        """
        Initialize the TextToSpeech client.

        Args:
            api_key: Sarvam API key. Defaults to config value.
            model: TTS model name. Defaults to config value.
            language: Target language code. Defaults to config value.
            speaker: Speaker voice name. Defaults to config value.
            sample_rate: Audio sample rate. Defaults to config value.
        """
        self.api_key = api_key or config["SARVAM_API_KEY"]
        self.base_url = config["SARVAM_API_BASE_URL"]
        self.model = model or config["TTS_MODEL"]
        self.language = language or config["TTS_LANGUAGE"]
        self.speaker = speaker or config["TTS_SPEAKER"]
        self.sample_rate = sample_rate or config["TTS_SAMPLE_RATE"]

        # Construct the full API endpoint URL
        self.endpoint = f"{self.base_url}/text-to-speech"

        logger.info(
            f"TTS initialized with model={self.model}, "
            f"speaker={self.speaker}, language={self.language}"
        )

    @retry_on_failure(
        max_retries=config["MAX_RETRIES"],
        delay_seconds=config["RETRY_DELAY_SECONDS"],
    )
    def synthesize(
        self, text: str, output_path: str = None
    ) -> str:
        """
        Convert text to speech and save as a WAV file.

        This method:
        1. Validates the text is not empty
        2. Sends the text to the Sarvam TTS API
        3. Decodes the base64 audio data from the response
        4. Saves the audio as a WAV file

        The API returns a JSON object with "audios" field containing
        an array of base64-encoded audio strings.

        Args:
            text: The text to convert to speech.
            output_path: Path to save the audio file.
                        Defaults to config value or 'response.wav'.

        Returns:
            str: Path to the saved audio file.

        Raises:
            ValueError: If the text is empty or too long.
            requests.HTTPError: If the API returns an error status.

        Example:
            >>> tts = TextToSpeech()
            >>> audio_file = tts.synthesize("Hello, how are you?")
            >>> print(f"Audio saved to: {audio_file}")
        """
        # Use configured output path if not specified
        output_path = output_path or config["OUTPUT_AUDIO_PATH"]

        # Step 1: Validate input text
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # API limit is 2500 characters per request
        if len(text) > 2500:
            logger.warning(
                f"Text is {len(text)} chars, truncating to 2500 chars"
            )
            text = text[:2500]

        logger.info(f"Synthesizing speech for: '{text[:50]}...'")
        print("🔊 Generating speech...")

        # Step 2: Prepare the API request
        payload = {
            "text": text,
            "target_language_code": self.language,
            "model": self.model,
            "speaker": self.speaker,
            "speech_sample_rate": self.sample_rate,
        }

        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json",
        }

        # Step 3: Send the request to the API
        response = requests.post(
            self.endpoint,
            json=payload,
            headers=headers,
            timeout=60,  # 60 second timeout
        )

        # Step 4: Check for HTTP errors
        response.raise_for_status()

        # Step 5: Parse the response
        result = response.json()

        # Step 6: Extract and decode the audio data
        try:
            # The API returns base64-encoded audio in the "audios" array
            audio_base64 = result["audios"][0]
            audio_data = base64.b64decode(audio_base64)
        except (KeyError, IndexError, Exception) as e:
            logger.error(f"Failed to decode audio response: {e}")
            raise ValueError(f"Invalid TTS API response: {e}")

        # Step 7: Save the audio data to a WAV file
        with open(output_path, "wb") as f:
            f.write(audio_data)

        logger.info(f"Speech saved to {output_path}")
        print(f"✅ Speech saved to {output_path}")
        return output_path

    def set_speaker(self, speaker: str) -> None:
        """
        Change the speaker voice.

        Args:
            speaker: Name of the speaker voice (e.g., "priya", "aditya").
        """
        self.speaker = speaker
        logger.info(f"Speaker changed to: {speaker}")

    def set_language(self, language: str) -> None:
        """
        Change the target language.

        Args:
            language: BCP-47 language code (e.g., "hi-IN", "ta-IN").
        """
        self.language = language
        logger.info(f"Language changed to: {language}")


def synthesize_speech(text: str, output_path: str = None) -> str:
    """
    Convenience function to synthesize speech without creating a class instance.

    This is the main entry point used by app.py. It creates a
    TextToSpeech instance and converts the given text to speech.

    Args:
        text: The text to convert to speech.
        output_path: Path to save the audio file.

    Returns:
        str: Path to the saved audio file.

    Example:
        >>> audio = synthesize_speech("Hello world!")
        >>> print(f"Audio saved to: {audio}")
    """
    tts = TextToSpeech()
    return tts.synthesize(text, output_path=output_path)
