"""
Dashboard - OpenCode-inspired 3-column TUI
Left: Blip | Center: Chat/Editor | Right: Context
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual import on
from textual.reactive import reactive
from textual.widgets import Input
from pathlib import Path
from typing import Optional, Dict

try:
    from .blip_panel import BlipPanel
    from .work_panel import WorkPanel
    from .context_panel import ContextPanel
    from .query_processor import get_query_processor, QueryResult
    from .session_manager import get_session_manager
    from .enhanced_settings import EnhancedSettings
    from .model_switcher import ModelSwitcher
    from .mcp_auto_setup import MCPAutoSetup
    MANAGERS_AVAILABLE = True
except ImportError:
    try:
        from blip_panel import BlipPanel
        from work_panel import WorkPanel
        from context_panel import ContextPanel
        from query_processor import get_query_processor, QueryResult
        from session_manager import get_session_manager
        from enhanced_settings import EnhancedSettings
        from model_switcher import ModelSwitcher
        from mcp_auto_setup import MCPAutoSetup
        MANAGERS_AVAILABLE = True
    except ImportError:
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
        ("ctrl+f", "toggle_file_tree", "Toggle File Tree"),
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
        self._last_query = ""
        
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
        
        # Update Blip to ready state
        try:
            blip_panel = self.query_one("#left_panel", BlipPanel)
            blip_panel.update_status("ready", "Ready for your commands")
        except:
            pass
        
        # Load session data from session_manager
        if self.session_manager and self.session_manager.current_session_data:
            session_data = self.session_manager.current_session_data
            
            # Update context panel with session info
            self._update_session_data(session_data)
            
            # Load chat history from previous session
            self._load_chat_history()
            
            # Handle first prompt if provided from welcome screen
            if self.first_prompt:
                self._handle_first_prompt()
            
            # Check and show session selector if multiple sessions exist
            self._check_and_show_session_selector()
            
            # Initialize context usage
            
            # Auto-start MCP servers if available
            try:
                from .mcp_auto_setup import MCPAutoSetup
                mcp_setup = MCPAutoSetup()
            except Exception:
                pass
            
            # Check and show session selector if multiple sessions exist
    
    def _load_chat_history(self):
        """Load previous session chat history into UI"""
        if not self.session_manager or not self.session_manager.current_session_data:
            return
        
        chat_history = self.session_manager.current_session_data.get("chat_history", [])
        if not chat_history:
            return
        
        try:
            work_panel = self.query_one("#center_panel", WorkPanel)
            chat_view = work_panel.get_chat_view()
            
            if chat_view:
                # Load last 10 messages to avoid overwhelming UI
                recent_messages = chat_history[-10:]
                for message in recent_messages:
                    role = message.get("role", "user")
                    content = message.get("content", "")
                    chat_view.add_message(role, content)
                
                if chat_history:
                    self.notify(f"Loaded {len(recent_messages)} messages from session", severity="information")
        except Exception as e:
            self.notify(f"Failed to load chat history: {e}", severity="warning")
    
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
    
    def _update_session_data(self, data: Dict):
        """Update all panels with session data"""
        try:
            context_panel = self.query_one("#right_panel", ContextPanel)
            context_panel.update_session(data)
        except:
            pass
    
    def _check_and_show_session_selector(self):
        """Check if multiple sessions exist and show selector"""
        try:
            if not self.session_manager:
                return
            
            sessions = self.session_manager.list_sessions(include_archived=False)
            
            # Only show selector if we have multiple sessions
            if len(sessions) > 1:
                # Create a simple notification about multiple sessions
                self.notify(
                    f"Multiple sessions available. Use settings to switch.",
                    severity="information",
                    timeout=5
                )
        except Exception as e:
            self.notify(f"Session selector error: {e}", severity="warning")
    
    def _update_blip_state(self, state: str, message: str):
        """Update Blip state and status message"""
        try:
            blip_panel = self.query_one("#left_panel", BlipPanel)
            blip_panel.update_status(state, message)
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
                    result = self.query_processor.process_query(
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
    
    @on(Input.Submitted, "#chat_input")
    def on_chat_submit(self, event: Input.Submitted) -> None:
        """Handle chat input submission"""
        message = event.value.strip()
        if message:
            # Add user message to chat
            try:
                work_panel = self.query_one("#center_panel", WorkPanel)
                chat_view = work_panel.get_chat_view()
                if chat_view:
                    chat_view.add_message("user", message)
            except:
                pass
            
            # Clear input
            event.input.value = ""
            
            # Update session with user message
            if self.session_manager:
                self.session_manager.update_chat_history("user", message)
            
            # Process the query
            self._process_query(message)
    
    def _on_query_complete(self, result: QueryResult):
        """Handle query completion"""
        # Save chat history
        if self.session_manager and self.query_processor:
            self.session_manager.update_chat_history("user", self.first_prompt or self._last_query)
        
        # Check if we have a valid response before saving
        response_text = result.code_output or result.response
        
        if self.session_manager and self.query_processor and response_text:
            self.session_manager.update_chat_history("assistant", response_text)
            self.session_manager.save_session()
        
        # Update Blip - check if we actually got a response
        if result.success and response_text:
            self._update_blip_state("happy", "Task complete!")
        else:
            self._update_blip_state("sad", "Task failed or empty response")
        
        # Add response to chat
        try:
            work_panel = self.query_one("#center_panel", WorkPanel)
            chat_view = work_panel.get_chat_view()
            
            if chat_view and response_text:
                chat_view.add_message("assistant", response_text)
                
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
    
    def action_toggle_file_tree(self) -> None:
        """Toggle file tree visibility in chat mode"""
        try:
            work_panel = self.query_one("#center_panel", WorkPanel)
            work_panel.toggle_file_tree()
            
            status = "shown" if work_panel.show_file_tree else "hidden"
            self.notify(f"File tree: {status}", severity="information")
        except:
            pass
    
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
        if MANAGERS_AVAILABLE:
            try:
                settings_screen = EnhancedSettings()
                
                # Handle settings result when dismissed
                def handle_settings_result(result: Optional[Dict[str, Any]]):
                    if result:
                        action = result.get("action", "")
                        
                        if action == "switch_provider":
                            # Provider switch handled by settings modal
                            pass
                        elif action == "switch_model":
                            # Model switch handled by settings modal
                            pass
                        elif action == "theme":
                            # Apply theme to dashboard
                            theme = result.get("theme", "dark")
                            self.apply_theme(theme)
                            self.notify(f"Theme changed to {theme}", severity="information")
                
                self.push_screen(settings_screen, handle_settings_result)
            except Exception as e:
                self.notify(f"Error opening settings: {e}", severity="error")
        else:
            self.notify("Settings module not available", severity="warning")
    
    def action_show_model_switcher(self) -> None:
        """Show model switcher modal"""
        if MANAGERS_AVAILABLE:
            try:
                model_switcher = ModelSwitcher()
                
                def handle_result(result):
                    if result:
                        provider = result.get("provider", "")
                        model = result.get("model", "")
                        if provider and model:
                            self.notify(f"Switched to {provider}/{model}", severity="information")
                            
                            # Update session data
                            if self.session_manager:
                                self.session_manager.current_session_data["provider"] = provider
                                self.session_manager.current_session_data["model"] = model
                                self.session_manager.save_session()
                            
                            # Update context panel
                            self._update_session_data(self.session_manager.current_session_data)
                
                self.push_screen(model_switcher, handle_result)
            except Exception as e:
                self.notify(f"Error opening model switcher: {e}", severity="error")
        else:
            self.notify("Model switcher not available", severity="warning")
    
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
