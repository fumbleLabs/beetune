"""
AI prompt generation utilities for beetune.

This module provides tools for generating prompts for OpenAI API calls
to analyze text and generate improvements.
"""

from .generators import (
    OutputFormat,
    PromptTone,
    gen_analysis,
    gen_suggestions,
)

__all__ = [
    "PromptTone",
    "OutputFormat",
    "gen_analysis",
    "gen_suggestions",
]
