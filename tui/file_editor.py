"""
File Editor - Inline file editor with autosave
Edit files in center column with 2-second debounce autosave
"""

from textual.widgets import Static, Button, TextArea, Label
from textual.containers import Vertical, Container
from textual import on
from textual.reactive import reactive
from pathlib import Path
from typing import Optional
from datetime import datetime
import asyncio


class FileEditor(Vertical):
    """File editor component with autosave"""
    
    file_path = reactive[Optional[Path]](None)
    file_content = reactive("")
    is_dirty = reactive(False)
    is_saving = reactive(False)
    autosave_enabled = reactive(True)
    autosave_delay = 2.0  # seconds
    
    def __init__(self):
        super().__init__()
        self.border_title = "File Editor"
        self.autosave_task: Optional[asyncio.Task] = None
        self.last_saved_content = ""
    
    def compose(self):
        """Compose file editor"""
        # File info
        yield Static(id="file_info")
        
        yield Static()  # Spacer
        
        # Text area
        yield TextArea(
            id="editor_textarea",
            language="python",
            theme="monokai",
            show_line_numbers=True,
            tab_behaviour="indent"
        )
        
        yield Static()  # Spacer
        
        # Status bar
        with Horizontal(id="status_bar"):
            yield Static(id="save_status")
            yield Label(id="dirty_indicator")
            yield Static(id="autosave_indicator")
        
        yield Static()  # Spacer
        
        # Actions
        with Horizontal(id="actions"):
            yield Button("Save (Ctrl+S)", id="save_btn", variant="primary")
            yield Button("Revert", id="revert_btn")
            yield Button("Close (Ctrl+Q)", id="close_btn")
    
    def on_mount(self):
        """Initialize editor on mount"""
        self._update_file_info()
        self._update_status()
    
    def watch_file_path(self, old_path, new_path):
        """Handle file path change"""
        self._load_file()
        self._update_file_info()
        self._update_status()
    
    def watch_is_dirty(self, old_dirty, new_dirty):
        """Update dirty indicator"""
        indicator = self.query_one("#dirty_indicator", Label)
        if indicator:
            if new_dirty:
                indicator.update("● [red]Unsaved changes[/red]")
            else:
                indicator.update("● [green]Saved[/green]")
    
    def watch_is_saving(self, old_saving, new_saving):
        """Update save status"""
        save_status = self.query_one("#save_status", Static)
        autosave_indicator = self.query_one("#autosave_indicator", Static)
        
        if save_status:
            if new_saving:
                save_status.update("[dim yellow]Saving...[/dim yellow]")
            else:
                save_status.update("")
        
        if autosave_indicator:
            if self.is_saving:
                autosave_indicator.update("[dim]Autosave pending[/dim]")
            elif not self.is_dirty:
                autosave_indicator.update("[dim green]Autosave complete[/dim green]")
            else:
                autosave_indicator.update("[dim]Autosave pending changes[/dim]")
    
    def _load_file(self):
        """Load file content"""
        if not self.file_path or not self.file_path.exists():
            self.file_content = ""
            return
        
        try:
            with open(self.file_path, 'r') as f:
                self.file_content = f.read()
            self.last_saved_content = self.file_content
            self.is_dirty = False
            
            # Update textarea
            textarea = self.query_one("#editor_textarea", TextArea)
            if textarea:
                textarea.text = self.file_content
        except Exception as e:
            self.file_content = f"Error loading file: {e}"
    
    def _save_file(self, show_notification: bool = True):
        """Save file content"""
        if not self.file_path:
            return False
        
        try:
            # Get content from textarea
            textarea = self.query_one("#editor_textarea", TextArea)
            if not textarea:
                return False
            
            content = textarea.text
            
            # Save to file
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w') as f:
                f.write(content)
            
            self.file_content = content
            self.last_saved_content = content
            self.is_dirty = False
            
            if show_notification:
                self.app.notify(
                    f"Saved: {self.file_path.name}",
                    severity="information"
                )
            
            return True
        except Exception as e:
            if show_notification:
                self.app.notify(
                    f"Error saving file: {e}",
                    severity="error"
                )
            return False
    
    def _update_file_info(self):
        """Update file info display"""
        display = self.query_one("#file_info", Static)
        if display:
            if self.file_path:
                lines = len(self.file_content.split('\n'))
                chars = len(self.file_content)
                size = self._format_size(self.file_path.stat().st_size if self.file_path.exists() else 0)
                
                display.update(
                    f"[bold]File:[/bold] {self.file_path.name}\n"
                    f"[dim]Path: {self.file_path}[/dim]\n"
                    f"[dim]Lines: {lines} | Chars: {chars} | Size: {size}[/dim]"
                )
            else:
                display.update("[dim]No file selected[/dim]")
    
    def _update_status(self):
        """Update status displays"""
        # These are reactive, will update automatically
        pass
    
    def _format_size(self, bytes_size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    def _trigger_autosave(self):
        """Trigger autosave with debounce"""
        if self.autosave_task:
            self.autosave_task.cancel()
        
        async def autosave_delay():
            await asyncio.sleep(self.autosave_delay)
            if self.is_dirty:
                self.is_saving = True
                self._save_file(show_notification=False)
                self.is_saving = False
        
        self.autosave_task = asyncio.create_task(autosave_delay())
    
    def _on_content_changed(self, new_content: str):
        """Handle content change"""
        old_content = self.last_saved_content
        self.file_content = new_content
        
        # Check if dirty
        self.is_dirty = (new_content != old_content)
        
        # Trigger autosave if enabled
        if self.autosave_enabled and self.is_dirty:
            self._trigger_autosave()
    
    @on(TextArea.Changed, "#editor_textarea")
    def on_textarea_changed(self, event: TextArea.Changed):
        """Handle textarea content change"""
        self._on_content_changed(event.text_area.text)
    
    @on(Button.Pressed, "#save_btn")
    def on_save(self):
        """Handle save button"""
        self.is_saving = True
        success = self._save_file(show_notification=True)
        self.is_saving = False
    
    @on(Button.Pressed, "#revert_btn")
    def on_revert(self):
        """Handle revert button"""
        if self.is_dirty and self.last_saved_content:
            textarea = self.query_one("#editor_textarea", TextArea)
            if textarea:
                textarea.text = self.last_saved_content
                self.is_dirty = False
    
    @on(Button.Pressed, "#close_btn")
    def on_close(self):
        """Handle close button"""
        if self.is_dirty:
            # Ask to save before closing
            self.app.notify(
                "Unsaved changes! Please save before closing.",
                severity="warning"
            )
            return
        
        # Clear file
        self.file_path = None
        self.file_content = ""
        self.last_saved_content = ""
        self.is_dirty = False
        
        textarea = self.query_one("#editor_textarea", TextArea)
        if textarea:
            textarea.text = ""
    
    def open_file(self, path: Path):
        """
        Open a file for editing
        
        Args:
            path: Path to file
        """
        self.file_path = path
        self._load_file()
    
    def get_current_content(self) -> str:
        """Get current editor content"""
        textarea = self.query_one("#editor_textarea", TextArea)
        if textarea:
            return textarea.text
        return self.file_content
    
    def set_content(self, content: str):
        """
        Set editor content programmatically
        
        Args:
            content: Content to set
        """
        textarea = self.query_one("#editor_textarea", TextArea)
        if textarea:
            textarea.text = content
        self._on_content_changed(content)


class EditorWithDiff(FileEditor):
    """File editor with diff panel integration"""
    
    def __init__(self, diff_callback=None):
        super().__init__()
        self.diff_callback = diff_callback
    
    def _on_content_changed(self, new_content: str):
        """Handle content change with diff callback"""
        old_content = self.last_saved_content
        
        # Call parent
        super()._on_content_changed(new_content)
        
        # Generate diff if callback provided
        if self.diff_callback and old_content:
            self.diff_callback(old_content, new_content)


if __name__ == "__main__":
    # Demo file editor
    from textual.app import App
    
    class DemoApp(App):
        def compose(self):
            editor = FileEditor()
            
            # Create a test file
            test_file = Path("/tmp/test_file.py")
            test_file.write_text("def hello():\n    print('Hello, World!')")
            
            editor.open_file(test_file)
            yield editor
    
    app = DemoApp()
    app.run()
