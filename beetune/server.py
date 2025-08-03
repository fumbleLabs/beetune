"""
Flask web server for beetune API endpoints.

Replicates the functionality of the previous resume-backend with
Docker-first LaTeX compilation and file processing.
"""

import base64
import logging
import os
import tempfile
from io import BytesIO

from flask import Flask, jsonify, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from .processors import TextAnalyzer
from .config import get_config
from .extractors import FileProcessor, FileUploadSecurity
from .renderers import DocumentStyler, UnifiedLatexConverter
from .utils import BeetuneException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global instances
config = get_config()
file_processor = FileProcessor()
file_security = FileUploadSecurity()
job_analyzer = None
resume_analyzer = None
resume_formatter = None
latex_converter = None


def get_job_analyzer():
    """Lazy-load job analyzer."""
    global job_analyzer
    if job_analyzer is None:
        job_analyzer = JobAnalyzer(config)
    return job_analyzer


def get_resume_analyzer():
    """Lazy-load resume analyzer."""
    global resume_analyzer
    if resume_analyzer is None:
        resume_analyzer = ResumeAnalyzer(config)
    return resume_analyzer


def get_resume_formatter():
    """Lazy-load resume formatter."""
    global resume_formatter
    if resume_formatter is None:
        resume_formatter = ResumeFormatter(config)
    return resume_formatter


def get_latex_converter():
    """Lazy-load LaTeX converter."""
    global latex_converter
    if latex_converter is None:
        latex_converter = UnifiedLatexConverter()
    return latex_converter


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    """Handle file size limit exceeded."""
    return jsonify({
        'error': 'File too large',
        'message': 'Maximum file size is 16MB'
    }), 413


@app.errorhandler(BeetuneError)
def handle_beetune_exception(e):
    """Handle beetune-specific exceptions."""
    return jsonify({
        'error': 'BeetuneError',
        'message': str(e)
    }), 400


@app.errorhandler(Exception)
def handle_general_exception(e):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({
        'error': 'InternalServerError',
        'message': 'An internal error occurred'
    }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Check if LaTeX is available
        latex_available = True
        try:
            get_latex_converter()
        except Exception:
            latex_available = False
        
        # Check AI configuration
        ai_configured = config.is_configured()
        
        status = {
            'status': 'healthy',
            'components': {
                'latex': 'available' if latex_available else 'unavailable',
                'ai_provider': 'configured' if ai_configured else 'not_configured',
                'file_processor': 'ready'
            }
        }
        
        return jsonify(status), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/analyze/job', methods=['POST'])
def analyze_job():
    """
    Analyze job description and extract keywords/requirements.
    
    Expected JSON payload:
    {
        "job_description": "Job description text..."
    }
    """
    try:
        if not config.is_configured():
            return jsonify({
                'error': 'ConfigurationError',
                'message': 'AI provider not configured'
            }), 400
        
        data = request.get_json()
        if not data or 'job_description' not in data:
            return jsonify({
                'error': 'BadRequest',
                'message': 'job_description is required'
            }), 400
        
        job_description = data['job_description']
        
        # Perform analysis
        analyzer = get_job_analyzer()
        result = analyzer.analyze_job_description(job_description)
        
        return jsonify({
            'success': True,
            'analysis': result
        }), 200
        
    except Exception as e:
        logger.error(f"Job analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'AnalysisError',
            'message': f'Job analysis failed: {str(e)}'
        }), 500


@app.route('/resume/extract-text', methods=['POST'])
def extract_resume_text():
    """
    Upload and extract text from resume files.
    
    Supports: PDF, DOC, DOCX, TXT files
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'BadRequest',
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'error': 'BadRequest',
                'message': 'No file selected'
            }), 400
        
        # Security validation
        if not file_security.is_allowed_file(file.filename):
            return jsonify({
                'error': 'InvalidFileType',
                'message': 'File type not allowed'
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
            file.save(temp_file.name)
            
            try:
                # Validate file
                if not file_security.validate_file(temp_file.name):
                    return jsonify({
                        'error': 'SecurityError',
                        'message': 'File failed security validation'
                    }), 400
                
                # Extract text
                extracted_text = file_processor.extract_text(temp_file.name)
                
                return jsonify({
                    'success': True,
                    'text': extracted_text,
                    'filename': filename
                }), 200
                
            finally:
                # Clean up temp file
                os.unlink(temp_file.name)
        
    except Exception as e:
        logger.error(f"Text extraction error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'ExtractionError',
            'message': f'Text extraction failed: {str(e)}'
        }), 500


@app.route('/resume/suggest-improvements', methods=['POST'])
def suggest_resume_improvements():
    """
    Analyze resume and suggest improvements.
    
    Expected JSON payload:
    {
        "resume_text": "Resume text...",
        "job_description": "Job description text..." (optional)
    }
    """
    try:
        if not config.is_configured():
            return jsonify({
                'error': 'ConfigurationError',
                'message': 'AI provider not configured'
            }), 400
        
        data = request.get_json()
        if not data or 'resume_text' not in data:
            return jsonify({
                'error': 'BadRequest',
                'message': 'resume_text is required'
            }), 400
        
        resume_text = data['resume_text']
        job_description = data.get('job_description')
        
        # Perform analysis
        analyzer = get_resume_analyzer()
        
        if job_description:
            # Targeted analysis with job description
            result = analyzer.analyze_resume_against_job(resume_text, job_description)
        else:
            # General resume analysis
            result = analyzer.analyze_resume(resume_text)
        
        return jsonify({
            'success': True,
            'analysis': result
        }), 200
        
    except Exception as e:
        logger.error(f"Resume analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'AnalysisError',
            'message': f'Resume analysis failed: {str(e)}'
        }), 500


@app.route('/document/apply-improvements', methods=['POST'])
def apply_document_improvements():
    """
    Generate improved LaTeX resume based on analysis.
    
    Expected JSON payload:
    {
        "resume_data": {...},  # Structured resume data
        "improvements": [...], # List of improvements to apply
        "template": "professional" (optional)
    }
    """
    try:
        if not config.is_configured():
            return jsonify({
                'error': 'ConfigurationError',
                'message': 'AI provider not configured'
            }), 400
        
        data = request.get_json()
        if not data or 'resume_data' not in data:
            return jsonify({
                'error': 'BadRequest',
                'message': 'resume_data is required'
            }), 400
        
        resume_data = data['resume_data']
        improvements = data.get('improvements', [])
        template = data.get('template', 'professional')
        
        # Generate LaTeX resume
        formatter = get_resume_formatter()
        latex_source = formatter.format_resume(resume_data, template, improvements)
        
        return jsonify({
            'success': True,
            'latex_source': latex_source
        }), 200
        
    except Exception as e:
        logger.error(f"Resume formatting error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'FormattingError',
            'message': f'Resume formatting failed: {str(e)}'
        }), 500


@app.route('/convert/latex', methods=['POST'])
def convert_latex_to_pdf():
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
        if not data or 'latex_source' not in data:
            return jsonify({
                'error': 'BadRequest',
                'message': 'latex_source is required'
            }), 400
        
        latex_source = data['latex_source']
        return_format = data.get('return_format', 'base64')
        
        # Compile LaTeX
        converter = get_latex_converter()
        result = converter.compile_latex(latex_source)
        
        if not result.success:
            return jsonify({
                'error': 'CompilationError',
                'message': result.error_message,
                'log': result.log_output
            }), 400
        
        if return_format == 'binary':
            # Return PDF as binary data
            pdf_data = base64.b64decode(result.pdf_base64)
            return send_file(
                BytesIO(pdf_data),
                mimetype='application/pdf',
                as_attachment=True,
                download_name='resume.pdf'
            )
        else:
            # Return base64 encoded PDF
            return jsonify({
                'success': True,
                'latex_source': result.tex_base64,
                'pdf_base64': result.pdf_base64
            }), 200
        
    except Exception as e:
        logger.error(f"LaTeX conversion error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'ConversionError',
            'message': f'LaTeX conversion failed: {str(e)}'
        }), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information."""
    return jsonify({
        'service': 'beetune-api',
        'version': '0.1.0',
        'endpoints': {
            'health': 'GET /health',
            'analyze_job': 'POST /analyze/job',
            'extract_text': 'POST /resume/extract-text',
            'suggest_improvements': 'POST /resume/suggest-improvements',
            'apply_improvements': 'POST /resume/apply-improvements',
            'convert_latex': 'POST /convert/latex'
        }
    })


def create_app():
    """Application factory."""
    return app


def main():
    """Entry point for beetune-server command."""
    import argparse
    
    parser = argparse.ArgumentParser(description='beetune server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()