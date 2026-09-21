"""Render a Legends social preview without generated typography or automatic scaling."""
import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1280, 640
MARGIN, TITLE_PX, SUBTITLE_PX = 80, 64, 36


def render(title, subtitle, font_path, output):
    if not title or title != title.lower() or any(c.isspace() for c in title):
        raise ValueError("Use the exact lowercase, hyphen-separated product name.")
    fonts = [ImageFont.truetype(str(font_path), size, layout_engine=ImageFont.Layout.BASIC)
             for size in (TITLE_PX, SUBTITLE_PX)]
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(canvas)
    available = WIDTH - 2 * MARGIN
    if draw.textlength(title, font=fonts[0]) > available:
        raise ValueError("Title exceeds fixed layout; do not shrink or rename it.")
    lines = []
    for word in subtitle.split():
        if draw.textlength(word, font=fonts[1]) > available:
            raise ValueError("Subtitle word exceeds fixed layout.")
        candidate = (lines[-1] + " " + word) if lines else word
        if lines and draw.textlength(candidate, font=fonts[1]) <= available:
            lines[-1] = candidate
        else:
            lines.append(word)
    if not lines or len(lines) > 3:
        raise ValueError("Subtitle requires one to three lines; revise copy, never scale type.")
    words = subtitle.split()

    @lru_cache(None)
    def balanced(start, count):
        if count == 0:
            return (0, []) if start == len(words) else (float("inf"), [])
        best = (float("inf"), [])
        for end in range(start + 1, len(words) + 1):
            line = " ".join(words[start:end])
            width = draw.textlength(line, font=fonts[1])
            if width > available:
                break
            score, rest = balanced(end, count - 1)
            score += (available - width) ** 2
            if score < best[0]:
                best = (score, [line] + rest)
        return best

    lines = balanced(0, len(lines))[1]
    draw.rectangle((0, 0, 3, HEIGHT - 1), fill="#ff0000")
    draw.line((MARGIN, 282, WIDTH - MARGIN, 282), fill="#666666", width=1)
    bounds = []
    rows = [(title, fonts[0], 176, "#ff0000")]
    rows += [(line, fonts[1], 324 + i * 48, "#ffffff") for i, line in enumerate(lines)]
    for text, font, y, color in rows:
        box = draw.textbbox((MARGIN, y), text, font=font, anchor="lt")
        if not (box[0] >= MARGIN and box[1] >= MARGIN and
                box[2] <= WIDTH - MARGIN and box[3] <= HEIGHT - MARGIN):
            raise ValueError(f"Text exceeds safe area: {text}")
        draw.text((MARGIN, y), text, font=font, anchor="lt", fill=color)
        bounds.append(list(box))
    output = Path(output)
    if output.suffix.lower() != ".png":
        raise ValueError("Output must be a PNG path.")
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, optimize=True)
    if output.stat().st_size >= 1_000_000:
        output.unlink()
        raise ValueError("Output exceeds the conservative 1 MB upload limit.")
    with Image.open(output) as check:
        assert check.size == (WIDTH, HEIGHT) and check.mode == "RGB"
    receipt = dict(template="legends-social-v1", title=title, subtitle=subtitle,
                   size=[WIDTH, HEIGHT], title_px=TITLE_PX, subtitle_px=SUBTITLE_PX,
                   safe_margin_px=MARGIN, lines=lines, text_bounds=bounds,
                   font_sha256=hashlib.sha256(Path(font_path).read_bytes()).hexdigest(),
                   image_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                   bytes=output.stat().st_size, upload_status="not_attempted")
    output.with_suffix(".json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("title", "subtitle", "font", "output"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    print(json.dumps(render(args.title, args.subtitle, args.font, args.output), indent=2))
