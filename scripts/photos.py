#!/usr/bin/env python3
"""Turn the originals in assets/photos/_originals/ into web-ready WebP files.

Each entry: output name -> (source file, crop box as fractions (left, top, right, bottom) or None, widths).
Run:  python3 scripts/photos.py   (needs Pillow)   then   python3 scripts/build.py"""
import json, os
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets/photos/_originals")
OUT = os.path.join(ROOT, "assets/photos")

PHOTOS = {
    # homepage hero: wide stage shot with open navy space on the left for the headline
    "hero":        ("Evan Website banner F.png", None, (1200, 1920)),
    # phone hero: tall crop centered on Evan
    "hero-m":      ("Evan Website banner F.png", (0.36, 0.0, 0.92, 1.0), (800,)),
    # centered cinematic hero: wide 21:9 stage shot (desktop) + 4:3 crop (phones)
    "hero-wide":   ("Evan Lopez2.JPEG", (0.0, 0.0, 1.0, 0.6429), (1200, 2000)),
    "hero-wide-m": ("Evan Lopez2.JPEG", (0.2, 0.0, 0.8, 0.675), (800,)),
    # blended hero backdrop: press-1 fades in from the left, foggy stage shot from the right
    "bg-left":     ("DSC00957-2.jpg", (0.0, 0.02, 1.0, 0.78), (700, 1200)),
    "bg-right":    ("Evan Website banner F.png", (0.36, 0.0, 1.0, 1.0), (700, 1200)),
    "about":       ("Evan Lopez.png", None, (800, 1200)),
    "podcast":     ("EvanPodcastcovercover.png", None, (600, 1200)),
    # on-stage gallery (4:5 frames)
    "live-1":      ("3E0A6707.jpg", (0.4, 0.0, 0.8, 1.0), (800,)),
    "live-2":      ("3E0A6757.jpg", (0.22, 0.0, 0.73, 1.0), (800,)),
    "live-3":      ("7M8A3619-Enhanced-NR.jpg", (0.0, 0.12, 1.0, 0.86), (800,)),
    "live-4":      ("C1678.00_34_38_09.Still006.jpg", (0.3, 0.0, 0.64, 1.0), (800,)),
    "live-5":      ("C3059 Copy 01.00_00_14_48.Still001 (1).jpg", (0.0, 0.14, 1.0, 0.83), (800,)),
    # press kit downloads
    "press-1":     ("DSC00957-2.jpg", None, (800, 1200, 2400)),
    "press-2":     ("Evan Lopez2.JPEG", None, (800, 1200, 2400)),
    "press-3":     ("3E0A6707.jpg", None, (800, 1200, 2400)),
    "press-4":     ("Evan Lopez.png", None, (800, 1200, 2400)),
}


def main():
    dims = {}
    for name, (fn, box, widths) in PHOTOS.items():
        im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, fn))).convert("RGB")
        if box:
            w, h = im.size
            im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
        dims[name] = [widths[0], round(im.height * widths[0] / im.width)]
        for tw in widths:
            r = im if im.width <= tw else im.resize((tw, round(im.height * tw / im.width)), Image.LANCZOS)
            r.save(os.path.join(OUT, f"{name}-{tw}.webp"), "WEBP", quality=80, method=6)
        print(name, im.size, "->", widths)
    json.dump(dims, open(os.path.join(OUT, "dims.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
