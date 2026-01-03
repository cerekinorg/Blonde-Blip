"""
Setup Wizard - Enhanced with Blip character selection and custom model input
Interactive setup wizard with modern Textual UI
"""

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Static, Input, Button, 
    Select, RadioSet, RadioButton
)
from textual.containers import Horizontal, Vertical, Container
from textual import on
from textual.reactive import reactive
from pathlib import Path
import os
import json
import subprocess

CONFIG_DIR = Path.home() / ".blonde"
CONFIG_FILE = CONFIG_DIR / "config.json"


try:
    from tui.blip_characters import (
        get_character, list_characters, get_default_character
    )
    BLIP_AVAILABLE = True
except ImportError:
    BLIP_AVAILABLE = False
    print("Warning: Blip characters not available")


class EnhancedSetupWizard(App):
    """Enhanced Textual-based setup wizard with Blip selection and custom model"""
    
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
    
    Select {
        margin: 1 0;
    }
    
    RadioSet {
        margin: 1 0;
    }
    
    .blip-preview {
        text-align: center;
        padding: 1;
        margin: 1 0;
    }
    
    .info-text {
        text-style: dim;
        padding: 1;
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
                "blip_character": "axolotl",
                "blip_animation_speed": 0.3,
                "colors": "auto"
            }
        }
        
        # Step selections
        self.selected_provider = "openrouter"
        self.selected_model = "openai/gpt-4"
        self.custom_model = ""
        self.selected_blip_character = "axolotl"
        self.selected_privacy_mode = "balanced"
        self.selected_theme = "auto"
    
    def compose(self) -> ComposeResult:
        yield Header("Blonde CLI - Setup Wizard")
        yield Static(self._get_step_content(), id="step_content", classes="StepContainer")
        yield Footer()
    
    def _get_step_content(self) -> str:
        """Get content for current step"""
        if self.current_step == 0:
            return self._welcome_step()
        elif self.current_step == 1:
            return self._blip_selection_step()
        elif self.current_step == 2:
            return self._provider_setup_step()
        elif self.current_step == 3:
            return self._preferences_step()
        elif self.current_step == 4:
            return self._complete_step()
        return "Unknown step"
    
    def _welcome_step(self) -> str:
        """Welcome step"""
        return f"""
        [bold cyan]╔═════════════════════════════════════════════════╗[/bold cyan]
        [bold cyan]║          Welcome to Blonde CLI Setup!             ║[/bold cyan]
        [bold cyan]╚═══════════════════════════════════════════════════╝[/bold cyan]
        
        This wizard will guide you through configuring Blonde CLI.
        
        [dim]Configuration will be saved to:[/dim] {CONFIG_FILE}
        
        [bold]You will configure:[/bold]
        • Choose your Blip character (digital companion)
        • AI Providers (OpenRouter, OpenAI, Anthropic, Local)
        • Model selection (with custom model option)
        • UI Preferences (Blip, colors, etc.)
        • Privacy Settings
        
        Press [bold]Enter[/bold] to begin configuration.
        """
    
    def _blip_selection_step(self) -> str:
        """Blip character selection step"""
        characters = list_characters() if BLIP_AVAILABLE else []
        
        character_options = ""
        for i, char_name in enumerate(characters, 1):
            char = get_character(char_name) if BLIP_AVAILABLE else None
            if char:
                art = char.get_art("happy")
                color = char.get_color("happy")
                selected = "← " if char_name == self.selected_blip_character else "  "
                character_options += f"[dim]{i}.[/dim] [cyan]{selected}{char_name.title()}[/cyan]\n"
                character_options += f"  [dim]   {art}[/dim]\n\n"
        
        return f"""
        [bold cyan]Choose Your Blip Character[/bold cyan]
        
        [dim]Blip is your digital companion that guides you through development.
        Choose the personality that fits your style![/dim]
        
        {character_options}
        
        [dim]Press number (1-{len(characters)}) or Enter to use Axolotl (default)[/dim]
        """
    
    def _provider_setup_step(self) -> str:
        """Provider configuration step with custom model input"""
        providers = "Not configured"
        if self.config_data.get("providers"):
            configured = [k for k, v in self.config_data["providers"].items() if v.get("configured", False)]
            if configured:
                providers = ", ".join(configured)
        
        model_options = ""
        provider_models = {
            "openrouter": [
                ("1", "openai/gpt-4", "GPT-4"),
                ("2", "openai/gpt-4-turbo", "GPT-4 Turbo"),
                ("3", "openai/gpt-3.5-turbo", "GPT-3.5 Turbo"),
                ("4", "anthropic/claude-3-opus-20240229", "Claude 3 Opus"),
                ("5", "anthropic/claude-3-sonnet-20240229", "Claude 3 Sonnet"),
                ("6", "mistralai/mistral-large", "Mistral Large")
            ],
            "openai": [
                ("1", "gpt-4", "GPT-4"),
                ("2", "gpt-4-turbo", "GPT-4 Turbo"),
                ("3", "gpt-4-turbo-preview", "GPT-4 Turbo Preview"),
                ("4", "gpt-3.5-turbo", "GPT-3.5 Turbo")
            ],
            "anthropic": [
                ("1", "claude-3-opus-20240229", "Claude 3 Opus"),
                ("2", "claude-3-sonnet-20240229", "Claude 3 Sonnet"),
                ("3", "claude-3-haiku-20240307", "Claude 3 Haiku")
            ],
            "local": [
                ("1", "TheBloke/CodeLlama-7B-GGUF", "CodeLlama 7B"),
                ("2", "TheBloke/Mistral-7B-Instruct-v0.2-GGUF", "Mistral 7B"),
                ("3", "TheBloke/Llama-2-7B-GGUF", "Llama 2 7B")
            ]
        }
        
        models = provider_models.get(self.selected_provider, [])
        for i, (num, model_id, model_name) in enumerate(models, 1):
            selected = "← " if model_id == self.selected_model else "  "
            model_options += f"[dim]{num}.[/dim] [cyan]{selected}{model_name}[/cyan]\n"
        
        return f"""
        [bold cyan]AI Provider Configuration[/bold cyan]
        
        [dim]Provider:[/dim] {self.selected_provider.title()}
        
        [bold]Model Selection:[/bold]
        {model_options}
        
        [bold dim]Or specify custom model:[/bold dim]
        [dim]Type the exact model name (e.g., meta-llama/llama-3-70b-instruct)[/dim]
        
        [cyan]Selected Provider:[/cyan] {self.selected_provider}
        [cyan]Selected Model:[/cyan] {self.selected_model}
        [cyan]Custom Model:[/cyan] {self.custom_model if self.custom_model else "None"}
        
        [dim]Note: You can change providers and models anytime in Settings (Ctrl+S)[/dim]
        """
    
    def _preferences_step(self) -> str:
        """Preferences configuration step"""
        return f"""
        [bold cyan]UI Preferences[/bold cyan]
        
        [dim]Configure your interface preferences:[/dim]
        
        [bold]Blip Character:[/bold] {self.selected_blip_character.title()}
        
        [bold]Privacy Mode:[/bold] {self.selected_privacy_mode}
        [dim]Options: strict, balanced, permissive[/dim]
        
        [bold]Show Tips:[/bold] {self.config_data['preferences'].get('show_tips', True)}
        
        [bold]Stream Responses:[/bold] {self.config_data['preferences'].get('stream_responses', True)}
        
        [bold]Animation Speed:[/bold] {self.config_data['preferences'].get('blip_animation_speed', 0.3)}s
        
        [bold]Theme:[/bold] {self.selected_theme}
        [dim]Options: auto, light, dark, none[/dim]
        """
    
    def _complete_step(self) -> str:
        """Complete step"""
        return f"""
        [bold cyan]╔═══════════════════════════════════════════════════╗[/bold cyan]
        [bold cyan]║            Setup Complete!                    ║[/bold cyan]
        [bold cyan]╚═════════════════════════════════════════════════════╝[/bold cyan]
        
        [bold green]✓ Configuration saved[/bold green]
        [bold green]✓ Ready to use![/bold green]
        
        [dim]Your settings:[/dim]
        
        [bold]Blip Character:[/bold] {self.selected_blip_character.title()}
        [bold]Default Provider:[/bold] {self.selected_provider}
        [bold]Model:[/bold] {self.custom_model if self.custom_model else self.selected_model}
        [bold]Privacy Mode:[/bold] {self.selected_privacy_mode}
        [bold]Theme:[/bold] {self.selected_theme}
        
        [bold]Next Steps:[/bold]
        1. Run [cyan]blonde[/cyan] to start the CLI
        2. Use [cyan]/help[/cyan] for available commands
        3. Use [cyan]Ctrl+S[/cyan] to open Settings anytime
        4. Use [cyan]Ctrl+M[/cyan] to switch models/providers
        5. Use [cyan]Ctrl+L[/cyan] to toggle left panel
        6. Use [cyan]Ctrl+R[/cyan] to toggle right panel
        
        [dim]Press Ctrl+C to exit and start using Blonde CLI![/dim]
        """
    
    def on_key(self, event) -> None:
        """Handle keyboard input for step navigation and selections"""
        if event.key == "enter":
            if self.current_step < 4:
                self.action_next_step()
            else:
                self.exit()
        elif event.key == "escape":
            self.exit()
        elif event.key.isdigit():
            # Handle number selections
            num = int(event.key)
            self._handle_number_selection(num)
    
    def _handle_number_selection(self, num: int):
        """Handle number-based selections"""
        if self.current_step == 1:
            # Blip character selection
            characters = list_characters() if BLIP_AVAILABLE else []
            if num >= 1 and num <= len(characters):
                self.selected_blip_character = characters[num - 1]
        elif self.current_step == 2:
            # Model selection
            provider_models = {
                "openrouter": ["openai/gpt-4", "openai/gpt-4-turbo", "openai/gpt-3.5-turbo", 
                             "anthropic/claude-3-opus-20240229", "anthropic/claude-3-sonnet-20240229", "mistralai/mistral-large"],
                "openai": ["gpt-4", "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-3.5-turbo"],
                "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
            }
            models = provider_models.get(self.selected_provider, [])
            if num >= 1 and num <= len(models):
                self.selected_model = models[num - 1]
        
        # Update display
        step_content = self.query_one("#step_content", Static)
        if step_content:
            step_content.update(self._get_step_content())
    
    def action_next_step(self):
        """Move to next step"""
        if self.current_step == 0:
            self.current_step = 1
        elif self.current_step == 1:
            # Save Blip selection
            self.config_data['preferences']['blip_character'] = self.selected_blip_character
            self.current_step = 2
        elif self.current_step == 2:
            # Save provider and model selection
            self.config_data['default_provider'] = self.selected_provider
            
            # Initialize provider config
            if self.selected_provider not in self.config_data['providers']:
                self.config_data['providers'][self.selected_provider] = {}
            
            # Use custom model if provided, otherwise use selected model
            final_model = self.custom_model if self.custom_model.strip() else self.selected_model
            
            self.config_data['providers'][self.selected_provider]['model'] = final_model
            self.config_data['providers'][self.selected_provider]['configured'] = True
            
            self.current_step = 3
        elif self.current_step == 3:
            self.current_step = 4
        elif self.current_step == 4:
            # Save all preferences
            self.action_save_config()
            self.exit()
        
        step_content = self.query_one("#step_content", Static)
        if step_content:
            step_content.update(self._get_step_content())
    
    def action_save_config(self):
        """Save configuration to file"""
        try:
            self.config_data['setup_completed'] = True
            
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            
            self.notify("Configuration saved successfully!", severity="information")
        except Exception as e:
            self.notify(f"Error saving configuration: {e}", severity="error")


def run_enhanced_setup_wizard():
    """Run enhanced setup wizard"""
    import sys
    
    try:
        from textual import __version__
        TEXTUAL_AVAILABLE = True
    except ImportError:
        TEXTUAL_AVAILABLE = False
    
    if TEXTUAL_AVAILABLE:
        # Use full Textual wizard
        app = EnhancedSetupWizard()
        app.run()
    else:
        # Use fallback
        print("Blonde CLI Setup Wizard")
        print("=" * 50)
        print()
        print("Enhanced setup requires Textual. Installing...")
        
        # Create default config with Blip character
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        config = {
            "version": "1.0.0",
            "setup_completed": True,
            "default_provider": "openrouter",
            "providers": {
                "openrouter": {
                    "model": "openai/gpt-4",
                    "configured": False
                }
            },
            "preferences": {
                "privacy_mode": "balanced",
                "show_tips": True,
                "stream_responses": True,
                "show_blip": True,
                "blip_character": "axolotl",
                "blip_animation_speed": 0.3,
                "colors": "auto"
            }
        }
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        print()
        print("Setup complete! You can now run 'blonde' to start.")
        print(f"Configuration saved to: {CONFIG_FILE}")


if __name__ == "__main__":
    run_enhanced_setup_wizard()
