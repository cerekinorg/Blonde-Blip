"""
Dashboard - Main TUI application with 3-column layout
Central hub integrating all components with collapsible panels
"""

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Static, DirectoryTree, 
    RichLog, Input, Button, ContentSwitcher, LoadingIndicator
)
from textual.containers import Horizontal, Vertical, Container
from textual import on, events
from textual.reactive import reactive
from pathlib import Path
import json
from typing import Optional, Dict
from datetime import datetime

try:
    from .blip_manager import get_blip_manager
    from .session_manager import get_session_manager
    from .session_panel import SessionPanel
    from .enhanced_settings import EnhancedSettings
    from .model_switcher import ModelSwitcher
    from .file_editor import FileEditor
    from .diff_panel import DiffPanel
    from .agent_thinking_panel import AgentThinkingPanel
    from .context_tracker import ContextTracker
    from .query_processor import get_query_processor, QueryResult
    MANAGERS_AVAILABLE = True
except ImportError:
    try:
        from blip_manager import get_blip_manager
        from session_manager import get_session_manager
        from session_panel import SessionPanel
        from enhanced_settings import EnhancedSettings
        from model_switcher import ModelSwitcher
        from file_editor import FileEditor
        from diff_panel import DiffPanel
        from agent_thinking_panel import AgentThinkingPanel
        from context_tracker import ContextTracker
        from query_processor import get_query_processor, QueryResult
        MANAGERS_AVAILABLE = True
    except ImportError:
        MANAGERS_AVAILABLE = False

CONFIG_DIR = Path.home() / ".blonde"
CONFIG_FILE = CONFIG_DIR / "config.json"


class BlipWidget(Static):
    """Widget displaying Blip mascot with state"""
    
    state = reactive("idle")
    message = reactive("")
    
    def __init__(self):
        super().__init__()
        self.blip_manager = None
        
        if MANAGERS_AVAILABLE:
            self.blip_manager = get_blip_manager()
    
    def watch_state(self, old_state: str, new_state: str) -> None:
        self.update_content()
    
    def watch_message(self, old_message: str, new_message: str) -> None:
        self.update_content()
    
    def update_content(self) -> None:
        if self.blip_manager:
            art = self.blip_manager.get_art(self.state)
            color = self.blip_manager.get_color(self.state)
            content = f"[{color}]{art}[/{color}]\n\n"
            if self.message:
                content += self.message
            self.update(content)
        else:
            self.update("Blip not available")


class WorkingDirectoryDisplay(Static):
    """Display current working directory"""
    
    def __init__(self):
        super().__init__()
        self.current_dir = str(Path.cwd())
        self.border_title = "Location"
    
    def on_mount(self) -> None:
        self.update_content()
    
    def update_content(self) -> None:
        self.update(f"📁 [bold cyan]{self.current_dir}[/bold cyan]")
    
    def set_directory(self, directory: str) -> None:
        self.current_dir = directory
        self.update_content()


class ChatPanel(Vertical):
    """Interactive chat panel with file editor integration"""
    
    messages = reactive[Dict]({})
    current_view = reactive("chat")  # "chat", "editor", "diff"
    
    def __init__(self):
        super().__init__()
        self.border_title = "Chat"
        self.session_manager = None
        self.file_editor = None
        self.diff_panel = None
        
        if MANAGERS_AVAILABLE:
            self.session_manager = get_session_manager()
    
    def compose(self) -> ComposeResult:
        # View mode indicator
        yield Static(id="view_mode_indicator")
        
        with ContentSwitcher(id="view_switcher"):
            # Chat view - Enhanced with inline agent thinking and diff
            with Vertical(id="chat_view"):
                # Prompt input at top (always visible)
                yield Input(placeholder="Type your message here...", id="chat_input")
                
                # Inline agent thinking display
                if MANAGERS_AVAILABLE:
                    yield Static(id="agent_thinking_inline")
                else:
                    yield Static("Agent thinking not available", id="agent_thinking_inline")
                
                # Inline diff display
                if MANAGERS_AVAILABLE:
                    yield Static(id="diff_display_inline")
                else:
                    yield Static("Diff not available", id="diff_display_inline")
                
                # Chat log as main content
                yield RichLog(id="chat_log", wrap=True, highlight=True)
            
            # File editor view
            with Vertical(id="editor_view"):
                if MANAGERS_AVAILABLE:
                    yield FileEditor()
                else:
                    yield Static("File editor not available")
            
            # Diff view (full screen)
            with Vertical(id="diff_view"):
                if MANAGERS_AVAILABLE:
                    yield DiffPanel()
                else:
                    yield Static("Diff panel not available")
    
    def on_mount(self) -> None:
        self.chat_log = self.query_one("#chat_log", RichLog)
        self.view_switcher = self.query_one("#view_switcher", ContentSwitcher)
        self._update_view_mode_indicator()
        self._update_agent_thinking_inline("")
        self._update_diff_display_inline("")
        self.add_message("system", "Welcome to Blonde CLI! Type your message or use Ctrl+S for settings.")
    
    def add_message(self, role: str, content: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        role_colors = {
            "system": "bold cyan",
            "user": "bold green",
            "assistant": "bold magenta",
            "error": "bold red"
        }
        
        color = role_colors.get(role, "white")
        prefix = f"[{color}]{role.upper()}[/{color}] [dim]{timestamp}[/dim]"
        self.chat_log.write(f"{prefix}: {content}")
        
        # Save to session
        if self.session_manager:
            self.session_manager.update_chat_history(role, content)
    
    @on(Input.Submitted, "#chat_input")
    def on_chat_submit(self, event: Input.Submitted) -> None:
        message = event.value.strip()
        if message:
            self.add_message("user", message)
            event.input.value = ""
            self.process_message(message)
    
    def process_message(self, message: str) -> None:
        """Process user message using the agent system"""
        # Update Blip to thinking state
        try:
            blip_widget = self.app.query_one(BlipWidget)
            if blip_widget:
                blip_widget.state = "thinking"
                blip_widget.message = "Processing your request..."
        except:
            pass
        
        # Show loading indicator
        self._show_loading(True)
        
        # Process in background
        def process_query():
            try:
                query_processor = get_query_processor()
                
                # Create progress callback for thinking panel
                def progress_callback(agent: str, status: str):
                    try:
                        # Update right panel thinking
                        thinking_panel = self.app.query_one(AgentThinkingPanel)
                        if thinking_panel:
                            thinking_panel.add_thought(agent, status)
                        
                        # Update inline thinking in center panel
                        self.app.call_from_thread(self._update_agent_thinking_inline, f"{agent}: {status}")
                    except:
                        pass
                
                # Process the query
                result: QueryResult = query_processor.process_query(
                    query=message,
                    context={"current_dir": str(Path.cwd())},
                    progress_callback=progress_callback
                )
                
                # Return to main thread for UI updates
                self.app.call_from_thread(self._on_query_complete, result)
                
            except Exception as e:
                self.app.call_from_thread(self._on_query_error, str(e))
        
        # Run in thread to not block UI
        import threading
        thread = threading.Thread(target=process_query, daemon=True)
        thread.start()
    
    def _show_loading(self, show: bool) -> None:
        """Show or hide loading indicator"""
        try:
            chat_log = self.query_one("#chat_log", RichLog)
            if show:
                chat_log.write("[cyan]Thinking...[/cyan]")
        except:
            pass
    
    def _on_query_complete(self, result: QueryResult) -> None:
        """Handle query processing complete"""
        self._show_loading(False)
        
        # Update Blip
        try:
            blip_widget = self.app.query_one(BlipWidget)
            if blip_widget:
                if result.success:
                    blip_widget.state = "happy"
                    blip_widget.message = "Task complete!"
                else:
                    blip_widget.state = "sad"
                    blip_widget.message = result.error or "Task failed"
        except:
            pass
        
        # Add response to chat
        if result.code_output:
            self.add_message("assistant", f"{result.response}\n\n```\n{result.code_output}\n```")
        else:
            self.add_message("assistant", result.response)
        
        # End any pending thoughts
        try:
            thinking_panel = self.app.query_one(AgentThinkingPanel)
            if thinking_panel:
                thinking_panel.end_thought(result.agent_used)
        except:
            pass
    
    def _on_query_error(self, error: str) -> None:
        """Handle query processing error"""
        self._show_loading(False)
        
        # Update Blip
        try:
            blip_widget = self.app.query_one(BlipWidget)
            if blip_widget:
                blip_widget.state = "sad"
                blip_widget.message = f"Error: {error[:50]}..."
        except:
            pass
        
        self.add_message("error", f"Error processing your request: {error}")
    
    def switch_to_editor(self, file_path: Path) -> None:
        """Switch to file editor view"""
        self.current_view = "editor"
        if self.view_switcher:
            self.view_switcher.current = "editor_view"
            self.border_title = f"File Editor - {file_path.name}"
            
            # Load file in editor
            if MANAGERS_AVAILABLE:
                try:
                    file_editor = self.query_one(FileEditor)
                    if file_editor:
                        file_editor.file_path = file_path
                except:
                    pass
        self._update_view_mode_indicator()
    
    def switch_to_diff(self, file_path: Path, old_content: str, new_content: str) -> None:
        """Switch to diff view"""
        self.current_view = "diff"
        if self.view_switcher:
            self.view_switcher.current = "diff_view"
            self.border_title = f"Diff - {file_path.name}"
            
            # Load diff
            if MANAGERS_AVAILABLE:
                try:
                    diff_panel = self.query_one(DiffPanel)
                    if diff_panel:
                        diff_panel.load_diff(file_path, old_content, new_content)
                except:
                    pass
        
        # Also update inline diff display
        try:
            from difflib import unified_diff
            diff_lines = list(unified_diff(
                old_content.splitlines(),
                new_content.splitlines(),
                fromfile=f"{file_path.name} (old)",
                tofile=f"{file_path.name} (new)",
                lineterm=""
            ))
            diff_text = "\n".join(diff_lines[:20])  # Show first 20 lines
            if len(diff_lines) > 20:
                diff_text += f"\n... ({len(diff_lines) - 20} more lines)"
            self._update_diff_display_inline(diff_text)
        except:
            pass
        
        self._update_view_mode_indicator()
    
    def watch_current_view(self, old_view: str, new_view: str) -> None:
        """Watch for current view changes"""
        self._update_view_mode_indicator()
    
    def switch_to_chat(self) -> None:
        """Switch back to chat view"""
        self.current_view = "chat"
        if self.view_switcher:
            self.view_switcher.current = "chat_view"
            self.border_title = "Chat"
        self._update_view_mode_indicator()
    
    def _update_view_mode_indicator(self) -> None:
        """Update view mode indicator"""
        try:
            indicator = self.query_one("#view_mode_indicator", Static)
            if indicator:
                mode_colors = {
                    "chat": "cyan",
                    "editor": "yellow",
                    "diff": "green"
                }
                color = mode_colors.get(self.current_view, "white")
                indicator.update(f"[{color}]Mode: {self.current_view.upper()}[/{color}] | Press Ctrl+E or Esc to return to chat")
        except:
            pass
    
    def _update_agent_thinking_inline(self, content: str) -> None:
        """Update inline agent thinking display"""
        try:
            thinking_display = self.query_one("#agent_thinking_inline", Static)
            if thinking_display:
                if content:
                    thinking_display.update(f"[bold cyan]Agent Thinking:[/bold cyan]\n{content}")
                else:
                    thinking_display.update("[dim]No active agent thoughts[/dim]")
        except:
            pass
    
    def _update_diff_display_inline(self, content: str) -> None:
        """Update inline diff display"""
        try:
            diff_display = self.query_one("#diff_display_inline", Static)
            if diff_display:
                if content:
                    diff_display.update(f"[bold green]Changes:[/bold green]\n{content}")
                else:
                    diff_display.update("[dim]No changes to display[/dim]")
        except:
            pass


class Dashboard(App):
    """Main 3-column dashboard application"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 1;
        grid-columns: 1fr 3fr 2fr;
    }
    
    #left_panel {
        border: solid $primary;
        background: $panel;
        width: 20;
        min-width: 15;
        max-width: 25;
    }
    
    #left_panel.hidden {
        display: none;
    }
    
    #center_panel {
        border: solid $primary;
        background: $surface;
    }
    
    #right_panel {
        border: solid $primary;
        background: $panel;
    }
    
    #right_panel.hidden {
        display: none;
    }
    
    BlipWidget {
        padding: 1;
        margin: 1;
        height: auto;
    }
    
    ChatPanel {
        height: 100%;
    }
    
    #chat_log {
        height: 1fr;
        border: solid $primary;
    }
    
    #chat_input {
        margin-top: 1;
    }
    
    #agent_thinking_inline {
        height: 8;
        max-height: 12;
        border: solid $primary;
        background: $panel;
    }
    
    #diff_display_inline {
        height: 8;
        max-height: 12;
        border: solid $primary;
        background: $panel;
    }
    
    #view_mode_indicator {
        padding: 1;
        background: $boost;
    }
    
    SessionPanel {
        padding: 1;
    }
    
    Button {
        width: 25;
        margin: 1;
    }
    """
    
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+s", "show_settings", "Settings"),
        ("ctrl+m", "show_model_switcher", "Model Switcher"),
        ("ctrl+l", "toggle_left_panel", "Toggle Left Panel"),
        ("ctrl+r", "toggle_right_panel", "Toggle Right Panel"),
        ("ctrl+e", "switch_to_chat", "Switch to Chat"),
        ("escape", "switch_to_chat", "Switch to Chat"),
        ("f1", "show_help", "Help")
    ]
    
    left_visible = reactive(True)
    right_visible = reactive(True)
    
    def __init__(self, session_id: Optional[str] = None, first_prompt: str = ""):
        super().__init__()
        self.session_id = session_id
        self.first_prompt = first_prompt
        
        self.blip_manager = None
        self.session_manager = None
        
        if MANAGERS_AVAILABLE:
            self.blip_manager = get_blip_manager()
            self.session_manager = get_session_manager()
    
    def compose(self) -> ComposeResult:
        # Left Panel (Collapsible - Ctrl+L) - Only Blip
        with Container(id="left_panel"):
            yield BlipWidget()
        
        # Center Panel - Enhanced with integrated prompt, agents, and diff
        with Container(id="center_panel"):
            yield ChatPanel()
        
        # Right Panel (Collapsible - Ctrl+R) - Session info
        with Container(id="right_panel"):
            session_panel = SessionPanel()
            
            # Update from session data
            if self.session_manager and self.session_manager.current_session_data:
                session_panel.update_from_session(self.session_manager.current_session_data)
            
            yield session_panel
            
            # Agent Thinking Panel (also shown inline in center)
            if MANAGERS_AVAILABLE:
                yield AgentThinkingPanel()
            else:
                yield Static("Agent thinking not available")
    
    def on_mount(self) -> None:
        self.title = "Blonde CLI - Dashboard"
        self.sub_title = "Multi-Agent AI Development Assistant"
        
        # Load panel visibility from config
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    preferences = config.get('preferences', {})
                    self.left_visible = preferences.get('show_left_panel', True)
                    self.right_visible = preferences.get('show_right_panel', True)
                    
                    # Apply visibility
                    left_panel = self.query_one("#left_panel")
                    right_panel = self.query_one("#right_panel")
                    
                    if left_panel:
                        if not self.left_visible:
                            left_panel.add_class("hidden")
                        else:
                            left_panel.remove_class("hidden")
                    
                    if right_panel:
                        if not self.right_visible:
                            right_panel.add_class("hidden")
                        else:
                            right_panel.remove_class("hidden")
        except Exception:
            pass
        
        # Handle first prompt if provided
        if self.first_prompt:
            chat_panel = self.query_one(ChatPanel)
            if chat_panel:
                chat_panel.add_message("user", self.first_prompt)
                # Process the first prompt through agent system
                chat_panel.process_message(self.first_prompt)
        else:
            # Show welcome message
            chat_panel = self.query_one(ChatPanel)
            if chat_panel:
                chat_panel.add_message("system", "Welcome to Blonde CLI! I'm your AI development assistant.\n\nI can help you with:\n• Code generation and implementation\n• Code review and quality analysis\n• Debugging and fixing issues\n• Writing tests\n• Refactoring code\n• Security analysis\n• Architecture design\n• Documentation\n• Performance optimization\n\nType your request or use /commands for special actions.")
        
        # Set Blip to happy
        if self.blip_manager:
            try:
                blip_widget = self.query_one(BlipWidget)
                if blip_widget:
                    blip_widget.message = "Ready to help!"
                    blip_widget.state = "happy"
            except:
                pass
    
    def action_switch_to_chat(self) -> None:
        """Switch center panel back to chat/prompt mode"""
        chat_panel = self.query_one(ChatPanel)
        if chat_panel:
            chat_panel.switch_to_chat()
            self.notify("Switched to chat mode", severity="information")
    
    def action_toggle_left_panel(self) -> None:
        """Toggle left panel visibility"""
        self.left_visible = not self.left_visible
        left_panel = self.query_one("#left_panel")
        
        if left_panel:
            if self.left_visible:
                left_panel.remove_class("hidden")
                self.notify("Left panel: Visible")
            else:
                left_panel.add_class("hidden")
                self.notify("Left panel: Hidden")
    
    def action_toggle_right_panel(self) -> None:
        """Toggle right panel visibility"""
        self.right_visible = not self.right_visible
        right_panel = self.query_one("#right_panel")
        
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
            settings_screen = EnhancedSettings()
            self.push_screen(settings_screen)
        else:
            self.notify("Settings not available - managers not loaded", severity="error")
    
    def action_show_model_switcher(self) -> None:
        """Show model switcher modal"""
        if MANAGERS_AVAILABLE:
            model_switcher = ModelSwitcher()
            self.push_screen(model_switcher)
        else:
            self.notify("Model switcher not available - managers not loaded", severity="error")
    
    def action_show_help(self) -> None:
        """Show help"""
        help_text = """
        [bold cyan]Blonde CLI - Dashboard Help[/bold cyan]
        
        [cyan]Keyboard Shortcuts:[/cyan]
        Ctrl+L - Toggle Left Panel (Blip)
        Ctrl+R - Toggle Right Panel (Session + Agent Thinking)
        Ctrl+E / Esc - Switch to Chat/Prompt Mode
        Ctrl+S - Enhanced Settings (5 tabs)
        Ctrl+M - Model/Provider Switcher
        F1 - Help
        Ctrl+Q - Quit
        
        [cyan]Features:[/cyan]
        • 3-column layout with collapsible panels
        • Left panel: Blip mascot (Terminal pet)
        • Center panel: Prompt input, agent thinking, diff, and chat/editor
        • Right panel: Session info and agent thinking
        • Real-time session information and cost tracking
        • Interactive chat with file editor and diff view
        • Agent thinking panel with streaming thoughts
        • Enhanced settings with 5 comprehensive tabs
        • Quick model/provider switcher
        """
        self.notify(help_text, title="Help", severity="information")
    
    def update_session_info(self):
        """Update all panels with current session data"""
        if not self.session_manager or not self.session_manager.current_session_data:
            return
        
        session_data = self.session_manager.current_session_data
        
        # Update session panel
        try:
            session_panel = self.query_one(SessionPanel)
            if session_panel:
                session_panel.update_from_session(session_data)
        except:
            pass
        
        # Update agent thinking panel
        try:
            thinking_panel = self.query_one(AgentThinkingPanel)
            if thinking_panel:
                thinking_panel.update_session_data(session_data)
        except:
            pass
    
    def update_blip_message(self, message: str, state: str = "idle"):
        """Update Blip widget with message and state"""
        blip_widget = self.query_one(BlipWidget)
        if blip_widget:
            blip_widget.message = message
            blip_widget.state = state


def launch_dashboard(session_id: Optional[str] = None, first_prompt: str = ""):
    """
    Launch the dashboard
    
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
