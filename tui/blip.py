"""
Blip - The Blonde CLI Mascot (Refactored for Character System)

A friendly character that helps guide users through Blonde CLI.
Blip shows different emotions and states through animations.

This file now uses the BlipManager system for character switching
while maintaining backward compatibility with existing code.
"""

from pathlib import Path
from typing import Optional
import time

# Import the character management system
try:
    from tui.blip_manager import BlipManager, get_blip_manager
    BLIP_MANAGER_AVAILABLE = True
except ImportError:
    BLIP_MANAGER_AVAILABLE = False
    print("Warning: BlipManager not available, using fallback")


class Blip:
    """
    Blip is the friendly mascot of Blonde CLI.
    This class wraps the BlipManager for backward compatibility.
    
    It shows different states and emotions through ASCII art animations.
    Multiple characters are supported: axolotl, wisp, inkling, sprout.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize Blip with optional config path
        
        Args:
            config_path: Path to config file for character preferences
        """
        if BLIP_MANAGER_AVAILABLE:
            self.manager = get_blip_manager()
        else:
            # Fallback if manager not available
            self.manager = None
            self.current_state = "idle"
            self.animation_frame = 0
    
    def get_character_name(self) -> str:
        """Get the name of the current character"""
        if self.manager:
            return self.manager.current_character_name
        return "axolotl"
    
    def get_character_info(self):
        """Get information about the current character"""
        if self.manager:
            return self.manager.get_character_info()
        return None
    
    def switch_character(self, character_name: str) -> bool:
        """Switch to a different character"""
        if self.manager:
            return self.manager.switch_character(character_name)
        return False
    
    def list_characters(self):
        """List available characters"""
        if self.manager:
            return self.manager.list_characters()
        return {}

    def get_art(self, state: str = "idle") -> str:
        """Get ASCII art for a state"""
        if self.manager:
            return self.manager.get_art(state)
        return "Blip not available"

    def get_color(self, state: str = "idle") -> str:
        """Get color for a state"""
        if self.manager:
            return self.manager.get_color(state)
        return "white"

    def advance_frame(self):
        """Advance to next animation frame"""
        if self.manager:
            self.manager.advance_frame()
        else:
            self.animation_frame += 1

    def show(
        self,
        message: str,
        state: str = "idle",
        animate: bool = False,
        duration: Optional[float] = None
    ):
        """
        Display Blip with a message

        Args:
            message: Message to display
            state: Blip's emotional state
            animate: Whether to animate
            duration: Animation duration in seconds (defaults to manager setting)
        """
        if self.manager:
            self.manager.show(message, state, animate, duration)
        else:
            # Fallback
            print(f"[{state.upper()}] {message}")

    def say(self, message: str, state: str = "idle"):
        """Simple speech from Blip"""
        self.show(message, state)

    def think(self, message: str):
        """Blip is thinking"""
        self.show(message, "thinking", animate=True)

    def work(self, message: str):
        """Blip is working on something"""
        self.show(message, "working", animate=True)

    def happy(self, message: str):
        """Blip is happy"""
        self.show(message, "happy")

    def excited(self, message: str):
        """Blip is excited"""
        self.show(message, "excited", animate=True)

    def error(self, message: str):
        """Blip encountered an error"""
        self.show(message, "error")

    def success(self, message: str):
        """Blip is celebrating success"""
        self.show(message, "success")

    def confused(self, message: str):
        """Blip is confused"""
        self.show(message, "confused")

    def love(self, message: str):
        """Blip shows love"""
        self.show(message, "love")

    def explain_what_is_happening(
        self,
        task: str,
        details: str = "",
        what_user_needs: str = ""
    ):
        """
        Blip explains what is happening in the program

        Args:
            task: What task is being performed
            details: Additional details about the task
            what_user_needs: What the user needs to do (if anything)
        """
        if self.manager:
            self.manager.explain_what_is_happening(task, details, what_user_needs)
        else:
            message = f"Task: {task}"
            if details:
                message += f"\nDetails: {details}"
            if what_user_needs:
                message += f"\nNeed: {what_user_needs}"
            self.show(message, "working", animate=True)

    def introduce(self):
        """Introduce Blip to the user"""
        if self.manager:
            self.manager.introduce()
        else:
            self.show("Hi! I'm Blip, your assistant!", "happy")

    def show_agent_status(self, agent_name: str, status: str, message: str = ""):
        """
        Show what an agent is doing

        Args:
            agent_name: Name of the agent
            status: Current status (working, waiting, done, error)
            message: Optional message from the agent
        """
        if self.manager:
            self.manager.show_agent_status(agent_name, status, message)
        else:
            msg = f"{agent_name}: {status}"
            if message:
                msg += f" - {message}"
            self.show(msg, "working")

    def show_multi_agent_status(self, agents: list):
        """
        Show status of multiple agents

        Args:
            agents: List of dicts with keys: name, status, message
        """
        if self.manager:
            self.manager.show_multi_agent_status(agents)
        else:
            # Fallback
            msg = "\n".join([f"{a['name']}: {a['status']}" for a in agents])
            self.show(msg, "working")


# Global Blip instance for backward compatibility
blip = Blip()


if __name__ == "__main__":
    # Demo Blip
    blip = Blip()

    print("=== Blip Demo ===\n")

    blip.introduce()
    time.sleep(2)

    blip.think("I'm thinking about what to show you next...")
    time.sleep(2)

    blip.happy("I figured it out!")
    time.sleep(1)

    blip.work("Generator agent is creating your code...")
    time.sleep(1)

    blip.show_agent_status("generator", "working", "Writing API endpoints")
    time.sleep(1)

    agents = [
        {"name": "generator", "status": "working", "message": "Creating initial code"},
        {"name": "reviewer", "status": "waiting", "message": ""},
        {"name": "tester", "status": "waiting", "message": ""}
    ]
    blip.show_multi_agent_status(agents)
    time.sleep(1)

    blip.success("All done! Your code is ready! 🎉")
