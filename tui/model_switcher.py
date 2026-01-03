"""
Model/Provider Switcher - Quick modal for switching AI models
Provides dropdowns for provider and model selection with custom input
"""

from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.widgets import (
    Static, Input, Button, Select, Label, LoadingIndicator
)
from textual.containers import Vertical, Container
from textual import on
from typing import Optional, List

try:
    from tui.provider_manager import ProviderManager
    MANAGERS_AVAILABLE = True
except ImportError:
    try:
        from provider_manager import ProviderManager
        MANAGERS_AVAILABLE = True
    except ImportError:
        MANAGERS_AVAILABLE = False


class ModelSwitcher(ModalScreen[Optional[dict]]):
    """Modal for switching provider and model"""
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
        ("enter", "confirm_switch", "Switch")
    ]
    
    def __init__(self):
        super().__init__()
        self.provider_manager = None
        self.is_testing = False
        
        if MANAGERS_AVAILABLE:
            self.provider_manager = ProviderManager()
        
        self.current_provider = ""
        self.current_model = ""
        self.custom_model = ""
        self.test_result = ""
    
    def compose(self) -> ComposeResult:
        """Compose model switcher modal"""
        with Container(id="switcher_container"):
            yield Static("[bold]Switch AI Provider & Model[/bold]")
            yield Static()
            
            # Provider Selection
            yield Static("Provider:")
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
            
            # Current Provider Display
            yield Static(id="current_provider_display")
            
            yield Static()  # Spacer
            
            # Model Selection
            yield Static("Model:")
            model_options = self._get_model_options("openrouter")
            yield Select(
                values=[opt for opt in model_options],
                id="model_select"
            )
            
            # Custom Model Input
            yield Static("[dim]Or specify custom model:[/dim]")
            yield Input(
                placeholder="e.g., meta-llama/llama-3-70b",
                id="custom_model_input"
            )
            
            # Current Model Display
            yield Static(id="current_model_display")
            
            yield Static()  # Spacer
            
            # Test Result
            yield Static(id="test_result")
            
            yield Static()  # Spacer
            
            # Actions
            yield Button("Test Connection", id="test_btn")
            yield Button("Switch (Enter)", id="switch_btn", variant="primary")
            yield Button("Cancel (Esc)", id="cancel_btn")
    
    def _get_model_options(self, provider: str) -> List[tuple]:
        """Get available models for a provider"""
        models_by_provider = {
            "openrouter": [
                ("GPT-4", "openai/gpt-4"),
                ("GPT-4 Turbo", "openai/gpt-4-turbo"),
                ("GPT-3.5 Turbo", "openai/gpt-3.5-turbo"),
                ("Claude 3 Opus", "anthropic/claude-3-opus-20240229"),
                ("Claude 3 Sonnet", "anthropic/claude-3-sonnet-20240229"),
                ("Mistral Large", "mistralai/mistral-large"),
                ("Gemini Pro", "google/gemini-pro"),
                ("Llama 3 70B", "meta-llama/llama-3-70b-instruct")
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
                ("Llama 2 7B", "TheBloke/Llama-2-7B-GGUF"),
                ("Llama 3 8B", "TheBloke/Llama-3-8B-GGUF")
            ]
        }
        
        return models_by_provider.get(provider, [])
    
    def on_mount(self) -> None:
        """Initialize on mount"""
        if not self.provider_manager:
            return
        
        # Get current provider
        current = self.provider_manager.get_current_provider()
        if current:
            self.current_provider = current.name
            self.current_model = current.model
            
            # Set provider selector
            provider_select = self.query_one("#provider_select", Select)
            if provider_select:
                provider_select.value = self.current_provider
            
            # Update model options
            self._update_model_options(self.current_provider)
            
            # Set model selector
            model_select = self.query_one("#model_select", Select)
            if model_select:
                model_select.value = self.current_model
            
            # Update displays
            self._update_displays()
    
    def _update_model_options(self, provider: str):
        """Update model options based on provider"""
        model_select = self.query_one("#model_select", Select)
        if not model_select:
            return
        
        model_select.clear_options()
        model_options = self._get_model_options(provider)
        model_select.add_options(model_options)
    
    def _update_displays(self):
        """Update current provider/model displays"""
        provider_display = self.query_one("#current_provider_display", Static)
        if provider_display:
            provider_display.update(f"[dim]Current: [cyan]{self.current_provider}[/cyan][/dim]")
        
        model_display = self.query_one("#current_model_display", Static)
        if model_display:
            model_display.update(f"[dim]Current: [cyan]{self.current_model}[/cyan][/dim]")
    
    def _update_test_result(self, message: str, severity: str = "information"):
        """Update test result display"""
        test_result = self.query_one("#test_result", Static)
        if not test_result:
            return
        
        colors = {
            "success": "bright_green",
            "error": "bright_red",
            "information": "cyan"
        }
        color = colors.get(severity, "white")
        test_result.update(f"[{color}]{message}[/{color}]")
    
    @on(Select.Changed, "#provider_select")
    def on_provider_changed(self, event: Select.Changed) -> None:
        """Handle provider change"""
        self.current_provider = event.value
        
        # Update model options
        self._update_model_options(self.current_provider)
        
        # Set default model
        model_select = self.query_one("#model_select", Select)
        if model_select and model_select.options:
            model_select.value = model_select.options[0][1]
            self.current_model = model_select.value
    
    @on(Select.Changed, "#model_select")
    def on_model_changed(self, event: Select.Changed) -> None:
        """Handle model change"""
        self.current_model = event.value
    
    @on(Input.Changed, "#custom_model_input")
    def on_custom_model_changed(self, event: Input.Changed) -> None:
        """Handle custom model input"""
        self.custom_model = event.value.strip()
    
    @on(Button.Pressed, "#test_btn")
    def on_test(self) -> None:
        """Handle test connection button"""
        if not self.provider_manager or self.is_testing:
            return
        
        self.is_testing = True
        self._update_test_result("Testing connection...", "information")
        
        # Determine final model
        final_model = self.custom_model if self.custom_model else self.current_model
        
        # Test connection
        try:
            success = self.provider_manager.test_provider(self.current_provider)
            
            if success:
                self._update_test_result(f"✓ Connection successful with {final_model}!", "success")
            else:
                self._update_test_result(f"✗ Connection failed", "error")
        except Exception as e:
            self._update_test_result(f"✗ Error: {e}", "error")
        finally:
            self.is_testing = False
    
    @on(Button.Pressed, "#switch_btn")
    def on_switch(self) -> None:
        """Handle switch button"""
        if not self.provider_manager:
            self.dismiss(None)
            return
        
        # Determine final model
        final_model = self.custom_model if self.custom_model else self.current_model
        
        # Switch provider
        success = self.provider_manager.switch_provider(self.current_provider)
        
        if success:
            # Update model in provider config
            if self.provider_manager.current_provider:
                self.provider_manager.current_provider.model = final_model
                self.provider_manager._save_config()
            
            self.dismiss({
                "provider": self.current_provider,
                "model": final_model
            })
        else:
            self._update_test_result("Failed to switch provider", "error")
    
    @on(Button.Pressed, "#cancel_btn")
    def on_cancel(self) -> None:
        """Handle cancel button"""
        self.dismiss(None)
    
    def action_confirm_switch(self) -> None:
        """Action: Switch (triggered by Enter)"""
        self.on_switch()


def show_model_switcher():
    """
    Show model switcher modal
    
    Returns:
        Dict with provider and model if switched, None if cancelled
    """
    return ModelSwitcher()


if __name__ == "__main__":
    # Demo model switcher
    from textual.app import App
    
    class DemoApp(App):
        def compose(self):
            yield Button("Open Model Switcher", id="open_switcher")
        
        def on_button_pressed(self, event):
            result = self.push_screen(ModelSwitcher())
            if result:
                print(f"Switched to: {result}")
    
    app = DemoApp()
    app.run()
