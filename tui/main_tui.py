"""
Main Dashboard TUI - Blonde CLI's primary interface
Like OpenCode: Rich TUI with natural command processing

Designed to be VERY user-friendly and intuitive.
"""

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.prompt import Prompt
from pathlib import Path
import sys

from tui.blip import blip


class MainTUI:
    """
    Main TUI interface for Blonde CLI

    User-friendly features:
    - Clean, minimal interface
    - Helpful prompts from Blip
    - Natural language commands (auto-detect)
    - Simplified slash commands
    - Clear feedback
    - Easy navigation
    """

    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.running = True
        self.command_history = []
        self.history_index = -1

    def initialize_layout(self):
        """Set up main layout - clean and minimal"""
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=4)
        )

        # Header - Simple and informative
        header_text = "[bold cyan]Blonde CLI[/bold cyan] [dim]• Multi-Agent AI Assistant[/dim]"
        self.layout["header"].update(Panel(header_text, style="bold blue"))

    def update_footer(self, context=""):
        """Update footer with helpful hints"""
        hints = [
            "[dim]Type your request naturally (e.g., 'Create a REST API')[/dim]",
            "[dim]Type /help for commands[/dim]",
            "[dim]Type /settings to configure[/dim]",
            "[dim]Ctrl+C to exit[/dim]"
        ]

        if context:
            hints.insert(0, f"[cyan]Context: {context}[/cyan]")

        footer_text = "  ".join(hints)
        self.layout["footer"].update(Panel(footer_text, style="on black"))

    def show_welcome(self):
        """Show friendly welcome message"""
        welcome = """
╔═════════════════════════════════════════════════╗
║                                                       ║
║   🚀 Welcome to Blonde CLI!                            ║
║                                                       ║
║   I'm here to help you build better code        ║
║   with the help of AI agents.                        ║
║                                                       ║
║   Just tell me what you need, and I'll figure    ║
║   out which agents can help!                          ║
║                                                       ║
╚═════════════════════════════════════════════════╝
        """
        self.console.print(welcome)
        self.console.print()
        blip.happy("I'm ready to help! What would you like to do today?")
        self.console.print()

    def run(self):
        """Main event loop - user-friendly and intuitive"""
        self.initialize_layout()
        self.show_welcome()

        with Live(self.layout, console=self.console, refresh_per_second=10):
            while self.running:
                try:
                    # Update main area with Blip's helpful message
                    self.layout["main"].update(
                        Panel(
                            f"{blip.work('Listening... Type your request below')}",
                            title="[bold green]Chat[/bold green]",
                            border_style="green"
                        )
                    )

                    # Get user input with helpful prompt
                    user_input = self.get_user_input()

                    if not user_input:
                        continue

                    # Add to history
                    self.command_history.append(user_input)
                    self.history_index = -1

                    # Process command
                    self.process_command(user_input)

                except KeyboardInterrupt:
                    blip.happy("Thanks for using Blonde CLI! Goodbye! 👋")
                    self.console.print()
                    self.running = False
                    break
                except EOFError:
                    blip.happy("Thanks for using Blonde CLI! Goodbye! 👋")
                    self.console.print()
                    self.running = False
                    break
                except Exception as e:
                    blip.error(f"Oops! Something went wrong: {e}")
                    self.console.print(f"[dim]Error details: {type(e).__name__}[/dim]")
                    self.console.print()
                    if "--debug" in sys.argv:
                        self.console.print_exception()

    def get_user_input(self) -> str:
        """Get user input with arrow key history support"""
        try:
            user_input = Prompt.ask(
                "[bold green]You:[/bold green]",
                console=self.console,
                default="",
                show_default=False
            )
            return user_input.strip()
        except (KeyboardInterrupt, EOFError):
            raise

    def process_command(self, user_input: str):
        """
        Process user command with automatic agent detection

        Designed for natural interaction - user just types what they want.
        """
        # Check for slash commands
        if user_input.startswith("/"):
            self.process_slash_command(user_input)

        # Natural language processing - auto-detect intent
        else:
            self.process_natural_language(user_input)

    def process_slash_command(self, command: str):
        """Process explicit slash commands - simplified and intuitive"""

        # Extract command and args
        parts = command[1:].split(maxsplit=1)
        cmd = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        # Simplified command mapping - user-friendly
        commands = {
            "help": {
                "handler": self.show_help,
                "desc": "Show available commands",
                "usage": "/help [command]"
            },
            "collab": {
                "handler": self.run_collaboration,
                "desc": "Have multiple agents collaborate",
                "usage": "/collab 'build a REST API'"
            },
            "agents": {
                "handler": self.show_agents,
                "desc": "Show agent status",
                "usage": "/agents"
            },
            "analyze": {
                "handler": self.analyze_code,
                "desc": "Analyze code quality",
                "usage": "/analyze [file]"
            },
            "test": {
                "handler": self.generate_tests,
                "desc": "Generate tests",
                "usage": "/test [file]"
            },
            "fix": {
                "handler": self.fix_code,
                "desc": "Fix bugs",
                "usage": "/fix [file]"
            },
            "refactor": {
                "handler": self.refactor_code,
                "desc": "Refactor code",
                "usage": "/refactor [file]"
            },
            "document": {
                "handler": self.generate_documentation,
                "desc": "Generate documentation",
                "usage": "/document [file]"
            },
            "settings": {
                "handler": self.open_settings,
                "desc": "Open settings",
                "usage": "/settings"
            },
            "provider": {
                "handler": self.manage_providers,
                "desc": "Manage AI providers",
                "usage": "/provider [list|switch|test]"
            },
            "mcp": {
                "handler": self.manage_mcp,
                "desc": "Manage MCP servers",
                "usage": "/mcp [setup|list]"
            },
            "clear": {
                "handler": self.clear_screen,
                "desc": "Clear the screen",
                "usage": "/clear"
            },
            "exit": {
                "handler": self.exit_app,
                "desc": "Exit Blonde CLI",
                "usage": "/exit"
            },
            "quit": {
                "handler": self.exit_app,
                "desc": "Exit Blonde CLI",
                "usage": "/quit"
            }
        }

        if cmd in commands:
            cmd_info = commands[cmd]
            try:
                response = cmd_info["handler"](args)
                self.display_response(response)
            except Exception as e:
                blip.error(f"Command failed: {e}")
                self.display_response(f"Error: {e}")
        else:
            self.display_response(f"Unknown command: /{cmd}\nType /help for available commands.")

    def process_natural_language(self, user_input: str):
        """
        Process natural language requests with automatic agent selection

        Like OpenCode - user just types what they want, and we figure out the rest.
        """
        # Auto-detect intent
        intent = self.detect_intent(user_input)

        blip.think(f"I understand you want to: {intent.replace('_', ' ').title()}")
        blip.work("Let me coordinate the right agents for this...")

        # Route to appropriate handler
        # Note: These will call actual agent implementations
        # For now, show what would happen
        response = f"""
[bold cyan]📋 Understanding your request...[/bold cyan]

[d]You said:[/d] {user_input}

[d]Detected intent:[/d] {intent.replace('_', ' ').title()}

[d]Agents that would help:[/d]

"""

        # Add specific agent suggestions based on intent
        if intent == "generate_code":
            response += """
[c]  🧱 Generator Agent[/c] - Will create the initial implementation
[c]  🔍 Reviewer Agent[/c] - Will check code quality
[c]  🔒 Security Agent[/c] - Will audit for vulnerabilities
"""
        elif intent == "fix_bug":
            response += """
[c]  🐛 Debugger Agent[/c] - Will identify and fix the issue
[c]  🔍 Reviewer Agent[/c] - Will review the fix
"""
        elif intent == "refactor":
            response += """
[c]  🔨 Refactorer Agent[/c] - Will improve code structure
[c]  ⚡ Optimizer Agent[/c] - Will suggest optimizations
"""
        elif intent == "analyze":
            response += """
[c]  🔍 Reviewer Agent[/c] - Will analyze code quality
[c]  🏗️ Architect Agent[/c] - Will review architecture
"""
        elif intent == "test":
            response += """
[c]  🧪 Tester Agent[/c] - Will generate comprehensive tests
[c]  🔍 Reviewer Agent[/c] - Will validate test coverage
"""
        elif intent == "document":
            response += """
[c]  📝 Documenter Agent[/c] - Will generate documentation
[c]  🔍 Reviewer Agent[/c] - Will check completeness
"""
        elif intent == "collaborative":
            response += """
[c]  🧱 Generator Agent[/c] - Creates initial implementation
[c]  🔍 Reviewer Agent[/c] - Reviews code quality
[c]  🧪 Tester Agent[/c] - Generates tests
[c]  🔨 Refactorer Agent[/c] - Improves structure
[c]  📝 Documenter Agent[/c] - Writes documentation
[c]  🏗️ Architect Agent[/c] - Designs architecture
[c]  🔒 Security Agent[/c] - Security audit
[c]  ⚡ Optimizer Agent[/c] - Coordinates all agents
"""

        response += f"""
[bold green]▶ Ready to execute![/bold green]

[italic]Tip: Type the same command again to execute with actual AI responses.
Or use /collab to run the full task.[/italic]
"""
        self.display_response(response)

    def detect_intent(self, user_input: str) -> str:
        """
        Simple keyword-based intent detection

        In production, this could use an LLM for better accuracy.
        """
        user_input_lower = user_input.lower()

        # Collaborative keywords (highest priority)
        collaborative_keywords = [
            "together", "team", "collab", "full stack", "complete", "complex",
            "entire", "end to end", "from scratch", "build a"
        ]
        for kw in collaborative_keywords:
            if kw in user_input_lower:
                return "collaborative"

        # Other intents
        intent_keywords = {
            "generate_code": [
                "create", "build", "implement", "write", "generate", "make", "add",
                "new function", "new class", "new feature", "build a"
            ],
            "fix_bug": [
                "fix", "bug", "error", "broken", "doesn't work", "solve", "debug",
                "not working", "crash", "fail"
            ],
            "refactor": [
                "refactor", "improve", "optimize", "better", "clean up", "simplify",
                "restructure", "reorganize"
            ],
            "analyze": [
                "analyze", "explain", "how does", "what is", "review", "understand",
                "check", "examine", "look at"
            ],
            "test": [
                "test", "tests", "coverage", "test cases", "unit test", "testing"
            ],
            "document": [
                "document", "documentation", "docs", "readme", "comments",
                "explain the code"
            ]
        }

        for intent, keywords in intent_keywords.items():
            for kw in keywords:
                if kw in user_input_lower:
                    return intent

        # Default for complex requests
        if len(user_input.split()) > 10:
            return "collaborative"

        return "general_chat"

    def display_response(self, response: str):
        """Display response in main area - clean formatting"""
        self.layout["main"].update(
            Panel(
                response,
                title="[bold green]Response[/bold green]",
                border_style="green"
            )
        )

    # Command handlers
    def show_help(self, args: str = "") -> str:
        """Show helpful command reference"""
        help_text = """
[bold cyan]╔═════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║                  Available Commands                    ║[/bold cyan]
[bold cyan]╚═════════════════════════════════════════════════╝[/bold cyan]

[dim]You can use natural language (just type what you want!)[/dim]

[bold cyan]Slash Commands:[/bold cyan]

  [bold green]/help[/bold green]              Show this help message
  [bold green]/collab <task>[/bold green]    Run collaborative agent task
  [bold green]/agents[/bold green]            Show agent status
  [bold green]/analyze <file>[/bold green]    Analyze code
  [bold green]/test <file>[/bold green]       Generate tests
  [bold green]/fix <file>[/bold green]        Fix bugs
  [bold green]/refactor <file>[/bold green]   Refactor code
  [bold green]/document <file>[/bold green]   Generate documentation
  [bold green]/settings[/bold green]          Configure all settings
  [bold green]/provider <action>[/bold green]  Manage AI providers
  [bold green]/mcp <action>[/bold green]      Manage MCP servers
  [bold green]/clear[/bold green]             Clear screen
  [bold green]/exit[/bold green]             Exit

[dim]────────────────────────────────────────────────────────────────────[/dim]

[bold cyan]Natural Language Examples:[/bold cyan]

  [dim]Just type what you want! Examples:[/dim]
  [dim]  • "Create a REST API with authentication"[/dim]
  [dim]  • "Fix bug in user_service.py"[/dim]
  [dim]  • "Analyze this repository"[/dim]
  [dim]  • "Generate tests for auth.py"[/dim]
  [dim]  • "Refactor the user module"[/dim]
  [dim]  • "Document the API endpoints"[/dim]

[bold cyan]Tips:[/bold cyan]
  [dim]• Use natural language - just describe what you need[/dim]
  [dim]• Start with verbs: Create, Fix, Analyze, Refactor, Test, Document[/dim]
  [dim]• Use /collab for complex tasks requiring multiple agents[/dim]
  [dim]• Type /settings to configure providers, UI preferences, MCP, etc.[/dim]

[dim]────────────────────────────────────────────────────────────────────[/dim]
"""
        return help_text

    def run_collaboration(self, args: str = "") -> str:
        """Run a collaborative task with multiple agents"""
        if not args:
            return """
[bold yellow]Collaborative Task[/bold yellow]

Usage: /collab "your task description"

Example:
  /collab "Build a REST API with user authentication and tests"

This will coordinate multiple agents working together to complete your task.
"""
        return f"""
[bold cyan]🤝 Collaborative Task Mode[/bold cyan]

[d]Task:[/d] {args}

[d]Agents that will work together:[/d]

[c]  🧱 Generator Agent[/c] - Creates initial code
[c]  🔍 Reviewer Agent[/c] - Reviews quality
[c]  🧪 Tester Agent[/c] - Generates tests
[c]  🔨 Refactorer Agent[/c] - Improves structure
[c]  📝 Documenter Agent[/c] - Writes docs
[c]  🏗️ Architect Agent[/c] - Reviews architecture
[c]  🔒 Security Agent[/c] - Security audit
[c]  ⚡ Optimizer Agent[/c] - Coordinates all agents

[italic]Note: In the next version, this will execute the actual task.
For now, it demonstrates which agents would be involved.[/italic]
"""

    def show_agents(self, args: str = "") -> str:
        """Show agent status"""
        return """
[bold cyan]╔═════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║              Agent Status                        ║[/bold cyan]
[bold cyan]╚═════════════════════════════════════════════════╝[/bold cyan]

[bold cyan]9 Specialized Agents:[/bold cyan]

  [bold green]🧱 Generator Agent[/bold green]       Code generation
  [bold green]🔍 Reviewer Agent[/bold green]        Code quality
  [bold green]🧪 Tester Agent[/bold green]          Test generation
  [bold green]🔨 Refactorer Agent[/bold green]       Code improvement
  [bold green]📝 Documenter Agent[/bold green]      Documentation
  [bold green]🏗️ Architect Agent[/bold green]        System design
  [bold green]🔒 Security Agent[/bold green]        Security audit
  [bold green]🐛 Debugger Agent[/bold green]        Bug fixing
  [bold green]⚡ Optimizer Agent[/bold green]        Coordination & quality

[italic]All agents work together under Optimizer coordination![/italic]

[dim]────────────────────────────────────────────────────────────────────[/dim]
"""

    def analyze_code(self, args: str = "") -> str:
        """Analyze code"""
        return """
[bold cyan]🔍 Code Analysis[/bold cyan]

Usage: /analyze <file_path>

Example: /analyze user_service.py

This will analyze your code for:
  • Code quality issues
  • Security vulnerabilities
  • Performance bottlenecks
  • Architectural problems
  • Best practice violations
"""

    def generate_tests(self, args: str = "") -> str:
        """Generate tests"""
        return """
[bold cyan]🧪 Test Generation[/bold cyan]

Usage: /test <file_path>

Example: /test auth.py

This will generate comprehensive tests including:
  • Unit tests
  • Integration tests
  • Edge cases
  • Error scenarios
"""

    def fix_code(self, args: str = "") -> str:
        """Fix bugs"""
        return """
[bold cyan]🐛 Bug Fixing[/bold cyan]

Usage: /fix <file_path>

Example: /fix user_service.py

The Debugger Agent will:
  • Identify the issue
  • Find root cause
  • Generate a fix
  • Reviewer Agent will validate the fix
"""

    def refactor_code(self, args: str = "") -> str:
        """Refactor code"""
        return """
[bold cyan]🔨 Code Refactoring[/bold cyan]

Usage: /refactor <file_path>

Example: /refactor user_module.py

The Refactorer Agent will:
  • Improve code structure
  • Reduce complexity
  • Apply best practices
  • Optimizer Agent will suggest improvements
"""

    def generate_documentation(self, args: str = "") -> str:
        """Generate documentation"""
        return """
[bold cyan]📝 Documentation Generation[/bold cyan]

Usage: /document <file_path>

Example: /document api.py

The Documenter Agent will:
  • Generate README
  • Add docstrings
  • Create usage examples
  • Document API endpoints
"""

    def open_settings(self, args: str = "") -> str:
        """Open settings panel"""
        return """
[bold cyan]⚙️ Settings[/bold cyan]

Opening settings panel with tabs:

  • [bold green]Providers[/bold green] - AI provider configuration
  • [bold green]Privacy[/bold green] - Privacy & data settings
  • [bold green]UI[/bold green] - Interface preferences
  • [bold green]MCP[/bold green] - MCP server configuration
  • [bold green]Memory[/bold green] - Memory & storage settings
  • [bold green]Agents[/bold green] - Agent configuration
  • [bold green]Workflows[/bold green] - Workflow management

[italic]Settings panel will open with all configuration options.[/italic]
"""

    def manage_providers(self, args: str = "") -> str:
        """Manage providers"""
        return """
[bold cyan]🤖 Provider Management[/bold cyan]

Usage: /provider <action>

Actions:
  [bold green]list[/bold green]       - Show all configured providers
  [bold green]switch[/bold green]    - Switch default provider
  [bold green]test[/bold green]      - Test provider connection

Examples:
  /provider list
  /provider switch openai
  /provider test
"""

    def manage_mcp(self, args: str = "") -> str:
        """Manage MCP servers"""
        return """
[bold cyan]🔌 MCP Management[/bold cyan]

Usage: /mcp <action>

Actions:
  [bold green]setup[/bold green]   - Configure MCP servers
  [bold green]list[/bold green]     - Show configured servers
  [bold green]enable[/bold green]  - Enable a server
  [bold green]disable[/bold green] - Disable a server

Examples:
  /mcp setup
  /mcp list
"""

    def clear_screen(self, args: str = "") -> str:
        """Clear screen"""
        self.console.clear()
        blip.happy("Screen cleared!")
        return ""

    def exit_app(self, args: str = "") -> str:
        """Exit application"""
        self.running = False
        return """
[bold cyan]👋 Goodbye![/bold cyan]

Thank you for using Blonde CLI!

[dim]────────────────────────────────────────────────────────────────────[/dim]

[italic]See you next time! Type 'blonde' to start again.[/italic]
"""


def launch_dashboard():
    """Launch main dashboard TUI"""
    tui = MainTUI()
    tui.run()
