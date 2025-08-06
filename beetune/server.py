"""
Flask web server for beetune API endpoints.

Replicates the functionality of the previous resume-backend with
Docker-first LaTeX compilation and file processing.
"""

# mypy: ignore-errors

import base64
import logging
import os
import tempfile
from io import BytesIO
from typing import Any, Dict, Tuple

from flask import Flask, jsonify, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from .config import get_config
from .extractors import FileProcessor, FileUploadSecurity
from .processors import TextAnalyzer
from .renderers import DocumentStyler, UnifiedLatexConverter
from .utils import BeetuneError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Global instances
file_processor = FileProcessor()
file_security = FileUploadSecurity()
text_analyzer = None
document_styler = None
latex_converter = None


def get_text_analyzer() -> TextAnalyzer:
    """Lazy-load text analyzer."""
    global text_analyzer
    if text_analyzer is None:
        config = get_config()
        api_key = config.get_api_key()
        endpoint = config.get_endpoint()
        model = config.get_model()
        text_analyzer = TextAnalyzer(api_key, base_url=endpoint, default_model=model)
    return text_analyzer


def get_document_styler() -> "DocumentStyler":
    """Lazy-load document styler."""
    global document_styler
    if document_styler is None:
        document_styler = DocumentStyler()
    return document_styler


def get_latex_converter() -> "UnifiedLatexConverter":
    """Lazy-load LaTeX converter."""
    global latex_converter
    if latex_converter is None:
        latex_converter = UnifiedLatexConverter()
    return latex_converter


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e) -> Tuple[Dict[str, Any], int]:
    """Handle file size limit exceeded."""
    return jsonify({"error": "File too large", "message": "Maximum file size is 16MB"}), 413


@app.errorhandler(BeetuneError)
def handle_beetune_exception(e) -> Tuple[Dict[str, Any], int]:
    """Handle beetune-specific exceptions."""
    return jsonify({"error": "BeetuneError", "message": str(e)}), 400


@app.errorhandler(Exception)
def handle_general_exception(e) -> Tuple[Dict[str, Any], int]:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({"error": "InternalServerError", "message": "An internal error occurred"}), 500


@app.route("/health", methods=["GET"])
def health_check() -> Tuple[Dict[str, Any], int]:
    """Health check endpoint."""
    try:
        # Check if LaTeX is available
        latex_available = True
        try:
            get_latex_converter()
        except Exception:
            latex_available = False

        # Check AI configuration
        ai_configured = get_config().is_configured()

        status = {
            "status": "healthy",
            "components": {
                "latex": "available" if latex_available else "unavailable",
                "ai_provider": "configured" if ai_configured else "not_configured",
                "file_processor": "ready",
            },
        }

        return jsonify(status), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route("/analyze/job", methods=["POST"])
def analyze_job() -> Tuple[Dict[str, Any], int]:
    """
    Analyze job description text using AI.

    Expected JSON payload:
    {
        "job_description": "Job description text..."
    }
    
    Returns analyzed content with insights and key information.
    """
    try:
        if not get_config().is_configured():
            return (
                jsonify({"error": "ConfigurationError", "message": "AI provider not configured"}),
                400,
            )

        data = request.get_json()
        if not data or "job_description" not in data:
            return jsonify({"error": "BadRequest", "message": "job_description is required"}), 400

        job_description = data["job_description"]

        # Perform analysis
        analyzer = get_text_analyzer()
        result = analyzer.analyze(job_description)

        return jsonify({"success": True, "analysis": result}), 200

    except Exception as e:
        logger.error(f"Job analysis error: {str(e)}", exc_info=True)
        return jsonify({"error": "AnalysisError", "message": f"Job analysis failed: {str(e)}"}), 500


@app.route("/resume/extract-text", methods=["POST"])
def extract_resume_text() -> Tuple[Dict[str, Any], int]:
    """
    Upload and extract text from resume files.

    Supports: PDF, DOC, DOCX, TXT files
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "BadRequest", "message": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "BadRequest", "message": "No file selected"}), 400

        # Security validation - check file extension
        try:
            file_security._validate_extension(file.filename or "")
        except Exception:
            return jsonify({"error": "InvalidFileType", "message": "File type not allowed"}), 400

        # Save file temporarily
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
            file.save(temp_file.name)

            try:
                # Validate file - use the proper validation method
                with open(temp_file.name, 'rb') as validation_file:
                    file_security.validate_file_upload(validation_file, filename)

                # Extract text
                with open(temp_file.name, 'rb') as f:
                    extracted_text = file_processor.extract_text(f, filename)

                return jsonify({"success": True, "text": extracted_text, "filename": filename}), 200

            finally:
                # Clean up temp file
                os.unlink(temp_file.name)

    except Exception as e:
        logger.error(f"Text extraction error: {str(e)}", exc_info=True)
        return (
            jsonify({"error": "ExtractionError", "message": f"Text extraction failed: {str(e)}"}),
            500,
        )


@app.route("/resume/suggest-improvements", methods=["POST"])
def suggest_resume_improvements() -> Tuple[Dict[str, Any], int]:
    """
    Analyze resume text and suggest improvements using AI.

    Expected JSON payload:
    {
        "resume_text": "Resume text...",
        "job_description": "Job description text..." (optional)
    }
    
    If job_description is provided, gives targeted suggestions.
    Otherwise, provides general resume analysis.
    """
    try:
        if not get_config().is_configured():
            return (
                jsonify({"error": "ConfigurationError", "message": "AI provider not configured"}),
                400,
            )

        data = request.get_json()
        if not data or "resume_text" not in data:
            return jsonify({"error": "BadRequest", "message": "resume_text is required"}), 400

        resume_text = data["resume_text"]
        job_description = data.get("job_description")

        # Perform analysis
        analyzer = get_text_analyzer()

        if job_description:
            # Targeted analysis with job description
            goal = f"Improve this resume to better match this job description: {job_description}"
            result = analyzer.suggest_improvements(resume_text, goal)
        else:
            # General resume analysis
            result = analyzer.analyze(resume_text)

        return jsonify({"success": True, "analysis": result}), 200

    except Exception as e:
        logger.error(f"Resume analysis error: {str(e)}", exc_info=True)
        return (
            jsonify({"error": "AnalysisError", "message": f"Resume analysis failed: {str(e)}"}),
            500,
        )


@app.route("/document/apply-improvements", methods=["POST"])
def apply_document_improvements() -> Tuple[Dict[str, Any], int]:
    """
    Apply LaTeX styling to document text.

    Expected JSON payload:
    {
        "resume_data": {...},  # Resume data (should contain 'content' field with text)
        "improvements": [...], # List of improvements (currently not used)
        "template": "professional" (optional) # professional=modern, other=classic
    }
    
    Returns LaTeX-formatted document source code.
    """
    try:
        if not get_config().is_configured():
            return (
                jsonify({"error": "ConfigurationError", "message": "AI provider not configured"}),
                400,
            )

        data = request.get_json()
        if not data or "resume_data" not in data:
            return jsonify({"error": "BadRequest", "message": "resume_data is required"}), 400

        resume_data = data["resume_data"]
        improvements = data.get("improvements", [])
        template = data.get("template", "professional")

        # Generate LaTeX document
        formatter = get_document_styler()
        # Convert resume_data to text format (assuming it's a dict with text content)
        resume_text = str(resume_data.get('content', resume_data))
        from .renderers import LaTeXStyle
        style = LaTeXStyle.MODERN if template == 'professional' else LaTeXStyle.CLASSIC
        latex_source = formatter.style_document(resume_text, style)

        return jsonify({"success": True, "latex_source": latex_source}), 200

    except Exception as e:
        logger.error(f"Resume formatting error: {str(e)}", exc_info=True)
        return (
            jsonify({"error": "FormattingError", "message": f"Resume formatting failed: {str(e)}"}),
            500,
        )


@app.route("/convert/latex", methods=["POST"])
def convert_latex_to_pdf() -> Tuple[Dict[str, Any], int]:
    """
    Convert LaTeX source to PDF.

    Expected JSON payload:
    {
        "latex_source": "LaTeX source code...",
        "return_format": "base64" | "binary" (optional, defaults to base64)
    }
    """
    try:
        data = request.get_json()
        if not data or "latex_source" not in data:
            return jsonify({"error": "BadRequest", "message": "latex_source is required"}), 400

        latex_source = data["latex_source"]
        return_format = data.get("return_format", "base64")

        # Compile LaTeX
        converter = get_latex_converter()
        result = converter.compile_latex(latex_source)

        if not result.success:
            return (
                jsonify(
                    {
                        "error": "CompilationError",
                        "message": result.error_message,
                        "log": result.log_output,
                    }
                ),
                400,
            )

        if return_format == "binary":
            # Return PDF as binary data
            pdf_data = base64.b64decode(result.pdf_base64)
            return send_file(
                BytesIO(pdf_data),
                mimetype="application/pdf",
                as_attachment=True,
                download_name="resume.pdf",
            )
        else:
            # Return base64 encoded PDF
            return (
                jsonify(
                    {
                        "success": True,
                        "latex_source": result.tex_base64,
                        "pdf_base64": result.pdf_base64,
                    }
                ),
                200,
            )

    except Exception as e:
        logger.error(f"LaTeX conversion error: {str(e)}", exc_info=True)
        return (
            jsonify({"error": "ConversionError", "message": f"LaTeX conversion failed: {str(e)}"}),
            500,
        )


@app.route("/", methods=["GET"])
def index() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return jsonify(
        {
            "service": "beetune-api",
            "version": "0.1.0",
            "endpoints": {
                "health": "GET /health",
                "analyze_job": "POST /analyze/job",
                "extract_text": "POST /resume/extract-text",
                "suggest_improvements": "POST /resume/suggest-improvements",
                "apply_improvements": "POST /document/apply-improvements",
                "convert_latex": "POST /convert/latex",
            },
        }
    )


def create_app() -> Flask:
    """Application factory."""
    return app


def main() -> None:
    """Entry point for beetune-server command."""
    import argparse

    parser = argparse.ArgumentParser(description="beetune server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
