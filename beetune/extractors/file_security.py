"""
File upload security utilities for beetune.

Provides comprehensive validation for file uploads including extension validation,
MIME type checking, and secure filename generation.
"""

from typing import Dict, Set, BinaryIO, Optional
import magic
from ..utils import ValidationError, ProcessingError


class FileUploadSecurity:
    """Security utilities for file uploads."""

    # Default allowed file extensions
    DEFAULT_ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "tex"}
    
    # MIME type mappings for allowed file extensions
    ALLOWED_MIME_TYPES: Dict[str, Set[str]] = {
        "pdf": {"application/pdf"},
        "doc": {"application/msword"},
        "docx": {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-word.document.macroEnabled.12",
        },
        "tex": {"text/plain", "application/x-tex", "text/x-tex"},
    }

    def __init__(self, allowed_extensions: Optional[Set[str]] = None):
        """
        Initialize file security validator.
        
        Args:
            allowed_extensions: Set of allowed file extensions. If None, uses defaults.
        """
        self.allowed_extensions = allowed_extensions or self.DEFAULT_ALLOWED_EXTENSIONS

    def validate_file_upload(self, file_stream: BinaryIO, filename: str) -> str:
        """
        Comprehensive file upload validation.

        Args:
            file_stream: Binary file stream to validate
            filename: Original filename

        Returns:
            str: Secure filename

        Raises:
            ValidationError: If file validation fails
            ProcessingError: If file processing fails
        """
        if not filename:
            raise ValidationError("Empty filename", "Uploaded file must have a valid filename")

        # Secure the filename
        secure_name = self._secure_filename(filename)
        if not secure_name:
            raise ValidationError("Invalid filename", "Filename contains only unsafe characters")

        # Validate file extension
        self._validate_extension(secure_name)

        # Validate MIME type
        self._validate_mime_type(file_stream, secure_name)

        return secure_name

    def _secure_filename(self, filename: str) -> str:
        """
        Generate a secure filename by removing dangerous characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Secure filename
        """
        # Basic secure filename implementation
        # Remove path separators and other dangerous characters
        import re
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Remove leading dots and underscores
        filename = filename.lstrip('._')
        
        # Ensure filename isn't empty after cleaning
        if not filename:
            return "upload"
            
        return filename

    def _validate_extension(self, filename: str) -> None:
        """Validate file extension against allowed extensions."""
        if "." not in filename:
            raise ValidationError("No file extension", "File must have a valid extension")

        extension = filename.lower().split(".")[-1]

        if extension not in self.allowed_extensions:
            allowed_extensions_str = ", ".join(sorted(self.allowed_extensions))
            raise ValidationError(
                "Invalid file extension",
                f"File extension '{extension}' not allowed. Allowed extensions: {allowed_extensions_str}",
            )

    def _validate_mime_type(self, file_stream: BinaryIO, filename: str) -> None:
        """Validate MIME type using python-magic."""
        try:
            # Reset file stream position
            current_pos = file_stream.tell()
            file_stream.seek(0)

            # Read a small portion of the file for MIME detection
            file_header = file_stream.read(1024)
            file_stream.seek(current_pos)  # Reset to original position

            if not file_header:
                raise ValidationError("Empty file", "Uploaded file appears to be empty")

            # Detect MIME type
            detected_mime = magic.from_buffer(file_header, mime=True)

            # Get expected MIME types for this extension
            extension = filename.lower().split(".")[-1]
            expected_mimes = self.ALLOWED_MIME_TYPES.get(extension, set())

            if expected_mimes and detected_mime not in expected_mimes:
                expected_mimes_str = ", ".join(sorted(expected_mimes))
                raise ValidationError(
                    "Invalid file type",
                    f"File content doesn't match extension. Expected MIME types: {expected_mimes_str}, "
                    f"but detected: {detected_mime}",
                )

        except ValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            raise ProcessingError(
                "File validation failed", f"Unable to validate file type: {str(e)}"
            )

    def get_file_info(self, file_stream: BinaryIO, filename: str) -> Dict[str, str]:
        """Get detailed file information for logging/debugging."""
        try:
            current_pos = file_stream.tell()
            file_stream.seek(0)
            
            file_header = file_stream.read(1024)
            file_stream.seek(0)
            file_content = file_stream.read()
            file_stream.seek(current_pos)

            detected_mime = magic.from_buffer(file_header, mime=True) if file_header else "unknown"

            return {
                "original_filename": filename,
                "secure_filename": self._secure_filename(filename),
                "detected_mime_type": detected_mime,
                "file_size_bytes": str(len(file_content)),
                "extension": filename.lower().split(".")[-1] if "." in filename else "none",
            }
        except Exception as e:
            return {"original_filename": filename, "error": f"Could not analyze file: {str(e)}"}