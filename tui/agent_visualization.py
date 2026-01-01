"""
Agent Visualization System

Shows all AI agents working together with real-time status updates
and explanations from Blip about what's happening.

Now includes the 9th agent: Optimizer (Master Agent)
"""

import time
import threading
from typing import List, Dict, Any, Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.text import Text
from rich.layout import Layout
from datetime import datetime

console = Console()


class Agent:
    """Represents a single AI agent"""

    def __init__(self, name: str, icon: str, color: str):
        self.name = name
        self.icon = icon
        self.color = color
        self.status = "waiting"  # waiting, working, done, error
        self.message = ""
        self.progress = 0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.result: Optional[Any] = None

    def set_status(self, status: str, message: str = ""):
        """Update agent status"""
        self.status = status
        self.message = message

        if status == "working":
            self.start_time = time.time()
        elif status in ["done", "error"]:
            self.end_time = time.time()

    def set_progress(self, progress: int, message: str = ""):
        """Update progress"""
        self.progress = min(100, max(0, progress))
        if message:
            self.message = message

    def get_duration(self) -> float:
        """Get task duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.time() - self.start_time
        return 0.0

    def render(self) -> Panel:
        """Render agent panel"""
        # Status colors
        status_colors = {
            "waiting": "dim",
            "working": "yellow",
            "done": "green",
            "error": "red"
        }

        status_style = status_colors.get(self.status, "white")
        status_text = self.status.upper()

        # Progress bar for working agents
        content = Text()
        content.append(f"{self.icon} ", style=self.color)
        content.append(f"{self.name}\n", style="bold white")

        # Status
        content.append("Status: ", style="dim")
        content.append(status_text, style=status_style)
        content.append("\n")

        # Progress
        if self.status == "working" and self.progress > 0:
            progress_bar = "█" * (self.progress // 10)
            remaining = "░" * (10 - (self.progress // 10))
            content.append(f"Progress: [{progress_bar}{remaining}] {self.progress}%\n", style="yellow")
        elif self.status == "done":
            content.append("✓ Completed\n", style="green")
        elif self.status == "error":
            content.append("✗ Failed\n", style="red")

        # Message
        if self.message:
            content.append(f"\n{self.message}", style="dim")

        # Duration
        duration = self.get_duration()
        if duration > 0:
            content.append(f"\n⏱ {duration:.1f}s", style="dim")

        panel = Panel(
            content,
            title=f"{self.icon} {self.name}",
            border_style=status_style,
            padding=(1, 1),
            width=35
        )

        return panel


class AgentCoordinator:
    """Coordinates multiple agents and visualizes their work"""

    def __init__(self):
        self.agents = {
            "generator": Agent("Generator", "🧱", "bright_magenta"),
            "reviewer": Agent("Reviewer", "🔍", "bright_blue"),
            "tester": Agent("Tester", "🧪", "bright_cyan"),
            "refactorer": Agent("Refactorer", "🔨", "bright_yellow"),
            "documenter": Agent("Documenter", "📝", "bright_green"),
            "architect": Agent("Architect", "🏗️", "bright_white"),
            "security": Agent("Security", "🔒", "bright_red"),
            "debugger": Agent("Debugger", "🐛", "orange1"),
            "optimizer": Agent("Optimizer", "⚡", "bright_white")  # 9th agent - MASTER
        }

        self.workflow: List[str] = []
        self.current_step = 0
        self.status = "idle"  # idle, running, paused, completed

        self.agent_icons = {
            "generator": "🧱",
            "reviewer": "🔍",
            "tester": "🧪",
            "refactorer": "🔨",
            "documenter": "📝",
            "architect": "🏗️",
            "security": "🔒",
            "debugger": "🐛",
            "optimizer": "⚡"
        }

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        return self.agents.get(name)

    def start_agent(self, name: str, message: str = ""):
        """Start an agent's work"""
        agent = self.get_agent(name)
        if agent:
            agent.set_status("working", message)
            console.print(f"[cyan]{agent.icon} {agent.name}: {message}[/cyan]")

    def complete_agent(self, name: str, message: str = ""):
        """Mark agent as done"""
        agent = self.get_agent(name)
        if agent:
            agent.set_status("done", message)
            console.print(f"[green]{agent.icon} {agent.name}: {message}[/green]")

    def fail_agent(self, name: str, message: str = ""):
        """Mark agent as failed"""
        agent = self.get_agent(name)
        if agent:
            agent.set_status("error", message)
            console.print(f"[red]{agent.icon} {agent.name}: {message}[/red]")

    def update_agent_progress(self, name: str, progress: int, message: str = ""):
        """Update agent's progress"""
        agent = self.get_agent(name)
        if agent:
            agent.set_progress(progress, message)
            console.print(f"[yellow]{agent.icon} {agent.name}: {progress}% {message}[/yellow]")

    def reset_all(self):
        """Reset all agents to waiting"""
        for agent in self.agents.values():
            agent.status = "waiting"
            agent.message = ""
            agent.progress = 0
            agent.start_time = None
            agent.end_time = None
            agent.result = None

        self.workflow = []
        self.current_step = 0
        self.status = "idle"
        console.print("[cyan]✓ All agents reset to waiting state[/cyan]")

    def set_workflow(self, workflow: List[str]):
        """Define workflow (order of agents to run)"""
        self.workflow = workflow
        self.current_step = 0

    def render_dashboard(self) -> Layout:
        """Render full agent visualization dashboard"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )

        # Header
        header_text = Text()
        header_text.append("🤖 ", style="bold cyan")
        header_text.append("Agent Team", style="bold cyan")
        header_text.append(" - ", style="dim")
        header_text.append(f"Status: {self.status.upper()}", style=self.status)

        layout["header"].update(Panel(
            header_text,
            border_style="cyan",
            padding=(0, 1)
        ))

        # Main content - Agents grid
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )

        # Left: 5 agents
        left_agents = list(self.agents.values())[:5]
        left_content = ""
        for agent in left_agents:
            left_content += str(agent.render()) + "\n"

        layout["main"]["left"].update(Panel(
            left_content,
            border_style="cyan"
        ))

        # Right: 4 agents (including Optimizer)
        right_agents = list(self.agents.values())[5:]
        right_content = ""
        for agent in right_agents:
            right_content += str(agent.render()) + "\n"

        layout["main"]["right"].update(Panel(
            right_content,
            border_style="cyan"
        ))

        # Footer
        footer_text = Text()
        if self.workflow:
            footer_text.append("Workflow: ", style="dim")
            for i, agent_name in enumerate(self.workflow):
                if i == self.current_step:
                    footer_text.append(f"{agent_name}", style="bold yellow")
                elif i < self.current_step:
                    footer_text.append(f"✓{agent_name}", style="green")
                else:
                    footer_text.append(agent_name, style="dim")

                if i < len(self.workflow) - 1:
                    footer_text.append(" → ", style="dim")

        layout["footer"].update(Panel(
            footer_text,
            border_style="cyan",
            padding=(0, 1)
        ))

        return layout

    def show_collaboration_view(self) -> Panel:
        """Show how agents are collaborating"""
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Icon", width=3)
        table.add_column("Agent", width=12)
        table.add_column("Status", width=10)
        table.add_column("Message", width=35)

        for agent in self.agents.values():
            status_colors = {
                "waiting": "dim",
                "working": "yellow",
                "done": "green",
                "error": "red"
            }

            status_style = status_colors.get(agent.status, "white")
            status_text = agent.status.upper()

            table.add_row(
                agent.icon,
                agent.name,
                Text(status_text, style=status_style),
                Text(agent.message or "", style="dim")
            )

        panel = Panel(
            table,
            title="🤖 Agent Team Status",
            border_style="cyan"
        )

        return panel

    def show_agent_count(self):
        """Display the total count of agents"""
        console.print(f"[cyan]📊 Total agents: {len(self.agents)}[/cyan]")
        console.print()

        for name, agent in self.agents.items():
            status_color = "green" if agent.status == "done" else "yellow" if agent.status == "working" else "red" if agent.status == "error" else "white"
            console.print(f"  [{agent.icon}] {agent.name}: [bold {status_color}]{agent.status}[/bold {status_color}]")


def demo_agent_workflow():
    """Demonstrate a complete agent workflow"""
    coordinator = AgentCoordinator()

    # Define workflow
    workflow = ["generator", "reviewer", "tester", "refactorer", "documenter"]
    coordinator.set_workflow(workflow)
    coordinator.status = "running"

    console.print("[cyan]Starting multi-agent collaboration workflow![/cyan]")
    console.print()

    # Generator agent
    coordinator.start_agent("generator", "Creating API endpoints")

    for progress in [10, 30, 50, 70, 90, 100]:
        coordinator.update_agent_progress("generator", progress, f"Generating API code... {progress}%")
        time.sleep(0.3)

    coordinator.complete_agent("generator", "Initial implementation complete")
    console.clear()
    console.print(coordinator.show_collaboration_view())
    time.sleep(1)

    # Reviewer agent
    coordinator.start_agent("reviewer", "Reviewing code for bugs and issues")

    for progress in [25, 50, 75, 100]:
        coordinator.update_agent_progress("reviewer", progress, f"Analyzing code... {progress}%")
        time.sleep(0.2)

    coordinator.complete_agent("reviewer", "Found 2 minor issues, 1 suggestion")
    console.clear()
    console.print(coordinator.show_collaboration_view())
    time.sleep(1)

    # Tester agent
    coordinator.start_agent("tester", "Generating comprehensive test suite")

    for progress in [20, 40, 60, 80, 100]:
        coordinator.update_agent_progress("tester", progress, f"Creating tests... {progress}%")
        time.sleep(0.2)

    coordinator.complete_agent("tester", "Generated 15 test cases")
    console.clear()
    console.print(coordinator.show_collaboration_view())
    time.sleep(1)

    # Refactorer agent
    coordinator.start_agent("refactorer", "Refactoring for better performance")

    for progress in [15, 30, 60, 100]:
        coordinator.update_agent_progress("refactorer", progress, f"Optimizing code... {progress}%")
        time.sleep(0.2)

    coordinator.complete_agent("refactorer", "Improved structure and performance")
    console.clear()
    console.print(coordinator.show_collaboration_view())
    time.sleep(1)

    # Documenter agent
    coordinator.start_agent("documenter", "Generating API documentation")

    for progress in [33, 66, 100]:
        coordinator.update_agent_progress("documenter", progress, f"Writing docs... {progress}%")
        time.sleep(0.2)

    coordinator.complete_agent("documenter", "Documentation complete")
    console.clear()
    console.print(coordinator.show_collaboration_view())

    # All done
    coordinator.status = "completed"
    console.clear()
    console.print(coordinator.show_collaboration_view())

    console.print("[green]✓ Multi-agent workflow complete![/green]")
    console.print()


if __name__ == "__main__":
    # Demo dashboard
    coordinator = AgentCoordinator()

    console.print("[cyan]=== Agent Visualization System Demo ===[/cyan]")
    console.print()

    # Show agent count
    coordinator.show_agent_count()

    # Run demo workflow
    demo_agent_workflow()
