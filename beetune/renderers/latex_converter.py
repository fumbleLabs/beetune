import base64
import logging
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class LaTeXValidationResult:
    """Result of LaTeX structure validation."""

    is_valid: bool
    missing_elements: List[str]
    warnings: List[str]


@dataclass
class LaTeXCompilationResult:
    """Result of LaTeX compilation."""

    success: bool
    tex_base64: str
    pdf_base64: Optional[str]
    log_output: str
    error_message: Optional[str]


class UnifiedLatexConverter:
    """
    Unified LaTeX converter that combines the functionality of LatexConverter and LatexConverter2.

    Features:
    - Comprehensive LaTeX structure validation
    - Two-pass pdflatex compilation for proper references
    - Base64-encoded output for both TEX and PDF
    - Robust error handling and logging
    - Installation validation
    """

    def __init__(self) -> None:
        """Initialize the converter and validate LaTeX installation."""
        self.validate_latex_installation()

    @staticmethod
    def validate_latex_installation() -> None:
        """
        Check if pdflatex is installed and accessible.

        Raises:
            RuntimeError: If pdflatex is not found or not working
        """
        try:
            result = subprocess.run(
                ["pdflatex", "--version"], capture_output=True, check=True, timeout=10
            )
            logger.debug(f"pdflatex version check successful: {result.stdout.decode()[:100]}...")
        except subprocess.TimeoutExpired:
            raise RuntimeError("pdflatex installation check timed out")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError("pdflatex not found. Please install TeX Live with pdflatex.") from e

    @staticmethod
    def validate_latex_structure(content: str) -> LaTeXValidationResult:
        """
        Validate LaTeX document structure and content.

        Args:
            content: The LaTeX content to validate

        Returns:
            LaTeXValidationResult with validation details
        """
        missing_elements = []
        warnings = []

        # Required elements for a valid LaTeX document
        required_elements = [
            (r"\\documentclass", "Document class declaration"),
            (r"\\begin{document}", "Document begin"),
            (r"\\end{document}", "Document end"),
        ]

        # Check for required elements
        for pattern, description in required_elements:
            if not re.search(pattern, content):
                missing_elements.append(f"Missing {description} ({pattern})")

        # Check for common issues that might cause compilation problems
        potential_issues = [
            (r"\\begin{document}.*\\begin{document}", "Multiple document beginnings detected"),
            (r"\\end{document}.*\\end{document}", "Multiple document endings detected"),
            (r"[^\\]%.*\\", "Potential unescaped percent sign in content"),
            (r"\\begin{(\w+)}(?!.*\\end{\1})", "Unmatched begin/end environment pairs"),
        ]

        for pattern, warning in potential_issues:
            if re.search(pattern, content, re.DOTALL):
                warnings.append(warning)

        # Check document order (documentclass should come before begin{document})
        doc_class_pos = content.find("\\documentclass")
        begin_doc_pos = content.find("\\begin{document}")

        if doc_class_pos > begin_doc_pos and doc_class_pos != -1 and begin_doc_pos != -1:
            warnings.append("Document class should appear before \\begin{document}")

        # Check for basic LaTeX packages that might be needed
        common_commands = [
            (
                "\\usepackage{geometry}",
                r"\\geometry\{",
                "geometry package needed for \\geometry command",
            ),
            (
                "\\usepackage{xcolor}",
                r"\\color\{|\\definecolor",
                "xcolor package needed for color commands",
            ),
            ("\\usepackage{hyperref}", r"\\href\{|\\url\{", "hyperref package needed for links"),
            (
                "\\usepackage{enumitem}",
                r"\\begin{itemize}.*\[.*\]",
                "enumitem package recommended for itemize options",
            ),
        ]

        for package, command_pattern, suggestion in common_commands:
            if re.search(command_pattern, content) and package not in content:
                warnings.append(suggestion)

        is_valid = len(missing_elements) == 0

        return LaTeXValidationResult(
            is_valid=is_valid, missing_elements=missing_elements, warnings=warnings
        )

    def compile_latex(
        self, content: str, validate_structure: bool = True
    ) -> LaTeXCompilationResult:
        """
        Compile LaTeX content to PDF with comprehensive error handling.

        Args:
            content: The LaTeX content to compile
            validate_structure: Whether to perform structure validation first

        Returns:
            LaTeXCompilationResult with compilation details
        """
        logger.debug("Starting unified LaTeX conversion...")

        # Structure validation
        if validate_structure:
            validation = self.validate_latex_structure(content)
            if not validation.is_valid:
                error_msg = f"Invalid LaTeX structure: {'; '.join(validation.missing_elements)}"
                logger.error(error_msg)
                return LaTeXCompilationResult(
                    success=False,
                    tex_base64="",
                    pdf_base64=None,
                    log_output="",
                    error_message=error_msg,
                )

            if validation.warnings:
                for warning in validation.warnings:
                    logger.warning(f"LaTeX validation warning: {warning}")

        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, "document.tex")
            pdf_file = os.path.join(temp_dir, "document.pdf")
            log_file = os.path.join(temp_dir, "document.log")

            try:
                # Write LaTeX content to file
                with open(tex_file, "w", encoding="utf-8") as f:
                    f.write(content)

                # Read tex content for base64 encoding
                with open(tex_file, "rb") as f:
                    tex_base64 = base64.b64encode(f.read()).decode("utf-8")

                log_content = ""

                # Compile LaTeX twice for proper references and cross-references
                for pass_num in range(1, 3):
                    logger.debug(f"LaTeX compilation pass {pass_num}/2")

                    process = subprocess.run(
                        [
                            "pdflatex",
                            "-interaction=nonstopmode",
                            "-file-line-error",
                            "-halt-on-error",
                            tex_file,
                        ],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=60,  # 60 second timeout
                    )

                    # Read log file if it exists
                    if os.path.exists(log_file):
                        with open(log_file, encoding="utf-8", errors="ignore") as f:
                            log_content = f.read()

                    # Check if compilation failed
                    if process.returncode != 0:
                        error_output = f"Pass {pass_num} failed:\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}\nLOG:\n{log_content}"
                        logger.error(
                            f"LaTeX compilation failed on pass {pass_num}:\n{error_output}"
                        )

                        return LaTeXCompilationResult(
                            success=False,
                            tex_base64=tex_base64,
                            pdf_base64=None,
                            log_output=log_content,
                            error_message=f"LaTeX compilation error on pass {pass_num}: {process.stderr}",
                        )

                    logger.debug(f"Pass {pass_num} completed successfully")

                # Check if PDF was generated
                if not os.path.exists(pdf_file):
                    error_msg = "PDF file was not generated despite successful compilation"
                    logger.error(error_msg)
                    return LaTeXCompilationResult(
                        success=False,
                        tex_base64=tex_base64,
                        pdf_base64=None,
                        log_output=log_content,
                        error_message=error_msg,
                    )

                # Read PDF content for base64 encoding
                with open(pdf_file, "rb") as f:
                    pdf_base64 = base64.b64encode(f.read()).decode("utf-8")

                logger.debug("LaTeX compilation completed successfully")

                return LaTeXCompilationResult(
                    success=True,
                    tex_base64=tex_base64,
                    pdf_base64=pdf_base64,
                    log_output=log_content,
                    error_message=None,
                )

            except subprocess.TimeoutExpired:
                error_msg = "LaTeX compilation timed out after 60 seconds"
                logger.error(error_msg)
                return LaTeXCompilationResult(
                    success=False,
                    tex_base64=tex_base64 if "tex_base64" in locals() else "",
                    pdf_base64=None,
                    log_output=log_content if "log_content" in locals() else "",
                    error_message=error_msg,
                )
            except Exception as e:
                error_msg = f"Unexpected error during LaTeX compilation: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return LaTeXCompilationResult(
                    success=False,
                    tex_base64=tex_base64 if "tex_base64" in locals() else "",
                    pdf_base64=None,
                    log_output=log_content if "log_content" in locals() else "",
                    error_message=error_msg,
                )

    def compile_latex_simple(self, content: str) -> Tuple[str, Optional[str]]:
        """
        Simple interface that maintains compatibility with existing code.

        Args:
            content: The LaTeX content to compile

        Returns:
            Tuple of (tex_base64, pdf_base64), where pdf_base64 is None on failure

        Raises:
            ValueError: If LaTeX structure is invalid
            RuntimeError: If compilation fails
        """
        result = self.compile_latex(content)

        if not result.success:
            if result.error_message and "Invalid LaTeX structure" in result.error_message:
                raise ValueError(result.error_message)
            else:
                raise RuntimeError(result.error_message)

        return result.tex_base64, result.pdf_base64
