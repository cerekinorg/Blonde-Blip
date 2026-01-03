# Modern Textual TUI for Blonde CLI

## Overview

The Modern Textual TUI is a new, feature-rich terminal user interface for Blonde CLI, inspired by OpenCode. It provides a dynamic, interactive experience with all the features you need.

## Features

### 📁 File Browser & Editor
- **Directory Tree**: Navigate your project files with an interactive tree
- **File Editor**: View and edit files directly in the TUI
- **Real-time Updates**: Files update as you navigate

### 🤖 Agent Status Panel
- **Live Agent Status**: See all 8 agents in real-time
  - 🧱 Generator - Code generation
  - 🔍 Reviewer - Code quality
  - 🧪 Tester - Test generation
  - 🔨 Refactorer - Code improvement
  - 📝 Documenter - Documentation
  - 🏗️ Architect - System design
  - 🔒 Security - Security audit
  - 🐛 Debugger - Bug fixing
- **Status Indicators**: Working, Done, Error, Waiting
- **Progress Messages**: Real-time updates from each agent

### 💬 Blip Mascot
- **Dynamic Animations**: Blip shows different states (idle, happy, working, thinking, error)
- **Context-Aware Messages**: Blip guides you through tasks
- **Visual Feedback**: See what the system is doing at a glance

### 📍 Working Directory Display
- **Current Location**: Always see where you are in the project
- **Project Context**: Understand your workspace

### 🎯 Command Palette (Ctrl+P)
- **Quick Access**: Fast command execution
- **Search Filter**: Find commands instantly
- **Command List**:
  - `/chat` - Start AI chat session
  - `/generate` - Generate code from prompt
  - `/fix` - Fix bugs in code
  - `/test` - Generate tests
  - `/analyze` - Analyze code
  - `/refactor` - Refactor code
  - `/document` - Generate documentation
  - `/settings` - Configure settings
  - `/providers` - Manage AI providers
  - `/mcp` - Manage MCP servers

### ⚙️ Settings Panel (Ctrl+S)
- **Tabbed Interface**: Organized settings categories
  - **Providers**: Configure AI providers
  - **Privacy**: Privacy & data settings
  - **UI**: Interface preferences
  - **Agents**: Agent configuration
- **Real-time Updates**: Changes apply immediately
- **Save/Reset**: Easy management

### 💬 Chat Interface
- **Interactive Chat**: Type messages and get AI responses
- **Message History**: See previous messages
- **Timestamps**: Track conversation flow
- **Rich Formatting**: Markdown and code block support

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` or `Ctrl+Q` | Quit the TUI |
| `Ctrl+P` | Open command palette |
| `Ctrl+S` | Open settings modal |
| `Ctrl+E` | Toggle file editor visibility |
| `Ctrl+B` | Toggle Blip visibility |
| `Ctrl+A` | Toggle agent status panel |
| `F1` | Show help |

## Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Header - Blonde CLI Title & Info                          │
├─────────────┬───────────────────────────────────────────┤
│ Sidebar    │ Main Content Area                           │
│             │                                           │
│ 📍 WorkDir  │ 📂 File Browser | 📝 File Editor     │
│             │                                           │
│ 💬 Blip     │                                           │
│             │                                           │
│ 🤖 Agents   │                                           │
│             │                                           │
├─────────────┴───────────────────────────────────────────┤
│ Chat Panel - Interactive chat interface                  │
├─────────────────────────────────────────────────────────────┤
│ Footer - Keyboard shortcuts & status                      │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Launch Modern TUI

```bash
# Method 1: Using the wrapper script
./blonde-modern

# Method 2: Using Python module
python3 -m tui.modern_tui

# Method 3: Using blonde CLI with --modern flag
blonde --modern
```

### Basic Workflow

1. **Navigate Files**: Use the file browser to explore your project
2. **Select File**: Click or use arrow keys + Enter to select files
3. **View/Edit**: Selected files appear in the editor panel
4. **Chat**: Type messages in the chat panel for AI assistance
5. **Monitor Agents**: Watch agents update their status in real-time
6. **Use Commands**: Press `Ctrl+P` for quick command access
7. **Configure**: Press `Ctrl+S` to open settings

### Example Commands

```bash
# Start a chat session
/chat

# Generate code
/generate "Create a REST API with authentication"

# Fix a file
/fix user_service.py

# Analyze code
/analyze app.py

# Generate tests
/test auth.py

# Refactor code
/refactor user_module.py

# Generate documentation
/document api.py
```

## Integration with Blonde CLI

The modern TUI integrates seamlessly with all Blonde CLI features:

### Memory System
- Automatically loads conversation memory
- Context-aware responses
- Persistent learning across sessions

### Agentic Tools
- Enhanced tool registry
- Autonomous task execution
- File operations, Git, Analysis tools

### MCP Integration
- Configure MCP servers
- Use external tools via MCP
- Dynamic tool loading

### Multi-Agent System
- All 8 agents available
- Real-time status updates
- Parallel/Sequential execution modes

### Provider Management
- Switch between AI providers
- Test provider connections
- Configure API keys

## Configuration

Settings are stored in `~/.blonde/config.json`:

```json
{
  "version": "1.0.0",
  "default_provider": "openrouter",
  "providers": {
    "openrouter": {
      "api_key": "...",
      "model": "openai/gpt-4"
    }
  },
  "preferences": {
    "privacy_mode": "balanced",
    "show_tips": true,
    "stream_responses": true,
    "show_blip": true,
    "colors": "auto"
  }
}
```

## Development

### Project Structure

```
tui/
├── modern_tui.py       # Main Modern TUI application
├── blip.py            # Blip mascot widget
├── cli.py             # CLI with modern flag support
└── ...
```

### Extending the TUI

To add new features:

1. **Add Widgets**: Create new Textual widgets in `modern_tui.py`
2. **Update Layout**: Modify the CSS grid layout
3. **Add Bindings**: Register new keyboard shortcuts
4. **Connect Events**: Add event handlers for interactivity

### Widget Components

- `BlipWidget`: Displays the Blip mascot with state
- `AgentStatusTable`: DataTable showing all agent statuses
- `WorkingDirectoryDisplay`: Shows current directory
- `FileEditor`: File viewer and editor
- `ChatPanel`: Interactive chat interface
- `CommandPalette`: Modal for command search
- `SettingsModal`: Tabbed settings interface

## Troubleshooting

### Textual Not Installed

```bash
pip install textual>=0.44.0
```

### Terminal Compatibility

The modern TUI requires a terminal that supports:
- 256-color mode
- Mouse support (optional)
- Unicode characters

Recommended terminals:
- iTerm2 (macOS)
- GNOME Terminal (Linux)
- Windows Terminal (Windows)
- Alacritty (cross-platform)

### Performance Issues

For large projects:
- Use `Ctrl+E` to hide the editor panel
- Use `Ctrl+A` to hide the agent panel
- Disable Blip with `Ctrl+B` for minimal mode

## Future Enhancements

Planned features:
- [ ] Split-pane editor
- [ ] Multiple file tabs
- [ ] Syntax highlighting in editor
- [ ] Git integration panel
- [ ] Task queue visualization
- [ ] Agent communication logs
- [ ] Code diff viewer
- [ ] Test runner integration
- [ ] Deployment panel
- [ ] Custom themes support

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.
