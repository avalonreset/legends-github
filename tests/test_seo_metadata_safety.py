"""Metadata recommendations must not invent licensing, and artifacts stay isolated."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "github" / "scripts"))

import meta_repo
import seo_repo


class SeoMetadataSafetyTests(unittest.TestCase):
    def test_seo_does_not_invent_open_source_topic(self):
        topics = seo_repo.build_topics("internal-tool", "inventory", [], [], "Python", "CLI Tool")
        self.assertNotIn("open-source", topics)

    def test_metadata_does_not_reintroduce_open_source_topic(self):
        seo_topics = seo_repo.build_topics("internal-tool", "inventory", [], [], "Python", "CLI Tool")
        topics = meta_repo.recommended_topics([], {"recommended_topics": seo_topics}, "Python", "CLI Tool")
        self.assertNotIn("open-source", topics)

    def test_explicit_open_source_topic_is_preserved(self):
        seo_topics = seo_repo.build_topics("example", "inventory", [], ["open-source"], "Python", "CLI Tool")
        self.assertIn("open-source", seo_topics)
        topics = meta_repo.recommended_topics(["open-source"], {"recommended_topics": seo_topics}, "Python", "CLI Tool")
        self.assertIn("open-source", topics)

    def test_full_existing_topic_set_is_not_removed_for_generated_topics(self):
        existing = [f"owner-topic-{index}" for index in range(20)]
        actual = meta_repo.recommended_topics(existing, {"recommended_topics": ["new-topic"]}, "Python", "CLI Tool")
        self.assertEqual(actual, existing)

    def test_description_and_keyword_fallbacks_do_not_claim_a_license(self):
        description = seo_repo.build_recommended_description("internal-tool", "", "inventory")
        self.assertNotIn("open source", description.lower())
        self.assertNotIn("open source", seo_repo.choose_primary_keyword([], "", "", "Unknown").lower())

    def test_supplied_open_source_description_is_preserved(self):
        description = "Example is an open source inventory tool."
        self.assertEqual(seo_repo.build_recommended_description("Example", description, "inventory"), description.rstrip("."))

    def test_offline_mutation_guards_reject_abbreviations_and_whitespace_env(self):
        scenarios = (
            (ROOT / "legends_github.py", ["--offline", "release", "--cre"], ""),
            (ROOT / "legends_github.py", ["release", "--create-release"], " true "),
            (ROOT / "github/scripts/run_headless.py", ["release", "--cre"], "true"),
        )
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repository"
            (repo / ".git").mkdir(parents=True)
            sentinel = repo / "CHANGELOG.md"
            sentinel.write_text("User-owned changelog\n", encoding="utf-8")
            for entrypoint, args, offline_value in scenarios:
                with self.subTest(entrypoint=entrypoint.name, args=args, offline=offline_value):
                    env = dict(os.environ)
                    env["LEGENDS_GITHUB_OFFLINE"] = offline_value
                    env["LEGENDS_GITHUB_HOME"] = str(Path(temporary) / "runtime")
                    result = subprocess.run(
                        [sys.executable, str(entrypoint), *args, "--path", str(repo)],
                        cwd=temporary, env=env, capture_output=True, text=True, timeout=20,
                    )
                    self.assertEqual(result.returncode, 2, result.stdout or result.stderr)
                    self.assertIn("offline", (result.stdout + result.stderr).lower())
                    self.assertEqual(sentinel.read_text(encoding="utf-8"), "User-owned changelog\n")
                    self.assertEqual({path.name for path in repo.iterdir()}, {".git", "CHANGELOG.md"})
                    self.assertFalse((Path(temporary) / "runtime").exists())

    def test_launcher_isolates_repositories_and_resolves_subdirectory_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo_a = root / "one" / "same-name"
            repo_b = root / "two" / "same-name"
            for repo in (repo_a, repo_b):
                (repo / ".git").mkdir(parents=True)
                (repo / "src").mkdir()
            artifacts = root / "artifacts"
            env = dict(os.environ)
            env["GITHUB_AUDIT_DIR"] = str(root / "ambient-cache")
            env["LEGENDS_GITHUB_HOME"] = str(root / "ambient-runtime")

            def run(target):
                result = subprocess.run(
                    [sys.executable, str(ROOT / "legends_github.py"), "--offline", "--artifacts-dir", str(artifacts),
                     "cache-status", "--path", str(target)],
                    cwd=temporary, env=env, capture_output=True, text=True, timeout=20,
                )
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
                return json.loads(result.stdout)["runtime_paths"]

            first = run(repo_a)
            nested = run(repo_a / "src")
            second = run(repo_b)
            self.assertEqual(first["repo_cache_dir"], nested["repo_cache_dir"])
            self.assertNotEqual(first["repo_cache_dir"], second["repo_cache_dir"])
            self.assertTrue(Path(first["repo_cache_dir"]).is_relative_to(artifacts))
            self.assertTrue(Path(first["github_home"]).is_relative_to(artifacts))
            self.assertFalse((root / "ambient-cache").exists())
            self.assertFalse((root / "ambient-runtime").exists())
            self.assertFalse((repo_a / ".github-audit").exists())
            self.assertFalse((repo_b / ".github-audit").exists())


if __name__ == "__main__":
    unittest.main()
