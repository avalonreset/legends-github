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
