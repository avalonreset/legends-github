#!/usr/bin/env python3
"""KIE.ai and Pillow helpers for deterministic image pipelines."""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from PIL import Image
except ImportError:  # pragma: no cover - exercised through pillow_available guards
    Image = None


KIE_CREATE_URL = "https://api.kie.ai/api/v1/jobs/createTask"
KIE_RECORD_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"
KIE_TEXT_TO_IMAGE_MODEL = "gpt-image-2-text-to-image"
KIE_IMAGE_TO_IMAGE_MODEL = "gpt-image-2-image-to-image"


def pillow_available() -> bool:
    """Return whether Pillow is importable."""
    return importlib.util.find_spec("PIL") is not None


class AssetGenerationError(RuntimeError):
    """Raised when deterministic asset generation fails."""


def _kie_request(api_key: str, method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Call one KIE API endpoint and return a parsed JSON payload."""
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "codex-github/1.0",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AssetGenerationError(f"KIE API HTTP {exc.code}: {detail or exc.reason}") from exc
    except URLError as exc:
        raise AssetGenerationError(f"KIE API request failed: {exc.reason}") from exc


def create_kie_task(
    api_key: str,
    prompt: str,
    *,
    aspect_ratio: str,
    input_urls: list[str] | None = None,
) -> str:
    """Create one KIE image generation task and return the task id."""
    image_urls = input_urls or []
    model = KIE_IMAGE_TO_IMAGE_MODEL if image_urls else KIE_TEXT_TO_IMAGE_MODEL
    task_input: dict[str, Any] = {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
    }
    if image_urls:
        task_input["input_urls"] = image_urls
    payload = {
        "model": model,
        "input": task_input,
    }
    response = _kie_request(api_key, "POST", KIE_CREATE_URL, payload)
    if int(response.get("code") or 0) != 200:
        raise AssetGenerationError(f"KIE task creation failed: {response}")
    task_id = str((response.get("data") or {}).get("taskId") or "").strip()
    if not task_id:
        raise AssetGenerationError(f"KIE task creation returned no taskId: {response}")
    return task_id


def poll_kie_task(api_key: str, task_id: str, *, timeout_seconds: int = 180, poll_seconds: int = 4) -> dict[str, Any]:
    """Poll a KIE task until it finishes or times out."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        url = f"{KIE_RECORD_URL}?{urlencode({'taskId': task_id})}"
        response = _kie_request(api_key, "GET", url)
        if int(response.get("code") or 0) != 200:
            raise AssetGenerationError(f"KIE task polling failed: {response}")
        data = response.get("data") or {}
        state = str(data.get("state") or "").lower()
        if state == "success":
            return data
        if state == "fail":
            raise AssetGenerationError(str(data.get("failMsg") or "KIE image generation failed."))
        time.sleep(poll_seconds)
    raise AssetGenerationError(f"KIE task timed out after {timeout_seconds} seconds: {task_id}")


def result_url(record: dict[str, Any]) -> str:
    """Extract the first downloadable result URL from a completed KIE record."""
    raw = record.get("resultJson")
    payload: dict[str, Any] = {}
    if isinstance(raw, dict):
        payload = raw
    elif isinstance(raw, str) and raw.strip():
        payload = json.loads(raw)
    urls = payload.get("resultUrls") or payload.get("urls") or []
    if not urls:
        raise AssetGenerationError(f"KIE task completed without result URLs: {record}")
    return str(urls[0])


def download_binary(url: str, destination: Path) -> Path:
    """Download one binary asset to disk."""
    request = Request(url, headers={"User-Agent": "codex-github/1.0"})
    try:
        with urlopen(request, timeout=120) as response:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(response.read())
            return destination
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AssetGenerationError(f"Asset download failed with HTTP {exc.code}: {detail or exc.reason}") from exc
    except URLError as exc:
        raise AssetGenerationError(f"Asset download failed: {exc.reason}") from exc


def convert_png_to_webp(source: Path, destination: Path) -> Path:
    """Convert a source image to an optimized WebP banner."""
    if Image is None:
        raise AssetGenerationError("Pillow is required for banner conversion.")
    with Image.open(source) as image:
        clean = Image.new(image.mode, image.size)
        clean.putdata(list(image.getdata()))
        destination.parent.mkdir(parents=True, exist_ok=True)
        clean.save(destination, "WEBP", quality=80, method=6)
    return destination


def convert_png_to_jpeg(source: Path, destination: Path) -> Path:
    """Convert a source image to an optimized JPEG avatar."""
    if Image is None:
        raise AssetGenerationError("Pillow is required for avatar conversion.")
    with Image.open(source) as image:
        clean = Image.new(image.mode, image.size)
        clean.putdata(list(image.getdata()))
        destination.parent.mkdir(parents=True, exist_ok=True)
        clean.convert("RGB").save(destination, "JPEG", quality=85, optimize=True)
    return destination


def render_social_preview_from_banner(source: Path, destination: Path) -> Path:
    """Create a 1280x640 social preview JPEG from an existing banner image."""
    if Image is None:
        raise AssetGenerationError("Pillow is required for social preview generation.")
    with Image.open(source) as image:
        width, height = image.size
        target_ratio = 2.0
        current_ratio = width / height if height else target_ratio
        if current_ratio > target_ratio:
            target_width = int(height * target_ratio)
            trim = max((width - target_width) // 2, 0)
            cropped = image.crop((trim, 0, width - trim, height))
        else:
            target_height = int(width / target_ratio)
            trim = max((height - target_height) // 2, 0)
            cropped = image.crop((0, trim, width, height - trim))
        preview = cropped.resize((1280, 640), Image.LANCZOS)
        clean = Image.new(preview.mode, preview.size)
        clean.putdata(list(preview.getdata()))
        destination.parent.mkdir(parents=True, exist_ok=True)
        clean.convert("RGB").save(destination, "JPEG", quality=85, optimize=True)
    if destination.stat().st_size > 1_048_576:
        with Image.open(destination) as image:
            image.save(destination, "JPEG", quality=70, optimize=True)
    return destination
