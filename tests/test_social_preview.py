import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "github/scripts"))
import social_preview as preview


def png(color="red", size=(1280, 640), compress_level=6):
    output = io.BytesIO()
    Image.new("RGB", size, color).save(output, format="PNG", compress_level=compress_level)
    return output.getvalue()


class SocialPreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.image = Path(self.temp.name) / "image with spaces.png"
        self.image.write_bytes(png())
        self.offline = patch.object(preview, "offline_mode", return_value=False)
        self.offline.start()
        self.addCleanup(self.offline.stop)

    def remote(self, data, custom=True):
        state = {"usesCustomOpenGraphImage": custom,
                 "openGraphImageUrl": "https://repository-images.githubusercontent.com/example"}
        with patch.object(preview, "github_image", return_value=state), \
                patch.object(preview, "fetch_image", return_value=data):
            return preview.social_preview("owner/repo", self.image, verify=True)

    def test_prepare_is_local_and_explicit(self):
        output = Path(self.temp.name) / "receipts" / "preview.json"
        with patch.object(preview, "github_image") as remote:
            receipt = preview.social_preview("owner/repo", self.image, output=output)
        remote.assert_not_called()
        self.assertEqual(receipt["status"], "prepared")
        self.assertEqual(receipt["settings_url"], "https://github.com/owner/repo/settings")
        self.assertEqual(receipt["image"]["width"], 1280)
        self.assertEqual(json.loads(output.read_text())["image"]["path"], str(self.image.resolve()))
        self.assertFalse(receipt["upload_performed_by_command"])

    def test_different_custom_image_cannot_pass(self):
        self.assertEqual(self.remote(png("blue"))["status"], "mismatch")

    def test_lossless_reencoding_passes(self):
        receipt = self.remote(png(compress_level=1))
        self.assertEqual(receipt["status"], "image_verified")
        self.assertNotEqual(receipt["remote"]["image"]["sha256"], receipt["image"]["sha256"])
        self.assertFalse(receipt["upload_performed_by_command"])

    def test_same_pixels_different_dimensions_do_not_pass(self):
        self.assertEqual(self.remote(png(size=(640, 1280)))["status"], "mismatch")

    def test_default_image_cannot_pass(self):
        self.assertEqual(self.remote(png(), custom=False)["status"], "mismatch")

    def test_offline_verification_never_calls_network(self):
        with patch.object(preview, "offline_mode", return_value=True), \
                patch.object(preview, "github_image") as remote:
            receipt = preview.social_preview("owner/repo", self.image, verify=True)
        remote.assert_not_called()
        self.assertEqual(receipt["status"], "unavailable")

    def test_failed_cli_does_not_leak_stderr(self):
        with patch.object(preview.subprocess, "run", return_value=subprocess.CompletedProcess(
                [], 1, "", "private credential information")):
            receipt = preview.social_preview("owner/repo", self.image, verify=True)
        self.assertEqual(receipt["status"], "unavailable")
        self.assertNotIn("private credential", json.dumps(receipt))

    def test_graphql_errors_even_with_data_fail(self):
        with patch.object(preview.subprocess, "run", return_value=subprocess.CompletedProcess(
                [], 0, '{"errors":[{"message":"no"}],"data":{"repository":{}}}', "")):
            with self.assertRaises(RuntimeError):
                preview.github_image("owner/repo")

    def test_graphql_repository_variables_are_explicit(self):
        with patch.object(preview.subprocess, "run", return_value=subprocess.CompletedProcess(
                [], 0, '{"data":{"repository":{}}}', "")) as run:
            preview.github_image("expected/repository")
        command = run.call_args.args[0]
        self.assertIn("owner=expected", command)
        self.assertIn("name=repository", command)
        self.assertIn("github.com", command)

    def test_invalid_repo_and_image_rejected(self):
        for repo in ("https://github.com/a/b", "a/b/c", "a/b?x"):
            with self.assertRaises(ValueError):
                preview.social_preview(repo, self.image)
        self.image.write_bytes(png(size=(100, 50)))
        with self.assertRaisesRegex(ValueError, "640"):
            preview.social_preview("a/b", self.image)

    def test_receipt_cannot_overwrite_image(self):
        with self.assertRaisesRegex(ValueError, "overwrite"):
            preview.social_preview("a/b", self.image, output=self.image)
        self.assertEqual(self.image.read_bytes(), png())

    def test_untrusted_image_urls_rejected(self):
        for url in ("http://githubusercontent.com/a", "https://githubusercontent.com.attacker.test/a",
                    "https://user:password@githubusercontent.com/a", "file:///secret",
                    "https://127.0.0.1/a", "https://githubusercontent.com:444/a"):
            self.assertFalse(preview.allowed_image_url(url), url)
        self.assertTrue(preview.allowed_image_url("https://repository-images.githubusercontent.com/a"))
        with self.assertRaises(ValueError):
            preview.ImageRedirects().redirect_request(None, None, 302, "", {}, "https://example.org")

    def test_bad_download_cannot_pass(self):
        self.assertEqual(self.remote(b"not an image")["status"], "unavailable")

    def test_unsafe_graphql_url_is_not_fetched_or_printed(self):
        state = {"usesCustomOpenGraphImage": True,
                 "openGraphImageUrl": "https://user:secret@githubusercontent.com/image"}
        with patch.object(preview, "github_image", return_value=state), \
                patch.object(preview, "fetch_image") as fetch:
            receipt = preview.social_preview("owner/repo", self.image, verify=True)
        fetch.assert_not_called()
        self.assertEqual(receipt["status"], "unavailable")
        self.assertNotIn("secret", json.dumps(receipt))

    def test_local_image_changed_during_verification_cannot_pass(self):
        state = {"usesCustomOpenGraphImage": True,
                 "openGraphImageUrl": "https://repository-images.githubusercontent.com/example"}
        def fetch(_url):
            self.image.write_bytes(png("blue"))
            return png()
        with patch.object(preview, "github_image", return_value=state), \
                patch.object(preview, "fetch_image", side_effect=fetch):
            receipt = preview.social_preview("owner/repo", self.image, verify=True)
        self.assertEqual(receipt["status"], "unavailable")

    def test_served_download_is_bounded_and_has_no_auth_headers(self):
        from unittest.mock import MagicMock
        response = MagicMock()
        response.read.return_value = b"x" * (preview.MAX_IMAGE_BYTES + 1)
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value = response
        with patch.object(preview, "build_opener", return_value=opener):
            with self.assertRaisesRegex(ValueError, "download limit"):
                preview.fetch_image("https://repository-images.githubusercontent.com/example")
        response.read.assert_called_once_with(preview.MAX_IMAGE_BYTES + 1)
        request = opener.open.call_args.args[0]
        self.assertNotIn("Authorization", request.headers)
        self.assertNotIn("Cookie", request.headers)

    def test_cli_prepares_from_unrelated_directory_and_offline_verify_fails(self):
        base = [sys.executable, str(ROOT / "legends_github.py"), "--offline",
                "social-preview", "--repo", "owner/repo", "--image", str(self.image)]
        prepared = subprocess.run(base, cwd=self.temp.name, capture_output=True, text=True)
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        self.assertEqual(json.loads(prepared.stdout)["status"], "prepared")
        verified = subprocess.run([*base, "--verify"], cwd=self.temp.name, capture_output=True, text=True)
        self.assertEqual(verified.returncode, 1, verified.stderr)
        self.assertEqual(json.loads(verified.stdout)["status"], "unavailable")


if __name__ == "__main__":
    unittest.main()
