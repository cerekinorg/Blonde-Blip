# Blonde CLI - Current Features

## Core CLI Commands

- **`blnd chat`**
  - Interactive chat mode.
  - Supports streaming output.
  - Optional memory and agentic tool usage.

- **`blnd gen` / `blnd fix` / `blnd doc` / `blnd create`**
  - Available in the CLI help output.

## Models

- **OpenRouter (default)**
  - Uses `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` from environment.

- **Offline local model support (GGUF)**
  - Available via `--offline` and model selection flow (when enabled).

## Memory (optional)

- **Conversation memory**
  - Enabled in chat with `--memory/--no-memory`.
  - Uses `chromadb` if installed.

## Agentic Mode (optional)

When enabled (`--agentic`), Blonde can execute multi-step tasks using tools.

### Built-in Enhanced Tools

- **File operations**
  - `read_file`, `write_file`, `edit_file`, `delete_file`, `rename_file`

- **Directory operations**
  - `list_dir`, `create_dir`, `search_files`, `search_in_files`

- **Code operations**
  - `replace_in_file`, `insert_at_line`, `remove_lines`

- **Git operations**
  - `git_status`, `git_diff`, `git_add`, `git_commit`

- **Terminal**
  - `run_command`
  - Requires confirmation for destructive actions.

## MCP Tool Integration (stdio)

Blonde supports loading MCP servers over **stdio** and registering their tools into the agentic tool registry.

### How MCP is loaded

- MCP is only attempted if the user config exists:
  - `~/.blonde/mcp_servers.json`
- CLI flags:
  - `--mcp-disable` disables MCP loading.
  - `--mcp-servers <ids>` loads only a comma-separated allowlist.

### Tool override strategy

- MCP tools are registered by tool name.
- If an MCP tool has the same name as a built-in tool, the MCP tool **overrides** the built-in tool.

### Default MCP server definitions (templates)

The repository includes default MCP server templates in `tui/mcp_config.py`:

- **Filesystem**: `@modelcontextprotocol/server-filesystem`
- **GitHub**: `@modelcontextprotocol/server-github` (requires `GITHUB_TOKEN`)
- **Web Search (optional)**: `@tavily-ai/tavily-mcp` (requires `TAVILY_API_KEY`)

To enable them, create `~/.blonde/mcp_servers.json` (copy from defaults) and set env vars as needed.

---

# NEW ADVANCED FEATURES

## Advanced Code Analysis

### AST-Based Code Understanding
- **Deep code entity extraction** using Abstract Syntax Trees
- **Code complexity analysis** with cyclomatic complexity metrics
- **Dependency tracking** between functions, classes, and modules
- **Code relationship analysis** - find callers, usages, and cross-references
- **Code quality metrics** - calculate maintainability and complexity scores
- **Code smell detection** - identify long functions, god classes, and anti-patterns

**Usage:**
```bash
blnd analyze <file>              # Analyze single file
blnd analyze-repo <directory>     # Analyze entire repository
blnd find-similar <code>          # Find similar code patterns
blnd code-quality                 # Generate quality report
```

## Repository-Wide Code Search & Refactoring

### Advanced Search Capabilities
- **Symbol search** - find functions, classes, variables across codebase
- **Pattern search** - regex-based code search
- **Similar code detection** - find duplicate or similar code blocks
- **Cross-language support** - Python, JavaScript, TypeScript, Go, and more

### Intelligent Refactoring
- **Safe symbol renaming** across entire codebase
- **Function extraction** - extract code blocks into functions
- **Function inlining** - inline small functions
- **Bulk operations** - apply changes across multiple files
- **Dependency analysis** - understand impact before refactoring

**Usage:**
```bash
blnd search <symbol>              # Search for symbol
blnd search-pattern <regex>       # Regex search
blnd rename <old> <new>          # Rename symbol across repo
blnd extract-func <file> <line>   # Extract function
blnd find-similar <code>          # Find similar code
```

## Test Generation & Analysis

### AI-Powered Test Generation
- **Automatic test generation** from source code
- **Multi-language support** - Python (pytest), JavaScript/TypeScript (Jest), Go
- **Edge case detection** - automatically identify and test edge cases
- **Test suite creation** - generate comprehensive test suites
- **Coverage analysis** - measure and report test coverage

### Test Execution & Reporting
- **Run tests** with integrated test runners
- **Generate test reports** with pass/fail statistics
- **Coverage reports** - see what code is tested
- **Failed test analysis** - understand why tests fail

**Usage:**
```bash
blnd generate-tests <file>        # Generate tests for file
blnd run-tests                    # Run test suite
blnd test-coverage                 # Check coverage
blnd test-report                   # Generate test report
```

## Intelligent Code Review & Linting

### Multi-Linter Integration
- **Python** - Flake8, Pylint, Ruff
- **JavaScript/TypeScript** - ESLint
- **Go** - go vet, golint
- **Custom linters** - integrate any command-line linter

### AI-Powered Code Review
- **Automated code reviews** using LLM
- **Bug detection** - find potential bugs and logic errors
- **Security analysis** - identify vulnerabilities and security issues
- **Performance suggestions** - optimization recommendations
- **Best practice checks** - ensure code follows best practices
- **Maintainability scoring** - assess code maintainability

**Usage:**
```bash
blnd lint <file>                  # Lint a file
blnd lint-repo                    # Lint entire repository
blnd review <file>                # AI code review
blnd review-diff                  # Review code changes
```

## Rollback & Undo System

### Operation Tracking
- **Automatic operation tracking** for all file operations
- **Snapshot creation** - capture entire project state
- **Operation history** - view all tracked operations
- **Selective rollback** - rollback specific operations
- **Project snapshots** - restore entire project to a point in time

### Safe File Operations
- **Safe editing** - automatically backup before changes
- **Safe deletion** - track and restore deleted files
- **Safe renaming** - track file moves and renames
- **Undo capability** - revert any operation

**Usage:**
```bash
blnd snapshot create <name>       # Create snapshot
blnd snapshot restore <name>       # Restore snapshot
blnd history                      # View operation history
blnd undo                         # Undo last operation
blnd rollback <operation_id>      # Rollback specific operation
```

## Workflow Automation

### Pre-Built Workflows
- **Project setup** - Python, Node.js, Go project initialization
- **Code quality checks** - run linting, testing, and coverage
- **Pre-commit checks** - automated validation before commits
- **CI/CD pipelines** - common deployment workflows

### Custom Workflows
- **Create workflows** - define custom automation scripts
- **Workflow variables** - parameterize workflows
- **Step dependencies** - define execution order
- **Error handling** - continue on error or fail fast

**Usage:**
```bash
blnd workflow list                # List available workflows
blnd workflow run <name>          # Run a workflow
blnd workflow create <name>       # Create custom workflow
blnd workflow enable/disable       # Enable/disable workflows
```

## Notes / Known Limitations

- MCP servers must follow the MCP stdio transport rules:
  - newline-delimited JSON-RPC messages
  - no non-MCP output on `stdout` (logs must go to `stderr`)

## Installation of New Features

To use all new features, install additional dependencies:

```bash
pip install -r requirements.txt

# For linting integration (optional)
pip install pylint flake8 ruff

# For test coverage
pip install coverage

# For tree-sitter AST parsing (advanced code analysis)
# Uncomment in requirements.txt and run:
# pip install tree-sitter tree-sitter-languages
```

## Environment Variables

Required:
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `OPENROUTER_MODEL` - Model to use (default: openai/gpt-oss-20b:free)

Optional:
- `OPENAI_API_KEY` - For OpenAI models
- `GITHUB_TOKEN` - For GitHub MCP server
- `TAVILY_API_KEY` - For web search MCP server

## Directory Structure

```
~/.blonde/                      # User config directory
  ├── mcp_servers.json          # MCP server configurations
  └── debug.log                 # Debug logs

<project>/.blonde/              # Project-specific directory
  ├── snapshots/                # Project snapshots
  └── workflows/                # Custom workflows
```
