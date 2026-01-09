"""
Blonde CLI - Configuration Manager
Simple, clean configuration handling
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import os


class ConfigManager:
    """Simple configuration manager"""

    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / ".blonde"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self._config = {}

    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self._config = json.load(f)
        return self._config

    def save(self) -> None:
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
        self.save()

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for provider"""
        return self._config.get(f"{provider}_api_key")

    def set_api_key(self, provider: str, key: str) -> None:
        """Set API key for provider"""
        self._config[f"{provider}_api_key"] = key
        self.save()

    @property
    def provider(self) -> str:
        """Get current provider"""
        return self._config.get('provider', 'openrouter')

    @provider.setter
    def provider(self, value: str) -> None:
        """Set provider"""
        self._config['provider'] = value
        self.save()

    @property
    def model(self) -> str:
        """Get current model"""
        return self._config.get('model', 'openai/gpt-4')

    @model.setter
    def model(self, value: str) -> None:
        """Set model"""
        self._config['model'] = value
        self.save()

    @property
    def blip_character(self) -> str:
        """Get Blip character"""
        return self._config.get('blip_character', 'axolotl')

    @blip_character.setter
    def blip_character(self, value: str) -> None:
        """Set Blip character"""
        self._config['blip_character'] = value
        self.save()


# Global instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
