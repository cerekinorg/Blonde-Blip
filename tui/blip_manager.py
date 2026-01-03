"""
Blip Manager - Manages Blip character selection and operations
Provides unified interface for all Blip operations
"""

from pathlib import Path
from typing import Optional, Dict, Any
import json
import time
from rich.console import Console

from tui.blip_characters import (
    CharacterArt,
    get_character,
    list_characters,
    get_default_character
)

console = Console()


class BlipManager:
    """Manages Blip character selection and operations"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (Path.home() / ".blonde" / "config.json")
        self.current_character_name = "axolotl"
        self.current_character: Optional[CharacterArt] = None
        self.animation_speed = 0.3  # seconds per frame
        self.animation_frame = 0
        
        self._load_config()
        self._load_character()
    
    def _load_config(self):
        """Load character preference from config"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                # Load character preference
                preferences = config.get('preferences', {})
                self.current_character_name = preferences.get(
                    'blip_character',
                    get_default_character()
                )
                
                # Load animation speed
                self.animation_speed = preferences.get(
                    'blip_animation_speed',
                    0.3
                )
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load blip config: {e}[/yellow]")
        else:
            self.current_character_name = get_default_character()
    
    def _load_character(self):
        """Load the current character art"""
        self.current_character = get_character(self.current_character_name)
        if not self.current_character:
            console.print(f"[yellow]Character '{self.current_character_name}' not found, using default[/yellow]")
            self.current_character_name = get_default_character()
            self.current_character = get_character(self.current_character_name)
    
    def _save_config(self):
        """Save character preference to config"""
        try:
            config = {}
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
            
            # Update preferences
            if 'preferences' not in config:
                config['preferences'] = {}
            
            config['preferences']['blip_character'] = self.current_character_name
            config['preferences']['blip_animation_speed'] = self.animation_speed
            
            # Save
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            console.print(f"[green]✓ Saved Blip character: {self.current_character_name}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to save Blip config: {e}[/red]")
    
    def switch_character(self, character_name: str) -> bool:
        """Switch to a different character"""
        character = get_character(character_name)
        
        if not character:
            console.print(f"[red]Character '{character_name}' not found[/red]")
            return False
        
        self.current_character_name = character_name
        self.current_character = character
        self._save_config()
        
        console.print(f"[green]✓ Switched to Blip: {character_name}[/green]")
        console.print(f"[dim]Personality: {character.personality}[/dim]")
        
        return True
    
    def list_characters(self) -> Dict[str, str]:
        """List available characters with descriptions"""
        result = {}
        for name in list_characters():
            character = get_character(name)
            if character:
                result[name] = f"{character.description}\nPersonality: {character.personality}"
        return result
    
    def get_art(self, state: str = "idle") -> str:
        """Get ASCII art for current state"""
        if not self.current_character:
            return "Blip not available"
        
        return self.current_character.get_art(state, self.animation_frame)
    
    def get_color(self, state: str = "idle") -> str:
        """Get color for current state"""
        if not self.current_character:
            return "white"
        
        return self.current_character.get_color(state)
    
    def get_character_info(self) -> Dict[str, Any]:
        """Get information about current character"""
        if not self.current_character:
            return {}
        
        return {
            "name": self.current_character.name,
            "description": self.current_character.description,
            "personality": self.current_character.personality,
            "states": list(self.current_character.states.keys())
        }
    
    def advance_frame(self):
        """Advance to next animation frame"""
        self.animation_frame += 1
    
    def set_animation_speed(self, speed: float):
        """Set animation speed (seconds per frame)"""
        self.animation_speed = max(0.1, min(2.0, speed))
        self._save_config()
    
    def animate(self, duration: float = None):
        """Run animation loop for a duration"""
        duration = duration or self.animation_speed
        time.sleep(duration)
        self.advance_frame()
    
    def show(
        self,
        message: str,
        state: str = "idle",
        animate: bool = False,
        duration: float = None
    ):
        """
        Display Blip with a message

        Args:
            message: Message to display
            state: Blip's emotional state
            animate: Whether to animate
            duration: Animation duration in seconds
        """
        from rich.text import Text
        from rich.panel import Panel
        
        if animate:
            frames = self.current_character.states.get(state, [""])
            for i in range(len(frames)):
                self.animation_frame = i
                self._render(message, state)
                self.animate(duration or self.animation_speed)
        else:
            self.animation_frame = 0
            self._render(message, state)
    
    def _render(self, message: str, state: str):
        """Render Blip with message"""
        from rich.text import Text
        from rich.panel import Panel
        
        art = self.get_art(state)
        color = self.get_color(state)

        # Create text with art
        blip_text = Text(art, style=color)

        # Create panel with Blip and message
        content = Text()
        content.append(blip_text)
        content.append("\n\n")
        content.append(message, style="white")

        panel = Panel(
            content,
            title=f"[bold]Blip - {self.current_character.name}[/bold]",
            border_style=color,
            padding=(1, 2)
        )

        console.print(panel)
    
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
        message = ""

        if task:
            message += f"🎯 [bold]{task}[/bold]\n\n"

        if details:
            message += f"📝 {details}\n\n"

        if what_user_needs:
            message += f"✨ {what_user_needs}\n"

        self.show(message.strip(), "working", animate=True)
    
    def introduce(self):
        """Introduce Blip to the user"""
        message = f"""
Hi! I'm [bold]Blip - {self.current_character.name}[/bold] 👋

{self.current_character.description}

I'm your friendly assistant here to guide you through Blonde CLI.
I'll help you understand what's happening, show you what the agents
are doing, and explain what you need to do next.

Let me show you around!
        """
        self.show(message.strip(), "happy")
    
    def show_agent_status(self, agent_name: str, status: str, message: str = ""):
        """
        Show what an agent is doing

        Args:
            agent_name: Name of the agent
            status: Current status (working, waiting, done, error)
            message: Optional message from the agent
        """
        agent_icons = {
            "generator": "🧱",
            "reviewer": "🔍",
            "tester": "🧪",
            "refactorer": "🔨",
            "documenter": "📝",
            "architect": "🏗️",
            "security": "🔒",
            "debugger": "🐛"
        }

        icon = agent_icons.get(agent_name.lower(), "🤖")
        status_colors = {
            "working": "bright_yellow",
            "waiting": "dim",
            "done": "bright_green",
            "error": "bright_red"
        }

        color = status_colors.get(status, "white")
        status_msg = f"[{color}]{status.upper()}[/{color}]"

        message = f"{icon} [bold]{agent_name}[/bold]: {status_msg}"
        if message:
            message += f"\n   {message}"

        self.show(message, "working")
    
    def show_multi_agent_status(self, agents: list):
        """
        Show status of multiple agents

        Args:
            agents: List of dicts with keys: name, status, message
        """
        from rich.text import Text
        from rich.panel import Panel
        
        status_text = Text()
        status_text.append("🤖 [bold]Agent Team Status[/bold]\n\n", style="bright_cyan")

        agent_icons = {
            "generator": "🧱",
            "reviewer": "🔍",
            "tester": "🧪",
            "refactorer": "🔨",
            "documenter": "📝",
            "architect": "🏗️",
            "security": "🔒",
            "debugger": "🐛"
        }

        for agent in agents:
            name = agent.get("name", "Unknown")
            status = agent.get("status", "unknown")
            message = agent.get("message", "")

            icon = agent_icons.get(name.lower(), "🤖")
            status_colors = {
                "working": "bright_yellow",
                "waiting": "dim",
                "done": "bright_green",
                "error": "bright_red"
            }

            color = status_colors.get(status, "white")
            status_text.append(f"{icon} {name}: ", style="white")
            status_text.append(f"{status.upper()}\n", style=color)

            if message:
                status_text.append(f"   {message}\n", style="dim")

        panel = Panel(
            status_text,
            title=f"[bold]Blip - {self.current_character.name}[/bold]",
            border_style="bright_cyan",
            padding=(1, 2)
        )

        console.print(panel)
        self.animation_frame += 1


# Global Blip Manager instance
blip_manager = BlipManager()


def get_blip_manager() -> BlipManager:
    """Get the global Blip manager instance"""
    return blip_manager


if __name__ == "__main__":
    # Demo Blip Manager
    manager = BlipManager()

    print("=== Blip Manager Demo ===\n")

    manager.introduce()
    time.sleep(2)

    manager.think("I'm thinking about what to show you next...")
    time.sleep(2)

    manager.happy("I figured it out!")
    time.sleep(1)

    manager.work("Generator agent is creating your code...")
    time.sleep(1)

    manager.show_agent_status("generator", "working", "Writing API endpoints")
    time.sleep(1)

    agents = [
        {"name": "generator", "status": "working", "message": "Creating initial code"},
        {"name": "reviewer", "status": "waiting", "message": ""},
        {"name": "tester", "status": "waiting", "message": ""}
    ]
    manager.show_multi_agent_status(agents)
    time.sleep(1)

    manager.success("All done! Your code is ready! 🎉")

    # Switch character
    print("\n=== Switching to Wisp ===\n")
    manager.switch_character("wisp")
    manager.happy("I'm now the Wisp! ✨")
