"""
beetune - Open-source resume analysis and LaTeX formatting engine.

This package provides tools for:
- Extracting text from resume files
- Analyzing job descriptions
- Formatting resumes as professional LaTeX documents
- Generating AI-powered resume suggestions
"""

__version__ = "0.1.0"
__author__ = "Harry Winkler"
__email__ = "harry@fumblebee.site"

# Core functionality imports
from .analyzers import JobAnalyzer, ResumeAnalyzer
from .config import AIProvider, Config, ConfigError, get_config
from .extractors import FileProcessor, FileUploadSecurity
from .formatters import ResumeFormatter, UnifiedLatexConverter
from .prompts import OutputFormat, PromptTone, gen_benefits, gen_keywords
from .utils import BeetuneException, ProcessingError, ValidationError

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",
    
    # Extractors
    "FileProcessor",
    "FileUploadSecurity",
    
    # Formatters
    "ResumeFormatter", 
    "UnifiedLatexConverter",
    
    # Analyzers
    "JobAnalyzer",
    "ResumeAnalyzer",
    
    # Prompts
    "PromptTone",
    "OutputFormat", 
    "gen_keywords",
    "gen_benefits",
    
    # Exceptions
    "BeetuneException",
    "ValidationError", 
    "ProcessingError",
    
    # Configuration
    "Config",
    "AIProvider",
    "ConfigError",
    "get_config",
]