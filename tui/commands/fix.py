"""
Blonde CLI - Fix Command
Fix code using new core systems
"""

import typer
from rich.console import Console
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tui.core import get_config_manager, get_session_manager, get_provider_manager, get_agent_team

console = Console()


def fix_cmd(
    code: str = typer.Argument(..., help="Code to fix"),
    file: str = typer.Option(None, help="File to fix"),
    save: str = typer.Option(None, help="Save fixed code to file"),
):
    """Fix code using Blonde reviewer agent"""
    console.print("[bold cyan]🔧 Code Fix[/bold cyan]\n")

    config = get_config_manager()
    provider_mgr = get_provider_manager()
    session_mgr = get_session_manager()
    agent_team = get_agent_team()

    # If file provided, read from file
    if file:
        try:
            with open(file, 'r') as f:
                code = f.read()
            console.print(f"[dim]Read code from {file}[/dim]\n")
        except Exception as e:
            console.print(f"[red]✗ Failed to read file: {e}[/red]")
            return

    console.print("[bold yellow]Analyzing and fixing code...[/bold yellow]")

    try:
        result = agent_team.execute_agent('reviewer', f"Review and fix this code:\n\n{code}")

        console.print("[green]✓ Code fixed successfully[/green]\n")
        console.print("[bold cyan]Fixed Code:[/bold cyan]")
        console.print(result)

        if save:
            with open(save, 'w') as f:
                f.write(result)
            console.print(f"\n[green]✓ Saved to {save}[/green]")

        session_mgr.add_message("user", f"/fix {file if file else 'code block'}")
        session_mgr.add_message("assistant", f"Fixed code using reviewer agent")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
