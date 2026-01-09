"""
Blonde CLI - Create Command
Create files/projects using new core systems
"""

import typer
from rich.console import Console
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tui.core import get_config_manager, get_session_manager, get_provider_manager, get_agent_team

console = Console()


def create_cmd(
    description: str = typer.Argument(..., help="Description of what to create"),
    type: str = typer.Option("file", help="Type to create (file, project, etc.)"),
    name: str = typer.Option(None, help="File/project name"),
    path: str = typer.Option(".", help="Path to create in"),
):
    """Create files/projects using Blonde generator agent"""
    console.print("[bold cyan]📁 Create[/bold cyan]")
    console.print(f"[dim]Type: {type}[/dim]")
    console.print(f"[dim]Description: {description[:100]}...[/dim]\n")

    config = get_config_manager()
    provider_mgr = get_provider_manager()
    session_mgr = get_session_manager()
    agent_team = get_agent_team()

    console.print("[bold yellow]Creating...[/bold yellow]")

    try:
        prompt = f"Create a {type} with the following description:\n\n{description}"
        if name:
            prompt += f"\n\nName: {name}"
        if path and path != ".":
            prompt += f"\n\nPath: {path}"

        result = agent_team.execute_agent('generator', prompt)

        console.print("[green]✓ Created successfully[/green]\n")
        console.print("[bold cyan]Generated Content:[/bold cyan]")
        console.print(result)

        # Save if it's a file
        if type == "file" and name:
            file_path = Path(path) / name
            with open(file_path, 'w') as f:
                f.write(result)
            console.print(f"\n[green]✓ Saved to {file_path}[/green]")

        session_mgr.add_message("user", f"/create {type} {name if name else ''}")
        session_mgr.add_message("assistant", f"Created {type} using generator agent")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
