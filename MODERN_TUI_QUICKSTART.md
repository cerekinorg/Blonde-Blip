# Quick Start Guide - Modern Textual TUI

## Installation

The Textual library is already included in the updated requirements. If you need to install it manually:

```bash
pip install textual>=0.44.0
```

## Launch the Modern TUI

You have three options to launch the modern TUI:

### Option 1: Using the wrapper script (Recommended)

```bash
./blonde-modern
```

### Option 2: Using Python module

```bash
python3 -m tui.modern_tui
```

### Option 3: Using blonde CLI with --modern flag

```bash
blonde --modern
```

## First-Time Setup

On first launch, if no configuration exists, the setup wizard will run automatically.

## Keyboard Shortcuts

**Essential Shortcuts:**
- `Ctrl+C` or `Ctrl+Q` - Quit TUI
- `Ctrl+P` - Open command palette
- `Ctrl+S` - Open settings

**Panel Toggles:**
- `Ctrl+E` - Toggle file editor
- `Ctrl+B` - Toggle Blip mascot
- `Ctrl+A` - Toggle agent status panel

**Help:**
- `F1` - Show help

## Basic Workflow

1. **Launch** the modern TUI
2. **Explore** your files in the file browser (left panel)
3. **Select** a file to view it in the editor
4. **Chat** with AI in the bottom panel
5. **Monitor** agent activity in the sidebar
6. **Use commands** via `Ctrl+P` for quick actions
7. **Configure** settings with `Ctrl+S`

## Command Palette Commands

Press `Ctrl+P` and type to search:

- `/chat` - Start AI chat
- `/generate` - Generate code
- `/fix` - Fix bugs
- `/test` - Generate tests
- `/analyze` - Analyze code
- `/refactor` - Refactor code
- `/document` - Generate docs
- `/settings` - Configure
- `/providers` - Manage AI
- `/mcp` - Manage MCP

## Layout Overview

```
┌──────────────────────────────────────────────────────────┐
│ Header: Blonde CLI - Modern TUI                     │
├──────────┬───────────────────────────────────────────┤
│ Sidebar  │ Main Content                            │
│          │                                         │
│ 📍 Dir   │ 📂 Files | 📝 Editor                │
│ 💬 Blip  │                                         │
│ 🤖 Agents│                                         │
├──────────┴───────────────────────────────────────────┤
│ Chat Panel: Interactive AI chat                     │
├──────────────────────────────────────────────────────────┤
│ Footer: Shortcuts and status                        │
└──────────────────────────────────────────────────────────┘
```

## Features

### ✅ Currently Implemented

- [x] File browser with directory tree
- [x] File viewer/editor panel
- [x] Blip mascot with animations
- [x] Agent status table (8 agents)
- [x] Working directory display
- [x] Interactive chat interface
- [x] Command palette (Ctrl+P)
- [x] Settings modal (Ctrl+S)
- [x] Panel toggles (Ctrl+E/B/A)
- [x] Real-time updates
- [x] Message history with timestamps
- [x] Tabbed settings interface

### 🚧 Coming Soon

- [ ] Syntax highlighting in editor
- [ ] Multiple file tabs
- [ ] Git integration panel
- [ ] Test runner
- [ ] Code diff viewer
- [ ] Task queue visualization
- [ ] Custom themes
- [ ] Agent communication logs

## Troubleshooting

### Terminal Issues

If you see display issues:
1. Ensure your terminal supports 256 colors
2. Try a modern terminal (iTerm2, GNOME Terminal, Windows Terminal)
3. Check that your terminal supports Unicode

### Performance

For large projects:
- Use `Ctrl+E` to hide the editor panel
- Use `Ctrl+A` to hide agent panel
- Use `Ctrl+B` to hide Blip for minimal mode

### Configuration

Settings are stored in: `~/.blonde/config.json`

## Getting Help

- Press `F1` inside the TUI for help
- See `MODERN_TUI_README.md` for detailed documentation
- Check the main `README.md` for general Blonde CLI help

## Integration

The modern TUI works with all Blonde CLI features:
- Memory system (conversation context)
- Agentic tools (file operations, Git, analysis)
- MCP integration (external tools)
- Multi-agent system (8 specialized agents)
- Provider management (OpenRouter, OpenAI, Anthropic, Local)

## Next Steps

1. Launch the TUI: `./blonde-modern`
2. Explore the interface
3. Try the command palette: `Ctrl+P`
4. Configure your settings: `Ctrl+S`
5. Start a chat session and interact with AI agents!

Enjoy the new modern TUI experience! 🚀
