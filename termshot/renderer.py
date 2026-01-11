"""
PNG Renderer - Render terminal buffer as PNG images.

This module uses Pillow to render the terminal buffer to an image.
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from termshot.themes import Theme, DEFAULT_THEME

if TYPE_CHECKING:
    from termshot.emulator import Cell


class TerminalRenderer:
    """Render terminal buffer to PNG images."""
    
    def __init__(
        self,
        theme: Theme | None = None,
        font_size: int = 14,
        padding: int = 20,
        line_height: float = 1.2,
        show_window_chrome: bool = True,
    ):
        """
        Initialize the renderer.
        
        Args:
            theme: Color theme to use
            font_size: Font size in pixels
            padding: Padding around the terminal content
            line_height: Line height multiplier
            show_window_chrome: Whether to show window title bar and buttons
        """
        self.theme = theme or DEFAULT_THEME
        self.font_size = font_size
        self.padding = padding
        self.line_height = line_height
        self.show_window_chrome = show_window_chrome
        
        # Load fonts
        self._font = self._load_font(font_size)
        self._bold_font = self._load_font(font_size, bold=True)
        
        # Calculate character dimensions
        self._char_width, self._char_height = self._calculate_char_size()
    
    def _load_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Load a monospace font."""
        # Try to find a good monospace font
        font_paths = [
            # Common Linux paths
            "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf" if bold else "",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "",
            # JetBrains Mono (popular coding font)
            "/usr/share/fonts/TTF/JetBrainsMonoNL-Regular.ttf",
            "/usr/share/fonts/TTF/JetBrainsMonoNL-Bold.ttf" if bold else "",
            # Liberation Mono
            "/usr/share/fonts/TTF/LiberationMono-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            # macOS paths
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/Monaco.dfont",
            # Windows paths
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/consolab.ttf" if bold else "",
        ]
        
        for path in font_paths:
            if path and os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
        
        # Fallback to default font
        try:
            return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()
    
    def _calculate_char_size(self) -> tuple[int, int]:
        """Calculate the width and height of a character."""
        # Create a temporary image to measure text
        img = Image.new("RGB", (100, 100))
        draw = ImageDraw.Draw(img)
        
        # Measure a sample character
        bbox = draw.textbbox((0, 0), "M", font=self._font)
        char_width = bbox[2] - bbox[0]
        char_height = int((bbox[3] - bbox[1]) * self.line_height)
        
        # Ensure minimum dimensions
        char_width = max(char_width, 8)
        char_height = max(char_height, 16)
        
        return char_width, char_height
    
    def _get_color_rgb(self, color: str | int, is_foreground: bool = True) -> tuple[int, int, int]:
        """
        Convert a color value to RGB tuple.
        
        Args:
            color: Color as string (hex/name) or int (palette index)
            is_foreground: Whether this is a foreground color
        
        Returns:
            RGB tuple
        """
        # Default colors
        if color == "default":
            hex_color = self.theme.foreground if is_foreground else self.theme.background
            return self.theme.hex_to_rgb(hex_color)
        
        # Palette index
        if isinstance(color, int):
            if 0 <= color < 16:
                # Standard 16 colors
                hex_color = self.theme.get_color(color)
            elif 16 <= color < 232:
                # 216 color cube (16-231)
                color -= 16
                r = (color // 36) % 6
                g = (color // 6) % 6
                b = color % 6
                # Convert to 0-255
                r = 0 if r == 0 else 55 + r * 40
                g = 0 if g == 0 else 55 + g * 40
                b = 0 if b == 0 else 55 + b * 40
                return (r, g, b)
            elif 232 <= color < 256:
                # Grayscale (232-255)
                gray = 8 + (color - 232) * 10
                return (gray, gray, gray)
            else:
                hex_color = self.theme.foreground if is_foreground else self.theme.background
            return self.theme.hex_to_rgb(hex_color)
        
        # Hex color
        if isinstance(color, str):
            if color.startswith("#"):
                return self.theme.hex_to_rgb(color)
            # Try to parse as a color name
            return self.theme.hex_to_rgb(self.theme.foreground if is_foreground else self.theme.background)
        
        # Fallback
        return self.theme.hex_to_rgb(self.theme.foreground if is_foreground else self.theme.background)
    
    def _draw_window_chrome(self, draw: ImageDraw.ImageDraw, width: int) -> int:
        """
        Draw window title bar with buttons.
        
        Args:
            draw: ImageDraw object
            width: Image width
        
        Returns:
            Height of the chrome
        """
        chrome_height = 36
        button_radius = 6
        button_spacing = 20
        button_y = chrome_height // 2
        
        # Draw title bar background (slightly lighter than terminal bg)
        bg_rgb = self.theme.hex_to_rgb(self.theme.background)
        title_bar_color = tuple(min(255, c + 30) for c in bg_rgb)
        draw.rectangle([(0, 0), (width, chrome_height)], fill=title_bar_color)
        
        # Draw window buttons (macOS style)
        button_colors = [
            "#ff5f56",  # Close (red)
            "#ffbd2e",  # Minimize (yellow)
            "#27c93f",  # Maximize (green)
        ]
        
        for i, color in enumerate(button_colors):
            x = self.padding + i * button_spacing
            draw.ellipse(
                [(x - button_radius, button_y - button_radius),
                 (x + button_radius, button_y + button_radius)],
                fill=color
            )
        
        return chrome_height
    
    def render(self, buffer: list[list["Cell"]]) -> Image.Image:
        """
        Render terminal buffer to a PIL Image.
        
        Args:
            buffer: 2D list of Cell objects from TerminalEmulator
        
        Returns:
            PIL Image object
        """
        if not buffer or not buffer[0]:
            # Empty buffer, return minimal image
            return Image.new("RGB", (100, 100), self.theme.hex_to_rgb(self.theme.background))
        
        rows = len(buffer)
        cols = len(buffer[0])
        
        # Calculate image dimensions
        content_width = cols * self._char_width
        content_height = rows * self._char_height
        
        chrome_height = 36 if self.show_window_chrome else 0
        
        img_width = content_width + 2 * self.padding
        img_height = content_height + 2 * self.padding + chrome_height
        
        # Create image
        bg_color = self.theme.hex_to_rgb(self.theme.background)
        img = Image.new("RGB", (img_width, img_height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw window chrome
        if self.show_window_chrome:
            self._draw_window_chrome(draw, img_width)
        
        # Draw characters
        y_offset = self.padding + chrome_height
        
        for row_idx, row in enumerate(buffer):
            x_offset = self.padding
            y = y_offset + row_idx * self._char_height
            
            for col_idx, cell in enumerate(row):
                x = x_offset + col_idx * self._char_width
                
                # Get colors
                fg_color = self._get_color_rgb(cell.fg, is_foreground=True)
                bg_color = self._get_color_rgb(cell.bg, is_foreground=False)
                
                # Handle reverse video
                if cell.reverse:
                    fg_color, bg_color = bg_color, fg_color
                
                # Draw background if not default
                if cell.bg != "default" or cell.reverse:
                    draw.rectangle(
                        [(x, y), (x + self._char_width, y + self._char_height)],
                        fill=bg_color
                    )
                
                # Draw character
                if cell.char and cell.char != " ":
                    font = self._bold_font if cell.bold else self._font
                    draw.text((x, y), cell.char, font=font, fill=fg_color)
                
                # Draw underline
                if cell.underline:
                    underline_y = y + self._char_height - 2
                    draw.line(
                        [(x, underline_y), (x + self._char_width, underline_y)],
                        fill=fg_color,
                        width=1
                    )
                
                # Draw strikethrough
                if cell.strikethrough:
                    strike_y = y + self._char_height // 2
                    draw.line(
                        [(x, strike_y), (x + self._char_width, strike_y)],
                        fill=fg_color,
                        width=1
                    )
        
        return img
    
    def save(self, buffer: list[list["Cell"]], path: str | Path) -> None:
        """
        Render terminal buffer and save as PNG.
        
        Args:
            buffer: 2D list of Cell objects
            path: Output file path
        """
        img = self.render(buffer)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path, "PNG")
