import re
from enum import Enum
from typing import Any, Dict, List


class LaTeXStyle(Enum):
    """Available LaTeX formatting styles."""

    MODERN = "modern"
    CLASSIC = "classic"
    MINIMAL = "minimal"
    ACADEMIC = "academic"


class ResumeFormatter:
    """
    Robust LaTeX resume formatter that combines resume text and suggestions
    with professional formatting and minimal complexity.
    """

    # LaTeX templates for different styles
    LATEX_TEMPLATES = {
        LaTeXStyle.MODERN: {
            "documentclass": "\\documentclass[11pt,a4paper]{article}",
            "packages": [
                "\\usepackage[utf8]{inputenc}",
                "\\usepackage[T1]{fontenc}",
                "\\usepackage{geometry}",
                "\\usepackage{titlesec}",
                "\\usepackage{enumitem}",
                "\\usepackage{hyperref}",
                "\\usepackage{xcolor}",
                "\\usepackage{fontawesome5}",
            ],
            "geometry": "\\geometry{top=1in, bottom=1in, left=0.75in, right=0.75in}",
            "colors": "\\definecolor{primarycolor}{RGB}{0, 102, 204}",
            "section_format": "\\titleformat{\\section}{\\large\\bfseries\\color{primarycolor}}{}{0em}{}[\\titlerule]",
        },
        LaTeXStyle.CLASSIC: {
            "documentclass": "\\documentclass[11pt,a4paper]{article}",
            "packages": [
                "\\usepackage[utf8]{inputenc}",
                "\\usepackage[T1]{fontenc}",
                "\\usepackage{geometry}",
                "\\usepackage{enumitem}",
            ],
            "geometry": "\\geometry{top=1in, bottom=1in, left=1in, right=1in}",
            "colors": "",
            "section_format": "",
        },
        LaTeXStyle.MINIMAL: {
            "documentclass": "\\documentclass[10pt,a4paper]{article}",
            "packages": [
                "\\usepackage[utf8]{inputenc}",
                "\\usepackage{geometry}",
                "\\usepackage{enumitem}",
            ],
            "geometry": "\\geometry{top=0.75in, bottom=0.75in, left=0.75in, right=0.75in}",
            "colors": "",
            "section_format": "\\renewcommand{\\section}[1]{\\vspace{0.5em}\\textbf{\\large #1}\\vspace{0.25em}\\hrule\\vspace{0.25em}}",
        },
    }

    @staticmethod
    def extract_contact_info(resume_text: str) -> Dict[str, str]:
        """
        Extract contact information from resume text.

        Args:
            resume_text: The resume content to analyze

        Returns:
            Dictionary containing extracted contact information
        """
        contact_info = {
            "name": "",
            "email": "",
            "phone": "",
            "linkedin": "",
            "github": "",
            "location": "",
        }

        lines = resume_text.split("\n")[:10]  # Check first 10 lines

        for line in lines:
            line = line.strip()

            # Extract email
            email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", line)
            if email_match and not contact_info["email"]:
                contact_info["email"] = email_match.group()

            # Extract phone number
            phone_match = re.search(
                r"[\+]?[1-9]?[\-\s\.]?\(?[0-9]{3}\)?[\-\s\.]?[0-9]{3}[\-\s\.]?[0-9]{4}", line
            )
            if phone_match and not contact_info["phone"]:
                contact_info["phone"] = phone_match.group()

            # Extract LinkedIn
            if "linkedin" in line.lower() and not contact_info["linkedin"]:
                linkedin_match = re.search(r"linkedin\.com/in/[\w\-]+", line.lower())
                if linkedin_match:
                    contact_info["linkedin"] = linkedin_match.group()

            # Extract GitHub
            if "github" in line.lower() and not contact_info["github"]:
                github_match = re.search(r"github\.com/[\w\-]+", line.lower())
                if github_match:
                    contact_info["github"] = github_match.group()

            # Extract name (first non-empty line that doesn't contain contact info)
            if (
                not contact_info["name"]
                and line
                and not any(
                    x in line.lower() for x in ["@", "phone", "email", "linkedin", "github"]
                )
                and len(line.split()) <= 4
            ):
                contact_info["name"] = line

        return contact_info

    @staticmethod
    def parse_resume_sections(resume_text: str) -> Dict[str, str]:
        """
        Parse resume text into structured sections.

        Args:
            resume_text: The resume content to parse

        Returns:
            Dictionary of section names to content
        """
        # Common section headers - simplified patterns
        section_patterns = [
            (r"^\s*(?:professional\s+)?(?:work\s+)?experience\s*:?\s*$", "experience"),
            (r"^\s*(?:technical\s+)?skills?\s*:?\s*$", "skills"),
            (r"^\s*education\s*:?\s*$", "education"),
            (r"^\s*(?:professional\s+)?summary\s*:?\s*$", "summary"),
            (r"^\s*projects?\s*:?\s*$", "projects"),
            (r"^\s*certifications?\s*:?\s*$", "certifications"),
            (r"^\s*achievements?\s*:?\s*$", "achievements"),
            (r"^\s*publications?\s*:?\s*$", "publications"),
        ]

        sections = {}
        current_section = "header"
        current_content: List[str] = []

        lines = resume_text.split("\n")

        for line in lines:
            line_stripped = line.strip()

            # Check if this line is a section header
            section_found = False
            for pattern, section_name in section_patterns:
                try:
                    if re.match(pattern, line_stripped, re.IGNORECASE):
                        # Save previous section
                        if current_content:
                            sections[current_section] = "\n".join(current_content).strip()

                        current_section = section_name
                        current_content = []
                        section_found = True
                        break
                except re.error:
                    # Skip malformed patterns
                    continue

            if not section_found:
                current_content.append(line)

        # Save the last section
        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    @staticmethod
    def generate_latex_header(
        contact_info: Dict[str, str], style: LaTeXStyle = LaTeXStyle.MODERN
    ) -> str:
        """
        Generate LaTeX document header with contact information.

        Args:
            contact_info: Dictionary containing contact information
            style: The LaTeX style to use

        Returns:
            LaTeX header string
        """
        template: Dict[str, Any] = ResumeFormatter.LATEX_TEMPLATES[style]

        header_parts: List[str] = [
            template["documentclass"],
            "",
        ]
        # Add packages
        header_parts.extend(template["packages"])
        header_parts.extend(
            [
                "",
                # Geometry
                template["geometry"],
                "",
            ]
        )

        # Colors and formatting
        if template["colors"]:
            header_parts.extend([template["colors"], ""])

        if template["section_format"]:
            header_parts.extend([template["section_format"], ""])

        # Document settings
        header_parts.extend(
            [
                "\\setlength{\\parindent}{0pt}",
                "\\setlength{\\parskip}{0.5em}",
                "",
                "\\begin{document}",
                "",
            ]
        )

        # Contact information
        if contact_info["name"]:
            if style == LaTeXStyle.MODERN:
                header_parts.append(f"\\centerline{{\\huge\\textbf{{{contact_info['name']}}}}}")
            else:
                header_parts.append(
                    f"\\begin{{center}}\\textbf{{\\Large {contact_info['name']}}}\\end{{center}}"
                )
            header_parts.append("")

        # Contact details
        contact_parts = []
        if contact_info["email"]:
            contact_parts.append(contact_info["email"])
        if contact_info["phone"]:
            contact_parts.append(contact_info["phone"])
        if contact_info["linkedin"]:
            contact_parts.append(contact_info["linkedin"])
        if contact_info["github"]:
            contact_parts.append(contact_info["github"])

        if contact_parts:
            contact_line = " $\\bullet$ ".join(contact_parts)
            header_parts.append(f"\\centerline{{{contact_line}}}")
            header_parts.append("")

        return "\n".join(header_parts)

    @staticmethod
    def format_section_content(section_name: str, content: str) -> str:
        """
        Format section content with appropriate LaTeX formatting.

        Args:
            section_name: The name of the section
            content: The content to format

        Returns:
            Formatted LaTeX content
        """
        if not content.strip():
            return ""

        # Clean up content
        content = content.strip()

        # Format based on section type
        if section_name == "experience":
            return ResumeFormatter._format_experience_section(content)
        elif section_name == "skills":
            return ResumeFormatter._format_skills_section(content)
        elif section_name == "education":
            return ResumeFormatter._format_education_section(content)
        elif section_name == "projects":
            return ResumeFormatter._format_projects_section(content)
        else:
            # Generic formatting
            return ResumeFormatter._format_generic_section(content)

    @staticmethod
    def _format_experience_section(content: str) -> str:
        """Format experience section with job entries."""
        lines = content.split("\n")
        formatted_lines = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # Check if this looks like a job header (contains | or has dates)
            if ("|" in line or re.search(r"\d{4}", line)) and not line.startswith("•"):
                # This is a job header
                formatted_lines.append(f"\\textbf{{{line}}}")

                # Look for bullet points that follow
                bullet_points = []
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if next_line.startswith("•"):
                        bullet_points.append(f"\\item {next_line[1:].strip()}")
                        i += 1
                    elif next_line and not ("|" in next_line or re.search(r"\d{4}", next_line)):
                        # Regular content line
                        bullet_points.append(f"\\item {next_line}")
                        i += 1
                    else:
                        break

                # Add bullet points if we found any
                if bullet_points:
                    formatted_lines.append("\\begin{itemize}[leftmargin=1em]")
                    formatted_lines.extend(bullet_points)
                    formatted_lines.append("\\end{itemize}")
            else:
                # Just a regular line
                if line.startswith("•"):
                    formatted_lines.append(f"\\item {line[1:].strip()}")
                else:
                    formatted_lines.append(line)
                i += 1

        return "\n".join(formatted_lines)

    @staticmethod
    def _format_skills_section(content: str) -> str:
        """Format skills section."""
        lines = content.split("\n")
        clean_lines = [line.strip() for line in lines if line.strip()]

        # Check if it's all on one line with commas (simple comma-separated)
        if len(clean_lines) == 1 and "," in clean_lines[0] and ":" not in clean_lines[0]:
            # Simple comma-separated format like "Python, JavaScript, SQL"
            skills = [skill.strip() for skill in clean_lines[0].split(",")]
            return ", ".join(f"\\textbf{{{skill}}}" for skill in skills if skill)
        else:
            # Multi-line format or categorized skills
            return " $\\bullet$ ".join(clean_lines)

    @staticmethod
    def _format_education_section(content: str) -> str:
        """Format education section."""
        lines = content.split("\n")
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if line:
                # Emphasize degree and institution names
                if any(
                    word in line.lower()
                    for word in ["bachelor", "master", "phd", "university", "college"]
                ):
                    formatted_lines.append(f"\\textbf{{{line}}}")
                else:
                    formatted_lines.append(line)

        return "\n\n".join(formatted_lines)

    @staticmethod
    def _format_projects_section(content: str) -> str:
        """Format projects section."""
        return ResumeFormatter._format_generic_section(content)

    @staticmethod
    def _format_generic_section(content: str) -> str:
        """Generic section formatting."""
        # Convert bullet points to LaTeX itemize
        lines = content.split("\n")
        formatted_lines = []
        in_itemize = False

        for line in lines:
            line = line.strip()
            if line.startswith("•") or line.startswith("-"):
                if not in_itemize:
                    formatted_lines.append("\\begin{itemize}[leftmargin=1em]")
                    in_itemize = True
                formatted_lines.append(f"\\item {line[1:].strip()}")
            else:
                if in_itemize:
                    formatted_lines.append("\\end{itemize}")
                    in_itemize = False
                if line:
                    formatted_lines.append(line)

        if in_itemize:
            formatted_lines.append("\\end{itemize}")

        return "\n".join(formatted_lines)

    @staticmethod
    def format_resume(
        resume_text: str,
        suggestions: str = "",
        style: LaTeXStyle = LaTeXStyle.MODERN,
        apply_suggestions: bool = False,
    ) -> str:
        """
        Format a complete resume with LaTeX markup.

        Args:
            resume_text: The original resume text
            suggestions: Optional improvement suggestions
            style: The LaTeX style to use
            apply_suggestions: Whether to apply suggestions to content

        Returns:
            Complete LaTeX-formatted resume
        """
        # Extract contact information
        contact_info = ResumeFormatter.extract_contact_info(resume_text)

        # Parse resume into sections
        sections = ResumeFormatter.parse_resume_sections(resume_text)

        # Generate LaTeX header
        latex_content = [ResumeFormatter.generate_latex_header(contact_info, style)]

        # Define section order
        section_order = [
            "summary",
            "experience",
            "skills",
            "projects",
            "education",
            "certifications",
            "achievements",
            "publications",
        ]

        # Add sections in order
        for section_name in section_order:
            if section_name in sections and sections[section_name].strip():
                # Format section title
                title = section_name.replace("_", " ").title()
                latex_content.append(f"\\section{{{title}}}")

                # Format section content
                formatted_content = ResumeFormatter.format_section_content(
                    section_name, sections[section_name]
                )
                if formatted_content:
                    latex_content.append(formatted_content)
                    latex_content.append("")

        # Add any remaining sections
        for section_name, content in sections.items():
            if section_name not in section_order and section_name != "header" and content.strip():
                title = section_name.replace("_", " ").title()
                latex_content.append(f"\\section{{{title}}}")
                formatted_content = ResumeFormatter.format_section_content(section_name, content)
                if formatted_content:
                    latex_content.append(formatted_content)
                    latex_content.append("")

        # Close document
        latex_content.append("\\end{document}")

        return "\n".join(latex_content)

    @staticmethod
    def combine_with_suggestions(resume_text: str, suggestions: str) -> str:
        """
        Combine resume text with improvement suggestions in a formatted way.

        Args:
            resume_text: The original resume text
            suggestions: The improvement suggestions

        Returns:
            Combined formatted text
        """
        # Format the resume part normally, but keep suggestions visible
        formatted_resume = ResumeFormatter.format_resume(resume_text, style=LaTeXStyle.MODERN)

        # Add suggestions as a comment in the LaTeX (will be visible in source but not rendered)
        suggestions_comment = (
            f"% IMPROVEMENT SUGGESTIONS:\n% {suggestions.replace(chr(10), chr(10) + '% ')}"
        )

        # Insert suggestions comment before \end{document}
        formatted_with_suggestions = formatted_resume.replace(
            "\\end{document}", f"{suggestions_comment}\n\\end{{document}}"
        )

        return formatted_with_suggestions
