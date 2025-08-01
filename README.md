# 🐝 beetune

**beetune** is an open-source resume analysis and LaTeX formatting engine. It provides powerful tools for processing resumes, analyzing job descriptions, and generating professionally formatted documents.

## Features

- **Resume Text Extraction**: Extract text from PDF, DOCX, and LaTeX files
- **Job Analysis**: Extract keywords and benefits from job descriptions using AI
- **LaTeX Formatting**: Convert resumes to professional LaTeX documents with multiple styles
- **Secure File Processing**: Comprehensive validation and security for file uploads
- **AI-Powered Suggestions**: Generate resume improvement suggestions using OpenAI

## Installation

### 🐳 Docker (Recommended)

The easiest way to use beetune is via Docker, which includes a complete LaTeX environment:

```bash
# One-line install (requires Docker)
curl -sSL https://raw.githubusercontent.com/fumbl3b/beetune/main/scripts/install.sh | bash

# Or pull the image directly
docker pull ghcr.io/fumbl3b/beetune:latest

# Set your API key
export OPENAI_API_KEY=your_api_key_here

# Use beetune normally
beetune --help
beetune version
```

### 🧪 Library Only (pip)

For library usage without LaTeX compilation:

```bash
pip install beetune
```

**Note**: The pip version excludes LaTeX compilation. For PDF generation, use the Docker version or install a LaTeX distribution separately.

## Quick Start

### 🐳 Docker CLI

```bash
# Configure your AI provider
beetune setup

# Analyze a job description
beetune analyze-job job_description.txt

# Format a resume as LaTeX/PDF
beetune format-resume resume.pdf --output resume.tex

# Check configuration
beetune config --list
```

### 🚀 API Server

Run beetune as a web service (great for business platforms):

```bash
# Development server
docker run -p 8000:8000 -e OPENAI_API_KEY=$OPENAI_API_KEY ghcr.io/fumbl3b/beetune:latest server

# Or with docker-compose
docker-compose up beetune-api
```

Available endpoints:
- `POST /analyze/job` - Analyze job descriptions
- `POST /resume/extract-text` - Extract text from uploaded files
- `POST /resume/suggest-improvements` - AI-powered resume analysis
- `POST /convert/latex` - Compile LaTeX to PDF
- `GET /health` - Health check

### CLI Setup (pip version)

First, configure your AI provider:

```bash
# Interactive setup
beetune setup

# Or with testing
beetune setup --test
```

### Basic Usage

```bash
# Analyze a job description
beetune analyze-job job_description.txt

# Format a resume as LaTeX
beetune format-resume resume.pdf --output resume.tex

# Check configuration
beetune config
beetune config --list
```

### Python API

```python
from beetune.extractors import FileProcessor
from beetune.formatters import ResumeFormatter
from beetune.analyzers import JobAnalyzer

# Extract text from a resume file
with open('resume.pdf', 'rb') as f:
    resume_text = FileProcessor.extract_text(f, 'resume.pdf')

# Analyze a job description (uses configured provider)
from beetune.config import get_config
config = get_config()
analyzer = JobAnalyzer(
    config.get_api_key(),
    base_url=config.get_endpoint(),
    default_model=config.get_model()
)
analysis = analyzer.analyze_job_description(job_description)
print(f"Keywords: {analysis['keywords']}")
print(f"Benefits: {analysis['benefits']}")

# Format resume as LaTeX
formatter = ResumeFormatter()
latex_content = formatter.format_resume(resume_text)
```

## Modules

### Extractors
- `FileProcessor`: Extract text from various file formats
- `FileUploadSecurity`: Validate and secure file uploads

### Formatters  
- `ResumeFormatter`: Convert resumes to LaTeX with professional styling
- `UnifiedLatexConverter`: Compile LaTeX to PDF with validation

### Analyzers
- `JobAnalyzer`: Extract insights from job descriptions
- `ResumeAnalyzer`: Analyze resume content and suggest improvements

### Prompts
- Enhanced prompt generation with parameterization support
- Multiple output formats and tone options

### Configuration
- `Config`: Manage AI provider settings
- Support for OpenAI, Anthropic, Ollama, and custom APIs
- Secure local storage of API keys and endpoints

## Configuration

beetune supports multiple AI providers:

### OpenAI
```bash
beetune setup
# Select: 1. openai
# Enter your OpenAI API key
# Default model: gpt-4o
```

### Anthropic Claude
```bash
beetune setup  
# Select: 2. anthropic
# Enter your Anthropic API key
# Default model: claude-3-5-sonnet-20241022
```

### Ollama (Local)
```bash
beetune setup
# Select: 3. ollama
# Endpoint: http://localhost:11434/v1 (default)
# Model: llama3.2, mistral, etc.
```

### Custom API
```bash
beetune setup
# Select: 4. custom
# Enter your custom endpoint URL
# Enter your API key and model
```

Configuration is stored securely in `~/.beetune/config.json` with restricted file permissions.

## Requirements

- Python 3.8+
- AI provider API key (OpenAI, Anthropic, etc.) or local Ollama installation
- LaTeX installation (for PDF generation)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.