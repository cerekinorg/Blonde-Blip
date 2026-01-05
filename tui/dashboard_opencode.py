"""
Dashboard - OpenCode-inspired 3-column TUI
Left: Blip | Center: Chat/Editor | Right: Context
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual import on
from textual.reactive import reactive
from pathlib import Path
from typing import Optional, Dict

try:
    from .blip_panel import BlipPanel
    from .work_panel import WorkPanel
    from .context_panel import ContextPanel
    from .query_processor import get_query_processor, QueryResult
    from .session_manager import get_session_manager
    MANAGERS_AVAILABLE = True
except ImportError:
    try:
        from blip_panel import BlipPanel
        from work_panel import WorkPanel
        from context_panel import ContextPanel
        from query_processor import get_query_processor, QueryResult
        from session_manager import get_session_manager
        MANAGERS_AVAILABLE = True
    except ImportError as e:
        print(f"Import error: {e}")
        MANAGERS_AVAILABLE = False


class Dashboard(App):
    """OpenCode-inspired 3-column dashboard TUI"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 1;
        grid-columns: 24 1fr 32;
        background: #0D1117;
    }
    
    /* Main Layout */
    Horizontal {
        height: 100%;
    }
    
    /* Left Panel - Blip */
    BlipPanel {
        background: #0E1621;
        border: solid #1E2A38;
        width: 24;
        height: 100%;
    }
    
    BlipPanel.hidden {
        display: none;
    }
    
    BlipPanel.shrunk {
        width: 12;
    }
    
    /* Center Panel - Workspace */
    WorkPanel {
        background: #0D1117;
        border: solid #1E2A38;
        height: 100%;
    }
    
    /* Right Panel - Context */
    ContextPanel {
        background: #0B0F14;
        border: solid #1E2A38;
        width: 32;
        height: 100%;
    }
    
    ContextPanel.hidden {
        display: none;
    }
    
    /* Typography */
    Static {
        color: #C9D1D9;
    }
    
    /* Borders */
    BlipPanel, WorkPanel, ContextPanel {
        border-title-color: #8B949E;
        border-title-style: bold;
    }
    """
    
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+e", "toggle_mode", "Toggle Chat/Editor"),
        ("ctrl+l", "toggle_left_panel", "Toggle Left Panel"),
        ("ctrl+r", "toggle_right_panel", "Toggle Right Panel"),
        ("ctrl+s", "show_settings", "Settings"),
        ("ctrl+m", "show_model_switcher", "Model Switcher"),
        ("f1", "show_help", "Help")
    ]
    
    left_visible = reactive(True)
    right_visible = reactive(True)
    
    def __init__(self, session_id: Optional[str] = None, first_prompt: str = ""):
        super().__init__()
        self.session_id = session_id
        self.first_prompt = first_prompt
        
        # Initialize managers
        self.query_processor = None
        self.session_manager = None
        self.context_update_timer = None
        
        if MANAGERS_AVAILABLE:
            try:
                self.query_processor = get_query_processor()
                self.session_manager = get_session_manager()
            except Exception as e:
                print(f"Error initializing managers: {e}")
    
    def compose(self) -> ComposeResult:
        """Compose 3-column layout"""
        yield BlipPanel(id="left_panel")
        yield WorkPanel(id="center_panel")
        yield ContextPanel(id="right_panel")
    
    def on_mount(self) -> None:
        """Initialize on mount"""
        self.title = "Blonde CLI - Dashboard"
        self.sub_title = "Agentic Development Assistant"
        
        # Get panel references
        try:
            self.left_panel = self.query_one("#left_panel", BlipPanel)
            self.center_panel = self.query_one("#center_panel", WorkPanel)
            self.right_panel = self.query_one("#right_panel", ContextPanel)
        except:
            pass
        
        # Update Blip state
        self._update_blip_state("idle", "Awaiting input")
        
        # Load session data from session_manager
        if self.session_manager and self.session_manager.current_session_data:
            session_data = self.session_manager.current_session_data
            
            # Update context panel with session info
            self._update_session_data(session_data)
            
            # Initialize context usage
            context_usage = session_data.get("context_usage", {})
            self._update_context_usage(
                tokens_used=context_usage.get("total_tokens", 0),
                max_tokens=context_usage.get("context_window", 128000)
            )
            
            # Initialize provider/model display
            self._update_provider_info(
                provider=session_data.get("provider", "openrouter"),
                model=session_data.get("model", "openai/gpt-4")
            )
            
            # Initialize modified files list
            files_edited = session_data.get("files_edited", [])
            if files_edited:
                self._update_modified_files([f["file_path"] for f in files_edited])
            
            # Start context update timer (every 50 seconds)
            self.context_update_timer = self.set_timer(50.0, self._update_context_from_session)
        
        # Handle first prompt if provided
        if self.first_prompt:
            self._handle_first_prompt()
        
        # Handle first prompt if provided
        if self.first_prompt:
            self._handle_first_prompt()
    
    def _update_blip_state(self, state: str, message: str):
        """Update Blip state and status message"""
        try:
            blip_panel = self.query_one("#left_panel", BlipPanel)
            blip_panel.update_status(state, message)
        except:
            pass
    
    def _update_session_data(self, data: Dict):
        """Update all panels with session data"""
        try:
            context_panel = self.query_one("#right_panel", ContextPanel)
            context_panel.update_session(data)
        except:
            pass
    
    def _update_context_usage(self, tokens_used: int, max_tokens: int):
        """Update context usage in context panel"""
        try:
            context_panel = self.query_one("#right_panel", ContextPanel)
            context_panel.update_context_usage(tokens_used, max_tokens)
        except:
            pass
    
    def _update_provider_info(self, provider: str, model: str):
        """Update provider/model info in context panel"""
        try:
            context_panel = self.query_one("#right_panel", ContextPanel)
            context_panel.update_provider(provider, model)
        except:
            pass
    
    def _update_modified_files(self, files: list):
        """Update modified files in context panel"""
        try:
            context_panel = self.query_one("#right_panel", ContextPanel)
            for file_path in files:
                context_panel.add_modified_file(file_path)
        except:
            pass
    
    def _update_context_from_session(self):
        """Update context panel from session data (called every 50s)"""
        if self.session_manager and self.session_manager.current_session_data:
            session_data = self.session_manager.current_session_data
            
            # Update context usage
            context_usage = session_data.get("context_usage", {})
            self._update_context_usage(
                tokens_used=context_usage.get("total_tokens", 0),
                max_tokens=context_usage.get("context_window", 128000)
            )
            
            # Update cost
            cost_data = session_data.get("cost", {})
            if cost_data:
                try:
                    context_panel = self.query_one("#right_panel", ContextPanel)
                    context_panel.update_cost(cost_data.get("total_usd", 0.0))
                except:
                    pass
            
            # Restart timer
            self.context_update_timer = self.set_timer(50.0, self._update_context_from_session)
    
    def _handle_first_prompt(self):
        """Handle first prompt if provided"""
        try:
            work_panel = self.query_one("#center_panel", WorkPanel)
            chat_view = work_panel.get_chat_view()
            
            if chat_view:
                chat_view.add_message("user", self.first_prompt)
                # Process the first prompt
                self._process_query(self.first_prompt)
        except:
            pass
    
    def _process_query(self, query: str):
        """Process user query"""
        # Update Blip to thinking
        self._update_blip_state("thinking", "Processing your request...")
        
        # Process in background
        import threading
        
        def process():
            try:
                if self.query_processor:
                    # Create progress callback for Blip
                    def progress_callback(agent: str, status: str):
                        self.app.call_from_thread(
                            self._update_blip_state,
                            "working",
                            f"{agent}: {status}"
                        )
                    
                    # Process query
                    result: QueryResult = self.query_processor.process_query(
                        query=query,
                        context={"current_dir": str(Path.cwd())},
                        progress_callback=progress_callback
                    )
                    
                    # Update UI with result
                    self.app.call_from_thread(self._on_query_complete, result)
                else:
                    self.app.call_from_thread(
                        self._update_blip_state,
                        "error",
                        "Query processor not available"
                    )
            except Exception as e:
                self.app.call_from_thread(
                    self._update_blip_state,
                    "error",
                    f"Error: {str(e)[:50]}"
                )
        
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
    
    def _on_query_complete(self, result: QueryResult):
        """Handle query completion"""
        # Update Blip
        if result.success:
            self._update_blip_state("happy", "Task complete!")
        else:
            self._update_blip_state("sad", "Task failed")
        
        # Add response to chat
        try:
            work_panel = self.query_one("#center_panel", WorkPanel)
            chat_view = work_panel.get_chat_view()
            
            if chat_view and result.response:
                chat_view.add_message("assistant", result.response)
                
                # Add diff cards if files were modified
                if result.files_modified:
                    context_panel = self.query_one("#right_panel", ContextPanel)
                    for file_path in result.files_modified:
                        context_panel.add_modified_file(file_path)
                        chat_view.add_diff_card(file_path, 0, 0, "File modified")
        except:
            pass
    
    def action_toggle_mode(self) -> None:
        """Toggle between chat and editor modes"""
        try:
            work_panel = self.query_one("#center_panel", WorkPanel)
            work_panel.toggle_mode()
            
            # Show notification
            mode = work_panel.current_mode.upper()
            self.notify(f"Switched to {mode} mode", severity="information")
        except:
            pass
    
    def action_toggle_left_panel(self) -> None:
        """Toggle left panel visibility"""
        self.left_visible = not self.left_visible
        left_panel = self.query_one("#left_panel", BlipPanel)
        
        if left_panel:
            if self.left_visible:
                left_panel.remove_class("hidden")
                left_panel.remove_class("shrunk")
                self.notify("Left panel: Visible")
            else:
                left_panel.add_class("hidden")
                self.notify("Left panel: Hidden")
    
    def action_toggle_right_panel(self) -> None:
        """Toggle right panel visibility"""
        self.right_visible = not self.right_visible
        right_panel = self.query_one("#right_panel", ContextPanel)
        
        if right_panel:
            if self.right_visible:
                right_panel.remove_class("hidden")
                self.notify("Right panel: Visible")
            else:
                right_panel.add_class("hidden")
                self.notify("Right panel: Hidden")
    
    def action_show_settings(self) -> None:
        """Show settings modal"""
        self.notify("Settings modal coming soon!", severity="information")
    
    def action_show_model_switcher(self) -> None:
        """Show model switcher modal"""
        self.notify("Model switcher coming soon!", severity="information")
    
    def action_show_help(self) -> None:
        """Show help"""
        help_text = """
        [bold cyan]Blonde CLI - Dashboard Help[/bold cyan]
        
        [cyan]Keyboard Shortcuts:[/cyan]
        Ctrl+E - Toggle Chat/Editor mode
        Ctrl+L - Toggle Left Panel (Blip)
        Ctrl+R - Toggle Right Panel (Context)
        Ctrl+S - Settings
        Ctrl+M - Model Switcher
        F1 - Help
        Ctrl+Q - Quit
        
        [cyan]Layout:[/cyan]
        Left Panel - Blip companion with status
        Center Panel - Chat or Editor mode
        Right Panel - Context, session info, modified files
        """
        self.notify(help_text, title="Help", severity="information")


def launch_dashboard(session_id: Optional[str] = None, first_prompt: str = ""):
    """
    Launch the OpenCode-style dashboard
    
    Args:
        session_id: Optional session ID to load
        first_prompt: First message to send
    """
    try:
        app = Dashboard(session_id=session_id, first_prompt=first_prompt)
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error launching dashboard: {e}")


if __name__ == "__main__":
    launch_dashboard()
