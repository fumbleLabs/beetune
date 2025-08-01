#!/usr/bin/env python3
"""
Example script demonstrating beetune setup and configuration.

This script shows how to programmatically configure beetune
without using the interactive CLI setup command.
"""

from beetune.config import AIProvider, Config


def setup_openai_example():
    """Example: Set up OpenAI configuration."""
    print("Setting up OpenAI configuration...")
    
    config = Config()
    config.set_provider(
        provider=AIProvider.OPENAI,
        api_key="your-openai-api-key-here",  # Replace with real key
        model="gpt-4o"
    )
    
    print("✅ OpenAI configured successfully!")
    print(f"Active provider: {config.get_active_provider()}")
    print(f"Endpoint: {config.get_endpoint()}")
    print(f"Model: {config.get_model()}")

def setup_ollama_example():
    """Example: Set up Ollama configuration."""
    print("\nSetting up Ollama configuration...")
    
    config = Config()
    config.set_provider(
        provider=AIProvider.OLLAMA,
        api_key="ollama",  # Ollama doesn't need a real API key
        endpoint="http://localhost:11434/v1",
        model="llama3.2"
    )
    
    print("✅ Ollama configured successfully!")
    print(f"Active provider: {config.get_active_provider()}")
    print(f"Endpoint: {config.get_endpoint()}")
    print(f"Model: {config.get_model()}")

def setup_custom_example():
    """Example: Set up custom API configuration."""
    print("\nSetting up custom API configuration...")
    
    config = Config()
    config.set_provider(
        provider=AIProvider.CUSTOM,
        api_key="your-custom-api-key",
        endpoint="https://your-api.example.com/v1",
        model="your-model-name"
    )
    
    print("✅ Custom API configured successfully!")
    print(f"Active provider: {config.get_active_provider()}")
    print(f"Endpoint: {config.get_endpoint()}")
    print(f"Model: {config.get_model()}")

def list_providers_example():
    """Example: List all configured providers."""
    print("\nListing all configured providers...")
    
    config = Config()
    providers = config.list_providers()
    active = config.get_active_provider()
    
    if not providers:
        print("No providers configured.")
        return
    
    for name, settings in providers.items():
        status = " (active)" if name == active else ""
        print(f"Provider: {name}{status}")
        print(f"  Endpoint: {settings.get('endpoint', 'default')}")
        print(f"  Model: {settings.get('model', 'default')}")

def main():
    """Run configuration examples."""
    print("🔧 beetune Configuration Examples")
    print("=" * 40)
    
    # Note: These examples use placeholder API keys
    # In real usage, you'd use actual API keys
    
    try:
        # Example 1: OpenAI setup
        setup_openai_example()
        
        # Example 2: Ollama setup  
        setup_ollama_example()
        
        # Example 3: Custom API setup
        setup_custom_example()
        
        # Example 4: List all providers
        list_providers_example()
        
    except Exception as e:
        print(f"Error during setup: {e}")

if __name__ == "__main__":
    main()