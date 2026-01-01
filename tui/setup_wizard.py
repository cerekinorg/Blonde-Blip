"""
Setup Wizard for Blonde CLI

Interactive wizard that guides users through initial setup:
- Provider selection (default: OpenRouter)
- API key configuration
- Model selection
- Testing connection
"""

import os
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from tui.blip import blip

console = Console()


class SetupWizard:
    """Interactive setup wizard"""

    CONFIG_DIR = Path.home() / ".blonde"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    def __init__(self):
        self.config = {}
        self.providers = {
            "openrouter": {
                "name": "OpenRouter",
                "icon": "🌐",
                "description": "Access to 100+ AI models including free options",
                "url": "https://openrouter.ai/keys",
                "default_model": "openai/gpt-oss-20b:free"
            },
            "openai": {
                "name": "OpenAI",
                "icon": "🤖",
                "description": "Official GPT-4, GPT-3.5 models",
                "url": "https://platform.openai.com/api-keys",
                "default_model": "gpt-4"
            },
            "anthropic": {
                "name": "Anthropic",
                "icon": "🧠",
                "description": "Claude 3 Opus, Sonnet, Haiku models",
                "url": "https://console.anthropic.com/",
                "default_model": "claude-3-sonnet-20240229"
            },
            "cerekin": {
                "name": "Cerekin (Coming Soon)",
                "icon": "🎯",
                "description": "Powerful free and premium models by Cerekin",
                "url": "https://cerekin.dev",
                "default_model": "cerekin-pro"
            }
        }

    def run(self):
        """Run the complete setup wizard"""
        console.clear()

        self.show_welcome()

        if self.config_file_exists():
            if not Confirm.ask("Configuration already exists. Would you like to reconfigure?", default=False):
                blip.happy("Great! Using existing configuration.")
                return

            blip.think("Let's reconfigure your setup...")

        self.select_provider()
        self.configure_provider()
        self.setup_model()
        self.test_connection()
        self.save_config()
        self.show_success()

    def config_file_exists(self) -> bool:
        """Check if config file already exists"""
        return self.CONFIG_FILE.exists()

    def show_welcome(self):
        """Show welcome screen"""
        welcome_text = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🚀 Welcome to Blonde CLI Setup!                              ║
║                                                               ║
║   Let's get you set up in 2 minutes...                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """

        console.print(welcome_text)
        console.print()

        blip.introduce()
        console.print()
        console.print("We'll configure your AI provider and get you ready to go!")
        console.print()

        if not Confirm.ask("Ready to begin?", default=True):
            console.print("[yellow]Setup cancelled. Run 'blonde' anytime to start over.[/yellow]")
            sys.exit(0)

        console.print()

    def select_provider(self):
        """Step 1: Select AI provider"""
        blip.work("Let's choose your AI provider...")

        console.print("[bold cyan]Step 1/4: Select AI Provider[/bold cyan]")
        console.print()

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Choice", width=8)
        table.add_column("Icon", width=4)
        table.add_column("Provider", width=15)
        table.add_column("Description", width=50)

        for i, (key, provider) in enumerate(self.providers.items(), 1):
            if key == "cerekin" and "Coming Soon" in provider["name"]:
                continue

            table.add_row(
                f"{i}",
                provider["icon"],
                f"[bold]{provider['name']}[/bold]",
                provider["description"]
            )

        console.print(table)
        console.print()
        console.print("[yellow]💡 Tip: OpenRouter offers free models and is a great starting point![/yellow]")
        console.print()

        while True:
            choice = Prompt.ask(
                "Select your provider [bold cyan](1-3)[/bold cyan]",
                choices=["1", "2", "3"],
                default="1"
            )

            provider_keys = list(self.providers.keys())
            provider_keys = [k for k in provider_keys if "Coming Soon" not in self.providers[k]["name"]]

            selected_key = provider_keys[int(choice) - 1]

            console.print()
            console.print(f"✓ You selected: [bold cyan]{self.providers[selected_key]['name']}[/bold cyan]")
            console.print()

            if Confirm.ask("Is this correct?", default=True):
                self.config["default_provider"] = selected_key
                blip.happy(f"Great choice! {self.providers[selected_key]['name']} is ready to go.")
                console.print()
                break

    def configure_provider(self):
        """Step 2: Configure provider (API key)"""
        blip.work("Now let's configure your provider...")

        provider_key = self.config["default_provider"]
        provider = self.providers[provider_key]

        console.print("[bold cyan]Step 2/4: Configure Provider[/bold cyan]")
        console.print()

        # Check for existing .env file
        env_file = Path.cwd() / ".env"
        existing_keys = {}

        if env_file.exists():
            console.print(f"[dim]Found existing .env file...[/dim]")
            from dotenv import load_dotenv
            load_dotenv(env_file)

            # Check for existing keys
            env_key_mapping = {
                "openrouter": "OPENROUTER_API_KEY",
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY"
            }

            env_key = env_key_mapping.get(provider_key)
            if env_key and os.getenv(env_key):
                existing_keys[provider_key] = os.getenv(env_key)

        if provider_key in existing_keys:
            console.print(f"[green]✓ Found existing API key for {provider['name']}[/green]")
            if Confirm.ask("Use existing API key?", default=True):
                self.config["api_key"] = existing_keys[provider_key]
                self.config["providers"] = {provider_key: {"api_key": existing_keys[provider_key], "configured": True}}
                console.print()
                blip.happy("Perfect! Using your existing API key.")
                console.print()
                return

        console.print(f"To use {provider['name']}, you'll need an API key.")
        console.print()
        console.print(f"🔗 Get your API key: [bold cyan]{provider['url']}[/bold cyan]")
        console.print()

        # Open browser if possible
        import webbrowser
        if Confirm.ask("Open API key page in browser?", default=True):
            try:
                webbrowser.open(provider['url'])
            except:
                pass

        console.print()
        api_key = Prompt.ask("Enter your API key", password=True)

        while len(api_key) < 10:
            console.print("[red]⚠️  API key seems too short. Please try again.[/red]")
            api_key = Prompt.ask("Enter your API key", password=True)

        self.config["api_key"] = api_key
        self.config["providers"] = {
            provider_key: {
                "api_key": api_key,
                "configured": True
            }
        }

        console.print()
        blip.happy("API key configured successfully!")
        console.print()

    def setup_model(self):
        """Step 3: Select model"""
        blip.think("Let's choose a model...")

        console.print("[bold cyan]Step 3/4: Select Model[/bold cyan]")
        console.print()

        provider_key = self.config["default_provider"]
        provider = self.providers[provider_key]

        console.print(f"Default model for {provider['name']}: [bold cyan]{provider['default_model']}[/bold cyan]")
        console.print()

        if Confirm.ask("Use default model?", default=True):
            self.config["model"] = provider["default_model"]
            self.config["providers"][provider_key]["model"] = provider["default_model"]
            console.print()
            blip.happy(f"Selected: {provider['default_model']}")
            console.print()
            return

        console.print("Available models for this provider:")
        console.print()

        if provider_key == "openrouter":
            models = [
                ("1", "openai/gpt-oss-20b:free", "Free, GPT-level quality"),
                ("2", "openai/gpt-4-turbo", "Best quality, paid"),
                ("3", "anthropic/claude-3-opus", "Excellent reasoning, paid"),
                ("4", "meta-llama/llama-3-70b-instruct", "Fast, affordable")
            ]
        elif provider_key == "openai":
            models = [
                ("1", "gpt-4", "Best quality"),
                ("2", "gpt-4-turbo", "Faster, almost as good"),
                ("3", "gpt-3.5-turbo", "Fast and affordable")
            ]
        elif provider_key == "anthropic":
            models = [
                ("1", "claude-3-opus-20240229", "Best quality"),
                ("2", "claude-3-sonnet-20240229", "Balanced"),
                ("3", "claude-3-haiku-20240307", "Fastest")
            ]
        else:
            models = []

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Choice", width=8)
        table.add_column("Model", width=30)
        table.add_column("Description", width=30)

        for choice, model, desc in models:
            table.add_row(choice, model, desc)

        console.print(table)
        console.print()

        while True:
            choice = Prompt.ask("Select a model")

            for c, model, desc in models:
                if choice == c or choice == model:
                    self.config["model"] = model
                    self.config["providers"][provider_key]["model"] = model
                    console.print()
                    blip.happy(f"Selected: {model}")
                    console.print()
                    return

            console.print("[red]Invalid choice. Please try again.[/red]")

    def test_connection(self):
        """Step 4: Test connection"""
        blip.work("Testing your connection...")

        console.print("[bold cyan]Step 4/4: Test Connection[/bold cyan]")
        console.print()

        if not Confirm.ask("Test connection now?", default=True):
            console.print()
            blip.happy("Configuration complete! You can test later.")
            console.print()
            return

        console.print("Testing connection to provider...")
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Connecting...", total=None)

            try:
                # Test with a simple request
                import requests
                provider_key = self.config["default_provider"]
                api_key = self.config["api_key"]

                if provider_key == "openrouter":
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.config["model"],
                            "messages": [{"role": "user", "content": "Hi"}],
                            "max_tokens": 5
                        },
                        timeout=10
                    )

                    if response.status_code == 200:
                        progress.update(task, description="Connected!")
                        console.print()
                        blip.success("Connection successful! 🎉")
                        console.print()
                        console.print("[green]✓ Your provider is working perfectly![/green]")
                    else:
                        raise Exception(f"HTTP {response.status_code}")

                elif provider_key == "openai":
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model=self.config["model"],
                        messages=[{"role": "user", "content": "Hi"}],
                        max_tokens=5
                    )
                    progress.update(task, description="Connected!")
                    console.print()
                    blip.success("Connection successful! 🎉")
                    console.print()

                else:
                    # For other providers, skip test for now
                    progress.update(task, description="Skipped (manual test required)")
                    console.print()
                    blip.happy("Configuration saved! Test your connection in chat.")
                    console.print()

            except Exception as e:
                progress.update(task, description="Failed")
                console.print()
                blip.error(f"Connection failed: {str(e)}")
                console.print()
                console.print("[yellow]⚠️  Connection test failed. You can:[/yellow]")
                console.print("  1. Check your API key")
                console.print("  2. Try again later")
                console.print("  3. Continue anyway and fix later")

                if not Confirm.ask("Continue with this configuration?", default=False):
                    console.print("[yellow]Setup cancelled. Run 'blonde' to try again.[/yellow]")
                    sys.exit(1)

    def save_config(self):
        """Save configuration to file"""
        blip.work("Saving your configuration...")

        console.print("[bold cyan]Saving Configuration[/bold cyan]")
        console.print()

        # Create config directory
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Build config
        config_data = {
            "version": "1.0.0",
            "setup_completed": True,
            "setup_date": str(Path.ctime(Path.cwd())),
            **self.config,
            "preferences": {
                "privacy_mode": "balanced",
                "show_tips": True,
                "stream_responses": True,
                "show_blip": True
            }
        }

        # Save config
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=2)

        console.print(f"[green]✓ Configuration saved to: {self.CONFIG_FILE}[/green]")
        console.print()

        # Also update .env file
        self.update_env_file()

        blip.happy("Configuration saved!")
        console.print()

    def update_env_file(self):
        """Update or create .env file"""
        env_file = Path.cwd() / ".env"

        provider_key = self.config["default_provider"]
        env_key_mapping = {
            "openrouter": "OPENROUTER_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY"
        }

        env_key = env_key_mapping.get(provider_key)
        if env_key:
            lines = []

            if env_file.exists():
                with open(env_file, "r") as f:
                    lines = f.readlines()

            # Update or add API key
            updated = False
            for i, line in enumerate(lines):
                if line.startswith(f"{env_key}="):
                    lines[i] = f"{env_key}={self.config['api_key']}\n"
                    updated = True

            if not updated:
                lines.append(f"\n{env_key}={self.config['api_key']}\n")

            with open(env_file, "w") as f:
                f.writelines(lines)

            console.print(f"[dim]✓ Updated .env file[/dim]")

    def show_success(self):
        """Show success message"""
        console.clear()

        success_text = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🎉 Setup Complete!                                          ║
║                                                               ║
║   Blonde CLI is ready to use!                                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """

        console.print(success_text)
        console.print()

        provider = self.providers[self.config["default_provider"]]
        console.print(f"[bold cyan]Provider:[/bold cyan] {provider['name']} {provider['icon']}")
        console.print(f"[bold cyan]Model:[/bold cyan] {self.config['model']}")
        console.print()

        blip.excitied("You're all set! Let's start coding! 🚀")
        console.print()

        console.print("[bold cyan]Quick Start:[/bold cyan]")
        console.print()
        console.print("  [dim]# Start interactive chat[/dim]")
        console.print("  [bold cyan]blonde chat[/bold cyan]")
        console.print()
        console.print("  [dim]# Generate code[/dim]")
        console.print("  [bold cyan]blonde gen 'create a REST API'[/bold cyan]")
        console.print()
        console.print("  [dim]# Or just run:[/dim]")
        console.print("  [bold cyan]blonde[/bold cyan]")
        console.print()

        console.print("[dim]For more information, run: blonde --help[/dim]")
        console.print()


def run_wizard():
    """Run setup wizard"""
    wizard = SetupWizard()
    wizard.run()


if __name__ == "__main__":
    run_wizard()
