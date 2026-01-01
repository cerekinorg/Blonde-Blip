"""
Configuration Migration System

Automatically migrates existing .env configuration to the new config format.
Handles backwards compatibility and creates backups.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel

console = Console()


class ConfigMigration:
    """Migrate old .env configurations to new config.json format"""

    CONFIG_DIR = Path.home() / ".blonde"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    BACKUP_DIR = CONFIG_DIR / "backups"

    def __init__(self):
        self.migration_log = []
        self.backup_created = False

    def run(self) -> bool:
        """
        Run migration process

        Returns:
            bool: True if migration occurred, False otherwise
        """
        # Check if new config already exists
        if self.CONFIG_FILE.exists():
            console.print("[dim]New config format already exists. Skipping migration.[/dim]")
            return False

        # Find and migrate .env files
        env_files = self.find_env_files()

        if not env_files:
            console.print("[dim]No .env files found to migrate.[/dim]")
            return False

        console.print("[cyan]📦 Found existing configuration. Migrating...[/cyan]")
        console.print()

        # Create backup
        self.create_backup()

        # Migrate from each .env file
        for env_file in env_files:
            self.migrate_env_file(env_file)

        # Save new config
        self.save_config()

        # Show migration summary
        self.show_summary()

        return True

    def find_env_files(self) -> list[Path]:
        """Find all .env files in common locations"""
        locations = []

        # Current directory
        cwd_env = Path.cwd() / ".env"
        if cwd_env.exists():
            locations.append(cwd_env)

        # Home directory
        home_env = Path.home() / ".env"
        if home_env.exists():
            locations.append(home_env)

        # Blonde config directory
        blonde_env = self.CONFIG_DIR / ".env"
        if blonde_env.exists():
            locations.append(blonde_env)

        return locations

    def create_backup(self):
        """Create backup of all configuration files"""
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.BACKUP_DIR / f"migration_{timestamp}"

        backup_path.mkdir(exist_ok=True)

        # Backup .env files
        for env_file in self.find_env_files():
            shutil.copy2(env_file, backup_path / env_file.name)

        self.backup_created = True
        self.migration_log.append(f"✓ Created backup at {backup_path}")

    def migrate_env_file(self, env_file: Path):
        """Migrate a single .env file"""
        console.print(f"[dim]Migrating: {env_file}[/dim]")

        # Read .env file
        env_vars = self.read_env_file(env_file)

        if not env_vars:
            self.migration_log.append(f"⚠️  {env_file}: Empty or invalid")
            return

        # Map env vars to config structure
        config = self.env_to_config(env_vars)

        if config:
            self.migration_log.append(f"✓ Migrated {env_file}")

    def read_env_file(self, env_file: Path) -> dict[str, str]:
        """Read .env file and return key-value pairs"""
        env_vars = {}

        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue

                    # Parse key=value
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()

        except Exception as e:
            console.print(f"[red]⚠️  Error reading {env_file}: {e}[/red]")

        return env_vars

    def env_to_config(self, env_vars: dict[str, str]) -> Optional[Dict[str, Any]]:
        """Convert .env vars to new config format"""
        config = {
            "providers": {}
        }

        # Detect provider from API keys
        if "OPENROUTER_API_KEY" in env_vars:
            config["providers"]["openrouter"] = {
                "api_key": env_vars["OPENROUTER_API_KEY"],
                "configured": True,
                "model": env_vars.get("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")
            }
            config["default_provider"] = "openrouter"

        if "OPENAI_API_KEY" in env_vars:
            config["providers"]["openai"] = {
                "api_key": env_vars["OPENAI_API_KEY"],
                "configured": True,
                "model": env_vars.get("OPENAI_MODEL", "gpt-4")
            }

            if "default_provider" not in config:
                config["default_provider"] = "openai"

        if "ANTHROPIC_API_KEY" in env_vars:
            config["providers"]["anthropic"] = {
                "api_key": env_vars["ANTHROPIC_API_KEY"],
                "configured": True,
                "model": env_vars.get("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
            }

            if "default_provider" not in config:
                config["default_provider"] = "anthropic"

        # Store other env vars in preferences
        config["env_vars"] = {
            k: v for k, v in env_vars.items()
            if k not in ["OPENROUTER_API_KEY", "OPENROUTER_MODEL",
                          "OPENAI_API_KEY", "OPENAI_MODEL",
                          "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL"]
        }

        return config if config["providers"] else None

    def save_config(self):
        """Save migrated configuration"""
        # Combine all migrations into final config
        config = {
            "version": "1.0.0",
            "setup_completed": True,
            "migrated_from": ".env",
            "migration_date": datetime.now().isoformat(),
            "default_provider": "openrouter",  # Will be updated
            "providers": {},
            "preferences": {
                "privacy_mode": "balanced",
                "show_tips": True,
                "stream_responses": True,
                "show_blip": True
            }
        }

        # Read all .env files and merge
        for env_file in self.find_env_files():
            env_vars = self.read_env_file(env_file)
            migrated = self.env_to_config(env_vars)

            if migrated:
                # Merge providers
                for provider, provider_config in migrated["providers"].items():
                    config["providers"][provider] = provider_config

                # Set default provider if needed
                if "default_provider" in migrated:
                    config["default_provider"] = migrated["default_provider"]

        # Create config directory
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Save config
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

        self.migration_log.append(f"✓ Saved config to {self.CONFIG_FILE}")

    def show_summary(self):
        """Show migration summary"""
        console.print()
        console.print("[bold cyan]Migration Summary[/bold cyan]")
        console.print()

        for log in self.migration_log:
            console.print(log)

        console.print()

        if self.backup_created:
            console.print("[yellow]💡 Old configurations backed up to:[/yellow]")
            console.print(f"  {self.BACKUP_DIR}")
            console.print()

        console.print("[green]✓ Migration complete![/green]")
        console.print()
        console.print("[dim]You can now use the new configuration format.[/dim]")
        console.print("[dim]Your old .env files are still there for compatibility.[/dim]")


def run_migration(force: bool = False) -> bool:
    """
    Run configuration migration

    Args:
        force: Force migration even if config exists

    Returns:
        bool: True if migration occurred
    """
    migrator = ConfigMigration()

    # Check if migration is needed
    if not force and migrator.CONFIG_FILE.exists():
        return False

    # Run migration
    panel = Panel(
        """[cyan]🔄 Configuration Migration[/cyan]

Blonde CLI is updating its configuration format.
Your existing settings will be preserved.

[dim]Press Enter to continue, or Ctrl+C to cancel[/dim]""",
        title="[bold]Blonde CLI[/bold]",
        border_style="cyan"
    )

    console.print(panel)
    input()

    return migrator.run()


def check_migration_needed() -> bool:
    """Check if configuration migration is needed"""
    CONFIG_FILE = Path.home() / ".blonde" / "config.json"

    # If config exists, migration is done
    if CONFIG_FILE.exists():
        return False

    # Check for .env files
    cwd_env = Path.cwd() / ".env"
    home_env = Path.home() / ".env"

    return cwd_env.exists() or home_env.exists()


if __name__ == "__main__":
    if check_migration_needed():
        run_migration()
    else:
        console.print("[green]✓ Configuration is up to date![/green]")
