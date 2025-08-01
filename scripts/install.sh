#!/usr/bin/env bash
set -euo pipefail

# Default installation directory
INSTALL_DIR="${INSTALL_DIR:-/usr/local/bin}"
BEETUNE_VERSION="${BEETUNE_VERSION:-latest}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    error "Docker is required but not installed. Please install Docker first."
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    error "Docker is not running. Please start Docker first."
fi

# Check if install directory is writable
if [[ ! -w "$INSTALL_DIR" ]]; then
    if [[ "$EUID" -ne 0 ]]; then
        warn "Installation directory $INSTALL_DIR is not writable."
        warn "You may need to run this script with sudo or choose a different directory:"
        warn "  curl -sSL https://raw.githubusercontent.com/fumbl3b/beetune/main/scripts/install.sh | INSTALL_DIR=$HOME/.local/bin bash"
        error "Permission denied"
    fi
fi

# Create install directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Download and install the wrapper script
info "Installing beetune Docker wrapper to $INSTALL_DIR/beetune"

# For now, copy from local (in production this would download from GitHub)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/beetune-docker" ]]; then
    cp "$SCRIPT_DIR/beetune-docker" "$INSTALL_DIR/beetune"
    chmod +x "$INSTALL_DIR/beetune"
else
    # In production, download from GitHub
    curl -sSL "https://raw.githubusercontent.com/fumbl3b/beetune/main/scripts/beetune-docker" > "$INSTALL_DIR/beetune"
    chmod +x "$INSTALL_DIR/beetune"
fi

# Pre-pull the Docker image
info "Pre-pulling beetune Docker image..."
BEETUNE_REGISTRY="${BEETUNE_REGISTRY:-ghcr.io/fumbl3b}"
BEETUNE_IMAGE="${BEETUNE_REGISTRY}/beetune:${BEETUNE_VERSION}"

if docker pull "$BEETUNE_IMAGE"; then
    info "Successfully pulled $BEETUNE_IMAGE"
else
    warn "Failed to pull $BEETUNE_IMAGE - it will be pulled on first use"
fi

# Verify installation
if command -v beetune &> /dev/null; then
    info "✅ beetune installed successfully!"
    info "Usage: beetune --help"
    info ""
    info "Set your OpenAI API key:"
    info "  export OPENAI_API_KEY=your_api_key_here"
    info ""
    info "Then try:"
    info "  beetune version"
else
    warn "beetune was installed to $INSTALL_DIR/beetune but is not in your PATH"
    warn "Add $INSTALL_DIR to your PATH or create a symlink:"
    warn "  export PATH=\"$INSTALL_DIR:\$PATH\""
fi