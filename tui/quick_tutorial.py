"""
Quick Tutorial for Blonde CLI

A 3-5 minute tutorial covering the basics of using Blonde CLI.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.markdown import Markdown

from tui.blip import blip

console = Console()


class QuickTutorial:
    """Interactive quick tutorial for new users"""

    def __init__(self):
        self.current_lesson = 1
        self.total_lessons = 5

    def run(self):
        """Run complete tutorial"""
        console.clear()

        welcome_panel = Panel(
            """[bold cyan]Welcome to Blonde CLI![/bold cyan]

This quick tutorial will teach you the basics in 5 minutes.

You'll learn:
• How to interact with Blip (your AI mascot)
• How to use the chat interface
• How the multi-agent team works
• How to generate code
• How to get help[dim]

Press Enter to continue, or 'q' to skip tutorial.""",
            title="[bold]🎓 Quick Tutorial[/bold]",
            border_style="cyan",
            padding=(2, 2)
        )

        console.print(welcome_panel)

        response = Prompt.ask("", choices=["", "q"], default="")

        if response == "q":
            blip.happy("Tutorial skipped. You can explore on your own!")
            return

        # Run lessons
        self.lesson_1_meet_blip()
        self.lesson_2_chat_basics()
        self.lesson_3_multi_agent_team()
        self.lesson_4_generate_code()
        self.lesson_5_getting_help()

        # Complete
        self.show_completion()

    def lesson_1_meet_blip(self):
        """Lesson 1: Meet Blip"""
        console.clear()

        blip.introduce()

        lesson_panel = Panel(
            """[bold]Lesson 1: Meet Blip[/bold]

Blip is your friendly AI mascot who guides you through Blonde CLI.

[bold]Blip's Roles:[/bold]
• Explains what's happening
• Shows agent status
• Provides helpful tips
• Celebrates your successes

[bold]Blip's Emotions:[/bold]
😊 Happy    - Celebrating success
🤔 Thinking  - Processing information
⚙️  Working   - Working on tasks
😵 Error    - Something went wrong

Blip will appear throughout your session to help you understand
what's happening and guide you to next steps.""",
            title=f"[cyan]Lesson 1/{self.total_lessons}[/cyan]",
            border_style="cyan",
            padding=(2, 2)
        )

        console.print(lesson_panel)

        if Confirm.ask("Ready for the next lesson?", default=True):
            pass

    def lesson_2_chat_basics(self):
        """Lesson 2: Chat Basics"""
        console.clear()

        blip.think("Let me show you how to chat with AI...")

        lesson_panel = Panel(
            """[bold]Lesson 2: Chat Basics[/bold]

The chat interface is where you interact with AI using natural language.

[bold]Starting Chat:[/bold]
  blonde chat

[bold]Basic Chat:[/bold]
  User: Create a function that sorts a list
  → AI generates the function

[bold]Chat Commands:[/bold]
  /providers        - See available AI providers
  /team status      - See agent team status
  /help [topic]     - Get help on a topic
  /clear            - Clear the screen

[bold]Tips:[/bold]
• Be specific in your requests
• Context is automatically included
• Blip explains what's happening
• Use natural language like talking to a colleague""",

            title=f"[cyan]Lesson 2/{self.total_lessons}[/cyan]",
            border_style="cyan",
            padding=(2, 2)
        )

        console.print(lesson_panel)

        blip.happy("Chat is intuitive - just ask questions in plain English!")

        if Confirm.ask("Ready for the next lesson?", default=True):
            pass

    def lesson_3_multi_agent_team(self):
        """Lesson 3: Multi-Agent Team"""
        console.clear()

        blip.excited("The best part - multiple AI agents working together!")

        lesson_panel = Panel(
            """[bold]Lesson 3: Multi-Agent Team[/bold]

Blonde CLI has 8 specialized AI agents that collaborate:

[bold]The Agents:[/bold]
  🧱 Generator   - Creates initial code
  🔍 Reviewer   - Reviews code quality
  🧪 Tester      - Generates test cases
  🔨 Refactorer  - Improves code structure
  📝 Documenter  - Writes documentation
  🏗️  Architect   - Designs architecture
  🔒 Security    - Identifies vulnerabilities
  🐛 Debugger    - Fixes bugs

[bold]Agent Collaboration:[/bold]
  User: /team collab Build a REST API
  → Generator creates the API
  → Reviewer checks for issues
  → Security audits for vulnerabilities
  → Tester generates tests
  → Documenter writes docs

All agents work together to produce high-quality code!""",

            title=f"[cyan]Lesson 3/{self.total_lessons}[/cyan]",
            border_style="cyan",
            padding=(2, 2)
        )

        console.print(lesson_panel)

        blip.work("Agents communicate with each other to improve results!")

        if Confirm.ask("Ready for the next lesson?", default=True):
            pass

    def lesson_4_generate_code(self):
        """Lesson 4: Generate Code"""
        console.clear()

        blip.work("Let's generate some code together...")

        lesson_panel = Panel(
            """[bold]Lesson 4: Generate Code[/bold]

You can generate code in multiple ways:

[bold]Method 1: Interactive Chat[/bold]
  blonde chat
  User: Create a Python function to validate email

[bold]Method 2: Direct Generation[/bold]
  blonde gen "Create a REST API with authentication"

[bold]Method 3: Create New File[/bold]
  blonde create "user_service.py" "Add user management"

[bold]Generated Code:[/bold]
The code is automatically:
• Saved to the appropriate file
• Formatted properly
• Ready to use
• Reviewed by agents (in collaboration mode)

[bold]Example Workflow:[/bold]
  1. Request: "Create a user authentication system"
  2. Generator creates the code
  3. Reviewer checks for bugs
  4. Tester generates tests
  5. Documenter writes API docs
  6. Result: Complete, tested, documented code!""",

            title=f"[cyan]Lesson 4/{self.total_lessons}[/cyan]",
            border_style="cyan",
            padding=(2, 2)
        )

        console.print(lesson_panel)

        blip.success("Code generation is fast and reliable with agent collaboration!")

        if Confirm.ask("Ready for the next lesson?", default=True):
            pass

    def lesson_5_getting_help(self):
        """Lesson 5: Getting Help"""
        console.clear()

        blip.think("Here's how to get help whenever you need it...")

        lesson_panel = Panel(
            """[bold]Lesson 5: Getting Help[/bold]

Help is always available within Blonde CLI:

[bold]Built-in Help:[/bold]
  blonde --help              # General help
  blonde chat --help         # Chat-specific help
  /help                     # In chat: show all commands
  /help [topic]             # In chat: help on specific topic

[bold]Common Help Topics:[/bold]
  /help provider             # Managing AI providers
  /help team                # Using multi-agent team
  /help chat                # Chat interface commands
  /help commands            # All available commands

[bold]Online Resources:[/bold]
  • Documentation: https://github.com/cerekinorg/Blonde-Blip#readme
  • GitHub Issues: https://github.com/blonde-team/blonde-cli/issues
  • Community Discord: https://discord.gg/blonde

[bold]Still Stuck?[/bold]
  1. Try the tutorial again: blonde --tutorial
  2. Check documentation: https://github.com/cerekinorg/Blonde-Blip#readme
  3. Ask in Discord community""",

            title=f"[cyan]Lesson 5/{self.total_lessons}[/cyan]",
            border_style="cyan",
            padding=(2, 2)
        )

        console.print(lesson_panel)

        blip.happy("Help is always available!")

        if Confirm.ask("Ready to complete the tutorial?", default=True):
            pass

    def show_completion(self):
        """Show tutorial completion"""
        console.clear()

        completion_panel = Panel(
            """[bold green]🎉 Tutorial Complete![/bold green]

You've learned the basics of Blonde CLI!

[bold]What You Can Do Now:[/bold]
✓ Chat with AI naturally
✓ Understand Blip's guidance
✓ Use multi-agent collaboration
✓ Generate code easily
✓ Get help when needed

[bold]Next Steps:[/bold]
1. Start chatting: blonde chat
2. Explore commands: blonde --help
3. Read documentation: https://github.com/cerekinorg/Blonde-Blip#readme
4. Try agent collaboration: /team collab

[bold]Remember:[/bold]
• Blip is here to guide you
• Multiple agents work together
• Help is always available
• Privacy is prioritized

[dim]You can replay this tutorial anytime with: blonde --tutorial[/dim]""",

            title="[bold cyan]🎓 Tutorial Complete[/bold cyan]",
            border_style="green",
            padding=(2, 2)
        )

        console.print(completion_panel)

        blip.love("Happy coding! You're going to do great things! 💖")


def run_tutorial():
    """Run the quick tutorial"""
    tutorial = QuickTutorial()
    tutorial.run()


if __name__ == "__main__":
    run_tutorial()
