"""
Agent Thinking Panel - Display agent thought process
Shows streaming thoughts that collapse to "Thought for X s" when complete
"""

from textual.widgets import Static, Button, LoadingIndicator
from textual.containers import Vertical, Container
from textual import on
from textual.reactive import reactive
from typing import Optional, Dict, List
from datetime import datetime, timedelta


class Thought:
    """Represents a single agent thought"""
    
    def __init__(self, agent_name: str, content: str, started_at: datetime = None):
        self.agent_name = agent_name
        self.content = content
        self.started_at = started_at or datetime.now()
        self.ended_at: Optional[datetime] = None
        self.duration: Optional[float] = None
        self.collapsed: bool = False
    
    def end(self):
        """Mark thought as complete"""
        self.ended_at = datetime.now()
        self.duration = (self.ended_at - self.started_at).total_seconds()
    
    def collapse(self):
        """Collapse thought to summary"""
        self.collapsed = True
    
    def expand(self):
        """Expand thought to show full content"""
        self.collapsed = False
    
    def to_display(self) -> str:
        """Convert thought to display string"""
        if self.collapsed:
            duration_str = f"{self.duration:.1f}s" if self.duration else "..."
            return f"[bold]{self.agent_name}[/bold]: Thought for [cyan]{duration_str}[/cyan]"
        else:
            return f"[bold]{self.agent_name}[/bold]: {self.content}"


class AgentThinkingPanel(Vertical):
    """Panel displaying agent thoughts"""
    
    thoughts = reactive[List[Thought]]([])
    detail_level = reactive("summary")  # summary, detailed, minimal
    auto_collapse = reactive(True)
    
    def __init__(self):
        super().__init__()
        self.border_title = "Agent Thinking"
    
    def compose(self):
        """Compose thinking panel"""
        yield Static(id="thoughts_container")
        
        # Toggle controls
        with Horizontal(id="controls"):
            yield Button("Toggle Expand/Collapse All", id="toggle_expand_btn")
            yield Button("Clear Thoughts", id="clear_btn", variant="error")
        
        # Detail level indicator
        yield Static(id="detail_level_display")
    
    def on_mount(self):
        """Initialize panel on mount"""
        self._update_display()
    
    def watch_thoughts(self, old_thoughts, new_thoughts):
        """Update display when thoughts change"""
        self._update_display()
    
    def watch_detail_level(self, old_level, new_level):
        """Update detail level display"""
        display = self.query_one("#detail_level_display", Static)
        if display:
            display.update(f"[dim]Detail Level: {new_level}[/dim]")
        self._update_display()
    
    def watch_auto_collapse(self, old_auto, new_auto):
        """Handle auto-collapse setting change"""
        if new_auto:
            # Collapse all completed thoughts
            for thought in self.thoughts:
                if thought.ended_at and not thought.collapsed:
                    thought.collapse()
            self._update_display()
    
    def add_thought(self, agent_name: str, content: str) -> Thought:
        """
        Add a new thought
        
        Args:
            agent_name: Name of the agent
            content: Thought content
        
        Returns:
            The created Thought object
        """
        thought = Thought(agent_name, content)
        self.thoughts.append(thought)
        return thought
    
    def end_thought(self, agent_name: str) -> Optional[Thought]:
        """
        End the most recent thought for an agent
        
        Args:
            agent_name: Name of the agent
        
        Returns:
            The ended thought or None
        """
        # Find most recent thought for this agent
        for thought in reversed(self.thoughts):
            if thought.agent_name == agent_name and thought.ended_at is None:
                thought.end()
                
                # Auto-collapse if enabled
                if self.auto_collapse:
                    thought.collapse()
                
                self._update_display()
                return thought
        
        return None
    
    def clear_thoughts(self):
        """Clear all thoughts"""
        self.thoughts = []
        self._update_display()
    
    def toggle_all(self, expand: bool = None):
        """
        Toggle all thoughts to expanded or collapsed
        
        Args:
            expand: If True, expand all. If False, collapse all. 
                     If None, toggle based on first thought.
        """
        if not self.thoughts:
            return
        
        if expand is None:
            # Toggle based on first thought
            expand = self.thoughts[0].collapsed
        
        for thought in self.thoughts:
            if expand:
                thought.expand()
            else:
                thought.collapse()
        
        self._update_display()
    
    def set_detail_level(self, level: str):
        """
        Set detail level
        
        Args:
            level: One of "summary", "detailed", "minimal"
        """
        self.detail_level = level
    
    def _update_display(self):
        """Update the thoughts display"""
        container = self.query_one("#thoughts_container", Static)
        if not container:
            return
        
        # Filter thoughts based on detail level
        filtered_thoughts = self._filter_thoughts()
        
        # Build display text
        display_lines = []
        for thought in filtered_thoughts:
            display_lines.append(thought.to_display())
        
        if not filtered_thoughts:
            display_lines.append("[dim]No thoughts to display[/dim]")
        
        container.update("\n".join(display_lines))
    
    def _filter_thoughts(self) -> List[Thought]:
        """Filter thoughts based on detail level"""
        if self.detail_level == "detailed":
            # Show all thoughts
            return self.thoughts
        elif self.detail_level == "minimal":
            # Only show completed (collapsed) thoughts
            return [t for t in self.thoughts if t.collapsed]
        else:  # summary
            # Show all, but completed ones are collapsed
            return self.thoughts
    
    @on(Button.Pressed, "#toggle_expand_btn")
    def on_toggle_expand(self):
        """Handle toggle expand/collapse button"""
        # Toggle based on first thought
        if self.thoughts:
            expand = self.thoughts[0].collapsed
            self.toggle_all(expand=not expand)
    
    @on(Button.Pressed, "#clear_btn")
    def on_clear(self):
        """Handle clear button"""
        self.clear_thoughts()


class StreamingThought:
    """
    Context manager for streaming thought updates
    
    Usage:
        with panel.streaming_thought("Generator") as thought:
            thought.update("Analyzing code...")
            thought.update("Found potential issue...")
            # Thought automatically ends when context exits
    """
    
    def __init__(self, panel: AgentThinkingPanel, agent_name: str):
        self.panel = panel
        self.agent_name = agent_name
        self.thought = None
        self.buffer = ""
    
    def __enter__(self):
        """Start streaming thought"""
        self.thought = self.panel.add_thought(self.agent_name, "")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End streaming thought"""
        if self.thought:
            self.panel.end_thought(self.agent_name)
    
    def update(self, content: str):
        """
        Update thought content
        
        Args:
            content: Content to add (can contain partial updates)
        """
        if self.thought:
            self.buffer += content
            self.thought.content = self.buffer
            self.panel._update_display()
    
    def append(self, content: str):
        """
        Append to thought content
        
        Args:
            content: Content to append
        """
        self.update(content + "\n")
    
    def complete(self):
        """Mark thought as complete"""
        if self.thought:
            self.thought.content = self.buffer
            self.panel.end_thought(self.agent_name)


if __name__ == "__main__":
    # Demo agent thinking panel
    from textual.app import App
    
    class DemoApp(App):
        def compose(self):
            panel = AgentThinkingPanel()
            yield panel
        
        def on_mount(self):
            panel = self.query_one(AgentThinkingPanel)
            
            # Add some sample thoughts
            panel.add_thought("Generator", "Starting code generation...")
            panel.add_thought("Reviewer", "Waiting for code to review...")
            
            # Simulate streaming
            import time
            thought = panel.add_thought("Architect", "Designing architecture...")
            time.sleep(1)
            panel.end_thought("Architect")
    
    app = DemoApp()
    app.run()
