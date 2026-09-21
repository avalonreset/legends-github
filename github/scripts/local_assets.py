#!/usr/bin/env python3
"""Local image preparation helpers; no providers, credentials, or network calls."""

from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover - exercised through capability guards
    Image = None
    ImageOps = None


class AssetPreparationError(RuntimeError):
    """Raised when a supplied local image cannot be prepared."""


def pillow_available() -> bool:
    """Return whether the optional local image dependency is usable."""
    return Image is not None


def _prepare_image(source: Path, destination: Path, image_format: str, *, preview: bool = False) -> Path:
    """Write a new metadata-free derivative while preserving existing files."""
    if Image is None:
        raise AssetPreparationError("Pillow is required to prepare local image derivatives.")
    if destination.exists():
        raise AssetPreparationError(f"Existing image will not be overwritten: {destination}")
    try:
        with Image.open(source) as image:
            oriented = ImageOps.exif_transpose(image)
            prepared = ImageOps.fit(oriented, (1280, 640), method=Image.Resampling.LANCZOS) if preview else oriented
            clean = Image.new("RGB" if image_format == "JPEG" else "RGBA", prepared.size)
            clean.paste(prepared.convert(clean.mode))
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation protects user files even if a destination appeared after the check.
            with destination.open("xb") as output:
                clean.save(output, image_format, quality=85 if image_format == "JPEG" else 80)
    except (OSError, ValueError) as exc:
        raise AssetPreparationError(f"Could not prepare local image {source}: {exc}") from exc
    return destination


def convert_to_webp(source: Path, destination: Path) -> Path:
    """Convert a supplied image to a WebP banner without changing its original."""
    return _prepare_image(source, destination, "WEBP")


def convert_to_jpeg(source: Path, destination: Path) -> Path:
    """Convert a supplied image to a JPEG avatar without changing its original."""
    return _prepare_image(source, destination, "JPEG")


def render_social_preview_from_banner(source: Path, destination: Path) -> Path:
    """Create a centered 1280x640 JPEG crop of a supplied local banner."""
    return _prepare_image(source, destination, "JPEG", preview=True)
