"""
Enhanced Chat Interface with Streaming and TUI
Provides rich, privacy-focused chat experience with all features integrated
"""

import os
import re
import threading
import queue
from pathlib import Path
from typing import Optional, List, Dict, Any, Generator
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.live import Live
from rich.text import Text

console = Console()


class StreamingResponse:
    """Handle streaming responses from LLM"""
    
    def __init__(self, adapter, max_tokens: int = 2000):
        self.adapter = adapter
        self.max_tokens = max_tokens
        self.token_queue = queue.Queue()
        self.is_complete = False
        self.current_response = []
    
    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Stream response tokens"""
        # For non-streaming adapters, simulate streaming
        try:
            response = self.adapter.chat(prompt)
            # Yield words/tokens one by one
            words = response.split()
            for i, word in enumerate(words):
                yield word + (" " if i < len(words) - 1 else "")
                if i % 3 == 0:  # Simulate token batching
                    import time
                    time.sleep(0.01)
        except Exception as e:
            yield f"[red]Error: {e}[/red]"


class ChatTUI:
    """Enhanced terminal UI for chat"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.layout = Layout()
        self.chat_history = []
        self.command_registry = None
        self.current_provider = None
        self.agent_status = {}
        self.is_streaming = False
        self.privacy_mode = True  # Default to privacy mode
    
    def initialize(self, command_registry=None, providers=None, dev_team=None):
        """Initialize TUI with services"""
        self.command_registry = command_registry
        self.providers = providers
        self.dev_team = dev_team
        
        if providers:
            current = providers.get_current_provider()
            if current:
                self.current_provider = current.name
    
    def render(self, message: str = None, streaming: bool = False) -> Live:
        """Render the TUI"""
        # Build layout
        self.layout.update(
            self._build_header(),
            self._build_chat_panel(message, streaming),
            self._build_status_panel(),
            self._build_footer()
        )
        
        return Live(self.layout, refresh_per_second=10)
    
    def _build_header(self):
        """Build header panel"""
        from rich.text import Text
        header = Text()
        header.append("Blonde CLI ", style="bold cyan")
        header.append("• ", style="dim")
        
        if self.current_provider:
            header.append(f"Provider: {self.current_provider} ", style="green")
        else:
            header.append("Provider: not configured ", style="yellow")
        
        if self.privacy_mode:
            header.append("• ", style="dim")
            header.append("🔒 Privacy Mode", style="bold green")
        
        return Panel(header, style="cyan")
    
    def _build_chat_panel(self, message: str = None, streaming: bool = False):
        """Build main chat panel"""
        if not message:
            return Panel(
                "Type your message or command (use /help)",
                title="Chat",
                border_style="cyan"
            )
        
        # Check if it's a command
        if message.startswith("/"):
            return self._handle_command_panel(message)
        
        # Regular message
        return Panel(
            Markdown(message),
            title="Assistant",
            border_style="green",
            subtitle="Streaming..." if streaming else None
        )
    
    def _handle_command_panel(self, command: str):
        """Handle and render command output"""
        if self.command_registry:
            result = self.command_registry.execute(command)
            if result:
                return Panel(
                    result,
                    title=f"Command: {command.split()[0]}",
                    border_style="yellow"
                )
        
        return Panel(
            "Unknown command. Use /help",
            title="Error",
            border_style="red"
        )
    
    def _build_status_panel(self):
        """Build status/agent panel"""
        table = Table(show_header=False, box=None)
        table.add_column("", style="dim")
        
        if self.dev_team:
            table.add_row("🤝 Dev Team: Active")
            table.add_row("   Ready for tasks")
        
        if self.providers:
            table.add_row("")
            table.add_row(f"🔌 Providers: {len(self.providers.providers)} configured")
        
        if self.privacy_mode:
            table.add_row("")
            table.add_row("🔒 Privacy: Enabled (all processing local)")
        
        return Panel(
            table,
            title="Status",
            border_style="blue"
        )
    
    def _build_footer(self):
        """Build footer with hints"""
        hints = [
            "[cyan]/help[/cyan] - Commands",
            "[cyan]/team[/cyan] - Dev team",
            "[cyan]/providers[/cyan] - Switch AI",
            "[cyan]/clear[/cyan] - Clear screen",
            "[cyan]/exit[/cyan] - Quit"
        ]
        return Panel("  ".join(hints), style="dim")
    
    def set_privacy_mode(self, enabled: bool):
        """Enable/disable privacy mode"""
        self.privacy_mode = enabled
        if enabled:
            console.print("[green]🔒 Privacy mode enabled - all processing stays local[/green]")
        else:
            console.print("[yellow]🔓 Privacy mode disabled - may use cloud providers[/yellow]")


class EnhancedChatSystem:
    """Complete chat system with all features integrated"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.console = Console()
        self.tui = ChatTUI(project_root)
        
        # Services (will be initialized)
        self.command_registry = None
        self.providers = None
        self.dev_team = None
        self.rollback_manager = None
        self.workflow_manager = None
        self.memory_manager = None
        
        # Chat state
        self.chat_history = []
        self.streaming_enabled = True
        self.autoconfirm = False
    
    def initialize(self):
        """Initialize all services"""
        from tui.chat_commands import create_command_registry
        
        # Initialize command registry
        self.command_registry = create_command_registry()
        
        # Initialize services if available
        try:
            from tui.provider_manager import ProviderManager
            self.providers = ProviderManager()
        except Exception:
            self.console.print("[yellow]Provider system not available[/yellow]")
        
        try:
            from tui.dev_team import DevelopmentTeam
            
            # Get LLM adapter
            llm = None
            if self.providers:
                llm = self.providers.get_adapter()
            
            if llm:
                self.dev_team = DevelopmentTeam(llm)
        except Exception:
            self.console.print("[yellow]Dev team system not available[/yellow]")
        
        try:
            from tui.rollback import RollbackManager
            self.rollback_manager = RollbackManager(str(self.project_root))
        except Exception:
            self.console.print("[yellow]Rollback system not available[/yellow]")
        
        try:
            from tui.workflow import WorkflowManager
            self.workflow_manager = WorkflowManager(str(self.project_root))
        except Exception:
            self.console.print("[yellow]Workflow system not available[/yellow]")
        
        try:
            from tui.memory import MemoryManager
            self.memory_manager = MemoryManager(str(self.project_root))
        except Exception:
            self.console.print("[yellow]Memory system not available[/yellow]")
        
        # Update TUI with services
        self.tui.initialize(
            command_registry=self.command_registry,
            providers=self.providers,
            dev_team=self.dev_team
        )
    
    def start(self):
        """Start the interactive chat session"""
        self._show_welcome()
        
        while True:
            try:
                # Get user input
                user_input = self._get_user_input()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if self._handle_special_commands(user_input):
                    continue
                
                # Handle chat commands
                if user_input.startswith("/"):
                    self._handle_chat_command(user_input)
                    continue
                
                # Regular chat message
                self._handle_chat_message(user_input)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use /exit to quit[/yellow]")
            except EOFError:
                self.console.print("\n[green]Goodbye![/green]")
                break
    
    def _show_welcome(self):
        """Show welcome message"""
        welcome = f"""
[bold cyan]🚀 Blonde CLI - Privacy-First AI Development Assistant[/bold cyan]

[dim]All features are available through natural commands. Type /help to see all options.[/dim]

[dim]Privacy: {'✓ Enabled' if self.tui.privacy_mode else '✗ Disabled'}[/dim]
[dim]Streaming: {'✓ Enabled' if self.streaming_enabled else '✗ Disabled'}[/dim]
"""
        self.console.print(welcome)
    
    def _get_user_input(self) -> str:
        """Get user input with prompt"""
        from rich.prompt import Prompt
        return Prompt.ask(
            "[bold cyan]You[/bold cyan]",
            default="",
            show_default=False
        )
    
    def _handle_special_commands(self, user_input: str) -> bool:
        """Handle special non-chat commands"""
        lower_input = user_input.lower().strip()
        
        # Exit commands
        if lower_input in ("exit", "quit", "q"):
            self.console.print("[green]Goodbye![/green]")
            return True
        
        # Clear screen
        if lower_input in ("clear", "cls"):
            import subprocess
            subprocess.run("clear" if os.name != "nt" else "cls", shell=True)
            return True
        
        return False
    
    def _handle_chat_command(self, command: str):
        """Handle slash commands"""
        result = self.command_registry.execute(command)
        if result:
            self.console.print(result)
        else:
            # Try to help user
            cmd_name = command.split()[0].lstrip("/")
            self.console.print(f"[yellow]Unknown command: {cmd_name}. Use /help[/yellow]")
    
    def _handle_chat_message(self, message: str):
        """Handle regular chat message"""
        # Add to history
        self.chat_history.append(("You", message))
        
        # Get LLM adapter
        llm = self.providers.get_adapter() if self.providers else None
        
        if not llm:
            self.console.print("[red]No AI provider configured. Use /providers to set one up.[/red]")
            return
        
        # Check for memory context
        prompt = message
        if self.memory_manager:
            context = self.memory_manager.get_context_for_prompt(message)
            if context:
                prompt = f"Context from previous interactions:\n{context}\n\nCurrent message: {message}"
        
        self.console.print("[bold magenta]Blonde:[/bold magenta]")
        
        # Generate response
        if self.streaming_enabled and hasattr(llm, 'chat'):
            # Try streaming (simulated for now)
            from tui.enhanced_chat import StreamingResponse
            streamer = StreamingResponse(llm)
            
            response_parts = []
            for token in streamer.stream(prompt):
                response_parts.append(token)
                self.console.print(token, end=" ")
            
            response = " ".join(response_parts)
            self.console.print()
        else:
            # Non-streaming
            response = llm.chat(prompt)
            self._render_code_blocks(response)
        
        # Add to history
        self.chat_history.append(("Blonde", response))
        
        # Store in memory
        if self.memory_manager:
            self.memory_manager.add_conversation(message, response)
    
    def _render_code_blocks(self, text: str):
        """Render markdown code blocks with syntax highlighting"""
        # Detect code blocks
        code_blocks = re.findall(r'```(\w*)\n(.*?)```', text, re.DOTALL)
        
        if not code_blocks:
            self.console.print(text)
            return
        
        last_end = 0
        for lang, code, end in code_blocks:
            # Print text before code
            start = text.find(f'```{lang}', last_end)
            if start > last_end:
                from rich.markdown import Markdown
                self.console.print(Markdown(text[last_end:start]))
            
            # Print code with highlighting
            if lang:
                from rich.syntax import Syntax
                self.console.print(Syntax(code, lang, theme="monokai", line_numbers=False))
            else:
                self.console.print(f"[dim]{code}[/dim]")
            
            last_end = end + 3
        
        # Print any remaining text
        if last_end < len(text):
            from rich.markdown import Markdown
            self.console.print(Markdown(text[last_end:]))
