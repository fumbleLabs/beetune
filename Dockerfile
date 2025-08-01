# Use Ubuntu with manual TeX Live installation for complete LaTeX environment
FROM ubuntu:22.04

# Install Python, TeX Live, and required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
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

# Copy project files
COPY pyproject.toml README.md LICENSE ./
COPY beetune/ ./beetune/

# Install beetune with server dependencies
RUN pip3 install --no-cache-dir .[server]

# Create non-root user for security with home directory
RUN groupadd -r beetune && useradd -r -g beetune -m beetune
RUN chown -R beetune:beetune /app
USER beetune

# Create config directory
RUN mkdir -p /home/beetune/.beetune

# Set up working directory for user files
WORKDIR /work

# Default entrypoint
ENTRYPOINT ["beetune"]