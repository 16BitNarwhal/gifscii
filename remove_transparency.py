"""
GIF Transparency Remover - Replace transparent backgrounds with white
Usage: python remove_transparency.py input.gif [output.gif]
"""

import argparse
import sys
from PIL import Image

def remove_transparency(input_path, output_path):
    """Remove transparency from GIF and replace with white background."""
    try:
        gif = Image.open(input_path)

        # Process each frame
        frames = []
        for frame_num in range(0, gif.n_frames):
            gif.seek(frame_num)

            # Convert RGBA to RGB with white background
            if gif.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', gif.size, (255, 255, 255))

                # Convert frame to RGBA if needed
                frame_rgba = gif.convert('RGBA')

                # Paste frame onto white background
                background.paste(frame_rgba, mask=frame_rgba.split()[-1] if frame_rgba.mode == 'RGBA' else None)
                frames.append(background)
            else:
                frames.append(gif.convert('RGB'))

        # Save as new GIF
        frames[0].save(output_path, save_all=True, append_images=frames[1:],
                       duration=gif.info.get('duration', 100), loop=gif.info.get('loop', 0))

        print(f"Success! Saved to {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Remove transparency from GIF and replace with white')
    parser.add_argument('input', help='Input GIF file')
    parser.add_argument('output', nargs='?', help='Output GIF file (default: overwrites input)')

    args = parser.parse_args()

    output_path = args.output if args.output else args.input

    remove_transparency(args.input, output_path)

if __name__ == "__main__":
    main()
