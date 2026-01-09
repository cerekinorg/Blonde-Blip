"""
Blonde CLI - Chat Command
Interactive chat with AI using new core systems
"""

import typer
from rich.console import Console
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import new core systems
from tui.core import get_config_manager, get_session_manager, get_provider_manager

console = Console()


def chat_cmd(
    debug: bool = typer.Option(False, help="Enable debug logging"),
    stream: bool = typer.Option(True, help="Stream responses"),
):
    """Interactive chat with Blonde - Simplified version with new core systems"""
    console.print("[bold cyan]💬 Blonde CLI - Interactive Chat[/bold cyan]")
    console.print("[dim]Type your message or /help for commands[/dim]")
    console.print("[dim]Press Ctrl+C to exit[/dim]\n")

    # Initialize new core systems
    config = get_config_manager()
    provider_mgr = get_provider_manager()
    session_mgr = get_session_manager()

    console.print(f"[dim]Provider: {provider_mgr.current_provider()}[/dim]")
    console.print(f"[dim]Model: {provider_mgr.current_model()}[/dim]\n")

    # Create session
    session = session_mgr.create_session(
        provider=provider_mgr.current_provider(),
        model=provider_mgr.current_model()
    )
    console.print(f"[green]✓ Session: {session.session_id[:8]}...[/green]\n")

    # Get adapter
    adapter = provider_mgr.get_adapter()

    # Main chat loop
    while True:
        try:
            user_input = typer.prompt("[bold green]You[/bold green]", default="")

            if not user_input.strip():
                continue

            if user_input.lower() in ("exit", "quit", "q"):
                console.print("[bold red]Goodbye![/bold red]")
                break

            # Handle commands
            if user_input.startswith("/"):
                _handle_command(user_input, console, provider_mgr, session_mgr)
                continue

            # Chat with AI
            console.print(f"[bold magenta]Blonde:[/bold magenta] Thinking...")

            try:
                response = adapter.chat(user_input)
                console.print(f"[bold magenta]Blonde:[/bold magenta] {response}\n")

                # Save to session
                session_mgr.add_message("user", user_input)
                session_mgr.add_message("assistant", response)

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]\n")

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupted[/bold yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]\n")


def _handle_command(command: str, console: Console, provider_mgr, session_mgr):
    """Handle special commands"""

    if command == "/help":
        console.print("\n[bold cyan]Available Commands:[/bold cyan]")
        console.print("  /help    - Show this help")
        console.print("  /mode    - Toggle Normal/Development mode")
        console.print("  /agent   - Show current agent")
        console.print("  /provider <name> - Switch provider")
        console.print("  /model <name>   - Switch model")
        console.print("  /session new     - Create new session")
        console.print("  /sessions list    - List all sessions")
        console.print("  /exit, /quit, /q - Exit\n")

    elif command.startswith("/provider "):
        provider = command.split(" ", 1)[1].strip()
        success = provider_mgr.switch_provider(provider)
        if success:
            console.print(f"[green]✓ Switched to {provider}[/green]")
        else:
            console.print(f"[red]✗ Failed to switch to {provider}[/red]")

    elif command.startswith("/model "):
        model = command.split(" ", 1)[1].strip()
        provider_mgr.set_model(model)
        console.print(f"[green]✓ Model changed to {model}[/green]")

    elif command == "/session new":
        session = session_mgr.create_session()
        console.print(f"[green]✓ New session: {session.session_id[:8]}...[/green]")

    elif command == "/sessions list":
        sessions = session_mgr.list_sessions()
        console.print(f"\n[bold cyan]Sessions ({len(sessions)}):[/bold cyan]")
        for i, s in enumerate(sessions[:10], 1):
            console.print(f"  {i}. {s.name} - {s.created_at[:10]}")
        if len(sessions) > 10:
            console.print(f"  ... and {len(sessions) - 10} more")

    else:
        console.print(f"[yellow]Unknown command: {command}[/yellow]")
        console.print("Type /help for available commands\n")
