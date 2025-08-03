import re
from enum import Enum
from typing import Any, Dict, List


class LaTeXStyle(Enum):
    """Available LaTeX formatting styles."""

    MODERN = "modern"
    CLASSIC = "classic"
    MINIMAL = "minimal"
    ACADEMIC = "academic"


class DocumentStyler:
    """
    Robust LaTeX document styler that combines text with professional formatting.
    """

    # LaTeX templates for different styles
    LATEX_TEMPLATES = {
        LaTeXStyle.MODERN: {
            "documentclass": r"\documentclass[11pt,a4paper]{article}",
            "packages": [
                r"\usepackage[utf8]{inputenc}",
                r"\usepackage[T1]{fontenc}",
                r"\usepackage{geometry}",
                r"\usepackage{titlesec}",
                r"\usepackage{enumitem}",
                r"\usepackage{hyperref}",
                r"\usepackage{xcolor}",
                r"\usepackage{fontawesome5}",
            ],
            "geometry": r"\geometry{top=1in, bottom=1in, left=0.75in, right=0.75in}",
            "colors": r"\definecolor{primarycolor}{RGB}{0, 102, 204}",
            "section_format": r"\titleformat{\section}{\large\bfseries\color{primarycolor}}{}{0em}{}[\titlerule]",
        },
        LaTeXStyle.CLASSIC: {
            "documentclass": r"\documentclass[11pt,a4paper]{article}",
            "packages": [
                r"\usepackage[utf8]{inputenc}",
                r"\usepackage[T1]{fontenc}",
                r"\usepackage{geometry}",
                r"\usepackage{enumitem}",
            ],
            "geometry": r"\geometry{top=1in, bottom=1in, left=1in, right=1in}",
            "colors": "",
            "section_format": "",
        },
        LaTeXStyle.MINIMAL: {
            "documentclass": r"\documentclass[10pt,a4paper]{article}",
            "packages": [
                r"\usepackage[utf8]{inputenc}",
                r"\usepackage{geometry}",
                r"\usepackage{enumitem}",
            ],
            "geometry": r"\geometry{top=0.75in, bottom=0.75in, left=0.75in, right=0.75in}",
            "colors": "",
            "section_format": r"\renewcommand{\section}[1]{\vspace{0.5em}\textbf{\large #1}\vspace{0.25em}\hrule\vspace{0.25em}]}",
        },
    }

    @staticmethod
    def style_document(
        text: str,
        style: LaTeXStyle = LaTeXStyle.MODERN,
    ) -> str:
        """
        Format a complete document with LaTeX markup.

        Args:
            text: The original text
            style: The LaTeX style to use

        Returns:
            Complete LaTeX-formatted document
        """
        # Generate LaTeX header
        latex_content = [DocumentStyler.generate_latex_header(style)]

        # Add the text
        latex_content.append(text)

        # Close document
        latex_content.append(r"\end{document}")

        return "\n".join(latex_content)

    @staticmethod
    def generate_latex_header(
        style: LaTeXStyle = LaTeXStyle.MODERN
    ) -> str:
        """
        Generate LaTeX document header.

        Args:
            style: The LaTeX style to use

        Returns:
            LaTeX header string
        """
        template: Dict[str, Any] = DocumentStyler.LATEX_TEMPLATES[style]

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
                r"\setlength{\parindent}{0pt}",
                r"\setlength{\parskip}{0.5em}",
                "",
                r"\begin{document}",
                "",
            ]
        )

        return "\n".join(header_parts)
