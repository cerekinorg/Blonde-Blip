"""
Enhanced Settings Modal - Comprehensive settings management
Tabs for Session, Model & Provider, Blip Character, Preferences, Privacy
"""

from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.widgets import (
    Static, Input, Button, Select, Tabs, Tab,
    ContentSwitcher, DataTable, Label, Switch
)
from textual.containers import Horizontal, Vertical, Container
from textual import on
from textual.reactive import reactive
from pathlib import Path
import json
from typing import Optional, Dict, List

try:
    from tui.blip_manager import get_blip_manager
    from tui.session_manager import get_session_manager
    from tui.provider_manager import ProviderManager
    MANAGERS_AVAILABLE = True
except ImportError:
    try:
        from blip_manager import get_blip_manager
        from session_manager import get_session_manager
        from provider_manager import ProviderManager
        MANAGERS_AVAILABLE = True
    except ImportError:
        MANAGERS_AVAILABLE = False

CONFIG_DIR = Path.home() / ".blonde"
CONFIG_FILE = CONFIG_DIR / "config.json"


class EnhancedSettings(ModalScreen[None]):
    """Comprehensive settings modal with multiple tabs"""
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
        ("ctrl+s", "save_settings", "Save"),
        ("ctrl+tab", "next_tab", "Next Tab"),
        ("ctrl+shift+tab", "prev_tab", "Prev Tab")
    ]
    
    def __init__(self, config_path: Path = None):
        super().__init__()
        self.config_path = config_path or CONFIG_FILE
        self.config = self._load_config()
        self.current_tab = "session"
        
        # Initialize managers
        self.blip_manager = None
        self.session_manager = None
        self.provider_manager = None
        
        if MANAGERS_AVAILABLE:
            self.blip_manager = get_blip_manager()
            self.session_manager = get_session_manager()
            self.provider_manager = ProviderManager()
    
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "version": "1.0.0",
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
                "colors": "auto"
            }
        }
    
    def compose(self) -> ComposeResult:
        """Compose settings modal"""
        with Container(id="settings_container"):
            yield Tabs(
                Tab("Session", id="session"),
                Tab("Model & Provider", id="model_provider"),
                Tab("Blip Character", id="blip"),
                Tab("Preferences", id="preferences"),
                Tab("Privacy", id="privacy")
            )
            
            with ContentSwitcher():
                self._compose_session_tab()
                self._compose_model_provider_tab()
                self._compose_blip_tab()
                self._compose_preferences_tab()
                self._compose_privacy_tab()
            
            with Horizontal(id="button_row"):
                yield Button("Save (Ctrl+S)", id="save_btn", variant="primary")
                yield Button("Cancel (Esc)", id="cancel_btn")
    
    def _compose_session_tab(self):
        """Compose session management tab"""
        with Vertical(id="session_tab"):
            yield Static("[bold]Session Management[/bold]")
            yield Static()
            
            # New Session
            yield Static("Create New Session:")
            yield Input(
                placeholder="Session name (optional)",
                id="new_session_name"
            )
            yield Button("Create Session", id="create_session_btn")
            
            yield Static()  # Spacer
            
            # Switch Session
            yield Static("Switch to Session:")
            yield DataTable(id="sessions_table")
            yield Button("Switch to Selected", id="switch_session_btn")
            
            yield Static()  # Spacer
            
            # Delete Session
            yield Button("Delete Selected Session", id="delete_session_btn", variant="error")
    
    def _compose_model_provider_tab(self):
        """Compose model and provider selection tab"""
        with Vertical(id="model_provider_tab"):
            yield Static("[bold]AI Provider & Model[/bold]")
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
                options=[opt for opt in provider_options],
                id="provider_select"
            )
            
            # Model Selection
            yield Static("Model:")
            model_options = self._get_model_options("openrouter")
            yield Select(
                options=[opt for opt in model_options],
                id="model_select"
            )
            
            # Custom Model
            yield Static("[dim]Or specify custom model:[/dim]")
            yield Input(
                placeholder="e.g., meta-llama/llama-3-70b",
                id="custom_model_input"
            )
            
            yield Static()  # Spacer
            
            # Test Connection
            yield Button("Test Connection", id="test_connection_btn")
            yield Button("Switch Provider/Model", id="switch_provider_btn", variant="primary")
            
            yield Static()  # Spacer
            
            # Quick Switch Section (NEW)
            yield Static("[bold]Quick Configuration[/bold]")
            yield Static("Add new provider configurations:")
            yield Button("Add OpenRouter Config", id="add_openrouter_btn")
            yield Button("Add OpenAI Config", id="add_openai_btn")
            yield Button("Add Anthropic Config", id="add_anthropic_btn")
            yield Button("Add Local Model", id="add_local_btn")
            
            yield Static()  # Spacer
            
            # Current Status
            yield Static("Current Status:")
            yield Static(id="current_status_display")
    
    def _compose_blip_tab(self):
        """Compose Blip character selection tab"""
        with Vertical(id="blip_tab"):
            yield Static("[bold]Blip Character[/bold]")
            yield Static()
            
            # Character Selection
            yield Static("Choose Your Blip:")
            yield Static(id="blip_preview")
            
            character_options = [
                ("🦎 Axolotl - Friendly, playful, curious", "axolotl"),
                ("✨ Wisp - Ethereal, mysterious, glowing", "wisp"),
                ("🌑 Inkling - Focused, meticulous, shy", "inkling"),
                ("🌱 Sprout - Cheerful, optimistic, growth-focused", "sprout")
            ]
            yield Select(
                values=[opt for opt in character_options],
                id="blip_character_select"
            )
            
            yield Static()  # Spacer
            
            # Character Info
            yield Static(id="character_info")
            
            yield Static()  # Spacer
            
            # Animation Speed
            yield Static("Animation Speed:")
            yield Static("[dim]Faster: 0.1s | Normal: 0.3s | Slower: 0.5s[/dim]")
            yield Input(
                placeholder="0.3",
                id="animation_speed_input",
                type="float"
            )
    
    def _compose_preferences_tab(self):
        """Compose user preferences tab"""
        preferences = self.config.get("preferences", {})
        
        with Vertical(id="preferences_tab"):
            yield Static("[bold]Preferences[/bold]")
            yield Static()
            
            # Display Options
            yield Static("Display Options:")
            yield Switch(
                value=preferences.get('show_blip', True),
                label="Show Blip",
                id="show_blip_switch"
            )
            yield Switch(
                value=preferences.get('show_tips', True),
                label="Show Tips",
                id="show_tips_switch"
            )
            yield Switch(
                value=preferences.get('show_agent_thinking', True),
                label="Show Agent Thinking",
                id="show_thinking_switch"
            )
            yield Switch(
                value=preferences.get('show_diff', True),
                label="Show Diff (auto on file edits)",
                id="show_diff_switch"
            )
            
            yield Static()  # Spacer
            
            # Response Options
            yield Static("Response Options:")
            yield Switch(
                value=preferences.get('stream_responses', True),
                label="Stream Responses",
                id="stream_responses_switch"
            )
            yield Switch(
                value=preferences.get('autosave_files', True),
                label="Autosave Files (2s debounce)",
                id="autosave_files_switch"
            )
            
            yield Static()  # Spacer
            
            # Theme
            yield Static("Theme:")
            theme_options = [
                ("Auto", "auto"),
                ("Light", "light"),
                ("Dark", "dark"),
                ("None", "none")
            ]
            yield Select(
                values=[opt for opt in theme_options],
                id="theme_select"
            )
    
    def _compose_privacy_tab(self):
        """Compose privacy settings tab"""
        preferences = self.config.get("preferences", {})
        
        with Vertical(id="privacy_tab"):
            yield Static("[bold]Privacy[/bold]")
            yield Static()
            
            # Privacy Mode
            yield Static("Privacy Mode:")
            mode_options = [
                ("Strict - Minimal data retention", "strict"),
                ("Balanced - Recommended", "balanced"),
                ("Permissive - Full functionality", "permissive")
            ]
            yield Select(
                values=[opt for opt in mode_options],
                id="privacy_mode_select"
            )
            
            yield Static()  # Spacer
            
            # Data Management
            yield Static("Data Management:")
            yield Button("Clear Chat History", id="clear_history_btn")
            yield Button("Clear Session Data", id="clear_sessions_btn", variant="error")
            yield Button("Export Settings", id="export_settings_btn")
            yield Button("Import Settings", id="import_settings_btn")
            
            yield Static()  # Spacer
            
            yield Static("[dim]Settings exported from Blonde CLI are safe to share.[/dim]")
            yield Static("[dim]They contain preferences only, no chat history or session data.[/dim]")
    
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
        """Initialize settings on mount"""
        # Set current values from config
        
        # Provider & Model
        provider_select = self.query_one("#provider_select", Select)
        if provider_select:
            provider_select.value = self.config.get("default_provider", "openrouter")
        
        model_select = self.query_one("#model_select", Select)
        if model_select:
            providers_config = self.config.get("providers", {})
            provider_data = providers_config.get(self.config.get("default_provider", "openrouter"), {})
            model_select.value = provider_data.get('model', 'openai/gpt-4')
        
        # Blip Character
        preferences = self.config.get("preferences", {})
        blip_select = self.query_one("#blip_character_select", Select)
        if blip_select:
            blip_select.value = preferences.get("blip_character", "axolotl")
        
        # Animation Speed
        anim_input = self.query_one("#animation_speed_input", Input)
        if anim_input:
            anim_input.value = str(preferences.get('blip_animation_speed', 0.3))
        
        # Theme
        theme_select = self.query_one("#theme_select", Select)
        if theme_select:
            theme_select.value = preferences.get('colors', 'auto')
        
        # Privacy Mode
        privacy_select = self.query_one("#privacy_mode_select", Select)
        if privacy_select:
            privacy_select.value = preferences.get('privacy_mode', 'balanced')
        
        # Load sessions list
        self._load_sessions_list()
        
        # Update Blip preview
        self._update_blip_preview()
    
    def _load_sessions_list(self):
        """Load sessions into table"""
        if not self.session_manager:
            return
        
        sessions_table = self.query_one("#sessions_table", DataTable)
        if not sessions_table:
            return
        
        sessions_table.clear()
        sessions_table.add_column("Name", width=30)
        sessions_table.add_column("Created", width=20)
        sessions_table.add_column("Provider", width=15)
        
        sessions = self.session_manager.list_sessions()
        for session in sessions:
            sessions_table.add_row(
                session['name'],
                session['created_at'][:19],
                session['provider']
            )
    
    def _update_blip_preview(self):
        """Update Blip character preview"""
        if not self.blip_manager:
            return
        
        blip_select = self.query_one("#blip_character_select", Select)
        if not blip_select:
            return
        
        character_name = blip_select.value or "axolotl"
        blip_select.value = character_name
        
        # Switch to preview character (without saving)
        character = blip_select.value
        
        # Display preview
        preview = self.query_one("#blip_preview", Static)
        info = self.query_one("#character_info", Static)
        
        # Temporarily get art from selected character
        from tui.blip_characters import get_character
        char = get_character(character)
        
        if char:
            art = char.get_art("happy")
            color = char.get_color("happy")
            preview.update(f"[{color}]{art}[/{color}]")
            info.update(f"[dim]{char.description}\n\nPersonality: {char.personality}[/dim]")
    
    def action_next_tab(self) -> None:
        """Move to next tab"""
        tabs = self.query_one(Tabs)
        tabs.active = (tabs.active + 1) % len(tabs)
    
    def action_prev_tab(self) -> None:
        """Move to previous tab"""
        tabs = self.query_one(Tabs)
        tabs.active = (tabs.active - 1) % len(tabs)
    
    def action_save_settings(self) -> None:
        """Save all settings"""
        try:
            # Get values from all tabs
            provider_select = self.query_one("#provider_select", Select)
            model_select = self.query_one("#model_select", Select)
            custom_model = self.query_one("#custom_model_input", Input)
            blip_select = self.query_one("#blip_character_select", Select)
            anim_input = self.query_one("#animation_speed_input", Input)
            theme_select = self.query_one("#theme_select", Select)
            privacy_select = self.query_one("#privacy_mode_select", Select)
            show_blip = self.query_one("#show_blip_switch", Switch)
            show_tips = self.query_one("#show_tips_switch", Switch)
            show_thinking = self.query_one("#show_thinking_switch", Switch)
            show_diff = self.query_one("#show_diff_switch", Switch)
            stream_responses = self.query_one("#stream_responses_switch", Switch)
            autosave_files = self.query_one("#autosave_files_switch", Switch)
            
            # Build updated config
            self.config['default_provider'] = provider_select.value
            self.config['providers'][provider_select.value] = {
                'model': custom_model.value.strip() if custom_model.value.strip() else model_select.value
            }
            
            # Preferences
            self.config['preferences']['blip_character'] = blip_select.value
            self.config['preferences']['blip_animation_speed'] = float(anim_input.value or 0.3)
            self.config['preferences']['colors'] = theme_select.value
            self.config['preferences']['privacy_mode'] = privacy_select.value
            self.config['preferences']['show_blip'] = show_blip.value
            self.config['preferences']['show_tips'] = show_tips.value
            self.config['preferences']['show_agent_thinking'] = show_thinking.value
            self.config['preferences']['show_diff'] = show_diff.value
            self.config['preferences']['stream_responses'] = stream_responses.value
            self.config['preferences']['autosave_files'] = autosave_files.value
            
            # Save to file
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            # Apply changes
            if self.blip_manager:
                self.blip_manager.switch_character(blip_select.value)
            
            self.notify("Settings saved successfully!", severity="information")
            self.dismiss(None)
            
        except Exception as e:
            self.notify(f"Error saving settings: {e}", severity="error")
    
    @on(Button.Pressed, "#cancel_btn")
    def on_cancel(self) -> None:
        """Handle cancel button"""
        self.dismiss(None)
    
    @on(Button.Pressed, "#create_session_btn")
    def on_create_session(self) -> None:
        """Handle create session button"""
        name_input = self.query_one("#new_session_name", Input)
        session_name = name_input.value.strip() if name_input else ""
        
        if self.session_manager:
            session_id = self.session_manager.create_session(name=session_name)
            self.notify(f"Created new session: {session_name}", severity="information")
    
    @on(Button.Pressed, "#switch_session_btn")
    def on_switch_session(self) -> None:
        """Handle switch session button"""
        sessions_table = self.query_one("#sessions_table", DataTable)
        if not sessions_table:
            return
        
        # Get selected row
        row_key = sessions_table.cursor_row
        if row_key is not None:
            # Switch to selected session
            self.notify("Session switching coming soon!", severity="information")
    
    @on(Button.Pressed, "#delete_session_btn")
    def on_delete_session(self) -> None:
        """Handle delete session button"""
        self.notify("Session deletion coming soon!", severity="information")
    
    @on(Button.Pressed, "#switch_provider_btn")
    def on_switch_provider(self) -> None:
        """Handle switch provider button"""
        if self.provider_manager:
            provider_select = self.query_one("#provider_select", Select)
            model_select = self.query_one("#model_select", Select)
            custom_model = self.query_one("#custom_model_input", Input)
            
            final_model = custom_model.value.strip() if custom_model.value.strip() else model_select.value
            
            success = self.provider_manager.switch_provider(provider_select.value)
            if success:
                self.notify(f"Switched to {provider_select.value}/{final_model}", severity="information")
    
    @on(Button.Pressed, "#test_connection_btn")
    def on_test_connection(self) -> None:
        """Handle test connection button"""
        self.notify("Connection testing coming soon!", severity="information")
    
    @on(Button.Pressed, "#blip_character_select")
    def on_blip_character_changed(self, event) -> None:
        """Handle Blip character selection change"""
        self._update_blip_preview()
    
    @on(Button.Pressed, "#clear_history_btn")
    def on_clear_history(self) -> None:
        """Handle clear history button"""
        self.notify("Clear history coming soon!", severity="information")
    
    @on(Button.Pressed, "#clear_sessions_btn")
    def on_clear_sessions(self) -> None:
        """Handle clear sessions button"""
        self.notify("Clear sessions coming soon!", severity="information")
    
    @on(Button.Pressed, "#export_settings_btn")
    def on_export_settings(self) -> None:
        """Handle export settings button"""
        self.notify("Export settings coming soon!", severity="information")
    
    @on(Button.Pressed, "#import_settings_btn")
    def on_import_settings(self) -> None:
        """Handle import settings button"""
        self.notify("Import settings coming soon!", severity="information")
    
    # Quick Configuration Button Handlers (NEW)
    @on(Button.Pressed, "#add_openrouter_btn")
    def on_add_openrouter_config(self) -> None:
        """Add OpenRouter configuration dialog"""
        self.push_screen(ProviderConfigDialog("openrouter"), self._on_provider_config_result)
    
    @on(Button.Pressed, "#add_openai_btn")
    def on_add_openai_config(self) -> None:
        """Add OpenAI configuration dialog"""
        self.push_screen(ProviderConfigDialog("openai"), self._on_provider_config_result)
    
    @on(Button.Pressed, "#add_anthropic_btn")
    def on_add_anthropic_config(self) -> None:
        """Add Anthropic configuration dialog"""
        self.push_screen(ProviderConfigDialog("anthropic"), self._on_provider_config_result)
    
    @on(Button.Pressed, "#add_local_btn")
    def on_add_local_config(self) -> None:
        """Add Local model configuration dialog"""
        self.push_screen(ProviderConfigDialog("local"), self._on_provider_config_result)
    
    def _on_provider_config_result(self, result: Optional[Dict[str, str]]) -> None:
        """Handle provider configuration dialog result"""
        if result:
            provider_name = result['provider']
            api_key = result['api_key']
            model = result['model']
            custom_model = result['custom_model']
            
            # Save configuration
            if provider_name not in self.config['providers']:
                self.config['providers'][provider_name] = {}
            
            if api_key:
                self.config['providers'][provider_name]['api_key'] = api_key
            
            final_model = custom_model if custom_model else model
            if final_model:
                self.config['providers'][provider_name]['model'] = final_model
            
            # Update current provider if this is the first config
            if len(self.config['providers']) == 1:
                self.config['default_provider'] = provider_name
            
            # Save to file
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            self.notify(f"Added {provider_name} configuration successfully!", severity="information")
            
            # Update current status display
            self._update_current_status()
    
    def _update_current_status(self) -> None:
        """Update current status display"""
        try:
            status_display = self.query_one("#current_status_display", Static)
            provider = self.config.get('default_provider', 'openrouter')
            providers = self.config.get('providers', {})
            model = providers.get(provider, {}).get('model', 'openai/gpt-4')
            
            status_text = f"Provider: [bold cyan]{provider}[/bold cyan]\n"
            status_text += f"Model: [bold cyan]{model}[/bold cyan]\n"
            status_text += f"Configured Providers: [bold]{len(providers)}[/bold]"
            
            status_display.update(status_text)
        except:
            pass


class ProviderConfigDialog(ModalScreen[Dict[str, str]]):
    """Dialog for adding provider configuration"""
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel")
    ]
    
    def __init__(self, provider_name: str):
        super().__init__()
        self.provider_name = provider_name
    
    def compose(self) -> ComposeResult:
        """Compose provider configuration dialog"""
        with Container():
            yield Static(f"[bold]Add {self.provider_name.title()} Configuration[/bold]")
            yield Static()
            
            # API Key (for cloud providers)
            if self.provider_name in ["openrouter", "openai", "anthropic"]:
                yield Static("API Key:")
                yield Input(
                    placeholder="Enter API key",
                    password=True,
                    id="api_key"
                )
                yield Static()
            
            # Model Selection
            yield Static("Model:")
            model_options = self._get_model_options()
            yield Select(
                options=model_options,
                id="model_select"
            )
            
            # Custom Model (optional)
            yield Static("[dim]Custom Model (optional):[/dim]")
            yield Input(
                placeholder="e.g., meta-llama/llama-3-70b",
                id="custom_model"
            )
            yield Static()
            
            # Buttons
            with Horizontal():
                yield Button("Save", id="save_btn", variant="primary")
                yield Button("Cancel", id="cancel_btn")
    
    def _get_model_options(self) -> List[tuple]:
        """Get model options for this provider"""
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
        
        return models_by_provider.get(self.provider_name, [])
    
    @on(Button.Pressed, "#save_btn")
    def on_save(self) -> None:
        """Handle save button"""
        api_key = ""
        model = ""
        custom_model = ""
        
        # Get API key if present
        if self.provider_name in ["openrouter", "openai", "anthropic"]:
            try:
                api_key_input = self.query_one("#api_key", Input)
                api_key = api_key_input.value.strip()
            except:
                pass
        
        # Get model selection
        try:
            model_select = self.query_one("#model_select", Select)
            model = str(model_select.value) if model_select.value else ""
        except:
            pass
        
        # Get custom model
        try:
            custom_model_input = self.query_one("#custom_model", Input)
            custom_model = custom_model_input.value.strip()
        except:
            pass
        
        # Validate required fields
        if self.provider_name in ["openrouter", "openai", "anthropic"] and not api_key:
            self.notify("API key is required for cloud providers", severity="error")
            return
        
        if not model and not custom_model:
            self.notify("Model selection is required", severity="error")
            return
        
        # Return result
        result = {
            'provider': self.provider_name,
            'api_key': api_key,
            'model': model,
            'custom_model': custom_model
        }
        
        self.dismiss(result)
    
    @on(Button.Pressed, "#cancel_btn")
    def on_cancel(self) -> None:
        """Handle cancel button"""
        self.dismiss(None)


if __name__ == "__main__":
    # Demo enhanced settings
    from textual.app import App
    
    class DemoApp(App):
        def compose(self):
            yield Button("Open Settings", id="open_settings")
        
        def on_button_pressed(self, event):
            self.push_screen(EnhancedSettings())
    
    app = DemoApp()
    app.run()
