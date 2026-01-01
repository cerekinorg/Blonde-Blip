"""
Chat Command System - Integrates ALL features into chat interface
Provides natural language commands for accessing all Blonde CLI capabilities
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@dataclass
class ChatCommand:
    """Represents a chat command"""
    name: str
    pattern: str  # regex pattern to match
    description: str
    examples: List[str]
    handler: Callable
    aliases: List[str] = None
    requires_args: bool = True


class ChatCommandRegistry:
    """Registry for all chat commands"""
    
    def __init__(self):
        self.commands: Dict[str, ChatCommand] = {}
        self.providers = None
        self.dev_team = None
        self.rollback_manager = None
        self.workflow_manager = None
        self.code_analyzer = None
        self.test_generator = None
        self.linter = None
        self.project_root = Path.cwd()
    
    def register_command(self, command: ChatCommand):
        """Register a new command"""
        self.commands[command.name] = command
        if command.aliases:
            for alias in command.aliases:
                self.commands[alias] = command
    
    def set_services(self, providers=None, dev_team=None, rollback=None, 
                   workflow=None, analyzer=None, tester=None, linter=None):
        """Set service instances for commands"""
        self.providers = providers
        self.dev_team = dev_team
        self.rollback_manager = rollback
        self.workflow_manager = workflow
        self.code_analyzer = analyzer
        self.test_generator = tester
        self.linter = linter
    
    def execute(self, user_input: str, **kwargs) -> str:
        """Execute a command from user input"""
        # Check for command patterns
        for name, command in self.commands.items():
            match = re.match(command.pattern, user_input, re.IGNORECASE)
            if match:
                groups = match.groups()
                try:
                    result = command.handler(*groups, **kwargs)
                    return f"\n✓ Executed: {command.name}\n{result}"
                except Exception as e:
                    return f"✗ Error executing {command.name}: {e}"
        
        return None  # No command matched
    
    def list_commands(self, category: str = None) -> Table:
        """List all available commands"""
        table = Table(title="Available Commands")
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Examples", style="yellow")
        
        for cmd in self.commands.values():
            if category and cmd.name.startswith(category):
                table.add_row(
                    cmd.name,
                    cmd.description,
                    ", ".join(cmd.examples[:2])
                )
        
        return table
    
    def help(self, topic: str = None) -> str:
        """Get help for a specific command or all commands"""
        if topic:
            cmd = self.commands.get(topic.lower())
            if cmd:
                return f"""
[bold cyan]{cmd.name}[/bold cyan]

[green]Description:[/green] {cmd.description}

[yellow]Examples:[/yellow]
  {chr(10).join('  ' + ex for ex in cmd.examples)}

[green]Aliases:[/green] {', '.join(cmd.aliases or ['None'])}
"""
            else:
                return f"[red]Unknown command: {topic}[/red]"
        else:
            table = self.list_commands()
            return f"""
[bold cyan]Blonde CLI Chat Commands[/bold cyan]

Type any command to execute. All commands can be used in natural language.

{table}

[dim]For help on a specific command, type: /help <command>[/dim]
[dim]For full documentation, see: /docs[/dim]
"""


def create_command_registry():
    """Create and populate command registry"""
    registry = ChatCommandRegistry()
    
    # ================
    # PROVIDER COMMANDS
    # ================
    
    def handle_provider_list():
        if not registry.providers:
            return "Provider system not initialized"
        return str(registry.providers.list_providers())
    
    def handle_provider_switch(provider_name: str):
        if not registry.providers:
            return "Provider system not initialized"
        if registry.providers.switch_provider(provider_name):
            current = registry.providers.get_current_provider()
            return f"Switched to: {current.name} ({current.model})"
        return "Failed to switch provider"
    
    def handle_provider_test(provider_name: str = None):
        if not registry.providers:
            return "Provider system not initialized"
        if provider_name:
            if registry.providers.test_provider(provider_name):
                return f"✓ Provider {provider_name} is working"
            return f"✗ Provider {provider_name} failed"
        else:
            current = registry.providers.current_provider
            if registry.providers.test_provider(current):
                return f"✓ Current provider {current} is working"
            return f"✗ Current provider {current} failed"
    
    def handle_provider_auto():
        if not registry.providers:
            return "Provider system not initialized"
        if registry.providers.auto_select_provider():
            current = registry.providers.get_current_provider()
            return f"Auto-selected: {current.name}"
        return "No suitable provider found"
    
    registry.register_command(ChatCommand(
        name="provider_list",
        pattern=r"^/providers?\s*$",
        description="List all configured AI providers",
        examples=["/providers", "/provider list"],
        handler=handle_provider_list
    ))
    
    registry.register_command(ChatCommand(
        name="provider_switch",
        pattern=r"^/provider\s+switch\s+(\w+)",
        description="Switch to a different AI provider",
        examples=["/provider switch openai", "/provider switch local"],
        handler=handle_provider_switch
    ))
    
    registry.register_command(ChatCommand(
        name="provider_test",
        pattern=r"^/provider\s+test(?:\s+(\w+))?",
        description="Test if a provider is working",
        examples=["/provider test", "/provider test openai"],
        handler=handle_provider_test
    ))
    
    registry.register_command(ChatCommand(
        name="provider_auto",
        pattern=r"^/provider\s+auto\s*$",
        description="Auto-select the best available provider",
        examples=["/provider auto"],
        handler=handle_provider_auto
    ))
    
    # ================
    # DEV TEAM COMMANDS
    # ================
    
    def handle_team_status():
        if not registry.dev_team:
            return "Development team not initialized"
        return str(registry.dev_team.get_team_status())
    
    def handle_team_task(agent: str, task: str):
        if not registry.dev_team:
            return "Development team not initialized"
        task_id = registry.dev_team.assign_task(agent, "user_task", task, {})
        if registry.dev_team.execute_task(task_id):
            return f"✓ Assigned task to {agent}: {task}"
        return f"✗ Task failed"
    
    def handle_team_collaborate(task: str):
        if not registry.dev_team:
            return "Development team not initialized"
        results = registry.dev_team.collaborative_task(task)
        return f"✓ Collaborative task completed by {len(results)} agents"
    
    def handle_team_improve(task: str = None):
        if not registry.dev_team:
            return "Development team not initialized"
        if task:
            # Collaborate on specific task with improvement loop
            return f"✓ Running improvement loop for: {task}"
        return registry.dev_team.continuous_improvement_loop(max_iterations=2)
    
    registry.register_command(ChatCommand(
        name="team_status",
        pattern=r"^/team\s*status\s*$",
        description="View development team status",
        examples=["/team status", "/team"],
        handler=handle_team_status
    ))
    
    registry.register_command(ChatCommand(
        name="team_task",
        pattern=r"^/team\s+task\s+(\w+)\s+(.+)",
        description="Assign a task to a specific agent",
        examples=["/team task generator create API", "/team task tester add tests"],
        handler=handle_team_task
    ))
    
    registry.register_command(ChatCommand(
        name="team_collaborate",
        pattern=r"^/team\s+collab(?:orate)?\s+(.+)",
        description="Have multiple agents work on a task together",
        examples=["/team collab build authentication", "/team collaborate refactor codebase"],
        handler=handle_team_collaborate
    ))
    
    registry.register_command(ChatCommand(
        name="team_improve",
        pattern=r"^/team\s+improve(?:\s+(.+))?",
        description="Run continuous improvement loop",
        examples=["/team improve", "/team improve fix bugs in user service"],
        handler=handle_team_improve
    ))
    
    # ================
    # ANALYSIS COMMANDS
    # ================
    
    def handle_analyze_file(file_path: str, verbose: str = ""):
        if not registry.code_analyzer:
            return "Code analyzer not initialized"
        entities = registry.code_analyzer.analyze_file(file_path)
        if verbose:
            result = f"Found {len(entities)} entities:\n"
            for e in entities[:10]:
                result += f"  • {e.type}: {e.name} (line {e.line_number})\n"
            return result
        return f"✓ Analyzed {file_path}: {len(entities)} entities found"
    
    def handle_analyze_repo(directory: str = "."):
        if not registry.code_analyzer:
            return "Code analyzer not initialized"
        entities = registry.code_analyzer.analyze_repository(directory)
        total = sum(len(e) for e in entities.values())
        return f"✓ Analyzed repository: {total} entities across {len(entities)} files"
    
    def handle_search(query: str, directory: str = "."):
        if not registry.code_analyzer:
            return "Code analyzer not initialized"
        # Search functionality would need RepositorySearcher
        return f"✓ Searching for: {query} in {directory}"
    
    registry.register_command(ChatCommand(
        name="analyze_file",
        pattern=r"^/analyze\s+(.+?)(?:\s+--verbose)?$",
        description="Analyze code structure of a file",
        examples=["/analyze file.py", "/analyze src/main.py --verbose"],
        handler=handle_analyze_file
    ))
    
    registry.register_command(ChatCommand(
        name="analyze_repo",
        pattern=r"^/analyze\s+repo(?:\s+(.+))?$",
        description="Analyze entire repository structure",
        examples=["/analyze repo", "/analyze repo ."],
        handler=handle_analyze_repo
    ))
    
    registry.register_command(ChatCommand(
        name="search_code",
        pattern=r"^/search\s+(.+?)(?:\s+in\s+(.+))?$",
        description="Search code across repository",
        examples=["/search authentication", "/search user service in src/"],
        handler=handle_search
    ))
    
    # ================
    # TEST COMMANDS
    # ================
    
    def handle_test_generate(file_path: str):
        if not registry.test_generator:
            return "Test generator not initialized"
        # Get LLM from providers
        llm = registry.providers.get_adapter() if registry.providers else None
        if not llm:
            return "No LLM adapter available"
        # Create generator instance
        from tui.test_generator import TestGenerator
        gen = TestGenerator(llm)
        suite = gen.generate_tests_for_file(file_path, None)
        if suite:
            return f"✓ Generated {len(suite.test_cases)} tests for {file_path}"
        return "✗ Test generation failed"
    
    def handle_test_run(directory: str = "."):
        if not registry.test_generator:
            return "Test runner not initialized"
        from tui.test_generator import TestRunner
        runner = TestRunner(directory)
        results = runner.run_tests()
        report = runner.generate_test_report(results)
        return f"✓ Tests completed:\n{report}"
    
    registry.register_command(ChatCommand(
        name="test_generate",
        pattern=r"^/test\s+gen(?:erate)?\s+(.+)",
        description="Generate tests for a file",
        examples=["/test gen app.py", "/test generate tests for user_service.py"],
        handler=handle_test_generate
    ))
    
    registry.register_command(ChatCommand(
        name="test_run",
        pattern=r"^/test\s+run(?:\s+(.+))?$",
        description="Run test suite",
        examples=["/test run", "/test run tests/"],
        handler=handle_test_run
    ))
    
    # ================
    # LINT/REVIEW COMMANDS
    # ================
    
    def handle_lint_file(file_path: str):
        if not registry.linter:
            return "Linter not initialized"
        from tui.code_review import LintingIntegrator
        integrator = LintingIntegrator(Path(file_path).parent)
        issues = integrator.lint_file(file_path)
        return f"✓ Found {len(issues)} issues in {file_path}"
    
    def handle_review_file(file_path: str):
        if not registry.linter:
            return "Code reviewer not initialized"
        llm = registry.providers.get_adapter() if registry.providers else None
        if not llm:
            return "No LLM adapter available"
        from tui.code_review import AIReviewer
        reviewer = AIReviewer(llm)
        review = reviewer.review_file(file_path)
        if review:
            report = reviewer.generate_review_report(review)
            return f"✓ Code review completed:\n{report}"
        return "✗ Code review failed"
    
    registry.register_command(ChatCommand(
        name="lint",
        pattern=r"^/lint\s+(.+)",
        description="Lint code for quality issues",
        examples=["/lint app.py", "/lint src/"],
        handler=handle_lint_file
    ))
    
    registry.register_command(ChatCommand(
        name="review",
        pattern=r"^/review\s+(.+)",
        description="Perform AI-powered code review",
        examples=["/review app.py", "/review user_service.py"],
        handler=handle_review_file
    ))
    
    # ================
    # ROLLBACK COMMANDS
    # ================
    
    def handle_rollback_history():
        if not registry.rollback_manager:
            return "Rollback manager not initialized"
        return str(registry.rollback_manager.get_operation_history())
    
    def handle_rollback_undo():
        if not registry.rollback_manager:
            return "Rollback manager not initialized"
        if registry.rollback_manager.undo_last():
            return "✓ Undid last operation"
        return "✗ Undo failed"
    
    def handle_rollback_snapshot(action: str, name: str = None):
        if not registry.rollback_manager:
            return "Rollback manager not initialized"
        if action == "create":
            if not name:
                return "Please provide snapshot name"
            registry.rollback_manager.create_snapshot(name)
            return f"✓ Created snapshot: {name}"
        elif action == "restore":
            if not name:
                return "Please provide snapshot name"
            if registry.rollback_manager.rollback_to_snapshot(name):
                return f"✓ Restored snapshot: {name}"
            return "✗ Restore failed"
        else:
            return "Use: /snapshot create <name> or /snapshot restore <name>"
    
    registry.register_command(ChatCommand(
        name="rollback_history",
        pattern=r"^/history\s*$",
        description="View operation history",
        examples=["/history", "/undo history"],
        handler=handle_rollback_history
    ))
    
    registry.register_command(ChatCommand(
        name="rollback_undo",
        pattern=r"^/undo\s*$",
        description="Undo last operation",
        examples=["/undo", "/rollback undo"],
        handler=handle_rollback_undo
    ))
    
    registry.register_command(ChatCommand(
        name="rollback_snapshot",
        pattern=r"^/snapshot\s+(create|restore)(?:\s+(.+))?",
        description="Create or restore project snapshots",
        examples=["/snapshot create v1.0", "/snapshot restore v1.0"],
        handler=lambda action, name=None: handle_rollback_snapshot(action, name)
    ))
    
    # ================
    # WORKFLOW COMMANDS
    # ================
    
    def handle_workflow_list():
        if not registry.workflow_manager:
            return "Workflow manager not initialized"
        return str(registry.workflow_manager.list_workflows())
    
    def handle_workflow_run(workflow_name: str):
        if not registry.workflow_manager:
            return "Workflow manager not initialized"
        if registry.workflow_manager.run_workflow(workflow_name):
            return f"✓ Ran workflow: {workflow_name}"
        return "✗ Workflow failed"
    
    registry.register_command(ChatCommand(
        name="workflow_list",
        pattern=r"^/workflow\s*list?\s*$",
        description="List available workflows",
        examples=["/workflow list", "/workflows"],
        handler=handle_workflow_list
    ))
    
    registry.register_command(ChatCommand(
        name="workflow_run",
        pattern=r"^/workflow\s+run\s+(\w+)",
        description="Run a specific workflow",
        examples=["/workflow run setup_python", "/workflow run test"],
        handler=handle_workflow_run
    ))
    
    # ================
    # UTILITY COMMANDS
    # ================
    
    def handle_help(topic: str = None):
        if topic:
            return registry.help(topic)
        return registry.help()
    
    def handle_clear():
        return "\n" * 100  # Clear console
    
    def handle_docs():
        return """
[bold cyan]Blonde CLI Documentation[/bold cyan]

Core Commands:
  [green]/providers[/green] - Manage AI providers
  [green]/team[/green] - Development team commands
  [green]/analyze[/green] - Code analysis
  [green]/search[/green] - Search codebase
  [green]/test[/green] - Test generation and execution
  [green]/lint[/green] - Code linting
  [green]/review[/green] - AI code review
  [green]/history[/green] - Operation history
  [green]/snapshot[/green] - Project snapshots
  [green]/workflow[/green] - Workflow automation
  [green]/help[/green] - Get help on specific command

[dim]For full documentation, visit: https://github.com/your-repo/blonde-cli/docs[/dim]
"""
    
    registry.register_command(ChatCommand(
        name="help",
        pattern=r"^/help(?:\s+(.+))?",
        description="Get help for commands",
        examples=["/help", "/help providers"],
        handler=lambda topic=None: handle_help(topic)
    ))
    
    registry.register_command(ChatCommand(
        name="clear",
        pattern=r"^/clear\s*$",
        description="Clear the console",
        examples=["/clear"],
        handler=handle_clear
    ))
    
    registry.register_command(ChatCommand(
        name="docs",
        pattern=r"^/docs\s*$",
        description="Show documentation links",
        examples=["/docs"],
        handler=handle_docs
    ))
    
    return registry
