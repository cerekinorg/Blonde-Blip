"""
Unified Provider Management System
Handles switching between different AI providers seamlessly
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

console = Console()


@dataclass
class ProviderConfig:
    """Configuration for an AI provider"""
    name: str
    provider_type: str  # openrouter, openai, anthropic, local
    api_key: str = ""
    model: str = ""
    api_url: str = ""
    enabled: bool = True
    priority: int = 0
    metadata: Dict[str, Any] = None


class ProviderManager:
    """Manages AI provider configurations and switching"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (Path.home() / ".blonde" / "providers.json")
        self.providers: Dict[str, ProviderConfig] = {}
        self.current_provider: Optional[str] = None
        
        self._load_config()
        self._register_default_providers()
    
    def _load_config(self):
        """Load provider configurations from disk"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                
                for name, config_data in data.get('providers', {}).items():
                    self.providers[name] = ProviderConfig(**config_data)
                
                self.current_provider = data.get('current_provider')
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load provider config: {e}[/yellow]")
    
    def _save_config(self):
        """Save provider configurations to disk"""
        config_data = {
            'providers': {name: asdict(config) for name, config in self.providers.items()},
            'current_provider': self.current_provider
        }
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def _register_default_providers(self):
        """Register default providers from environment variables"""
        # OpenRouter
        if os.getenv("OPENROUTER_API_KEY") and "openrouter" not in self.providers:
            self.providers["openrouter"] = ProviderConfig(
                name="openrouter",
                provider_type="openrouter",
                api_key=os.getenv("OPENROUTER_API_KEY", ""),
                model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
                api_url=os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions"),
                priority=1
            )
        
        # OpenAI
        if os.getenv("OPENAI_API_KEY") and "openai" not in self.providers:
            self.providers["openai"] = ProviderConfig(
                name="openai",
                provider_type="openai",
                api_key=os.getenv("OPENAI_API_KEY", ""),
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                api_url="https://api.openai.com/v1/chat/completions",
                priority=2
            )
        
        # Anthropic
        if os.getenv("ANTHROPIC_API_KEY") and "anthropic" not in self.providers:
            self.providers["anthropic"] = ProviderConfig(
                name="anthropic",
                provider_type="anthropic",
                api_key=os.getenv("ANTHROPIC_API_KEY", ""),
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
                api_url="https://api.anthropic.com/v1/messages",
                priority=3
            )
        
        # Local GGUF
        self.providers["local"] = ProviderConfig(
            name="local",
            provider_type="local",
            model=os.getenv("LOCAL_MODEL_REPO", "TheBloke/CodeLlama-7B-GGUF"),
            metadata={
                "model_file": os.getenv("LOCAL_MODEL_FILE", "codellama-7b.Q4_K_M.gguf"),
                "cached_path": None
            },
            priority=4
        )
        
        # Set default provider if none selected
        if not self.current_provider and self.providers:
            self.current_provider = self._get_best_provider()
    
    def _get_best_provider(self) -> Optional[str]:
        """Get the best available provider based on priority and availability"""
        available = [(name, p) for name, p in self.providers.items() 
                     if p.enabled and (p.api_key or p.provider_type == "local")]
        
        if not available:
            return None
        
        # Sort by priority (lower is better)
        available.sort(key=lambda x: x[1].priority)
        return available[0][0]
    
    def list_providers(self) -> Table:
        """List all configured providers"""
        table = Table(title="Configured Providers")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Model", style="yellow")
        table.add_column("Priority", style="magenta")
        table.add_column("Status", style="bold")
        
        for name, provider in self.providers.items():
            is_current = name == self.current_provider
            status = "[green]● Active[/green]" if is_current else "[dim]○ Inactive[/dim]"
            
            table.add_row(
                name,
                provider.provider_type,
                provider.model,
                str(provider.priority),
                status
            )
        
        return table
    
    def switch_provider(self, provider_name: str) -> bool:
        """Switch to a different provider"""
        if provider_name not in self.providers:
            console.print(f"[red]Provider not found: {provider_name}[/red]")
            return False
        
        provider = self.providers[provider_name]
        
        # Validate provider
        if provider.provider_type != "local" and not provider.api_key:
            console.print(f"[red]Provider '{provider_name}' has no API key configured[/red]")
            return False
        
        self.current_provider = provider_name
        self._save_config()
        
        console.print(f"[green]✓ Switched to provider: {provider_name}[/green]")
        console.print(f"[dim]Model: {provider.model}[/dim]")
        
        return True
    
    def add_provider(self, config: ProviderConfig) -> bool:
        """Add a new provider"""
        try:
            self.providers[config.name] = config
            self._save_config()
            console.print(f"[green]✓ Added provider: {config.name}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to add provider: {e}[/red]")
            return False
    
    def remove_provider(self, provider_name: str) -> bool:
        """Remove a provider"""
        if provider_name not in self.providers:
            console.print(f"[red]Provider not found: {provider_name}[/red]")
            return False
        
        if provider_name == self.current_provider:
            console.print("[red]Cannot remove the currently active provider[/red]")
            return False
        
        del self.providers[provider_name]
        self._save_config()
        
        console.print(f"[green]✓ Removed provider: {provider_name}[/green]")
        return True
    
    def get_current_provider(self) -> Optional[ProviderConfig]:
        """Get the current active provider"""
        if self.current_provider:
            return self.providers.get(self.current_provider)
        return None
    
    def get_adapter(self):
        """Get the adapter instance for the current provider"""
        provider = self.get_current_provider()
        
        if not provider:
            console.print("[red]No provider configured[/red]")
            return None
        
        try:
            if provider.provider_type == "openrouter":
                from models.openrouter import OpenRouterAdapter
                adapter = OpenRouterAdapter()
                adapter.api_key = provider.api_key
                adapter.model = provider.model
                adapter.api_url = provider.api_url
                return adapter
            
            elif provider.provider_type == "openai":
                from models.openrouter import OpenRouterAdapter  # Reuse for OpenAI too
                adapter = OpenRouterAdapter()
                adapter.api_key = provider.api_key
                adapter.model = provider.model
                adapter.api_url = provider.api_url
                return adapter
            
            elif provider.provider_type == "local":
                from models.local import LocalAdapter
                metadata = provider.metadata or {}
                adapter = LocalAdapter(
                    model_name=provider.model,
                    model_file=metadata.get("model_file", "codellama-7b.Q4_K_M.gguf"),
                    cached_path=metadata.get("cached_path")
                )
                return adapter
            
            else:
                console.print(f"[red]Unknown provider type: {provider.provider_type}[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]Failed to load adapter: {e}[/red]")
            return None
    
    def test_provider(self, provider_name: str) -> bool:
        """Test if a provider is working"""
        if provider_name not in self.providers:
            console.print(f"[red]Provider not found: {provider_name}[/red]")
            return False
        
        original_current = self.current_provider
        self.current_provider = provider_name
        
        adapter = self.get_adapter()
        
        if not adapter:
            self.current_provider = original_current
            return False
        
        console.print(f"[cyan]Testing provider: {provider_name}...[/cyan]")
        
        try:
            response = adapter.chat("Hello! This is a test message. Please respond with 'OK'.")
            if response and "OK" in response:
                console.print(f"[green]✓ Provider {provider_name} is working![/green]")
                self.current_provider = original_current
                return True
            else:
                console.print(f"[yellow]⚠ Provider {provider_name} responded but unexpectedly[/yellow]")
                self.current_provider = original_current
                return False
        except Exception as e:
            console.print(f"[red]✗ Provider {provider_name} test failed: {e}[/red]")
            self.current_provider = original_current
            return False
    
    def auto_select_provider(self) -> bool:
        """Automatically select the best available provider"""
        best = self._get_best_provider()
        
        if best:
            return self.switch_provider(best)
        else:
            console.print("[red]No available providers found[/red]")
            return False


def interactive_provider_setup():
    """Interactive provider setup wizard"""
    console.print("\n[bold cyan]🔧 Provider Setup Wizard[/bold cyan]\n")
    
    manager = ProviderManager()
    
    while True:
        console.print(manager.list_providers())
        
        action = Prompt.ask(
            "\n[cyan]What would you like to do?[/cyan]",
            choices=["switch", "add", "remove", "test", "auto", "exit"],
            default="exit"
        )
        
        if action == "exit":
            break
        
        elif action == "switch":
            provider_names = list(manager.providers.keys())
            provider_name = Prompt.ask(
                "[cyan]Select provider to activate[/cyan]",
                choices=provider_names
            )
            manager.switch_provider(provider_name)
        
        elif action == "add":
            console.print("\n[bold]Add New Provider[/bold]")
            name = Prompt.ask("[cyan]Provider name[/cyan]")
            ptype = Prompt.ask(
                "[cyan]Provider type[/cyan]",
                choices=["openrouter", "openai", "anthropic", "local"],
                default="openrouter"
            )
            
            config = ProviderConfig(name=name, provider_type=ptype)
            
            if ptype != "local":
                config.api_key = Prompt.ask("[cyan]API Key[/cyan]", password=True)
                config.model = Prompt.ask("[cyan]Model[/cyan]")
                config.api_url = Prompt.ask("[cyan]API URL[/cyan]", default="")
            else:
                config.model = Prompt.ask("[cyan]HuggingFace repo[/cyan]")
                model_file = Prompt.ask("[cyan]Model file[/cyan]")
                config.metadata = {"model_file": model_file}
            
            manager.add_provider(config)
        
        elif action == "remove":
            provider_names = list(manager.providers.keys())
            provider_name = Prompt.ask(
                "[cyan]Select provider to remove[/cyan]",
                choices=provider_names
            )
            if Confirm.ask(f"[yellow]Are you sure you want to remove {provider_name}?[/yellow]"):
                manager.remove_provider(provider_name)
        
        elif action == "test":
            provider_names = list(manager.providers.keys())
            provider_name = Prompt.ask(
                "[cyan]Select provider to test[/cyan]",
                choices=provider_names
            )
            manager.test_provider(provider_name)
        
        elif action == "auto":
            manager.auto_select_provider()
        
        console.print()


if __name__ == "__main__":
    interactive_provider_setup()
