"""
Unified Work Panel - Consolidated with new core systems
Center panel with Chat/Editor modes, plus all Task 5 enhancements
"""

from textual.containers import Vertical, Horizontal, Container
from textual.widgets import Static, Input, Button, ProgressBar, RichLog
from textual import on
from textual.reactive import reactive
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import new core systems
from tui.core import (
    get_config_manager,
    get_session_manager,
    get_provider_manager,
    get_agent_team
)

try:
    from tui.chat_view import ChatView
    from tui.editor_view import EditorView
    VIEWS_AVAILABLE = True
except ImportError:
    VIEWS_AVAILABLE = False


class UnifiedWorkPanel(Vertical):
    """Unified work panel with all Task 5 enhancements"""

    MODES = ["chat", "editor", "development"]
    border_title = "Workspace"

    # Reactive state
    current_mode = reactive("chat")
    development_mode = reactive(False)
    agent_status = reactive("")
    context_usage = reactive({"tokens": 0, "percentage": 0.0})
    session_cost = reactive(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize new core systems
        self.config = get_config_manager()
        self.session_mgr = get_session_manager()
        self.provider_mgr = get_provider_manager()
        self.agent_team = get_agent_team()

        # UI components
        self.chat_view = None
        self.editor_view = None
        self.rich_log = None

        # Mode indicators
        self.mode_label = None
        self.agent_status_label = None
        self.context_label = None
        self.cost_label = None

    def compose(self):
        """Compose unified work panel"""
        # Header with mode info
        with Container(id="work_panel_header"):
            yield Static(f"Mode: {self.current_mode.upper()}", id="mode_display")

        # Mode toggle buttons
        with Horizontal(id="mode_buttons"):
            yield Button("Chat", id="btn_chat", variant="primary")
            yield Button("Editor", id="btn_editor")
            yield Button("Development", id="btn_development")

        # Agent status and context info
        with Horizontal(id="info_row"):
            yield Static("Agent: Ready", id="agent_status")
            yield Static("Context: 0 tokens (0.0%)", id="context_display")
            yield Static("Cost: $0.0000", id="cost_display")

        # Chat/Editor view
        if VIEWS_AVAILABLE:
            if self.current_mode in ["chat", "development"]:
                self.chat_view = ChatView()
                yield self.chat_view
            else:
                self.editor_view = EditorView()
                yield self.editor_view
        else:
            yield RichLog(id="rich_log")

        # Provider/Model info
        with Horizontal(id="provider_info"):
            provider = self.provider_mgr.current_provider()
            model = self.provider_mgr.current_model()
            yield Static(f"Provider: {provider}", id="provider_display")
            yield Static(f"Model: {model}", id="model_display")

    def on_mount(self):
        """Initialize on mount"""
        self.border_title = f"Workspace ({self.current_mode.upper()})"
        self._update_mode_display()
        self._update_context_display()
        self._update_cost_display()

    def _update_mode_display(self):
        """Update mode display"""
        try:
            mode_label = self.query_one("#mode_display", Static)
            if mode_label:
                mode_text = self.current_mode.upper()
                if self.development_mode:
                    mode_text += " (DEV)"
                mode_label.update(f"Mode: {mode_text}")
        except:
            pass

    def _update_context_display(self):
        """Update context usage display"""
        try:
            context_label = self.query_one("#context_display", Static)
            if context_label:
                tokens = self.context_usage["tokens"]
                percentage = self.context_usage["percentage"]
                context_label.update(f"Context: {tokens:,} tokens ({percentage:.1f}%)")
        except:
            pass

    def _update_cost_display(self):
        """Update cost display"""
        try:
            cost_label = self.query_one("#cost_display", Static)
            if cost_label:
                cost_label.update(f"Cost: ${self.session_cost:.4f}")
        except:
            pass

    @on(Button.Pressed, "#btn_chat")
    def on_chat_button(self):
        """Switch to chat mode"""
        self.current_mode = "chat"
        self.border_title = "Workspace (CHAT)"
        self._update_mode_display()
        self._switch_view("chat")

    @on(Button.Pressed, "#btn_editor")
    def on_editor_button(self):
        """Switch to editor mode"""
        self.current_mode = "editor"
        self.border_title = "Workspace (EDITOR)"
        self._update_mode_display()
        self._switch_view("editor")

    @on(Button.Pressed, "#btn_development")
    def on_development_button(self):
        """Toggle development mode"""
        self.development_mode = not self.development_mode

        if self.development_mode:
            self.border_title = "Workspace (DEVELOPMENT)"
            self.show_agent_status("Development mode enabled - Multi-agent active")
        else:
            if self.current_mode == "chat":
                self.border_title = "Workspace (CHAT)"
            else:
                self.border_title = "Workspace (EDITOR)"
            self.show_agent_status("Development mode disabled - Single agent active")

        self._update_mode_display()

    def _switch_view(self, mode: str):
        """Switch between chat and editor views"""
        if not VIEWS_AVAILABLE:
            return

        # Remove current view
        if self.chat_view and self.chat_view in self.children:
            self.chat_view.remove()
        if self.editor_view and self.editor_view in self.children:
            self.editor_view.remove()

        # Add new view
        if mode == "chat":
            self.chat_view = ChatView()
            self.mount(self.chat_view, before=self.children[0] if self.children else None)
        elif mode == "editor":
            self.editor_view = EditorView()
            self.mount(self.editor_view, before=self.children[0] if self.children else None)

    def show_agent_status(self, status: str):
        """Show agent status"""
        try:
            agent_label = self.query_one("#agent_status", Static)
            if agent_label:
                # Truncate if too long
                if len(status) > 50:
                    status = status[:47] + "..."
                agent_label.update(f"Agent: {status}")
        except:
            pass

    def update_context_usage(self, tokens: int, percentage: float):
        """Update context usage"""
        self.context_usage["tokens"] += tokens
        self.context_usage["percentage"] = percentage
        self._update_context_display()

        # Update session
        if self.session_mgr._current_session:
            self.session_mgr.update_context_usage(tokens, percentage)

    def update_session_cost(self, cost_usd: float):
        """Update session cost"""
        self.session_cost += cost_usd
        self._update_cost_display()

        # Update session
        if self.session_mgr._current_session:
            self.session_mgr.update_cost(cost_usd)

    def switch_provider(self, provider: str):
        """Switch provider"""
        success = self.provider_mgr.switch_provider(provider)
        if success:
            try:
                provider_display = self.query_one("#provider_display", Static)
                if provider_display:
                    model = self.provider_mgr.current_model()
                    provider_display.update(f"Provider: {provider}")
                self.show_agent_status(f"Switched to {provider}")
            except:
                pass
        else:
            self.show_agent_status(f"Failed to switch to {provider}")

    def switch_model(self, model: str):
        """Switch model"""
        self.provider_mgr.set_model(model)
        try:
            model_display = self.query_one("#model_display", Static)
            if model_display:
                provider = self.provider_mgr.current_provider()
                model_display.update(f"Provider: {provider} / {model}")
            self.show_agent_status(f"Model switched to {model}")
        except:
            pass
