#!/usr/bin/env python3
"""
Command-line interface for beetune.

Provides a simple CLI for common beetune operations like formatting resumes
and analyzing job descriptions.
"""

import argparse
import sys
from getpass import getpass
from pathlib import Path

from . import FileProcessor, JobAnalyzer, ResumeFormatter
from .config import AIProvider, ConfigError, get_config
from .formatters import LaTeXStyle
from .utils import BeetuneException


def format_resume_command(args):
    """Handle the format-resume command."""
    try:
        # Read input file
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file '{args.input}' not found")
            return 1
        
        # Extract text from file
        processor = FileProcessor()
        with open(input_path, 'rb') as f:
            resume_text = processor.extract_text(f, input_path.name)
        
        # Format as LaTeX
        formatter = ResumeFormatter()
        style = LaTeXStyle(args.style)
        latex_content = formatter.format_resume(resume_text, style=style)
        
        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            print(f"✅ Formatted resume saved to {args.output}")
        else:
            print(latex_content)
        
        return 0
        
    except BeetuneException as e:
        print(f"Error: {e.message}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1


def analyze_job_command(args):
    """Handle the analyze-job command."""
    try:
        # Get configuration
        config = get_config()
        if not config.is_configured():
            print("Error: No AI provider configured. Run 'beetune setup' first.")
            return 1
        
        api_key = config.get_api_key()
        endpoint = config.get_endpoint()
        model = config.get_model()
        
        # Read job description
        if args.input == '-':
            job_description = sys.stdin.read()
        else:
            with open(args.input, 'r', encoding='utf-8') as f:
                job_description = f.read()
        
        # Analyze job description
        analyzer = JobAnalyzer(api_key, base_url=endpoint, default_model=model)
        analysis = analyzer.analyze_job_description(job_description)
        
        # Output results
        print("📋 Job Analysis Results")
        print("=" * 40)
        print(f"\n🔑 Keywords:\n{analysis['keywords']}")
        print(f"\n💰 Benefits:\n{analysis['benefits']}")
        
        return 0
        
    except (BeetuneException, ConfigError) as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1


def setup_command(args):
    """Handle the setup command."""
    try:
        config = get_config()
        
        print("🔧 beetune Setup")
        print("=" * 40)
        print("Configure your AI provider settings.\n")
        
        # Show current configuration if exists
        if config.is_configured():
            active_provider = config.get_active_provider()
            providers = config.list_providers()
            print(f"Current active provider: {active_provider}")
            print(f"Configured providers: {', '.join(providers.keys())}\n")
        
        # Provider selection
        print("Available providers:")
        providers = list(AIProvider)
        for i, provider in enumerate(providers, 1):
            if provider == AIProvider.OPENAI:
                print(f"  {i}. {provider.value} - OpenAI GPT models")
            elif provider == AIProvider.ANTHROPIC:
                print(f"  {i}. {provider.value} - Claude models")
            elif provider == AIProvider.OLLAMA:
                print(f"  {i}. {provider.value} - Local Ollama server")
            elif provider == AIProvider.CUSTOM:
                print(f"  {i}. {provider.value} - Custom OpenAI-compatible API")
        
        while True:
            try:
                choice = input(f"\nSelect provider (1-{len(providers)}): ").strip()
                provider_idx = int(choice) - 1
                if 0 <= provider_idx < len(providers):
                    selected_provider = providers[provider_idx]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
        
        print(f"\nConfiguring {selected_provider.value}...")
        
        # Get API key
        if selected_provider == AIProvider.OLLAMA:
            api_key = "ollama"  # Ollama doesn't need a real API key
            print("Using 'ollama' as API key (Ollama doesn't require authentication)")
        else:
            api_key = getpass("Enter your API key: ").strip()
            if not api_key:
                print("API key is required.")
                return 1
        
        # Get endpoint
        endpoint = None
        if selected_provider == AIProvider.OLLAMA:
            endpoint = input("Enter Ollama endpoint (default: http://localhost:11434/v1): ").strip()
            if not endpoint:
                endpoint = "http://localhost:11434/v1"
        elif selected_provider == AIProvider.CUSTOM:
            endpoint = input("Enter custom API endpoint: ").strip()
            if not endpoint:
                print("Custom endpoint is required.")
                return 1
        
        # Get default model
        model = None
        if selected_provider == AIProvider.OPENAI:
            model = input("Enter default model (default: gpt-4o): ").strip()
            if not model:
                model = "gpt-4o"
        elif selected_provider == AIProvider.ANTHROPIC:
            model = input("Enter default model (default: claude-3-5-sonnet-20241022): ").strip()
            if not model:
                model = "claude-3-5-sonnet-20241022"
        elif selected_provider == AIProvider.OLLAMA:
            model = input("Enter default model (e.g., llama3.2, mistral): ").strip()
            if not model:
                print("Model name is required for Ollama.")
                return 1
        elif selected_provider == AIProvider.CUSTOM:
            model = input("Enter default model: ").strip()
        
        # Save configuration
        config.set_provider(selected_provider, api_key, endpoint, model)
        
        print(f"\n✅ Successfully configured {selected_provider.value}")
        if endpoint:
            print(f"   Endpoint: {endpoint}")
        if model:
            print(f"   Default model: {model}")
        
        # Test the configuration
        if args.test:
            print("\n🧪 Testing configuration...")
            try:
                analyzer = JobAnalyzer(api_key, base_url=endpoint, default_model=model)
                # Simple test with a minimal job description
                test_result = analyzer.analyze_job_description("Software Engineer position requiring Python skills.")
                print("✅ Configuration test successful!")
            except Exception as e:
                print(f"⚠️  Configuration test failed: {e}")
                print("You may need to check your API key and endpoint.")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        return 1
    except (ConfigError, BeetuneException) as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1


def config_command(args):
    """Handle the config command."""
    try:
        config = get_config()
        
        if args.list:
            providers = config.list_providers()
            active = config.get_active_provider()
            
            if not providers:
                print("No providers configured. Run 'beetune setup' to get started.")
                return 0
            
            print("Configured providers:")
            for name, settings in providers.items():
                status = " (active)" if name == active else ""
                endpoint = settings.get("endpoint", "default")
                model = settings.get("model", "default")
                print(f"  {name}{status}")
                print(f"    Endpoint: {endpoint}")
                print(f"    Model: {model}")
        
        elif args.remove:
            config.remove_provider(args.remove)
            print(f"✅ Removed provider '{args.remove}'")
        
        else:
            # Show current active configuration
            if not config.is_configured():
                print("No providers configured. Run 'beetune setup' to get started.")
                return 0
            
            active = config.get_active_provider()
            provider_config = config.get_provider_config()
            
            print(f"Active provider: {active}")
            print(f"Endpoint: {provider_config.get('endpoint', 'default')}")
            print(f"Model: {provider_config.get('model', 'default')}")
        
        return 0
        
    except (ConfigError, BeetuneException) as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1


def server_command(args):
    """Handle the server command."""
    try:
        # Import server module
        import sys

        from .server import main as server_main
        
        # Prepare arguments for server
        server_args = [
            '--host', args.host,
            '--port', str(args.port)
        ]
        
        if args.debug:
            server_args.append('--debug')
        
        # Temporarily replace sys.argv for server argument parsing
        original_argv = sys.argv
        sys.argv = ['beetune-server'] + server_args
        
        try:
            print(f"🚀 Starting beetune server on {args.host}:{args.port}")
            if args.debug:
                print("🐛 Debug mode enabled")
            server_main()
            return 0
        finally:
            sys.argv = original_argv
            
    except ImportError:
        print("Error: Server functionality not available.")
        print("Install with server dependencies: pip install beetune[server]")
        return 1
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="beetune - Resume analysis and formatting toolkit",
        prog="beetune"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # setup command
    setup_parser = subparsers.add_parser(
        'setup',
        help='Configure AI provider settings'
    )
    setup_parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Test the configuration after setup'
    )
    
    # config command
    config_parser = subparsers.add_parser(
        'config',
        help='Manage configuration settings'
    )
    config_parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all configured providers'
    )
    config_parser.add_argument(
        '--remove', '-r',
        help='Remove a provider configuration'
    )
    
    # format-resume command
    format_parser = subparsers.add_parser(
        'format-resume', 
        help='Format a resume as LaTeX'
    )
    format_parser.add_argument(
        'input', 
        help='Input resume file (PDF, DOCX, or TEX)'
    )
    format_parser.add_argument(
        '--output', '-o',
        help='Output LaTeX file (default: stdout)'
    )
    format_parser.add_argument(
        '--style', '-s',
        choices=['modern', 'classic', 'minimal'],
        default='modern',
        help='LaTeX style to use (default: modern)'
    )
    
    # analyze-job command
    analyze_parser = subparsers.add_parser(
        'analyze-job',
        help='Analyze a job description'
    )
    analyze_parser.add_argument(
        'input',
        help='Job description file (use "-" for stdin)'
    )
    
    # version command
    subparsers.add_parser('version', help='Show version information')
    
    # server command
    server_parser = subparsers.add_parser(
        'server',
        help='Start the web API server'
    )
    server_parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    server_parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to bind to (default: 8000)'
    )
    server_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        return setup_command(args)
    elif args.command == 'config':
        return config_command(args)
    elif args.command == 'format-resume':
        return format_resume_command(args)
    elif args.command == 'analyze-job':
        return analyze_job_command(args)
    elif args.command == 'version':
        from . import __version__
        print(f"beetune {__version__}")
        return 0
    elif args.command == 'server':
        return server_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())