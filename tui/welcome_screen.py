"""
Welcome Screen - Initial landing screen for Blonde CLI
Provides app name, chat input, and model/provider selection
"""

from textual.app import App, ComposeResult
from textual.widgets import (
    Static, Input, Button, Select, Label,
    ContentSwitcher, RadioSet, RadioButton
)
from textual.containers import Vertical, Horizontal, Container
from textual.screen import ModalScreen
from textual import on
from textual.reactive import reactive
from pathlib import Path
import json
from typing import Optional, List

try:
    from .blip_manager import get_blip_manager
    from .session_manager import get_session_manager
    from .provider_manager import ProviderManager
    from .enhanced_settings import EnhancedSettings
    MANAGERS_AVAILABLE = True
except ImportError:
    try:
        from blip_manager import get_blip_manager
        from session_manager import get_session_manager
        from provider_manager import ProviderManager
        from enhanced_settings import EnhancedSettings
        MANAGERS_AVAILABLE = True
    except ImportError:
        MANAGERS_AVAILABLE = False

CONFIG_DIR = Path.home() / ".blonde"
CONFIG_FILE = CONFIG_DIR / "config.json"


class WelcomeScreen(App):
    """Welcome screen with chat input and model selection"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 1 2;
        grid-rows: 1fr 3;
    }
    
    #header_container {
        height: 8;
        border: solid $primary;
        background: $panel;
    }
    
    #content_container {
        border: solid $primary;
        background: $surface;
    }
    
    BlipDisplay {
        height: 100%;
        margin: 1;
    }
    
    #app_title {
        text-align: center;
        padding: 1;
        text-style: bold;
    }
    
    #app_subtitle {
        text-align: center;
        text-style: dim;
        padding: 1;
    }
    
    #input_container {
        padding: 2;
    }
    
    #chat_input {
        margin-top: 1;
    }
    
    #model_container {
        padding: 1;
    }
    
    #selection_row {
        height: 3;
    }
    
    Button {
        width: 20;
        margin: 1;
    }
    
    #start_button {
        margin-top: 2;
        width: 30;
    }
    
    .info_text {
        text-style: dim;
        padding: 1;
    }
    """
    
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+s", "show_settings", "Settings"),
        ("enter", "start_session", "Start Session"),
        ("escape", "quit", "Quit")
    ]
    
    def __init__(self, on_start: Optional[callable] = None):
        super().__init__()
        self.on_start_callback = on_start
        self.session_started = reactive(False)
        self.current_provider = "openrouter"
        self.current_model = "openai/gpt-4"
        self.custom_model = ""
        self.first_prompt = ""
        
        # Load managers
        if MANAGERS_AVAILABLE:
            self.blip_manager = get_blip_manager()
            self.session_manager = get_session_manager()
            self.provider_manager = ProviderManager()
        
        # Load config
        self._load_config()
    
    def _load_config(self):
        """Load current provider and model from config"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                
                self.current_provider = config.get('default_provider', 'openrouter')
                providers_config = config.get('providers', {})
                provider_data = providers_config.get(self.current_provider, {})
                self.current_model = provider_data.get('model', 'openai/gpt-4')
            except Exception:
                pass
    
    def compose(self) -> ComposeResult:
        """Compose the welcome screen"""
        with Container(id="header_container"):
            yield Static(
                "[bold cyan]╔═════════════════════════════════════════════╗[/bold cyan]",
                id="top_border"
            )
            yield Static("[bold cyan]║           Blonde CLI - AI Assistant              ║[/bold cyan]", id="app_title")
            yield Static("[bold cyan]╚═════════════════════════════════════════════╝[/bold cyan]", id="bottom_border")
        
        with Container(id="content_container"):
            with Horizontal(id="selection_row"):
                # Left side: Model/Provider selection
                with Vertical(id="model_container"):
                    yield Static("[bold]AI Provider:[/bold]", id="provider_label")
                    provider_options = [
                        ("OpenRouter", "openrouter"),
                        ("OpenAI", "openai"),
                        ("Anthropic", "anthropic"),
                        ("Local (GGUF)", "local")
                    ]
                    yield Select(
                        values=[opt for opt in provider_options],
                        id="provider_select"
                    )
                    
                    yield Static("[bold]Model:[/bold]", id="model_label")
                    model_options = self._get_model_options(self.current_provider)
                    yield Select(
                        values=[opt for opt in model_options],
                        id="model_select"
                    )
                    
                    yield Static("[bold dim]Or enter custom model:[/bold dim]", id="custom_label")
                    yield Input(
                        placeholder="e.g., meta-llama/llama-3-70b",
                        id="custom_model_input"
                    )
            
            # Right side: Blip display
            with Vertical(id="blip_container"):
                if MANAGERS_AVAILABLE:
                    character_name = self.blip_manager.current_character_name
                    character_info = self.blip_manager.get_character_info()
                    yield Static(
                        f"[bold]Blip - {character_name.title()}[/bold]\n{character_info.get('description', '')}",
                        id="blip_info"
                    )
                    art = self.blip_manager.get_art("happy")
                    color = self.blip_manager.get_color("happy")
                    yield Static(f"[{color}]{art}[/{color}]", id="blip_display")
            
            # Bottom: Chat input
            with Vertical(id="input_container"):
                yield Static("[bold]Start a new session:[/bold]", id="input_label")
                yield Input(
                    placeholder="Type your first message here, or press Enter to start...",
                    id="chat_input"
                )
                yield Static(
                    "[dim]💡 Tip: You can change model/provider and other settings anytime with Ctrl+S[/dim]",
                    id="tip_text",
                    classes="info_text"
                )
                
                with Horizontal():
                    yield Button("Start Session", id="start_button", variant="primary")
                    yield Button("Settings (Ctrl+S)", id="settings_button")
                    yield Button("Quit", id="quit_button", variant="error")
    
    def _get_model_options(self, provider: str) -> List[tuple]:
        """Get available models for a provider"""
        models_by_provider = {
            "openrouter": [
                ("GPT-4", "openai/gpt-4"),
                ("GPT-4 Turbo", "openai/gpt-4-turbo"),
                ("GPT-3.5 Turbo", "openai/gpt-3.5-turbo"),
                ("Claude 3 Opus", "anthropic/claude-3-opus-20240229"),
                ("Claude 3 Sonnet", "anthropic/claude-3-sonnet-20240229"),
                ("Mistral Large", "mistralai/mistral-large")
            ],
            "openai": [
                ("GPT-4", "gpt-4"),
                ("GPT-4 Turbo", "gpt-4-turbo"),
                ("GPT-4 Turbo Preview", "gpt-4-turbo-preview"),
                ("GPT-3.5 Turbo", "gpt-3.5-turbo")
            ],
            "anthropic": [
                ("Claude 3 Opus", "claude-3-opus-20240229"),
                ("Claude 3 Sonnet", "claude-3-sonnet-20240229"),
                ("Claude 3 Haiku", "claude-3-haiku-20240307")
            ],
            "local": [
                ("CodeLlama 7B", "TheBloke/CodeLlama-7B-GGUF"),
                ("Mistral 7B", "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"),
                ("Llama 2 7B", "TheBloke/Llama-2-7B-GGUF")
            ]
        }
        
        return models_by_provider.get(provider, [])
    
    def on_mount(self) -> None:
        """Initialize screen on mount"""
        # Set current provider
        provider_select = self.query_one("#provider_select", Select)
        provider_select.value = self.current_provider
        
        # Set current model
        model_select = self.query_one("#model_select", Select)
        model_select.value = self.current_model
        
        # Focus chat input
        chat_input = self.query_one("#chat_input", Input)
        chat_input.focus()
    
    @on(Select.Changed, "#provider_select")
    def on_provider_changed(self, event: Select.Changed) -> None:
        """Handle provider change"""
        self.current_provider = event.value
        
        # Update model options
        model_select = self.query_one("#model_select", Select)
        model_select.clear_options()
        model_options = self._get_model_options(self.current_provider)
        model_select.add_options(model_options)
        model_select.value = model_options[0][1] if model_options else ""
        self.current_model = model_select.value
    
    @on(Select.Changed, "#model_select")
    def on_model_changed(self, event: Select.Changed) -> None:
        """Handle model change"""
        self.current_model = event.value
    
    @on(Input.Changed, "#custom_model_input")
    def on_custom_model_changed(self, event: Input.Changed) -> None:
        """Handle custom model input"""
        self.custom_model = event.value.strip()
    
    @on(Input.Submitted, "#chat_input")
    def on_chat_submit(self, event: Input.Submitted) -> None:
        """Handle chat input submission"""
        self.first_prompt = event.value.strip()
        self.action_start_session()
    
    @on(Button.Pressed, "#start_button")
    def on_start_button(self) -> None:
        """Handle start button press"""
        chat_input = self.query_one("#chat_input", Input)
        self.first_prompt = chat_input.value.strip()
        self.action_start_session()
    
    @on(Button.Pressed, "#settings_button")
    def on_settings_button(self) -> None:
        """Handle settings button press"""
        self.action_show_settings()
    
    @on(Button.Pressed, "#quit_button")
    def on_quit_button(self) -> None:
        """Handle quit button press"""
        self.action_quit()
    
    def action_start_session(self) -> None:
        """Start a new session and launch dashboard"""
        # Determine final model (use custom if provided)
        final_model = self.custom_model if self.custom_model else self.current_model
        
        # Create session
        if MANAGERS_AVAILABLE:
            session_id = self.session_manager.create_session(
                name="",
                provider=self.current_provider,
                model=final_model
            )
            
            # Save first prompt
            if self.first_prompt:
                self.session_manager.update_chat_history("user", self.first_prompt)
            
            # Mark session as started
            self.session_started = True
            
            # Call callback to launch dashboard
            if self.on_start_callback:
                self.on_start_callback(
                    session_id=session_id,
                    first_prompt=self.first_prompt,
                    provider=self.current_provider,
                    model=final_model
                )
            else:
                self.notify(
                    f"Session started! Provider: {self.current_provider}, Model: {final_model}",
                    title="Session Started",
                    severity="information"
                )
        else:
            self.notify(
                "Session managers not available",
                title="Error",
                severity="error"
            )
    
    def action_show_settings(self) -> None:
        """Show settings modal"""
        if MANAGERS_AVAILABLE:
            settings_screen = EnhancedSettings()
            self.push_screen(settings_screen)
        else:
            self.notify("Settings not available - managers not loaded", severity="error")
    
    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()


def launch_welcome_screen(on_start: Optional[callable] = None):
    """
    Launch the welcome screen
    
    Args:
        on_start: Callback when session starts (session_id, first_prompt, provider, model)
    """
    app = WelcomeScreen(on_start=on_start)
    
    def on_session_started(**kwargs):
        app.exit()
        if on_start:
            on_start(**kwargs)
    
    app.on_start_callback = on_session_started
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error launching welcome screen: {e}")


if __name__ == "__main__":
    # Demo welcome screen
    launch_welcome_screen()
