"""
Color themes for terminal rendering.

Provides built-in themes and a Theme dataclass for customization.
"""

from dataclasses import dataclass, field


@dataclass
class Theme:
    """Terminal color theme configuration."""
    
    name: str
    background: str  # Hex color (e.g., "#282a36")
    foreground: str  # Hex color (e.g., "#f8f8f2")
    cursor: str  # Hex color for cursor
    
    # Standard 16 ANSI colors (0-15)
    # 0-7: normal colors (black, red, green, yellow, blue, magenta, cyan, white)
    # 8-15: bright colors
    palette: list[str] = field(default_factory=list)
    
    def get_color(self, index: int) -> str:
        """Get color from palette by index."""
        if 0 <= index < len(self.palette):
            return self.palette[index]
        return self.foreground
    
    def hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


# Default dark theme
DEFAULT_THEME = Theme(
    name="default",
    background="#1e1e1e",
    foreground="#d4d4d4",
    cursor="#ffffff",
    palette=[
        # Normal colors (0-7)
        "#000000",  # Black
        "#cd3131",  # Red
        "#0dbc79",  # Green
        "#e5e510",  # Yellow
        "#2472c8",  # Blue
        "#bc3fbc",  # Magenta
        "#11a8cd",  # Cyan
        "#e5e5e5",  # White
        # Bright colors (8-15)
        "#666666",  # Bright Black
        "#f14c4c",  # Bright Red
        "#23d18b",  # Bright Green
        "#f5f543",  # Bright Yellow
        "#3b8eea",  # Bright Blue
        "#d670d6",  # Bright Magenta
        "#29b8db",  # Bright Cyan
        "#ffffff",  # Bright White
    ]
)

# Dracula theme
DRACULA_THEME = Theme(
    name="dracula",
    background="#282a36",
    foreground="#f8f8f2",
    cursor="#f8f8f2",
    palette=[
        # Normal colors (0-7)
        "#21222c",  # Black
        "#ff5555",  # Red
        "#50fa7b",  # Green
        "#f1fa8c",  # Yellow
        "#bd93f9",  # Blue
        "#ff79c6",  # Magenta
        "#8be9fd",  # Cyan
        "#f8f8f2",  # White
        # Bright colors (8-15)
        "#6272a4",  # Bright Black
        "#ff6e6e",  # Bright Red
        "#69ff94",  # Bright Green
        "#ffffa5",  # Bright Yellow
        "#d6acff",  # Bright Blue
        "#ff92df",  # Bright Magenta
        "#a4ffff",  # Bright Cyan
        "#ffffff",  # Bright White
    ]
)

# Monokai theme
MONOKAI_THEME = Theme(
    name="monokai",
    background="#272822",
    foreground="#f8f8f2",
    cursor="#f8f8f0",
    palette=[
        # Normal colors (0-7)
        "#272822",  # Black
        "#f92672",  # Red
        "#a6e22e",  # Green
        "#f4bf75",  # Yellow
        "#66d9ef",  # Blue
        "#ae81ff",  # Magenta
        "#a1efe4",  # Cyan
        "#f8f8f2",  # White
        # Bright colors (8-15)
        "#75715e",  # Bright Black
        "#f92672",  # Bright Red
        "#a6e22e",  # Bright Green
        "#f4bf75",  # Bright Yellow
        "#66d9ef",  # Bright Blue
        "#ae81ff",  # Bright Magenta
        "#a1efe4",  # Bright Cyan
        "#f9f8f5",  # Bright White
    ]
)

# Nord theme
NORD_THEME = Theme(
    name="nord",
    background="#2e3440",
    foreground="#d8dee9",
    cursor="#d8dee9",
    palette=[
        # Normal colors (0-7)
        "#3b4252",  # Black
        "#bf616a",  # Red
        "#a3be8c",  # Green
        "#ebcb8b",  # Yellow
        "#81a1c1",  # Blue
        "#b48ead",  # Magenta
        "#88c0d0",  # Cyan
        "#e5e9f0",  # White
        # Bright colors (8-15)
        "#4c566a",  # Bright Black
        "#bf616a",  # Bright Red
        "#a3be8c",  # Bright Green
        "#ebcb8b",  # Bright Yellow
        "#81a1c1",  # Bright Blue
        "#b48ead",  # Bright Magenta
        "#8fbcbb",  # Bright Cyan
        "#eceff4",  # Bright White
    ]
)

# Theme registry
THEMES: dict[str, Theme] = {
    "default": DEFAULT_THEME,
    "dracula": DRACULA_THEME,
    "monokai": MONOKAI_THEME,
    "nord": NORD_THEME,
}


def get_theme(name: str) -> Theme:
    """Get a theme by name, or return default if not found."""
    return THEMES.get(name.lower(), DEFAULT_THEME)
