"""
Welcome Screen - Compact centered design for Blonde CLI
Provides theme-aware logo, expandable chatbox, and provider/model badges
"""

from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Horizontal, Container
from textual import on
from textual.reactive import reactive
from pathlib import Path
import json
import threading
import time
from typing import Optional, List, Dict, Any

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

# One-size ASCII logo as specified in the plan
ASCII_LOGO = r"""
 ██████╗ ██╗      ██████╗ ███╗   ██╗██████╗ ███████╗
 ██╔══██╗██║     ██╔═══██╗████╗  ██║██╔══██╗██╔════╝
 ██████╔╝██║     ██║   ██║██╔██╗ ██║██║  ██║█████╗  
 ██╔══██╗██║     ██║   ██║██║╚██╗██║██║  ██║██╔══╝  
  ██████╔╝███████╗╚██████╔╝██║ ╚████║██████╔╝███████╗
  ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝
"""

# Theme color mapping as specified in the plan
THEME_COLORS = {
    "none": "white",      # Default theme
    "auto": "cyan",       # Auto-detect theme
    "light": "blue",      # Light theme
    "dark": "cyan",       # Dark theme
}


class ChatInput(Input):
    """Custom chat input with auto-scroll behavior"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_lines = 3
    
    def _on_change(self, event: Input.Changed) -> None:
        """Handle input change and auto-scroll"""
        # Auto-scroll to show what's being typed
        self.scroll_end()
        
        # Expand height if needed (up to 3 lines)
        line_count = len(self.value.split('\n'))
        if line_count > self.max_lines:
            self.styles.height = self.max_lines


class WelcomeScreen(App):
    """Compact centered welcome screen with theme-aware logo and expandable chat"""
    
    # Reactive logo color for theme updates
    logo_color = reactive('white')
    
    CSS = """
    Screen {
        align: center middle;
        background: $background;
    }

    #welcome_container {
        width: 80;
        height: auto;
        min-height: 20;
        border: solid $primary;
        background: $panel;
        padding: 2;
        margin: 2;
    }

    #container_title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #logo_section {
        text-align: center;
        padding: 1;
        height: 8;
    }

    #chat_section {
        height: auto;
        margin-top: 1;
    }

    #chat_input {
        width: 60%;
        height: 2;
        max-height: 3;
        overflow-y: auto;
        border: solid $primary;
        background: $surface;
        padding: 1;
    }

    #chat_input:focus {
        border: solid $accent;
        background: $primary;
    }

    #model_info {
        width: 40%;
        margin-left: 2;
        padding: 1;
        background: $surface;
        border: solid $accent;
    }

    #model_info_label {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #provider_badge, #model_badge {
        width: 100%;
        padding: 0 1;
        margin: 0 0 1 0;
        border: solid $primary;
        background: $panel;
        text-align: center;
    }

    #help_text {
        text-align: center;
        text-style: dim;
        padding: 1;
        margin-top: 1;
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
        ("ctrl+c", "app.quit", "Quit"),
        ("ctrl+s", "show_settings", "Settings"),
        ("enter", "start_session", "Start Session"),
        ("escape", "app.quit", "Quit")
    ]
    
    def __init__(self, on_start: Optional[callable] = None):
        super().__init__()
        self.on_start_callback = on_start
        self.session_started = reactive(False)
        self.current_provider = "openrouter"
        self.current_model = "openai/gpt-4"
        self.first_prompt = ""
        self._config_watcher = None
        self._last_config_mtime = 0
        
        # Load managers
        if MANAGERS_AVAILABLE:
            self.blip_manager = get_blip_manager()
            self.session_manager = get_session_manager()
            self.provider_manager = ProviderManager()
        
        # Load config
        self._load_config()
    
    def get_theme_color(self) -> str:
        """Get current theme color for logo"""
        config = self._load_config()
        theme = config.get('preferences', {}).get('colors', 'none')
        return THEME_COLORS.get(theme, 'white')
    
    def watch_logo_color(self, old_color: str, new_color: str) -> None:
        """Update logo color when theme changes"""
        try:
            logo_widget = self.query_one("#ascii_logo", Static)
            logo_widget.update(f"[bold {new_color}]{ASCII_LOGO}[/bold {new_color}]")
        except:
            pass
    
    def _load_config(self) -> Dict[str, Any]:
        """Load current provider and model from config"""
        config = {}
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
        return config
    
    def compose(self) -> ComposeResult:
        """Compose the compact centered welcome screen"""
        with Container(id="welcome_container"):
            # Add title manually since CSS border-title is not supported
            yield Static("[bold]Blonde CLI[/bold]", id="container_title")
            # Logo section
            with Vertical(id="logo_section"):
                yield Static(
                    f"[bold {self.logo_color}]{ASCII_LOGO}[/bold {self.logo_color}]",
                    id="ascii_logo"
                )
            
            # Chat section with input and model info
            with Horizontal(id="chat_section"):
                # Chat input (60% width)
                yield ChatInput(
                    placeholder="Type your message here...",
                    id="chat_input"
                )
                
                # Model info badges (40% width)
                with Container(id="model_info"):
                    yield Static("Current Model", id="model_info_label")
                    yield Static("Provider: Loading...", id="provider_badge")
                    yield Static("Model: Loading...", id="model_badge")
            
            # Help text
            yield Static(
                "[dim]Press Enter to start session • Ctrl+S for settings • Ctrl+C to quit[/dim]",
                id="help_text"
            )
            
            # Action buttons
            with Horizontal():
                yield Button("Start Session", id="start_button", variant="primary")
                yield Button("Settings", id="settings_button")
                yield Button("Quit", id="quit_button", variant="error")
    
    def on_mount(self) -> None:
        """Initialize screen on mount"""
        # Start configuration file watcher
        self._start_config_watcher()
        
        # Update from config
        self._update_from_config()
        
        # Focus chat input
        chat_input = self.query_one("#chat_input", ChatInput)
        chat_input.focus()
    
    def _start_config_watcher(self) -> None:
        """Watch configuration file for changes"""
        def watch_config():
            while True:
                try:
                    if CONFIG_FILE.exists():
                        mtime = CONFIG_FILE.stat().st_mtime
                        if mtime > self._last_config_mtime:
                            self._last_config_mtime = mtime
                            self.call_from_thread(self._update_from_config)
                except Exception:
                    pass
                time.sleep(1)  # Check every second
        
        self._config_watcher = threading.Thread(target=watch_config, daemon=True)
        self._config_watcher.start()
    
    def _update_from_config(self) -> None:
        """Update UI when configuration changes"""
        config = self._load_config()
        
        # Update logo color
        theme = config.get('preferences', {}).get('colors', 'none')
        self.logo_color = THEME_COLORS.get(theme, 'white')
        
        # Update provider/model badges
        self._update_provider_model_badges()
    
    def _update_provider_model_badges(self) -> None:
        """Update provider/model display badges"""
        config = self._load_config()
        provider = config.get('default_provider', 'openrouter')
        providers = config.get('providers', {})
        model = providers.get(provider, {}).get('model', 'openai/gpt-4')
        
        try:
            provider_badge = self.query_one("#provider_badge", Static)
            model_badge = self.query_one("#model_badge", Static)
            
            provider_badge.update(f"Provider: [bold cyan]{provider}[/bold cyan]")
            model_badge.update(f"Model: [bold cyan]{model}[/bold cyan]")
        except:
            pass
    
    @on(Input.Submitted, "#chat_input")
    def on_chat_submit(self, event: Input.Submitted) -> None:
        """Handle chat input submission"""
        self.first_prompt = event.value.strip()
        self.action_start_session()
    
    @on(Button.Pressed, "#start_button")
    def on_start_button(self) -> None:
        """Handle start button press"""
        chat_input = self.query_one("#chat_input", ChatInput)
        self.first_prompt = chat_input.value.strip()
        self.action_start_session()
    
    @on(Button.Pressed, "#settings_button")
    def on_settings_button(self) -> None:
        """Handle settings button press"""
        self.action_show_settings()
    
    @on(Button.Pressed, "#quit_button")
    def on_quit_button(self) -> None:
        """Handle quit button press"""
        self.app.exit()
    
    def action_start_session(self) -> None:
        """Start a new session and launch dashboard"""
        config = self._load_config()
        provider = config.get('default_provider', 'openrouter')
        providers = config.get('providers', {})
        model = providers.get(provider, {}).get('model', 'openai/gpt-4')
        
        # Create session
        if MANAGERS_AVAILABLE:
            session_id = self.session_manager.create_session(
                name="",
                provider=str(provider),
                model=str(model)
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
                    provider=str(provider),
                    model=str(model)
                )
            else:
                self.notify(
                    f"Session started! Provider: {provider}, Model: {model}",
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