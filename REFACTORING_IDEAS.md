# Refactoring Plan: Generalizing Beetune

The goal is to shift Beetune from a resume-specific tool to a general-purpose document improvement and formatting engine. This involves abstracting away resume-centric logic and creating a more flexible, template-driven architecture.

## 1. Rename Core Modules and Files

-   **`beetune/analyzers/` -> `beetune/processors/` or `beetune/enhancers/`**: This module will handle all forms of text analysis and improvement.
-   **`beetune/analyzers/resume_analyzer.py` & `beetune/analyzers/job_analyzer.py` -> `beetune/processors/text_analyzer.py`**: This new file will contain classes for different analysis types (e.g., `StyleAnalyzer`, `KeywordExtractor`, `SuggestionGenerator`).
-   **`beetune/formatters/resume_formatter.py` -> `beetune/renderers/document_styler.py` or `beetune/formatters/template_engine.py`**: This will apply various styles or templates to any document.

## 2. Introduce a Templating System

-   Create a new top-level directory: `templates/`.
-   This directory will house different output templates, organized by type (e.g., `latex`, `markdown`).
    ```
    templates/
    ├───latex/
    │   ├───modern_report/
    │   │   └───template.tex
    │   └───classic_letter/
    │       └───template.tex
    └───markdown/
        └───github_flavored.md
    ```
-   The `document_styler.py` will be responsible for loading a document's text and injecting it into one of these templates.

## 3. Generalize the CLI and API

-   **CLI Commands:**
    -   `beetune analyze-job ...` -> `beetune analyze text ...`
    -   `beetune format-resume ...` -> `beetune format document <file> --template modern_report`
    -   **New Command:** `beetune improve text <file> --goal "make it more concise"`
-   **API Endpoints:**
    -   `POST /analyze/job` -> `POST /analyze/text`
    -   `POST /resume/suggest-improvements` -> `POST /document/improve`
    -   `POST /convert/latex` -> `POST /render/pdf`

## 4. Update Prompts and Configuration

-   **Prompts (`prompts/generators.py`):** Rewrite prompts to be more general (e.g., "Rewrite the following text to have a more professional tone.").
-   **Configuration (`config.py`):** No major changes are expected as the configuration system is already flexible.

## 5. New Project Name

-   Consider renaming the project from **beetune** to something more general like `doctune`, `textcraft`, or `scribe` to align with the new vision.
