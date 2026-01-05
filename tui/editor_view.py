"""
EditorView - Center panel editor mode with file tree and buffer
"""

from textual.containers import Horizontal, Vertical
from textual.widgets import DirectoryTree, Static, TextArea
from textual import on
from textual.reactive import reactive
from pathlib import Path


class EditorHeader(Static):
    """Editor header showing current mode"""
    
    def __init__(self):
        super().__init__("Mode: EDITOR | Ctrl+E → Chat")
    
    def render(self):
        """Render header"""
        return "[bold #8B949E]" + self.content


class FileTreePane(Vertical):
    """File tree pane for navigation"""
    
    border_title = "Files"
    
    def __init__(self):
        super().__init__()
        self.file_tree = None
    
    def compose(self):
        """Compose file tree pane"""
        yield DirectoryTree(str(Path.cwd()), id="editor_file_tree")
    
    def on_mount(self):
        """Initialize on mount"""
        self.file_tree = self.query_one("#editor_file_tree", DirectoryTree)


class EditorPane(Vertical):
    """Editor pane with code buffer and inline diff"""
    
    border_title = "Editor"
    current_file = reactive("")
    
    def __init__(self):
        super().__init__()
        self.code_buffer = None
        self.line_numbers = None
        self.diff_display = None
    
    def compose(self):
        """Compose editor pane"""
        # Code buffer
        yield TextArea(
            id="code_buffer",
            language="python",
            theme="monokai"
        )
        
        # Inline diff display
        yield Static(id="inline_diff")
    
    def on_mount(self):
        """Initialize on mount"""
        self.code_buffer = self.query_one("#code_buffer", TextArea)
        self.diff_display = self.query_one("#inline_diff", Static)
    
    def load_file(self, file_path: Path):
        """Load file into editor"""
        try:
            content = file_path.read_text()
            self.code_buffer.text = content
            self.current_file = str(file_path)
            self.border_title = f"Editor - {file_path.name}"
        except Exception as e:
            self.diff_display.update(f"[red]Error loading file: {e}[/red]")
    
    def show_inline_diff(self, diff_text: str):
        """Show inline git diff"""
        formatted_diff = self._format_diff(diff_text)
        self.diff_display.update(formatted_diff)
    
    def _format_diff(self, diff_text: str) -> str:
        """Format diff with colors"""
        lines = diff_text.split('\n')
        formatted = []
        
        for line in lines:
            if line.startswith('+'):
                formatted.append(f"[green]{line}[/green]")
            elif line.startswith('-'):
                formatted.append(f"[red]{line}[/red]")
            else:
                formatted.append(f"[dim]{line}[/dim]")
        
        return '\n'.join(formatted)
    
    def watch_current_file(self, old_file: str, new_file: str):
        """Update border title when file changes"""
        if new_file:
            path = Path(new_file)
            self.border_title = f"Editor - {path.name}"


class EditorView(Horizontal):
    """Editor view with file tree and editor pane"""
    
    def __init__(self):
        super().__init__()
        self.file_tree_pane = None
        self.editor_pane = None
    
    def compose(self):
        """Compose editor view"""
        # Header
        yield EditorHeader(id="editor_header")
        
        # File tree and editor side by side
        with Horizontal(id="editor_split"):
            yield FileTreePane()
            yield EditorPane()
    
    def on_mount(self):
        """Initialize on mount"""
        self.file_tree_pane = self.query_one(FileTreePane)
        self.editor_pane = self.query_one(EditorPane)
    
    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected):
        """Handle file selection"""
        path = Path(event.path)
        if path.is_file():
            self.editor_pane.load_file(path)


if __name__ == "__main__":
    # Demo editor view
    from textual.app import App
    
    class DemoApp(App):
        CSS = """
        Screen {
            background: #0D1117;
        }
        EditorView {
            height: 100%;
            background: #0D1117;
        }
        #editor_header {
            text-style: bold;
            color: #8B949E;
            padding: 1;
            background: #0E1621;
        }
        #editor_split {
            height: 1fr;
        }
        FileTreePane {
            width: 30%;
            background: #0E1621;
            border: solid #1E2A38;
        }
        EditorPane {
            flex: 1;
            background: #0D1117;
            border: solid #1E2A38;
        }
        TextArea {
            background: #0D1117;
        }
        """
        
        def compose(self):
            view = EditorView()
            yield view
    
    app = DemoApp()
    app.run()
