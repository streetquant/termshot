"""
Terminal Emulator - Parse ANSI escape codes and maintain terminal state.

This module wraps pyte to provide terminal emulation capabilities.
"""

import pyte
from dataclasses import dataclass
from typing import Optional


@dataclass
class Cell:
    """Represents a single character cell in the terminal."""
    
    char: str
    fg: str | int  # Foreground color (name, index, or hex)
    bg: str | int  # Background color (name, index, or hex)
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    reverse: bool = False


class TerminalEmulator:
    """Terminal emulator using pyte to parse ANSI escape codes."""
    
    def __init__(self, rows: int = 24, cols: int = 80):
        """
        Initialize the terminal emulator.
        
        Args:
            rows: Number of terminal rows
            cols: Number of terminal columns
        """
        self.rows = rows
        self.cols = cols
        self.screen = pyte.Screen(cols, rows)
        self.stream = pyte.Stream(self.screen)
    
    def feed(self, data: bytes) -> None:
        """
        Feed data to the terminal emulator.
        
        Args:
            data: Raw bytes from PTY output
        """
        # Decode with error handling for invalid sequences
        try:
            text = data.decode("utf-8", errors="replace")
        except Exception:
            text = data.decode("latin-1", errors="replace")
        
        self.stream.feed(text)
    
    def get_buffer(self) -> list[list[Cell]]:
        """
        Get the terminal buffer as a 2D grid of cells.
        
        Returns:
            List of rows, each containing a list of Cell objects
        """
        buffer = []
        
        for y in range(self.rows):
            row = []
            line = self.screen.buffer[y]
            
            for x in range(self.cols):
                char_data = line[x]
                
                # Extract character
                char = char_data.data if char_data.data else " "
                
                # Extract colors
                fg = self._convert_color(char_data.fg, "default")
                bg = self._convert_color(char_data.bg, "default")
                
                # Extract attributes
                cell = Cell(
                    char=char,
                    fg=fg,
                    bg=bg,
                    bold=char_data.bold,
                    italic=char_data.italics,
                    underline=char_data.underscore,
                    strikethrough=char_data.strikethrough,
                    reverse=char_data.reverse,
                )
                row.append(cell)
            
            buffer.append(row)
        
        return buffer
    
    def _convert_color(self, color: str, default: str) -> str | int:
        """
        Convert pyte color to a usable format.
        
        Args:
            color: Color from pyte (name or hex)
            default: Default value if color is 'default'
        
        Returns:
            Color as string (name/hex) or int (palette index)
        """
        if color == "default":
            return default
        
        # Check if it's a named color (maps to palette index)
        color_map = {
            "black": 0,
            "red": 1,
            "green": 2,
            "yellow": 3,
            "brown": 3,  # Some terminals use brown for yellow
            "blue": 4,
            "magenta": 5,
            "cyan": 6,
            "white": 7,
            "brightblack": 8,
            "brightred": 9,
            "brightgreen": 10,
            "brightyellow": 11,
            "brightblue": 12,
            "brightmagenta": 13,
            "brightcyan": 14,
            "brightwhite": 15,
        }
        
        color_lower = color.lower().replace(" ", "").replace("_", "")
        if color_lower in color_map:
            return color_map[color_lower]
        
        # Check for 256-color index
        if isinstance(color, int) or (isinstance(color, str) and color.isdigit()):
            return int(color)
        
        # Return as-is (might be hex color)
        return color
    
    def reset(self) -> None:
        """Reset the terminal to initial state."""
        self.screen.reset()
    
    def get_cursor_position(self) -> tuple[int, int]:
        """Get the current cursor position (row, col)."""
        return (self.screen.cursor.y, self.screen.cursor.x)
    
    def get_display_lines(self) -> list[str]:
        """
        Get the display as a list of strings (without styling).
        
        Returns:
            List of strings, one per row
        """
        return list(self.screen.display)
