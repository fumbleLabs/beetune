"""
Entry point for running beetune as a module.
"""

import argparse

from .server import app


def main():
    """Main entry point for module execution."""
    parser = argparse.ArgumentParser(description="beetune server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
