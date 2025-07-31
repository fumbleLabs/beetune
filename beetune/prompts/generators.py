from enum import Enum
from typing import Optional


class PromptTone(Enum):
    """Available tone options for prompts."""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"
    CONCISE = "concise"


class OutputFormat(Enum):
    """Available output format options."""

    BULLET_POINTS = "bullet_points"
    COMMA_SEPARATED = "comma_separated"
    NUMBERED_LIST = "numbered_list"
    PARAGRAPH = "paragraph"


class PromptTemplates:
    """Enhanced prompt templates with parameterization support."""

    TONE_MODIFIERS = {
        PromptTone.PROFESSIONAL: "You are a professional career advisor with extensive experience in recruitment and talent acquisition.",
        PromptTone.CASUAL: "You are a friendly career coach who helps job seekers in a relaxed, approachable manner.",
        PromptTone.ENTHUSIASTIC: "You are an energetic career expert who is passionate about helping people succeed.",
        PromptTone.CONCISE: "You are an efficient career advisor who provides clear, direct guidance.",
    }

    FORMAT_INSTRUCTIONS = {
        OutputFormat.BULLET_POINTS: "Present your response as clear bullet points using • symbols.",
        OutputFormat.COMMA_SEPARATED: "Present your response as a comma-separated list with no additional formatting.",
        OutputFormat.NUMBERED_LIST: "Present your response as a numbered list with clear numbering (1., 2., 3., etc.).",
        OutputFormat.PARAGRAPH: "Present your response in well-structured paragraphs with clear explanations.",
    }


def gen_keywords(
    job_description: str,
    tone: PromptTone = PromptTone.PROFESSIONAL,
    output_format: OutputFormat = OutputFormat.COMMA_SEPARATED,
    include_soft_skills: bool = True,
    prioritize_technical: bool = True,
) -> str:
    """
    Generate a prompt for extracting keywords from a job description.

    Args:
        job_description: The job description text to analyze
        tone: The tone of the prompt (professional, casual, etc.)
        output_format: How to format the output
        include_soft_skills: Whether to include interpersonal/soft skills
        prioritize_technical: Whether to prioritize technical skills

    Returns:
        A well-structured prompt for keyword extraction
    """
    tone_modifier = PromptTemplates.TONE_MODIFIERS[tone]
    format_instruction = PromptTemplates.FORMAT_INSTRUCTIONS[output_format]

    skill_types = []
    if prioritize_technical:
        skill_types.append("technical skills (programming languages, frameworks, tools)")

    skill_types.extend(
        [
            "required qualifications and certifications",
            "experience levels and years",
            "industry-specific knowledge",
        ]
    )

    if include_soft_skills:
        skill_types.append("interpersonal and soft skills")

    skills_list = ", ".join(skill_types)

    prompt = f"""{tone_modifier}

Your task is to extract the most important and relevant keywords from the following job description. Focus on identifying:
- {skills_list}
- Key responsibilities and role requirements
- Specific technologies, methodologies, or domain expertise mentioned

IMPORTANT GUIDELINES:
1. Extract only explicit requirements mentioned in the job description
2. Include both must-have and nice-to-have skills if clearly distinguished
3. Avoid generic terms unless they are specifically emphasized
4. Include acronyms and their full forms when both are mentioned
5. Prioritize skills that appear multiple times or are emphasized

{format_instruction}

Job Description:
{job_description}

Extract the keywords now:"""

    return prompt


def gen_benefits(
    job_description: str,
    tone: PromptTone = PromptTone.PROFESSIONAL,
    output_format: OutputFormat = OutputFormat.COMMA_SEPARATED,
    prioritize_compensation: bool = True,
    include_culture: bool = True,
) -> str:
    """
    Generate a prompt for extracting benefits from a job description.

    Args:
        job_description: The job description text to analyze
        tone: The tone of the prompt
        output_format: How to format the output
        prioritize_compensation: Whether to list compensation first
        include_culture: Whether to include cultural benefits

    Returns:
        A well-structured prompt for benefits extraction
    """
    tone_modifier = PromptTemplates.TONE_MODIFIERS[tone]
    format_instruction = PromptTemplates.FORMAT_INSTRUCTIONS[output_format]

    benefit_categories = []
    if prioritize_compensation:
        benefit_categories.append(
            "compensation and salary information (list this first if available)"
        )

    benefit_categories.extend(
        [
            "health and wellness benefits",
            "time off and vacation policies",
            "professional development opportunities",
            "retirement and financial benefits",
        ]
    )

    if include_culture:
        benefit_categories.extend(
            ["work environment and culture perks", "flexible work arrangements"]
        )

    categories_list = "\n- ".join(benefit_categories)

    prompt = f"""{tone_modifier}

Your task is to extract all benefits, perks, and compensation information mentioned in this job description. Look for:
- {categories_list}
- Stock options, equity, or ownership opportunities
- Unique company perks or unusual benefits

IMPORTANT GUIDELINES:
1. Only extract benefits that are explicitly mentioned in the job description
2. If salary ranges are provided, include the full range
3. Include both monetary and non-monetary benefits
4. Distinguish between guaranteed benefits and potential perks when possible
5. Avoid assumptions - only list what is clearly stated

{format_instruction}

Job Description:
{job_description}

Extract the benefits now:"""

    return prompt


def gen_resume_suggestions(
    resume_text: str,
    job_description: str,
    tone: PromptTone = PromptTone.PROFESSIONAL,
    output_format: OutputFormat = OutputFormat.BULLET_POINTS,
    focus_areas: Optional[list] = None,
) -> str:
    """
    Generate a prompt for suggesting resume improvements.

    Args:
        resume_text: The current resume content
        job_description: The target job description
        tone: The tone of the prompt
        output_format: How to format the suggestions
        focus_areas: Specific areas to focus on (e.g., ['skills', 'experience', 'keywords'])

    Returns:
        A well-structured prompt for resume improvement suggestions
    """
    tone_modifier = PromptTemplates.TONE_MODIFIERS[tone]
    format_instruction = PromptTemplates.FORMAT_INSTRUCTIONS[output_format]

    default_focus_areas = [
        "keyword optimization for ATS systems",
        "quantification of achievements with specific metrics",
        "alignment of experience with job requirements",
        "highlighting relevant technical skills",
        "improving action verbs and impact statements",
        "addressing any obvious gaps or missing qualifications",
    ]

    areas_to_analyze = focus_areas if focus_areas else default_focus_areas
    focus_list = "\n- ".join(areas_to_analyze)

    prompt = f"""{tone_modifier}

You are analyzing a resume against a specific job description to provide targeted improvement suggestions. Your analysis should focus on:
- {focus_list}

ANALYSIS APPROACH:
1. Compare the resume content directly with job requirements
2. Identify missing keywords that should be naturally incorporated
3. Suggest specific, actionable improvements rather than generic advice
4. Consider both content improvements and formatting/presentation enhancements
5. Assume the candidate has broader experience that may not be fully reflected in the current resume

IMPORTANT: Do not rewrite the resume. Only provide specific, actionable suggestions for improvement.

{format_instruction}

Job Description:
{job_description}

Current Resume:
{resume_text}

Provide your improvement suggestions:"""

    return prompt


def gen_resume_application(
    resume_text: str,
    suggestions: str,
    job_description: str,
    tone: PromptTone = PromptTone.PROFESSIONAL,
    latex_style: str = "modern",
) -> str:
    """
    Generate a prompt for applying improvements to a resume with LaTeX formatting.

    Args:
        resume_text: The original resume content
        suggestions: The improvement suggestions to apply
        job_description: The target job description for context
        tone: The tone of the prompt
        latex_style: The LaTeX style to apply (modern, classic, minimal)

    Returns:
        A well-structured prompt for applying resume improvements
    """
    tone_modifier = PromptTemplates.TONE_MODIFIERS[tone]

    style_instructions = {
        "modern": "Use a clean, modern LaTeX format with clear section headers and professional typography.",
        "classic": "Use a traditional, conservative LaTeX format suitable for formal industries.",
        "minimal": "Use a minimalist LaTeX format with subtle styling and maximum readability.",
    }

    style_instruction = style_instructions.get(latex_style, style_instructions["modern"])

    prompt = f"""{tone_modifier} You are an expert resume writer and LaTeX specialist.

Your task is to take the original resume content and improvement suggestions, then create an enhanced, professionally formatted resume in LaTeX.

REQUIREMENTS:
1. Incorporate ALL the provided suggestions naturally and authentically
2. {style_instruction}
3. Ensure the content directly addresses the job requirements where possible
4. Maintain professional language and avoid over-embellishment
5. Include proper LaTeX document structure with appropriate packages
6. Use consistent formatting throughout the document
7. Optimize for both human readers and ATS systems

STRUCTURE GUIDELINES:
- Start with \\documentclass and necessary packages
- Include contact information section
- Organize content in logical sections (Experience, Skills, Education, etc.)
- Use appropriate LaTeX commands for formatting (\\section, \\subsection, \\textbf, etc.)
- End with \\end{{document}}

Job Description (for context):
{job_description}

Improvement Suggestions to Incorporate:
{suggestions}

Original Resume Content:
{resume_text}

Generate the complete, improved LaTeX resume:"""

    return prompt


# Backward compatibility functions
def gen_keywords_simple(job_description: str) -> str:
    """Simple keyword extraction for backward compatibility."""
    return gen_keywords(
        job_description, tone=PromptTone.PROFESSIONAL, output_format=OutputFormat.COMMA_SEPARATED
    )


def gen_benefits_simple(job_description: str) -> str:
    """Simple benefits extraction for backward compatibility."""
    return gen_benefits(
        job_description, tone=PromptTone.PROFESSIONAL, output_format=OutputFormat.COMMA_SEPARATED
    )


# Maintain backward compatibility with original function names
gen_keywords.__name__ = "gen_keywords"
gen_benefits.__name__ = "gen_benefits"
