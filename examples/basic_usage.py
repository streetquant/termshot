#!/usr/bin/env python3
"""
Basic usage examples for termshot.
"""

from termshot import Screenshotter, capture

# Example 1: Simple one-liner
# Captures "ls -la" with colors and saves to PNG
capture("ls -la --color=always", "output/ls_example.png")
print("Saved: output/ls_example.png")

# Example 2: Using the Screenshotter class
shot = Screenshotter(
    rows=30,
    cols=100,
    theme="dracula",
    font_size=14,
)
shot.run("echo -e '\\033[1;32mHello\\033[0m \\033[1;34mWorld\\033[0m!'")
shot.save("output/hello_world.png")
print("Saved: output/hello_world.png")

# Example 3: Capture with different themes
for theme_name in ["default", "dracula", "monokai", "nord"]:
    shot = Screenshotter(rows=10, cols=60, theme=theme_name)
    shot.run("echo -e '\\033[31mRed\\033[0m \\033[32mGreen\\033[0m \\033[34mBlue\\033[0m'")
    shot.save(f"output/theme_{theme_name}.png")
    print(f"Saved: output/theme_{theme_name}.png")

# Example 4: Interactive tool with timeout
# This captures htop running for 2 seconds
capture(
    "htop",
    "output/htop_example.png",
    timeout=2.0,
    rows=30,
    cols=120,
    theme="monokai",
)
print("Saved: output/htop_example.png")

# Example 5: Without window chrome
shot = Screenshotter(rows=10, cols=60, show_window_chrome=False)
shot.run("ls --color=always")
shot.save("output/no_chrome.png")
print("Saved: output/no_chrome.png")

# Example 6: Get the PIL Image object for further processing
shot = Screenshotter()
shot.run("date")
img = shot.to_image()
print(f"Image size: {img.size}")
# You can manipulate the image further with PIL
img.save("output/date.png")
print("Saved: output/date.png")

print("\nAll examples completed!")
