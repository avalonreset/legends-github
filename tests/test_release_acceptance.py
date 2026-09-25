"""Regressions for the concrete blockers found in the GeoGrid review."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'github/scripts'))
import community_repo
import legal_repo
import meta_repo
import release_repo


class ReleaseAcceptanceTests(unittest.TestCase):
    def test_ci_follows_nested_package_scripts_without_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow = root / 'ci.yml'
            workflow.write_text('run: pnpm check')
            (root / 'package.json').write_text(json.dumps({'scripts': {
                'check': 'pnpm run proof', 'proof': 'node --test && pnpm check'}}))
            self.assertEqual(community_repo.quality_ci([workflow], root),
                             ('good', 'Keep the current CI workflow.'))
            workflow.write_text('run: ./custom-validation.sh')
            self.assertIn('manual coverage review', community_repo.quality_ci([workflow], root)[1])

    def test_ordinary_extends_is_not_provenance(self):
        self.assertEqual(legal_repo.detect_upstream_signals('Visibility extends across the map.', ''), [])
        self.assertTrue(legal_repo.detect_upstream_signals('This is a fork of upstream.', ''))

    def test_changelog_accepts_bare_and_bracketed_versions(self):
        for heading in ('## 0.3.0 - 2026-09-20', '## [0.3.0] - 2026-09-20'):
            self.assertEqual(release_repo.changelog_versions(heading)[0]['version'], '0.3.0')

    def test_unavailable_metadata_cannot_authorize_remote_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = dict(repo='owner/project', repo_root=str(root), repo_name='project',
                            repo_type='Application', metadata={}, cached_context={},
                            seo_data={'recommended_description': 'A useful application'},
                            languages={}, social_preview_asset=None, primary_language='')
            with patch.object(meta_repo, 'build_snapshot', return_value=snapshot):
                payload = meta_repo.build_meta_payload(root)
            self.assertEqual(payload['current']['availability'], 'unavailable')
            self.assertFalse(any(c['status'] == 'ready' for c in payload['commands']))
            with patch.object(meta_repo, 'run_command') as execute:
                with self.assertRaisesRegex(RuntimeError, 'metadata unavailable'):
                    meta_repo.apply_meta_plan(payload)
                execute.assert_not_called()

    def test_no_per_host_installers_router_native(self):
        for name in ('social-preview-sop.md', 'legends-readme-style.md'):
            self.assertTrue((ROOT / 'github/references' / name).is_file())
        self.assertTrue((ROOT / 'github/scripts/render_social_preview.py').is_file())
        for installer in ('install.ps1', 'install.sh',
                          'install-codex.ps1', 'install-codex.sh'):
            self.assertFalse((ROOT / installer).exists())
