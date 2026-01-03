#!/bin/bash

# Blonde CLI Installer for Unix/Linux/macOS
# Usage: curl -fsSL https://raw.githubusercontent.com/cerekinorg/Blonde-Blip/main/install.sh | bash

# Error handling and debugging
set -euo pipefail
trap 'echo "ERROR: Failed at line $LINENO"; exit 1' ERR
trap 'echo "INTERRUPTED"; exit 130' INT

BLONDE_VERSION="1.0.0"
INSTALL_DIR="${HOME}/.blonde"
VENV_DIR="${INSTALL_DIR}/venv"
BIN_DIR="${HOME}/.local/bin"
REPO_URL="https://github.com/cerekinorg/Blonde-Blip.git"
REPO_DIR="${INSTALL_DIR}/repo"

# Debug mode (only enabled when user sets DEBUG=1)
DEBUG="${DEBUG:-0}"

# Installation log
LOG_FILE="${INSTALL_DIR}/logs/install_$(date +%Y%m%d_%H%M%S).log"

log_to_file() {
    if [ -d "${INSTALL_DIR}/logs" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    fi
}

log_to_file "Installer started"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test color support
if [ -t 1 ]; then
    log_to_file "Terminal supports colors"
else
    log_to_file "No color support, using plain output"
    # Disable colors for piped output
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Print colored message
print_msg() {
    echo -e "${2}${1}${NC}"
    log_to_file "${2}${1}"
}

print_header() {
    echo ""
    print_msg "═════════════════════════════════════════════════" "${BLUE}"
    print_msg "   🚀 Blonde CLI Installer v${BLONDE_VERSION}" "${BLUE}"
    print_msg "═════════════════════════════════════════════════" "${BLUE}"
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

debug_log() {
    if [ "$DEBUG" -eq 1 ]; then
        echo "[DEBUG] $1" >&2
        log_to_file "[DEBUG] $1"
    fi
}

debug_log "Home: $HOME"
debug_log "Install dir: $INSTALL_DIR"
debug_log "Log file: $LOG_FILE"

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --yes|-y|--silent|-s)
                AUTO_CONFIRM=1
                debug_log "Auto-confirm mode enabled"
                shift
                ;;
            --help|-h)
                echo "Blonde CLI Installer"
                echo ""
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --yes, -y     Skip confirmation prompt"
                echo "  --silent, -s   Skip confirmation and reduce output"
                echo "  --debug, -d    Enable debug logging (set DEBUG=1)"
                echo "  --help, -h     Show this help"
                exit 0
                ;;
            --debug|-d)
                DEBUG=1
                shift
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage"
                exit 1
                ;;
        esac
    done
}

# Parse arguments
parse_args "$@"

# Detect OS
detect_os() {
    debug_log "Detecting OS..."
    
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
    
    debug_log "OS detected: $OS"
    print_success "Detected OS: $OS"
}

# Check Python installation
check_python() {
    debug_log "Checking Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON=python3
        debug_log "Found python3"
    elif command -v python &> /dev/null; then
        PYTHON=python
        debug_log "Found python"
    else
        print_error "Python 3.8+ is not installed"
        print_info "Please install Python 3.8 or higher from https://www.python.org/"
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
    debug_log "Python version: $PYTHON_VERSION"
    print_success "Found Python $PYTHON_VERSION"
}

# Create directories
create_directories() {
    debug_log "Creating directories..."
    
    mkdir -p "$INSTALL_DIR" || {
        print_error "Failed to create $INSTALL_DIR"
        exit 1
    }
    mkdir -p "${INSTALL_DIR}/models" || {
        print_error "Failed to create models directory"
        exit 1
    }
    mkdir -p "${INSTALL_DIR}/cache" || {
        print_error "Failed to create cache directory"
        exit 1
    }
    mkdir -p "${INSTALL_DIR}/memory" || {
        print_error "Failed to create memory directory"
        exit 1
    }
    mkdir -p "${INSTALL_DIR}/logs" || {
        print_error "Failed to create logs directory"
        exit 1
    }
    mkdir -p "$BIN_DIR" || {
        print_error "Failed to create $BIN_DIR"
        exit 1
    }

    debug_log "All directories created"
    print_success "Directories created"
}

# Clone or update repository
get_source() {
    debug_log "Downloading source code..."
    
    if [ -d "$REPO_DIR" ]; then
        print_info "Updating existing installation..."
        cd "$REPO_DIR" || {
            print_error "Failed to cd to $REPO_DIR"
            exit 1
        }
        
        if git pull origin main 2>&1; then
            debug_log "Git pull succeeded (main branch)"
        elif git pull origin master 2>&1; then
            debug_log "Git pull succeeded (master branch)"
        else
            debug_log "No updates available"
            print_info "No updates available"
        fi
    else
        debug_log "Cloning repository: $REPO_URL"
        if git clone "$REPO_URL" "$REPO_DIR" 2>&1; then
            debug_log "Git clone succeeded"
        else
            print_error "Failed to clone repository"
            exit 1
        fi
    fi

    print_success "Source downloaded"
}

# Create virtual environment
create_venv() {
    debug_log "Creating virtual environment..."
    
    if [ -d "$VENV_DIR" ]; then
        print_info "Virtual environment already exists"
    else
        $PYTHON -m venv "$VENV_DIR" || {
            print_error "Failed to create virtual environment"
            exit 1
        }
        debug_log "Virtual environment created"
        print_success "Virtual environment created"
    fi
}

# Install dependencies
install_dependencies() {
    debug_log "Installing dependencies..."
    
    if [ ! -f "${VENV_DIR}/bin/activate" ]; then
        print_error "Virtual environment not found at $VENV_DIR"
        print_info "Please run create_venv first"
        exit 1
    fi
    
    # Activate virtual environment
    source "${VENV_DIR}/bin/activate" || {
        print_error "Failed to activate virtual environment"
        exit 1
    }
    
    debug_log "Virtual environment activated"

    # Upgrade pip
    pip install --upgrade pip --quiet || {
        print_error "Failed to upgrade pip"
        exit 1
    }
    
    debug_log "Pip upgraded"
    
    # Install Textual (required for new TUI)
    print_info "Installing Textual TUI framework..."
    pip install "textual>=0.44.0" --quiet || {
        print_error "Failed to install Textual"
        exit 1
    }
    debug_log "Textual installed"

    # Install requirements
    if [ -f "${REPO_DIR}/requirements.txt" ]; then
        debug_log "Installing from requirements.txt"
        pip install -r "${REPO_DIR}/requirements.txt" --quiet || {
            print_error "Failed to install dependencies"
            exit 1
        }
        debug_log "Dependencies installed"
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found at ${REPO_DIR}"
        exit 1
    fi

    # Install as editable package
    if [ -f "${REPO_DIR}/pyproject.toml" ]; then
        debug_log "Installing editable package"
        pip install -e "${REPO_DIR}" --quiet || {
            print_error "Failed to install blonde-cli"
            exit 1
        }
        debug_log "Package installed"
        print_success "Blonde CLI installed"
    fi

    deactivate
    debug_log "Virtual environment deactivated"
}

# Create symlink
create_symlink() {
    debug_log "Creating symlink..."
    
    # Remove old symlink if exists
    rm -f "${BIN_DIR}/blonde" 2>/dev/null || true
    rm -f "${BIN_DIR}/blnd" 2>/dev/null || true

    # Create new symlink
    if ln -sf "${VENV_DIR}/bin/blonde" "${BIN_DIR}/blonde" 2>&1; then
        debug_log "Symlink created: ${BIN_DIR}/blonde -> ${VENV_DIR}/bin/blonde"
        print_success "Command 'blonde' created"
    else
        print_error "Failed to create symlink"
        print_info "Try running manually:"
        echo "  ln -s ${VENV_DIR}/bin/blonde ${BIN_DIR}/blonde"
        exit 1
    fi
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
    debug_log "Checking for existing configuration..."
    
    if [ -f ".env" ]; then
        print_info "Found existing .env file"
        print_info "Creating backup..."
        
        BACKUP_FILE="${INSTALL_DIR}/.env.backup.$(date +%Y%m%d_%H%M%S)"
        cp .env "$BACKUP_FILE" || {
            print_error "Failed to create backup"
            exit 1
        }
        
        debug_log "Backup created: $BACKUP_FILE"
        print_info "Configuration will be migrated during first run"
    fi
    
    print_success "Configuration check complete"
}

# Run setup wizard
run_setup_wizard() {
    print_step "Running setup wizard..."
    
    source "${VENV_DIR}/bin/activate" || {
        print_error "Failed to activate virtual environment"
        exit 1
    }
    
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
    print_info "Installation log: $LOG_FILE"
    echo ""
    print_msg "═════════════════════════════════════════════════" "${BLUE}"
    echo ""
}

# Main installation flow
main() {
    print_header
    print_info "This will install Blonde CLI to ${INSTALL_DIR}"
    echo ""
    
    debug_log "Checking if interactive..."
    
    # Detect if running interactively or piped
    if [ -t 0 ]; then
        # Interactive terminal - prompt for confirmation
        read -p "Continue? [Y/n] " -n 1 -r REPLY
        echo ""
        
        if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
            print_info "Installation cancelled"
            exit 0
        fi
        debug_log "User confirmed installation"
    else
        # Piped input - auto-confirm with warning
        print_info "Non-interactive mode detected - proceeding with installation"
        debug_log "Auto-confirming installation"
        REPLY="Y"
    fi
    
    debug_log "Starting installation steps..."
    
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
