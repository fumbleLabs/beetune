# Use official TeX Live image for complete LaTeX environment
FROM texlive/texlive:2024 as base

# Install Python and required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
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

# Create non-root user for security
RUN groupadd -r beetune && useradd -r -g beetune beetune
RUN chown -R beetune:beetune /app
USER beetune

# Set up working directory for user files
WORKDIR /work

# Default entrypoint
ENTRYPOINT ["beetune"]