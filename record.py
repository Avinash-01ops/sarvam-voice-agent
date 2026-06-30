"""
record.py
---------
Audio recording module for the Sarvam Voice Agent.

This module handles recording audio from the user's microphone and saving
it as a WAV file. It uses the `sounddevice` library for cross-platform
audio input and `scipy` for saving WAV files.

The recording supports two modes:
1. Fixed-duration recording: Records for a set number of seconds
2. Voice-activated recording: Stops when silence is detected

The recorded audio is saved as a mono WAV file at the sample rate
configured in config.py (default: 16000 Hz), which is optimal for
speech recognition.

Dependencies:
    - sounddevice: For microphone input
    - scipy: For saving WAV files
    - numpy: For audio data manipulation
"""

import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from config import load_config
from utils import setup_logger

# Initialize logger for this module
logger = setup_logger("record")

# Load configuration
config = load_config()


class AudioRecorder:
    """
    Records audio from the microphone and saves it as a WAV file.

    This class provides methods to:
    - Record audio for a fixed duration
    - Record audio until silence is detected (voice-activated)
    - Save recorded audio to a WAV file

    The recorder uses the system's default microphone and records in
    mono channel at the configured sample rate.

    Attributes:
        sample_rate: Audio sample rate in Hz (default: 16000).
        channels: Number of audio channels (1 = mono).
        chunk_size: Number of frames per buffer.
        silence_threshold: Amplitude threshold below which is considered silence.
        silence_duration: Seconds of silence before stopping (voice mode).
        output_path: Path where the recorded audio will be saved.
    """

    def __init__(self, output_path: str = None):
        """
        Initialize the AudioRecorder with configuration values.

        Args:
            output_path: Path to save the recorded audio.
                        Defaults to config value or 'input.wav'.
        """
        self.sample_rate = config["RECORD_SAMPLE_RATE"]
        self.channels = config["RECORD_CHANNELS"]
        self.chunk_size = config["RECORD_CHUNK_SIZE"]
        self.silence_threshold = config["RECORD_SILENCE_THRESHOLD"]
        self.silence_duration = config["RECORD_SILENCE_DURATION"]
        self.output_path = output_path or config["INPUT_AUDIO_PATH"]

        # Log the audio device being used
        try:
            default_device = sd.query_devices(kind="input")
            logger.info(f"Using microphone: {default_device['name']}")
        except Exception:
            logger.warning("Could not query audio device info")

    def record_fixed_duration(self, duration: int = None) -> str:
        """
        Record audio for a fixed duration.

        This method blocks until the recording is complete. It records
        audio from the microphone for the specified number of seconds
        and saves it as a WAV file.

        Args:
            duration: Recording duration in seconds.
                      Defaults to config value (10 seconds).

        Returns:
            str: Path to the saved audio file.

        Raises:
            RuntimeError: If the recording fails.
        """
        # Use configured duration if not specified
        duration = duration or config["RECORD_SECONDS"]

        logger.info(f"Recording for {duration} seconds...")
        print(f"\n🎤 Recording... (speak now, {duration}s)")

        try:
            # Calculate total number of frames to record
            total_frames = int(self.sample_rate * duration)

            # Record audio using sounddevice
            # This blocks until recording is complete
            audio_data = sd.rec(
                frames=total_frames,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",  # 16-bit audio for good quality
            )

            # Wait for the recording to finish
            sd.wait()

            # Save the recorded audio to a WAV file
            self._save_audio(audio_data)

            logger.info(f"Audio saved to {self.output_path}")
            print(f"✅ Recording saved to {self.output_path}")
            return self.output_path

        except Exception as e:
            logger.error(f"Recording failed: {e}")
            raise RuntimeError(f"Failed to record audio: {e}")

    def record_until_silence(self, max_duration: int = 30) -> str:
        """
        Record audio until silence is detected or max duration is reached.

        This method records audio continuously and monitors the volume.
        When the volume stays below the silence threshold for the
        configured silence duration, recording stops.

        This is useful for voice commands where you don't know exactly
        how long the user will speak.

        Args:
            max_duration: Maximum recording duration in seconds (default: 30).

        Returns:
            str: Path to the saved audio file.

        Raises:
            RuntimeError: If the recording fails.
        """
        logger.info("Recording until silence is detected...")
        print("\n🎤 Recording... (speak now, will stop on silence)")

        try:
            # List to collect audio chunks
            audio_chunks = []
            # Counter for consecutive silent chunks
            silent_chunks = 0
            # Calculate how many chunks equal the silence duration
            chunks_for_silence = int(
                self.silence_duration * self.sample_rate / self.chunk_size
            )
            # Maximum number of chunks to record
            max_chunks = int(
                max_duration * self.sample_rate / self.chunk_size
            )

            # Create an input stream
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                blocksize=self.chunk_size,
            ) as stream:
                chunk_count = 0
                while chunk_count < max_chunks:
                    # Read a chunk of audio data
                    data, overflowed = stream.read(self.chunk_size)
                    audio_chunks.append(data)
                    chunk_count += 1

                    # Calculate the volume (RMS amplitude)
                    volume = np.sqrt(np.mean(data.astype(float) ** 2))

                    # Check if this chunk is silent
                    if volume < self.silence_threshold:
                        silent_chunks += 1
                    else:
                        silent_chunks = 0  # Reset counter on sound

                    # Stop if we've had enough consecutive silent chunks
                    if (
                        silent_chunks >= chunks_for_silence
                        and chunk_count > chunks_for_silence
                    ):
                        logger.info(
                            f"Silence detected after {chunk_count * self.chunk_size / self.sample_rate:.1f}s"
                        )
                        break

            # Combine all chunks into one array
            audio_data = np.concatenate(audio_chunks, axis=0)

            # Save the recorded audio
            self._save_audio(audio_data)

            duration = len(audio_data) / self.sample_rate
            logger.info(
                f"Audio saved to {self.output_path} ({duration:.1f}s)"
            )
            print(
                f"✅ Recording saved to {self.output_path} ({duration:.1f}s)"
            )
            return self.output_path

        except Exception as e:
            logger.error(f"Recording failed: {e}")
            raise RuntimeError(f"Failed to record audio: {e}")

    def _save_audio(self, audio_data: np.ndarray) -> None:
        """
        Save audio data as a WAV file.

        This internal method takes raw audio data and writes it to a
        WAV file at the configured output path.

        Args:
            audio_data: Numpy array of audio samples (int16 format).
        """
        # Ensure the data is in the right format for WAV
        if audio_data.dtype != np.int16:
            audio_data = audio_data.astype(np.int16)

        # If stereo, convert to mono by averaging channels
        if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
            audio_data = audio_data.mean(axis=1).astype(np.int16)

        # Write the WAV file using scipy
        wavfile.write(self.output_path, self.sample_rate, audio_data)
        logger.debug(
            f"Saved {len(audio_data)} samples at {self.sample_rate} Hz"
        )


def record_audio(output_path: str = None, mode: str = "fixed") -> str:
    """
    Convenience function to record audio without creating a class instance.

    This is the main entry point used by app.py. It creates an
    AudioRecorder instance and records audio based on the specified mode.

    Args:
        output_path: Path to save the recorded audio.
        mode: Recording mode - "fixed" for fixed duration,
              "voice" for voice-activated recording.

    Returns:
        str: Path to the saved audio file.

    Example:
        >>> audio_file = record_audio("input.wav", mode="fixed")
        >>> print(f"Recorded: {audio_file}")
    """
    recorder = AudioRecorder(output_path=output_path)

    if mode == "voice":
        return recorder.record_until_silence()
    else:
        return recorder.record_fixed_duration()
