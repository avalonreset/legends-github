import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "github" / "scripts"))
import cache_state
import github_runtime
import validate_setup

class RuntimeSafetyTests(unittest.TestCase):
    def test_external_cache_does_not_edit_target_gitignore(self):
        with tempfile.TemporaryDirectory() as root:
            repo = Path(root) / "repo"; repo.mkdir()
            ignore = repo / ".gitignore"; ignore.write_text("user-owned\n")
            external = Path(root) / "external"
            with patch.dict(os.environ, {"GITHUB_AUDIT_DIR": str(external)}):
                path = cache_state.write_repo_cache(repo, "test.json", {"ok": True})
            self.assertEqual(ignore.read_text(), "user-owned\n")
            self.assertEqual(path.parent, external)
            self.assertTrue(json.loads(path.read_text())["ok"])
            self.assertEqual(list(repo.iterdir()), [ignore])

    def test_default_cache_does_not_create_gitignore(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ, {}, clear=True):
            repo = Path(root)
            cache_state.write_repo_cache(repo, "test.json", {"ok": True})
            self.assertFalse((repo / ".gitignore").exists())

    def test_failed_atomic_write_preserves_original(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "cache.json"; path.write_text('{"old":true}')
            with patch.object(cache_state.os, "replace", side_effect=OSError("failure")):
                with self.assertRaises(OSError):
                    cache_state._atomic_json(path, {"new": True})
            self.assertEqual(json.loads(path.read_text()), {"old": True})
            self.assertEqual(list(Path(root).iterdir()), [path])

    def test_offline_blocks_github_subprocess(self):
        with patch.dict(os.environ, {"LEGENDS_GITHUB_OFFLINE": "1"}), patch.object(github_runtime.subprocess, "run") as run:
            self.assertFalse(github_runtime.gh_auth_ok())
            result = github_runtime.run_command(["gh", "repo", "view"], check=False)
            self.assertEqual(result.returncode, 125)
            run.assert_not_called()

    def test_portable_readiness_without_host_or_providers(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ, {"LEGENDS_GITHUB_OFFLINE": "1", "LEGENDS_GITHUB_HOME": str(Path(root)/"state"), "GITHUB_AUDIT_DIR": str(Path(root)/"cache")}):
            with patch.object(validate_setup, "have_command", side_effect=lambda name: name == "git"), patch.object(validate_setup, "repo_slug_from_git", return_value=None), patch.object(validate_setup, "pillow_available", return_value=False):
                for mode in ("portable", "cli", "api", "both"):
                    result = validate_setup.validate_setup(Path(root), mode=mode)
                    self.assertTrue(result["ready"], result)
                    self.assertFalse(result["capabilities"]["github_metadata_ready"])
                    self.assertFalse(any("Installed skill" in c["label"] for c in result["checks"]))

    def test_capabilities_does_not_require_target_repo(self):
        with tempfile.TemporaryDirectory() as root:
            p = subprocess.run([sys.executable, str(ROOT/"legends_github.py"), "capabilities"], cwd=root, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertFalse(json.loads(p.stdout)["requires_llm_provider"])

    def test_offline_rejects_remote_mutation(self):
        p = subprocess.run([sys.executable, str(ROOT/"legends_github.py"), "--offline", "meta", "--apply"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertTrue(json.loads(p.stdout)["error"])

if __name__ == "__main__":
    unittest.main()
