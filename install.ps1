# Blonde CLI Installer for Windows PowerShell
# Usage: irm https://blonde.dev/install.ps1 | iex

$ErrorActionPreference = "Stop"

$BLONDE_VERSION = "1.0.0"
$INSTALL_DIR = "$env:USERPROFILE\.blonde"
$VENV_DIR = "$INSTALL_DIR\venv"
$REPO_URL = "https://github.com/blonde-team/blonde-cli.git"
$REPO_DIR = "$INSTALL_DIR\repo"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    Write-Host ""
    Write-ColorOutput "═══════════════════════════════════════════════════" "Cyan"
    Write-ColorOutput "   🚀 Blonde CLI Installer v$BLONDE_VERSION" "Cyan"
    Write-ColorOutput "═══════════════════════════════════════════════════" "Cyan"
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

# Check Python installation
function Test-Python {
    Write-Step "Checking Python installation..."

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue

    if ($pythonCmd) {
        $version = & python --version 2>&1
        Write-Success "Found $version"
        return "python"
    }

    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $version = & python3 --version 2>&1
        Write-Success "Found $version"
        return "python3"
    }

    Write-Error "Python 3.8+ is not installed"
    Write-Info "Please install Python 3.8 or higher from https://www.python.org/"
    exit 1
}

# Check Git installation
function Test-Git {
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

    if (!(Test-Path $INSTALL_DIR)) {
        New-Item -ItemType Directory -Path $INSTALL_DIR | Out-Null
    }

    if (!(Test-Path "$INSTALL_DIR\models")) {
        New-Item -ItemType Directory -Path "$INSTALL_DIR\models" | Out-Null
    }

    if (!(Test-Path "$INSTALL_DIR\cache")) {
        New-Item -ItemType Directory -Path "$INSTALL_DIR\cache" | Out-Null
    }

    if (!(Test-Path "$INSTALL_DIR\memory")) {
        New-Item -ItemType Directory -Path "$INSTALL_DIR\memory" | Out-Null
    }

    if (!(Test-Path "$INSTALL_DIR\logs")) {
        New-Item -ItemType Directory -Path "$INSTALL_DIR\logs" | Out-Null
    }

    Write-Success "Directories created"
}

# Clone or update repository
function Get-Repository {
    Write-Step "Downloading Blonde CLI..."

    if (Test-Path $REPO_DIR) {
        Write-Info "Updating existing installation..."
        Set-Location $REPO_DIR
        git pull origin main 2>$null
        git pull origin master 2>$null
    } else {
        git clone $REPO_URL $REPO_DIR
    }

    Set-Location $HOME
    Write-Success "Source downloaded"
}

# Create virtual environment
function Initialize-VirtualEnvironment {
    Write-Step "Creating virtual environment..."

    if (Test-Path $VENV_DIR) {
        Write-Info "Virtual environment already exists"
    } else {
        & python -m venv $VENV_DIR
        Write-Success "Virtual environment created"
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Step "Installing dependencies..."

    # Activate virtual environment
    $activateScript = "$VENV_DIR\Scripts\Activate.ps1"
    & $activateScript

    # Upgrade pip
    python -m pip install --upgrade pip --quiet

    # Install requirements
    if (Test-Path "$REPO_DIR\requirements.txt") {
        python -m pip install -r "$REPO_DIR\requirements.txt" --quiet
        Write-Success "Dependencies installed"
    } else {
        Write-Error "requirements.txt not found"
        exit 1
    }

    # Install as editable package
    if (Test-Path "$REPO_DIR\pyproject.toml") {
        python -m pip install -e "$REPO_DIR" --quiet
        Write-Success "Blonde CLI installed"
    }

    deactivate
}

# Create command wrapper
function Install-Command {
    Write-Step "Creating 'blonde' command..."

    $wrapperScript = @"
# Blonde CLI wrapper
& "$VENV_DIR\Scripts\blonde.exe" `$args
"@

    $binDir = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps"

    # Remove old wrapper
    if (Test-Path "$binDir\blonde.bat") {
        Remove-Item "$binDir\blonde.bat"
    }

    # Create new wrapper
    $wrapperScript | Out-File -FilePath "$binDir\blonde.bat" -Encoding ASCII

    Write-Success "Command 'blonde' created"
}

# Migrate existing configuration
function Migrate-Configuration {
    Write-Step "Checking for existing configuration..."

    $envFile = ".env"
    if (Test-Path $envFile) {
        Write-Info "Found existing .env file"

        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupFile = "$INSTALL_DIR\.env.backup.$timestamp"
        Copy-Item $envFile $backupFile

        Write-Info "Configuration will be migrated during first run"
    }

    Write-Success "Configuration check complete"
}

# Run setup wizard
function Invoke-SetupWizard {
    Write-Step "Running setup wizard..."

    $activateScript = "$VENV_DIR\Scripts\Activate.ps1"
    & $activateScript

    # Check if wizard exists and run it
    if (Test-Path "$REPO_DIR\tui\setup_wizard.py") {
        python "$REPO_DIR\tui\setup_wizard.py"
    } else {
        Write-Info "Setup wizard will run on first 'blonde' command"
    }

    deactivate
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
    Write-Info "Documentation: https://blonde.dev/docs"
    Write-Host ""
    Write-ColorOutput "═══════════════════════════════════════════════════" "Cyan"
    Write-Host ""
}

# Main installation flow
function Main {
    Write-Header
    Write-Info "This will install Blonde CLI to $INSTALL_DIR"
    Write-Host ""

    $response = Read-Host "Continue? [Y/n]"

    if ($response -ne "" -and $response -ne "Y" -and $response -ne "y") {
        Write-Info "Installation cancelled"
        exit 0
    }

    $python = Test-Python
    Test-Git
    Initialize-Directories
    Get-Repository
    Initialize-VirtualEnvironment
    Install-Dependencies
    Install-Command
    Migrate-Configuration
    # Invoke-SetupWizard  # Optional: can run on first 'blonde' command
    Show-SuccessMessage
}

# Run main function
Main
