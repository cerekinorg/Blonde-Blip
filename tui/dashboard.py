"""
Enhanced UI Dashboard for Blonde CLI

A comprehensive TUI dashboard with:
- File browser
- Agent visualization
- Command palette
- Blip mascot integration
- Interactive controls
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.live import Live
from rich.columns import Columns
from rich.padding import Padding
from datetime import datetime

from tui.blip import blip

console = Console()


class FileBrowser:
    """File browser component"""

    def __init__(self, start_path: Optional[str] = None):
        self.current_path = Path(start_path or os.getcwd())
        self.selected_index = 0
        self.show_hidden = False

    def get_files(self) -> List[Dict[str, Any]]:
        """Get list of files and directories"""
        items = []

        # Add parent directory if not at root
        if self.current_path.parent != self.current_path:
            items.append({
                "name": "..",
                "path": self.current_path.parent,
                "is_dir": True,
                "size": "",
                "modified": ""
            })

        # Get all items
        for item in sorted(self.current_path.iterdir()):
            if not self.show_hidden and item.name.startswith("."):
                continue

            try:
                stat = item.stat()
                is_dir = item.is_dir()
                size = f"{stat.st_size / 1024:.1f}KB" if not is_dir else ""
                modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")

                items.append({
                    "name": item.name,
                    "path": item,
                    "is_dir": is_dir,
                    "size": size,
                    "modified": modified
                })
            except (OSError, PermissionError):
                continue

        return items

    def navigate_up(self):
        """Go to parent directory"""
        if self.current_path.parent != self.current_path:
            self.current_path = self.current_path.parent
            self.selected_index = 0

    def navigate_to_selected(self):
        """Navigate to currently selected item"""
        items = self.get_files()
        if 0 <= self.selected_index < len(items):
            item = items[self.selected_index]
            if item["is_dir"]:
                self.current_path = item["path"]
                self.selected_index = 0

    def render(self) -> Panel:
        """Render file browser panel"""
        items = self.get_files()

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("", width=2)
        table.add_column("Name", width=30)
        table.add_column("Size", width=10)
        table.add_column("Modified", width=16)

        for i, item in enumerate(items):
            icon = "📁" if item["is_dir"] else "📄"
            marker = "→ " if i == self.selected_index else "  "
            style = "bold yellow" if i == self.selected_index else "white"

            table.add_row(
                Text(f"{marker}{icon}", style=style),
                Text(item["name"], style=style),
                Text(item["size"], style="dim"),
                Text(item["modified"], style="dim")
            )

        panel = Panel(
            table,
            title=f"📂 File Browser - {self.current_path}",
            border_style="cyan"
        )

        return panel


class AgentStatusPanel:
    """Panel showing agent status"""

    def __init__(self):
        self.agents = [
            {"name": "Generator", "status": "waiting", "message": ""},
            {"name": "Reviewer", "status": "waiting", "message": ""},
            {"name": "Tester", "status": "waiting", "message": ""},
            {"name": "Refactorer", "status": "waiting", "message": ""},
            {"name": "Documenter", "status": "waiting", "message": ""},
            {"name": "Architect", "status": "waiting", "message": ""},
            {"name": "Security", "status": "waiting", "message": ""},
            {"name": "Debugger", "status": "waiting", "message": ""}
        ]

        self.agent_icons = {
            "Generator": "🧱",
            "Reviewer": "🔍",
            "Tester": "🧪",
            "Refactorer": "🔨",
            "Documenter": "📝",
            "Architect": "🏗️",
            "Security": "🔒",
            "Debugger": "🐛"
        }

    def update_agent(self, name: str, status: str, message: str = ""):
        """Update agent status"""
        for agent in self.agents:
            if agent["name"] == name:
                agent["status"] = status
                agent["message"] = message
                break

    def reset_all(self):
        """Reset all agents to waiting"""
        for agent in self.agents:
            agent["status"] = "waiting"
            agent["message"] = ""

    def render(self) -> Panel:
        """Render agent status panel"""
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("", width=3)
        table.add_column("Agent", width=12)
        table.add_column("Status", width=10)
        table.add_column("Message", width=30)

        for agent in self.agents:
            icon = self.agent_icons.get(agent["name"], "🤖")
            status = agent["status"]

            status_colors = {
                "working": "yellow",
                "done": "green",
                "error": "red",
                "waiting": "dim"
            }

            status_style = status_colors.get(status, "white")
            status_text = status.upper()

            table.add_row(
                icon,
                agent["name"],
                Text(status_text, style=status_style),
                Text(agent["message"], style="dim")
            )

        panel = Panel(
            table,
            title="🤖 Agent Team Status",
            border_style="cyan"
        )

        return panel


class CommandPalette:
    """Interactive command palette"""

    def __init__(self):
        self.commands = {
            "Chat": "💬 Start AI chat session",
            "Generate": "📝 Generate code from prompt",
            "Fix": "🐛 Fix bugs in code",
            "Test": "🧪 Generate tests",
            "Analyze": "🔍 Analyze code",
            "Refactor": "🔨 Refactor code",
            "Document": "📚 Generate documentation",
            "Settings": "⚙️ Configure settings",
            "Tutorial": "🎓 Start tutorial",
            "Help": "❓ Show help"
        }

        self.selected_index = 0
        self.keys = list(self.commands.keys())

    def get_selected(self) -> tuple:
        """Get selected command"""
        return (self.keys[self.selected_index], self.commands[self.keys[self.selected_index]])

    def navigate_up(self):
        """Navigate up in command list"""
        self.selected_index = max(0, self.selected_index - 1)

    def navigate_down(self):
        """Navigate down in command list"""
        self.selected_index = min(len(self.keys) - 1, self.selected_index + 1)

    def render(self) -> Panel:
        """Render command palette panel"""
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("", width=3)
        table.add_column("Command", width=15)
        table.add_column("Description", width=35)

        for i, key in enumerate(self.keys):
            marker = "→ " if i == self.selected_index else "  "
            style = "bold yellow" if i == self.selected_index else "white"
            description = self.commands[key]

            table.add_row(
                Text(marker, style=style),
                Text(key, style=style),
                Text(description, style="dim")
            )

        panel = Panel(
            table,
            title="⚡ Quick Actions",
            border_style="cyan"
        )

        return panel


class Dashboard:
    """Main dashboard UI"""

    def __init__(self, start_path: Optional[str] = None):
        self.file_browser = FileBrowser(start_path)
        self.agent_panel = AgentStatusPanel()
        self.command_palette = CommandPalette()
        self.current_mode = "menu"  # menu, chat, work

    def render(self) -> Layout:
        """Render full dashboard layout"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )

        # Header
        header_text = Text()
        header_text.append("Blonde CLI ", style="bold cyan")
        header_text.append("v1.0.0", style="dim")
        header_text.append(" - Privacy-First Multi-Agent AI Development Assistant", style="white")

        layout["header"].update(Panel(
            header_text,
            border_style="cyan",
            padding=(0, 1)
        ))

        # Main content
        if self.current_mode == "menu":
            layout["main"].split_row(
                Layout(name="left"),
                Layout(name="right")
            )

            # Left: File browser + Commands
            layout["left"].split_column(
                Layout(name="files", ratio=2),
                Layout(name="commands", ratio=1)
            )

            layout["left"]["files"].update(self.file_browser.render())
            layout["left"]["commands"].update(self.command_palette.render())

            # Right: Agent status + Blip
            layout["right"].split_column(
                Layout(name="agents"),
                Layout(name="blip")
            )

            layout["right"]["agents"].update(self.agent_panel.render())
            layout["right"]["blip"].update(Panel(
                Text("Blip says: 'Hi! How can I help you today?'"),
                title="💬 Blip",
                border_style="cyan"
            ))

        # Footer
        footer_text = Text()
        footer_text.append("Use ", style="dim")
        footer_text.append("↑↓ ", style="bold cyan")
        footer_text.append("to navigate, ", style="dim")
        footer_text.append("Enter ", style="bold cyan")
        footer_text.append("to select, ", style="dim")
        footer_text.append("q ", style="bold cyan")
        footer_text.append("to quit", style="dim")

        layout["footer"].update(Panel(
            footer_text,
            border_style="cyan",
            padding=(0, 1)
        ))

        return layout

    def handle_input(self, key: str) -> bool:
        """Handle keyboard input. Returns False to exit."""
        if key.lower() == "q":
            return False

        if self.current_mode == "menu":
            # File browser navigation
            if key == "up":
                self.file_browser.selected_index = max(0, self.file_browser.selected_index - 1)
            elif key == "down":
                items = self.file_browser.get_files()
                self.file_browser.selected_index = min(len(items) - 1, self.file_browser.selected_index + 1)
            elif key == "left":
                # Switch to command palette
                pass  # Tab switching would be better
            elif key == "enter":
                self.file_browser.navigate_to_selected()

        return True

    def run(self):
        """Run the dashboard"""
        blip.introduce()

        with Live(self.render(), refresh_per_second=30) as live:
            while True:
                # In a real implementation, we'd get key input here
                # For now, just show the dashboard
                import time
                time.sleep(0.1)

                # Demo: Simulate some agent activity
                import random
                if random.random() < 0.02:  # 2% chance per frame
                    agent = random.choice(self.agent_panel.agents)
                    statuses = ["working", "done", "waiting"]
                    agent["status"] = random.choice(statuses)
                    live.update(self.render())


def show_welcome():
    """Show welcome screen"""
    welcome_text = """
╔════════════════════════════════════════════════════════════╗
║                                                              ║
║   [bold cyan]Welcome to Blonde CLI![/bold cyan]                             ║
║                                                              ║
║   Your privacy-first multi-agent AI development assistant     ║
║                                                              ║
║   🧱 7 AI Agents collaborate to build better code           ║
║   🔒 Local-first approach with privacy controls            ║
║   🚀 Powered by OpenRouter, OpenAI, Anthropic, and local  ║
║                                                              ║
╚════════════════════════════════════════════════════════════╝
    """

    console.print(welcome_text)


def show_quick_actions():
    """Show quick actions menu"""
    actions = [
        ("💬", "Start Chat", "Begin interactive AI chat session"),
        ("📝", "Generate Code", "Generate code from natural language"),
        ("🐛", "Fix Bugs", "AI-powered bug fixing"),
        ("🧪", "Generate Tests", "Create comprehensive test suites"),
        ("🔍", "Analyze Code", "Analyze code structure and quality"),
        ("🔨", "Refactor", "Improve code quality and structure"),
        ("⚙️", "Settings", "Configure providers and preferences"),
        ("🎓", "Tutorial", "Learn how to use Blonde CLI"),
        ("❓", "Help", "Get help and documentation")
    ]

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Icon", width=3)
    table.add_column("Action", width=15)
    table.add_column("Description", width=40)

    for icon, action, description in actions:
        table.add_row(icon, action, description)

    console.print(table)


def start_dashboard(start_path: Optional[str] = None):
    """Start the interactive dashboard"""
    show_welcome()
    console.print()

    # Check if setup is needed
    from pathlib import Path
    config_path = Path.home() / ".blonde" / "config.json"

    if not config_path.exists():
        console.print("[yellow]⚠️  Setup needed! Running configuration wizard...[/yellow]")
        from tui.setup_wizard import SetupWizard
        wizard = SetupWizard()
        wizard.run()

    console.print()
    show_quick_actions()
    console.print()

    choice = Prompt.ask(
        "What would you like to do?",
        choices=["chat", "generate", "fix", "test", "analyze", "settings", "help"],
        default="chat"
    )

    return choice


if __name__ == "__main__":
    # Demo dashboard
    dashboard = Dashboard()
    dashboard.run()
