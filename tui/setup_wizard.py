"""
Blonde CLI - Textual-based Setup Wizard
Interactive setup wizard with modern Textual UI
"""

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Static, Input, Button, 
    Tabs, Tab, ContentSwitcher, RadioButton, RadioSet
)
from textual.containers import Horizontal, Vertical, Container
from textual import on
from textual.reactive import reactive
from rich.text import Text
from pathlib import Path
import os
import json
import subprocess

CONFIG_DIR = Path.home() / ".blonde"
CONFIG_FILE = CONFIG_DIR / "config.json"


class SetupWizard(App):
    """Textual-based setup wizard"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 1 1;
    }
    
    #header {
        height: 3;
    }
    
    #content {
        border: solid $primary;
        background: $panel;
    }
    
    #footer {
        height: 3;
    }
    
    StepContainer {
        padding: 2;
    }
    
    Button {
        width: 25;
        margin: 1;
    }
    
    Input {
        margin: 1 0;
    }
    """
    
    BINDINGS = [
        ("escape", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit")
    ]
    
    def __init__(self):
        super().__init__()
        self.current_step = 0
        self.config_data = {
            "version": "1.0.0",
            "setup_completed": False,
            "default_provider": "openrouter",
            "providers": {},
            "preferences": {
                "privacy_mode": "balanced",
                "show_tips": True,
                "stream_responses": True,
                "show_blip": True,
                "colors": "auto"
            }
        }
    
    def compose(self) -> ComposeResult:
        yield Header("Blonde CLI - Setup Wizard")
        yield Static(self._get_step_content(), id="step_content", classes="StepContainer")
        yield Footer()
    
    def _get_step_content(self) -> str:
        """Get content for current step"""
        if self.current_step == 0:
            return self._welcome_step()
        elif self.current_step == 1:
            return self._provider_setup_step()
        elif self.current_step == 2:
            return self._preferences_step()
        elif self.current_step == 3:
            return self._complete_step()
        return "Unknown step"
    
    def _welcome_step(self) -> str:
        """Welcome step"""
        return f"""
        [bold cyan]╔═════════════════════════════════════════════╗[/bold cyan]
        [bold cyan]║          Welcome to Blonde CLI Setup!             ║[/bold cyan]
        [bold cyan]╚═════════════════════════════════════════════╝[/bold cyan]
        
        This wizard will guide you through configuring Blonde CLI.
        
        [dim]Configuration will be saved to:[/dim] {CONFIG_FILE}
        
        [bold]You will configure:[/bold]
        • AI Providers (OpenRouter, OpenAI, Anthropic, Local)
        • UI Preferences (Blip, colors, etc.)
        • Privacy Settings
        
        Press [bold]Enter[/bold] to begin configuration.
        """
    
    def _provider_setup_step(self) -> str:
        """Provider configuration step"""
        providers = "Not configured"
        if self.config_data.get("providers"):
            configured = [k for k, v in self.config_data["providers"].items() if v.get("configured", False)]
            if configured:
                providers = ", ".join(configured)
        
        return f"""
        [bold cyan]AI Provider Configuration[/bold cyan]
        
        [dim]Current providers:[/dim] {providers if providers != 'Not configured' else 'None'}
        
        [bold]Available Providers:[/bold]
        1. [cyan]OpenRouter[/cyan] - Multiple AI models, one API key
        2. [cyan]OpenAI[/cyan] - GPT models, official OpenAI API
        3. [cyan]Anthropic[/cyan] - Claude models, official Anthropic API
        4. [cyan]Local (GGUF)[/cyan] - Run locally, no API key needed
        
        [dim]Note: You can configure multiple providers and switch between them later.[/dim]
        """
    
    def _preferences_step(self) -> str:
        """Preferences configuration step"""
        return f"""
        [bold cyan]UI Preferences[/bold cyan]
        
        [dim]Configure your interface preferences:[/dim]
        
        [bold]Privacy Mode:[/bold] {self.config_data['preferences'].get('privacy_mode', 'balanced')}
        [dim]Options: strict, balanced, permissive[/dim]
        
        [bold]Show Tips:[/bold] {self.config_data['preferences'].get('show_tips', True)}
        [bold]Stream Responses:[/bold] {self.config_data['preferences'].get('stream_responses', True)}
        [bold]Show Blip:[/bold] {self.config_data['preferences'].get('show_blip', True)}
        [bold]Colors:[/bold] {self.config_data['preferences'].get('colors', 'auto')}
        [dim]Options: auto, light, dark, none[/dim]
        """
    
    def _complete_step(self) -> str:
        """Complete step"""
        return f"""
        [bold cyan]╔═════════════════════════════════════════════╗[/bold cyan]
        [bold cyan]║            Setup Complete!                    ║[/bold cyan]
        [bold cyan]╚═════════════════════════════════════════════╝[/bold cyan]
        
        [bold green]✓ Configuration saved[/bold green]
        [bold green]✓ Ready to use![/bold green]
        
        [dim]Your settings:[/dim]
        
        [bold]Default Provider:[/bold] {self.config_data.get('default_provider', 'openrouter')}
        [bold]Providers Configured:[/bold] {len(self.config_data.get('providers', {}))}
        
        [bold]Next Steps:[/bold]
        1. Run [cyan]blonde[/cyan] to start the CLI
        2. Use [cyan]/help[/cyan] for available commands
        3. Use [cyan]/settings[/cyan] to change configuration
        
        Press [bold]Ctrl+C[/bold] to exit and start using Blonde CLI!
        """
    
    def on_key(self, event) -> None:
        """Handle keyboard input for step navigation"""
        if event.key == "enter":
            if self.current_step < 3:
                if self.current_step == 1:
                    # Provider step - save provider info
                    self.action_save_provider()
                elif self.current_step == 2:
                    # Preferences step - save preferences
                    self.action_save_config()
                else:
                    self.action_next_step()
            else:
                # Complete - exit
                self.exit()
    
    def action_next_step(self) -> None:
        """Move to next step"""
        self.current_step = (self.current_step + 1) % 4
        self.query_one("#step_content", Static).update(self._get_step_content())
    
    def action_save_provider(self) -> None:
        """Save provider configuration"""
        self.config_data["providers"]["openrouter"] = {
            "configured": False,
            "model": "openai/gpt-4"
        }
        self.notify("Provider saved (configure in /settings)", severity="information")
        self.action_next_step()
    
    def action_save_config(self) -> None:
        """Save configuration to file"""
        self.config_data["setup_completed"] = True
        
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            
            self.notify("Configuration saved successfully!", severity="information")
            self.action_next_step()
        except Exception as e:
            self.notify(f"Error saving configuration: {e}", severity="error")


class SimpleSetupWizard(App):
    """Simplified setup wizard with minimal dependencies"""
    
    BINDINGS = [
        ("ctrl+c", "quit", "Quit")
    ]
    
    def __init__(self):
        super().__init__()
        self.step = 0
        
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("""
                [bold cyan]Blonde CLI Setup Wizard[/bold cyan]
                
                This wizard will help you configure Blonde CLI.
                
                [dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]
                """)
            yield Static("Press Enter to continue...", id="status")
    
    def on_key(self, event) -> None:
        if self.step == 0 and event.key == "enter":
            self.step = 1
            self.query_one("#status").update("Installing dependencies...")
            self._install_dependencies()
        elif self.step == 1:
            self.step = 2
            self.query_one("#status").update("Creating configuration...")
            self._create_config()
        elif self.step == 2:
            self.step = 3
            self.query_one("#status").update(
                """
                [bold green]✓ Setup Complete![/bold green]
                
                You can now run [cyan]blonde[/cyan] to start.
                
                Press Ctrl+C to exit.
                """
            )
    
    def _install_dependencies(self) -> None:
        """Install dependencies in venv if present"""
        venv_path = Path(".venv")
        
        if venv_path.exists():
            python_path = venv_path / "bin" / "python"
            pip_path = venv_path / "bin" / "pip"
            
            if python_path.exists() and pip_path.exists():
                self.notify(f"Found venv at {venv_path}", severity="information")
                
                try:
                    # Install textual in venv
                    subprocess.run(
                        [str(pip_path), "install", "textual>=0.44.0"],
                        check=True,
                        capture_output=True
                    )
                    self.notify("✓ Textual installed in venv", severity="information")
                except subprocess.CalledProcessError as e:
                    self.notify(f"✗ Failed to install: {e}", severity="error")
        else:
            self.notify("No venv found - skipping dependency installation", severity="warning")
    
    def _create_config(self) -> None:
        """Create default configuration"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        if not CONFIG_FILE.exists():
            config = {
                "version": "1.0.0",
                "setup_completed": True,
                "default_provider": "openrouter",
                "providers": {},
                "preferences": {
                    "privacy_mode": "balanced",
                    "show_tips": True,
                    "stream_responses": True,
                    "show_blip": True,
                    "colors": "auto"
                }
            }
            
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.notify("✓ Configuration created", severity="information")
        else:
            self.notify("✓ Configuration already exists", severity="information")


def run_setup_wizard():
    """Run setup wizard"""
    import sys
    
    try:
        from textual import __version__
        TEXTUAL_AVAILABLE = True
    except ImportError:
        TEXTUAL_AVAILABLE = False
    
    if TEXTUAL_AVAILABLE:
        # Use full Textual wizard
        app = SetupWizard()
        app.run()
    else:
        # Use simplified wizard
        print("Blonde CLI Setup Wizard")
        print("=" * 50)
        print()
        print("Installing dependencies...")
        
        wizard = SimpleSetupWizard()
        wizard.run()
        
        print()
        print("Setup complete! You can now run 'blonde' to start.")


if __name__ == "__main__":
    run_setup_wizard()
