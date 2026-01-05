"""
ContextPanel - Right panel with session info, context usage, modified files
Read-only panel modeled after OpenCode's right panel
"""

from textual.containers import Vertical
from textual.widgets import Static, ProgressBar, DataTable
from textual import on
from textual.reactive import reactive
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class SessionInfoSection(Vertical):
    """Session information section"""
    
    session_name = reactive("New Session")
    start_time = reactive("")
    provider = reactive("openrouter")
    model = reactive("openai/gpt-4")
    
    def compose(self):
        """Compose session info section"""
        yield Static("[bold uppercase #8B949E]SESSION[/bold uppercase #8B949E]", classes="section_header")
        yield Static(id="session_name_display")
        yield Static(id="start_time_display")
        yield Static(id="model_provider_display", classes="muted")
        yield Static(id="cost_display")
    
    def on_mount(self):
        """Initialize on mount"""
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._update_display()
    
    def _update_display(self):
        """Update display"""
        try:
            name_display = self.query_one("#session_name_display", Static)
            name_display.update(f"[bold #C9D1D9]{self.session_name}[/bold #C9D1D9]")
        except:
            pass
        
        try:
            time_display = self.query_one("#start_time_display", Static)
            time_display.update(f"[dim #7D8590]Started: {self.start_time}[/dim #7D8590]")
        except:
            pass
        
        try:
            model_display = self.query_one("#model_provider_display", Static)
            model_display.update(f"[dim #7D8590]{self.provider} / {self.model}[/dim #7D8590]")
        except:
            pass
        
        try:
            cost_display = self.query_one("#cost_display", Static)
            cost_display.update(f"[dim #7D8590]Cost: ${self.session_cost:.4f}[/dim #7D8590]")
        except:
            pass
    
    def update_session_data(self, data: Dict):
        """Update from session data"""
        self.session_name = data.get("name", "New Session")
        self.provider = data.get("provider", "openrouter")
        self.model = data.get("model", "openai/gpt-4")
        self.start_time = data.get("start_time", self.start_time)
        cost_data = data.get("cost", {})
        self.session_cost = cost_data.get("total_usd", 0.0)
        self._update_display()
    
    def update_provider(self, provider: str, model: str):
        """Update provider and model"""
        self.provider = provider
        self.model = model
        self._update_display()
    
    def update_cost(self, total_usd: float):
        """Update cost display"""
        self.session_cost = total_usd
        # Will trigger watch_session_cost to update display
    
    def update_provider(self, provider: str, model: str):
        """Update provider and model"""
        self.provider = provider
        self.model = model
        self._update_display()
    
    def update_cost(self, total_usd: float):
        """Update cost display in session info"""
        # Note: This method is called on ContextPanel but delegated to SessionInfoSection
        # Cost display is in a separate component, so this is a stub
        pass

if __name__ == "__main__":
    # Demo context panel
    from textual.app import App
    
    class DemoApp(App):
        CSS = """
        Screen {
            background: #0B0F14;
        }
        ContextPanel {
            width: 32;
            height: 100%;
            background: #0B0F14;
            border: solid #1E2A38;
            padding: 1;
        }
        .section_header {
            text-style: bold uppercase;
            margin-bottom: 0;
        }
        .muted {
            text-style: dim;
            margin-top: 1;
        }
        Static {
            color: #C9D1D9;
            margin: 0 0 1 0;
        }
        ProgressBar {
            height: 1;
            margin: 1 0;
        }
        """
        
        def compose(self):
            panel = ContextPanel()
            yield panel
        
        def on_mount(self):
            context_panel = self.query_one(ContextPanel)
            
            # Update with demo data
            context_panel.update_session({
                "name": "Session - Fix auth bug",
                "start_time": "2024-01-05 14:30:22",
                "provider": "openrouter",
                "model": "openai/gpt-4"
            })
            
            context_panel.update_context_usage(85600, 128000)
            context_panel.add_modified_file("src/auth.py")
            context_panel.add_modified_file("src/api.py")
            context_panel.update_lsp_status("Ready", 5)
    
    app = DemoApp()
    app.run()
