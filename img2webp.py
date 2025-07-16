#!/usr/bin/env python3
# convert_images.py
# Recursively convert all PNG/JPG/GIF/BMP/TIFF under ../01-* folders
# into WebP (lossy Q=80), then emit images.json for the gallery.

import sys
import json
import os
from pathlib import Path
from PIL import Image
from tqdm import tqdm

# Quality for .webp output
WEBP_QUALITY = 80

# Supported source extensions
SRC_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tif', '.tiff', '.webp'}

script_dir = Path(__file__).resolve().parent
root_dir = script_dir

out_list = []

for category_dir in tqdm(sorted(root_dir.iterdir()), desc="Scanning categories"):
    if not category_dir.is_dir():
        continue

    category = category_dir.name.split(':', 1)[-1]

    # collect all image files in this category
    files = [p for p in category_dir.rglob('*') if p.is_file() and p.suffix.lower() in SRC_EXTS]
    for src in tqdm(files, desc=f"Processing {category}", leave=False):
        # target .webp next to the source
        dst = src.with_suffix('.webp')
        # skip if up-to-date
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            webp_path = dst
        else:
            img = Image.open(src).convert('RGBA')
            img.save(dst, 'WEBP', quality=WEBP_QUALITY, method=6)
            webp_path = dst

        # read dimensions
        w, h = Image.open(webp_path).size

        # make path relative to index.html in project root
        rel = webp_path.relative_to(root_dir).as_posix()

        out_list.append({
            'category': category,
            'file':     rel,
            'width':    w,
            'height':   h
        })

# write JSON
with open(script_dir / 'images.json', 'w', encoding='utf-8') as f:
    json.dump(out_list, f, indent=2)

print(f'✓ Converted {len(out_list)} images, manifest → images.json')