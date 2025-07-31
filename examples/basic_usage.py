#!/usr/bin/env python3
"""
Basic usage example for beetune.

This script demonstrates how to use beetune for resume processing and analysis.
"""

from beetune import FileProcessor, ResumeFormatter, JobAnalyzer
from beetune.formatters import LaTeXStyle
import os


def main():
    """Demonstrate basic beetune functionality."""
    
    # Example job description
    job_description = """
    Software Engineer - Python
    
    We are looking for a Python developer with experience in:
    - Python, Flask, Django
    - REST APIs and microservices
    - SQL databases (PostgreSQL, MySQL)
    - Docker and cloud deployment
    - Git version control
    
    Benefits:
    - Competitive salary $80,000-$120,000
    - Health insurance
    - Remote work options
    - Professional development budget
    """
    
    # Example resume text
    resume_text = """
    John Doe
    john.doe@email.com | (555) 123-4567
    
    Experience
    Software Developer | Tech Corp | 2020-2023
    • Developed web applications using Python and Flask
    • Built REST APIs serving 10,000+ daily requests
    • Worked with PostgreSQL databases
    
    Skills
    Python, JavaScript, SQL, Git, Docker
    
    Education
    Bachelor of Computer Science | University | 2020
    """
    
    print("🐝 beetune - Resume Analysis Demo")
    print("=" * 40)
    
    # 1. Format resume as LaTeX
    print("\n1. Formatting resume as LaTeX...")
    formatter = ResumeFormatter()
    latex_content = formatter.format_resume(resume_text, style=LaTeXStyle.MODERN)
    print(f"✅ Generated LaTeX document ({len(latex_content)} characters)")
    
    # 2. Analyze job description (requires OpenAI API key)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("\n2. Analyzing job description...")
        analyzer = JobAnalyzer(openai_key)
        
        try:
            analysis = analyzer.analyze_job_description(job_description)
            print(f"✅ Keywords: {analysis['keywords'][:100]}...")
            print(f"✅ Benefits: {analysis['benefits'][:100]}...")
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
    else:
        print("\n2. Skipping job analysis (OPENAI_API_KEY not set)")
    
    # 3. File processing example
    print("\n3. File processing capabilities:")
    processor = FileProcessor()
    
    # Test with LaTeX content
    from io import BytesIO
    tex_file = BytesIO(latex_content.encode())
    extracted_text = processor.extract_text(tex_file, "resume.tex")
    print(f"✅ Extracted {len(extracted_text)} characters from LaTeX")
    
    print("\n🎉 Demo complete!")
    print("\nNext steps:")
    print("- Set OPENAI_API_KEY to enable AI analysis")
    print("- Try with your own resume files")
    print("- Explore different LaTeX styles")


if __name__ == "__main__":
    main()