"""
Utility classes and functions for beetune.

This module provides common utilities including exception classes,
validation helpers, and shared functionality.
"""

from .exceptions import (
    BeetuneError,
    LaTeXError,
    OpenAIError,
    ProcessingError,
    ValidationError,
)

__all__ = [
    "BeetuneError",
    "ValidationError",
    "ProcessingError",
    "OpenAIError",
    "LaTeXError",
]
