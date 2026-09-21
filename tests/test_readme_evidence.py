"""README drafts must preserve source material and avoid fabricated usage claims."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "github" / "scripts"))
import readme_repo


class ReadmeEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)

    def snapshot(self, readme="", repo_type="Skill/Plugin"):
        return {
            "repo_root": str(self.repo), "repo": "example", "repo_name": "Different Project",
            "repo_type": repo_type, "current_readme": readme, "license_label": "Not established",
            "docs_link": "", "banner_path": None,
            "seo_data": {"primary_keyword": {"keyword": "inventory"}, "secondary_keywords": [],
                         "paa_questions": ["What is its architecture?"]},
        }

    def test_missing_evidence_creates_draft_requirements_without_fabricated_sections(self):
        readme, sections, _ = readme_repo.build_readme_content(self.snapshot())
        self.assertIn("**Draft requirement:**", readme)
        for absent in ("Commands", "Architecture", "Frequently Asked Questions", "Examples", "License"):
            self.assertNotIn(absent, sections)
        for invented in ("cleaner GitHub experience", "small set of entrypoints", "answers this in the sections above",
                         "| Audit |", "| SEO |", "| Meta |", "~/.codex", "python main.py", "OWNER/REPO"):
            self.assertNotIn(invented, readme)

    def test_manifest_name_does_not_prove_registry_publication_or_import_name(self):
        (self.repo / "package.json").write_text(json.dumps({"name": "unpublished-app", "private": True, "scripts": {"test": "exit 0"}}))
        (self.repo / "pyproject.toml").write_text('[project]\nname = "distribution-not-module"\n')
        (self.repo / "Cargo.toml").write_text('[package]\nname = "unpublished-rust"\n')
        (self.repo / "Dockerfile").write_text("FROM scratch\n")
        for repo_type in ("CLI Tool", "Library/Package", "Application", "Skill/Plugin"):
            with self.subTest(repo_type=repo_type):
                install = readme_repo.install_snippet(self.repo, repo_type, "unknown-command")
                usage = readme_repo.quick_start_snippet(self.repo, repo_type, "unknown-command")
                self.assertNotIn("```", install + usage)
                self.assertIn("Draft requirement", install)
                self.assertIn("Draft requirement", usage)

    def test_existing_sections_title_and_custom_guidance_are_preserved(self):
        source = """# Actual Project

Tracks local inventory changes.

## Installation

```sh
./setup-local --verified
```

## Commands

Run `./inventory count` to count items.

## Architecture

The inventory daemon stores append-only records in SQLite.

## Frequently Asked Questions

### Can it run offline?
Yes, all records stay local.

## Recovery Procedure

Restore the latest verified inventory snapshot.
"""
        readme, sections, _ = readme_repo.build_readme_content(self.snapshot(source))
        self.assertTrue(readme.startswith("# Actual Project\n"))
        for body in readme_repo.extract_sections(source).values():
            self.assertIn(body, readme)
        self.assertIn("Recovery Procedure", sections)
        self.assertEqual(readme.count("./setup-local --verified"), 1)
        self.assertIn("Tracks local inventory changes.", readme)

    def test_configuration_and_licensing_do_not_invent_required_files(self):
        self.assertEqual(readme_repo.configuration_snippet(self.repo), "")
        self.assertEqual(readme_repo.license_type(self.repo, {}, {}), "Not established")
        badges = readme_repo.build_badges(self.repo, "owner/project", "Not established")
        self.assertFalse(any("(LICENSE)" in badge for badge in badges))
        (self.repo / ".env.example").write_text("OPTIONAL_SETTING=\n")
        configuration = readme_repo.configuration_snippet(self.repo)
        self.assertIn(".env.example", configuration)
        self.assertNotIn(".env.local", configuration)


if __name__ == "__main__":
    unittest.main()
