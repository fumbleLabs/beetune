"""
Exception classes for beetune.

Provides a hierarchy of exceptions for different types of errors that can occur
during resume processing, file handling, and analysis operations.
"""

from typing import Optional


class BeetuneException(Exception):
    """Base exception class for all beetune-related errors."""

    def __init__(self, message: str, detail: Optional[str] = None):
        self.message = message
        self.detail = detail or message
        super().__init__(self.message)


class ValidationError(BeetuneException):
    """Raised when input validation fails."""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, detail)


class ProcessingError(BeetuneException):
    """Raised when file or data processing fails."""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, detail)


class OpenAIError(BeetuneException):
    """Raised when OpenAI API calls fail."""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, detail)


class LaTeXError(BeetuneException):
    """Raised when LaTeX compilation fails."""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, detail)