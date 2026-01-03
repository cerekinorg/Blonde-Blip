# Deployment Guide for Blonde CLI

This guide covers how to deploy Blonde CLI to PyPI and make it installable via `pip install blonde-cli`.

## Prerequisites

1. **GitHub Repository**: ✅ Already set up at `https://github.com/cerekinorg/Blonde-Blip`
2. **PyPI Account**: Create account at https://pypi.org/account/register/
3. **PyPI API Token**: Generate token for automatic publishing

## Step 1: Create PyPI API Token

1. Go to: https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Fill in:
   - **Token name**: `blonde-cli-github-actions` (or similar)
   - **Scope**: "Entire account" (recommended)
4. Click "Add token"
5. **IMPORTANT**: Copy the token immediately (you won't see it again!)

## Step 2: Add PyPI Token to GitHub Secrets

1. Go to: https://github.com/cerekinorg/Blonde-Blip/settings/secrets/actions
2. Click "New repository secret"
3. Fill in:
   - **Name**: `PYPI_API_TOKEN` (exact match required!)
   - **Value**: Paste the PyPI token from Step 1
4. Click "Add secret"

## Step 3: Create a GitHub Release (Triggers PyPI Publishing)

### Option A: Using Git Tags (Recommended)

```bash
# Create a version tag
git tag v1.0.0

# Push tag to GitHub (triggers PyCI workflow!)
git push origin v1.0.0
```

The `publish-to-pypi.yml` workflow will automatically:
1. Build the package
2. Run quality checks
3. Upload to PyPI

### Option B: Using GitHub Web UI

1. Go to: https://github.com/cerekinorg/Blonde-Blip/releases/new
2. Fill in:
   - **Tag**: `v1.0.0`
   - **Release title**: `Blonde CLI v1.0.0 - Multi-Agent AI Development Platform`
   - **Description**: (Copy from CHANGELOG.md)
3. Click "Publish release"

The GitHub Actions workflow will automatically trigger and publish to PyPI!

## Step 4: Verify PyPI Installation

After the workflow completes (check Actions tab):

```bash
# Install from PyPI
pip install blonde-cli

# Verify installation
blonde --help

# Test all imports
python -c "
from tui.cli import app
from tui.optimizer_agent import OptimizerAgent
from tui.parallel_executor import ParallelAgentExecutor
from tui.dev_team import DevelopmentTeam
from tui.blip import blip
print('All imports successful!')
"
```

## Step 5: Test the Installer Script

After PyPI deployment, test the one-line installer:

```bash
# On Unix/Linux/macOS
curl -fsSL https://raw.githubusercontent.com/cerekinorg/Blonde-Blip/main/install.sh | bash

# On Windows PowerShell
irm https://raw.githubusercontent.com/cerekinorg/Blonde-Blip/main/install.ps1 | iex
```

## Step 6: Update README with Installation Instructions

After PyPI deployment is successful, update README.md:

```markdown
## 🚀 Quick Start

### Option 1: PyPI (Recommended)

```bash
pip install blonde-cli
blonde
```

### Option 2: Installer Script

```bash
curl -fsSL https://raw.githubusercontent.com/cerekinorg/Blonde-Blip/main/install.sh | bash
blonde
```

### Option 3: Manual Installation

```bash
git clone https://github.com/cerekinorg/Blonde-Blip.git
cd Blonde-Blip
pip install -r requirements.txt
pip install -e .
blonde
```
```

## Versioning Strategy

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backward compatible

### Example Version Sequence

```bash
# First release
git tag v1.0.0
git push origin v1.0.0

# Bug fixes
git tag v1.0.1
git push origin v1.0.1

# New feature
git tag v1.1.0
git push origin v1.1.0

# Breaking change
git tag v2.0.0
git push origin v2.0.0
```

## Workflow Overview

### Test Workflow (`.github/workflows/test-package.yml`)

Triggers on:
- Push to `main` or `develop` branches
- Pull requests to `main` branch
- Manual trigger via GitHub Actions UI

Tests:
- Package builds successfully
- All imports work
- Code linting (pylint)
- Installation from wheel file

### Publish Workflow (`.github/workflows/publish-to-pypi.yml`)

Triggers on:
- Version tags (`v*`)
- GitHub releases
- Manual trigger

Actions:
- Builds source distribution (.tar.gz)
- Builds wheel (.whl)
- Checks package metadata
- Publishes to PyPI

## Troubleshooting

### "Invalid or missing authentication credentials"

**Cause**: PyPI API token not set in GitHub secrets

**Fix**:
1. Go to GitHub repo settings → Secrets and variables → Actions
2. Add `PYPI_API_TOKEN` with your PyPI token

### "HTTP 400 Bad Request"

**Cause**: Package name already taken or version already exists

**Fix**:
1. Check if `blonde-cli` exists on PyPI: https://pypi.org/project/blonde-cli/
2. If name taken, update `pyproject.toml` and use a different name
3. If version exists, increment version in `pyproject.toml`

### "Workflow failed to build package"

**Cause**: Build errors in package

**Fix**:
1. Check GitHub Actions logs
2. Try building locally: `python -m build`
3. Fix any build errors
4. Commit and push fixes

### "Installer script fails to download"

**Cause**: GitHub raw URL incorrect or repository not public

**Fix**:
1. Verify repository is public: https://github.com/cerekinorg/Blonde-Blip
2. Test raw URL in browser: https://raw.githubusercontent.com/cerekinorg/Blonde-Blip/main/install.sh
3. Check `REPO_URL` in install.sh

## Next Steps After Initial Release

1. **Create GitHub Releases**: For each new version
2. **Update CHANGELOG.md**: Document all changes
3. **Increment version**: Update `pyproject.toml`
4. **Tag and push**: `git tag v1.0.1 && git push origin v1.0.1`
5. **Monitor PyPI**: Check downloads and issues

## Automated Testing

The test workflow automatically tests on Python 3.8, 3.9, 3.10, 3.11, and 3.12.

If you add a new dependency, test locally first:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m build
pip install dist/*.whl
python -c "from tui.cli import app; print('OK')"
```

## Manual Publishing (Alternative to Automation)

If GitHub Actions fails, you can publish manually:

```bash
# Build package
python -m build

# Upload to PyPI
twine upload dist/*
```

You'll need to:
1. Install build tools: `pip install build twine`
2. Create PyPI account and token
3. Run twine upload with your credentials

## Summary

✅ **Ready for Deployment**:
- LICENSE file created
- CHANGELOG.md created
- GitHub Actions workflows added
- All URLs updated to correct repository
- Package builds successfully

📦 **Next Steps**:
1. Create PyPI account and token
2. Add token to GitHub secrets
3. Create version tag (v1.0.0)
4. Push to GitHub
5. Verify on PyPI

🎉 **After Deployment**:
- Users can install via `pip install blonde-cli`
- Automatic publishing for future versions
- Tested across Python 3.8-3.12
- One-line installer works from GitHub
