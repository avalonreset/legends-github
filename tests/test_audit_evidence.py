"""Offline contract fixtures: evidence is not a substitute for a runtime test."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "github" / "scripts"))

import audit_evidence as evidence
import audit_repo

STAMP = "2026-09-20T12:00:00+00:00"


def result(stdout="", returncode=0, stderr=""):
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"LEGENDS_GITHUB_OFFLINE": "0"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_no_remote_never_calls_github(self):
        with patch.object(evidence, "run_command") as run:
            remote = evidence.collect_remote(None, STAMP)
        run.assert_not_called()
        self.assertEqual(remote["metadata"]["reason"], "no_github_remote")

    def test_offline_never_probes_auth(self):
        with patch.dict(os.environ, {"LEGENDS_GITHUB_OFFLINE": "1"}), patch.object(evidence, "run_command") as run:
            remote = evidence.collect_remote("owner/repo", STAMP)
        run.assert_not_called()
        self.assertEqual(remote["metadata"]["reason"], "offline")

    def test_missing_gh_is_unavailable(self):
        with patch.object(evidence, "have_command", return_value=False):
            remote = evidence.collect_remote("owner/repo", STAMP)
        self.assertEqual(remote["metadata"]["reason"], "command_unavailable")

    def test_missing_auth_is_not_empty_metadata_and_errors_are_redacted(self):
        with patch.object(evidence, "have_command", return_value=True), patch.object(
                evidence, "run_command", return_value=result(returncode=1, stderr="secret-token-do-not-print")) as run:
            remote = evidence.collect_remote("owner/repo", STAMP)
        self.assertEqual(run.call_count, 1)
        self.assertEqual(remote["metadata"]["reason"], "authentication_unavailable")
        self.assertIsNone(remote["metadata"]["value"])
        self.assertNotIn("secret-token", json.dumps(remote))

    def test_empty_successful_releases_are_available(self):
        with patch.object(evidence, "have_command", return_value=True), patch.object(
                evidence, "run_command", side_effect=[result(), result('{"description":""}'), result("[]")]):
            remote = evidence.collect_remote("owner/repo", STAMP)
        self.assertEqual(remote["releases"]["availability"], "available")
        self.assertEqual(remote["releases"]["value"], [])

    def test_network_failure_does_not_invent_absent_releases(self):
        with patch.object(evidence, "have_command", return_value=True), patch.object(
                evidence, "run_command", side_effect=[result(), result("{}"), result(returncode=1)]):
            remote = evidence.collect_remote("owner/repo", STAMP)
        self.assertEqual(remote["metadata"]["availability"], "available")
        self.assertEqual(remote["releases"]["availability"], "unavailable")
        self.assertEqual(remote["releases"]["reason"], "command_failed")

    def test_malformed_response_is_unavailable(self):
        for value in ("not json", "[]", '{"repositoryTopics":"wrong-shape"}', '{"watchers":4}'):
            with self.subTest(value=value), patch.object(evidence, "have_command", return_value=True), patch.object(
                    evidence, "run_command", side_effect=[result(), result(value), result("[]")]):
                remote = evidence.collect_remote("owner/repo", STAMP)
            self.assertEqual(remote["metadata"]["reason"], "invalid_response")
            self.assertEqual(remote["releases"]["availability"], "available")

    def test_timeout_is_recorded(self):
        with patch.object(evidence, "have_command", return_value=True), patch.object(
                evidence, "run_command", side_effect=subprocess.TimeoutExpired("gh", 60)):
            remote = evidence.collect_remote("owner/repo", STAMP)
        self.assertEqual(remote["metadata"]["reason"], "timeout")

    def test_git_failure_is_not_empty_success(self):
        with patch.object(evidence, "have_command", return_value=True), patch.object(
                evidence, "run_command", side_effect=[result(), result(returncode=128)]):
            git = evidence.collect_git(Path.cwd(), STAMP)
        self.assertEqual(git["tags"]["value"], [])
        self.assertEqual(git["tags"]["availability"], "available")
        self.assertEqual(git["recent_commit"]["availability"], "unavailable")


class FindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = {
            "metadata": evidence.observation("github:repository", STAMP, reason="authentication_unavailable"),
            "releases": evidence.observation("github:releases", STAMP, reason="authentication_unavailable"),
        }
        self.git = {
            "tags": evidence.observation("git:tags", STAMP, []),
            "recent_commit": evidence.observation("git:commit", STAMP, "2026-09-20T00:00:00+00:00"),
        }

    def write(self, relative, content="fixture"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def package(self, payload):
        self.write("package.json", json.dumps(payload))

    def build(self):
        return evidence.build_findings(self.root, STAMP, self.remote, self.git)

    def checks(self):
        return {f["id"]: f for f in self.build()["findings"]}

    def test_contract_carries_traceable_evidence_and_verification(self):
        payload = self.build()
        self.assertEqual(payload["evidence_schema_version"], "1.0.0")
        for finding in payload["findings"]:
            with self.subTest(check=finding["id"]):
                self.assertIn(finding["status"], {"observed", "missing", "unavailable", "not_applicable"})
                for key in ("source", "collected_at", "availability", "applicability", "confidence", "impact", "effort", "verification"):
                    self.assertIn(key, finding)
                self.assertTrue(finding["evidence"])
                self.assertEqual(finding["verification"]["status"], "not_run")

    def test_unavailable_metadata_never_becomes_recommendation(self):
        payload = self.build()
        self.assertEqual(self.checks()["metadata.description"]["status"], "unavailable")
        self.assertFalse(any(a["category"] == "meta" for a in payload["prioritized_actions"]))
        counts = payload["evidence_coverage"]["counts"]
        self.assertEqual(payload["evidence_coverage"]["evaluated"], counts["observed"] + counts["missing"])

    def test_explicit_empty_metadata_is_missing_and_omitted_field_unavailable(self):
        self.remote["metadata"] = evidence.observation("github:repository", STAMP, {"description": ""})
        checks = self.checks()
        self.assertEqual(checks["metadata.description"]["status"], "missing")
        self.assertEqual(checks["metadata.topics"]["status"], "unavailable")

    def test_private_profile_excludes_public_discovery_and_license(self):
        self.remote["metadata"] = evidence.observation("github:repository", STAMP,
                                                      {"visibility": "PRIVATE", "description": "", "repositoryTopics": []})
        self.assertEqual(self.build()["repository_profile"]["audience"], "internal")
        for check in ("metadata.description", "metadata.topics", "license.present", "contributing.guidance"):
            self.assertEqual(self.checks()[check]["status"], "not_applicable")

    def test_package_private_flag_does_not_claim_github_private(self):
        self.package({"private": True})
        self.assertEqual(self.build()["repository_profile"]["audience"], "unknown")

    def test_agents_file_does_not_classify_project_as_skill(self):
        self.write("AGENTS.md")
        self.package({"name": "library", "exports": "./index.js"})
        self.assertEqual(self.build()["repository_profile"]["primary"], "library")

    def test_profiles_have_meaningful_type_signals(self):
        for name, content, expected in (("SKILL.md", "# Skill", "skill"),
                                       ("mkdocs.yml", "site_name: Manual", "documentation"),
                                       ("openapi.yaml", "openapi: 3.0.0", "service"),
                                       ("pyproject.toml", "[project.scripts]\ncmd='pkg:main'", "cli")):
            with self.subTest(expected=expected):
                self.write(name, content)
                self.assertIn(expected, self.build()["repository_profile"]["types"])
                (self.root / name).unlink()

    def test_docs_profile_excludes_software_setup_security_and_releases(self):
        self.write("mkdocs.yml", "site_name: Manual")
        for check in ("readme.installation", "security.contact", "release.version_history"):
            self.assertEqual(self.checks()[check]["status"], "not_applicable")

    def test_monorepo_scope_is_explicit(self):
        self.package({"workspaces": ["packages/*"]})
        profile = self.build()["repository_profile"]
        self.assertTrue(profile["monorepo"])
        self.assertIn("package-level audits are separate", profile["scope"])

    def test_missing_cli_target_is_high_priority_concrete_evidence(self):
        self.package({"bin": {"tool": "bin/tool.js"}})
        finding = self.checks()["package.entrypoints"]
        self.assertEqual(finding["status"], "missing")
        self.assertEqual(finding["priority"], "high")
        self.assertIn("bin/tool.js", finding["evidence"][0]["detail"])

    def test_generated_cli_target_requires_artifact_verification(self):
        self.package({"bin": "dist/cli.js", "scripts": {"build": "tsc"}})
        finding = self.checks()["package.entrypoints"]
        self.assertEqual(finding["status"], "unavailable")
        self.assertEqual(finding["evidence"][0]["reason"], "build_artifact_not_verified")
        self.assertEqual(finding["priority"], "none")

    def test_existing_cli_target_observed_without_executing(self):
        self.package({"bin": "cli.js"})
        self.write("cli.js", "throw new Error('must not execute');")
        self.assertEqual(self.checks()["package.entrypoints"]["status"], "observed")

    def test_invalid_package_is_a_concrete_high_impact_finding(self):
        self.write("package.json", "{ not valid json")
        self.assertEqual(self.checks()["package.manifest"]["priority"], "high")

    def test_outside_repo_cli_target_is_unavailable(self):
        self.package({"bin": "../outside.js"})
        self.assertEqual(self.checks()["package.entrypoints"]["status"], "unavailable")

    def test_absent_readme_precedes_optional_policies_and_no_decoration_actions(self):
        payload = self.build()
        self.assertEqual(payload["prioritized_actions"][0]["id"], "readme.present")
        rendered = json.dumps(payload["prioritized_actions"])
        self.assertNotIn("badge", rendered)
        self.assertNotIn("banner", rendered)
        self.assertNotIn("critical", rendered)

    def test_stale_cache_is_not_current_evidence(self):
        self.write(".github-audit/audit-data.json", json.dumps({"timestamp": "2001-01-01", "overall_score": 100}))
        self.write(".github-audit/repo-context.json", json.dumps({"description": "cached", "visibility": "PUBLIC"}))
        self.assertEqual(self.checks()["readme.present"]["status"], "missing")
        self.assertEqual(self.checks()["metadata.description"]["status"], "unavailable")

    def test_conflicting_local_and_remote_version_availability_keeps_positive_evidence(self):
        self.package({"bin": "cli.js"})
        self.git["tags"]["value"] = ["v1.0.0"]
        version = self.checks()["release.version_history"]
        self.assertEqual(version["status"], "observed")
        self.assertEqual(len(version["evidence"]), 2)
        self.git["tags"]["value"] = []
        self.assertEqual(self.checks()["release.version_history"]["status"], "unavailable")
        self.remote["releases"] = evidence.observation("github:releases", STAMP, [])
        self.assertEqual(self.checks()["release.version_history"]["status"], "missing")

    def test_broken_readme_link_is_evidence_but_external_links_are_not_fetched(self):
        self.write("README.md", "# Tool\n[Setup](docs/setup.md) [Web](https://example.invalid)\n")
        finding = self.checks()["readme.local_links"]
        self.assertEqual(finding["status"], "missing")
        self.assertIn("docs/setup.md", finding["evidence"][0]["detail"])
        self.write("docs/setup.md", "Setup")
        self.assertEqual(self.checks()["readme.local_links"]["status"], "observed")

    def test_readme_link_examples_in_code_blocks_are_not_false_failures(self):
        self.write("README.md", "# Tool\n```md\n[example](does-not-exist.md)\n```\n")
        self.assertNotIn("readme.local_links", self.checks())

    def test_empty_heading_is_not_setup_and_heuristics_are_labeled(self):
        self.write("README.md", "# Tool\n\n## Installation\n\n## License\nMIT\n")
        finding = self.checks()["readme.installation"]
        self.assertEqual(finding["status"], "missing")
        self.assertEqual(finding["recommendation_basis"], "hypothesis")
        self.write("README.md", "# Tool\n## Installation\n```sh\npip install tool\n```\n")
        self.assertEqual(self.checks()["readme.installation"]["status"], "observed")

    def test_large_readme_is_unavailable_not_missing(self):
        self.write("README.md", "a" * (evidence.MAX_TEXT_BYTES + 1))
        self.assertEqual(self.checks()["readme.present"]["status"], "unavailable")

    def test_custom_headings_with_real_setup_and_example_signals_are_observed(self):
        self.write("README.md", "# Tool\n## Try a report first\n```sh\npython -m pip install -r requirements.txt\npython tools/report.py --example\n```\n")
        self.assertEqual(self.checks()["readme.installation"]["status"], "observed")
        self.assertEqual(self.checks()["readme.usage"]["status"], "observed")

    def test_setup_only_block_does_not_invent_a_usage_example(self):
        self.write("README.md", "# Tool\n```sh\ngit clone https://example.invalid/tool\ncd tool\npnpm install\n```\n")
        self.assertEqual(self.checks()["readme.installation"]["status"], "observed")
        self.assertEqual(self.checks()["readme.usage"]["status"], "missing")

    def test_findings_do_not_copy_readme_body_or_read_dotenv(self):
        self.write("README.md", "# Tool\nprivate-value-not-for-report\n")
        self.write(".env", "TOKEN=never-read-this")
        payload = self.build()
        self.assertNotIn("private-value-not-for-report", json.dumps(payload))
        self.assertNotIn("never-read-this", json.dumps(payload))
        self.assertIn("sha256", self.checks()["readme.present"]["evidence"][0])

    def test_run_audit_preserves_legacy_outputs_and_writes_evidence_artifact(self):
        self.write("README.md", "# Fixture\nA minimal repository.\n")
        self.write(".gitignore", "user-work/\n")
        with patch.object(audit_repo, "repo_slug_from_git", return_value=None), patch.object(
                audit_repo, "collect_remote", return_value=self.remote), patch.object(
                audit_repo, "collect_git", return_value=self.git):
            bundle = audit_repo.run_audit(self.root)
        for key in ("scores", "weights", "overall_score", "checks", "action_items", "file_existence", "releases", "tags"):
            self.assertIn(key, bundle.audit_data)
        expected_readme = audit_repo.score_readme("# Fixture\nA minimal repository.\n", self.root)[0]
        self.assertEqual(bundle.audit_data["scores"]["readme"], expected_readme)
        self.assertIn("Legacy checklist (compatibility only)", bundle.report_markdown)
        self.assertNotIn("[critical]", bundle.report_markdown)
        self.assertNotIn("Add version, license, or CI badges", bundle.action_plan_markdown)
        with tempfile.TemporaryDirectory() as artifacts, patch.dict(os.environ, {"GITHUB_AUDIT_DIR": artifacts}):
            paths = audit_repo.write_audit_artifacts(self.root, bundle)
            payload = json.loads(Path(paths["findings_json"]).read_text(encoding="utf-8"))
            self.assertEqual(payload["evidence_schema_version"], "1.0.0")
            self.assertEqual(payload["findings"], bundle.audit_data["findings"])
        self.assertEqual((self.root / ".gitignore").read_text(encoding="utf-8"), "user-work/\n")
        self.assertFalse((self.root / ".github-audit").exists())


if __name__ == "__main__":
    unittest.main()
