"""
Exception classes for beetune.

Provides a hierarchy of exceptions for different types of errors that can occur
during resume processing, file handling, and analysis operations.
"""

from typing import Optional


class BeetuneError(Exception):
    """Base exception class for all beetune-related errors."""

    def __init__(self, message: str, detail: Optional[str] = None):
        self.message = message
        self.detail = detail or message
        super().__init__(self.message)


class ValidationError(BeetuneError):
    """Raised when input validation fails."""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, detail)


class ProcessingError(BeetuneError):
    """Raised when file or data processing fails."""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, detail)


class OpenAIError(BeetuneError):
    """Raised when OpenAI API calls fail."""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, detail)


class LaTeXError(BeetuneError):
    """Raised when LaTeX compilation fails."""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, detail)
