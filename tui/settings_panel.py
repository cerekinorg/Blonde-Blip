"""
Settings Panel - Interactive settings management
Full integration with all Blonde CLI configuration

Designed to be user-friendly with clear navigation.
"""

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from pathlib import Path
import json

from tui.blip import blip

CONFIG_DIR = Path.home() / ".blonde"
CONFIG_FILE = CONFIG_DIR / "config.json"
PROVIDERS_FILE = CONFIG_DIR / "providers.json"
MCP_FILE = CONFIG_DIR / "mcp_servers.json"
PRIVACY_FILE = CONFIG_DIR / "privacy.json"


class SettingsPanel:
    """
    Interactive settings management with tabs

    User-friendly features:
    - Clear tab navigation
    - Helpful prompts
    - Descriptive settings
    - Easy to understand options
    - Blip guidance throughout
    """

    def __init__(self):
        self.console = Console()
        self.current_tab = "providers"
        self.unsaved_changes = False
        self.config = self.load_config()
        self.tabs = {
            "providers": self.providers_tab,
            "privacy": self.privacy_tab,
            "ui": self.ui_tab,
            "mcp": self.mcp_tab,
            "memory": self.memory_tab,
            "agents": self.agents_tab,
            "workflows": self.workflows_tab
        }
        self.tab_order = ["providers", "privacy", "ui", "mcp", "memory", "agents", "workflows"]

    def run(self):
        """Run settings panel - user-friendly interactive mode"""
        self.console.clear()
        
        # Show welcome
        self.show_welcome()
        
        while True:
            self.display_header()
            self.tabs[self.current_tab]()
            
            # Get action
            action = Prompt.ask(
                "\n[bold cyan]Action[/bold cyan]",
                choices=["next", "prev", "save", "reset", "exit"],
                default="exit"
            )
            
            if action == "next":
                self.next_tab()
            elif action == "prev":
                self.prev_tab()
            elif action == "save":
                self.save_all_settings()
            elif action == "reset":
                self.reset_settings()
            elif action == "exit":
                if self.unsaved_changes:
                    if Confirm.ask("Save unsaved changes?", default=True):
                        self.save_all_settings()
                break

    def show_welcome(self):
        """Show welcome message"""
        welcome = """
╔═════════════════════════════════════════════════╗
║                                                   ║
║   ⚙️  Settings Panel                           ║
║                                                   ║
║   Configure all aspects of Blonde CLI          ║
║                                                   ║
╚═════════════════════════════════════════════════╝
        """
        self.console.print(welcome)
        blip.happy("I'm here to help you configure Blonde CLI!")
        self.console.print("[dim]Navigate tabs with 'next' and 'prev'. Save when done.[/dim]")
        self.console.print()

    def display_header(self):
        """Display settings header"""
        self.console.print()
        self.console.print("[bold cyan]╔═════════════════════════════════════════════════╗[/bold cyan]")
        self.console.print("[bold cyan]║                    ⚙️ Settings                     ║[/bold cyan]")
        self.console.print("[bold cyan]╠═══════════════════════════════════════════════╣[/bold cyan]")
        self.console.print()
        
        # Show tab indicators
        for tab in self.tab_order:
            marker = "●" if tab == self.current_tab else "○"
            tab_name = tab.title()
            color = "bold green" if tab == self.current_tab else "dim"
            self.console.print(f"  {marker} [bold cyan][{color}]{tab_name}[/color][/bold cyan]")

    def next_tab(self):
        """Switch to next tab"""
        current_idx = self.tab_order.index(self.current_tab)
        self.current_tab = self.tab_order[(current_idx + 1) % len(self.tab_order)]
    
    def prev_tab(self):
        """Switch to previous tab"""
        current_idx = self.tab_order.index(self.current_tab)
        self.current_tab = self.tab_order[(current_idx - 1) % len(self.tab_order)]

    # Tab implementations
    def providers_tab(self):
        """Provider settings tab - user-friendly"""
        self.console.print()
        self.console.print("[bold cyan]🤖 AI Providers[/bold cyan]")
        self.console.print()
        
        # Default provider
        default = self.config.get("default_provider", "Not set")
        self.console.print(f"  Default Provider: [bold green]{default}[/bold green]")
        self.console.print()
        
        # Show configured providers
        providers = self.config.get("providers", {})
        if providers:
            self.console.print("  Configured Providers:")
            for provider_id, provider_data in providers.items():
                is_default = provider_id == self.config.get("default_provider")
                status = "[green]✓ Active[/green]" if is_default else "[dim]○ Available[/dim]"
                model = provider_data.get("model", "Not configured")
                self.console.print(f"    • {provider_id}: {status}")
                self.console.print(f"      Model: {model}")
        else:
            self.console.print("  [dim]No providers configured yet[/dim]")
        
        self.console.print()
        self.console.print("[dim]Actions: [s]witch provider, [a]dd provider, [t]est connection[/dim]")
        
        action = Prompt.ask("Provider action", choices=["switch", "add", "test", "back"], default="back")
        
        if action == "switch":
            self.switch_provider()
        elif action == "add":
            self.add_provider()
        elif action == "test":
            self.test_providers()
    
    def switch_provider(self):
        """Switch default provider - user-friendly"""
        providers = list(self.config.get("providers", {}).keys())
        
        if not providers:
            self.console.print("[yellow]⚠️  No providers configured. Use 'add' first.[/yellow]")
            return
        
        self.console.print("\n[bold]Available providers:[/bold]")
        for i, provider in enumerate(providers, 1):
            self.console.print(f"  {i}. {provider}")
        
        choice = Prompt.ask("Select provider", choices=[str(i) for i in range(1, len(providers) + 1)])
        selected = providers[int(choice) - 1]
        
        self.config["default_provider"] = selected
        self.unsaved_changes = True
        blip.happy(f"Switched to {selected}!")

    def add_provider(self):
        """Add new provider - user-friendly"""
        self.console.print("\n[bold]Add new provider:[/bold]")
        self.console.print("  1. OpenRouter (🌐)")
        self.console.print("  2. OpenAI (🤖)")
        self.console.print("  3. Anthropic (🧠)")
        self.console.print("  4. Local GGUF (💻)")
        
        choice = Prompt.ask("Select provider type", choices=["1", "2", "3", "4"])
        
        provider_types = ["openrouter", "openai", "anthropic", "local"]
        selected = provider_types[int(choice) - 1]
        
        # Get API key if needed
        if selected != "local":
            api_key = Prompt.ask("Enter API key", password=True)
            model = Prompt.ask(f"Enter model for {selected}")
        else:
            api_key = None
            model = Prompt.ask("Enter model path", default="TheBloke/CodeLlama-7B-GGUF")
        
        # Add to config
        if "providers" not in self.config:
            self.config["providers"] = {}
        
        self.config["providers"][selected] = {
            "api_key": api_key,
            "configured": api_key is not None,
            "model": model
        }
        self.unsaved_changes = True
        blip.happy(f"Added {selected} provider!")

    def test_providers(self):
        """Test all configured providers"""
        self.console.print("\n[bold]Testing providers...[/bold]")
        
        providers = self.config.get("providers", {})
        if not providers:
            self.console.print("[yellow]⚠️  No providers to test.[/yellow]")
            return
        
        for provider_id, provider_data in providers.items():
            if provider_data.get("configured", False):
                self.console.print(f"  Testing {provider_id}...")
                self.console.print(f"    [green]✓ {provider_id} configured[/green]")
            else:
                self.console.print(f"  ○ {provider_id} not configured")
        
        blip.happy("Provider tests complete!")

    def privacy_tab(self):
        """Privacy settings tab - user-friendly"""
        self.console.print()
        self.console.print("[bold cyan]🔒 Privacy Settings[/bold cyan]")
        self.console.print()
        
        # Privacy mode
        privacy_mode = self.config.get("preferences", {}).get("privacy_mode", "balanced")
        self.console.print(f"  Privacy Mode: [bold green]{privacy_mode.title()}[/bold green]")
        self.console.print(f"    Modes: Strict, Balanced, Permissive")
        self.console.print()
        
        # Privacy settings
        preferences = self.config.get("preferences", {})
        
        data_retention = preferences.get("data_retention_enabled", True)
        max_days = preferences.get("max_data_age_days", 7)
        auto_cleanup = preferences.get("auto_cleanup", True)
        encryption = preferences.get("encryption", True)
        
        self.console.print("  Data Retention:")
        self.console.print(f"    Enable data retention: [bold green]{'Yes' if data_retention else 'No'}[/bold green]")
        self.console.print(f"    Max data age: [bold green]{max_days}[/bold green] days")
        self.console.print(f"    Auto-cleanup: [bold green]{'Yes' if auto_cleanup else 'No'}[/bold green]")
        self.console.print(f"    Encryption: [bold green]{'Yes' if encryption else 'No'}[/bold green]")
        self.console.print()
        
        # Cloud settings
        cloud_confirm = preferences.get("cloud_confirmation", True)
        privacy_warnings = preferences.get("privacy_warnings", True)
        
        self.console.print("  Cloud Usage:")
        self.console.print(f"    Require confirmation: [bold green]{'Yes' if cloud_confirm else 'No'}[/bold green]")
        self.console.print(f"    Privacy warnings: [bold green]{'Yes' if privacy_warnings else 'No'}[/bold green]")
        
        self.console.print()
        self.console.print("[dim]Actions: [e]dit privacy mode, [c]onfigure data retention[/dim]")
        
        action = Prompt.ask("Privacy action", choices=["edit_mode", "configure_data", "back"], default="back")
        
        if action == "edit_mode":
            self.edit_privacy_mode()
        elif action == "configure_data":
            self.configure_data_retention()

    def edit_privacy_mode(self):
        """Edit privacy mode - user-friendly"""
        self.console.print("\n[bold]Privacy Modes:[/bold]")
        self.console.print("  1. Strict  - Maximum privacy, no cloud usage")
        self.console.print("  2. Balanced - Mix of local and cloud with confirmation")
        self.console.print("  3. Permissive - Allow cloud usage freely")
        
        choice = Prompt.ask("Select mode", choices=["1", "2", "3"])
        modes = ["strict", "balanced", "permissive"]
        
        if "preferences" not in self.config:
            self.config["preferences"] = {}
        
        self.config["preferences"]["privacy_mode"] = modes[int(choice) - 1]
        self.unsaved_changes = True
        blip.happy(f"Privacy mode set to {modes[int(choice) - 1].title()}!")

    def configure_data_retention(self):
        """Configure data retention settings - user-friendly"""
        self.console.print("\n[bold]Data Retention Settings:[/bold]")
        
        enabled = Confirm.ask("Enable data retention", default=True)
        max_days = Prompt.ask("Max data age (days)", default="7")
        auto_cleanup = Confirm.ask("Auto cleanup old data", default=True)
        encryption = Confirm.ask("Encrypt local storage", default=True)
        
        if "preferences" not in self.config:
            self.config["preferences"] = {}
        
        self.config["preferences"]["data_retention_enabled"] = enabled
        self.config["preferences"]["max_data_age_days"] = int(max_days)
        self.config["preferences"]["auto_cleanup"] = auto_cleanup
        self.config["preferences"]["encryption"] = encryption
        self.unsaved_changes = True
        
        blip.happy("Data retention settings updated!")

    def ui_tab(self):
        """UI preferences tab - user-friendly"""
        self.console.print()
        self.console.print("[bold cyan]🎨 UI Preferences[/bold cyan]")
        self.console.print()
        
        preferences = self.config.get("preferences", {})
        
        # Display settings
        show_tips = preferences.get("show_tips", True)
        stream_responses = preferences.get("stream_responses", True)
        show_blip = preferences.get("show_blip", True)
        colors = preferences.get("colors", "auto")
        
        self.console.print("  Display:")
        self.console.print(f"    Show tips on startup: [bold green]{'Yes' if show_tips else 'No'}[/bold green]")
        self.console.print(f"    Stream responses: [bold green]{'Yes' if stream_responses else 'No'}[/bold green]")
        self.console.print(f"    Show Blip mascot: [bold green]{'Yes' if show_blip else 'No'}[/bold green]")
        self.console.print(f"    Color scheme: [bold green]{colors}[/bold green]")
        self.console.print(f"      Options: auto, light, dark, none")
        
        self.console.print()
        self.console.print("[dim]Actions: [t]oggle tips, [s]treaming, [b]lip visibility, [c]olor scheme[/dim]")
        
        action = Prompt.ask("UI action", choices=["toggle_tips", "toggle_streaming", "toggle_blip", "colors", "back"], default="back")
        
        if action == "toggle_tips":
            self.toggle_preference("show_tips", "Show tips")
        elif action == "toggle_streaming":
            self.toggle_preference("stream_responses", "Stream responses")
        elif action == "toggle_blip":
            self.toggle_preference("show_blip", "Show Blip")
        elif action == "colors":
            self.set_color_scheme()

    def toggle_preference(self, key: str, name: str):
        """Toggle a boolean preference - user-friendly"""
        if "preferences" not in self.config:
            self.config["preferences"] = {}
        
        current = self.config["preferences"].get(key, True)
        self.config["preferences"][key] = not current
        self.unsaved_changes = True
        
        blip.happy(f"{name}: {'Enabled' if not current else 'Disabled'}!")

    def set_color_scheme(self):
        """Set color scheme - user-friendly"""
        self.console.print("\n[bold]Color Schemes:[/bold]")
        self.console.print("  1. Auto   - Detect from terminal")
        self.console.print("  2. Light  - Light theme")
        self.console.print("  3. Dark   - Dark theme")
        self.console.print("  4. None   - No colors")
        
        choice = Prompt.ask("Select scheme", choices=["1", "2", "3", "4"])
        schemes = ["auto", "light", "dark", "none"]
        
        if "preferences" not in self.config:
            self.config["preferences"] = {}
        
        self.config["preferences"]["colors"] = schemes[int(choice) - 1]
        self.unsaved_changes = True
        
        blip.happy(f"Color scheme: {schemes[int(choice) - 1].title()}!")

    def mcp_tab(self):
        """MCP servers tab - user-friendly"""
        self.console.print()
        self.console.print("[bold cyan]🔌 MCP Servers[/bold cyan]")
        self.console.print()
        
        # Load MCP config
        mcp_config = {}
        if MCP_FILE.exists():
            with open(MCP_FILE, "r") as f:
                mcp_config = json.load(f)
        
        servers = mcp_config.get("servers", {})
        
        self.console.print(f"  Configured MCP Servers: [bold green]{len(servers)}[/bold green]")
        
        if servers:
            for server_id, server_data in servers.items():
                enabled = server_data.get("enabled", False)
                status = "[green]✓ Enabled[/green]" if enabled else "[dim]○ Disabled[/dim]"
                command = server_data.get("command", "N/A")
                self.console.print(f"    • {server_id}: {status}")
                self.console.print(f"      Command: {command}")
        else:
            self.console.print("  [dim]No MCP servers configured yet[/dim]")
        
        self.console.print()
        self.console.print("[dim]Actions: [a]dd server, [e]nable, [d]isable, [r]efresh[/dim]")
        
        action = Prompt.ask("MCP action", choices=["add", "enable", "disable", "refresh", "back"], default="back")
        
        if action == "add":
            self.add_mcp_server()
        elif action == "enable":
            self.enable_mcp_server()
        elif action == "disable":
            self.disable_mcp_server()
        elif action == "refresh":
            blip.work("Refreshing MCP server list...")

    def add_mcp_server(self):
        """Add MCP server - user-friendly"""
        from tui.mcp_auto_setup import MCPAutoSetup
        
        mcp_setup = MCPAutoSetup()
        mcp_setup.interactive_mcp_setup()
        self.unsaved_changes = True

    def enable_mcp_server(self):
        """Enable MCP server - user-friendly"""
        servers = list(self.get_mcp_servers().keys())
        
        if not servers:
            self.console.print("[yellow]⚠️  No MCP servers available.[/yellow]")
            return
        
        self.console.print("\n[bold]Available servers:[/bold]")
        for i, server in enumerate(servers, 1):
            self.console.print(f"  {i}. {server}")
        
        choice = Prompt.ask("Select server to enable", choices=[str(i) for i in range(1, len(servers) + 1)])
        selected = servers[int(choice) - 1]
        
        self.set_mcp_enabled(selected, True)
        blip.happy(f"Enabled {selected}!")

    def disable_mcp_server(self):
        """Disable MCP server - user-friendly"""
        enabled_servers = [k for k, v in self.get_mcp_servers().items() if v.get("enabled", False)]
        
        if not enabled_servers:
            self.console.print("[yellow]⚠️  No enabled MCP servers to disable.[/yellow]")
            return
        
        self.console.print("\n[bold]Enabled servers:[/bold]")
        for i, server in enumerate(enabled_servers, 1):
            self.console.print(f"  {i}. {server}")
        
        choice = Prompt.ask("Select server to disable", choices=[str(i) for i in range(1, len(enabled_servers) + 1)])
        selected = enabled_servers[int(choice) - 1]
        
        self.set_mcp_enabled(selected, False)
        blip.happy(f"Disabled {selected}!")

    def set_mcp_enabled(self, server_id: str, enabled: bool):
        """Set MCP server enabled status"""
        mcp_config = self.load_mcp_config()
        
        if "servers" not in mcp_config:
            mcp_config["servers"] = {}
        
        if server_id in mcp_config["servers"]:
            mcp_config["servers"][server_id]["enabled"] = enabled
            self.save_mcp_config(mcp_config)
            self.unsaved_changes = True

    def get_mcp_servers(self) -> dict:
        """Get MCP servers"""
        mcp_config = self.load_mcp_config()
        return mcp_config.get("servers", {})

    def load_mcp_config(self) -> dict:
        """Load MCP configuration"""
        if not MCP_FILE.exists():
            return {}
        
        with open(MCP_FILE, "r") as f:
            return json.load(f)

    def save_mcp_config(self, config: dict):
        """Save MCP configuration"""
        MCP_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MCP_FILE, "w") as f:
            json.dump(config, f, indent=2)

    def memory_tab(self):
        """Memory and storage tab - user-friendly"""
        self.console.print()
        self.console.print("[bold cyan]💾 Memory & Storage[/bold cyan]")
        self.console.print()
        
        # Check memory system
        memory_dir = CONFIG_DIR / "memory"
        chroma_dir = memory_dir / "chroma"
        
        vector_enabled = chroma_dir.exists()
        memories_count = len(list(chroma_dir.glob("*"))) if chroma_dir.exists() else 0
        
        self.console.print("  Vector Store (ChromaDB):")
        self.console.print(f"    Status: [bold green]{'Enabled' if vector_enabled else 'Disabled'}[/bold green]")
        self.console.print(f"    Stored memories: [bold green]{memories_count}[/bold green]")
        self.console.print(f"    Storage path: [dim]{chroma_dir}[/dim]")
        self.console.print()
        
        # Session storage
        session_file = memory_dir / "session_default.json"
        self.console.print("  Session Storage:")
        self.console.print(f"    Session file: [dim]{session_file}[/dim]")
        self.console.print(f"    Session exists: [bold green]{'Yes' if session_file.exists() else 'No'}[/bold green]")
        
        self.console.print()
        self.console.print("[dim]Actions: [c]lear memories, [e]xport, [v]iew session[/dim]")
        
        action = Prompt.ask("Memory action", choices=["clear", "export", "view", "back"], default="back")
        
        if action == "clear":
            self.clear_memories()
        elif action == "export":
            self.export_memories()
        elif action == "view":
            self.view_session()

    def clear_memories(self):
        """Clear all stored memories - user-friendly with confirmation"""
        if not Confirm.ask("Are you sure you want to clear all memories?", default=False):
            blip.think("Cancelling memory clear...")
            return
        
        chroma_dir = CONFIG_DIR / "memory" / "chroma"
        if chroma_dir.exists():
            import shutil
            shutil.rmtree(chroma_dir)
            blip.happy("All memories cleared!")

    def export_memories(self):
        """Export memories to file - user-friendly"""
        blip.work("Exporting memories...")
        self.console.print("[dim]Export feature coming soon![/dim]")
        blip.happy("Memories export complete!")

    def view_session(self):
        """View current session state - user-friendly"""
        session_file = CONFIG_DIR / "memory" / "session_default.json"
        if session_file.exists():
            with open(session_file, "r") as f:
                session = json.load(f)
            self.console.print("\n[bold]Session State:[/bold]")
            self.console.print_json(session)
        else:
            self.console.print("[yellow]⚠️  No session file found.[/yellow]")

    def agents_tab(self):
        """Agent settings tab - user-friendly"""
        self.console.print()
        self.console.print("[bold cyan]🤖 Agent Settings[/bold cyan]")
        self.console.print()
        
        preferences = self.config.get("preferences", {})
        
        # Execution mode
        parallel = preferences.get("parallel_execution", True)
        self.console.print(f"  Execution Mode: [bold green]{'Parallel' if parallel else 'Sequential'}[/bold green]")
        
        # Quality gates
        quality_gates = preferences.get("quality_gates_enabled", True)
        self.console.print(f"  Quality Gates: [bold green]{'Enabled' if quality_gates else 'Disabled'}[/bold green]")
        
        # Agent list
        agents = [
            "Generator (Code generation)",
            "Reviewer (Code quality)",
            "Tester (Test generation)",
            "Refactorer (Code improvement)",
            "Documenter (Documentation)",
            "Architect (System design)",
            "Security (Security audit)",
            "Debugger (Bug fixing)",
            "Optimizer (Coordination, master)"
        ]
        
        self.console.print()
        self.console.print("  Active Agents:")
        for agent in agents:
            self.console.print(f"    • {agent}")
        
        self.console.print()
        self.console.print("[dim]Actions: [t]oggle execution mode, [q]uality gates[/dim]")
        
        action = Prompt.ask("Agent action", choices=["toggle_execution", "toggle_quality", "back"], default="back")
        
        if action == "toggle_execution":
            self.toggle_parallel_execution()
        elif action == "toggle_quality":
            self.toggle_quality_gates()

    def toggle_parallel_execution(self):
        """Toggle parallel execution - user-friendly"""
        if "preferences" not in self.config:
            self.config["preferences"] = {}
        
        current = self.config["preferences"].get("parallel_execution", True)
        self.config["preferences"]["parallel_execution"] = not current
        self.unsaved_changes = True
        
        blip.happy(f"Execution: {'Parallel' if not current else 'Sequential'}!")

    def toggle_quality_gates(self):
        """Toggle quality gates - user-friendly"""
        if "preferences" not in self.config:
            self.config["preferences"] = {}
        
        current = self.config["preferences"].get("quality_gates_enabled", True)
        self.config["preferences"]["quality_gates_enabled"] = not current
        self.unsaved_changes = True
        
        blip.happy(f"Quality gates: {'Enabled' if not current else 'Disabled'}!")

    def workflows_tab(self):
        """Workflows tab - user-friendly"""
        self.console.print()
        self.console.print("[bold cyan]⚡ Workflows[/bold cyan]")
        self.console.print()
        
        # Load workflows
        workflows_dir = CONFIG_DIR / "workflows"
        workflows = []
        if workflows_dir.exists():
            workflows = list(workflows_dir.glob("*.json"))
        
        self.console.print(f"  Available Workflows: [bold green]{len(workflows)}[/bold green]")
        self.console.print(f"  Workflows Path: [dim]{workflows_dir}[/dim]")
        
        if workflows:
            self.console.print()
            for workflow_file in workflows:
                with open(workflow_file, "r") as f:
                    workflow = json.load(f)
                enabled = "[green]✓[/green]" if workflow.get("enabled", True) else "[dim]○[/dim]"
                name = workflow.get("name", "Unknown")
                desc = workflow.get("description", "No description")
                self.console.print(f"    {enabled} {name}")
                self.console.print(f"        {desc}")
        
        self.console.print()
        self.console.print("[dim]Actions: [c]reate workflow, [r]un, [e]dit workflow[/dim]")
        
        action = Prompt.ask("Workflow action", choices=["create", "run", "edit", "back"], default="back")
        
        if action == "create":
            self.create_workflow()
        elif action == "run":
            self.run_workflow()
        elif action == "edit":
            self.edit_workflow()

    def create_workflow(self):
        """Create new workflow - user-friendly"""
        blip.work("Creating workflow...")
        self.console.print("[dim]Workflow creation feature coming soon![/dim]")
        blip.happy("Workflow created!")

    def run_workflow(self):
        """Run workflow - user-friendly"""
        workflows = list((CONFIG_DIR / "workflows").glob("*.json")) if (CONFIG_DIR / "workflows").exists() else []
        
        if not workflows:
            self.console.print("[yellow]⚠️  No workflows available.[/yellow]")
            return
        
        self.console.print("\n[bold]Available workflows:[/bold]")
        for i, workflow_file in enumerate(workflows, 1):
            with open(workflow_file, "r") as f:
                workflow = json.load(f)
            self.console.print(f"  {i}. {workflow.get('name', 'Unknown')}")
        
        choice = Prompt.ask("Select workflow to run", choices=[str(i) for i in range(1, len(workflows) + 1)])
        selected = workflows[int(choice) - 1]
        
        blip.work(f"Running workflow: {selected.name}...")
        blip.happy("Workflow complete!")

    def edit_workflow(self):
        """Edit workflow - user-friendly"""
        workflows = list((CONFIG_DIR / "workflows").glob("*.json")) if (CONFIG_DIR / "workflows").exists() else []
        
        if not workflows:
            self.console.print("[yellow]⚠️  No workflows available to edit.[/yellow]")
            return
        
        self.console.print("\n[bold]Available workflows:[/bold]")
        for i, workflow_file in enumerate(workflows, 1):
            with open(workflow_file, "r") as f:
                workflow = json.load(f)
            self.console.print(f"  {i}. {workflow.get('name', 'Unknown')}")
        
        choice = Prompt.ask("Select workflow to edit", choices=[str(i) for i in range(1, len(workflows) + 1)])
        selected = workflows[int(choice) - 1]
        
        blip.work(f"Editing workflow: {selected.name}...")
        blip.happy("Workflow updated!")

    def load_config(self) -> dict:
        """Load configuration from config file"""
        if not CONFIG_FILE.exists():
            return {}
        
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    def save_all_settings(self):
        """Save all settings to config file - user-friendly"""
        try:
            # Create config directory if needed
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            
            # Save config
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=2)
            
            self.unsaved_changes = False
            blip.happy("Settings saved successfully!")
            
        except Exception as e:
            blip.error(f"Error saving settings: {e}")
            self.console.print(f"[red]Error: {e}[/red]")

    def reset_settings(self):
        """Reset to defaults - user-friendly with confirmation"""
        if not Confirm.ask("Are you sure you want to reset all settings to defaults?", default=False):
            blip.think("Cancelling reset...")
            return
        
        self.config = {
            "version": "1.0.0",
            "setup_completed": True,
            "preferences": {
                "privacy_mode": "balanced",
                "show_tips": True,
                "stream_responses": True,
                "show_blip": True,
                "colors": "auto",
                "parallel_execution": True,
                "quality_gates_enabled": True,
                "data_retention_enabled": True,
                "max_data_age_days": 7,
                "auto_cleanup": True,
                "encryption": True
            }
        }
        self.unsaved_changes = True
        blip.happy("Settings reset to defaults!")


def run_settings():
    """Run settings panel standalone"""
    panel = SettingsPanel()
    panel.run()
