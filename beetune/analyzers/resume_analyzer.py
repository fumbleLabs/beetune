"""
Resume analysis utilities for beetune.

Provides AI-powered analysis of resumes to generate improvement suggestions
and optimize content for specific job descriptions.
"""

import logging
from typing import Optional
from openai import OpenAI

from ..prompts import gen_resume_suggestions, gen_resume_application, PromptTone, OutputFormat
from ..utils import OpenAIError

logger = logging.getLogger(__name__)


class ResumeAnalyzer:
    """AI-powered resume analyzer and optimizer."""

    def __init__(self, openai_api_key: str, default_model: str = "gpt-4o"):
        """
        Initialize the resume analyzer with OpenAI credentials.
        
        Args:
            openai_api_key: OpenAI API key
            default_model: Default OpenAI model to use
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.default_model = default_model

    def suggest_improvements(
        self,
        resume_text: str,
        job_description: str,
        model: Optional[str] = None,
        tone: Optional[PromptTone] = None,
        output_format: Optional[OutputFormat] = None,
    ) -> str:
        """
        Generate improvement suggestions for a resume based on a job description.
        
        Args:
            resume_text: The current resume content
            job_description: Target job description
            model: OpenAI model to use (defaults to instance default)
            tone: Tone for the suggestions
            output_format: Format for the output
            
        Returns:
            String containing improvement suggestions
            
        Raises:
            OpenAIError: If the API call fails
        """
        model = model or self.default_model
        tone = tone or PromptTone.PROFESSIONAL
        output_format = output_format or OutputFormat.BULLET_POINTS

        try:
            # Generate prompt
            prompt = gen_resume_suggestions(
                resume_text=resume_text,
                job_description=job_description,
                tone=tone,
                output_format=output_format,
            )

            logger.debug("Sending request to OpenAI for resume improvement suggestions...")
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3,
            )
            
            result = response.choices[0].message.content
            if result is None:
                raise OpenAIError("No content in OpenAI response")
            
            result = result.strip()
            logger.debug(f"Suggestions generated: {result}")
            return result

        except Exception as e:
            logger.error(f"OpenAI API error during resume analysis: {str(e)}")
            raise OpenAIError("Failed to generate resume suggestions", str(e))

    def apply_improvements(
        self,
        resume_text: str,
        suggestions: str,
        job_description: str = "",
        model: Optional[str] = None,
        tone: Optional[PromptTone] = None,
        latex_style: str = "modern",
    ) -> str:
        """
        Apply improvement suggestions to generate an optimized resume.
        
        Args:
            resume_text: Original resume content
            suggestions: Improvement suggestions to apply
            job_description: Target job description for context
            model: OpenAI model to use (defaults to instance default)
            tone: Tone for the application
            latex_style: LaTeX style to use
            
        Returns:
            Optimized resume content in LaTeX format
            
        Raises:
            OpenAIError: If the API call fails
        """
        model = model or self.default_model
        tone = tone or PromptTone.PROFESSIONAL

        try:
            # Generate prompt
            prompt = gen_resume_application(
                resume_text=resume_text,
                suggestions=suggestions,
                job_description=job_description,
                tone=tone,
                latex_style=latex_style,
            )

            logger.debug("Sending request to OpenAI for optimized resume generation...")
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.1,  # Lower temperature for more consistent output
            )
            
            result = response.choices[0].message.content
            if result is None:
                raise OpenAIError("No content in OpenAI response")
            
            return result.strip()

        except Exception as e:
            logger.error(f"OpenAI API error during resume optimization: {str(e)}")
            raise OpenAIError("Failed to apply improvements", str(e))