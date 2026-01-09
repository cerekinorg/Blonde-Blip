"""
Blonde CLI - Gen Command
Generate code using new core systems
"""

import typer
from rich.console import Console
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import new core systems
from tui.core import get_config_manager, get_session_manager, get_provider_manager, get_agent_team

console = Console()


def gen_cmd(
    task: str = typer.Argument(..., help="Task description for code generation"),
    agent: str = typer.Option("generator", help="Agent to use (generator, reviewer, tester)"),
    save: str = typer.Option(None, help="Save generated code to file"),
):
    """Generate code using Blonde agents"""
    console.print(f"[bold cyan]🧱 Code Generation[/bold cyan]")
    console.print(f"[dim]Task: {task[:100]}...[/dim]\n")

    # Initialize new core systems
    config = get_config_manager()
    provider_mgr = get_provider_manager()
    session_mgr = get_session_manager()
    agent_team = get_agent_team()

    console.print(f"[dim]Provider: {provider_mgr.current_provider()}[/dim]")
    console.print(f"[dim]Agent: {agent}[/dim]\n")

    # Execute agent
    console.print(f"[bold yellow]Generating code...[/bold yellow]")

    try:
        result = agent_team.execute_agent(agent, task)

        console.print(f"[green]✓ Code generated successfully[/green]\n")
        console.print(f"[bold cyan]Generated Code:[/bold cyan]")
        console.print(result)

        # Save to file if specified
        if save:
            with open(save, 'w') as f:
                f.write(result)
            console.print(f"\n[green]✓ Saved to {save}[/green]")

        # Save to session
        session_mgr.add_message("user", f"/gen {task}")
        session_mgr.add_message("assistant", f"Generated code using {agent} agent")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
