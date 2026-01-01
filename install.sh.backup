#!/bin/bash

# Blonde CLI Installer for Unix/Linux/macOS
# Usage: curl -fsSL https://raw.githubusercontent.com/cerekinorg/Blonde-Blip/main/install.sh | bash

set -e

BLONDE_VERSION="1.0.0"
INSTALL_DIR="${HOME}/.blonde"
VENV_DIR="${INSTALL_DIR}/venv"
BIN_DIR="${HOME}/.local/bin"
REPO_URL="https://github.com/cerekinorg/Blonde-Blip.git"
REPO_DIR="${INSTALL_DIR}/repo"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${2}${1}${NC}"
}

print_header() {
    echo ""
    print_msg "═══════════════════════════════════════════════════" "${BLUE}"
    print_msg "   🚀 Blonde CLI Installer v${BLONDE_VERSION}" "${BLUE}"
    print_msg "═══════════════════════════════════════════════════" "${BLUE}"
    echo ""
}

print_step() {
    print_msg "▶ $1" "${YELLOW}"
}

print_success() {
    print_msg "✓ $1" "${GREEN}"
}

print_error() {
    print_msg "✗ $1" "${RED}"
}

print_info() {
    print_msg "ℹ $1" "${BLUE}"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        print_error "Windows detected. Please use install.ps1 instead."
        exit 1
    else
        print_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
    print_success "Detected OS: $OS"
}

# Check Python installation
check_python() {
    print_step "Checking Python installation..."

    if command -v python3 &> /dev/null; then
        PYTHON=python3
    elif command -v python &> /dev/null; then
        PYTHON=python
    else
        print_error "Python 3.8+ is not installed"
        print_info "Please install Python 3.8 or higher from https://www.python.org/"
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
    print_success "Found Python $PYTHON_VERSION"
}

# Create directories
create_directories() {
    print_step "Creating directories..."

    mkdir -p "$INSTALL_DIR"
    mkdir -p "${INSTALL_DIR}/models"
    mkdir -p "${INSTALL_DIR}/cache"
    mkdir -p "${INSTALL_DIR}/memory"
    mkdir -p "${INSTALL_DIR}/logs"
    mkdir -p "$BIN_DIR"

    print_success "Directories created"
}

# Clone or update repository
get_source() {
    print_step "Downloading Blonde CLI..."

    if [ -d "$REPO_DIR" ]; then
        print_info "Updating existing installation..."
        cd "$REPO_DIR"
        git pull origin main || git pull origin master || print_info "No updates available"
    else
        git clone "$REPO_URL" "$REPO_DIR"
    fi

    print_success "Source downloaded"
}

# Create virtual environment
create_venv() {
    print_step "Creating virtual environment..."

    if [ -d "$VENV_DIR" ]; then
        print_info "Virtual environment already exists"
    else
        $PYTHON -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    fi
}

# Install dependencies
install_dependencies() {
    print_step "Installing dependencies..."

    # Activate virtual environment
    source "${VENV_DIR}/bin/activate"

    # Upgrade pip
    pip install --upgrade pip --quiet

    # Install requirements
    if [ -f "${REPO_DIR}/requirements.txt" ]; then
        pip install -r "${REPO_DIR}/requirements.txt" --quiet
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi

    # Install as editable package
    if [ -f "${REPO_DIR}/pyproject.toml" ]; then
        pip install -e "${REPO_DIR}" --quiet
        print_success "Blonde CLI installed"
    fi

    deactivate
}

# Create symlink
create_symlink() {
    print_step "Creating 'blonde' command..."

    # Remove old symlink if exists
    rm -f "${BIN_DIR}/blonde"
    rm -f "${BIN_DIR}/blnd"

    # Create new symlink
    ln -s "${VENV_DIR}/bin/blonde" "${BIN_DIR}/blonde"
    print_success "Command 'blonde' created"
}

# Add to PATH if needed
check_path() {
    if [[ ":$PATH:" != *":${BIN_DIR}:"* ]]; then
        print_info ""
        print_info "⚠️  ${BIN_DIR} is not in your PATH" "${YELLOW}"
        print_info ""
        print_info "Add this to your shell configuration (~/.bashrc, ~/.zshrc, etc.):"
        print_info ""
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
        print_info ""
        print_info "Then run: source ~/.bashrc  # or ~/.zshrc"
        print_info ""
    fi
}

# Migrate existing configuration
migrate_config() {
    print_step "Checking for existing configuration..."

    if [ -f ".env" ]; then
        print_info "Found existing .env file"
        print_info "Creating backup..."

        BACKUP_FILE="${INSTALL_DIR}/.env.backup.$(date +%Y%m%d_%H%M%S)"
        cp .env "$BACKUP_FILE"

        print_info "Configuration will be migrated during first run"
    fi

    print_success "Configuration check complete"
}

# Run setup wizard
run_setup_wizard() {
    print_step "Running setup wizard..."

    source "${VENV_DIR}/bin/activate"

    # Check if wizard exists and run it
    if [ -f "${REPO_DIR}/tui/setup_wizard.py" ]; then
        $PYTHON "${REPO_DIR}/tui/setup_wizard.py"
    else
        print_info "Setup wizard will run on first 'blonde' command"
    fi

    deactivate
}

# Print success message
print_success_message() {
    print_header
    print_success "Installation complete!"
    echo ""
    print_info "To start using Blonde CLI:"
    echo ""
    print_msg "  blonde" "${GREEN}"
    echo ""
    print_info "If you see 'command not found', add to PATH:"
    echo ""
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    print_info "Documentation: https://github.com/cerekinorg/Blonde-Blip#readme"
    echo ""
    print_msg "═══════════════════════════════════════════════════" "${BLUE}"
    echo ""
}

# Main installation flow
main() {
    print_header
    print_info "This will install Blonde CLI to ${INSTALL_DIR}"
    echo ""
    read -p "Continue? [Y/n] " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
        print_info "Installation cancelled"
        exit 0
    fi

    detect_os
    check_python
    create_directories
    get_source
    create_venv
    install_dependencies
    create_symlink
    check_path
    migrate_config
    # run_setup_wizard  # Optional: can run on first 'blonde' command
    print_success_message
}

# Run main function
main
