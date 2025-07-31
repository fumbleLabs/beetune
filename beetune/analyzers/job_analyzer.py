"""
Job description analysis utilities for beetune.

Provides AI-powered analysis of job descriptions to extract keywords, benefits,
and other relevant information for resume optimization.
"""

import logging
from typing import Dict, Optional
from openai import OpenAI

from ..prompts import gen_keywords, gen_benefits
from ..utils import OpenAIError

logger = logging.getLogger(__name__)


class JobAnalyzer:
    """AI-powered job description analyzer."""

    def __init__(self, openai_api_key: str, default_model: str = "gpt-4o", base_url: Optional[str] = None):
        """
        Initialize the job analyzer with OpenAI-compatible API credentials.
        
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

    def analyze_job_description(
        self, 
        job_description: str, 
        model: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Analyze a job description to extract keywords and benefits.
        
        Args:
            job_description: The job description text to analyze
            model: OpenAI model to use (defaults to instance default)
            
        Returns:
            Dictionary containing extracted keywords and benefits
            
        Raises:
            OpenAIError: If the API call fails
        """
        model = model or self.default_model
        result = {}

        try:
            # Extract keywords
            logger.debug("Sending request to OpenAI for keyword extraction...")
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": gen_keywords(job_description)}],
                max_tokens=300,
                temperature=0.3,
            )
            
            keywords_content = response.choices[0].message.content
            if keywords_content is None:
                raise OpenAIError("No content in OpenAI response for keywords")
            result["keywords"] = keywords_content.strip()
            logger.debug(f"Keywords extracted: {result['keywords']}")

            # Extract benefits
            logger.debug("Sending request to OpenAI for benefit extraction...")
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": gen_benefits(job_description)}],
                max_tokens=300,
                temperature=0.3,
            )
            
            benefits_content = response.choices[0].message.content
            if benefits_content is None:
                raise OpenAIError("No content in OpenAI response for benefits")
            result["benefits"] = benefits_content.strip()
            logger.debug(f"Benefits extracted: {result['benefits']}")

        except Exception as e:
            logger.error(f"OpenAI API error during job analysis: {str(e)}")
            raise OpenAIError("Failed to analyze job description", str(e))

        return result