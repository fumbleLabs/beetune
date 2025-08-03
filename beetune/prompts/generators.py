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


def gen_analysis(
    text: str,
    tone: PromptTone = PromptTone.PROFESSIONAL,
    output_format: OutputFormat = OutputFormat.BULLET_POINTS,
) -> str:
    """
    Generate a prompt for analyzing a text.

    Args:
        text: The text to analyze
        tone: The tone of the prompt (professional, casual, etc.)
        output_format: How to format the output

    Returns:
        A well-structured prompt for text analysis
    """
    tone_modifier = PromptTemplates.TONE_MODIFIERS[tone]
    format_instruction = PromptTemplates.FORMAT_INSTRUCTIONS[output_format]

    prompt = f"""{tone_modifier}

Your task is to analyze the following text and extract key information. Focus on identifying:
- Main topics and themes
- Key entities (people, places, organizations)
- Overall sentiment

IMPORTANT GUIDELINES:
1. Extract only explicit information mentioned in the text.
2. Avoid generic terms unless they are specifically emphasized.
3. Include acronyms and their full forms when both are mentioned.

{format_instruction}

Text:
{text}

Extract the key information now:"""

    return prompt


def gen_suggestions(
    text: str,
    goal: str,
    tone: PromptTone = PromptTone.PROFESSIONAL,
    output_format: OutputFormat = OutputFormat.BULLET_POINTS,
) -> str:
    """
    Generate a prompt for suggesting improvements to a text.

    Args:
        text: The text to improve
        goal: The improvement goal (e.g., "make it more concise")
        tone: The tone of the prompt
        output_format: How to format the suggestions

    Returns:
        A well-structured prompt for improvement suggestions
    """
    tone_modifier = PromptTemplates.TONE_MODIFIERS[tone]
    format_instruction = PromptTemplates.FORMAT_INSTRUCTIONS[output_format]

    prompt = f"""{tone_modifier}

You are analyzing a text to provide targeted improvement suggestions. Your analysis should focus on the following goal: {goal}.

ANALYSIS APPROACH:
1. Identify areas of the text that can be improved to meet the goal.
2. Suggest specific, actionable improvements rather than generic advice.
3. Consider both content improvements and formatting/presentation enhancements.

IMPORTANT: Do not rewrite the text. Only provide specific, actionable suggestions for improvement.

{format_instruction}

Text:
{text}

Provide your improvement suggestions:"""

    return prompt