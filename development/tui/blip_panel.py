"""
BlipPanel - Left panel with movable Blip terminal pet
Only contains Blip sprite and minimal status text
"""

from textual.containers import Vertical, Container
from textual.widgets import Static, DirectoryTree
from textual import on
from textual.reactive import reactive
from pathlib import Path

try:
    from .blip_manager import get_blip_manager
    MANAGERS_AVAILABLE = True
except ImportError:
    try:
        from blip_manager import get_blip_manager
        MANAGERS_AVAILABLE = True
    except ImportError:
        MANAGERS_AVAILABLE = False


class BlipSprite(Static):
    """Movable Blip ASCII sprite that moves gradually based on agent state"""
    
    vertical_position = reactive("middle")
    target_position = reactive("middle")
    animation_timer = None
    animation_step_index = 0
    animation_positions = ["top", "middle", "bottom"]
    target_position = reactive("middle")
    animation_timer = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blip_manager = None
        self.current_art = ""
        
        # Animation support
        self.animation_step_index = 0
        self.animation_positions = ["top", "middle", "bottom"]
        
        if MANAGERS_AVAILABLE:
            self.blip_manager = get_blip_manager()
    
    def on_mount(self):
        """Initialize on mount"""
        self._update_art()
    
    def _update_art(self):
        """Update Blip ASCII art based on current position"""
        if not self.blip_manager or not self.blip_manager.current_character:
            return
        
        # Map position to state
        position_to_state = {
            "top": "idle",
            "middle": "thinking",
            "bottom": "error"
        }
        
        state = position_to_state.get(self.vertical_position, "idle")
        art = self.blip_manager.current_character.get_art(state)
        color = self.blip_manager.current_character.get_color(state)
        
        # Update display with colored art
        self.update(f"[{color}]{art}[/{color}]")
    
    def watch_vertical_position(self, old_pos, new_pos):
        """Update Blip art based on position"""
        self._update_art()
    
    def animate_to_position(self, target_pos: str):
        """Gradually animate to target position"""
        self.target_position = target_pos
        
        # Cancel existing animation
        if self.animation_timer and self.animation_timer.is_alive:
            self.animation_timer.cancel()
        
        # Start animation
        self.animation_step_index = 0
        self.animation_timer = self.set_timer(0.3, self._animate_step)
    
    def _animate_step(self):
        """Single animation step"""
        target_idx = self.animation_positions.index(self.target_position)
        current_idx = self.animation_positions.index(self.vertical_position)
        
        if current_idx < target_idx:
            # Move down one step
            next_idx = min(current_idx + 1, target_idx)
            self.vertical_position = self.animation_positions[next_idx]
            
            # Continue animation
            if self.vertical_position != self.target_position:
                self.animation_step_index += 1
                self.animation_timer = self.set_timer(0.3, self._animate_step)
            else:
                # Animation complete
                self.animation_timer = None
        elif current_idx > target_idx:
            # Move up one step
            next_idx = max(current_idx - 1, target_idx)
            self.vertical_position = self.animation_positions[next_idx]
            
            # Continue animation
            if self.vertical_position != self.target_position:
                self.animation_step_index += 1
                self.animation_timer = self.set_timer(0.3, self._animate_step)
            else:
                # Animation complete
                self.animation_timer = None
        # Already at target position
        else:
            self.animation_timer = None
    
    def set_state(self, state: str):
        """Set Blip state (idle, working, error, thinking, happy)"""
        # Map state to vertical position
        state_to_position = {
            "idle": "top",
            "thinking": "middle",
            "working": "middle",
            "error": "bottom",
            "sad": "bottom",
            "happy": "top",
            "excited": "top"
        }
        self.vertical_position = state_to_position.get(state, "middle")


class BlipStatusText(Static):
    """Minimal status text below Blip (1-2 lines max)"""
    
    status = reactive("")
    
    def watch_status(self, old_status: str, new_status: str):
        """Update status text"""
        self.update(new_status)


class BlipPanel(Vertical):
    """Left panel containing Blip companion"""
    
    border_title = "Blip"
    blip_state = reactive("idle")
    status_message = reactive("Awaiting input")
    editor_mode = reactive(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blip_sprite = None
        self.status_text = None
        self.mini_file_tree = None
    
    def compose(self):
        """Compose Blip panel"""
        # Blip sprite (movable)
        yield BlipSprite(id="blip_sprite")
        
        # Status text
        yield BlipStatusText(self.status_message, id="blip_status")
        
        # Mini file tree (only visible in editor mode)
        yield DirectoryTree(str(Path.cwd()), id="mini_file_tree")
    
    def on_mount(self):
        """Initialize on mount"""
        self.blip_sprite = self.query_one("#blip_sprite", BlipSprite)
        self.status_text = self.query_one("#blip_status", BlipStatusText)
        self.mini_file_tree = self.query_one("#mini_file_tree", DirectoryTree)
        
        # Hide mini file tree initially
        self.mini_file_tree.display = False
    
    def watch_blip_state(self, old_state: str, new_state: str):
        """Update Blip state"""
        if self.blip_sprite:
            self.blip_sprite.set_state(new_state)
    
    def watch_status_message(self, old_msg: str, new_msg: str):
        """Update status message"""
        if self.status_text:
            self.status_text.status = new_msg
    
    def add_agent_thinking(self, thinking: str):
        """Add agent thinking message (for multi-agent system)"""
        self.status_message = thinking[:50]
    
    def update_status(self, state: str, message: str):
        """Update Blip state and status message, trigger gradual animation"""
        self.blip_state = state
        self.status_message = message[:50]  # Keep it short (1-2 lines)
        
        # Trigger gradual animation
        state_to_position = {
            "idle": "top",
            "happy": "top",
            "excited": "top",
            "thinking": "middle",
            "working": "middle",
            "confused": "middle",
            "error": "bottom",
            "sad": "bottom",
            "surprised": "top"
        }
        target_pos = state_to_position.get(state, "middle")
        
        # Trigger animation via BlipSprite
        if self.blip_sprite:
            self.blip_sprite.animate_to_position(target_pos)
    
    def set_editor_mode(self, enabled: bool):
        """Enable/disable editor mode (shows mini file tree)"""
        self.editor_mode = enabled


if __name__ == "__main__":
    # Demo Blip panel
    from textual.app import App
    
    class DemoApp(App):
        CSS = """
        Screen {
            background: #0E1621;
        }
        BlipPanel {
            width: 24;
            background: #0E1621;
            border: solid #1E2A38;
            padding: 1;
        }
        BlipSprite {
            text-align: center;
            height: 8;
        }
        BlipStatusText {
            text-align: center;
            text-style: bold;
            color: #C9D1D9;
            margin: 1 0;
        }
        DirectoryTree {
            display: none;
        }
        """
        
        def compose(self):
            panel = BlipPanel()
            yield panel
        
        def on_mount(self):
            import time
            panel = self.query_one(BlipPanel)
            
            states = [
                ("idle", "Awaiting input"),
                ("thinking", "Analyzing repo..."),
                ("working", "3 files modified"),
                ("happy", "Task complete!"),
                ("error", "Error occurred")
            ]
            
            for state, msg in states:
                panel.update_status(state, msg)
                time.sleep(2)
    
    app = DemoApp()
    app.run()
