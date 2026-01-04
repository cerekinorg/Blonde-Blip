"""
Diff Panel - Display file changes with color coding
Shows side-by-side diff with apply/reject buttons
"""

from textual.widgets import Static, Button, TextArea
from textual.containers import Horizontal, Vertical, Container
from textual import on
from textual.reactive import reactive
from typing import Optional, List, Dict
from pathlib import Path


class Diff:
    """Represents a single diff block"""
    
    def __init__(
        self,
        file_path: str,
        line_number: int,
        original: str,
        modified: str,
        change_type: str = "modify"  # modify, insert, delete
    ):
        self.file_path = file_path
        self.line_number = line_number
        self.original = original
        self.modified = modified
        self.change_type = change_type
        self.applied: bool = False
    
    def apply(self):
        """Mark diff as applied"""
        self.applied = True
    
    def reject(self):
        """Mark diff as rejected"""
        self.applied = False
    
    def to_display(self, show_original: bool = False) -> str:
        """
        Convert diff to display string
        
        Args:
            show_original: If True, show original content
        
        Returns:
            Formatted display string
        """
        line_num = f"[dim]{self.line_number:4d}[/dim] "
        
        if self.change_type == "insert":
            return f"{line_num}[bold green]+ {self.modified}[/bold green]"
        elif self.change_type == "delete":
            return f"{line_num}[bold red]- {self.original}[/bold red]"
        else:  # modify
            if show_original:
                return (
                    f"{line_num}[bold red]- {self.original}[/bold red]\n"
                    f"{line_num}[bold green]+ {self.modified}[/bold green]"
                )
            else:
                return f"{line_num}[bold green]+ {self.modified}[/bold green]"
    
    def get_summary(self) -> str:
        """Get summary of this diff"""
        type_str = {
            "insert": "inserted",
            "delete": "deleted",
            "modify": "modified"
        }.get(self.change_type, "changed")
        
        return f"[cyan]{self.file_path}:{self.line_number}[/cyan] {type_str}"


class DiffPanel(Vertical):
    """Panel displaying file diffs"""
    
    diffs = reactive[List[Diff]]([])
    current_file = reactive[Optional[Path]](None)
    show_original = reactive(False)
    
    def __init__(self):
        super().__init__()
        self.border_title = "Diff"
    
    def compose(self):
        """Compose diff panel"""
        # File info
        yield Static(id="file_info")
        
        yield Static()  # Spacer
        
        # Diff display
        yield Static(id="diff_display")
        
        yield Static()  # Spacer
        
        # Controls
        with Horizontal(id="controls"):
            yield Button("Show Original", id="show_original_btn")
            yield Button("Apply All", id="apply_all_btn", variant="primary")
            yield Button("Reject All", id="reject_all_btn", variant="error")
            yield Button("Close", id="close_btn")
    
    def on_mount(self):
        """Initialize panel on mount"""
        self._update_display()
    
    def watch_diffs(self, old_diffs, new_diffs):
        """Update display when diffs change"""
        self._update_display()
    
    def watch_current_file(self, old_file, new_file):
        """Update file info display"""
        display = self.query_one("#file_info", Static)
        if display:
            if new_file:
                applied_count = sum(1 for d in self.diffs if d.applied)
                total_count = len(self.diffs)
                display.update(
                    f"[bold]File:[/bold] {new_file.name}\n"
                    f"[dim]{new_file}[/dim]\n"
                    f"[dim]Changes: {applied_count}/{total_count} applied[/dim]"
                )
            else:
                display.update("[dim]No file selected[/dim]")
    
    def watch_show_original(self, old_show, new_show):
        """Update display when show original changes"""
        self._update_display()
    
    def add_diffs(self, diffs: List[Diff]):
        """
        Add multiple diffs at once
        
        Args:
            diffs: List of Diff objects
        """
        self.diffs.extend(diffs)
    
    def add_diff(self, diff: Diff):
        """
        Add a single diff
        
        Args:
            diff: Diff object to add
        """
        self.diffs.append(diff)
    
    def clear_diffs(self):
        """Clear all diffs"""
        self.diffs = []
        self.current_file = None
        self._update_display()
    
    def load_diff(self, file_path: Path, old_content: str, new_content: str) -> None:
        """
        Load diff from file content
        
        Args:
            file_path: Path to the file
            old_content: Original file content
            new_content: New file content
        """
        self.current_file = file_path
        diffs = parse_simple_diff(str(file_path), old_content, new_content)
        self.diffs = diffs
        self._update_display()
    
    def apply_all(self):
        """Apply all diffs"""
        for diff in self.diffs:
            diff.apply()
        self._update_display()
    
    def reject_all(self):
        """Reject all diffs"""
        for diff in self.diffs:
            diff.reject()
        self._update_display()
    
    def toggle_show_original(self):
        """Toggle showing original content"""
        self.show_original = not self.show_original
    
    def _update_display(self):
        """Update diff display"""
        display = self.query_one("#diff_display", Static)
        if not display:
            return
        
        if not self.diffs:
            display.update("[dim]No changes to display[/dim]")
            return
        
        # Build display text
        display_lines = []
        
        # Group diffs by file
        files = {}
        for diff in self.diffs:
            if diff.file_path not in files:
                files[diff.file_path] = []
            files[diff.file_path].append(diff)
        
        # Display each file's diffs
        for file_path, file_diffs in files.items():
            path = Path(file_path)
            display_lines.append(f"\n[bold cyan]=== {path.name} ===[/bold cyan]")
            
            for diff in file_diffs:
                display_lines.append(diff.to_display(self.show_original))
                
                # Show status
                status_color = "green" if diff.applied else "yellow"
                status_str = "✓ Applied" if diff.applied else "○ Pending"
                display_lines.append(f"    [{status_color}]{status_str}[/{status_color}]")
        
        display.update("\n".join(display_lines))
    
    def get_applied_diffs(self) -> List[Diff]:
        """Get all applied diffs"""
        return [d for d in self.diffs if d.applied]
    
    def get_pending_diffs(self) -> List[Diff]:
        """Get all pending diffs"""
        return [d for d in self.diffs if not d.applied]
    
    def get_summary(self) -> str:
        """Get summary of all diffs"""
        if not self.diffs:
            return "No changes"
        
        applied = len(self.get_applied_diffs())
        pending = len(self.get_pending_diffs())
        total = len(self.diffs)
        
        return f"Total: {total} | Applied: {applied} | Pending: {pending}"
    
    @on(Button.Pressed, "#show_original_btn")
    def on_show_original(self):
        """Handle show original button"""
        self.toggle_show_original()
    
    @on(Button.Pressed, "#apply_all_btn")
    def on_apply_all(self):
        """Handle apply all button"""
        self.apply_all()
    
    @on(Button.Pressed, "#reject_all_btn")
    def on_reject_all(self):
        """Handle reject all button"""
        self.reject_all()
    
    @on(Button.Pressed, "#close_btn")
    def on_close(self):
        """Handle close button"""
        self.clear_diffs()
        # Notify parent to close panel
        self.app.notify("Diff panel closed", severity="information")


def parse_simple_diff(file_path: str, original_content: str, new_content: str) -> List[Diff]:
    """
    Parse simple line-by-line diff
    
    Args:
        file_path: Path to file
        original_content: Original file content
        new_content: New file content
    
    Returns:
        List of Diff objects
    """
    diffs = []
    
    original_lines = original_content.split('\n')
    new_lines = new_content.split('\n')
    
    # Simple line comparison
    max_lines = max(len(original_lines), len(new_lines))
    
    for i in range(max_lines):
        original_line = original_lines[i] if i < len(original_lines) else ""
        new_line = new_lines[i] if i < len(new_lines) else ""
        
        if original_line != new_line:
            # Determine change type
            if not original_line and new_line:
                change_type = "insert"
                content = new_line
            elif original_line and not new_line:
                change_type = "delete"
                content = original_line
            else:
                change_type = "modify"
                diffs.append(Diff(
                    file_path=file_path,
                    line_number=i + 1,
                    original=original_line,
                    modified=new_line,
                    change_type=change_type
                ))
    
    return diffs


if __name__ == "__main__":
    # Demo diff panel
    from textual.app import App
    
    class DemoApp(App):
        def compose(self):
            panel = DiffPanel()
            panel.current_file = Path("example.py")
            
            # Add some sample diffs
            panel.add_diff(Diff(
                file_path="example.py",
                line_number=1,
                original="def old_function():",
                modified="def new_function():",
                change_type="modify"
            ))
            
            panel.add_diff(Diff(
                file_path="example.py",
                line_number=5,
                original="",
                modified="    print('Hello')",
                change_type="insert"
            ))
            
            panel.add_diff(Diff(
                file_path="example.py",
                line_number=10,
                original="    print('Old code')",
                modified="",
                change_type="delete"
            ))
            
            yield panel
    
    app = DemoApp()
    app.run()
