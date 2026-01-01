# Changelog

All notable changes to Blonde CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 9-agent AI development team with parallel execution
- Optimizer agent as master coordinator
- Blip mascot with animated ASCII art (10 emotional states)
- Enhanced dashboard UI with file browser
- Setup wizard for easy configuration (4-step interactive)
- Auto-migration from .env to config.json
- MCP auto-setup with project detection
- Quality gates for agent outputs
- Real-time agent communication
- Parallel executor for collaborative workflows
- Agent visualization with status tracking
- New `blonde agent-task` command for parallel execution
- Integration of Blip mascot throughout CLI

### Changed
- Upgraded from 8-agent system to 9-agent system
- Moved from sequential to parallel agent execution
- Optimizer agent sits above all agents as master coordinator
- Enhanced help text with detailed agent descriptions
- Improved configuration system with JSON format
- Better error handling and user feedback

### Fixed
- Fixed syntax errors in optimizer_agent.py (unterminated string literal)
- Fixed dataclass field ordering in parallel_executor.py
- Added explicit command names for typer CLI functions
- Fixed Python 3.12 compatibility issues

### Security
- Enhanced security agent capabilities
- Improved secrets detection in code
- Added SQL injection risk detection

## [1.0.0] - 2025-01-02

### Added
- Initial release of Blonde CLI
- Multi-agent AI development platform (8 agents)
- Privacy-first architecture
- Provider switching system (OpenRouter, OpenAI, Anthropic, Local)
- Complete chat interface with 40+ commands
- AST-based code analysis
- AI-powered test generation
- Multi-linter integration (Pylint, Flake8, Ruff)
- Intelligent code review
- Rollback system with snapshots
- Workflow automation
- MCP (Model Context Protocol) integration
- Memory system for conversation context
- Agentic tools for code operations

### Features
- 9 specialized AI agents:
  - Generator Agent - Creates initial implementations
  - Reviewer Agent - Reviews code quality
  - Tester Agent - Generates test suites
  - Refactorer Agent - Improves code structure
  - Documenter Agent - Writes documentation
  - Architect Agent - Designs system architecture
  - Security Agent - Identifies vulnerabilities
  - Debugger Agent - Fixes bugs
  - Optimizer Agent - Coordinates all agents (master)

- Provider management:
  - List all available providers
  - Switch between providers instantly
  - Test provider connections
  - Auto-select best provider

- Code analysis tools:
  - AST-based code parsing
  - Cyclomatic complexity metrics
  - Dependency tracking
  - Code smell detection
  - Symbol search across repository

- Testing capabilities:
  - Automatic test case generation
  - Edge case detection
  - Test execution and reporting
  - Coverage analysis

- Linting integration:
  - Python: Pylint, Flake8, Ruff
  - JavaScript/TypeScript: ESLint (planned)
  - Go: go vet, golint (planned)

- Code review:
  - AI-powered reviews using LLM
  - Bug detection
  - Security vulnerability scanning
  - Performance suggestions
  - Maintainability scoring (0-100)

- Rollback & safety:
  - Automatic operation tracking
  - Project snapshots
  - Selective rollback
  - Operation history

- Workflow automation:
  - Pre-built workflows
  - Custom workflow creation
  - Task scheduling
  - Parallel execution

### Documentation
- Quick start guide
- Complete feature documentation
- Privacy guide
- Backend architecture guide
- Provider and team documentation

### Installation
- Installer script (Unix/Linux/macOS): `install.sh`
- Installer script (Windows PowerShell): `install.ps1`
- PyPI package: `blonde-cli`
- Manual installation support

### License
- MIT License - Free to use, modify, and distribute
