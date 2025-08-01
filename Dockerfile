FROM python:3.11-slim

# Install system dependencies including LaTeX
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r beetune && useradd -r -g beetune beetune
RUN chown -R beetune:beetune /app
USER beetune

# Expose port for web service
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "beetune.server"]