"""
Screenshotter - Main API class for capturing CLI screenshots.

This module provides the main public API for the termshot library.
"""

from pathlib import Path
from typing import Union

from PIL import Image

from termshot.runner import PTYRunner
from termshot.emulator import TerminalEmulator
from termshot.renderer import TerminalRenderer
from termshot.themes import Theme, get_theme, DEFAULT_THEME


class Screenshotter:
    """
    Main class for capturing CLI tool screenshots.
    
    Example:
        >>> shot = Screenshotter(rows=30, cols=120)
        >>> shot.run("ls -la --color")
        >>> shot.save("output.png")
    """
    
    def __init__(
        self,
        rows: int = 24,
        cols: int = 80,
        theme: str | Theme = "default",
        font_size: int = 14,
        padding: int = 20,
        show_window_chrome: bool = True,
        show_command: bool = True,
        prompt: str = "$ ",
    ):
        """
        Initialize the Screenshotter.
        
        Args:
            rows: Number of terminal rows
            cols: Number of terminal columns
            theme: Theme name (string) or Theme object
            font_size: Font size in pixels
            padding: Padding around terminal content
            show_window_chrome: Whether to show window title bar
            show_command: Whether to show the command in the screenshot
            prompt: The prompt string to display before the command
        """
        self.rows = rows
        self.cols = cols
        self.show_command = show_command
        self.prompt = prompt
        
        # Resolve theme
        if isinstance(theme, str):
            self._theme = get_theme(theme)
        else:
            self._theme = theme
        
        self.font_size = font_size
        self.padding = padding
        self.show_window_chrome = show_window_chrome
        
        # Initialize components
        self._runner = PTYRunner(rows=rows, cols=cols)
        self._emulator = TerminalEmulator(rows=rows, cols=cols)
        self._renderer = TerminalRenderer(
            theme=self._theme,
            font_size=font_size,
            padding=padding,
            show_window_chrome=show_window_chrome,
        )
        
        # State
        self._output: bytes = b""
        self._has_run = False
    
    def run(
        self,
        command: Union[str, list[str]],
        timeout: float | None = None,
        env: dict[str, str] | None = None,
        title: str | None = None,
    ) -> "Screenshotter":
        """
        Run a command and capture its output.
        
        Args:
            command: Command to run (string or list of arguments)
            timeout: Maximum time to run (seconds). Use for interactive tools.
            env: Additional environment variables
            title: Custom title to display instead of the actual command
        
        Returns:
            Self for chaining
        """
        # Run command in PTY
        self._output = self._runner.run(command, timeout=timeout, env=env)
        
        # Feed output to emulator
        self._emulator.reset()
        
        # If show_command is enabled, prepend the command prompt
        if self.show_command:
            # Use title if provided, otherwise use the actual command
            if title:
                display_text = title
            else:
                display_text = command if isinstance(command, str) else " ".join(command)
            
            prompt_line = f"{self.prompt}{display_text}\n"
            self._emulator.feed(prompt_line.encode("utf-8"))
        
        # Add carriage return to ensure output starts at column 0
        self._emulator.feed(b"\r")
        self._emulator.feed(self._output)
        
        self._has_run = True
        return self
    
    def to_image(self) -> Image.Image:
        """
        Get the screenshot as a PIL Image.
        
        Returns:
            PIL Image object
        
        Raises:
            RuntimeError: If no command has been run yet
        """
        if not self._has_run:
            raise RuntimeError("No command has been run yet. Call run() first.")
        
        buffer = self._emulator.get_buffer()
        return self._renderer.render(buffer)
    
    def save(self, path: str | Path) -> "Screenshotter":
        """
        Save the screenshot to a file.
        
        Args:
            path: Output file path (PNG)
        
        Returns:
            Self for chaining
        
        Raises:
            RuntimeError: If no command has been run yet
        """
        if not self._has_run:
            raise RuntimeError("No command has been run yet. Call run() first.")
        
        buffer = self._emulator.get_buffer()
        self._renderer.save(buffer, path)
        return self
    
    def get_raw_output(self) -> bytes:
        """Get the raw PTY output bytes."""
        return self._output
    
    def get_text_output(self) -> str:
        """Get the visible text content (without ANSI codes)."""
        if not self._has_run:
            return ""
        lines = self._emulator.get_display_lines()
        return "\n".join(lines)
    
    @property
    def theme(self) -> Theme:
        """Get the current theme."""
        return self._theme
    
    @theme.setter
    def theme(self, value: str | Theme) -> None:
        """Set the theme."""
        if isinstance(value, str):
            self._theme = get_theme(value)
        else:
            self._theme = value
        
        # Update renderer
        self._renderer = TerminalRenderer(
            theme=self._theme,
            font_size=self.font_size,
            padding=self.padding,
            show_window_chrome=self.show_window_chrome,
        )


def capture(
    command: Union[str, list[str]],
    output: str | Path,
    timeout: float | None = None,
    rows: int = 24,
    cols: int = 80,
    theme: str | Theme = "default",
    font_size: int = 14,
    show_window_chrome: bool = True,
    show_command: bool = True,
    prompt: str = "$ ",
    title: str | None = None,
    env: dict[str, str] | None = None,
) -> Image.Image:
    """
    Capture a command's output as a PNG screenshot.
    
    This is a convenience function that creates a Screenshotter,
    runs the command, and saves the output.
    
    Args:
        command: Command to run
        output: Output file path (PNG)
        timeout: Maximum execution time (seconds)
        rows: Terminal rows
        cols: Terminal columns
        theme: Theme name or Theme object
        font_size: Font size in pixels
        show_window_chrome: Whether to show window title bar
        show_command: Whether to show the command in the screenshot
        prompt: The prompt string to display before the command
        title: Custom title to display instead of the actual command
        env: Additional environment variables
    
    Returns:
        PIL Image object
    
    Example:
        >>> capture("ls -la --color", "screenshot.png")
        >>> capture("htop", "htop.png", timeout=2)
    """
    shot = Screenshotter(
        rows=rows,
        cols=cols,
        theme=theme,
        font_size=font_size,
        show_window_chrome=show_window_chrome,
        show_command=show_command,
        prompt=prompt,
    )
    shot.run(command, timeout=timeout, env=env, title=title)
    shot.save(output)
    return shot.to_image()
