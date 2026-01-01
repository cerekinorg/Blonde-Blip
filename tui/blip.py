"""
Blip - The Blonde CLI Mascot

A friendly blob character that helps guide users through Blonde CLI.
Blip shows different emotions and states through animations.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from typing import Optional
import time
import random

console = Console()


class Blip:
    """
    Blip is the friendly mascot of Blonde CLI.
    It shows different states and emotions through ASCII art animations.
    """

    # ASCII art for different Blip states
    STATES = {
        "idle": [
            """
    (• ◡•)
     /   \\
    /_____\\
     """,
            """
    (• ○•)
     /   \\
    /_____\\
     """,
            """
    (• ◡•)
     /   \\
    /_____\\
     """
        ],
        "happy": [
            """
    (◕‿◕)
     /   \\
    /_____\\
    ~~~~~
    """
        ],
        "excited": [
            """
    (⌐■_■)
     /   \\
    /_____\\
    ~~~~~!
    """,
            """
    (⌐■_■)
     /   \\
    /_____\\
    ~!!~~
            """
        ],
        "thinking": [
            """
    (•_•)?
     /   \\
    /_____\\
     """,
            """
    (•_•)
     /   \\
    /_____\\
    ~~~
            """,
            """
    (•_•)...
     /   \\
    /_____\\
            """
        ],
        "working": [
            """
    (•_•)
     /   \\
    /_____\\
    ~[ ]~~
            """,
            """
    (•_•)
     /   \\
    /_____\\
    ~[=]~~
            """,
            """
    (•_•)
     /   \\
    /_____\\
    ~[#]~~
            """
        ],
        "confused": [
            """
    (O_O)
     /   \\
    /_____\\
     ???
            """
        ],
        "error": [
            """
    (x_x)
     /   \\
    /_____\\
    !!!!
            """
        ],
        "success": [
            """
    (⌐■_■)
     /   \\
    /_____\\
    ✓✓✓
            """
        ],
        "love": [
            """
    (♥_♥)
     /   \\
    /_____\\
    <3 <3
            """
        ],
        "surprised": [
            """
    (O_O)
     /   \\
    /_____\\
     !!!
            """
        ]
    }

    # Color schemes for different states
    COLORS = {
        "idle": "bright_cyan",
        "happy": "bright_green",
        "excited": "bright_yellow",
        "thinking": "bright_blue",
        "working": "bright_magenta",
        "confused": "yellow",
        "error": "bright_red",
        "success": "bright_green",
        "love": "bright_red",
        "surprised": "bright_yellow"
    }

    def __init__(self):
        self.current_state = "idle"
        self.animation_frame = 0
        self.message_queue = []

    def get_art(self, state: str = "idle") -> str:
        """Get ASCII art for a state"""
        frames = self.STATES.get(state, self.STATES["idle"])
        return frames[self.animation_frame % len(frames)]

    def get_color(self, state: str = "idle") -> str:
        """Get color for a state"""
        return self.COLORS.get(state, "white")

    def advance_frame(self):
        """Advance to next animation frame"""
        self.animation_frame += 1

    def show(
        self,
        message: str,
        state: str = "idle",
        animate: bool = False,
        duration: float = 0.3
    ):
        """
        Display Blip with a message

        Args:
            message: Message to display
            state: Blip's emotional state
            animate: Whether to animate
            duration: Animation duration in seconds
        """
        self.current_state = state

        if animate:
            frames = self.STATES.get(state, self.STATES["idle"])
            for i in range(len(frames)):
                console.clear()
                self.animation_frame = i
                self._render(message, state)
                time.sleep(duration)
        else:
            self.animation_frame = 0
            self._render(message, state)

    def _render(self, message: str, state: str):
        """Render Blip with message"""
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
            title="[bold]Blip[/bold]",
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
        message = """
Hi! I'm [bold]Blip[/bold] 👋

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
            border_style="bright_cyan",
            padding=(1, 2)
        )

        console.print(panel)
        self.animation_frame += 1


# Global Blip instance
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
