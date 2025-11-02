"""
Safe error recovery and user-friendly messages.

Provides error handling utilities that convert technical exceptions
into user-friendly messages with recovery suggestions.
"""

import logging
import traceback
from typing import Any, Dict, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)


class BackendError(Exception):
    """Base exception for backend errors."""

    pass


class ConfigurationError(BackendError):
    """Configuration validation errors."""

    pass


class ExecutionError(BackendError):
    """Pipeline execution errors."""

    pass


class DatasetError(BackendError):
    """Dataset access errors."""

    pass


def get_user_friendly_message(error: Exception) -> str:
    """
    Convert exception to user-friendly message.

    Args:
        error: Exception to convert

    Returns:
        User-friendly error message

    Example:
        >>> try:
        ...     raise FileNotFoundError("config.json")
        ... except Exception as e:
        ...     msg = get_user_friendly_message(e)
    """
    error_type = type(error).__name__
    error_msg = str(error)

    if isinstance(error, FileNotFoundError):
        return f"File not found: {error_msg}. Please check the file path."

    if isinstance(error, KeyError):
        return f"Missing required key: {error_msg}. Please check your configuration."

    if isinstance(error, ValueError):
        return f"Invalid value: {error_msg}. Please check your input data."

    if isinstance(error, TypeError):
        return f"Type error: {error_msg}. Please check data types in your configuration."

    if isinstance(error, ConfigurationError):
        return f"Configuration error: {error_msg}"

    if isinstance(error, ExecutionError):
        return f"Execution error: {error_msg}"

    if isinstance(error, DatasetError):
        return f"Dataset error: {error_msg}"

    return f"{error_type}: {error_msg}"


def get_recovery_suggestion(error: Exception) -> Optional[str]:
    """
    Get recovery suggestion for error.

    Args:
        error: Exception to analyze

    Returns:
        Recovery suggestion or None

    Example:
        >>> suggestion = get_recovery_suggestion(KeyError("columns"))
    """
    if isinstance(error, FileNotFoundError):
        return "Verify the file path exists and you have read permissions."

    if isinstance(error, KeyError):
        return "Check that all required configuration fields are present."

    if isinstance(error, ValueError):
        return "Validate your input values match the expected format and range."

    if isinstance(error, ConfigurationError):
        return "Review the configuration schema and ensure all required fields are set."

    if isinstance(error, ExecutionError):
        return "Check the pipeline logs for detailed error information."

    if isinstance(error, DatasetError):
        return "Ensure the dataset exists and is in the correct format."

    return "Please check the logs for more details."


def safe_execute(func: Callable) -> Callable:
    """
    Decorator for safe error handling with user-friendly responses.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function that returns standardized error response

    Example:
        >>> @safe_execute
        ... def risky_operation(param):
        ...     return {"result": param}
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "data": None,
                "error": get_user_friendly_message(e),
                "error_type": type(e).__name__,
                "recovery_suggestion": get_recovery_suggestion(e),
                "stack_trace": traceback.format_exc(),
            }

    return wrapper


class ErrorContext:
    """
    Context manager for error handling with custom messages.

    Example:
        >>> with ErrorContext("Loading dataset"):
        ...     df = load_data()
    """

    def __init__(self, operation: str, error_class: type = BackendError):
        """
        Initialize error context.

        Args:
            operation: Description of operation
            error_class: Exception class to raise on error
        """
        self.operation = operation
        self.error_class = error_class

    def __enter__(self):
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context and handle errors.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback

        Returns:
            False to propagate exception
        """
        if exc_type is not None:
            logger.error(f"Error during {self.operation}: {exc_val}", exc_info=True)
            raise self.error_class(f"{self.operation} failed: {str(exc_val)}") from exc_val
        return False
