"""Render an optional typography banner from explicit copy and a supplied font."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont


def render_banner(title: str, lines: list[str], font_path: Path, output_dir: Path) -> dict:
    """Use the Legends layout without providers, font substitution or overwrites."""
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", title):
        raise ValueError("Title must be the exact lowercase, dash-separated project name.")
    if not 1 <= len(lines) <= 2 or any(not line.strip() or line != line.lower() or '\n' in line for line in lines):
        raise ValueError("Supply one or two nonempty lowercase subtitle lines.")
    if len(title) > 100 or any(len(line) > 140 for line in lines):
        raise ValueError("Copy is too long; edit the copy rather than shrinking the font.")
    font_path = font_path.expanduser().resolve(strict=True)
    fonts = [ImageFont.truetype(str(font_path), size, layout_engine=ImageFont.Layout.BASIC) for size in (176, 104)]
    canvas = Image.new('RGB', (4096, 1024), '#000000')
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 7, 1023), fill='#ff0000')
    boxes = []
    rows = [(title, fonts[0], 212, '#ff0000')] + [(line, fonts[1], 534 + i * 132, '#ffffff') for i, line in enumerate(lines)]
    for text, font, y, color in rows:
        box = draw.textbbox((192, y), text, font=font, anchor='lt')
        if box[0] < 192 or box[2] > 3904 or box[3] > 864:
            raise ValueError("Copy does not fit the template. Shorten it or choose a deliberate two-line break.")
        draw.text((192, y), text, font=font, anchor='lt', fill=color)
        boxes.append(box)
    draw.line((192, 456, 3904, 456), fill='#666666', width=2)
    # Fresh directory only: originals and previous drafts are never replaced.
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=False)
    canvas.save(output_dir / 'banner.png', optimize=True)
    canvas.save(output_dir / 'banner.webp', lossless=True, method=6)
    canvas.resize((1024, 256), Image.Resampling.LANCZOS).save(output_dir / 'preview.png')
    receipt = {'template': 'legends-type-v1', 'title': title, 'subtitle_lines': lines,
               'size': list(canvas.size), 'text_bounds': boxes,
               'font_sha256': hashlib.sha256(font_path.read_bytes()).hexdigest(),
               'banner_sha256': hashlib.sha256((output_dir / 'banner.webp').read_bytes()).hexdigest(),
               'output_dir': str(output_dir), 'published': False}
    (output_dir / 'banner.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--title', required=True)
    parser.add_argument('--subtitle-line', action='append', required=True)
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(render_banner(args.title, args.subtitle_line, args.font, args.output_dir), indent=2))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
