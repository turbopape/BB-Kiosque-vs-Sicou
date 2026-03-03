#!/usr/bin/env python3
"""Convert green-screen PNGs to transparent PNGs with optional luminosity normalization.

Usage: python green2alpha.py <folder> [--suffix _trans] [--tolerance 80] [--normalize] [--pixelate 3]
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageStat, ImageEnhance
except ImportError:
    print("Pillow is required: pip install Pillow")
    sys.exit(1)


def remove_bg(img_path, tolerance):
    img = Image.open(img_path).convert("RGBA")
    pixels = img.load()
    w, h = img.size

    bg_r, bg_g, bg_b, _ = pixels[0, 0]
    print(f"  Detected background color: ({bg_r}, {bg_g}, {bg_b})")

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if (abs(r - bg_r) < tolerance and
                abs(g - bg_g) < tolerance and
                abs(b - bg_b) < tolerance):
                pixels[x, y] = (0, 0, 0, 0)

    return img


def mean_luminosity(img):
    """Average brightness of visible (non-transparent) pixels."""
    pixels = img.load()
    w, h = img.size
    total = 0
    count = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a > 0:
                total += 0.299 * r + 0.587 * g + 0.114 * b
                count += 1
    return total / count if count > 0 else 128


def adjust_luminosity(img, target_lum):
    """Scale brightness to match target luminosity."""
    current = mean_luminosity(img)
    if current == 0:
        return img
    factor = target_lum / current
    print(f"  Luminosity: {current:.1f} -> {target_lum:.1f} (factor {factor:.2f})")
    # Preserve alpha — only adjust RGB via brightness enhancer
    rgb = img.convert("RGB")
    enhanced = ImageEnhance.Brightness(rgb).enhance(factor)
    enhanced = enhanced.convert("RGBA")
    # Restore original alpha channel
    enhanced.putalpha(img.getchannel("A"))
    return enhanced


def darken_edges(img, threshold=120):
    """Push dark pixels toward pure black for crisper outlines."""
    img = img.copy()
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum < threshold:
                # Scale toward black — the darker it already is, the blacker it gets
                factor = lum / threshold
                pixels[x, y] = (int(r * factor), int(g * factor), int(b * factor), a)
    return img


def pixelate(img, factor):
    """Downscale then upscale with nearest-neighbor for a pixel art look."""
    w, h = img.size
    small = img.resize((w // factor, h // factor), Image.NEAREST)
    result = small.resize((w, h), Image.NEAREST)
    print(f"  Pixelated: {w}x{h} -> {w // factor}x{h // factor} -> {w}x{h} (factor {factor})")
    return result


def main():
    parser = argparse.ArgumentParser(description="Convert green-screen PNGs to transparent PNGs.")
    parser.add_argument("folder", help="Folder containing PNG files (searched recursively)")
    parser.add_argument("--suffix", default="_trans", help="Suffix added before .png (default: _trans)")
    parser.add_argument("--tolerance", type=int, default=80, help="Color tolerance 0-255 (default: 80)")
    parser.add_argument("--normalize", action="store_true", help="Normalize luminosity across all sprites")
    parser.add_argument("--pixelate", type=int, default=0, metavar="N", help="Pixelate by factor N (default: off, recommended: 3)")
    parser.add_argument("--ink", type=int, default=0, metavar="T", help="Darken pixels below brightness T toward black (recommended: 120)")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"Error: {folder} is not a directory")
        sys.exit(1)

    sources = sorted([p for p in folder.rglob("*.png") if args.suffix not in p.stem])
    if not sources:
        print(f"No PNG files found in {folder}")
        sys.exit(1)

    # Pass 1: remove backgrounds
    processed = []
    for p in sources:
        print(f"{p}")
        img = remove_bg(p, args.tolerance)
        out = p.with_stem(p.stem + args.suffix)
        processed.append((out, img))

    # Pass 2: normalize luminosity if requested
    if args.normalize and len(processed) > 1:
        lums = [(path, mean_luminosity(img)) for path, img in processed]
        avg_lum = sum(l for _, l in lums) / len(lums)
        print(f"\nNormalizing to average luminosity: {avg_lum:.1f}")
        processed = [(path, adjust_luminosity(img, avg_lum)) for path, img in processed]

    # Pass 3: pixelate if requested
    if args.pixelate > 1:
        print(f"\nPixelating (factor {args.pixelate}):")
        processed = [(path, pixelate(img, args.pixelate)) for path, img in processed]

    # Pass 4: darken edges if requested
    if args.ink > 0:
        print(f"\nDarkening edges (threshold {args.ink}):")
        processed = [(path, darken_edges(img, args.ink)) for path, img in processed]

    # Save
    for out, img in processed:
        img.save(out, "PNG")
        print(f"  Saved {out}")

    print(f"\nDone. Processed {len(processed)} files.")


if __name__ == "__main__":
    main()
