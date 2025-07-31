"""
AI prompt generation utilities for beetune.

This module provides tools for generating prompts for OpenAI API calls
to analyze resumes, job descriptions, and generate improvements.
"""

from .generators import (
    PromptTone,
    OutputFormat,
    gen_keywords,
    gen_benefits,
    gen_resume_suggestions,
    gen_resume_application,
)

__all__ = [
    "PromptTone", 
    "OutputFormat",
    "gen_keywords",
    "gen_benefits", 
    "gen_resume_suggestions",
    "gen_resume_application",
]