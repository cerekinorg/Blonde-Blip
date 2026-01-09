"""
Simple Dashboard - Proof of Concept
Minimal dashboard demonstrating new core systems integration
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static, Input
from textual import on
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import new core systems
from tui.core import (
    get_config_manager,
    get_session_manager,
    get_provider_manager,
    get_agent_team
)

from tui.blip_panel import BlipPanel
from tui.work_panel import WorkPanel
from tui.context_panel import ContextPanel


class SimpleDashboard(App):
    """Simple dashboard demonstrating new core systems"""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 1;
        grid-columns: 24 1fr 32;
        background: #0D1117;
    }

    Horizontal {
        height: 100%;
    }

    .panel {
        border: solid #30363D;
        background: #0D1117;
        padding: 1;
    }

    Button {
        margin: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self, session_id: str = None, first_prompt: str = ""):
        super().__init__()
        self.session_id = session_id
        self.first_prompt = first_prompt

        # Initialize new core systems
        self.config = get_config_manager()
        self.session_mgr = get_session_manager()
        self.provider_mgr = get_provider_manager()
        self.agent_team = get_agent_team()

        print(f"✅ Core systems initialized:")
        print(f"  - Config Manager: {type(self.config).__name__}")
        print(f"  - Session Manager: {type(self.session_mgr).__name__}")
        print(f"  - Provider Manager: {type(self.provider_mgr).__name__}")
        print(f"  - Agent Team: {type(self.agent_team).__name__}")

    def compose(self) -> ComposeResult:
        """Compose 3-column layout"""
        # Left panel - Blip
        with Vertical(id="left_panel"):
            yield Static("[bold cyan]🎨 Blip Panel[/bold cyan]", id="blip_panel")
            yield Static("Character: " + self.config.blip_character, id="blip_char")
            yield Static("Status: Ready", id="blip_status")

        # Center panel - Work
        with Vertical(id="center_panel"):
            yield Static("[bold yellow]💻 Work Panel[/bold yellow]")
            yield Input(placeholder="Type your message...", id="chat_input")
            yield Static("", id="chat_output")
            yield Static("Mode: Normal (Single Agent)", id="mode_display")

        # Right panel - Context
        with Vertical(id="right_panel"):
            yield Static("[bold green]📊 Context Panel[/bold green]")
            yield Static(f"Provider: {self.provider_mgr.current_provider()}", id="provider_display")
            yield Static(f"Model: {self.provider_mgr.current_model()}", id="model_display")
            yield Static(f"Session: {self.session_id[:8] if self.session_id else 'None'}", id="session_display")
            yield Static("Context: 0 tokens (0.0%)", id="context_display")
            yield Static("Cost: $0.0000", id="cost_display")

    def on_mount(self) -> None:
        """Initialize on mount"""
        self.title = "Blonde CLI v2.0 - Simple Dashboard"
        self.sub_title = "New Core Systems Integration"

        self.log("🚀 Dashboard mounted with new core systems!")
        self.log(f"✅ Session ID: {self.session_id}")
        self.log(f"✅ Provider: {self.provider_mgr.current_provider()}")
        self.log(f"✅ Model: {self.provider_mgr.current_model()}")
        self.log(f"✅ Agents Available: {', '.join(self.agent_team.get_agent_list())}")

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle chat input"""
        message = event.value
        if not message:
            return

        chat_output = self.query_one("#chat_output", Static)
        chat_output.update(f"👤 You: {message}")
        self.log(f"👤 You: {message}")

        # Process message
        if message.startswith("/"):
            self._handle_command(message)
        else:
            self._handle_chat(message)

        # Clear input
        chat_input = self.query_one("#chat_input", Input)
        chat_input.value = ""

    def _handle_chat(self, message: str) -> None:
        """Handle chat message with agent"""
        chat_output = self.query_one("#chat_output", Static)

        current_content = str(chat_output.content) if chat_output.content else ""
        chat_output.update(f"{current_content}\n🤖 Blonde: Thinking...")
        self.log("🤖 Agent processing...")

        # Get adapter and chat
        adapter = self.provider_mgr.get_adapter()
        try:
            response = adapter.chat(message)
            chat_output.update(f"{current_content}\n🤖 Blonde: {response[:200]}...")
            self.log(f"✅ Agent response received ({len(response)} chars)")

            # Save to session
            if self.session_mgr._current_session:
                self.session_mgr.add_message("user", message)
                self.session_mgr.add_message("assistant", response)
                self._update_context_display()

        except Exception as e:
            chat_output.update(f"{current_content}\n❌ Error: {e}")
            self.log(f"❌ Error: {e}")

    def _handle_command(self, command: str) -> None:
        """Handle commands"""
        self.log(f"🔧 Command: {command}")

        if command == "/mode":
            # Toggle mode
            mode = "Development (Multi-Agent)" if not hasattr(self, '_dev_mode') or not self._dev_mode else "Normal (Single Agent)"
            self._dev_mode = not hasattr(self, '_dev_mode') or not self._dev_mode
            mode_display = self.query_one("#mode_display", Static)
            mode_display.update(f"Mode: {mode}")
            self.log(f"✅ Switched to {mode}")

        elif command.startswith("/provider "):
            # Switch provider
            provider = command.split(" ", 1)[1]
            success = self.provider_mgr.switch_provider(provider)
            if success:
                provider_display = self.query_one("#provider_display", Static)
                provider_display.update(f"Provider: {provider}")
                self.log(f"✅ Switched to {provider}")
            else:
                self.log(f"❌ Failed to switch to {provider}")

        elif command == "/agents":
            # List agents
            agents = self.agent_team.get_agent_list()
            self.log(f"📋 Available Agents: {', '.join(agents)}")

        elif command.startswith("/gen "):
            # Generate code
            task = command.split(" ", 1)[1]
            chat_output = self.query_one("#chat_output", Static)
            chat_output.update(f"\n🧱 Generator Agent working...")
            self.log(f"🧱 Generator Agent: {task}")

            result = self.agent_team.execute_agent('generator', task)
            chat_output.update(f"{chat_output.renderable}\n✅ Code Generated:\n{result[:300]}...")
            self.log("✅ Code generation complete")

        elif command.startswith("/team "):
            # Multi-agent collaboration
            task = command.split(" ", 1)[1]
            chat_output = self.query_one("#chat_output", Static)
            chat_output.update(f"\n🤖 Multi-Agent Collaboration started...")
            self.log(f"🤖 Team Task: {task}")

            results = self.agent_team.collaborate(task, agents=['generator', 'reviewer'])
            for agent, result in results.items():
                chat_output.update(f"{chat_output.renderable}\n✅ {agent.capitalize()} complete")
                self.log(f"✅ {agent.capitalize()}: {len(result)} chars")

        else:
            self.log(f"❓ Unknown command: {command}")
            self.log("Available commands: /mode, /provider <name>, /agents, /gen <task>, /team <task>")

    def _update_context_display(self) -> None:
        """Update context usage display"""
        if self.session_mgr._current_session:
            tokens = self.session_mgr._current_session.context_usage.get('total_tokens', 0)
            percentage = self.session_mgr._current_session.context_usage.get('percentage', 0.0)
            context_display = self.query_one("#context_display", Static)
            context_display.update(f"Context: {tokens:,} tokens ({percentage:.1f}%)")
