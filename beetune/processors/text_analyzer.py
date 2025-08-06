"""
Text analysis utilities for beetune.

Provides AI-powered analysis of text to extract keywords, suggest improvements,
and other relevant information.
"""

import logging
from typing import Dict, Optional

from openai import OpenAI

from ..prompts import gen_analysis, gen_suggestions
from ..utils import OpenAIError

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """AI-powered text analyzer."""

    def __init__(
        self, openai_api_key: str, default_model: str = "gpt-4o", base_url: Optional[str] = None
    ):
        """
        Initialize the text analyzer with OpenAI-compatible API credentials.

        Args:
            openai_api_key: API key for the AI provider
            default_model: Default model to use
            base_url: Custom API endpoint (for Ollama, custom providers, etc.)
        """
        if base_url:
            self.client = OpenAI(api_key=openai_api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=openai_api_key)
        self.default_model = default_model

    def analyze(self, text: str, model: Optional[str] = None) -> Dict[str, str]:
        """
        Analyze a text to extract keywords and other information.

        Args:
            text: The text to analyze
            model: OpenAI model to use (defaults to instance default)

        Returns:
            Dictionary containing extracted information

        Raises:
            OpenAIError: If the API call fails
        """
        model = model or self.default_model
        result = {}

        try:
            # Extract keywords
            logger.debug("Sending request to OpenAI for analysis...")
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": gen_analysis(text)}],
                max_tokens=300,
                temperature=0.3,
            )

            content = response.choices[0].message.content
            if content is None:
                raise OpenAIError("No content in OpenAI response for analysis")
            # A more robust parsing logic would be needed here in a real application
            # For now, we'll assume the model returns a simple key: value format.
            for line in content.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    result[key.strip().lower()] = value.strip()

        except Exception as e:
            logger.error(f"OpenAI API error during text analysis: {str(e)}")
            raise OpenAIError("Failed to analyze text", str(e))

        return result

    def suggest_improvements(self, text: str, goal: str, model: Optional[str] = None) -> str:
        """
        Suggest improvements for a given text based on a goal.

        Args:
            text: The text to improve
            goal: The goal for the improvement (e.g., "make it more concise")
            model: OpenAI model to use (defaults to instance default)

        Returns:
            A string containing the suggested improvements

        Raises:
            OpenAIError: If the API call fails
        """
        model = model or self.default_model

        try:
            logger.debug("Sending request to OpenAI for suggestions...")
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": gen_suggestions(text, goal)}],
                max_tokens=500,
                temperature=0.5,
            )

            content = response.choices[0].message.content
            if content is None:
                raise OpenAIError("No content in OpenAI response for suggestions")

            return content.strip()

        except Exception as e:
            logger.error(f"OpenAI API error during suggestion generation: {str(e)}")
            raise OpenAIError("Failed to generate suggestions", str(e))
