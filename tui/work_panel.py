"""
WorkPanel - Center panel with Chat/Editor modes
Primary work area that toggles between Chat and Editor
"""

from textual.containers import Horizontal, Vertical
from textual.widgets import Static
from textual import on
from textual.reactive import reactive

try:
    from .chat_view import ChatView
    from .editor_view import EditorView
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
            chat_view = ChatView()
            chat_view.id = "chat_view"
            yield chat_view
        else:
            yield Static("Views not available")
    
    def on_mount(self):
        """Initialize on mount"""
        if VIEWS_AVAILABLE:
            self.chat_view = self.query_one("#chat_view", ChatView)
            self.editor_view = EditorView()
        
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
            self.editor_view.remove()
        
        # Ensure chat view is present
        if self.chat_view and self.chat_view not in self.children:
            self.mount(self.chat_view, before=self.children[0])
        
        self.border_title = "Workspace (Chat)"
        self.current_child = self.chat_view
        
        # Update Blip panel
        if self.app:
            try:
                blip_panel = self.app.query_one("BlipPanel")
                blip_panel.set_editor_mode(False)
            except:
                pass
    
    def _switch_to_editor(self):
        """Switch to editor mode"""
        # Remove chat view if present
        if self.chat_view and self.chat_view in self.children:
            self.chat_view.remove()
        
        # Ensure editor view is present
        if self.editor_view and self.editor_view not in self.children:
            self.mount(self.editor_view, before=self.children[0])
        
        self.border_title = "Workspace (Editor)"
        self.current_child = self.editor_view
        
        # Update Blip panel (shows mini file tree)
        if self.app:
            try:
                blip_panel = self.app.query_one("BlipPanel")
                blip_panel.set_editor_mode(True)
            except:
                pass
    
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
