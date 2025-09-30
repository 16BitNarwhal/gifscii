"""
GIF to ASCII Terminal Animation Converter
Usage: python ascii.py input.gif [width]
"""

import argparse
import os
import shutil
import sys
import time
from typing import List, Tuple

try:
    from PIL import Image, ImageSequence
except ImportError:
    print("Error: PIL (Pillow) is required. Install with: pip install Pillow")
    sys.exit(1)

def image_to_ascii(image: Image.Image, max_width: int = 80, max_height: int = 24) -> str:
    """Convert a PIL Image to ASCII art."""
    # ASCII characters from darkest to lightest
    ascii_chars = "@%#*+=-:. "

    # Calculate dimensions to fit within terminal bounds
    aspect_ratio = image.width / image.height

    # Calculate width and height based on constraints
    width_by_height = int(max_height * aspect_ratio * 2)  # *2 to account for character height
    height_by_width = int(max_width / aspect_ratio * 0.5)  # *0.5 to account for character height

    if width_by_height <= max_width:
        # Height is the limiting factor
        width = width_by_height
        height = max_height
    else:
        # Width is the limiting factor
        width = max_width
        height = height_by_width

    # Resize image
    image = image.resize((width, height))

    # Convert to grayscale
    image = image.convert('L')
    
    # Convert pixels to ASCII
    ascii_art = []
    for y in range(height):
        line = ""
        for x in range(width):
            pixel = image.getpixel((x, y))
            # Map pixel value (0-255) to ASCII character
            char_index = min(len(ascii_chars) - 1, pixel * len(ascii_chars) // 256)
            line += ascii_chars[char_index]
        ascii_art.append(line)
    
    return '\n'.join(ascii_art)

def extract_gif_frames(gif_path: str) -> Tuple[List[Image.Image], List[float]]:
    """Extract all frames from a GIF with their durations."""
    try:
        with Image.open(gif_path) as img:
            frames = []
            durations = []
            
            for frame in ImageSequence.Iterator(img):
                # Convert frame to RGB (some GIFs have palette mode)
                rgb_frame = frame.convert('RGB')
                frames.append(rgb_frame)
                
                # Get frame duration (in milliseconds)
                duration = frame.info.get('duration', 100)  # Default 100ms
                durations.append(duration / 1000.0)  # Convert to seconds
            
            return frames, durations
    except Exception as e:
        print(f"Error reading GIF: {e}")
        sys.exit(1)

def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def play_ascii_animation(frames: List[Image.Image], durations: List[float], max_width: int, max_height: int, speed: float = 0.5) -> None:
    """Play ASCII animation in the terminal."""
    ascii_frames = []

    print("Converting frames to ASCII...")
    for i, frame in enumerate(frames):
        ascii_frame = image_to_ascii(frame, max_width, max_height)
        ascii_frames.append(ascii_frame)
        print(f"\rProgress: {i+1}/{len(frames)}", end='', flush=True)

    print("\nStarting animation... (Press Ctrl+C to stop)")
    time.sleep(1)

    try:
        frame_count = 0
        while True:  # Loop forever
            for i, (ascii_frame, duration) in enumerate(zip(ascii_frames, durations)):
                # Use ANSI escape sequences for smooth updates
                if frame_count == 0:
                    clear_screen()
                else:
                    # Move cursor to top-left
                    print('\033[H', end='')

                print(ascii_frame, flush=True)

                # Sleep for frame duration (minimum 0.03 seconds for readability)
                sleep_time = max(0.03, duration * speed)
                time.sleep(sleep_time)

                frame_count += 1
    
    except KeyboardInterrupt:
        print("\n\nAnimation stopped.")
        sys.exit(0)

def get_terminal_size() -> Tuple[int, int]:
    """Get the current terminal width and height."""
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except (AttributeError, OSError):
        return 80, 24  # Default fallback

def main() -> None:
    parser = argparse.ArgumentParser(description='Convert GIF to ASCII terminal animation')
    parser.add_argument('gif_file', help='Path to the GIF file')
    parser.add_argument('width', nargs='?', type=int, help='ASCII art width (default: terminal width)')
    parser.add_argument('--speed', type=float, default=0.5, help='Animation speed multiplier (default: 0.5, higher = slower)')

    args = parser.parse_args()
    
    if not os.path.exists(args.gif_file):
        print(f"Error: File '{args.gif_file}' not found.")
        sys.exit(1)

    if not args.gif_file.lower().endswith(('.gif', '.png', '.jpg', '.jpeg')):
        print("Warning: File may not be a supported image format. Continuing anyway...")
    
    # Determine dimensions
    terminal_width, terminal_height = get_terminal_size()
    max_height = terminal_height - 4  # Leave some margin for messages

    if args.width:
        if args.width <= 0:
            print("Error: Width must be a positive integer.")
            sys.exit(1)
        max_width = args.width
    else:
        max_width = min(terminal_width - 2, 120)  # Leave some margin

    print(f"Loading GIF: {args.gif_file}")
    print(f"Terminal size: {terminal_width}x{terminal_height}")
    print(f"Max ASCII dimensions: {max_width}x{max_height} characters")

    # Extract frames from GIF
    frames, durations = extract_gif_frames(args.gif_file)
    print(f"Found {len(frames)} frames")

    # Play the animation
    play_ascii_animation(frames, durations, max_width, max_height, args.speed)

if __name__ == "__main__":
    main()
