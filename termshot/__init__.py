"""
termshot - Capture CLI tool output as PNG screenshots.

This library allows you to run CLI commands in a pseudo-terminal (PTY)
and capture the visual output as PNG images, preserving ANSI colors
and formatting.
"""

from termshot.screenshotter import Screenshotter, capture
from termshot.themes import Theme, THEMES

__version__ = "0.1.0"
__all__ = ["Screenshotter", "capture", "Theme", "THEMES"]
