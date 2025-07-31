"""
Utility classes and functions for beetune.

This module provides common utilities including exception classes,
validation helpers, and shared functionality.
"""

from .exceptions import (
    BeetuneException,
    ValidationError,
    ProcessingError,
    OpenAIError,
    LaTeXError,
)

__all__ = [
    "BeetuneException",
    "ValidationError", 
    "ProcessingError",
    "OpenAIError",
    "LaTeXError",
]