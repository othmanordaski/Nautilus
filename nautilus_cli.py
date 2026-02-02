"""
Nautilus CLI Entry Point
Command-line interface entry point for the Nautilus streaming application.
"""
import sys
from app import main

def cli_main():
    """Entry point for the nautilus command."""
    sys.exit(main() or 0)

if __name__ == "__main__":
    cli_main()
