"""Tests for beetune extractors module."""

from io import BytesIO

import pytest

from beetune.extractors import FileProcessor, FileUploadSecurity
from beetune.utils import ProcessingError, ValidationError


class TestFileProcessor:
    """Test file processing functionality."""

    def test_extract_text_pdf_unsupported(self):
        """Test that unsupported file types raise appropriate errors."""
        processor = FileProcessor()
        
        with pytest.raises(ProcessingError) as exc_info:
            processor.extract_text(BytesIO(b"test"), "test.xyz")
        
        assert "Unsupported file type" in str(exc_info.value)

    def test_extract_text_tex(self):
        """Test LaTeX file text extraction."""
        processor = FileProcessor()
        tex_content = "\\documentclass{article}\\begin{document}Hello World\\end{document}"
        
        result = processor.extract_text(BytesIO(tex_content.encode()), "test.tex")
        assert result == tex_content


class TestFileUploadSecurity:
    """Test file upload security functionality."""

    def test_validate_empty_filename(self):
        """Test that empty filenames are rejected."""
        security = FileUploadSecurity()
        
        with pytest.raises(ValidationError) as exc_info:
            security.validate_file_upload(BytesIO(b"test"), "")
        
        assert "Empty filename" in str(exc_info.value)

    def test_validate_no_extension(self):
        """Test that files without extensions are rejected."""
        security = FileUploadSecurity()
        
        with pytest.raises(ValidationError) as exc_info:
            security.validate_file_upload(BytesIO(b"test"), "noextension")
        
        assert "No file extension" in str(exc_info.value)

    def test_secure_filename(self):
        """Test secure filename generation."""
        security = FileUploadSecurity()
        
        # Test basic cleaning
        result = security._secure_filename("test file.pdf")
        assert result == "test_file.pdf"
        
        # Test dangerous characters
        result = security._secure_filename("../../../etc/passwd")
        assert result == "etc_passwd"