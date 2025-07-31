"""Tests for beetune configuration management."""

import json
import os
import tempfile
from pathlib import Path
import pytest

from beetune.config import Config, AIProvider, ConfigError


class TestConfig:
    """Test configuration management functionality."""

    def setup_method(self):
        """Set up test environment with temporary config directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / ".beetune"
        self.config = Config(config_dir=self.config_dir)

    def teardown_method(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initial_config_empty(self):
        """Test that initial configuration is empty."""
        assert not self.config.is_configured()
        assert self.config.get_active_provider() is None

    def test_set_openai_provider(self):
        """Test setting OpenAI provider configuration."""
        self.config.set_provider(
            AIProvider.OPENAI,
            api_key="sk-test123",
            model="gpt-4"
        )
        
        assert self.config.is_configured()
        assert self.config.get_active_provider() == "openai"
        assert self.config.get_api_key() == "sk-test123"
        assert self.config.get_model() == "gpt-4"
        assert self.config.get_endpoint() == "https://api.openai.com/v1"

    def test_set_ollama_provider(self):
        """Test setting Ollama provider configuration."""
        self.config.set_provider(
            AIProvider.OLLAMA,
            api_key="ollama",
            endpoint="http://localhost:11434/v1",
            model="llama3.2"
        )
        
        assert self.config.is_configured()
        assert self.config.get_active_provider() == "ollama"
        assert self.config.get_api_key() == "ollama"
        assert self.config.get_model() == "llama3.2"
        assert self.config.get_endpoint() == "http://localhost:11434/v1"

    def test_set_custom_provider(self):
        """Test setting custom provider configuration."""
        self.config.set_provider(
            AIProvider.CUSTOM,
            api_key="custom-key",
            endpoint="https://my-api.example.com/v1",
            model="custom-model"
        )
        
        assert self.config.is_configured()
        assert self.config.get_active_provider() == "custom"
        assert self.config.get_api_key() == "custom-key"
        assert self.config.get_endpoint() == "https://my-api.example.com/v1"

    def test_multiple_providers(self):
        """Test configuring multiple providers."""
        # Set OpenAI first
        self.config.set_provider(AIProvider.OPENAI, "sk-openai", model="gpt-4")
        assert self.config.get_active_provider() == "openai"
        
        # Set Ollama second (should become active)
        self.config.set_provider(
            AIProvider.OLLAMA, 
            "ollama", 
            endpoint="http://localhost:11434/v1",
            model="llama3.2"
        )
        assert self.config.get_active_provider() == "ollama"
        
        # List all providers
        providers = self.config.list_providers()
        assert "openai" in providers
        assert "ollama" in providers
        assert len(providers) == 2

    def test_get_provider_config_specific(self):
        """Test getting configuration for specific provider."""
        self.config.set_provider(AIProvider.OPENAI, "sk-openai", model="gpt-4")
        self.config.set_provider(AIProvider.OLLAMA, "ollama", endpoint="http://localhost:11434/v1")
        
        # Get OpenAI config specifically
        openai_config = self.config.get_provider_config("openai")
        assert openai_config["api_key"] == "sk-openai"
        assert openai_config["model"] == "gpt-4"
        
        # Get Ollama config specifically
        ollama_config = self.config.get_provider_config("ollama")
        assert ollama_config["api_key"] == "ollama"
        assert ollama_config["endpoint"] == "http://localhost:11434/v1"

    def test_remove_provider(self):
        """Test removing provider configuration."""
        self.config.set_provider(AIProvider.OPENAI, "sk-test")
        self.config.set_provider(AIProvider.OLLAMA, "ollama", endpoint="http://localhost:11434/v1")
        
        assert len(self.config.list_providers()) == 2
        
        self.config.remove_provider("openai")
        providers = self.config.list_providers()
        assert "openai" not in providers
        assert "ollama" in providers
        assert len(providers) == 1

    def test_remove_active_provider(self):
        """Test removing the currently active provider."""
        self.config.set_provider(AIProvider.OPENAI, "sk-test")
        assert self.config.get_active_provider() == "openai"
        
        self.config.remove_provider("openai")
        assert self.config.get_active_provider() is None
        assert not self.config.is_configured()

    def test_config_persistence(self):
        """Test that configuration persists across instances."""
        # Set configuration in first instance
        self.config.set_provider(AIProvider.OPENAI, "sk-test", model="gpt-4")
        
        # Create new instance with same config directory
        new_config = Config(config_dir=self.config_dir)
        assert new_config.is_configured()
        assert new_config.get_active_provider() == "openai"
        assert new_config.get_api_key() == "sk-test"
        assert new_config.get_model() == "gpt-4"

    def test_config_file_permissions(self):
        """Test that config file has correct permissions."""
        self.config.set_provider(AIProvider.OPENAI, "sk-test")
        
        config_file = self.config_dir / "config.json"
        assert config_file.exists()
        
        # Check that file has restrictive permissions (owner read/write only)
        file_mode = oct(config_file.stat().st_mode)[-3:]
        assert file_mode == "600"

    def test_error_no_provider_configured(self):
        """Test error when no provider is configured."""
        with pytest.raises(ConfigError, match="No AI provider configured"):
            self.config.get_api_key()

    def test_error_provider_not_found(self):
        """Test error when requesting unknown provider."""
        self.config.set_provider(AIProvider.OPENAI, "sk-test")
        
        with pytest.raises(ConfigError, match="Provider 'nonexistent' is not configured"):
            self.config.get_provider_config("nonexistent")

    def test_error_no_api_key(self):
        """Test error when provider has no API key."""
        # Manually create invalid config
        self.config._config_data = {
            "openai": {"model": "gpt-4"},  # Missing api_key
            "active_provider": "openai"
        }
        
        with pytest.raises(ConfigError, match="No API key configured"):
            self.config.get_api_key()

    def test_config_file_corruption(self):
        """Test handling of corrupted config file."""
        # Create config directory and write invalid JSON
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_dir / "config.json"
        with open(config_file, 'w') as f:
            f.write("invalid json content")
        
        # Should raise ConfigError when trying to load
        with pytest.raises(ConfigError, match="Failed to load config file"):
            Config(config_dir=self.config_dir)