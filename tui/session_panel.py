"""
Session Panel - Display session metadata, context usage, and costs
Right column component showing session information and actions
"""

from textual.widgets import Static, Button, ProgressBar, Label
from textual.containers import Vertical, Container
from textual import on
from textual.reactive import reactive
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

try:
    from tui.session_manager import get_session_manager
    from tui.cost_tracker import get_cost_tracker
    from tui.blip_manager import get_blip_manager
    MANAGERS_AVAILABLE = True
except ImportError:
    try:
        from session_manager import get_session_manager
        from cost_tracker import get_cost_tracker
        from blip_manager import get_blip_manager
        MANAGERS_AVAILABLE = True
    except ImportError:
        MANAGERS_AVAILABLE = False


class SessionPanel(Vertical):
    """Panel displaying session information and actions"""
    
    session_id = reactive("")
    session_name = reactive("No Session")
    provider = reactive("openrouter")
    model = reactive("openai/gpt-4")
    blip_character = reactive("axolotl")
    context_percentage = reactive(0.0)
    cost_total = reactive(0.0)
    
    def __init__(self):
        super().__init__()
        self.border_title = "Session"
        self.session_manager = None
        self.cost_tracker = None
        self.blip_manager = None
        
        if MANAGERS_AVAILABLE:
            self.session_manager = get_session_manager()
            self.cost_tracker = get_cost_tracker()
            self.blip_manager = get_blip_manager()
    
    def compose(self):
        """Compose the session panel"""
        # Blip Preview
        yield Static("[bold]Blip:[/bold]", classes="label")
        yield Static(id="blip_preview")
        
        yield Static()  # Spacer
        
        # Session Info
        yield Static("[bold]Session:[/bold]", classes="label")
        yield Static(id="session_name_display")
        yield Static(f"[dim]ID: {self.session_id}[/dim]", id="session_id_display", classes="dim")
        
        yield Static()  # Spacer
        
        # Model/Provider
        yield Static("[bold]AI:[/bold]", classes="label")
        yield Static(id="model_provider_display")
        
        yield Static()  # Spacer
        
        # Context Usage
        yield Static("[bold]Context:[/bold]", classes="label")
        yield Static(id="context_display")
        yield ProgressBar(
            id="context_progress",
            show_eta=False,
            show_percentage=True
        )
        
        yield Static()  # Spacer
        
        # Cost Tracking
        yield Static("[bold]Cost (USD):[/bold]", classes="label")
        yield Static(id="cost_display")
        yield Static(id="cost_estimate_display", classes="dim")
        
        yield Static()  # Spacer
        
        # Actions
        yield Static("[bold]Actions:[/bold]", classes="label")
        yield Button("New Session", id="new_session_btn", variant="primary")
        yield Button("Switch Session", id="switch_session_btn")
        yield Button("Export Session", id="export_session_btn")
    
    def on_mount(self):
        """Initialize panel on mount"""
        self._update_display()
    
    def watch_session_name(self, old_name, new_name):
        """Update session name display"""
        display = self.query_one("#session_name_display", Static)
        if display:
            display.update(new_name)
    
    def watch_provider(self, old_provider, new_provider):
        """Update provider display"""
        self._update_model_provider_display()
    
    def watch_model(self, old_model, new_model):
        """Update model display"""
        self._update_model_provider_display()
    
    def watch_blip_character(self, old_character, new_character):
        """Update Blip preview"""
        self._update_blip_preview()
    
    def watch_context_percentage(self, old_pct, new_pct):
        """Update context display and progress bar"""
        display = self.query_one("#context_display", Static)
        progress = self.query_one("#context_progress", ProgressBar)
        
        if display:
            # Color-coded based on percentage
            if new_pct < 80:
                color = "bright_green"
                status = "OK"
            elif new_pct < 90:
                color = "yellow"
                status = "Warning"
            elif new_pct < 95:
                color = "orange"
                status = "High"
            else:
                color = "bright_red"
                status = "Critical"
            
            display.update(f"[{color}]{status}: {new_pct:.1f}%[/{color}]")
        
        if progress:
            progress.progress = new_pct / 100
            progress.update()
    
    def watch_cost_total(self, old_cost, new_cost):
        """Update cost display"""
        display = self.query_one("#cost_display", Static)
        estimate = self.query_one("#cost_estimate_display", Static)
        
        if display:
            display.update(f"${new_cost:.4f}")
        
        if estimate and self.session_manager:
            # Estimate cost for next prompt
            session_data = self.session_manager.current_session_data
            context_usage = session_data.get("context_usage", {})
            total_tokens = context_usage.get("total_tokens", 0)
            
            if total_tokens > 0:
                avg_cost_per_token = new_cost / total_tokens
                estimated = avg_cost_per_token * 1000  # Assume 1000 tokens next prompt
                estimate.update(f"[dim]~${estimated:.6f} / 1K tokens[/dim]")
    
    def _update_model_provider_display(self):
        """Update model and provider display"""
        display = self.query_one("#model_provider_display", Static)
        if display:
            display.update(f"[cyan]{self.provider}[/cyan]\n[dim]{self.model}[/dim]")
    
    def _update_blip_preview(self):
        """Update Blip character preview"""
        display = self.query_one("#blip_preview", Static)
        
        if display and self.blip_manager:
            character_name = self.blip_manager.current_character_name
            art = self.blip_manager.get_art("happy")
            color = self.blip_manager.get_color("happy")
            display.update(f"[{color}]{art}[/{color}]\n[dim]{character_name}[/dim]")
    
    def _update_display(self):
        """Update all displays"""
        self.watch_session_name("", self.session_name)
        self._update_model_provider_display()
        self._update_blip_preview()
        self.watch_context_percentage(0, self.context_percentage)
        self.watch_cost_total(0, self.cost_total)
    
    def update_from_session(self, session_data: Dict):
        """
        Update panel from session data
        
        Args:
            session_data: Session data dictionary
        """
        self.session_id = session_data.get("session_id", "")
        self.session_name = session_data.get("name", "No Session")
        self.provider = session_data.get("provider", "openrouter")
        self.model = session_data.get("model", "openai/gpt-4")
        self.blip_character = session_data.get("blip_character", "axolotl")
        
        # Context usage
        context_usage = session_data.get("context_usage", {})
        self.context_percentage = context_usage.get("percentage", 0.0)
        
        # Cost
        cost_data = session_data.get("cost", {})
        self.cost_total = cost_data.get("total_usd", 0.0)
    
    @on(Button.Pressed, "#new_session_btn")
    def on_new_session(self):
        """Handle new session button"""
        # Trigger callback or emit event
        self.app.notify("New session creation coming soon!", severity="information")
    
    @on(Button.Pressed, "#switch_session_btn")
    def on_switch_session(self):
        """Handle switch session button"""
        self.app.notify("Session switch coming soon!", severity="information")
    
    @on(Button.Pressed, "#export_session_btn")
    def on_export_session(self):
        """Handle export session button"""
        self.app.notify("Session export coming soon!", severity="information")


class SessionPanelCSS:
    """CSS for Session Panel"""
    
    CSS = """
    SessionPanel {
        padding: 1;
        border: solid $primary;
        background: $panel;
    }
    
    SessionPanel > Static {
        padding: 0 1;
    }
    
    .label {
        text-style: bold;
        margin-bottom: 0;
    }
    
    .dim {
        text-style: dim;
        margin-bottom: 1;
    }
    
    #blip_preview {
        text-align: center;
        margin: 1 0;
    }
    
    Button {
        width: 100%;
        margin: 0 0 1 0;
    }
    """


if __name__ == "__main__":
    # Demo session panel
    from textual.app import App
    
    class DemoApp(App):
        CSS = SessionPanelCSS.CSS
        
        def compose(self):
            panel = SessionPanel()
            panel.session_id = "20240104_143022_123456"
            panel.session_name = "Session - Fix authentication bug"
            panel.provider = "openrouter"
            panel.model = "openai/gpt-4"
            panel.blip_character = "axolotl"
            panel.context_percentage = 75.5
            panel.cost_total = 2.3456
            yield panel
    
    app = DemoApp()
    app.run()
