"""
MCP Auto-Setup Enhancement

Enhanced setup wizard with:
- Auto-detect common MCP servers
- Interactive MCP installation
- One-click enable/disable
- Pre-configured MCP templates
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()


class MCPAutoSetup:
    """
    Enhanced MCP auto-setup for the setup wizard.
    
    Automatically detects, recommends, and configures MCP servers
    based on user's project and workflow.
    """

    # Pre-configured MCP server definitions
    MCP_SERVERS = {
        "filesystem": {
            "name": "Filesystem",
            "package": "@modelcontextprotocol/server-filesystem",
            "description": "Access local files via MCP",
            "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
            "env_var": None,
            "required_env_vars": [],
            "recommended": True,
            "category": "files"
        },
        "github": {
            "name": "GitHub",
            "package": "@modelcontextprotocol/server-github",
            "description": "Access GitHub repositories via MCP",
            "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/github",
            "env_var": "GITHUB_TOKEN",
            "required_env_vars": ["GITHUB_TOKEN"],
            "recommended": False,
            "category": "git"
        },
        "tavily": {
            "name": "Tavily (Web Search)",
            "package": "@tavily-ai/tavily-mcp",
            "description": "Web search and retrieval via Tavily AI",
            "url": "https://github.com/tavily-ai/tavily-mcp",
            "env_var": "TAVILY_API_KEY",
            "required_env_vars": ["TAVILY_API_KEY"],
            "recommended": False,
            "category": "web_search"
        },
        "brave-search": {
            "name": "Brave Search",
            "package": "@brave-search/mcp",
            "description": "Brave Search MCP server",
            "url": "https://github.com/brave-search/mcp-server",
            "env_var": None,
            "required_env_vars": [],
            "recommended": False,
            "category": "web_search"
        },
        "postgres": {
            "name": "PostgreSQL",
            "package": "@sourcegraph/mcp-postgres",
            "description": "Access PostgreSQL databases",
            "url": "https://github.com/sourcegraph/mcp-postgres",
            "env_var": "DATABASE_URL",
            "required_env_vars": ["DATABASE_URL"],
            "recommended": False,
            "category": "database"
        }
    }

    def __init__(self):
        self.config_dir = Path.home() / ".blonde"
        self.mcp_config_file = self.config_dir / "mcp_servers.json"
        self.installed_servers = {}
        self.detected_needs = []

    def detect_installed_mcps(self) -> Dict[str, Dict[str, Any]]:
        """Detect which MCP servers are already installed"""
        installed = {}

        for server_id, config in self.MCP_SERVERS.items():
            # Check if package is installed
            if config["package"]:
                try:
                    import subprocess
                    result = subprocess.run(
                        ["npm", "list", "-g", "--depth=0"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    if config["package"] in result.stdout:
                        installed[server_id] = True

                except:
                    installed[server_id] = False

        return installed

    def detect_user_needs(self, project_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Analyze user's project to recommend MCP servers.
        
        Scans for:
        - Git repositories
        - API files
        - Test files
        - Database usage
        - Web search needs
        """
        needs = []

        if not project_path:
            project_path = Path.cwd()

        # Scan for indicators
        # Git repository
        if (project_path / ".git").exists():
            needs.append(self.MCP_SERVERS["github"])
            console.print("[dim]→ Detected: Git repository - GitHub MCP recommended[/dim]")

        # Scan for API files
        for file in project_path.rglob("**/*api*.{py,ts,js}"):
            needs.append(self.MCP_SERVERS["filesystem"])
            break

        # Scan for database connections
        for file in project_path.rglob("**/*{postgres,mysql,sqlite,mongo}*.{py,ts,js}"):
            needs.append(self.MCP_SERVERS["postgres"])

        # Scan for web/API integration needs
        if any(file.exists() for file in project_path.rglob("**/*fetch*,*http*,*request*,*api*client*.{py,ts,js}")):
            needs.append(self.MCP_SERVERS["tavily"])

        return needs

    def show_mcp_recommendations(self, detected_needs: List[Dict[str, Any]]):
        """Show recommended MCP servers based on detected needs"""
        if not detected_needs:
            console.print("[green]✓ No specific MCP needs detected for your project[/green]")
            return

        console.print("[cyan]📊 Recommended MCP Servers:[/cyan]")
        console.print()

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Category", width=15)
        table.add_column("MCP Server", width=20)
        table.add_column("Description", width=40)
        table.add_column("Install?", width=10)

        all_servers = list(self.MCP_SERVERS.keys())

        for server_id in all_servers:
            server = self.MCP_SERVERS[server_id]
            is_recommended = server.get("recommended", False)
            in_needs = any(n["name"] for n in detected_needs)
            install_marker = "[green]✓" if server_id in [n["name"] for n in detected_needs] else "[dim] "

            table.add_row(
                Text(server.get("category"), style="dim"),
                Text(server["name"], style="bold" if is_recommended else "dim"),
                Text(server["description"], style="white"),
                Text(install_marker, style="white")
            )

        console.print(table)

        return detected_needs

    def interactive_mcp_setup(self):
        """Interactive MCP server setup"""
        console.print()
        console.print("[cyan]╔════════════════════════════════════════════╗[/cyan]")
        console.print("[cyan]║         📦 MCP Server Setup Wizard             ║[/cyan]")
        console.print("[cyan]╠═══════════════════════════════════════╣[/cyan]")
        console.print()

        # Detect needs
        console.print("[bold]Step 1: Analyzing your project...[/bold]")
        project_path = Path.cwd()
        detected_needs = self.detect_user_needs(project_path)
        self.detected_needs = detected_needs

        console.print()
        console.print("[bold]Step 2: Reviewing recommendations...[/bold]")
        self.show_mcp_recommendations(detected_needs)

        # Show available MCP servers
        console.print()
        console.print("[bold]Available MCP Servers:[/bold]")
        console.print()

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", width=5)
        table.add_column("Name", width=20)
        table.add_column("Category", width=15)
        table.add_column("Recommended", width=12)

        for i, (server_id, config) in enumerate(self.MCP_SERVERS.items()):
            is_recommended = config.get("recommended", False)
            marker = "[dim] (auto)" if is_recommended else ""
            table.add_row(
                str(i + 1),
                Text(config["name"], style="bold"),
                Text(config.get("category"), style="dim"),
                Text("Yes" if is_recommended else "No", style="yellow" if is_recommended else "red")
            )

        console.print(table)

        # Prompt for selection
        console.print()
        selected_ids = []

        while True:
            selection = Prompt.ask(
                "\nSelect MCP servers to install (comma-separated, or 'done'):",
                default="done"
            )

            if selection.lower() == "done":
                break

            if selection.strip():
                for server_id in selection.split(","):
                    server_id = server_id.strip()
                    if server_id in self.MCP_SERVERS:
                        selected_ids.append(server_id)
                        console.print(f"  → Selected: {self.MCP_SERVERS[server_id]['name']}")

            console.print()
            if selected_ids:
                self.install_mcps(selected_ids)
            else:
                console.print("[dim]No servers selected.[/dim]")
                break

    def install_mcps(self, server_ids: List[str]) -> bool:
        """Install selected MCP servers"""
        console.print()
        console.print("[cyan]⏳ Installing MCP servers...[/cyan]")
        console.print()

        all_success = True

        for server_id in server_ids:
            server = self.MCP_SERVERS[server_id]

            # Check env requirements
            if server["env_var"]:
                env_var = server["env_var"]
                env_value = os.getenv(env_var)

                if not env_value:
                    console.print(f"[yellow]⚠️  Required: {env_var}[/yellow]")
                    console.print(f"  Example: export {env_var}=your_value")
                    all_success = False

            # Install package
            if server["package"]:
                package = server["package"]

                console.print(f"  → Installing {package}...")
                try:
                    result = subprocess.run(
                        ["npm", "install", "-g", package],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )

                    if result.returncode == 0:
                        console.print(f"[green]✓ {package} installed successfully[/green]")
                    else:
                        console.print(f"[red]✗ Failed to install {package}[/red]")
                        all_success = False

                except Exception as e:
                    console.print(f"[red]✗ Error installing {package}: {e}[/red]")
                    all_success = False

        console.print()

        if all_success:
            self.save_config(server_ids)

        return all_success

    def save_config(self, enabled_servers: List[str]):
        """Save MCP server configuration"""
        config = {
            "version": "1.0.0",
            "installed_servers": {},
            "enabled_servers": enabled_servers,
            "last_updated": datetime.now().isoformat()
        }

        for server_id in enabled_servers:
            if server_id in self.MCP_SERVERS:
                config["installed_servers"][server_id] = {
                    "installed": True,
                    "enabled": True,
                    "package": self.MCP_SERVERS[server_id]["package"]
                }

        config_file = self.mcp_config_file
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        console.print(f"[green]✓ MCP configuration saved to {config_file}[/green]")

    def load_config(self) -> Dict[str, Any]:
        """Load existing MCP configuration"""
        if not self.mcp_config_file.exists():
            return {}

        with open(self.mcp_config_file, "r") as f:
            return json.load(f)

    def enable_mcp(self, server_id: str):
        """Enable an MCP server"""
        config = self.load_config()

        if "installed_servers" not in config:
            config["installed_servers"] = {}

        config["installed_servers"][server_id] = {
            "installed": True,
            "enabled": True
        }

        self.save_config(list(config.get("enabled_servers", {}).keys()))

        console.print(f"[green]✓ Enabled {self.MCP_SERVERS[server_id]['name']}[/green]")

    def disable_mcp(self, server_id: str):
        """Disable an MCP server"""
        config = self.load_config()

        if "installed_servers" in config:
            config["installed_servers"][server_id]["enabled"] = False

        self.save_config(list(config.get("enabled_servers", {}).keys()))

        console.print(f"[yellow]⚠️  Disabled {self.MCP_SERVERS[server_id]['name']}[/yellow]")


def run_mcp_setup():
    """Run MCP auto-setup"""
    setup = MCPAutoSetup()

    # Detect needs
    detected_needs = setup.detect_user_needs()

    # Show recommendations
    setup.show_mcp_recommendations(detected_needs)

    # Prompt for action
    console.print()
    action = Prompt.ask(
        "What would you like to do?",
        choices=["install", "configure", "skip"],
        default="skip"
    )

    if action == "install":
        setup.interactive_mcp_setup()

    elif action == "configure":
        # Load existing config
        config = setup.load_config()
        console.print(f"[cyan]Current MCP configuration:[/cyan]")
        console.print(json.dumps(config, indent=2))

        # Ask for server to enable/disable
        server_id = Prompt.ask(
            "Enter server ID to enable/disable (or 'done'):",
            default="done"
        )

        if server_id and server_id != "done":
            if server_id in setup.MCP_SERVERS:
                if Confirm.ask(f"Enable {setup.MCP_SERVERS[server_id]['name']}?"):
                    setup.enable_mcp(server_id)
                else:
                    console.print("[dim]Skipped configuration[/dim]")

    else:
        console.print("[dim]Skipped configuration[/dim]")


if __name__ == "__main__":
    run_mcp_setup()
