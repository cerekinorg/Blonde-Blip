"""
Setup Wizard Enhanced - Complete first-time setup flow
Provider, Model, API, Blip, Theme, Privacy configuration with skip options
"""

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Static, Input, Button, 
    Select, RadioSet, RadioButton, Switch
)
from textual.containers import Horizontal, Vertical, Container
from textual.screen import ModalScreen
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
    """Enhanced setup wizard with complete flow per specification"""
    
    CSS = """
    Screen {
        background: #0b0b0b;
        layout: grid;
        grid-size: 1 1;
    }

    #setup_container {
        border: solid #444;
        background: #1a1a1a;
        padding: 2;
        margin: 1;
        width: 80;
        height: auto;
        align: center middle;
    }

    #step_title {
        text-align: center;
        text-style: bold;
        padding: 1;
        color: #3b82f6;
    }

    #step_content {
        padding: 1;
        background: #202020;
        border: solid #444;
        margin: 1 0;
    }

    Button {
        width: 20;
        margin: 1;
        background: #333;
        border: solid #555;
    }

    #continue_btn {
        background: #3b82f6;
        border: solid #3b82f6;
    }

    #skip_btn {
        background: #444;
        border: solid #666;
        color: #aaa;
    }

    Input {
        margin: 1 0;
        width: 100%;
        background: #111;
        border: solid #444;
        color: #d6d6d6;
    }

    Input:focus {
        border: solid #3b82f6;
    }

    Select {
        margin: 1 0;
        width: 100%;
        background: #111;
        border: solid #444;
    }

    RadioSet, RadioButton {
        margin: 1 0;
        color: #d6d6d6;
    }

    .step-indicator {
        text-align: center;
        text-style: dim;
        padding: 1;
        color: #888;
    }

    .required-note {
        text-style: bold;
        color: #ef4444;
        padding: 1;
    }

    .optional-note {
        text-style: dim;
        padding: 1;
        color: #888;
    }

    .blip-preview {
        text-align: center;
        padding: 1;
        margin: 1 0;
        border: solid #444;
        background: #111;
    }

    .provider-option {
        padding: 1;
        margin: 1 0;
        background: #252525;
        border: solid #444;
        color: #d6d6d6;
    }

    .provider-option:hover {
        background: #2a2a2a;
        border: solid #555;
    }
    """
    
    BINDINGS = [
        ("escape", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("enter", "continue", "Continue"),
        ("s", "skip_step", "Skip Step")
    ]
    
    def __init__(self):
        super().__init__()
        self.current_step = 0
        self.total_steps = 6  # Total setup steps
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
                "show_agent_thinking": True,
                "show_diff": True,
                "autosave_files": True,
                "blip_character": "axolotl",
                "blip_animation_speed": 0.3,
                "colors": "none"  # Default to "none" theme as per spec
            }
        }
        
        # Step data
        self.selected_provider = "openrouter"
        self.selected_model = "openai/gpt-4"
        self.api_key = ""
        self.custom_model = ""
        self.selected_blip_character = "axolotl"
        self.selected_theme = "none"
        self.selected_privacy_mode = "balanced"
    
    def compose(self) -> ComposeResult:
        """Compose setup wizard"""
        with Container(id="setup_container"):
            yield Static(f"Step {self.current_step + 1}/{self.total_steps}", id="step_indicator", classes="step-indicator")
            yield Static(self._get_step_title(), id="step_title")
            yield Static(id="step_content")
            yield Static(id="step_note")
            
            with Horizontal(id="button_container"):
                yield Button("Back", id="back_btn", disabled=self.current_step == 0)
                yield Button("Skip", id="skip_btn", classes="optional-note")
                yield Button("Continue", id="continue_btn", variant="primary")
                yield Button("Quit", id="quit_btn", variant="error")
    
    def on_mount(self) -> None:
        """Initialize wizard on mount"""
        self._update_step()
    
    def _get_step_title(self) -> str:
        """Get title for current step"""
        titles = [
            "Provider Selection",
            "Model Selection", 
            "API Configuration",
            "Blip Character (Optional)",
            "Theme Selection (Optional)",
            "Privacy Settings (Optional)"
        ]
        return titles[self.current_step] if self.current_step < len(titles) else "Setup Complete"
    
    def _update_step(self) -> None:
        """Update current step content"""
        step_content = self.query_one("#step_content", Static)
        step_note = self.query_one("#step_note", Static)
        continue_btn = self.query_one("#continue_btn", Button)
        back_btn = self.query_one("#back_btn", Button)
        skip_btn = self.query_one("#skip_btn", Button)
        
        # Update step indicator
        step_indicator = self.query_one("#step_indicator", Static)
        step_indicator.update(f"Step {self.current_step + 1}/{self.total_steps}")
        
        # Update title
        title = self.query_one("#step_title", Static)
        title.update(self._get_step_title())
        
        # Update content based on step
        if self.current_step == 0:
            # Provider Selection (Required)
            step_content.update(self._get_provider_content())
            step_note.update("[required-note]⚠️ This step is required[/required-note]")
            skip_btn.disabled = True
            
        elif self.current_step == 1:
            # Model Selection (Required)
            step_content.update(self._get_model_content())
            step_note.update("[required-note]⚠️ This step is required[/required-note]")
            skip_btn.disabled = True
            
        elif self.current_step == 2:
            # API Configuration (Required)
            step_content.update(self._get_api_content())
            step_note.update("[required-note]⚠️ This step is required[/required-note]")
            skip_btn.disabled = True
            
        elif self.current_step == 3:
            # Blip Character (Optional)
            step_content.update(self._get_blip_content())
            step_note.update("[optional-note]💡 This step is optional - you can skip and use default (axolotl)[/optional-note]")
            skip_btn.disabled = False
            
        elif self.current_step == 4:
            # Theme Selection (Optional)
            step_content.update(self._get_theme_content())
            step_note.update("[optional-note]💡 This step is optional - you can skip and use default (none)[/optional-note]")
            skip_btn.disabled = False
            
        elif self.current_step == 5:
            # Privacy Settings (Optional)
            step_content.update(self._get_privacy_content())
            step_note.update("[optional-note]💡 This step is optional - you can skip and use default (balanced)[/optional-note]")
            skip_btn.disabled = False
            
        elif self.current_step == 6:
            # Setup Complete
            step_content.update(self._get_complete_content())
            step_note.update("")
            continue_btn.label = "Launch Blonde CLI"
            skip_btn.disabled = True
            back_btn.disabled = True
        
        # Re-mount widgets for interactive steps
        if self.current_step in [0, 1, 2, 3, 4, 5]:
            self._mount_step_widgets()
    
    def _get_provider_content(self) -> str:
        """Get provider selection content"""
        return """
        [bold]Select AI Provider[/bold]
        
        Choose the AI provider you want to use with Blonde CLI:
        
        • [bold]OpenRouter[/bold] - Access multiple models from various providers
        • [bold]OpenAI[/bold] - Official OpenAI models (GPT-4, GPT-3.5)
        • [bold]Anthropic[/bold] - Claude models (Claude 3 Opus, Sonnet, Haiku)
        • [bold]Local[/bold] - Run models locally on your machine
        
        [dim]You can add more providers later in Settings.[/dim]
        """
    
    def _get_model_content(self) -> str:
        """Get model selection content"""
        return """
        [bold]Select Default Model[/bold]
        
        Choose the default model for your selected provider:
        
        [dim]Premium models offer better reasoning, while smaller models are faster.[/dim]
        """
    
    def _get_api_content(self) -> str:
        """Get API configuration content"""
        return """
        [bold]Configure API Access[/bold]
        
        Enter your API key to access the selected provider.
        
        [dim]Your API key will be stored locally and only used for AI requests.[/dim]
        """
    
    def _get_blip_content(self) -> str:
        """Get Blip character selection content"""
        return """
        [bold]Choose Your Blip Character[/bold]
        
        Blip is your digital companion that guides you through development.
        Choose a personality that fits your style!
        
        [dim]Default: Axolotl (friendly, playful, curious)[/dim]
        """
    
    def _get_theme_content(self) -> str:
        """Get theme selection content"""
        return """
        [bold]Choose UI Theme[/bold]
        
        Select the color theme for Blonde CLI interface:
        
        • [bold]None[/bold] - Default terminal colors
        • [bold]Auto[/bold] - Auto-detect terminal theme  
        • [bold]Light[/bold] - Optimized for light terminals
        • [bold]Dark[/bold] - Optimized for dark terminals
        
        [dim]Default: None theme (can be changed later)[/dim]
        """
    
    def _get_privacy_content(self) -> str:
        """Get privacy settings content"""
        return """
        [bold]Configure Privacy Settings[/bold]
        
        Choose how Blonde CLI handles your data:
        
        • [bold]Strict[/bold] - Maximum privacy, minimal data collection
        • [bold]Balanced[/bold] - Good balance of privacy and functionality
        • [bold]Permissive[/bold] - Enhanced features with more data usage
        
        [dim]Default: Balanced (recommended for most users)[/dim]
        """
    
    def _get_complete_content(self) -> str:
        """Get setup complete content"""
        config_summary = f"""
        [bold green]✓ Setup Complete![/bold green]
        
        [bold]Configuration Summary:[/bold]
        
        Provider: [cyan]{self.selected_provider}[/cyan]
        Model: [cyan]{self.custom_model or self.selected_model}[/cyan]
        API Key: [cyan]{'✓ Configured' if self.api_key else '✗ Not configured'}[/cyan]
        Blip Character: [cyan]{self.selected_blip_character}[/cyan]
        Theme: [cyan]{self.selected_theme}[/cyan]
        Privacy Mode: [cyan]{self.selected_privacy_mode}[/cyan]
        
        Configuration saved to: {CONFIG_FILE}
        
        Press [bold]Continue[/bold] to launch Blonde CLI, or [bold]Quit[/bold] to exit.
        """
        return config_summary
    
    def _mount_step_widgets(self) -> None:
        """Mount interactive widgets for current step"""
        # Clear existing widgets (except static content)
        step_container = self.query_one("#setup_container", Container)
        
        # Remove any existing interactive widgets
        for widget in step_container.children:
            if isinstance(widget, (Input, Select, RadioSet, Switch)) and widget.id not in ["step_indicator", "step_title", "step_content", "step_note"]:
                widget.remove()
        
        # Add widgets based on current step
        if self.current_step == 0:
            # Provider selection
            provider_options = [
                ("OpenRouter", "openrouter"),
                ("OpenAI", "openai"), 
                ("Anthropic", "anthropic"),
                ("Local (GGUF)", "local")
            ]
            provider_select = Select(options=provider_options, id="provider_select")
            provider_select.value = self.selected_provider
            step_container.mount(provider_select)
            
        elif self.current_step == 1:
            # Model selection
            model_options = self._get_model_options(self.selected_provider)
            model_select = Select(options=model_options, id="model_select")
            model_select.value = self.selected_model
            step_container.mount(model_select)
            
            # Custom model input
            custom_input = Input(
                placeholder="Or enter custom model (e.g., meta-llama/llama-3-70b)",
                value=self.custom_model,
                id="custom_model_input"
            )
            step_container.mount(custom_input)
            
        elif self.current_step == 2:
            # API configuration
            if self.selected_provider in ["openrouter", "openai", "anthropic"]:
                api_input = Input(
                    placeholder="Enter your API key",
                    password=True,
                    value=self.api_key,
                    id="api_key_input"
                )
                step_container.mount(api_input)
            else:
                # Local provider - model path
                path_input = Input(
                    placeholder="Path to local model file (optional)",
                    id="model_path_input"
                )
                step_container.mount(path_input)
            
            # Test connection button
            test_btn = Button("Test Connection", id="test_connection_btn")
            step_container.mount(test_btn)
            
        elif self.current_step == 3:
            # Blip character selection
            if BLIP_AVAILABLE:
                character_options = []
                characters = list_characters()
                for char_name in characters:
                    char = get_character(char_name)
                    if char:
                        character_options.append((f"{char_name.title()} - {char.description[:30]}...", char_name))
                
                blip_select = Select(options=character_options, id="blip_select")
                blip_select.value = self.selected_blip_character
                step_container.mount(blip_select)
                
                # Preview
                preview = Static(id="blip_preview", classes="blip-preview")
                step_container.mount(preview)
                self._update_blip_preview()
            else:
                note = Static("[dim]Blip characters not available - will use default[/dim]")
                step_container.mount(note)
                
        elif self.current_step == 4:
            # Theme selection
            theme_options = [
                ("None - Default terminal colors", "none"),
                ("Auto - Auto-detect theme", "auto"),
                ("Light - Optimized for light terminals", "light"),
                ("Dark - Optimized for dark terminals", "dark")
            ]
            theme_select = Select(options=theme_options, id="theme_select")
            theme_select.value = self.selected_theme
            step_container.mount(theme_select)
            
        elif self.current_step == 5:
            # Privacy settings
            privacy_options = [
                ("Strict - Maximum privacy", "strict"),
                ("Balanced - Recommended", "balanced"),
                ("Permissive - Enhanced features", "permissive")
            ]
            privacy_select = Select(options=privacy_options, id="privacy_select")
            privacy_select.value = self.selected_privacy_mode
            step_container.mount(privacy_select)
    
    def _get_model_options(self, provider: str) -> list:
        """Get model options for provider"""
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
    
    def _update_blip_preview(self) -> None:
        """Update Blip character preview"""
        try:
            blip_select = self.query_one("#blip_select", Select)
            preview = self.query_one("#blip_preview", Static)
            
            if blip_select and preview:
                character_name = blip_select.value or "axolotl"
                char = get_character(character_name)
                
                if char:
                    art = char.get_art("happy")
                    color = char.get_color("happy")
                    preview.update(f"[{color}]{art}[/{color}]\n[dim]{char.description}[/dim]")
        except:
            pass
    
    # Button handlers
    @on(Button.Pressed, "#continue_btn")
    def on_continue(self) -> None:
        """Handle continue button"""
        if self.current_step < 6:
            # Save current step data
            self._save_step_data()
            
            # Validate required steps
            if self.current_step < 3:  # First 3 steps are required
                if not self._validate_current_step():
                    return
            
            # Move to next step
            self.current_step += 1
            self._update_step()
        else:
            # Complete setup
            self._complete_setup()
    
    @on(Button.Pressed, "#back_btn")
    def on_back(self) -> None:
        """Handle back button"""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_step()
    
    @on(Button.Pressed, "#skip_btn")
    def on_skip(self) -> None:
        """Handle skip button"""
        if self.current_step < 6:
            self.current_step += 1
            self._update_step()
    
    @on(Button.Pressed, "#quit_btn")
    def on_quit(self) -> None:
        """Handle quit button"""
        self.exit()
    
    @on(Button.Pressed, "#test_connection_btn")
    def on_test_connection(self) -> None:
        """Handle test connection button"""
        self.notify("Connection testing coming soon!", severity="information")
    
    @on(Select.Changed, "#provider_select")
    def on_provider_changed(self, event: Select.Changed) -> None:
        """Handle provider change"""
        self.selected_provider = event.value
        # Update model options
        if self.current_step == 1:
            self._update_step()
    
    @on(Select.Changed, "#blip_select")
    def on_blip_changed(self, event: Select.Changed) -> None:
        """Handle Blip character change"""
        self.selected_blip_character = event.value
        self._update_blip_preview()
    
    def _save_step_data(self) -> None:
        """Save data from current step"""
        try:
            if self.current_step == 0:
                # Provider selection
                provider_select = self.query_one("#provider_select", Select)
                if provider_select:
                    self.selected_provider = provider_select.value
                    self.config_data["default_provider"] = self.selected_provider
                    
            elif self.current_step == 1:
                # Model selection
                model_select = self.query_one("#model_select", Select)
                custom_input = self.query_one("#custom_model_input", Input)
                if model_select:
                    self.selected_model = model_select.value
                if custom_input:
                    self.custom_model = custom_input.value.strip()
                    
            elif self.current_step == 2:
                # API configuration
                if self.selected_provider in ["openrouter", "openai", "anthropic"]:
                    api_input = self.query_one("#api_key_input", Input)
                    if api_input:
                        self.api_key = api_input.value.strip()
                        
            elif self.current_step == 3:
                # Blip character
                if BLIP_AVAILABLE:
                    blip_select = self.query_one("#blip_select", Select)
                    if blip_select:
                        self.selected_blip_character = blip_select.value
                    self.config_data["preferences"]["blip_character"] = self.selected_blip_character
                    
            elif self.current_step == 4:
                # Theme selection
                theme_select = self.query_one("#theme_select", Select)
                if theme_select:
                    self.selected_theme = theme_select.value
                    self.config_data["preferences"]["colors"] = self.selected_theme
                    
            elif self.current_step == 5:
                # Privacy settings
                privacy_select = self.query_one("#privacy_select", Select)
                if privacy_select:
                    self.selected_privacy_mode = privacy_select.value
                    self.config_data["preferences"]["privacy_mode"] = self.selected_privacy_mode
                    
        except:
            pass
    
    def _validate_current_step(self) -> bool:
        """Validate current step data"""
        if self.current_step == 0:
            # Provider must be selected
            if not self.selected_provider:
                self.notify("Please select a provider", severity="error")
                return False
                
        elif self.current_step == 1:
            # Model must be selected
            if not self.selected_model and not self.custom_model:
                self.notify("Please select or enter a model", severity="error")
                return False
                
        elif self.current_step == 2:
            # API key required for cloud providers
            if self.selected_provider in ["openrouter", "openai", "anthropic"]:
                if not self.api_key:
                    self.notify("API key is required for cloud providers", severity="error")
                    return False
                    
        return True
    
    def _complete_setup(self) -> None:
        """Complete setup and save configuration"""
        try:
            # Build final configuration
            provider_config = {
                "model": self.custom_model if self.custom_model else self.selected_model
            }
            
            # Save API key securely using keyring
            if self.api_key:
                from tui.utils import save_api_key
                key_name = f"{self.selected_provider.upper()}_API_KEY"
                save_api_key(key_name, self.api_key)
            
            self.config_data["providers"][self.selected_provider] = provider_config
            self.config_data["setup_completed"] = True
            self.config_data["default_provider"] = self.selected_provider
            
            # Save configuration
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            
            self.notify("Setup completed successfully!", severity="success")
            
            # Exit to allow main app to launch
            self.exit()
            
        except Exception as e:
            self.notify(f"Error saving configuration: {e}", severity="error")
    
    def action_continue(self) -> None:
        """Action for Enter key"""
        self.on_continue()
    
    def action_skip_step(self) -> None:
        """Action for S key"""
        self.on_skip()


if __name__ == "__main__":
    wizard = EnhancedSetupWizard()
    wizard.run()