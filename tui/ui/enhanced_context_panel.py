"""
Enhanced Context Panel - Uses new core systems with Task 5 enhancements
Right panel with session info, context usage, cost tracking, and agent visibility
"""

from textual.containers import Vertical, Horizontal, Container
from textual.widgets import Static, Button, ProgressBar
from textual import on
from textual.reactive import reactive
from pathlib import Path
import sys
from datetime import datetime
from typing import Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import new core systems
from tui.core import (
    get_config_manager,
    get_session_manager
)


class EnhancedContextPanel(Vertical):
    """Enhanced context panel with new core systems and all Task 5 features"""

    CSS = """
    EnhancedContextPanel {
        border: solid #30363D;
        background: #0D1117;
        padding: 1;
    }

    .section_header {
        text-align: center;
        padding: 0 0 1 0;
        border-bottom: solid #30363D;
    }

    .section_header Static {
        text-style: bold #6b6b6b;
    }

    .info_row {
        display: grid;
        grid-columns: 1 1;
        padding: 0;
    }

    .info_row Static {
        padding: 0;
    }

    .info_label {
        text-style: bold #6b6b6b;
    }

    .info_value {
        text-style: #C9D1D9;
    }

    Button {
        width: 1fr;
        margin: 0 0 1 0;
    }

    # Warning colors
    .warning {
        text-style: bold #E36808;
    }

    .critical {
        text-style: bold #FF6B6B;
    }
    """

    border_title = "Context"

    # Reactive state
    session_id = reactive("No Session")
    provider = reactive("unknown")
    model = reactive("unknown")
    context_tokens = reactive(0)
    context_percentage = reactive(0.0)
    session_cost = reactive(0.0)
    agent_activity = reactive("")
    files_modified = reactive([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize new core systems
        self.config = get_config_manager()
        self.session_mgr = get_session_manager()

    def compose(self):
        """Compose enhanced context panel"""
        # Session section
        yield Static("[bold #8B949E]SESSION[/bold #8B949E]", classes="section_header")

        with Horizontal(classes="info_row"):
            yield Static("ID:", classes="info_label")
            yield Static(id="session_id", classes="info_value")

        with Horizontal(classes="info_row"):
            yield Static("Started:", classes="info_label")
            yield Static(id="start_time", classes="info_value")

        # Provider/Model section
        yield Static("[bold #8B949E]PROVIDER[/bold #8B949E]", classes="section_header")

        with Horizontal(classes="info_row"):
            yield Static("Provider:", classes="info_label")
            yield Static(id="provider", classes="info_value")

        with Horizontal(classes="info_row"):
            yield Static("Model:", classes="info_label")
            yield Static(id="model", classes="info_value")

        # Agent Activity section
        yield Static("[bold #8B949E]AGENT ACTIVITY[/bold #8B949E]", classes="section_header")
        yield Static(id="agent_activity", classes="info_value")
        yield Button("List Agents", id="btn_list_agents")

        # Context Usage section
        yield Static("[bold #8B949E]CONTEXT USAGE[/bold #8B949E]", classes="section_header")

        with Horizontal(classes="info_row"):
            yield Static("Tokens:", classes="info_label")
            yield Static(id="context_tokens", classes="info_value")

        with Horizontal(classes="info_row"):
            yield Static("Usage:", classes="info_label")
            yield Static(id="context_percentage", classes="info_value")

        # Progress bar for context
        yield ProgressBar(
            total=100,
            show_eta=False,
            id="context_progress"
        )

        # Cost section
        yield Static("[bold #8B949E]SESSION COST[/bold #8B949E]", classes="section_header")

        with Horizontal(classes="info_row"):
            yield Static("Total:", classes="info_label")
            yield Static(f"${self.session_cost:.4f}", id="session_cost_total", classes="info_value")

        # Files Modified section
        yield Static("[bold #8B949E]FILES MODIFIED[/bold #8B949E]", classes="section_header")
        yield Static(id="files_list", classes="info_value")
        yield Button("Clear", id="btn_clear_files")

    def on_mount(self):
        """Initialize on mount"""
        self._update_session_info()
        self._update_provider_info()
        self._update_context_display()
        self._update_cost_display()
        self._update_files_list()

    def _update_session_info(self):
        """Update session information"""
        if self.session_mgr._current_session:
            session = self.session_mgr._current_session
            try:
                session_id_display = self.query_one("#session_id", Static)
                if session_id_display:
                    session_id_display.update(f"{session.session_id[:8]}...")

                start_time_display = self.query_one("#start_time", Static)
                if start_time_display:
                    created = session.created_at
                    # Format: YYYY-MM-DD HH:MM
                    start_time_display.update(created[:19])
            except:
                pass

    def _update_provider_info(self):
        """Update provider and model information"""
        provider = self.provider_mgr.current_provider()
        model = self.provider_mgr.current_model()

        try:
            provider_display = self.query_one("#provider", Static)
            if provider_display:
                provider_display.update(provider)

            model_display = self.query_one("#model", Static)
            if model_display:
                model_display.update(model)
        except:
            pass

    def _update_context_display(self):
        """Update context usage display"""
        try:
            tokens_display = self.query_one("#context_tokens", Static)
            if tokens_display:
                tokens_display.update(f"{self.context_tokens:,}")

            percentage_display = self.query_one("#context_percentage", Static)
            if percentage_display:
                # Set warning colors based on usage
                percentage = self.context_percentage
                if percentage >= 95:
                    percentage_display.update(f"{percentage:.1f}%", classes="critical")
                elif percentage >= 80:
                    percentage_display.update(f"{percentage:.1f}%", classes="warning")
                else:
                    percentage_display.update(f"{percentage:.1f}%")

            progress_bar = self.query_one("#context_progress", ProgressBar)
            if progress_bar:
                progress_bar.progress = percentage
        except:
            pass

    def _update_cost_display(self):
        """Update cost display"""
        try:
            cost_display = self.query_one("#session_cost_total", Static)
            if cost_display:
                cost_display.update(f"${self.session_cost:.4f}")
        except:
            pass

    def _update_files_list(self):
        """Update files modified list"""
        if not self.files_modified:
            try:
                files_display = self.query_one("#files_list", Static)
                if files_display:
                    files_display.update("[dim]No files modified[/dim]")
            except:
                pass
        else:
            try:
                files_display = self.query_one("#files_list", Static)
                if files_display:
                    # Show last 10 files
                    files = self.files_modified[-10:]
                    files_text = "\n".join([f"  • {f}" for f in files])
                    files_display.update(files_text)
            except:
                pass

    @on(Button.Pressed, "#btn_list_agents")
    def on_list_agents(self):
        """Show available agents"""
        self.agent_activity = "Available agents: Generator, Reviewer, Tester, Refactorer, Documenter"
        self._update_agent_activity()

    def _update_agent_activity(self):
        """Update agent activity display"""
        try:
            agent_display = self.query_one("#agent_activity", Static)
            if agent_display:
                agent_display.update(self.agent_activity)
        except:
            pass

    def update_session_info(self, session_id: str):
        """Update session info from outside"""
        self.session_id = session_id
        self._update_session_info()

    def update_provider_info(self, provider: str, model: str):
        """Update provider info from outside"""
        self.provider = provider
        self.model = model
        self._update_provider_info()

    def update_context_usage(self, tokens: int, percentage: float):
        """Update context usage from outside"""
        self.context_tokens += tokens
        self.context_percentage = percentage
        self._update_context_display()

        # Sync with session manager
        if self.session_mgr._current_session:
            self.session_mgr.update_context_usage(tokens, percentage)

    def update_session_cost(self, cost_usd: float):
        """Update session cost from outside"""
        self.session_cost += cost_usd
        self._update_cost_display()

        # Sync with session manager
        if self.session_mgr._current_session:
            self.session_mgr.update_cost(cost_usd)

    def add_file_modified(self, file_path: str):
        """Add file to modified list"""
        if file_path not in self.files_modified:
            self.files_modified.append(file_path)
            self._update_files_list()

    @on(Button.Pressed, "#btn_clear_files")
    def on_clear_files(self):
        """Clear files list"""
        self.files_modified = []
        self._update_files_list()

    def show_agent_thinking(self, agent_name: str, status: str):
        """Show agent thinking status"""
        self.agent_activity = f"{agent_name}: {status}"
        self._update_agent_activity()
