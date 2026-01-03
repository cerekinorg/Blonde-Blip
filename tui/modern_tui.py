"""
Modern Textual-based TUI for Blonde CLI
Like OpenCode: Dynamic, feature-rich terminal user interface

Features:
- File viewer and editor
- Blip mascot integration
- Agent status sidebar
- Working directory display
- Settings modal (Ctrl+S)
- Command palette (Ctrl+P)
- Chat interface
- Real-time updates
"""

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Static, DirectoryTree, RichLog, Input, 
    DataTable, Button, Label, Tabs, Tab, ContentSwitcher,
    MarkdownViewer, ProgressBar
)
from textual.containers import Horizontal, Vertical, Container, ScrollableContainer
from textual.screen import ModalScreen
from textual import events, on
from textual.reactive import reactive
from rich.text import Text
from rich.console import Console
from pathlib import Path
import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from tui.blip import Blip, blip


class BlipWidget(Static):
    """Widget to display Blip mascot with current state"""
    
    state = reactive("idle")
    message = reactive("")
    
    def __init__(self, blip_instance: Blip):
        super().__init__()
        self.blip_instance = blip_instance
        self.border_title = "Blip"
    
    def watch_state(self, old_state: str, new_state: str) -> None:
        """Update Blip when state changes"""
        self.update_content()
    
    def watch_message(self, old_message: str, new_message: str) -> None:
        """Update Blip when message changes"""
        self.update_content()
    
    def update_content(self) -> None:
        """Update Blip display"""
        art = self.blip_instance.get_art(self.state)
        color = self.blip_instance.get_color(self.state)
        
        content = f"[{color}]{art}[/{color}]\n\n"
        if self.message:
            content += f"{self.message}"
        
        self.update(content)


class AgentStatusTable(DataTable):
    """DataTable showing status of all agents"""
    
    def __init__(self):
        super().__init__()
        self.agent_statuses = {
            "Generator": {"status": "waiting", "message": "", "icon": "🧱"},
            "Reviewer": {"status": "waiting", "message": "", "icon": "🔍"},
            "Tester": {"status": "waiting", "message": "", "icon": "🧪"},
            "Refactorer": {"status": "waiting", "message": "", "icon": "🔨"},
            "Documenter": {"status": "waiting", "message": "", "icon": "📝"},
            "Architect": {"status": "waiting", "message": "", "icon": "🏗️"},
            "Security": {"status": "waiting", "message": "", "icon": "🔒"},
            "Debugger": {"status": "waiting", "message": "", "icon": "🐛"}
        }
    
    def on_mount(self) -> None:
        """Initialize table columns"""
        self.add_column("Agent", width=15)
        self.add_column("Status", width=10)
        self.add_column("Message", width=30)
        self.refresh_table()
    
    def refresh_table(self) -> None:
        """Refresh the table with current agent statuses"""
        self.clear()
        
        status_colors = {
            "working": "yellow",
            "done": "green",
            "error": "red",
            "waiting": "grey"
        }
        
        for agent_name, data in self.agent_statuses.items():
            status = data["status"]
            status_text = Text(status.upper())
            status_text.stylize(status_colors.get(status, "white"))
            
            row_key = self.add_row(
                f"{data['icon']} {agent_name}",
                status_text,
                data.get("message", "")
            )
    
    def update_agent(self, agent_name: str, status: str, message: str = "") -> None:
        """Update a specific agent's status"""
        if agent_name in self.agent_statuses:
            self.agent_statuses[agent_name]["status"] = status
            self.agent_statuses[agent_name]["message"] = message
            self.refresh_table()


class WorkingDirectoryDisplay(Static):
    """Display current working directory"""
    
    def __init__(self):
        super().__init__()
        self.current_dir = str(Path.cwd())
    
    def on_mount(self) -> None:
        """Update display on mount"""
        self.update_content()
    
    def update_content(self) -> None:
        """Update the directory display"""
        content = f"📁 [bold cyan]{self.current_dir}[/bold cyan]"
        self.update(content)
    
    def set_directory(self, directory: str) -> None:
        """Set a new working directory"""
        self.current_dir = directory
        self.update_content()


class FileEditor(Static):
    """File editor component"""
    
    current_file = reactive[Optional[Path]](None)
    file_content = reactive("")
    
    def __init__(self):
        super().__init__()
        self.border_title = "File Editor"
    
    def watch_current_file(self, old_file: Optional[Path], new_file: Optional[Path]) -> None:
        """Load file content when file changes"""
        if new_file and new_file.exists():
            self.load_file(new_file)
            self.border_title = f"File Editor: {new_file.name}"
        else:
            self.file_content = ""
            self.border_title = "File Editor"
        self.update_content()
    
    def watch_file_content(self, old_content: str, new_content: str) -> None:
        """Update display when content changes"""
        self.update_content()
    
    def load_file(self, file_path: Path) -> None:
        """Load content from file"""
        try:
            with open(file_path, 'r') as f:
                self.file_content = f.read()
        except Exception as e:
            self.file_content = f"Error loading file: {e}"
    
    def update_content(self) -> None:
        """Update the editor display"""
        if self.file_content:
            self.update(self.file_content)
        else:
            self.update("No file selected. Use the file browser to select a file.")


class ChatPanel(Vertical):
    """Chat interface panel"""
    
    messages = reactive[List[Dict]]([])
    
    def __init__(self):
        super().__init__()
        self.border_title = "Chat"
    
    def compose(self) -> ComposeResult:
        """Compose chat interface"""
        yield RichLog(id="chat_log", wrap=True, highlight=True)
        yield Input(placeholder="Type your message here...", id="chat_input")
    
    def on_mount(self) -> None:
        """Initialize chat log"""
        self.chat_log = self.query_one("#chat_log", RichLog)
        self.add_message("system", "Welcome to Blonde CLI! Type your message or use Ctrl+P for commands.")
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        role_colors = {
            "system": "bold cyan",
            "user": "bold green",
            "assistant": "bold magenta",
            "error": "bold red"
        }
        
        color = role_colors.get(role, "white")
        prefix = f"[{color}]{role.upper()}[/{color}] [dim]{timestamp}[/dim]"
        self.chat_log.write(f"{prefix}: {content}")
    
    @on(Input.Submitted, "#chat_input")
    def on_chat_submit(self, event: Input.Submitted) -> None:
        """Handle chat message submission"""
        message = event.value.strip()
        if message:
            self.add_message("user", message)
            event.input.value = ""
            
            # Process the message
            self.process_message(message)
    
    def process_message(self, message: str) -> None:
        """Process user message"""
        # This would integrate with actual AI processing
        self.add_message("assistant", f"Processing: {message}...")


class CommandPalette(ModalScreen[str]):
    """Command palette modal"""
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
        ("up", "move_up", "Previous"),
        ("down", "move_down", "Next"),
        ("enter", "select_command", "Select")
    ]
    
    def __init__(self, commands: Dict[str, str]):
        super().__init__()
        self.commands = commands
        self.filtered_commands = list(commands.items())
        self.selected_index = 0
    
    def compose(self) -> ComposeResult:
        """Compose command palette"""
        with Vertical():
            yield Input(placeholder="Search commands...", id="command_search")
            yield DataTable(id="command_table")
    
    def on_mount(self) -> None:
        """Initialize command table"""
        self.search_input = self.query_one("#command_search", Input)
        self.command_table = self.query_one("#command_table", DataTable)
        
        self.command_table.add_column("Command", width=20)
        self.command_table.add_column("Description", width=50)
        self.refresh_commands()
    
    def refresh_commands(self) -> None:
        """Refresh the command table"""
        self.command_table.clear()
        for i, (cmd, desc) in enumerate(self.filtered_commands):
            row_key = self.command_table.add_row(f"/{cmd}", desc)
            if i == self.selected_index:
                self.command_table.cursor_type = "row"
                self.command_table.move_cursor(row=row_key)
    
    def action_move_up(self) -> None:
        """Move selection up"""
        if self.selected_index > 0:
            self.selected_index -= 1
            self.refresh_commands()
    
    def action_move_down(self) -> None:
        """Move selection down"""
        if self.selected_index < len(self.filtered_commands) - 1:
            self.selected_index += 1
            self.refresh_commands()
    
    def action_select_command(self) -> None:
        """Select and return the command"""
        if self.filtered_commands:
            cmd, _ = self.filtered_commands[self.selected_index]
            self.dismiss(cmd)
    
    @on(Input.Changed, "#command_search")
    def on_search_changed(self, event: Input.Changed) -> None:
        """Filter commands based on search"""
        query = event.value.lower()
        self.filtered_commands = [
            (cmd, desc) for cmd, desc in self.commands.items()
            if query in cmd.lower() or query in desc.lower()
        ]
        self.selected_index = 0
        self.refresh_commands()


class SettingsModal(ModalScreen[None]):
    """Settings modal screen"""
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
        ("ctrl+s", "save_settings", "Save"),
        ("ctrl+tab", "next_tab", "Next Tab"),
        ("shift+ctrl+tab", "prev_tab", "Previous Tab")
    ]
    
    def __init__(self, config_path: Path):
        super().__init__()
        self.config_path = config_path
        self.config = self.load_config()
        self.current_tab = "providers"
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            "providers": {},
            "preferences": {
                "privacy_mode": "balanced",
                "show_tips": True,
                "stream_responses": True,
                "show_blip": True
            }
        }
    
    def compose(self) -> ComposeResult:
        """Compose settings modal"""
        with Container(id="settings_container"):
            yield Tabs("Providers", "Privacy", "UI", "Agents")
            with ContentSwitcher():
                with Vertical(id="providers_tab"):
                    yield Static("AI Providers Configuration")
                    yield DataTable(id="providers_table")
                    yield Button("Add Provider", id="add_provider_btn")
                with Vertical(id="privacy_tab"):
                    yield Static("Privacy Settings")
                    # Add privacy controls
                with Vertical(id="ui_tab"):
                    yield Static("UI Preferences")
                    # Add UI controls
                with Vertical(id="agents_tab"):
                    yield Static("Agent Configuration")
                    # Add agent controls
    
    def on_mount(self) -> None:
        """Initialize settings"""
        self.tabs = self.query_one(Tabs)
        self.switcher = self.query_one(ContentSwitcher)
        self.action_next_tab()  # Show first tab
    
    def action_next_tab(self) -> None:
        """Switch to next tab"""
        self.tabs.active = (self.tabs.active + 1) % len(self.tabs)
    
    def action_prev_tab(self) -> None:
        """Switch to previous tab"""
        self.tabs.active = (self.tabs.active - 1) % len(self.tabs)
    
    @on(Tabs.TabActivated)
    def on_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle tab activation"""
        tab_names = ["providers", "privacy", "ui", "agents"]
        self.current_tab = tab_names[event.tab_index]
        self.switcher.current = f"{self.current_tab}_tab"
    
    def action_save_settings(self) -> None:
        """Save settings to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.notify("Settings saved successfully!", severity="information")
        except Exception as e:
            self.notify(f"Error saving settings: {e}", severity="error")


class ModernTUI(App):
    """Main modern TUI application"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 4 4;
        grid-rows: 3 1fr 1fr 3;
    }
    
    #header {
        column-span: 4;
    }
    
    #sidebar {
        row-span: 2;
        border: solid $primary;
        background: $panel;
    }
    
    #main_content {
        row-span: 2;
        border: solid $primary;
        background: $surface;
    }
    
    #chat_panel {
        column-span: 3;
        row-span: 1;
        border: solid $primary;
        background: $surface;
    }
    
    #footer {
        column-span: 4;
    }
    
    BlipWidget {
        padding: 1;
        margin: 1;
    }
    
    AgentStatusTable {
        height: 20;
    }
    
    WorkingDirectoryDisplay {
        padding: 1;
        background: $panel;
    }
    
    ChatPanel {
        height: 100%;
    }
    
    #chat_log {
        height: 1fr;
        border: solid $primary;
    }
    
    #chat_input {
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+p", "show_command_palette", "Commands"),
        ("ctrl+s", "show_settings", "Settings"),
        ("ctrl+e", "toggle_editor", "Toggle Editor"),
        ("ctrl+b", "toggle_blip", "Toggle Blip"),
        ("ctrl+a", "show_agents", "Show Agents"),
        ("f1", "show_help", "Help")
    ]
    
    def __init__(self):
        super().__init__()
        self.blip_instance = Blip()
        self.config_path = Path.home() / ".blonde" / "config.json"
        self.show_editor = True
        self.show_blip = True
        self.show_agents = True
        
        # Command palette commands
        self.commands = {
            "chat": "Start AI chat session",
            "generate": "Generate code from prompt",
            "fix": "Fix bugs in code",
            "test": "Generate tests",
            "analyze": "Analyze code",
            "refactor": "Refactor code",
            "document": "Generate documentation",
            "settings": "Configure settings",
            "providers": "Manage AI providers",
            "mcp": "Manage MCP servers",
            "clear": "Clear screen",
            "help": "Show help"
        }
    
    def compose(self) -> ComposeResult:
        """Compose the TUI layout"""
        yield Header(id="header")
        
        with Container(id="sidebar"):
            yield WorkingDirectoryDisplay()
            yield BlipWidget(self.blip_instance)
            yield AgentStatusTable()
        
        with Container(id="main_content"):
            with Horizontal():
                yield DirectoryTree(str(Path.cwd()), id="file_browser")
                yield FileEditor()
        
        with Container(id="chat_panel"):
            yield ChatPanel()
        
        yield Footer(id="footer")
    
    def on_mount(self) -> None:
        """Initialize on mount"""
        self.title = "Blonde CLI - Modern TUI"
        self.sub_title = "Multi-Agent AI Development Assistant"
        
        # Update Blip state
        self.blip_widget = self.query_one(BlipWidget)
        self.blip_widget.message = "Ready to help!"
        self.blip_widget.state = "happy"
        
        # Initialize working directory
        self.working_dir = self.query_one(WorkingDirectoryDisplay)
        
        # Initialize agent status
        self.agent_table = self.query_one(AgentStatusTable)
        
        # Initialize file browser
        self.file_browser = self.query_one("#file_browser", DirectoryTree)
        self.file_editor = self.query_one(FileEditor)
    
    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection"""
        path = Path(event.path)
        self.file_editor.current_file = path
        self.blip_widget.message = f"Selected: {path.name}"
        self.blip_widget.state = "working"
    
    def action_show_command_palette(self) -> None:
        """Show command palette"""
        self.push_screen(CommandPalette(self.commands), self.handle_command)
    
    def handle_command(self, command: Optional[str]) -> None:
        """Handle selected command"""
        if command:
            chat_panel = self.query_one(ChatPanel)
            chat_panel.add_message("system", f"Executing: /{command}")
            self.blip_widget.message = f"Running: {command}"
            self.blip_widget.state = "working"
    
    def action_show_settings(self) -> None:
        """Show settings modal"""
        self.push_screen(SettingsModal(self.config_path))
    
    def action_toggle_editor(self) -> None:
        """Toggle file editor visibility"""
        self.show_editor = not self.show_editor
        self.notify(f"Editor: {'Enabled' if self.show_editor else 'Disabled'}")
    
    def action_toggle_blip(self) -> None:
        """Toggle Blip visibility"""
        self.show_blip = not self.show_blip
        blip_widget = self.query_one(BlipWidget)
        blip_widget.display = self.show_blip
        self.notify(f"Blip: {'Enabled' if self.show_blip else 'Disabled'}")
    
    def action_show_agents(self) -> None:
        """Show/hide agent status"""
        self.show_agents = not self.show_agents
        agent_table = self.query_one(AgentStatusTable)
        agent_table.display = self.show_agents
        self.notify(f"Agent Status: {'Enabled' if self.show_agents else 'Disabled'}")
    
    def action_show_help(self) -> None:
        """Show help"""
        help_text = """
        [bold]Blonde CLI - Modern TUI[/bold]

        [cyan]Keyboard Shortcuts:[/cyan]
        Ctrl+P - Command Palette
        Ctrl+S - Settings
        Ctrl+E - Toggle Editor
        Ctrl+B - Toggle Blip
        Ctrl+A - Toggle Agent Status
        F1 - Help
        Ctrl+Q - Quit

        [cyan]Features:[/cyan]
        • File browser and editor
        • Real-time agent status
        • Interactive chat interface
        • Blip mascot guidance
        • Configurable settings
        • Command palette for quick actions
        """
        self.notify(help_text, title="Help", severity="information")
    
    def update_agent_status(self, agent_name: str, status: str, message: str = "") -> None:
        """Update an agent's status (external API)"""
        agent_table = self.query_one(AgentStatusTable)
        agent_table.update_agent(agent_name, status, message)
        
        # Update Blip based on status
        if status == "working":
            self.blip_widget.state = "working"
            self.blip_widget.message = f"{agent_name} is working..."
        elif status == "done":
            self.blip_widget.state = "success"
            self.blip_widget.message = f"{agent_name} completed!"
        elif status == "error":
            self.blip_widget.state = "error"
            self.blip_widget.message = f"{agent_name} encountered an error"
    
    def set_blip_message(self, message: str, state: str = "idle") -> None:
        """Set Blip message and state (external API)"""
        self.blip_widget.message = message
        self.blip_widget.state = state


def launch_modern_tui():
    """Launch the modern TUI application"""
    app = ModernTUI()
    app.run()


if __name__ == "__main__":
    launch_modern_tui()
