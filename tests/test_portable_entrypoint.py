import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class PortableEntrypointTests(unittest.TestCase):
    def test_help_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run([sys.executable, str(ROOT / "legends_github.py"), "--help"], cwd=cwd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("cache-status", result.stdout)

    def test_workflow_help_routes_to_existing_contract(self):
        for command in ("verify", "audit", "discover", "seo", "meta", "community", "legal", "readme", "release", "empire", "cache-status"):
            with self.subTest(command=command):
                result = subprocess.run([sys.executable, str(ROOT / "legends_github.py"), command, "--help"], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("--path", result.stdout)

    def test_unknown_operation_fails(self):
        result = subprocess.run([sys.executable, str(ROOT / "legends_github.py"), "not-a-workflow"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)

if __name__ == "__main__":
    unittest.main()
