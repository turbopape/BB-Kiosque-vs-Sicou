#!/usr/bin/env python3
"""Convert green-screen PNGs to transparent PNGs.

Usage: python green2alpha.py <folder> [--suffix _trans] [--tolerance 80]
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow is required: pip install Pillow")
    sys.exit(1)


def remove_green(img_path, out_path, tolerance):
    img = Image.open(img_path).convert("RGBA")
    pixels = img.load()
    w, h = img.size

    # Sample top-left corner to detect the actual background color
    bg_r, bg_g, bg_b, _ = pixels[0, 0]
    print(f"  Detected background color: ({bg_r}, {bg_g}, {bg_b})")

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if (abs(r - bg_r) < tolerance and
                abs(g - bg_g) < tolerance and
                abs(b - bg_b) < tolerance):
                pixels[x, y] = (0, 0, 0, 0)

    img.save(out_path, "PNG")


def main():
    parser = argparse.ArgumentParser(description="Convert green-screen PNGs to transparent PNGs.")
    parser.add_argument("folder", help="Folder containing PNG files (searched recursively)")
    parser.add_argument("--suffix", default="_trans", help="Suffix added before .png (default: _trans)")
    parser.add_argument("--tolerance", type=int, default=80, help="Color tolerance 0-255 (default: 80)")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"Error: {folder} is not a directory")
        sys.exit(1)

    pngs = list(folder.rglob("*.png"))
    if not pngs:
        print(f"No PNG files found in {folder}")
        sys.exit(1)

    for p in pngs:
        if args.suffix in p.stem:
            continue
        out = p.with_stem(p.stem + args.suffix)
        print(f"{p} -> {out}")
        remove_green(p, out, args.tolerance)

    print(f"Done. Processed {len(pngs)} files.")


if __name__ == "__main__":
    main()
