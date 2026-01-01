<div align="center">

![Blonde CLI](https://img.shields.io/badge/Blonde-CLI-Privacy--First-blue?style=for-the-badge&logo=python)
![Version](https://img.shields.io/badge/version-1.0.0-green?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)
![Python](https://img.shields.io/badge/python-3.8+-yellow?style=flat-square&logo=python)

**Privacy-First Multi-Agent AI Development Assistant**

[Build Better Code, Privately.](https://github.com/cerekinorg/Blonde-Blip)

---

</div>

<div align="center">

**The First AI Development Platform Where Multiple Agents Collaborate to Build Better Code**

[Multi-Agent Team](#multi-agent-team) • [Provider System](#provider-system) • [Privacy-First](#privacy-first) • [All Features in Chat](#all-features-in-chat)

[Quick Start](#quick-start) • [Installation](#installation) • [Documentation](#documentation) • [Contributing](#contributing)

---

</div>

---

## 🚀 About Blonde CLI

**Blonde CLI** is the world's first privacy-first, multi-agent AI development platform designed for developers who need powerful AI assistance without compromising their code's confidentiality.

Unlike other AI tools that send your code to cloud servers by default, Blonde CLI:
- **Processes everything locally** by default
- **Lets you choose** when to use cloud AI
- **Provides complete transparency** about data flow
- **Features a team of 9 specialized AI agents** that collaborate to improve your code

### 🎯 What Makes Blonde CLI Different

| Feature | Blonde CLI | Others |
|---------|-------------|---------|
| **9 AI Agents** | ✅ Collaborating together | ❌ Single AI only |
| **Privacy-First** | ✅ Local by default | ❌ Cloud by default |
| **Provider Flexibility** | ✅ Switch 4+ providers | ❌ 1-2 providers |
| **Everything in Chat** | ✅ 40+ commands | ❌ Separate tools |
| **Peer Review System** | ✅ Agents review each other | ❌ No collaboration |
| **Rollback System** | ✅ Snapshots & undo | ❌ Basic undo |
| **Knowledge Base** | ✅ Per-agent learning | ❌ No memory |
| **Open Source** | ✅ 100% | ❌ Proprietary |

---

## ✨ Key Features

### 🤝 Multi-Agent Development Team

**Watch AI agents work together to build better code**

Blonde CLI includes 9 specialized AI agents, each an expert in their domain:

- **🧱 Generator Agent** - Creates initial implementations
- **🔍 Reviewer Agent** - Reviews code quality, finds bugs
- **🧪 Tester Agent** - Generates comprehensive test suites
- **🔨 Refactorer Agent** - Improves code structure
- **📝 Documenter Agent** - Writes documentation
- **🏗️ Architect Agent** - Designs system architecture
- **🔒 Security Agent** - Identifies vulnerabilities
- **🐛 Debugger Agent** - Fixes bugs and troubleshoots

**How it works:**
```bash
# Have multiple agents collaborate on a task
blnd chat
You: /team collab Build a REST API with authentication
# → Generator creates initial code
# → Reviewer checks quality
# → Security audits for vulnerabilities
# → Tester generates tests
# → All agents provide feedback
# → Code gets better with each iteration
```

### 🔄 Provider Switching

**Seamlessly switch between AI providers**

Support for 4+ providers with instant switching:

- **🌐 OpenRouter** - Access to multiple models
- **🤖 OpenAI** - GPT-4, GPT-3.5
- **🧠 Anthropic** - Claude 3 Opus, Sonnet
- **💻 Local GGUF** - Run models offline, 100% private

**Features:**
```bash
# List all providers
blnd provider list

# Switch providers (instant)
blnd provider switch local       # Fast, private, free
blnd provider switch openai       # Use GPT-4
blnd provider switch anthropic    # Use Claude
blnd provider switch openrouter   # Access multiple models

# Test provider
blnd provider test local
```

### 🔒 Privacy-First Design

**Your data stays on your machine unless you choose otherwise**

- **Local-Only Mode** - All file operations, code analysis, refactoring
- **Explicit Cloud Use** - Clear warnings before sending data to cloud providers
- **Privacy Tiers** - Provider privacy ratings (local, privacy cloud, standard cloud)
- **Data Control** - Choose what's stored, for how long, if encrypted
- **Audit Trails** - See exactly what was sent where
- **Easy Cleanup** - Delete all data with one command

**Privacy Settings:**
```bash
# Check privacy status
blnd chat
You: /privacy

# Clear all stored data
blnd chat
You: /clear-all-data
```

### 📚 All Features in Chat

**40+ commands accessible through natural language**

No need to learn separate CLI tools - everything is available in the chat interface:

```bash
# Provider Management
/providers                   # List all AI providers
/provider switch [provider]    # Switch provider
/provider test [provider]        # Test if provider works
/provider auto                # Auto-select best provider

# Multi-Agent Team
/team status                # View team status and metrics
/team task [agent] [task] # Assign task to agent
/team collab [task]          # Multiple agents collaborate
/team improve [task]         # Continuous improvement loop

# Code Analysis
/analyze [file]             # Analyze code structure
/analyze repo [path]         # Analyze entire repository
/search [query]                # Search code for symbol/pattern

# Testing
/test gen [file]             # Generate tests for a file
/test run                     # Run test suite
/test coverage                # Get coverage report

# Linting & Review
/lint [file]                 # Lint code for quality issues
/review [file]               # AI-powered code review

# Refactoring
/search "User"                # Find symbol usage
/refactor "rename old new"      # Rename symbol across repo

# Rollback & Safety
/history                     # View operation history
/undo                         # Undo last operation
/snapshot create [name]     # Create project snapshot
/snapshot restore [name]     # Restore from snapshot

# Workflows
/workflow list               # List available workflows
/workflow run [name]         # Execute workflow

# Help & Utilities
/help [topic]               # Get help on specific command
/docs                         # Full documentation links
/clear                        # Clear screen
```

### 🧪 Advanced Development Tools

**Complete toolset for professional development**

1. **AST-Based Code Analysis**
   - Deep code entity extraction (functions, classes, variables)
   - Cyclomatic complexity metrics
   - Dependency tracking and relationship mapping
   - Code smell detection (long functions, god classes)
   - Code quality scoring

2. **Repository-Wide Search & Refactoring**
   - Symbol search across entire codebase
   - Regex pattern search
   - Similar code detection
   - Safe symbol renaming across multiple files
   - Function extraction
   - Dependency analysis

3. **AI-Powered Test Generation**
   - Automatic test case generation from source code
   - Multi-language support (Python pytest, JavaScript Jest, Go)
   - Edge case detection
   - Test execution and reporting
   - Coverage analysis

4. **Multi-Linter Integration**
   - Python: Pylint, Flake8, Ruff
   - JavaScript/TypeScript: ESLint
   - Go: go vet, golint
   - Custom linter support
   - Unified issue reporting

5. **Intelligent Code Review**
   - AI-powered code reviews using LLM
   - Bug detection
   - Security vulnerability scanning
   - Performance suggestions
   - Best practice validation
   - Maintainability scoring (0-100)

6. **Rollback & Undo System**
   - Automatic operation tracking
   - Project snapshots (full project state)
   - Selective rollback (undo specific operations)
   - Safe file operations with automatic backups
   - Operation history with details

7. **Workflow Automation**
   - Pre-built workflows (Python setup, Node.js setup, code quality checks)
   - Custom workflow creation
   - Task scheduling
   - Dependency handling
   - Parallel execution support

---

## 🎯 Use Cases

### For Individual Developers

**"I want to build a new feature quickly"**
```bash
# Use multi-agent team for rapid development
blnd chat
You: /team collab Implement user authentication with JWT
# → Generator creates API
# → Security validates auth flow
# → Tester generates tests
# → Documenter writes docs
# → All agents provide feedback
```

**"I need to refactor a complex codebase"**
```bash
# Use collaborative refactoring
blnd chat
You: /team collab Refactor user service module for better performance
# → Refactorer improves structure
# → Reviewer validates changes
# → Optimizer tunes performance
# → Security checks for vulnerabilities
```

**"I want comprehensive tests for my code"**
```bash
# AI-powered test generation
blnd chat
You: /test gen auth_service.py
# → Tester generates unit tests, integration tests, edge cases
# → Reviewer validates test quality
# → Security checks for test security
```

### For Teams

**"I need to maintain code quality across the team"**
```bash
# Automated code review
blnd chat
You: /review feature_X.py
# → AI finds bugs, issues, security vulnerabilities
# → Provides specific improvement suggestions
# → Scores maintainability
```

**"We need to refactor safely"**
```bash
# Use rollback system
blnd chat
You: /snapshot create before-refactor
# → Save current state

You: /team collab Refactor database layer
# → Multiple agents work together

You: /snapshot restore before-refactor
# → If issues, revert instantly
```

### For Privacy-Conscious Developers

**"I work on sensitive code"**
```bash
# Stay 100% local
blnd chat
You: /provider switch local
# → Use local GGUF model
You: /team collab Implement encryption system
# → All processing stays on your machine

# Generate code locally, polish with cloud
blnd chat
You: /provider switch local
You: /team collab Generate MVP
# → Create basic implementation locally
You: /provider switch anthropic
You: /team improve Add advanced features
# → Polish with Claude API
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/cerekinorg/Blonde-Blip.git
cd blonde-cli

# Install dependencies
pip install -r requirements.txt

# Verify installation
blnd --help
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# OPENROUTER_API_KEY=your_key_here
# OPENROUTER_MODEL=openai/gpt-oss-20b:free

# Optional: Add more providers
# OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key
```

### 3. Start Using

```bash
# Interactive chat mode (recommended)
blnd chat

# Generate code
blnd gen "Create a Flask REST API with user authentication"

# Fix code
blnd fix app.py

# Document code
blnd doc app.py

# Run commands directly
blnd provider list
blnd /team status
blnd /analyze repo
```

---

## 📖 Documentation

- **[Quick Start Guide](./QUICKSTART.md)** - Get up in 5 minutes
- **[Complete Feature List](./FEATURES.md)** - All capabilities explained
- **[Privacy Guide](./PRIVACY.md)** - How Blonde protects your data
- **[Backend Architecture](./BACKEND_GUIDE.md)** - For extending the platform
- **[Provider & Team Docs](./PROVIDER_TEAM.md)** - Advanced usage
- **[Implementation Summary](./FINAL_IMPLEMENTATION.md)** - What was built

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│              Blonde CLI Architecture                 │
└────────────┬───────────────────────┬───────────────┘
             │                       │
    ┌────────┴────────┐     ┌─────┴─────────┐
    │  Chat Interface   │     │  Core Services  │
    │  (Enhanced)      │     │                │
    │                  │     ├────────────────┤
    │ • Commands       │     │ • Provider     │
    │ • Rich TUI        │     │ • Dev Team    │
    │ • Streaming        │     │ • Code Analyzer│
    │ • Help System     │     │ • Test Generator│
    └───────────────────┘     │ • Linter       │
    │                           │ • Reviewer      │
    │                           │ • Rollback      │
    │                           │ • Workflow      │
    │                           │ • Memory        │
    │                           │ • File Ops      │
    │                           └────────────────┘
    │
    ┌───────────────────────────────────┐
    │  Local Processing               │
    │  (Privacy-First by default)     │
    │                                 │
    │  • File System Operations        │
    │  • AST Parsing                  │
    │  • Local LLM (GGUF)            │
    │  • ChromaDB (Embeddings)        │
    └───────────────────────────────────┘
```

**Key Design Principles:**
- 🎯 **Privacy-First** - Local by default, explicit cloud use
- 🔄 **Extensibility** - Easy to add custom agents, providers, tools
- 🔓 **Modularity** - Each component independent but integrated
- 📊 **Observability** - Clear logs, audit trails
- 🛡️ **Safety** - Rollback, snapshots, validation

---

## 🤖 Supported Providers

### Local (Privacy-Focused)

| Provider | Privacy | Cost | Best For | Setup |
|----------|---------|-------|---------|-------|
| **Local GGUF** | ⭐⭐⭐⭐⭐ | Free | Sensitive code, privacy-critical | Download model |

### Cloud (Performance-Focused)

| Provider | Privacy | Cost | Best For | Setup |
|----------|---------|-------|---------|-------|
| **OpenRouter** | ⭐⭐⭐ | Token-based | Multiple models | API Key |
| **Anthropic** | ⭐⭐⭐ | Token-based | Claude models | API Key |
| **OpenAI** | ⭐⭐ | Token-based | GPT-4, 3.5 | API Key |

**Switching is instant** - Change providers on the fly without restarting!

---

## 🔄 Continuous Improvement

### Current Capabilities

✅ Multi-agent collaboration
✅ Seamless provider switching
✅ Complete chat integration
✅ Privacy-first architecture
✅ Rollback & snapshots
✅ AST-based code analysis
✅ AI-powered test generation
✅ Multi-linter integration
✅ Intelligent code review
✅ Workflow automation
✅ All features in chat interface

### Planned Enhancements

🚧 **Phase 1: Enhanced UX** (Next 2-3 weeks)
- Real-time streaming with visual progress
- Rich TUI with file browser
- Project knowledge graph with semantic search
- Performance optimizations

🚧 **Phase 2: Integration Layer** (Next 1-2 months)
- REST API for programmatic access
- WebSocket server for real-time streaming
- VS Code extension (inline completions, chat panel)
- Web dashboard for visual project management

🚧 **Phase 3: Advanced Features** (Next 3-6 months)
- Real semantic code graph with embeddings
- Agent marketplace (community-shared agents)
- Project-specific fine-tuning
- Team collaboration features
- Enterprise capabilities (SSO, audit logs)

---

## 📊 Comparison

### Blonde CLI vs Competitors

| Capability | Blonde CLI | Claude Cursor | GitHub Copilot | Sourcegraph |
|------------|-------------|---------------|---------------|-------------|
| **Multi-Agent AI** | ✅ 9 agents | ❌ 1 AI | ❌ 1 AI | ❌ 1 AI |
| **Provider Switching** | ✅ 4+ providers | ❌ 1-2 providers | ❌ 1 provider | ❌ 2 providers |
| **Privacy-First** | ✅ Local by default | ❌ Cloud by default | ❌ Cloud by default | ✅ Mixed |
| **All in Chat** | ✅ 40+ commands | ✅ 10+ commands | ✅ Basic | ✅ Basic |
| **Peer Review** | ✅ Agent-to-agent | ❌ | ❌ | ❌ | ❌ |
| **Self-Improving** | ✅ Continuous loops | ❌ | ❌ | ❌ | ❌ |
| **Rollback System** | ✅ Snapshots | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Open Source** | ✅ 100% | ❌ | ❌ | ❌ | ❌ |
| **Custom Agents** | ✅ Easy to add | ❌ | ❌ | ❌ | ❌ |
| **Knowledge Base** | ✅ Per agent | ❌ | ❌ | ❌ | ✅ |
| **Privacy Controls** | ✅ Complete | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Terminal-First** | ✅ Best in terminal | ❌ GUI only | ❌ | ❌ | ❌ |

**Unique Value:** "The only tool where multiple AI agents collaborate to build better code, with complete privacy controls."

---

## 🔒 Privacy Guarantee

Blonde CLI is designed from the ground up to respect your privacy:

### Privacy Principles

1. **Local Processing by Default**
   - All file operations happen locally
   - Code analysis runs on your machine
   - Refactoring stays on your system

2. **Explicit Cloud Usage**
   - Clear warnings before using cloud providers
   - Show what data will be sent
   - Require confirmation for cloud AI
   - Provider privacy ratings

3. **Data Control**
   - Choose what's stored (chat history, embeddings, snapshots)
   - Choose retention period
   - Enable/disable encryption
   - Delete all data with one command

4. **Transparency**
   - See exactly what's sent where
   - Audit logs for all cloud usage
   - Open source code for verification

5. **No Hidden Tracking**
   - No telemetry by default
   - No usage analytics
   - No crash reporting
   - Opt-in only

### Privacy Tiers

| Tier | Description | When Used |
|------|-------------|-----------|
| **Local Only** | 100% private | Always recommended |
| **Privacy Cloud** | Logs usage only | Good balance |
| **Standard Cloud** | May train on data | Use with caution |

---

## 🤝 Contributing

We welcome contributions! Blonde CLI is built to be modular and extensible.

### Areas to Contribute

1. **New Agents** - Create specialized AI agents
2. **New Providers** - Add support for more AI providers
3. **Linter Integration** - Add support for more languages/tools
4. **Test Frameworks** - Add support for more testing frameworks
5. **Documentation** - Improve guides and examples
6. **Performance** - Optimize for speed and memory
7. **Privacy Features** - Enhance data controls

### Contributing Guidelines

- Follow privacy-first principles
- Add tests for new features
- Document all changes
- Respect existing code style
- Ensure type safety

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

**Free to use** for personal and commercial projects
**Free to modify** - Custom agents, workflows, tools
**Free to distribute** - Share your custom agents with community
**Privacy-respecting** - User data always stays local

---

## 🙏 Acknowledgments

Built with:
- [Typer](https://typer.tiangolo.com/) - Beautiful CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [OpenRouter](https://openrouter.ai/) - AI model access
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) - Local LLM inference

Inspired by:
- [Cursor](https://cursor.sh/) - Multi-agent approach
- [Sourcegraph](https://sourcegraph.com/) - Code intelligence
- [GitHub Copilot](https://github.com/features/copilot) - AI assistance

---

## 🚀 Get Started Now

```bash
# Install
pip install blonde-cli

# Start the experience
blnd chat

# Try a multi-agent task
blnd chat
You: /team collab Build a REST API with authentication
# → Watch 9 AI agents work together!

# Switch providers
blnd provider switch local    # For privacy
blnd provider switch anthropic # For power
```

---

<div align="center">

### ⭐ Star on GitHub

If Blonde CLI helps you build better code, please star us!

[https://github.com/cerekinorg/Blonde-Blip](https://github.com/cerekinorg/Blonde-Blip)

### 📖 Explore Documentation

- [Quick Start Guide](./QUICKSTART.md)
- [Complete Features](./FEATURES.md)
- [Privacy Guide](./PRIVACY.md)
- [Provider & Team](./PROVIDER_TEAM.md)
- [Backend Architecture](./BACKEND_GUIDE.md)

---

<div align="center">

**Blonde CLI: Where AI Agents Collaborate to Build Better Code, Privately.** 🚀🔒

</div>
