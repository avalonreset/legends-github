"""Local discovery planning contracts, including boundaries and evidence gaps."""

import json
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "github" / "scripts"))

from discovery_repo import MAX_DISCOVERED_FILES, MAX_TEXT_BYTES, run_discovery, write_discovery_artifacts


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        self.root.mkdir()

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_library_plan_is_deterministic_read_only_and_uses_evidence(self):
        self.write("README.md", "# Example\n\n## Installation\nUse the package.\n## Usage\nSee examples.\n")
        self.write("pyproject.toml", '[project]\nname = "example"\n')
        self.write("docs/guide.md", "# Guide\n## Limitations\nSupported tasks only.\n")
        self.write("examples/start.py", "raise RuntimeError('must never run')\n")
        self.write("CHANGELOG.md", "# Releases\nInitial example.\n")
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        with patch.object(socket, "create_connection", side_effect=AssertionError("network")), patch.object(
            subprocess, "run", side_effect=AssertionError("process")
        ):
            plan = run_discovery(self.root, "Python developers", "data transformation")
            self.assertEqual(plan, run_discovery(self.root, "Python developers", "data transformation"))
        json.dumps(plan)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        self.assertIn("library", plan["repository_profile"]["types"])
        rows = {row["id"]: row for row in plan["evidence_inventory"]}
        self.assertEqual(rows["file:examples/start.py"]["inspection"], "filename_only")
        self.assertIn({"name": "setup", "line": 3}, rows["file:README.md"]["signals"])
        for experiment in plan["experiments"]:
            self.assertEqual(experiment["basis"], "hypothesis")
            self.assertTrue(experiment["brief"]["proof_required"])
            self.assertTrue(set(experiment["evidence_refs"]) <= rows.keys())
        self.assertEqual(plan["comparison_matrix"]["status"], "not_requested")

    def test_blank_context_is_explicit_and_has_no_invented_competitors(self):
        self.write("README.md", "# App\nAlternative to Imaginary Competitor.\n")
        plan = run_discovery(self.root)
        self.assertEqual(plan["context"]["missing"], ["audience", "category"])
        self.assertEqual(plan["experiments"][0]["id"], "context")
        self.assertEqual(plan["context"]["competitors"], [])
        self.assertEqual(plan["metadata"]["topic_candidates"], [])
        self.assertNotIn("Imaginary Competitor", json.dumps(plan))
        self.assertNotIn("score", plan)

    def test_documentation_brief_uses_worked_navigation_not_installation(self):
        self.write("README.md", "# Handbook\n## Contents\nStart in docs.\n")
        self.write("mkdocs.yml", "site_name: Handbook\n")
        self.write("docs/first.md", "# First task\nA worked answer.\n")
        plan = run_discovery(self.root, "readers", "research handbook")
        self.assertEqual(plan["repository_profile"]["types"], ["documentation"])
        example = next(item for item in plan["experiments"] if item["id"] == "example")
        outline = " ".join(example["brief"]["outline"])
        self.assertIn("navigation steps", outline)
        self.assertNotIn("task commands", outline)

    def test_private_manifest_and_internal_audience_scope_distribution(self):
        for package, audience in (({"private": True}, "developers"), ({}, "internal analysts")):
            with self.subTest(package=package, audience=audience):
                self.write("package.json", json.dumps(package))
                plan = run_discovery(self.root, audience, "sensitive project")
                self.assertEqual(plan["repository_profile"]["distribution_scope"], "internal")
                self.assertEqual(plan["repository_profile"]["visibility"], "unknown")
                self.assertEqual(plan["metadata"]["topic_candidates"], [])
                distribution = next(item for item in plan["experiments"] if item["id"] == "distribution")
                self.assertEqual(distribution["brief"]["destination"], "Internal team knowledge channel draft")

    def test_comparison_cells_are_unknown_and_cost_claims_require_proof(self):
        self.write("README.md", "# App\n## API pricing\nAn unverified price is $12345.67.\n")
        plan = run_discovery(self.root, "analysts", "maps", ["Competitor A", " competitor a ", "Competitor B"])
        self.assertEqual(plan["context"]["competitors"], ["Competitor A", "Competitor B"])
        self.assertIn("costs", [item["id"] for item in plan["experiments"]])
        self.assertNotIn("12345.67", json.dumps(plan))
        for row in plan["comparison_matrix"]["rows"]:
            for cell in row["cells"]:
                self.assertIsNone(cell["claim"])
                self.assertIsNone(cell["checked_at"])
                self.assertEqual(cell["official_sources"], [])
                self.assertEqual(cell["status"], "unverified")
        self.assertEqual(plan["metadata"]["topic_candidates"][0]["topic"], "maps")

    def test_metrics_unavailability_is_not_zero_or_cached_evidence(self):
        self.write(".github-audit/seo-data.json", '{"traffic": 99999}')
        plan = run_discovery(self.root)
        baseline = plan["metrics_baseline"]
        self.assertEqual(baseline["availability"], "unavailable")
        self.assertTrue(all(value is None for value in baseline["traffic_14_days"].values()))
        self.assertIsNone(baseline["release_assets"])
        self.assertIsNone(baseline["observed_at_utc"])
        self.assertNotIn("99999", json.dumps(plan))
        metrics = {item["metric"] for item in baseline["manual_collection"]}
        self.assertEqual(metrics, {"views", "clones", "referrers", "popular_paths", "release_assets"})

    def test_bounded_inventory_does_not_copy_content_or_read_secret_trees(self):
        self.write("README.md", "# Example\nPRIVATE_CONTENT_SENTINEL\n")
        self.write(".env", "TOKEN=PRIVATE_ENV_SENTINEL")
        self.write("docs/credentials.md", "PRIVATE_CREDENTIAL_SENTINEL")
        self.write("docs/.hidden.md", "PRIVATE_HIDDEN_SENTINEL")
        self.write("docs/secrets/data.md", "PRIVATE_SECRET_SENTINEL")
        self.write("docs/large.md", "x" * (MAX_TEXT_BYTES + 1))
        self.write("src/private.md", "PRIVATE_SOURCE_SENTINEL")
        for i in range(MAX_DISCOVERED_FILES + 5):
            self.write(f"examples/{i:03}.py", "raise RuntimeError('do not execute')")
        plan = run_discovery(self.root)
        self.assertTrue(plan["coverage"]["truncated"])
        self.assertLessEqual(plan["coverage"]["discovered_files"], MAX_DISCOVERED_FILES)
        self.assertNotIn("PRIVATE_", json.dumps(plan))
        paths = {row["path"] for row in plan["evidence_inventory"]}
        self.assertNotIn("docs/credentials.md", paths)
        self.assertNotIn("docs/.hidden.md", paths)
        self.assertNotIn("src/private.md", paths)
        large = next(row for row in plan["evidence_inventory"] if row["path"] == "docs/large.md")
        self.assertEqual(large["reason"], "text_size_limit")

    def test_symlinked_docs_do_not_escape_repository(self):
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (outside / "outside.md").write_text("OUTSIDE_SENTINEL", encoding="utf-8")
        try:
            (self.root / "docs").symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"Symlink unavailable: {type(error).__name__}")
        plan = run_discovery(self.root)
        self.assertNotIn("OUTSIDE_SENTINEL", json.dumps(plan))
        self.assertFalse(any(row["kind"] == "documentation" for row in plan["evidence_inventory"]))
        self.assertTrue(plan["coverage"]["notes"])

    def test_malformed_manifest_and_missing_readme_remain_usable(self):
        self.write("package.json", "[]")
        plan = run_discovery(self.root)
        self.assertEqual(plan["evidence_inventory"][0]["availability"], "missing")
        self.assertEqual(plan["repository_profile"]["visibility"], "unknown")
        self.write("package.json", "{bad json")
        json.dumps(run_discovery(self.root))

    def test_invalid_context_is_rejected_without_writes(self):
        for context in ({"audience": "x" * 241}, {"competitors": "not-a-list"},
                        {"competitors": ["x"] * 11}, {"competitors": [None]}):
            with self.subTest(context=context), self.assertRaises(ValueError):
                run_discovery(self.root, **context)
        with self.assertRaises(ValueError):
            run_discovery(self.root / "missing")
        self.assertEqual(list(self.root.iterdir()), [])

    def test_writer_respects_cache_override_and_preserves_previous_runs(self):
        self.write("README.md", "# Project\n")
        self.write(".gitignore", "user-work\n")
        plan = run_discovery(self.root, "developers", "testing", ["Example alternative"])
        cache = Path(self.temporary.name) / "external-cache"
        with patch.dict(os.environ, {"GITHUB_AUDIT_DIR": str(cache)}):
            first = write_discovery_artifacts(self.root, plan)
            second = write_discovery_artifacts(self.root, plan)
        self.assertNotEqual(first["output_dir"], second["output_dir"])
        for key, value in first.items():
            self.assertTrue(Path(value).exists(), key)
            self.assertTrue(Path(value).is_relative_to(cache))
        self.assertEqual(json.loads(Path(first["plan_json"]).read_text(encoding="utf-8")), plan)
        report = Path(first["report"]).read_text(encoding="utf-8")
        self.assertIn("Alternatives evidence matrix", report)
        self.assertIn("Example alternative", report)
        self.assertIn("Proof required:", report)
        self.assertEqual((self.root / ".gitignore").read_text(), "user-work\n")
        self.assertFalse((self.root / ".github-audit").exists())
        wrong = dict(plan, repo_root=str(self.root / "wrong"))
        with self.assertRaises(ValueError):
            write_discovery_artifacts(self.root, wrong)


if __name__ == "__main__":
    unittest.main()
