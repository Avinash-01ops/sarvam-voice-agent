"""
app.py
------
Main orchestrator for the Sarvam Voice Agent.

This is the entry point of the application. It coordinates all the
modules to create a continuous voice conversation loop:

    Record → Transcribe → Think (LLM) → Speak (TTS) → Play → Repeat

The application flow:
1. Record audio from microphone → input.wav
2. Send to Sarvam STT API → recognized text
3. Send text to Sarvam LLM → response text
4. Send response to Sarvam TTS API → response.wav
5. Play the audio response
6. Repeat until user exits (Ctrl+C or says "exit"/"quit")

The app maintains conversation history across turns, allowing the LLM
to have context-aware conversations.

Usage:
    python app.py              # Start with default settings
    python app.py --voice      # Use voice-activated recording
    python app.py --language hi-IN  # Set Hindi language

Dependencies:
    All dependencies from the other modules (record, stt, llm, tts)
"""

import argparse
import os
import platform
import subprocess
import sys

from config import load_config
from llm import LanguageModel
from record import AudioRecorder
from stt import SpeechToText
from tts import TextToSpeech
from utils import setup_logger

# Initialize logger for the main application
logger = setup_logger("app")


def play_audio(file_path: str) -> None:
    """
    Play an audio file using the system's default audio player.

    This function uses platform-specific commands to play audio:
    - Windows: Uses `start` command with default media player
    - macOS: Uses `afplay` command
    - Linux: Uses `aplay` command

    Args:
        file_path: Path to the audio file to play.

    Raises:
        RuntimeError: If the audio cannot be played.
    """
    print("🔈 Playing response...")

    try:
        system = platform.system()

        if system == "Windows":
            # Use the default media player on Windows
            os.startfile(file_path)
        elif system == "Darwin":
            # macOS: use afplay
            subprocess.run(
                ["afplay", file_path],
                check=True,
                timeout=60,
            )
        elif system == "Linux":
            # Linux: use aplay (ALSA)
            subprocess.run(
                ["aplay", file_path],
                check=True,
                timeout=60,
            )
        else:
            logger.warning(f"Unsupported OS: {system}")
            print(f"⚠ Cannot play audio on {system}. File saved at: {file_path}")

    except FileNotFoundError:
        # Audio player not found - just inform the user
        logger.warning("Audio player not found")
        print(f"⚠ Audio player not found. File saved at: {file_path}")
    except subprocess.TimeoutExpired:
        logger.warning("Audio playback timed out")
    except Exception as e:
        logger.error(f"Failed to play audio: {e}")
        print(f"⚠ Could not play audio: {e}")
        print(f"  Audio file saved at: {file_path}")


def print_banner() -> None:
    """Print the application banner and instructions."""
    print("\n" + "=" * 60)
    print("  🤖 Sarvam Voice Agent")
    print("  Your AI Voice Assistant")
    print("=" * 60)
    print("\n  How to use:")
    print("  1. Wait for 'Recording...' prompt")
    print("  2. Speak your message")
    print("  3. Wait for the AI response")
    print("  4. Listen to the response")
    print("\n  Commands:")
    print("  • Say 'exit' or 'quit' to stop")
    print("  • Press Ctrl+C to force quit")
    print("  • Say 'clear' to reset conversation")
    print("=" * 60 + "\n")


def print_conversation_stats(turn_count: int, llm: LanguageModel) -> None:
    """
    Print conversation statistics.

    Args:
        turn_count: Number of conversation turns so far.
        llm: The language model instance (for history info).
    """
    print(f"\n📊 Stats: {turn_count} turns | "
          f"History: {llm.get_history_length()} messages")


def run_voice_agent(
    recording_mode: str = "fixed",
    language: str = None,
    system_prompt: str = None,
) -> None:
    """
    Main function that runs the voice agent conversation loop.

    This function:
    1. Initializes all components (recorder, STT, LLM, TTS)
    2. Enters a continuous loop of:
       a. Record user audio
       b. Transcribe to text
       c. Send to LLM
       d. Convert response to speech
       e. Play the audio
    3. Handles exit conditions and errors

    Args:
        recording_mode: "fixed" for fixed duration, "voice" for voice-activated.
        language: Override language code (e.g., "hi-IN").
        system_prompt: Override system prompt for the LLM.
    """
    # Load configuration
    config = load_config()

    # Override config with command-line arguments if provided
    if language:
        config["STT_LANGUAGE"] = language
        config["TTS_LANGUAGE"] = language

    # Print the welcome banner
    print_banner()

    # --- Initialize all components ---
    print("🚀 Initializing voice agent...\n")

    try:
        # Audio recorder for capturing microphone input
        recorder = AudioRecorder()

        # Speech-to-Text client (Saaras v3)
        stt = SpeechToText(language=config["STT_LANGUAGE"])

        # Language Model client (Sarvam-30B)
        llm = LanguageModel(
            system_prompt=system_prompt or config["SYSTEM_PROMPT"]
        )

        # Text-to-Speech client (Bulbul v3)
        tts = TextToSpeech(
            language=config["TTS_LANGUAGE"],
            speaker=config["TTS_SPEAKER"],
        )

        print("✅ All components initialized successfully!\n")
        print(f"   🎙 STT Model: {config['STT_MODEL']}")
        print(f"   🧠 LLM Model: {config['LLM_MODEL']}")
        print(f"   🔊 TTS Model: {config['TTS_MODEL']}")
        print(f"   🗣 Speaker: {config['TTS_SPEAKER']}")
        print(f"   🌐 Language: {config['STT_LANGUAGE']}")
        print()

    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        print(f"\n❌ Initialization failed: {e}")
        sys.exit(1)

    # --- Main conversation loop ---
    turn_count = 0

    print("🎯 Voice agent is ready! Starting conversation...\n")
    print("-" * 60)

    while True:
        try:
            turn_count += 1
            print(f"\n--- Turn {turn_count} ---")

            # Step 1: Record audio from microphone
            # Use voice-activated mode if specified, otherwise fixed duration
            if recording_mode == "voice":
                audio_file = recorder.record_until_silence()
            else:
                audio_file = recorder.record_fixed_duration()

            # Step 2: Transcribe audio to text using Sarvam STT
            user_text = stt.transcribe(audio_file)

            # Check if transcription was successful
            if not user_text:
                print("⚠ Could not understand audio. Please try again.")
                continue

            # Display what the user said
            print(f"\n👤 You said: {user_text}")

            # Step 3: Check for exit commands
            # Allow the user to exit by saying "exit" or "quit"
            if user_text.lower().strip() in [
                "exit",
                "quit",
                "goodbye",
                "bye",
                "stop",
            ]:
                print("\n👋 Goodbye! Thanks for chatting.")
                break

            # Check for clear history command
            if user_text.lower().strip() in ["clear", "reset", "new conversation"]:
                llm.clear_history()
                print("🔄 Conversation history cleared.")
                continue

            # Step 4: Send text to LLM and get response
            llm_response = llm.chat(user_text)

            # Display the LLM's response
            print(f"\n🤖 Assistant: {llm_response}")

            # Step 5: Convert LLM response to speech using Sarvam TTS
            audio_response_path = tts.synthesize(llm_response)

            # Step 6: Play the audio response
            play_audio(audio_response_path)

            # Print conversation stats
            print_conversation_stats(turn_count, llm)

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\n👋 Interrupted by user. Goodbye!")
            break

        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            print(f"\n❌ File error: {e}")
            print("   Please check your configuration and try again.")
            continue

        except Exception as e:
            # Log the error but continue the conversation
            logger.error(f"Error in conversation loop: {e}")
            print(f"\n❌ Error: {e}")
            print("   Continuing to next turn... (Ctrl+C to quit)")
            continue

    # Print final statistics
    print("\n" + "=" * 60)
    print("  Session Summary")
    print("=" * 60)
    print(f"  Total turns: {turn_count}")
    print(f"  Conversation history: {llm.get_history_length()} messages")
    print("=" * 60)
    print("\nThank you for using Sarvam Voice Agent! 🙏\n")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Sarvam Voice Agent - AI Voice Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py                          # Start with default settings
  python app.py --voice                  # Use voice-activated recording
  python app.py --language hi-IN         # Set Hindi language
  python app.py --speaker priya          # Use female voice
  python app.py --prompt "Be helpful"    # Custom system prompt
        """,
    )

    parser.add_argument(
        "--voice",
        action="store_true",
        help="Use voice-activated recording (stops on silence)",
    )

    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help='Language code (e.g., "en-IN", "hi-IN", "ta-IN", "unknown")',
    )

    parser.add_argument(
        "--speaker",
        type=str,
        default=None,
        help='TTS speaker voice (e.g., "shubh", "priya", "aditya")',
    )

    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Custom system prompt for the LLM",
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Recording duration in seconds (default: 10)",
    )

    return parser.parse_args()


def main():
    """
    Entry point for the Sarvam Voice Agent.

    Parses command-line arguments and starts the voice agent.
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Determine recording mode
    recording_mode = "voice" if args.voice else "fixed"

    # Override config with command-line arguments
    if args.duration:
        os.environ["RECORD_SECONDS"] = str(args.duration)
    if args.speaker:
        os.environ["TTS_SPEAKER"] = args.speaker

    # Run the voice agent
    run_voice_agent(
        recording_mode=recording_mode,
        language=args.language,
        system_prompt=args.prompt,
    )


if __name__ == "__main__":
    main()
