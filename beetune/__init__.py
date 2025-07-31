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
from .extractors import FileProcessor, FileUploadSecurity
from .formatters import ResumeFormatter, UnifiedLatexConverter
from .analyzers import JobAnalyzer, ResumeAnalyzer
from .prompts import PromptTone, OutputFormat, gen_keywords, gen_benefits
from .utils import BeetuneException, ValidationError, ProcessingError
from .config import Config, AIProvider, ConfigError, get_config

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