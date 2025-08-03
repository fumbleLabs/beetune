"""
beetune - Open-source document analysis and formatting engine.

This package provides tools for:
- Extracting text from files
- Analyzing text
- Formatting documents as professional LaTeX documents
- Generating AI-powered suggestions
"""

__version__ = "0.1.0"
__author__ = "Harry Winkler"
__email__ = "harry@fumblebee.site"

# Core functionality imports
from .processors import TextAnalyzer
from .config import AIProvider, Config, ConfigError, get_config
from .extractors import FileProcessor, FileUploadSecurity
from .renderers import DocumentStyler, UnifiedLatexConverter
from .prompts import OutputFormat, PromptTone, gen_analysis, gen_suggestions
from .utils import BeetuneError, ProcessingError, ValidationError

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",
    
    # Extractors
    "FileProcessor",
    "FileUploadSecurity",
    
    # Renderers
    "DocumentStyler", 
    "UnifiedLatexConverter",
    
    # Processors
    "TextAnalyzer",
    
    # Prompts
    "PromptTone",
    "OutputFormat", 
    "gen_analysis",
    "gen_suggestions",
    
    # Exceptions
    "BeetuneError",
    "ValidationError", 
    "ProcessingError",
    
    # Configuration
    "Config",
    "AIProvider",
    "ConfigError",
    "get_config",
]