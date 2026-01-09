"""
Blonde CLI - Provider Manager
Simple provider switching and management
"""

from typing import Dict, Any, Optional
from .config import get_config_manager


class ProviderManager:
    """Simplified provider manager"""

    def __init__(self):
        self.config = get_config_manager()
        self._adapters: Dict[str, Any] = {}
        self._current_adapter = None

    def get_adapter(self, provider: str = None):
        """Get LLM adapter for provider"""
        provider = provider or self.config.provider

        if provider not in self._adapters:
            self._adapters[provider] = self._load_adapter(provider)

        return self._adapters[provider]

    def _load_adapter(self, provider: str):
        """Load adapter for provider"""
        if provider == "local":
            from models.local import LocalAdapter
            return LocalAdapter()
        elif provider == "openai":
            from models.openai import OpenAIAdapter
            return OpenAIAdapter()
        elif provider == "openrouter":
            from models.openrouter import OpenRouterAdapter
            api_key = self.config.get_api_key('openrouter')
            return OpenRouterAdapter(api_key=api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def switch_provider(self, provider: str) -> bool:
        """Switch to different provider"""
        try:
            self.config.provider = provider
            self._current_adapter = self.get_adapter(provider)
            return True
        except Exception as e:
            print(f"Failed to switch provider: {e}")
            return False

    def test_provider(self, provider: str) -> bool:
        """Test if provider is working"""
        try:
            adapter = self.get_adapter(provider)
            adapter.chat("Hello!")
            return True
        except Exception:
            return False

    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all available providers"""
        return {
            'local': {'name': 'Local (GGUF)', 'privacy': '⭐⭐⭐⭐⭐', 'cost': 'Free'},
            'openrouter': {'name': 'OpenRouter', 'privacy': '⭐⭐', 'cost': 'Per API call'},
            'openai': {'name': 'OpenAI', 'privacy': '⭐⭐', 'cost': 'Per API call'},
            'anthropic': {'name': 'Anthropic (Claude)', 'privacy': '⭐⭐⭐', 'cost': 'Per API call'}
        }

    def current_provider(self) -> str:
        """Get current provider"""
        return self.config.provider

    def current_model(self) -> str:
        """Get current model"""
        return self.config.model

    def set_model(self, model: str) -> None:
        """Set model for current provider"""
        self.config.model = model


# Global instance
_provider_manager = None


def get_provider_manager() -> ProviderManager:
    """Get global provider manager instance"""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager()
    return _provider_manager
