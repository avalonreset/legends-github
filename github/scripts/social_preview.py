"""Portable upload preparation and public served-image verification.

Uploading uses the agent host's supported browser/file-picker tools. This module
does not automate a private GitHub API or access browser credentials.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from github_runtime import offline_mode

MAX_IMAGE_BYTES = 10_000_000
QUERY = """query($owner:String!,$name:String!){
  repository(owner:$owner,name:$name){openGraphImageUrl usesCustomOpenGraphImage}
}"""


def image_details(data: bytes) -> dict:
    """Compare decoded pixels so lossless re-encoding does not cause a mismatch."""
    from PIL import Image

    with Image.open(io.BytesIO(data)) as image:
        if image.width * image.height > 20_000_000:
            raise ValueError("Image exceeds the 20 megapixel inspection limit.")
        if getattr(image, "n_frames", 1) != 1:
            raise ValueError("Use a static image for verifiable social previews.")
        pixels = image.convert("RGBA")
        return {
            "format": image.format,
            "width": image.width,
            "height": image.height,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "pixel_sha256": hashlib.sha256(pixels.tobytes()).hexdigest(),
        }


def allowed_image_url(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    return (
        parsed.scheme == "https"
        and parsed.port in (None, 443)
        and not parsed.username and not parsed.password
        and any(host == domain or host.endswith("." + domain)
                for domain in ("githubusercontent.com", "githubassets.com"))
    )


class ImageRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed_image_url(newurl):
            raise ValueError("Served-image redirect is outside supported GitHub image hosts.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_image(url: str) -> bytes:
    if not allowed_image_url(url):
        raise ValueError("Served-image URL is outside supported GitHub image hosts.")
    request = Request(url, headers={"User-Agent": "legends-github-social-preview",
                                    "Cache-Control": "no-cache"})
    with build_opener(ImageRedirects()).open(request, timeout=30) as response:
        data = response.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError("Served image exceeds the download limit.")
    return data


def github_image(repo: str) -> dict:
    owner, name = repo.split("/")
    completed = subprocess.run(
        ["gh", "api", "graphql", "--hostname", "github.com", "-f", f"query={QUERY}",
         "-f", f"owner={owner}", "-f", f"name={name}"],
        capture_output=True, text=True, timeout=45, check=False,
    )
    if completed.returncode:
        raise RuntimeError("GitHub GraphQL read failed; check gh authentication and repository access.")
    payload = json.loads(completed.stdout)
    if payload.get("errors"):
        raise RuntimeError("GitHub GraphQL returned errors; image state is unavailable.")
    repository = (payload.get("data") or {}).get("repository")
    if not isinstance(repository, dict):
        raise RuntimeError("Repository image state is unavailable.")
    return repository


def social_preview(repo: str, image: Path, *, verify: bool = False,
                   output: Path | None = None) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Use an explicit github.com OWNER/REPO.")
    image = image.expanduser().resolve(strict=True)
    if not image.is_file() or image.stat().st_size >= 1_000_000:
        raise ValueError("Use a static PNG, JPG or GIF file under 1,000,000 bytes.")
    expected = image_details(image.read_bytes())
    if expected["format"] not in ("PNG", "JPEG", "GIF"):
        raise ValueError("Use a PNG, JPG or GIF image.")
    if expected["width"] < 640 or expected["height"] < 320:
        raise ValueError("Social preview must be at least 640 by 320 pixels.")
    if output and output.expanduser().resolve() == image:
        raise ValueError("Receipt output must not overwrite the image.")
    receipt = {
        "schema_version": "1.0", "operation": "social-preview", "status": "prepared",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "repo": repo, "settings_url": f"https://github.com/{repo}/settings",
        "image": {"path": str(image), **expected},
        "recommended_dimensions": [1280, 640],
        "upload_performed_by_command": False,
        "instructions": [
            "Inspect Settings > General > Social preview in an authenticated supported browser.",
            "Click Edit scoped to Social preview, then Upload an image.",
            "Use the host's supported file-upload control with the exact absolute image path.",
            "If label matching fails, inspect the current DOM and bind the supported upload "
            "to the observed input[type=file] in this section, or use the supported native picker.",
            "Complete any visible save/crop control, preserve the full image, then reload Settings.",
            "Run this command with --verify and inspect the saved thumbnail before declaring complete.",
        ],
        "required_host_capabilities": [
            "authenticated page inspection and click",
            "supported DOM-bound file input upload OR native file picker control",
        ],
    }
    if verify:
        if offline_mode():
            receipt.update(status="unavailable", reason="Offline mode prevents live verification.")
        else:
            try:
                state = github_image(repo)
                custom = state.get("usesCustomOpenGraphImage")
                url = state.get("openGraphImageUrl")
                receipt["remote"] = {"uses_custom_image": custom}
                if custom is not True:
                    receipt.update(status="mismatch", reason="GitHub does not report a custom image.")
                elif not isinstance(url, str) or not url:
                    receipt.update(status="unavailable", reason="GraphQL did not return an image URL.")
                elif not allowed_image_url(url):
                    receipt.update(status="unavailable", reason="Unsupported served-image URL.")
                else:
                    receipt["remote"]["url"] = url
                    served = image_details(fetch_image(url))
                    receipt["remote"]["image"] = served
                    match = all(expected[key] == served[key]
                                for key in ("width", "height", "pixel_sha256"))
                    receipt.update(
                        status="image_verified" if match else "mismatch",
                        reason="Served dimensions and decoded pixels match the requested image."
                        if match else "Served image differs; inspect for an old image, cache delay "
                        "or platform recompression. Do not claim verified upload.",
                    )
                    if hashlib.sha256(image.read_bytes()).hexdigest() != expected["sha256"]:
                        receipt.update(status="unavailable",
                                       reason="Local image changed during verification; prepare it again.")
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
                # Do not echo CLI stderr, response bodies, or credential-bearing URLs.
                receipt.update(status="unavailable",
                               reason=f"Live image verification failed ({type(exc).__name__}); "
                               "check gh access, network and supported image format.")
    if output:
        output = output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt
