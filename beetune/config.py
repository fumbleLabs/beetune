"""
Configuration management for beetune.

Handles storing and retrieving API keys, endpoints, and other user settings.
"""

import json
import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from .utils import BeetuneError


class AIProvider(Enum):
    """Supported AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class ConfigError(BeetuneError):
    """Configuration-related errors."""

    pass


class Config:
    """Configuration manager for beetune."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_dir: Custom config directory. Defaults to ~/.beetune
        """
        self.config_dir = config_dir or Path.home() / ".beetune"
        self.config_file = self.config_dir / "config.json"
        self._config_data: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self._config_data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                raise ConfigError(f"Failed to load config file: {e}")
        else:
            self._config_data = {}

    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(self._config_data, f, indent=2)
            # Set restrictive permissions for security
            os.chmod(self.config_file, 0o600)
        except IOError as e:
            raise ConfigError(f"Failed to save config file: {e}")

    def set_provider(
        self,
        provider: AIProvider,
        api_key: str,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        """Set AI provider configuration.

        Args:
            provider: The AI provider
            api_key: API key for the provider
            endpoint: Custom endpoint URL (for ollama/custom providers)
            model: Default model to use
        """
        provider_config = {"api_key": api_key, "model": model}

        if endpoint:
            provider_config["endpoint"] = endpoint

        # Set default endpoints for known providers
        if provider == AIProvider.OPENAI and not endpoint:
            provider_config["endpoint"] = "https://api.openai.com/v1"
        elif provider == AIProvider.ANTHROPIC and not endpoint:
            provider_config["endpoint"] = "https://api.anthropic.com"

        self._config_data[provider.value] = provider_config
        self._config_data["active_provider"] = provider.value
        self._save_config()

    def get_active_provider(self) -> Optional[str]:
        """Get the active AI provider."""
        return self._config_data.get("active_provider")

    def get_provider_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for a provider.

        Args:
            provider: Provider name. If None, uses active provider.

        Returns:
            Provider configuration dictionary

        Raises:
            ConfigError: If provider is not configured
        """
        provider_name = provider or self.get_active_provider()
        if not provider_name:
            raise ConfigError("No AI provider configured. Run 'beetune setup' first.")

        provider_config = self._config_data.get(provider_name)
        if not provider_config:
            raise ConfigError(f"Provider '{provider_name}' is not configured.")

        return provider_config  # type: ignore

    def get_api_key(self, provider: Optional[str] = None) -> str:
        """Get API key for a provider."""
        config = self.get_provider_config(provider)
        api_key = config.get("api_key")
        if not api_key:
            provider_name = provider or self.get_active_provider()
            raise ConfigError(f"No API key configured for provider '{provider_name}'.")
        return str(api_key)

    def get_endpoint(self, provider: Optional[str] = None) -> Optional[str]:
        """Get endpoint for a provider."""
        config = self.get_provider_config(provider)
        return config.get("endpoint")

    def get_model(self, provider: Optional[str] = None) -> Optional[str]:
        """Get default model for a provider."""
        config = self.get_provider_config(provider)
        return config.get("model")

    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all configured providers."""
        providers = {}
        for key, value in self._config_data.items():
            if key != "active_provider" and isinstance(value, dict):
                providers[key] = value
        return providers

    def remove_provider(self, provider: str) -> None:
        """Remove a provider configuration."""
        if provider in self._config_data:
            del self._config_data[provider]
            # If this was the active provider, clear it
            if self._config_data.get("active_provider") == provider:
                self._config_data.pop("active_provider", None)
            self._save_config()

    def is_configured(self) -> bool:
        """Check if any provider is configured."""
        return bool(self.get_active_provider())


# Global config instance
_config = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config() -> None:
    """Reset the global configuration instance (mainly for testing)."""
    global _config
    _config = None
