"""
Simple Welcome Screen - Proof of Concept
Minimal welcome screen demonstrating new core systems integration
"""

from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Horizontal, Container
from textual import on
from pathlib import Path
import json
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import new core systems
from tui.core import (
    get_config_manager,
    get_session_manager,
    get_provider_manager
)

CONFIG_DIR = Path.home() / ".blonde"
CONFIG_FILE = CONFIG_DIR / "config.json"


class SimpleWelcomeScreen(App):
    """Simple welcome screen demonstrating new core systems"""

    CSS = """
    Screen {
        align: center middle;
        background: #0b0b0b;
    }

    #root {
        width: 100%;
        height: 100%;
    }

    #center_stack {
        align: center middle;
        max-width: 80;
    }

    #logo {
        text-align: center;
        margin-bottom: 2;
    }

    #input_card {
        border: solid #30363D;
        background: #0D1117;
        padding: 2;
        border-subtle: round;
    }

    #input_input {
        width: 1fr;
    }

    Button {
        width: 1fr;
        margin: 1 0 0 0;
    }

    #info_text {
        text-align: center;
        margin-top: 2;
    }
    """

    BINDINGS = [
        ("enter", "start_session", "Start Session"),
        ("escape", "app.quit", "Quit")
    ]

    def __init__(self, on_start: callable = None):
        super().__init__()
        self.on_start_callback = on_start

        # Initialize new core systems
        self.config = get_config_manager()
        self.session_mgr = get_session_manager()
        self.provider_mgr = get_provider_manager()

        print(f"✅ Core systems initialized in Welcome Screen:")
        print(f"  - Config Manager: {type(self.config).__name__}")
        print(f"  - Session Manager: {type(self.session_mgr).__name__}")
        print(f"  - Provider Manager: {type(self.provider_mgr).__name__}")

    def compose(self) -> ComposeResult:
        """Compose welcome screen"""
        with Container(id="root"):
            with Container(id="center_stack"):
                # Logo
                with Vertical(id="logo"):
                    yield Static(
                        r"""
        ╔══════════════════════════════════════════════════════╗
        ║                                                            ║
        ║         🎨  B L O N D E   C L I   v 2 . 0              ║
        ║                                                            ║
        ║         Privacy-First Multi-Agent AI Development Platform        ║
        ║                                                            ║
        ╚══════════════════════════════════════════════════════╝
                        """,
                        id="brand_logo"
                    )

                # Input card
                with Container(id="input_card"):
                    yield Static("Type your message to start:", id="label")
                    with Horizontal():
                        yield Input(
                            placeholder='Ask anything... "What can you help me with?"',
                            id="input_input",
                        )
                        yield Button("Start", id="start_button", variant="primary")

                # Info text
                with Vertical(id="info_text"):
                    provider = self.provider_mgr.current_provider()
                    model = self.provider_mgr.current_model()

                    yield Static(f"[bold cyan]Provider:[/bold cyan] {provider}")
                    yield Static(f"[bold cyan]Model:[/bold cyan] {model}")
                    yield Static(f"[bold cyan]Blip:[/bold cyan] {self.config.blip_character}")
                    yield Static("")
                    yield Static("[dim]Press Enter to start or Escape to quit[/dim]")

    def on_mount(self) -> None:
        """Initialize on mount"""
        self.title = "Blonde CLI v2.0 - Welcome"
        self.sub_title = "Simplified AI Development Platform"

        self.log("🚀 Simple Welcome Screen mounted with new core systems!")
        self.log(f"✅ Provider: {self.provider_mgr.current_provider()}")
        self.log(f"✅ Model: {self.provider_mgr.current_model()}")

    @on(Button.Pressed, "#start_button")
    def on_start_button_pressed(self) -> None:
        """Handle start button press"""
        self._start_session()

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission"""
        self._start_session(event.value)

    def _start_session(self, prompt: str = None) -> None:
        """Start session with given prompt"""
        input_widget = self.query_one("#input_input", Input)

        if not prompt:
            prompt = input_widget.value

        if not prompt:
            self.log("⚠️  No prompt provided")
            return

        self.log(f"👤 User: {prompt}")

        # Create new session
        session = self.session_mgr.create_session(
            provider=self.provider_mgr.current_provider(),
            model=self.provider_mgr.current_model()
        )

        self.log(f"✅ Session created: {session.session_id[:8]}...")

        # Save initial prompt to session
        self.session_mgr.add_message("user", prompt)

        self.log(f"✅ Message saved to session")

        # Return session data
        result = {
            'session_id': session.session_id,
            'first_prompt': prompt,
            'provider': self.provider_mgr.current_provider(),
            'model': self.provider_mgr.current_model()
        }

        # Call callback if provided
        if self.on_start_callback:
            self.on_start_callback(result)

        # Exit app
        self.exit(result)
