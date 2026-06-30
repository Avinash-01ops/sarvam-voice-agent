"""
llm.py
------
Large Language Model module for the Sarvam Voice Agent.

This module handles communication with the Sarvam Chat Completions API
(Sarvam-30B model). It sends text prompts and receives intelligent
responses, maintaining conversation history for context.

The Sarvam LLM API is OpenAI-compatible and supports:
- Multi-turn conversations with history
- System prompts for personality/behavior control
- Configurable temperature, max_tokens, top_p parameters
- Streaming responses (not used in this synchronous implementation)

API Endpoint: POST https://api.sarvam.ai/v1/chat/completions
Authentication: api-subscription-key header

This module uses the `requests` library for HTTP communication,
implementing the REST API directly as specified in the Sarvam docs.

Dependencies:
    - requests: For HTTP API calls
"""

import requests

from config import load_config
from utils import retry_on_failure, setup_logger

# Initialize logger for this module
logger = setup_logger("llm")

# Load configuration
config = load_config()


class LanguageModel:
    """
    Communicates with the Sarvam Chat Completions API (Sarvam-30B).

    This class handles:
    - Sending text prompts to the Sarvam LLM
    - Maintaining conversation history for context
    - Managing system prompts for personality/behavior
    - Handling API errors and retries

    The conversation history is stored as a list of message dictionaries,
    each with a "role" (system/user/assistant) and "content" (text).

    The history is automatically trimmed to prevent exceeding the
    model's context window (64K tokens for Sarvam-30B).

    Attributes:
        api_key: Sarvam API key for authentication.
        base_url: Base URL for the Sarvam API.
        model: LLM model to use (default: sarvam-30b).
        temperature: Controls randomness (0.0 = deterministic, 2.0 = creative).
        max_tokens: Maximum tokens in the response.
        top_p: Nucleus sampling parameter.
        system_prompt: The system message defining assistant behavior.
        history: List of conversation messages.
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        top_p: float = None,
        system_prompt: str = None,
    ):
        """
        Initialize the LanguageModel client.

        Args:
            api_key: Sarvam API key. Defaults to config value.
            model: LLM model name. Defaults to config value.
            temperature: Response randomness. Defaults to config value.
            max_tokens: Max response tokens. Defaults to config value.
            top_p: Nucleus sampling. Defaults to config value.
            system_prompt: System message. Defaults to config value.
        """
        self.api_key = api_key or config["SARVAM_API_KEY"]
        self.base_url = config["SARVAM_API_BASE_URL"]
        self.model = model or config["LLM_MODEL"]
        self.temperature = (
            temperature
            if temperature is not None
            else config["LLM_TEMPERATURE"]
        )
        self.max_tokens = max_tokens or config["LLM_MAX_TOKENS"]
        self.top_p = top_p if top_p is not None else config["LLM_TOP_P"]
        self.system_prompt = system_prompt or config["SYSTEM_PROMPT"]

        # Construct the full API endpoint URL
        self.endpoint = f"{self.base_url}/v1/chat/completions"

        # Initialize conversation history with the system prompt
        # The system prompt sets the assistant's personality and behavior
        self.history = [{"role": "system", "content": self.system_prompt}]

        logger.info(f"LLM initialized with model={self.model}")

    def chat(self, user_message: str) -> str:
        """
        Send a user message and get the assistant's response.

        This method:
        1. Adds the user's message to the conversation history
        2. Sends the full history to the LLM API
        3. Extracts the assistant's response
        4. Adds the response to the history
        5. Trims history if it gets too long

        Args:
            user_message: The user's text input.

        Returns:
            str: The assistant's text response.

        Raises:
            requests.HTTPError: If the API returns an error status.
            ValueError: If the API response is invalid.

        Example:
            >>> llm = LanguageModel()
            >>> response = llm.chat("What is the capital of India?")
            >>> print(response)
            "The capital of India is New Delhi."
        """
        # Step 1: Add user message to history
        self.history.append({"role": "user", "content": user_message})

        logger.info(f"Sending to LLM: '{user_message[:50]}...'")
        print("🧠 Sending to LLM...")

        # Step 2: Prepare the API request
        # The request body follows the OpenAI chat completions format
        payload = {
            "model": self.model,
            "messages": self.history,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }

        # Set up authentication header
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json",
        }

        # Step 3: Send the request with retry logic
        response = self._send_request(payload, headers)

        # Step 4: Parse the response
        result = response.json()

        # Step 5: Extract the assistant's message
        try:
            assistant_message = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected API response format: {result}")
            raise ValueError(f"Invalid API response format: {e}")

        # Step 6: Add assistant response to history
        self.history.append(
            {"role": "assistant", "content": assistant_message}
        )

        # Step 7: Trim history to prevent context overflow
        self._trim_history()

        logger.info(f"LLM response: '{assistant_message[:50]}...'")
        return assistant_message

    @retry_on_failure(
        max_retries=config["MAX_RETRIES"],
        delay_seconds=config["RETRY_DELAY_SECONDS"],
    )
    def _send_request(self, payload: dict, headers: dict):
        """
        Send the HTTP request to the LLM API.

        This method is decorated with retry_on_failure so it will
        automatically retry on transient errors.

        Args:
            payload: The JSON request body.
            headers: The HTTP headers including authentication.

        Returns:
            requests.Response: The API response.

        Raises:
            requests.HTTPError: If the API returns an error status.
        """
        response = requests.post(
            self.endpoint,
            json=payload,
            headers=headers,
            timeout=120,  # 2 minute timeout for LLM processing
        )
        response.raise_for_status()
        return response

    def _trim_history(self) -> None:
        """
        Trim conversation history to prevent exceeding context limits.

        This keeps the system prompt and the most recent messages,
        removing older messages when the history gets too long.

        The max history length is configured via MAX_CONVERSATION_HISTORY
        which counts user-assistant pairs (so actual messages = pairs * 2 + 1).
        """
        max_pairs = config["MAX_CONVERSATION_HISTORY"]
        # Keep system prompt + (max_pairs * 2) messages
        max_messages = 1 + (max_pairs * 2)

        if len(self.history) > max_messages:
            # Keep system prompt (index 0) and the most recent messages
            self.history = [self.history[0]] + self.history[-(max_messages - 1) :]
            logger.debug(f"Trimmed history to {len(self.history)} messages")

    def set_system_prompt(self, new_prompt: str) -> None:
        """
        Update the system prompt and reset conversation history.

        Changing the system prompt mid-conversation would create
        inconsistent behavior, so this resets the history.

        Args:
            new_prompt: The new system prompt text.
        """
        self.system_prompt = new_prompt
        # Reset history with the new system prompt
        self.history = [{"role": "system", "content": self.system_prompt}]
        logger.info("System prompt updated and history reset")

    def clear_history(self) -> None:
        """
        Clear conversation history while keeping the system prompt.

        This is useful for starting a fresh conversation without
        changing the assistant's personality.
        """
        self.history = [{"role": "system", "content": self.system_prompt}]
        logger.info("Conversation history cleared")

    def get_history_length(self) -> int:
        """
        Get the number of messages in the conversation history.

        Returns:
            int: Total number of messages (including system prompt).
        """
        return len(self.history)


def chat_with_llm(user_message: str, system_prompt: str = None) -> str:
    """
    Convenience function for one-off LLM interactions without history.

    This creates a new LanguageModel instance for each call, so
    conversation history is NOT maintained between calls.

    For continuous conversation with history, use the LanguageModel
    class directly.

    Args:
        user_message: The user's text input.
        system_prompt: Optional system prompt override.

    Returns:
        str: The assistant's text response.

    Example:
        >>> response = chat_with_llm("What is 2+2?")
        >>> print(response)
        "2+2 equals 4."
    """
    llm = LanguageModel(system_prompt=system_prompt)
    return llm.chat(user_message)
