"""Evidence imports must preserve unknowns and reject mismatched research."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "github" / "scripts"))
from seo_research import import_research


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "demand.json"
        self.payload = {"status_code": 20000, "cost": 0.01, "tasks": [{
            "status_code": 20000, "path": ["v3", "dataforseo_labs", "google", "keyword_overview", "live"],
            "result": [{"location_code": 2840, "language_code": "en", "items": [
                {"keyword": "rank checker", "keyword_info": {"search_volume": 0}},
                {"keyword": "unknown"}]}]}]}

    def save(self):
        self.path.write_text(json.dumps(self.payload), encoding="utf-8-sig")

    def test_zero_and_missing_are_distinct(self):
        self.save()
        result = import_research(self.path, "rank checker")
        self.assertEqual(result["primary_keyword"]["volume"], 0)
        self.assertIsNone(result["keyword_research"][1]["volume"])
        self.assertEqual(result["serp_observations"], [])

    def test_unknown_primary_is_rejected(self):
        self.save()
        with self.assertRaises(ValueError):
            import_research(self.path, "unreturned keyword")

    def test_failed_task_is_rejected(self):
        self.payload["tasks"][0]["status_code"] = 40000
        self.save()
        with self.assertRaises(ValueError):
            import_research(self.path, "rank checker")

    def test_mixed_locales_are_rejected(self):
        self.payload["tasks"][0]["result"].append({"location_code": 2826, "language_code": "en"})
        self.save()
        with self.assertRaises(ValueError):
            import_research(self.path, "rank checker")

    def test_serp_locale_is_checked(self):
        self.save()
        serp = Path(self.temp.name) / "serp.json"
        serp.write_text(json.dumps({"status_code": 20000, "tasks": [{"status_code": 20000,
            "path": ["v3", "serp", "google", "organic", "live", "advanced"],
            "result": [{"location_code": 2826, "language_code": "en"}]}]}))
        with self.assertRaises(ValueError):
            import_research(self.path, "rank checker", [serp])

    def test_run_seo_with_imported_research_recomputes_topics_and_serp_rank(self):
        import seo_repo
        self.payload["tasks"][0]["result"][0]["items"] = [
            {"keyword": "github seo", "keyword_info": {"search_volume": 90, "cpc": 18.28}},
            {"keyword": "ai coding agent", "keyword_info": {"search_volume": 8100, "cpc": 26.39}},
            {"keyword": "open source seo tools", "keyword_info": {"search_volume": 110, "cpc": 9.93}},
        ]
        self.save()
        serp = Path(self.temp.name) / "serp.json"
        serp.write_text(json.dumps({
            "status_code": 20000,
            "cost": 0.002,
            "tasks": [{
                "status_code": 20000,
                "path": ["v3", "serp", "google", "organic", "live", "advanced"],
                "result": [{
                    "keyword": "github seo",
                    "location_code": 2840,
                    "language_code": "en",
                    "items_count": 2,
                    "items": [
                        {"type": "organic", "rank_group": 1, "title": "Guide", "url": "https://example.com/guide"},
                        {"type": "organic", "rank_group": 3, "title": "Repo", "url": "https://github.com/avalonreset/legends-github"},
                    ],
                }],
            }],
        }), encoding="utf-8")
        repo = Path(self.temp.name) / "repo"
        repo.mkdir()
        (repo / "README.md").write_text("# legends-github\n\nOpen source GitHub SEO toolkit.\n", encoding="utf-8")
        bundle = seo_repo.run_seo(repo, keyword_data=self.path, primary_keyword_choice="github seo", serp_data=[serp])
        self.assertEqual(bundle.seo_data["analysis_mode"], "imported-dataforseo-evidence")
        self.assertEqual(bundle.seo_data["secondary_keywords"][0]["keyword"], "ai coding agent")
        self.assertIn("github-seo", bundle.seo_data["recommended_topics"])
        self.assertIn("ai-coding-agent", bundle.seo_data["recommended_topics"])
        self.assertTrue(bundle.seo_data["github_in_serp"])
        self.assertEqual(bundle.seo_data["github_serp_position"], 3)
