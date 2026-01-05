"""
Fixed WorkPanel - Center panel with Chat/Editor modes
Primary work area that toggles between Chat and Editor
"""

from textual.containers import Horizontal, Vertical
from textual.widgets import Static
from textual import on
from textual.reactive import reactive

try:
    from tui.chat_view import ChatView
    from tui.editor_view import EditorView
    VIEWS_AVAILABLE = True
except ImportError:
    VIEWS_AVAILABLE = False


class WorkPanel(Vertical):
    """Center panel - primary work area with Chat/Editor modes"""
    
    border_title = "Workspace"
    current_mode = reactive("chat")  # chat, editor
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_view = None
        self.editor_view = None
        self.current_child = None
    
    def compose(self):
        """Compose work panel - show one view at a time"""
        # Initially show chat view
        if VIEWS_AVAILABLE:
            self.chat_view = ChatView()
            self.chat_view.id = "chat_view"
            yield self.chat_view
        else:
            yield Static("Views not available")
    
    def on_mount(self):
        """Initialize on mount"""
        if VIEWS_AVAILABLE:
            # Chat view is already created and mounted
            self.chat_view = self.query_one("#chat_view", ChatView)
            # Create editor view but don't mount it yet
            try:
                self.editor_view = EditorView()
            except Exception as e:
                print(f"Error creating EditorView: {e}")
                self.editor_view = None
        
        # Start in chat mode
        self._switch_to_chat()
    
    def watch_current_mode(self, old_mode: str, new_mode: str):
        """Watch for mode changes"""
        if new_mode == "chat":
            self._switch_to_chat()
        elif new_mode == "editor":
            self._switch_to_editor()
    
    def _switch_to_chat(self):
        """Switch to chat mode"""
        # Remove editor view if present
        if self.editor_view and self.editor_view in self.children:
            try:
                self.editor_view.remove()
            except Exception as e:
                print(f"Error removing editor view: {e}")
        
        # Ensure chat view is present
        if self.chat_view and self.chat_view not in self.children:
            try:
                if len(self.children) > 0:
                    self.mount(self.chat_view, before=self.children[0])
                else:
                    self.mount(self.chat_view)
            except Exception as e:
                print(f"Error mounting chat view: {e}")
        
        self.border_title = "Workspace (Chat)"
        self.current_child = self.chat_view
        
        # Update Blip panel
        if self.app:
            try:
                blip_panel = self.app.query_one("BlipPanel")
                blip_panel.set_editor_mode(False)
            except Exception as e:
                print(f"Error updating blip panel: {e}")
    
    def _switch_to_editor(self):
        """Switch to editor mode"""
        # Remove chat view if present
        if self.chat_view and self.chat_view in self.children:
            try:
                self.chat_view.remove()
            except Exception as e:
                print(f"Error removing chat view: {e}")
        
        # Ensure editor view is present
        if self.editor_view and self.editor_view not in self.children:
            try:
                if len(self.children) > 0:
                    self.mount(self.editor_view, before=self.children[0])
                else:
                    self.mount(self.editor_view)
            except Exception as e:
                print(f"Error mounting editor view: {e}")
        
        self.border_title = "Workspace (Editor)"
        self.current_child = self.editor_view
        
        # Update Blip panel (shows mini file tree)
        if self.app:
            try:
                blip_panel = self.app.query_one("BlipPanel")
                blip_panel.set_editor_mode(True)
            except Exception as e:
                print(f"Error updating blip panel: {e}")
    
    def toggle_mode(self):
        """Toggle between chat and editor modes"""
        self.current_mode = "editor" if self.current_mode == "chat" else "chat"
    
    def get_chat_view(self):
        """Get chat view instance"""
        return self.chat_view
    
    def get_editor_view(self):
        """Get editor view instance"""
        return self.editor_view


if __name__ == "__main__":
    # Demo work panel
    from textual.app import App
    
    class DemoApp(App):
        CSS = """
        Screen {
            background: #0D1117;
        }
        WorkPanel {
            height: 100%;
            background: #0D1117;
            border: solid #1E2A38;
        }
        """
        
        def compose(self):
            panel = WorkPanel()
            yield panel
        
        def on_key(self, event):
            if event.key == "ctrl+e":
                work_panel = self.query_one(WorkPanel)
                work_panel.toggle_mode()
    
    app = DemoApp()
    app.run()
