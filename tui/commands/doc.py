"""
Blonde CLI - Doc Command
Generate documentation using new core systems
"""

import typer
from rich.console import Console
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tui.core import get_config_manager, get_session_manager, get_provider_manager, get_agent_team

console = Console()


def doc_cmd(
    code: str = typer.Argument(..., help="Code to document"),
    format: str = typer.Option("google", help="Documentation format (google, numpy)"),
    save: str = typer.Option(None, help="Save documentation to file"),
):
    """Generate documentation using Blonde documenter agent"""
    console.print("[bold cyan]📝 Documentation Generation[/bold cyan]\n")

    config = get_config_manager()
    provider_mgr = get_provider_manager()
    session_mgr = get_session_manager()
    agent_team = get_agent_team()

    console.print("[bold yellow]Generating documentation...[/bold yellow]")

    try:
        result = agent_team.execute_agent('documenter', f"Generate {format} style documentation for:\n\n{code}")

        console.print("[green]✓ Documentation generated successfully[/green]\n")
        console.print("[bold cyan]Generated Documentation:[/bold cyan]")
        console.print(result)

        if save:
            with open(save, 'w') as f:
                f.write(result)
            console.print(f"\n[green]✓ Saved to {save}[/green]")

        session_mgr.add_message("user", f"/doc {code[:50]}...")
        session_mgr.add_message("assistant", f"Documentation generated using documenter agent")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
