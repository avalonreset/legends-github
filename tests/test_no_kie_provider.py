"""Optional artwork must stay local and must never require provider credentials."""

import json
import os
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "github" / "scripts"))

import empire_repo
import github_runtime
import local_assets
import readme_repo


class NoImageProviderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.guards = ExitStack()
        self.addCleanup(self.guards.close)
        self.guards.enter_context(patch.dict(os.environ, {"KIE_API_KEY": "unused-test-sentinel"}))
        self.guards.enter_context(patch.object(github_runtime, "load_env_file", side_effect=AssertionError("credential file read")))
        self.guards.enter_context(patch("urllib.request.urlopen", side_effect=AssertionError("network request")))
        self.guards.enter_context(patch("socket.socket", side_effect=AssertionError("network socket")))

    def asset_snapshot(self, **updates):
        snapshot = {
            "repo_root": str(self.repo),
            "repo": "owner/example",
            "metadata": {},
            "banner_path": None,
            "social_preview_path": None,
        }
        snapshot.update(updates)
        return snapshot

    def write_asset(self, name, *, image=False):
        path = self.repo / "assets" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if image:
            local_assets.Image.new("RGB", (400, 300), "teal").save(path)
        else:
            path.write_bytes(b"existing user asset")
        return path

    def test_missing_artwork_needs_no_credentials_or_pillow(self):
        with patch.object(local_assets, "Image", None):
            readme = readme_repo.ensure_readme_assets(self.asset_snapshot())
            avatar = empire_repo.generate_avatar_asset(self.repo, "owner/example", "owner", [])
        self.assertFalse(readme["banner_generated"])
        self.assertFalse(readme["social_preview_generated"])
        self.assertEqual(readme["asset_tasks"], [])
        self.assertEqual(avatar["status"], "not_supplied")
        self.assertFalse(avatar["generated"])
        self.assertFalse((self.repo / "assets").exists())

    def test_existing_assets_are_reused_without_pillow_or_overwrites(self):
        paths = [self.write_asset(name) for name in ("banner.png", "social-preview.jpg", "avatar.jpg")]
        original = {path: path.read_bytes() for path in paths}
        with patch.object(local_assets, "Image", None):
            readme = readme_repo.ensure_readme_assets(self.asset_snapshot(
                banner_path="assets/banner.png", social_preview_path="assets/social-preview.jpg"))
            avatar = empire_repo.generate_avatar_asset(self.repo, "owner/example", "owner", [])
        self.assertEqual(avatar["status"], "existing")
        self.assertEqual(avatar["path"], "assets/avatar.jpg")
        self.assertFalse(readme["social_preview_generated"])
        self.assertEqual({path: path.read_bytes() for path in paths}, original)
        self.assertNotIn("unused-test-sentinel", json.dumps([readme, avatar]))

    def test_snapshot_does_not_load_provider_credentials(self):
        base = {"repo": "example", "repo_name": "example"}
        with patch.object(readme_repo, "build_repo_snapshot", return_value=base), \
                patch.object(readme_repo, "load_seo_payload", return_value={}), \
                patch.object(readme_repo, "read_repo_cache", return_value={}):
            snapshot = readme_repo.build_snapshot(self.repo)
        self.assertNotIn("kie_api_key", snapshot)
        self.assertNotIn("unused-test-sentinel", json.dumps(snapshot))

    def test_readme_flag_continues_without_artwork_blockers_or_placeholders(self):
        snapshot = self.asset_snapshot(
            repo_name="example", repo_type="CLI Tool", current_readme="# Example\n",
            current_readme_path=str(self.repo / "README.md"),
            seo_data={"primary_keyword": {"keyword": "example"}, "secondary_keywords": []},
            audit_data={}, legal_data={}, license_label="MIT", docs_link="",
        )
        with patch.object(readme_repo, "build_snapshot", return_value=snapshot):
            payload = readme_repo.build_readme_payload(self.repo, generate_assets=True)
        self.assertTrue(payload["assets_requested"])
        self.assertEqual(payload["asset_mode"], "local-only")
        self.assertEqual(payload["banner_status"], "not_supplied")
        self.assertEqual(payload["blocked"], [])
        self.assertNotIn("TODO: Add banner", payload["generated_readme"])

    @unittest.skipUnless(local_assets.pillow_available(), "Pillow is optional")
    def test_local_derivatives_preserve_originals_and_reuse_second_run(self):
        banner = self.write_asset("originals/banner.png", image=True)
        avatar_source = self.write_asset("originals/avatar.png", image=True)
        originals = {path: path.read_bytes() for path in (banner, avatar_source)}
        readme = readme_repo.ensure_readme_assets(self.asset_snapshot())
        avatar = empire_repo.generate_avatar_asset(self.repo, "owner/example", "owner", [])
        self.assertTrue(readme["banner_prepared"])
        self.assertFalse(readme["banner_generated"])
        self.assertTrue(readme["social_preview_generated"])
        self.assertTrue(avatar["prepared"])
        self.assertFalse(avatar["generated"])
        with local_assets.Image.open(self.repo / readme["social_preview_path"]) as image:
            self.assertEqual(image.size, (1280, 640))
        second = readme_repo.ensure_readme_assets(self.asset_snapshot(
            banner_path=readme["banner_path"], social_preview_path=readme["social_preview_path"]))
        self.assertFalse(second["banner_prepared"])
        self.assertFalse(second["social_preview_generated"])
        self.assertEqual({path: path.read_bytes() for path in originals}, originals)

    def test_missing_pillow_keeps_planning_available(self):
        self.write_asset("originals/banner.png")
        with patch.object(local_assets, "Image", None):
            readme = readme_repo.ensure_readme_assets(self.asset_snapshot())
        self.assertFalse(readme["banner_prepared"])
        self.assertIn("Pillow", " ".join(readme["asset_notes"]))
        self.assertFalse((self.repo / "assets" / "banner.webp").exists())

    @unittest.skipUnless(local_assets.pillow_available(), "Pillow is optional")
    def test_existing_destination_is_never_overwritten(self):
        source = self.write_asset("originals/avatar.png", image=True)
        destination = self.write_asset("avatar.jpg")
        before = destination.read_bytes()
        with self.assertRaises(local_assets.AssetPreparationError):
            local_assets.convert_to_jpeg(source, destination)
        self.assertEqual(destination.read_bytes(), before)

    def test_module_scripts_have_no_provider_code(self):
        self.assertFalse((ROOT / "github/scripts/kie_assets.py").exists())
        for installer in ("install.ps1", "install.sh",
                          "install-codex.ps1", "install-codex.sh"):
            self.assertFalse((ROOT / installer).exists())
        files = [ROOT / "github/scripts" / name for name in ("local_assets.py", "readme_repo.py", "empire_repo.py")]
        for path in files:
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8").lower()
                for marker in ("kie.ai", "kie_api_key", "kie_assets", "resolve_kie", "create_kie", "poll_kie"):
                    self.assertNotIn(marker, source)


if __name__ == "__main__":
    unittest.main()
