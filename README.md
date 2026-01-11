# termshot

Capture CLI tool output as PNG screenshots.

## Features

- Run any CLI command in a pseudo-terminal (PTY)
- Preserve ANSI colors and formatting
- Render terminal output as PNG images
- Customizable themes and dimensions
- Support for interactive tools (with timeout)

## Installation

```bash
pip install termshot
```

Or install from source:

```bash
pip install -e .
```

## Quick Start

```python
from termshot import capture

# Simple one-liner
capture("ls -la --color", "screenshot.png")
```

## Advanced Usage

```python
from termshot import Screenshotter

# Create a screenshotter with custom settings
shot = Screenshotter(
    rows=30,
    cols=120,
    theme="dracula",
    font_size=16
)

# Run a command
shot.run("htop", timeout=2.0)

# Save as PNG
shot.save("htop.png")

# Or get the PIL Image object
img = shot.to_image()
```

## CLI Usage

```bash
# Capture a command
termshot "ls -la --color" -o screenshot.png

# With custom dimensions
termshot "htop" -o htop.png --rows 30 --cols 120 --timeout 2
```

## Available Themes

- `default` - Classic dark terminal
- `dracula` - Dracula color scheme
- `monokai` - Monokai color scheme
- `nord` - Nord color scheme

## License

MIT
