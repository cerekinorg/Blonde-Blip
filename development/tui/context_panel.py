"""
ContextPanel - Right panel with session info, context usage, modified files
Read-only panel modeled after OpenCode's right panel
"""

from textual.containers import Vertical
from textual.widgets import Static, ProgressBar
from textual import on
from textual.reactive import reactive
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class SessionInfoSection(Vertical):
    """Session information section"""
    
    session_name = reactive("No Session")
    start_time = reactive("")
    provider = reactive("openrouter")
    model = reactive("openai/gpt-4")
    session_cost = reactive(0.0)
    
    def compose(self):
        """Compose session info section"""
        yield Static("[bold uppercase #8B949E]SESSION[/bold uppercase #8B949E]", classes="section_header")
        yield Static(id="session_name_display")
        yield Static(id="start_time_display")
        yield Static(id="model_provider_display", classes="muted")
        yield Static(id="cost_display", classes="muted")
    
    def on_mount(self):
        """Initialize on mount"""
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._update_display()
    
    def watch_session_name(self, old_name, new_name):
        """Update session name display"""
        try:
            display = self.query_one("#session_name_display", Static)
            if display:
                display.update(f"[bold #C9D1D9]{new_name}[/bold #C9D1D9]")
        except:
            pass
    
    def watch_provider(self, old_provider, new_provider):
        """Update provider display"""
        try:
            display = self.query_one("#model_provider_display", Static)
            if display:
                display.update(f"[dim #7D8590]{new_provider} / {self.model}[/dim #7D8590]")
        except:
            pass
    
    def watch_model(self, old_model, new_model):
        """Update model display"""
        try:
            display = self.query_one("#model_provider_display", Static)
            if display:
                display.update(f"[dim #7D8590]{self.provider} / {new_model}[/dim #7D8590]")
        except:
            pass
    
    def watch_session_cost(self, old_cost, new_cost):
        """Update cost display"""
        try:
            display = self.query_one("#cost_display", Static)
            if display:
                display.update(f"[dim #7D8590]Cost: ${new_cost:.4f}[/dim #7D8590]")
        except:
            pass
    
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


class ContextUsageSection(Vertical):
    """Context usage section with progress bar"""
    
    tokens_used = reactive(0)
    max_tokens = reactive(128000)
    
    def compose(self):
        """Compose context usage section"""
        yield Static("[bold uppercase #8B949E]CONTEXT[/bold uppercase #8B949E]", classes="section_header")
        yield Static(id="tokens_display")
        yield ProgressBar(
            id="context_progress",
            show_eta=False,
            show_percentage=True
        )
    
    def watch_tokens_used(self, old_tokens: int, new_tokens: int):
        """Update when tokens used changes"""
        self._update_display()
    
    def watch_max_tokens(self, old_max: int, new_max: int):
        """Update when max tokens changes"""
        self._update_display()
    
    def _update_display(self):
        """Update display"""
        try:
            tokens_display = self.query_one("#tokens_display", Static)
            percentage = (self.tokens_used / self.max_tokens * 100) if self.max_tokens > 0 else 0
            
            # Color coding
            if percentage < 80:
                color = "#3FB950"
                status = "OK"
            elif percentage < 90:
                color = "#D29922"
                status = "Warning"
            elif percentage < 95:
                color = "#E3B341"
                status = "High"
            else:
                color = "#F85149"
                status = "Critical"
            
            tokens_display.update(
                f"[{color}]{status}: {self.tokens_used:,} / {self.max_tokens:,} ({percentage:.1f}%)[/{color}]"
            )
        except:
            pass
        
        try:
            progress = self.query_one("#context_progress", ProgressBar)
            progress.progress = self.tokens_used / self.max_tokens
            progress.update()
        except:
            pass
    
    def update_usage(self, tokens_used: int, max_tokens: int):
        """Update usage"""
        self.tokens_used = tokens_used
        self.max_tokens = max_tokens


class ModifiedFilesSection(Vertical):
    """Modified files list section"""
    
    files = reactive([])
    
    def compose(self):
        """Compose modified files section"""
        yield Static("[bold uppercase #8B949E]MODIFIED FILES[/bold uppercase #8B949E]", classes="section_header")
        yield Static(id="files_list")
    
    def watch_files(self, old_files: List, new_files: List):
        """Update when files list changes"""
        self._update_display()
    
    def _update_display(self):
        """Update display"""
        try:
            files_display = self.query_one("#files_list", Static)
            
            if not self.files:
                files_display.update("[dim #7D8590]No files modified[/dim #7D8590]")
            else:
                lines = []
                for file_path in self.files:
                    path = Path(file_path)
                    lines.append(f"  [bold cyan]{path.name}[/bold cyan]")
                files_display.update("\n".join(lines))
        except:
            pass
    
    def add_file(self, file_path: str):
        """Add file to modified list"""
        if file_path not in self.files:
            self.files.append(file_path)
    
    def clear_files(self):
        """Clear files list"""
        self.files = []


class LSPStatusSection(Vertical):
    """LSP and tool status section"""
    
    status = reactive("Ready")
    tool_count = reactive(0)
    
    def compose(self):
        """Compose LSP status section"""
        yield Static("[bold uppercase #8B949E]STATUS[/bold uppercase #8B949E]", classes="section_header")
        yield Static(id="status_display")
        yield Static(id="tool_display", classes="muted")
    
    def watch_status(self, old_status: str, new_status: str):
        """Update when status changes"""
        self._update_display()
    
    def watch_tool_count(self, old_count: int, new_count: int):
        """Update when tool count changes"""
        self._update_display()
    
    def _update_display(self):
        """Update display"""
        try:
            status_display = self.query_one("#status_display", Static)
            
            # Color based on status
            color = "#3FB950" if self.status == "Ready" else "#F85149"
            status_display.update(f"[{color}]● {self.status}[/{color}]")
        except:
            pass
        
        try:
            tool_display = self.query_one("#tool_display", Static)
            tool_display.update(f"[dim #7D8590]{self.tool_count} tools active[/dim #7D8590]")
        except:
            pass
    
    def update_status(self, status: str, tool_count: int = 0):
        """Update status"""
        self.status = status
        self.tool_count = tool_count


class ContextPanel(Vertical):
    """Right panel - context and session intelligence"""
    
    border_title = "Context"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session_info = None
        self.context_usage = None
        self.modified_files = None
        self.lsp_status = None
    
    def compose(self):
        """Compose context panel"""
        # Session info
        yield SessionInfoSection()
        
        # Spacer
        yield Static()
        
        # Context usage
        yield ContextUsageSection()
        
        # Spacer
        yield Static()
        
        # Modified files
        yield ModifiedFilesSection()
        
        # Spacer
        yield Static()
        
        # LSP status
        yield LSPStatusSection()
    
    def on_mount(self):
        """Initialize on mount"""
        self.session_info = self.query_one(SessionInfoSection)
        self.context_usage = self.query_one(ContextUsageSection)
        self.modified_files = self.query_one(ModifiedFilesSection)
        self.lsp_status = self.query_one(LSPStatusSection)
    
    def update_session(self, data: Dict):
        """Update session info"""
        if self.session_info:
            self.session_info.update_session_data(data)
    
    def update_context_usage(self, tokens_used: int, max_tokens: int):
        """Update context usage"""
        if self.context_usage:
            self.context_usage.update_usage(tokens_used, max_tokens)
    
    def add_modified_file(self, file_path: str):
        """Add modified file"""
        if self.modified_files:
            self.modified_files.add_file(file_path)
    
    def update_provider(self, provider: str, model: str):
        """Update provider and model display"""
        if self.session_info:
            self.session_info.update_provider(provider, model)
    
    def update_cost(self, total_usd: float):
        """Update cost display"""
        if self.session_info:
            self.session_info.update_cost(total_usd)
    
    def clear_modified_files(self):
        """Clear modified files"""
        if self.modified_files:
            self.modified_files.clear_files()
    
    def update_lsp_status(self, status: str, tool_count: int = 0):
        """Update LSP status"""
        if self.lsp_status:
            self.lsp_status.update_status(status, tool_count)


class ContextPanelCSS:
    """CSS for Context Panel"""
    
    CSS = """
    ContextPanel {
        padding: 1;
        border: solid #1E2A38;
        background: $panel;
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
                "model": "openai/gpt-4",
                "cost": {"total_usd": 2.3456}
            })
            
            context_panel.update_context_usage(85600, 128000)
            context_panel.add_modified_file("src/auth.py")
            context_panel.add_modified_file("src/api.py")
            context_panel.update_lsp_status("Ready", 5)
    
    app = DemoApp()
    app.run()
