# Blonde CLI Installer for Windows PowerShell
# Usage: irm https://raw.githubusercontent.com/cerekinorg/Blonde-Blip/main/install.ps1 | iex

# Error handling
$ErrorActionPreference = "Stop"

$BLONDE_VERSION = "1.0.0"
$INSTALL_DIR = "$env:USERPROFILE\.blonde"
$VENV_DIR = "$INSTALL_DIR\venv"
$REPO_URL = "https://github.com/cerekinorg/Blonde-Blip.git"
$REPO_DIR = "$INSTALL_DIR\repo"
$LOG_DIR = "$INSTALL_DIR\logs"

# Debug mode (only enabled when user sets $env:DEBUG=1)
$DEBUG = $env:DEBUG
if (-not $DEBUG) { $DEBUG = "0" }

# Installation log
$LOG_FILE = "$LOG_DIR\install_$((Get-Date -Format "yyyyMMdd_HHmmss")).log"

function Write-Log {
    param([string]$Message)
    if (Test-Path $LOG_DIR) {
        "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message" | Out-File -FilePath $LOG_FILE -Append
    }
}

Write-Log "Installer started"

# Color output functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
    Write-Log $Message
}

function Write-Header {
    Write-Host ""
    Write-ColorOutput "═══════════════════════════════════════════════" "Cyan"
    Write-ColorOutput "   🚀 Blonde CLI Installer v$BLONDE_VERSION" "Cyan"
    Write-ColorOutput "═══════════════════════════════════════════════" "Cyan"
    Write-Host ""
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "▶ $Message" "Yellow"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ $Message" "Cyan"
}

function Write-Debug {
    param([string]$Message)
    if ($DEBUG -eq "1") {
        Write-Host "[DEBUG] $Message" -ForegroundColor DarkGray
        Write-Log "[DEBUG] $Message"
    }
}

Write-Debug "User profile: $env:USERPROFILE"
Write-Debug "Install dir: $INSTALL_DIR"
Write-Debug "Log file: $LOG_FILE"
Write-Debug "Debug mode: $DEBUG"

# Parse command line arguments
$AUTO_CONFIRM = $false
$SILENT_MODE = $false

$script:Args = $args
for ($i = 0; $i -lt $script:Args.Count; $i++) {
    switch ($script:Args[$i]) {
        "--yes" { $AUTO_CONFIRM = $true; Write-Debug "Auto-confirm enabled" }
        "-y" { $AUTO_CONFIRM = $true; Write-Debug "Auto-confirm enabled" }
        "--silent" { $SILENT_MODE = $true; Write-Debug "Silent mode enabled" }
        "-s" { $SILENT_MODE = $true; Write-Debug "Silent mode enabled" }
        "--help" { Show-Help }
        "-h" { Show-Help }
        "--debug" { $DEBUG = "1"; Write-Debug "Debug mode enabled" }
        "-d" { $DEBUG = "1"; Write-Debug "Debug mode enabled" }
        default {
            Write-Error "Unknown option: $($script:Args[$i])"
            Write-Info "Use --help for usage"
            exit 1
        }
    }
}

function Show-Help {
    Write-Host "Blonde CLI Installer"
    Write-Host ""
    Write-Host "Usage: install.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  --yes, -y     Skip confirmation prompt"
    Write-Host "  --silent, -s   Skip confirmation and reduce output"
    Write-Host "  --debug, -d    Enable debug logging (set `$env:DEBUG=1`)"
    Write-Host "  --help, -h     Show this help"
    exit 0
}

# Check Python installation
function Test-Python {
    param()
    
    Write-Step "Checking Python installation..."
    
    try {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            $version = & python --version 2>&1
            Write-Debug "Found python: $version"
            Write-Success "Found $version"
            return "python"
        }
    } catch {
        # Continue to python3 check
    }
    
    try {
        $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            $version = & python3 --version 2>&1
            Write-Debug "Found python3: $version"
            Write-Success "Found $version"
            return "python3"
        }
    } catch {
        Write-Error "Python 3.8+ is not installed"
        Write-Info "Please install Python 3.8 or higher from https://www.python.org/"
        exit 1
    }
    
    Write-Error "Python 3.8+ is not installed"
    Write-Info "Please install Python 3.8 or higher from https://www.python.org/"
    exit 1
}

# Check Git installation
function Test-Git {
    param()
    
    Write-Step "Checking Git installation..."
    
    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCmd) {
        Write-Success "Git found"
        return $true
    }
    
    Write-Error "Git is not installed"
    Write-Info "Please install Git from https://git-scm.com/downloads"
    exit 1
}

# Create directories
function Initialize-Directories {
    Write-Step "Creating directories..."
    
    try {
        if (!(Test-Path $INSTALL_DIR)) {
            New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
            Write-Debug "Created $INSTALL_DIR"
        }
        if (!(Test-Path "$INSTALL_DIR\models")) {
            New-Item -ItemType Directory -Path "$INSTALL_DIR\models" -Force | Out-Null
            Write-Debug "Created models directory"
        }
        if (!(Test-Path "$INSTALL_DIR\cache")) {
            New-Item -ItemType Directory -Path "$INSTALL_DIR\cache" -Force | Out-Null
            Write-Debug "Created cache directory"
        }
        if (!(Test-Path "$INSTALL_DIR\memory")) {
            New-Item -ItemType Directory -Path "$INSTALL_DIR\memory" -Force | Out-Null
            Write-Debug "Created memory directory"
        }
        if (!(Test-Path $LOG_DIR)) {
            New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
            Write-Debug "Created logs directory"
        }
        
        Write-Success "Directories created"
    } catch {
        Write-Error "Failed to create directories: $_"
        exit 1
    }
}

# Clone or update repository
function Get-Repository {
    Write-Step "Downloading Blonde CLI..."
    
    try {
        if (Test-Path $REPO_DIR) {
            Write-Info "Updating existing installation..."
            Set-Location $REPO_DIR
            
            $output = git pull origin main 2>&1
            if ($LASTEXITCODE -ne 0) {
                $output = git pull origin master 2>&1
                if ($LASTEXITCODE -ne 0) {
                    Write-Debug "No updates available"
                    Write-Info "No updates available"
                }
            } else {
                Write-Debug "Git pull succeeded (main branch)"
            }
        } else {
            Write-Debug "Cloning repository: $REPO_URL"
            git clone $REPO_URL $REPO_DIR 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                throw "Git clone failed"
            }
            Write-Debug "Git clone succeeded"
        }
        
        Set-Location $HOME
        Write-Success "Source downloaded"
    } catch {
        Write-Error "Failed to clone repository: $_"
        exit 1
    }
}

# Create virtual environment
function Initialize-VirtualEnvironment {
    Write-Step "Creating virtual environment..."
    
    try {
        $python = Test-Python
        
        if (Test-Path $VENV_DIR) {
            Write-Info "Virtual environment already exists"
        } else {
            & python -m venv $VENV_DIR
            Write-Debug "Virtual environment created"
            Write-Success "Virtual environment created"
        }
    } catch {
        Write-Error "Failed to create virtual environment: $_"
        exit 1
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Step "Installing dependencies..."
    
    try {
        if (!(Test-Path "$VENV_DIR\Scripts\activate.ps1")) {
            Write-Error "Virtual environment not found at $VENV_DIR"
            Write-Info "Please run Initialize-VirtualEnvironment first"
            exit 1
        }
        
        # Activate virtual environment
        & "$VENV_DIR\Scripts\activate.ps1"
        Write-Debug "Virtual environment activated"
        
        # Upgrade pip
        python -m pip install --upgrade pip --quiet
        Write-Debug "Pip upgraded"
        
        # Install requirements
        if (Test-Path "$REPO_DIR\requirements.txt") {
            Write-Debug "Installing from requirements.txt"
            python -m pip install -r "$REPO_DIR\requirements.txt" --quiet
            Write-Debug "Dependencies installed"
            Write-Success "Dependencies installed"
        } else {
            Write-Error "requirements.txt not found at $REPO_DIR"
            exit 1
        }
        
        # Install as editable package
        if (Test-Path "$REPO_DIR\pyproject.toml") {
            Write-Debug "Installing editable package"
            python -m pip install -e "$REPO_DIR" --quiet
            Write-Debug "Package installed"
            Write-Success "Blonde CLI installed"
        }
        
        # Deactivate
        deactivate
        Write-Debug "Virtual environment deactivated"
    } catch {
        Write-Error "Failed to install dependencies: $_"
        exit 1
    }
}

# Create command wrapper
function Install-Command {
    Write-Step "Creating 'blonde' command..."
    
    try {
        $python = Test-Python
        
        # Remove old wrapper if exists
        $wrapperPath = "$VENV_DIR\Scripts\blonde.exe"
        if (Test-Path $wrapperPath) {
            Remove-Item $wrapperPath -Force
            Write-Debug "Removed old wrapper"
        }
        
        # Create Python wrapper script
        $wrapperContent = @"
# Blonde CLI wrapper
@echo off
python "%~dp0\venv\Scripts\blonde.exe" %*
"@
        
        $wrapperContent | Out-File -FilePath "$VENV_DIR\Scripts\blonde.bat" -Encoding ASCII -Force
        Write-Debug "Created wrapper script"
        
        Write-Success "Command 'blonde' created"
    } catch {
        Write-Error "Failed to create command: $_"
        exit 1
    }
}

# Add to PATH
function Add-To-Path {
    Write-Step "Adding to PATH..."
    
    try {
        # Get current PATH
        $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
        $venvScriptsPath = "$VENV_DIR\Scripts"
        
        # Check if already in PATH
        if ($currentPath -like "*$venvScriptsPath*") {
            Write-Info "Already in PATH"
        } else {
            Write-Info "Adding to user PATH..."
            [Environment]::SetEnvironmentVariable("Path", "$currentPath;$venvScriptsPath", "User")
            Write-Success "Added to PATH"
            Write-Info "Please restart your terminal or PowerShell session"
        }
    } catch {
        Write-Error "Failed to update PATH: $_"
        exit 1
    }
}

# Migrate existing configuration
function Migrate-Configuration {
    Write-Step "Checking for existing configuration..."
    
    try {
        $envFile = ".env"
        if (Test-Path $envFile) {
            Write-Info "Found existing .env file"
            Write-Info "Creating backup..."
            
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $backupFile = "$INSTALL_DIR\.env.backup.$timestamp"
            Copy-Item $envFile $backupFile -Force
            
            Write-Debug "Backup created: $backupFile"
            Write-Info "Configuration will be migrated during first run"
        }
        
        Write-Success "Configuration check complete"
    } catch {
        Write-Error "Failed to migrate configuration: $_"
        exit 1
    }
}

# Run setup wizard
function Invoke-SetupWizard {
    Write-Step "Running setup wizard..."
    
    try {
        if (!(Test-Path "$VENV_DIR\Scripts\activate.ps1")) {
            Write-Error "Virtual environment not found at $VENV_DIR"
            exit 1
        }
        
        # Activate virtual environment
        & "$VENV_DIR\Scripts\activate.ps1"
        Write-Debug "Virtual environment activated"
        
        # Check if wizard exists and run it
        if (Test-Path "$REPO_DIR\tui\setup_wizard.py") {
            python "$REPO_DIR\tui\setup_wizard.py"
        } else {
            Write-Info "Setup wizard will run on first 'blonde' command"
        }
        
        # Deactivate
        deactivate
    } catch {
        Write-Error "Failed to run setup wizard: $_"
        exit 1
    }
}

# Print success message
function Show-SuccessMessage {
    Write-Header
    Write-Success "Installation complete!"
    Write-Host ""
    Write-Info "To start using Blonde CLI:"
    Write-Host ""
    Write-ColorOutput "  blonde" "Green"
    Write-Host ""
    Write-Info "Documentation: https://github.com/cerekinorg/Blonde-Blip#readme"
    Write-Host ""
    Write-Info "Installation log: $LOG_FILE"
    Write-Host ""
    Write-ColorOutput "═══════════════════════════════════════════════" "Cyan"
    Write-Host ""
}

# Main installation flow
function Main {
    Write-Header
    Write-Info "This will install Blonde CLI to $INSTALL_DIR"
    Write-Host ""
    
    # Detect if running interactively or piped
    Write-Debug "Checking if interactive..."
    
    if ([Console]::IsInputRedirected) {
        # Non-interactive (piped) - auto-confirm
        Write-Info "Non-interactive mode detected - proceeding with installation"
        Write-Debug "Auto-confirming installation"
    } else {
        # Interactive - ask for confirmation
        $response = Read-Host "Continue? [Y/n]"
        
        if ($response -ne "" -and $response -ne "Y" -and $response -ne "y") {
            Write-Info "Installation cancelled"
            exit 0
        }
        Write-Debug "User confirmed installation"
    }
    
    Write-Debug "Starting installation steps..."
    
    $python = Test-Python
    Test-Git
    Initialize-Directories
    Get-Repository
    Initialize-VirtualEnvironment
    Install-Dependencies
    Install-Command
    Add-To-Path
    Migrate-Configuration
    # Invoke-SetupWizard  # Optional: can run on first 'blonde' command
    Show-SuccessMessage
}

# Run main function
Main
