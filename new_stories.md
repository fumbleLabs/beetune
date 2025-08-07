1. Multi‑format output (DOCX/HTML/Markdown)

Currently the tool can only output LaTeX/PDF via ResumeFormatter and UnifiedLatexConverter. Adding a DocxFormatter and/or HtmlFormatter module would allow users to generate Word or HTML resumes directly. Libraries like python-docx could be used to assemble a DOCX document with styled sections (header, education, experience, skills). Similarly, Markdown export could be a lightweight option for web profiles. This would make the tool useful for applicants who need Word or web‑friendly resumes instead of LaTeX.

2. New Page Stubs

Lets create a comparison page where the user can see the diff between the two documents.  differences between the two should be highlighted with green for additions and red for deletions.

3. Improve LaTeX formatting

Let's improve the prompt for latex generation to be more specific about styling parameters and the way the final product should be laid out. Include total page count as well as other details from the main template.

4. Begin Backend Work to handle storage of previously generated documents.

5. Think through improvement engine.  Options should include - Improve, Design, No-Changes etc.
