"""
Blonde CLI - Modern Textual TUI
A comprehensive, feature-rich terminal UI with all capabilities

Features:
- File browser and editor
- Blip mascot integration
- Agent status monitoring
- Working directory display
- Interactive chat interface
- Command palette (Ctrl+P)
- Settings modal (Ctrl+S)
- All agent operations
"""

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Static, DirectoryTree, RichLog, Input, 
    DataTable, Button, Tabs, Tab, ContentSwitcher,
    Markdown, ProgressBar
)
from textual.containers import Horizontal, Vertical, Container, ScrollableContainer
from textual.screen import ModalScreen
from textual import events, on
from textual.reactive import reactive
from rich.text import Text
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
import os
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

# Check if textual is available
try:
    from textual import __version__ as textual_version
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    textual_version = None

# Import Blip
try:
    from tui.blip import Blip, blip
    BLIP_AVAILABLE = True
except ImportError:
    BLIP_AVAILABLE = False
    blip = None

CONFIG_DIR = Path.home() / ".blonde"
CONFIG_FILE = CONFIG_DIR / "config.json"


class BlipWidget(Static):
    """Widget displaying Blip mascot with state"""
    
    state = reactive("idle")
    message = reactive("")
    
    def __init__(self, blip_instance: Optional[Blip] = None):
        super().__init__()
        self.blip_instance = blip_instance or blip
        self.border_title = "Blip"
    
    def watch_state(self, old_state: str, new_state: str) -> None:
        self.update_content()
    
    def watch_message(self, old_message: str, new_message: str) -> None:
        self.update_content()
    
    def update_content(self) -> None:
        if self.blip_instance and BLIP_AVAILABLE:
            art = self.blip_instance.get_art(self.state)
            color = self.blip_instance.get_color(self.state)
            content = f"[{color}]{art}[/{color}]\n\n"
            if self.message:
                content += self.message
            self.update(content)
        else:
            self.update("Blip not available")


class AgentStatusTable(DataTable):
    """DataTable showing all agent statuses"""
    
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
        self.add_column("Agent", width=15)
        self.add_column("Status", width=10)
        self.add_column("Message", width=30)
        self.refresh_table()
    
    def refresh_table(self) -> None:
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
            
            self.add_row(
                f"{data['icon']} {agent_name}",
                status_text,
                data.get("message", "")
            )
    
    def update_agent(self, agent_name: str, status: str, message: str = "") -> None:
        if agent_name in self.agent_statuses:
            self.agent_statuses[agent_name]["status"] = status
            self.agent_statuses[agent_name]["message"] = message
            self.refresh_table()


class WorkingDirectoryDisplay(Static):
    """Display current working directory"""
    
    def __init__(self):
        super().__init__()
        self.current_dir = str(Path.cwd())
        self.border_title = "Location"
    
    def on_mount(self) -> None:
        self.update_content()
    
    def update_content(self) -> None:
        self.update(f"📁 [bold cyan]{self.current_dir}[/bold cyan]")
    
    def set_directory(self, directory: str) -> None:
        self.current_dir = directory
        self.update_content()


class FileViewer(Static):
    """File viewer component"""
    
    current_file = reactive[Optional[Path]](None)
    file_content = reactive("")
    
    def __init__(self):
        super().__init__()
        self.border_title = "File Viewer"
    
    def watch_current_file(self, old_file: Optional[Path], new_file: Optional[Path]) -> None:
        if new_file and new_file.exists():
            self.load_file(new_file)
            self.border_title = f"File Viewer: {new_file.name}"
        else:
            self.file_content = ""
            self.border_title = "File Viewer"
        self.update_content()
    
    def watch_file_content(self, old_content: str, new_content: str) -> None:
        self.update_content()
    
    def load_file(self, file_path: Path) -> None:
        try:
            with open(file_path, 'r') as f:
                self.file_content = f.read()
        except Exception as e:
            self.file_content = f"Error loading file: {e}"
    
    def update_content(self) -> None:
        if self.file_content:
            self.update(self.file_content[:10000])  # Limit display
        else:
            self.update("No file selected. Use the file browser to select a file.")


class ChatPanel(Vertical):
    """Interactive chat panel"""
    
    messages = reactive[List[Dict]]([])
    
    def __init__(self):
        super().__init__()
        self.border_title = "Chat"
    
    def compose(self) -> ComposeResult:
        yield RichLog(id="chat_log", wrap=True, highlight=True)
        yield Input(placeholder="Type your message here...", id="chat_input")
    
    def on_mount(self) -> None:
        self.chat_log = self.query_one("#chat_log", RichLog)
        self.add_message("system", "Welcome to Blonde CLI! Type your message or use Ctrl+P for commands.")
    
    def add_message(self, role: str, content: str) -> None:
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
        message = event.value.strip()
        if message:
            self.add_message("user", message)
            event.input.value = ""
            self.process_message(message)
    
    def process_message(self, message: str) -> None:
        """Process user message - this integrates with actual Blonde CLI"""
        # For now, simulate responses
        # In production, this would call actual LLM and agent systems
        if message.startswith("/"):
            self.add_message("system", f"Command: {message}")
        else:
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
        with Vertical():
            yield Input(placeholder="Search commands...", id="command_search")
            yield DataTable(id="command_table")
    
    def on_mount(self) -> None:
        self.search_input = self.query_one("#command_search", Input)
        self.command_table = self.query_one("#command_table", DataTable)
        
        self.command_table.add_column("Command", width=20)
        self.command_table.add_column("Description", width=50)
        self.refresh_commands()
    
    def refresh_commands(self) -> None:
        self.command_table.clear()
        for i, (cmd, desc) in enumerate(self.filtered_commands):
            row_key = self.command_table.add_row(f"/{cmd}", desc)
            if i == self.selected_index:
                self.command_table.cursor_type = "row"
                self.command_table.move_cursor(row=row_key)
    
    def action_move_up(self) -> None:
        if self.selected_index > 0:
            self.selected_index -= 1
            self.refresh_commands()
    
    def action_move_down(self) -> None:
        if self.selected_index < len(self.filtered_commands) - 1:
            self.selected_index += 1
            self.refresh_commands()
    
    def action_select_command(self) -> None:
        if self.filtered_commands:
            cmd, _ = self.filtered_commands[self.selected_index]
            self.dismiss(cmd)
    
    @on(Input.Changed, "#command_search")
    def on_search_changed(self, event: Input.Changed) -> None:
        query = event.value.lower()
        self.filtered_commands = [
            (cmd, desc) for cmd, desc in self.commands.items()
            if query in cmd.lower() or query in desc.lower()
        ]
        self.selected_index = 0
        self.refresh_commands()


class SettingsModal(ModalScreen[None]):
    """Settings modal with tabs"""
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
        ("ctrl+s", "save_settings", "Save"),
        ("ctrl+tab", "next_tab", "Next Tab")
    ]
    
    def __init__(self, config_path: Path):
        super().__init__()
        self.config_path = config_path
        self.config = self.load_config()
        self.current_tab = "providers"
    
    def load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            "version": "1.0.0",
            "default_provider": "openrouter",
            "providers": {},
            "preferences": {
                "privacy_mode": "balanced",
                "show_tips": True,
                "stream_responses": True,
                "show_blip": True
            }
        }
    
    def compose(self) -> ComposeResult:
        with Container(id="settings_container"):
            yield Tabs("Providers", "Privacy", "UI")
            with ContentSwitcher():
                with Vertical(id="providers_tab"):
                    yield Static("AI Providers Configuration")
                    yield DataTable(id="providers_table")
                    yield Button("Add Provider", id="add_provider_btn")
                with Vertical(id="privacy_tab"):
                    yield Static("Privacy Settings")
                    yield Static("Privacy mode configuration")
                with Vertical(id="ui_tab"):
                    yield Static("UI Preferences")
                    yield Static("Interface customization")
    
    def on_mount(self) -> None:
        self.tabs = self.query_one(Tabs)
        self.switcher = self.query_one(ContentSwitcher)
        self.action_next_tab()
    
    def action_next_tab(self) -> None:
        self.tabs.active = (self.tabs.active + 1) % len(self.tabs)
    
    def action_save_settings(self) -> None:
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.notify("Settings saved successfully!", severity="information")
        except Exception as e:
            self.notify(f"Error saving settings: {e}", severity="error")
    
    @on(Tabs.TabActivated)
    def on_tab_activated(self, event: Tabs.TabActivated) -> None:
        tab_names = ["providers", "privacy", "ui"]
        self.current_tab = tab_names[event.tab_index]
        self.switcher.current = f"{self.current_tab}_tab"


class ModernTUI(App):
    """Main Textual TUI application"""
    
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
        ("ctrl+a", "toggle_agents", "Show Agents"),
        ("f1", "show_help", "Help")
    ]
    
    def __init__(self):
        super().__init__()
        self.blip_instance = Blip() if BLIP_AVAILABLE else None
        self.config_path = CONFIG_FILE
        self.show_editor = True
        self.show_blip = True
        self.show_agents = True
        
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
            "help": "Show help",
            "exit": "Exit application"
        }
    
    def compose(self) -> ComposeResult:
        yield Header(id="header")
        
        with Container(id="sidebar"):
            yield WorkingDirectoryDisplay()
            if BLIP_AVAILABLE:
                yield BlipWidget(self.blip_instance)
            yield AgentStatusTable()
        
        with Container(id="main_content"):
            with Horizontal():
                yield DirectoryTree(str(Path.cwd()), id="file_browser")
                if self.show_editor:
                    yield FileViewer()
        
        with Container(id="chat_panel"):
            yield ChatPanel()
        
        yield Footer(id="footer")
    
    def on_mount(self) -> None:
        self.title = "Blonde CLI - Modern TUI"
        self.sub_title = "Multi-Agent AI Development Assistant"
        
        if BLIP_AVAILABLE and self.blip_instance:
            blip_widget = self.query_one(BlipWidget)
            if blip_widget:
                blip_widget.message = "Ready to help!"
                blip_widget.state = "happy"
    
    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        path = Path(event.path)
        file_viewer = self.query_one(FileViewer)
        if file_viewer:
            file_viewer.current_file = path
        
        if BLIP_AVAILABLE:
            blip_widget = self.query_one(BlipWidget)
            if blip_widget:
                blip_widget.message = f"Selected: {path.name}"
                blip_widget.state = "working"
    
    def action_show_command_palette(self) -> None:
        self.push_screen(CommandPalette(self.commands), self.handle_command)
    
    def handle_command(self, command: Optional[str]) -> None:
        if command:
            chat_panel = self.query_one(ChatPanel)
            if chat_panel:
                chat_panel.add_message("system", f"Executing: /{command}")
            
            if BLIP_AVAILABLE:
                blip_widget = self.query_one(BlipWidget)
                if blip_widget:
                    blip_widget.message = f"Running: {command}"
                    blip_widget.state = "working"
    
    def action_show_settings(self) -> None:
        self.push_screen(SettingsModal(self.config_path))
    
    def action_toggle_editor(self) -> None:
        self.show_editor = not self.show_editor
        file_viewer = self.query_one(FileViewer)
        if file_viewer:
            file_viewer.display = self.show_editor
        self.notify(f"Editor: {'Enabled' if self.show_editor else 'Disabled'}")
    
    def action_toggle_blip(self) -> None:
        self.show_blip = not self.show_blip
        blip_widget = self.query_one(BlipWidget)
        if blip_widget:
            blip_widget.display = self.show_blip
        self.notify(f"Blip: {'Enabled' if self.show_blip else 'Disabled'}")
    
    def action_toggle_agents(self) -> None:
        self.show_agents = not self.show_agents
        agent_table = self.query_one(AgentStatusTable)
        if agent_table:
            agent_table.display = self.show_agents
        self.notify(f"Agent Status: {'Enabled' if self.show_agents else 'Disabled'}")
    
    def action_show_help(self) -> None:
        help_text = """
        [bold cyan]Blonde CLI - Modern TUI Help[/bold cyan]
        
        [cyan]Keyboard Shortcuts:[/cyan]
        Ctrl+P - Command Palette
        Ctrl+S - Settings
        Ctrl+E - Toggle Editor
        Ctrl+B - Toggle Blip
        Ctrl+A - Toggle Agents
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
        """External API to update agent status"""
        agent_table = self.query_one(AgentStatusTable)
        if agent_table:
            agent_table.update_agent(agent_name, status, message)
        
        if BLIP_AVAILABLE:
            blip_widget = self.query_one(BlipWidget)
            if blip_widget:
                if status == "working":
                    blip_widget.state = "working"
                    blip_widget.message = f"{agent_name} is working..."
                elif status == "done":
                    blip_widget.state = "success"
                    blip_widget.message = f"{agent_name} completed!"
                elif status == "error":
                    blip_widget.state = "error"
                    blip_widget.message = f"{agent_name} encountered an error"
    
    def set_blip_message(self, message: str, state: str = "idle") -> None:
        """External API to set Blip message and state"""
        if BLIP_AVAILABLE:
            blip_widget = self.query_one(BlipWidget)
            if blip_widget:
                blip_widget.message = message
                blip_widget.state = state


def launch_modern_tui():
    """Launch the modern TUI application"""
    if not TEXTUAL_AVAILABLE:
        print("Error: Textual is not installed")
        print("Please install with: pip install textual>=0.44.0")
        sys.exit(1)
    
    try:
        app = ModernTUI()
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error launching TUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    launch_modern_tui()
