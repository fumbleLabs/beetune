"""
File text extraction utilities for beetune.

Provides secure text extraction from various file formats including PDF, DOCX, and LaTeX.
"""

from typing import BinaryIO

import docx
import PyPDF2

from ..utils import ProcessingError


class FileProcessor:
    """Secure file text extraction for resume processing."""

    @staticmethod
    def extract_text(file_stream: BinaryIO, filename: str) -> str:
        """
        Extract text content from a file stream.

        Args:
            file_stream: Binary file stream to process
            filename: Original filename to determine processing method

        Returns:
            Extracted text content

        Raises:
            ProcessingError: If file type is unsupported or extraction fails
        """
        try:
            file_extension = filename.lower().split(".")[-1]

            if file_extension == "pdf":
                return FileProcessor._extract_from_pdf(file_stream)
            elif file_extension in ["docx", "doc"]:
                return FileProcessor._extract_from_docx(file_stream)
            elif file_extension == "tex":
                return file_stream.read().decode("utf-8")
            else:
                raise ProcessingError(f"Unsupported file type: {file_extension}")
        except Exception as e:
            if isinstance(e, ProcessingError):
                raise
            raise ProcessingError(f"Failed to extract text from {filename}: {str(e)}")

    @staticmethod
    def _extract_from_pdf(file_stream: BinaryIO) -> str:
        """Extract text from PDF file stream."""
        try:
            pdf_reader = PyPDF2.PdfReader(file_stream)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text.strip()
        except Exception as e:
            raise ProcessingError(f"Failed to process PDF file: {str(e)}")

    @staticmethod
    def _extract_from_docx(file_stream: BinaryIO) -> str:
        """Extract text from DOCX file stream."""
        try:
            doc = docx.Document(file_stream)
            return " ".join([paragraph.text for paragraph in doc.paragraphs]).strip()
        except Exception as e:
            raise ProcessingError(f"Failed to process DOCX file: {str(e)}")
