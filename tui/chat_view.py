"""
ChatView - Center panel chat mode with conversation stream
"""

from textual.containers import Vertical
from textual.widgets import RichLog, Input, Static
from textual import on
from textual.reactive import reactive
from datetime import datetime
from typing import Dict, List, Optional


class ChatMessage(Static):
    """Individual chat message component"""
    
    def __init__(self, role: str, content: str, timestamp: str = None):
        super().__init__()
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now().strftime("%H:%M:%S")
    
    def render(self):
        """Render message with appropriate styling"""
        role_colors = {
            "user": "#C9D1D9",
            "assistant": "#C9D1D9",
            "system": "#8B949E",
            "error": "#F85149"
        }
        
        color = role_colors.get(self.role, "#C9D1D9")
        role_label = self.role.upper()
        
        # Format message
        return f"[{color}][bold]{role_label}[/{color}] [dim]{self.timestamp}[/dim]\n{self.content}"


class AgentThinkingBlock(Static):
    """Collapsible agent thinking block"""
    
    thinking = reactive("")
    expanded = reactive(True)
    
    def __init__(self):
        super().__init__()
        self.collapsed_content = ""
    
    def watch_thinking(self, old_thinking: str, new_thinking: str):
        """Update thinking content"""
        if new_thinking:
            self.collapsed_content = f"[dim]▸ Thought for {len(new_thinking)} chars[/dim]"
            self.update(self._format_thinking(new_thinking) if self.expanded else self.collapsed_content)
        else:
            self.update("")
    
    def watch_expanded(self, old_expanded: bool, new_expanded: bool):
        """Toggle expanded/collapsed state"""
        if self.thinking:
            content = self._format_thinking(self.thinking) if new_expanded else self.collapsed_content
            self.update(content)
    
    def _format_thinking(self, thinking: str) -> str:
        """Format thinking content"""
        return f"[dim #7D8590]Agent Thinking:[/dim #7D8590]\n{thinking}"
    
    def toggle(self):
        """Toggle expanded state"""
        self.expanded = not self.expanded


class DiffCard(Static):
    """Inline git diff card as summary"""
    
    def __init__(self, file_path: str, added: int, removed: int, diff_summary: str):
        super().__init__()
        self.file_path = file_path
        self.added = added
        self.removed = removed
        self.diff_summary = diff_summary
    
    def render(self):
        """Render diff card"""
        header = f"[bold cyan]{self.file_path}[/bold cyan]"
        stats = f"[dim][green]+{self.added}[/green] [red]-{self.removed}[/red][/dim]"
        
        content = f"""{header}
{stats}

{self.diff_summary}"""
        
        return f"""[on #0B1220]{content}[/on #0B1221]"""
    
    def on_click(self):
        """Handle click to expand diff"""
        self.app.notify(f"Full diff for {self.file_path} coming soon!", severity="information")


class ChatView(Vertical):
    """Chat view with message stream and input"""
    
    border_title = "CHAT"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages: List[ChatMessage] = []
        self.chat_log = None
        self.chat_input = None
    
    def compose(self):
        """Compose chat view"""
        # Header
        yield Static("Mode: CHAT | Ctrl+E → Editor", id="chat_header")
        
        # Chat log (scrollable message stream)
        yield RichLog(
            id="chat_log",
            wrap=True,
            highlight=True,
            auto_scroll=True,
            markup=True
        )
        
        # Input at bottom
        yield Input(
            placeholder="Type your message...",
            id="chat_input"
        )
    
    def on_mount(self):
        """Initialize on mount"""
        self.chat_log = self.query_one("#chat_log", RichLog)
        self.chat_input = self.query_one("#chat_input", Input)
        self.chat_input.focus()
    
    def add_message(self, role: str, content: str):
        """Add message to chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        role_colors = {
            "user": "bold green",
            "assistant": "bold magenta",
            "system": "bold cyan",
            "error": "bold red"
        }
        
        color = role_colors.get(role, "white")
        prefix = f"[{color}]{role.upper()}[/{color}] [dim]{timestamp}[/dim]"
        
        self.chat_log.write(f"{prefix}: {content}")
        self.messages.append({"role": role, "content": content, "timestamp": timestamp})
    
    def add_agent_thinking(self, thinking: str):
        """Add agent thinking block"""
        thinking_block = AgentThinkingBlock()
        thinking_block.thinking = thinking
        self.chat_log.write(thinking_block.render())
    
    def add_diff_card(self, file_path: str, added: int, removed: int, diff_summary: str):
        """Add inline diff card"""
        diff_card = DiffCard(file_path, added, removed, diff_summary)
        self.chat_log.write(diff_card.render())
    
    def clear_chat(self):
        """Clear chat log"""
        self.chat_log.clear()
        self.messages = []


if __name__ == "__main__":
    # Demo chat view
    from textual.app import App
    
    class DemoApp(App):
        CSS = """
        Screen {
            background: #0D1117;
        }
        ChatView {
            height: 100%;
            background: #0D1117;
        }
        #chat_header {
            text-style: bold;
            color: #8B949E;
            padding: 1;
            background: #0E1621;
        }
        #chat_log {
            height: 1fr;
            background: #0D1117;
            border: solid #1E2A38;
        }
        #chat_input {
            margin-top: 1;
            height: 3;
        }
        """
        
        def compose(self):
            view = ChatView()
            yield view
        
        def on_mount(self):
            chat_view = self.query_one(ChatView)
            chat_view.add_message("system", "Welcome to Blonde CLI!")
            chat_view.add_message("user", "Help me create a REST API")
            chat_view.add_agent_thinking("Analyzing request...\nIdentifying requirements...\nPlanning architecture...")
            chat_view.add_message("assistant", "I'll help you create a REST API. Let me start by analyzing your project structure.")
            chat_view.add_diff_card("api.py", 45, 12, "+ Added POST /users endpoint\n- Removed deprecated authentication")
    
    app = DemoApp()
    app.run()
