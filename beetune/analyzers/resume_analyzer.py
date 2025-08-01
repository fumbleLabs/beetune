"""
Resume analysis utilities for beetune.

Provides AI-powered analysis of resumes to generate improvement suggestions
and optimize content for specific job descriptions.
"""

import logging
from typing import Optional

from openai import OpenAI

from ..prompts import OutputFormat, PromptTone, gen_resume_application, gen_resume_suggestions
from ..utils import OpenAIError

logger = logging.getLogger(__name__)


class ResumeAnalyzer:
    """AI-powered resume analyzer and optimizer."""

    def __init__(self, config, default_model: str = "gpt-4o"):
        """
        Initialize the resume analyzer with configuration.
        
        Args:
            config: Configuration instance with API credentials
            default_model: Default OpenAI model to use
        """
        self.config = config
        api_key = config.get_api_key()
        self.client = OpenAI(api_key=api_key)
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
    
    def analyze_resume(self, resume_text: str, model: Optional[str] = None) -> dict:
        """
        Perform general resume analysis without specific job targeting.
        
        Args:
            resume_text: The resume content to analyze
            model: OpenAI model to use (defaults to instance default)
            
        Returns:
            Dictionary containing analysis results with suggestions and keywords
        """
        model = model or self.default_model
        
        try:
            prompt = f"""
            Analyze the following resume and provide structured feedback:
            
            Resume:
            {resume_text}
            
            Please provide:
            1. A list of key strengths
            2. Areas for improvement
            3. Missing sections or information
            4. Keyword suggestions
            5. Overall assessment
            
            Format your response as JSON with the following structure:
            {{
                "strengths": ["strength1", "strength2", ...],
                "improvements": ["improvement1", "improvement2", ...],
                "missing_sections": ["section1", "section2", ...],
                "keywords": ["keyword1", "keyword2", ...],
                "overall_assessment": "brief assessment",
                "suggestions": ["suggestion1", "suggestion2", ...]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3,
            )
            
            result = response.choices[0].message.content
            if result is None:
                raise OpenAIError("No content in OpenAI response")
            
            # Try to parse as JSON, fallback to text format
            try:
                import json
                return json.loads(result.strip())
            except json.JSONDecodeError:
                # Fallback to structured text format
                return {
                    "analysis": result.strip(),
                    "suggestions": [result.strip()],
                    "keywords": []
                }
                
        except Exception as e:
            logger.error(f"OpenAI API error during resume analysis: {str(e)}")
            raise OpenAIError("Failed to analyze resume", str(e))
    
    def analyze_resume_against_job(self, resume_text: str, job_description: str, 
                                  model: Optional[str] = None) -> dict:
        """
        Analyze resume against a specific job description.
        
        Args:
            resume_text: The resume content to analyze
            job_description: Target job description
            model: OpenAI model to use (defaults to instance default)
            
        Returns:
            Dictionary containing targeted analysis results
        """
        model = model or self.default_model
        
        try:
            prompt = f"""
            Analyze the following resume against the specific job description and provide targeted feedback:
            
            Job Description:
            {job_description}
            
            Resume:
            {resume_text}
            
            Please provide:
            1. How well the resume matches the job requirements
            2. Missing skills or experiences needed for the job
            3. Relevant experiences that should be highlighted
            4. Keywords from the job description that should be incorporated
            5. Specific improvements for this job application
            6. Match percentage (0-100)
            
            Format your response as JSON with the following structure:
            {{
                "match_percentage": 75,
                "missing_skills": ["skill1", "skill2", ...],
                "relevant_experiences": ["exp1", "exp2", ...],
                "job_keywords": ["keyword1", "keyword2", ...],
                "improvements": ["improvement1", "improvement2", ...],
                "strengths": ["strength1", "strength2", ...],
                "suggestions": ["suggestion1", "suggestion2", ...],
                "overall_assessment": "brief assessment for this specific job"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3,
            )
            
            result = response.choices[0].message.content
            if result is None:
                raise OpenAIError("No content in OpenAI response")
            
            # Try to parse as JSON, fallback to text format
            try:
                import json
                return json.loads(result.strip())
            except json.JSONDecodeError:
                # Fallback to structured text format
                return {
                    "analysis": result.strip(),
                    "suggestions": [result.strip()],
                    "keywords": [],
                    "match_percentage": 50
                }
                
        except Exception as e:
            logger.error(f"OpenAI API error during targeted resume analysis: {str(e)}")
            raise OpenAIError("Failed to analyze resume against job", str(e))