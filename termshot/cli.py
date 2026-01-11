"""
CLI interface for termshot.

Provides command-line access to the screenshot functionality.
"""

import argparse
import sys
from pathlib import Path

from termshot import capture, THEMES


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="termshot",
        description="Capture CLI tool output as PNG screenshots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  termshot "ls -la --color" -o screenshot.png
  termshot "htop" -o htop.png --timeout 2
  termshot "neofetch" -o neofetch.png --theme dracula
        """,
    )
    
    parser.add_argument(
        "command",
        help="Command to run and capture",
    )
    
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output PNG file path",
    )
    
    parser.add_argument(
        "--rows",
        type=int,
        default=24,
        help="Terminal rows (default: 24)",
    )
    
    parser.add_argument(
        "--cols",
        type=int,
        default=80,
        help="Terminal columns (default: 80)",
    )
    
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Timeout in seconds (for interactive commands)",
    )
    
    parser.add_argument(
        "--theme",
        choices=list(THEMES.keys()),
        default="default",
        help="Color theme (default: default)",
    )
    
    parser.add_argument(
        "--font-size",
        type=int,
        default=14,
        help="Font size in pixels (default: 14)",
    )
    
    parser.add_argument(
        "--no-chrome",
        action="store_true",
        help="Disable window chrome (title bar, buttons)",
    )
    
    parser.add_argument(
        "--no-command",
        action="store_true",
        help="Don't show the command in the screenshot",
    )
    
    parser.add_argument(
        "--prompt",
        type=str,
        default="$ ",
        help="Prompt string to display before the command (default: '$ ')",
    )
    
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Custom title to display instead of the actual command",
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    
    args = parser.parse_args()
    
    try:
        capture(
            command=args.command,
            output=args.output,
            timeout=args.timeout,
            rows=args.rows,
            cols=args.cols,
            theme=args.theme,
            font_size=args.font_size,
            show_window_chrome=not args.no_chrome,
            show_command=not args.no_command,
            prompt=args.prompt,
            title=args.title,
        )
        print(f"Screenshot saved to: {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
