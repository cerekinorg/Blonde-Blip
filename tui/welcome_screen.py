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

BLONDE_WORDMARK_DIM = r"""
██████╗ ██╗      ██████╗ ███╗   ██╗██████╗ ███████╗
██╔══██╗██║     ██╔═══██╗████╗  ██║██╔══██╗██╔════╝
██████╔╝██║     ██║   ██║██╔██╗ ██║██║  ██║█████╗  
██╔══██╗██║     ██║   ██║██║╚██╗██║██║  ██║██╔══╝  
██████╔╝███████╗╚██████╔╝██║ ╚████║██████╔╝███████╗
╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝
"""

BLONDE_WORDMARK_BRIGHT = r"""
░▒▓███████▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓███████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓███████▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓███████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░        
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░        
░▒▓███████▓▒░░▒▓████████▓▒░▒▓█▓▒░▒▓█▓▒░                                              
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
        background: #0b0b0b;
    }

    #root {
        width: 100%;
        height: 100%;
    }

    #center_stack {
        align: center middle;
        width: 100%;
        height: 100%;
    }

    #brand_logo {
        content-align: center middle;
        width: auto;
        height: auto;
        margin-bottom: 1;
    }

    #prompt_card {
        width: 78;
        height: auto;
        background: #202020;
        padding: 0;
    }

    #prompt_row {
        width: 100%;
        height: auto;
    }

    #prompt_bar {
        width: 1;
        background: #3b82f6;
    }

    #search_input {
        width: 1fr;
        height: 3;
        border: none;
        background: #202020;
        padding: 0 1;
        color: #d6d6d6;
    }

    #search_input:focus {
        border: none;
        background: #202020;
    }

    #chips_row {
        width: 100%;
        padding: 0 1 1 1;
        height: auto;
    }

    .chip {
        width: auto;
        height: auto;
        margin-right: 1;
        color: #a8a8a8;
    }

    #hints {
        width: 78;
        text-align: right;
        color: #a8a8a8;
        padding-top: 1;
    }

    #badges {
        display: none;
    }

    #status_bar {
        dock: bottom;
        width: 100%;
        height: 1;
        color: #a8a8a8;
        background: #0b0b0b;
    }

    #status_left {
        dock: left;
        width: auto;
        padding-left: 1;
    }

    #status_right {
        dock: right;
        width: auto;
        padding-right: 1;
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
            logo_widget = self.query_one("#brand_logo", Static)
            logo_widget.update(
                f"[bold #6b6b6b]{BLONDE_WORDMARK_DIM}[/bold #6b6b6b][bold {new_color}]{BLONDE_WORDMARK_BRIGHT}[/bold {new_color}]"
            )
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
        """Compose the OpenCode-style welcome screen"""
        with Container(id="root"):
            with Container(id="status_bar"):
                yield Static("~ /Reboot/Blonde-cli:main", id="status_left")
                yield Static("1.0.0", id="status_right")

            with Vertical(id="center_stack"):
                yield Static(
                    f"[bold #6b6b6b]{BLONDE_WORDMARK_DIM}[/bold #6b6b6b][bold {self.logo_color}]{BLONDE_WORDMARK_BRIGHT}[/bold {self.logo_color}]",
                    id="brand_logo",
                )

                with Container(id="prompt_card"):
                    with Horizontal(id="prompt_row"):
                        yield Static("", id="prompt_bar")
                        yield ChatInput(
                            placeholder='Ask anything... "What is the tech stack of this project?"',
                            id="search_input",
                        )
                    with Horizontal(id="chips_row"):
                        yield Static("[bold #3b82f6]Provider[/bold #3b82f6]", classes="chip", id="chip_provider")
                        yield Static("[bold]Model[/bold]", classes="chip", id="chip_model")
                        yield Static("[dim]Agent[/dim]", classes="chip", id="chip_agent")

                yield Static("[bold]tab[/bold] switch agent   [bold]ctrl+p[/bold] commands", id="hints")

                with Container(id="badges"):
                    yield Static("Provider: Loading...", id="provider_badge")
                    yield Static("Model: Loading...", id="model_badge")
    
    def on_mount(self) -> None:
        """Initialize screen on mount"""
        # Start configuration file watcher
        self._start_config_watcher()
        
        # Update from config
        self._update_from_config()
        
        # Focus search input
        search_input = self.query_one("#search_input", ChatInput)
        search_input.focus()
    
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

        self._update_chips_and_hints(config)

    def _update_chips_and_hints(self, config: Dict[str, Any]) -> None:
        provider = config.get('default_provider', 'openrouter')
        providers = config.get('providers', {})
        model = providers.get(provider, {}).get('model', 'openai/gpt-4')
        agent = config.get('preferences', {}).get('default_agent', 'generator')

        try:
            chip_provider = self.query_one("#chip_provider", Static)
            chip_model = self.query_one("#chip_model", Static)
            chip_agent = self.query_one("#chip_agent", Static)
            hints = self.query_one("#hints", Static)

            chip_provider.update(f"[bold #3b82f6]{provider}[/bold #3b82f6]")
            chip_model.update(f"[bold]{model}[/bold]")
            chip_agent.update(f"[dim]{agent}[/dim]")
            hints.update(f"[bold]tab[/bold] switch agent ({agent})   [bold]ctrl+p[/bold] commands")
        except Exception:
            pass
    
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
    
    @on(Input.Submitted, "#search_input")
    def on_search_submit(self, event: Input.Submitted) -> None:
        """Handle search input submission"""
        self.first_prompt = event.value.strip()
        self.action_start_session()
    
    @on(Button.Pressed, "#start_button")
    def on_start_button(self) -> None:
        """Handle start button press"""
        search_input = self.query_one("#search_input", ChatInput)
        self.first_prompt = search_input.value.strip()
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
        try:
            search_input = self.query_one("#search_input", ChatInput)
            self.first_prompt = search_input.value.strip()
        except Exception:
            pass

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