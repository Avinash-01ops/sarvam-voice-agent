"""
utils.py
--------
Utility functions shared across all modules.

This module provides common helper functions for:
- Logging setup (consistent formatting across all modules)
- Retry logic for API calls (exponential backoff)
- File validation (checking if files exist and are valid)
- Audio file handling helpers

Keeping these functions in a separate module avoids code duplication
and ensures consistent behavior across the project.
"""

import logging
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create and configure a logger with consistent formatting.

    This function sets up a logger that outputs to the console with a
    standardized format including timestamp, logger name, log level,
    and the message.

    Args:
        name: The name for the logger (usually the module name).
        level: The logging level (default: INFO).

    Returns:
        logging.Logger: A configured logger instance.

    Example:
        >>> logger = setup_logger("stt")
        >>> logger.info("Processing audio file...")
        2026-06-30 10:30:00 - stt - INFO - Processing audio file...
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if logger already exists
    if not logger.handlers:
        # Create console handler with formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Define the log message format:
        # Timestamp - Logger Name - Level - Message
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def retry_on_failure(
    max_retries: int = 3,
    delay_seconds: float = 2.0,
    backoff_factor: float = 2.0,
) -> Callable:
    """
    Decorator that retries a function on failure with exponential backoff.

    This is useful for API calls that may fail temporarily due to:
    - Network issues
    - Rate limiting
    - Server overload

    The decorator will:
    1. Try to call the function
    2. If it fails, wait and retry
    3. Each retry waits longer (exponential backoff)
    4. After max_retries, raise the last exception

    Args:
        max_retries: Maximum number of retry attempts (default: 3).
        delay_seconds: Initial delay between retries in seconds (default: 2.0).
        backoff_factor: Multiplier for delay after each retry (default: 2.0).

    Returns:
        Callable: The decorated function with retry logic.

    Example:
        >>> @retry_on_failure(max_retries=3, delay_seconds=1.0)
        ... def call_api():
        ...     # This will be retried up to 3 times on failure
        ...     response = requests.post(...)
        ...     return response
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Track the current delay (increases with each retry)
            current_delay = delay_seconds
            # Store the last exception to re-raise if all retries fail
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    # Attempt to call the function
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        # Log the failure and wait before retrying
                        # We use print here to avoid circular imports with logging
                        print(
                            f"  ⚠ Attempt {attempt + 1}/{max_retries + 1} failed: "
                            f"{type(e).__name__}: {e}"
                        )
                        print(
                            f"  ↻ Retrying in {current_delay:.1f} seconds..."
                        )
                        time.sleep(current_delay)
                        # Increase delay for next retry (exponential backoff)
                        current_delay *= backoff_factor
                    else:
                        # All retries exhausted
                        print(
                            f"  ✗ All {max_retries + 1} attempts failed. "
                            f"Last error: {e}"
                        )

            # If we get here, all retries failed - raise the last exception
            raise last_exception

        return wrapper

    return decorator


def validate_file_exists(file_path: str) -> bool:
    """
    Check if a file exists and is readable.

    Args:
        file_path: Path to the file to validate.

    Returns:
        bool: True if the file exists and is readable, False otherwise.
    """
    path = Path(file_path)
    return path.exists() and path.is_file() and path.stat().st_size > 0


def get_file_size(file_path: str) -> str:
    """
    Get a human-readable file size string.

    Args:
        file_path: Path to the file.

    Returns:
        str: Human-readable file size (e.g., "1.5 MB").
    """
    size_bytes = Path(file_path).stat().st_size

    # Convert bytes to human-readable format
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024

    return f"{size_bytes:.1f} TB"


def ensure_wav_format(file_path: str) -> bool:
    """
    Check if a file has a valid WAV format header.

    This reads the first few bytes of the file to verify it's a valid
    WAV file (starts with 'RIFF' header).

    Args:
        file_path: Path to the file to check.

    Returns:
        bool: True if the file appears to be a valid WAV file.
    """
    try:
        with open(file_path, "rb") as f:
            # WAV files start with 'RIFF' and have 'WAVE' at position 8
            header = f.read(12)
            return header[:4] == b"RIFF" and header[8:12] == b"WAVE"
    except (IOError, OSError):
        return False
