"""Prove paid acquisition is bounded and never implicit."""
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "github" / "scripts"))
import research_dataforseo as research


class CollectionTests(TestCase):
    def test_default_is_offline_estimate_without_kit(self):
        with patch.dict(sys.modules, {"legends_dataforseo": None}):
            result = research.collect_research(Path('.'), keywords=['a', 'b'], serp_keywords=['a'])
        self.assertEqual(result['status'], 'estimate')
        self.assertEqual(result['estimated_cost_usd'], 0.01424)

    def test_no_http_with_insufficient_budget_or_offline(self):
        request = Mock()
        with patch.dict(sys.modules, {"legends_dataforseo": SimpleNamespace(api_request=request)}):
            with patch.dict(os.environ, {"LEGENDS_GITHUB_OFFLINE": "1"}):
                with self.assertRaisesRegex(ValueError, 'offline'):
                    research.collect_research(Path('.'), keywords=['a'], execute=True, ceiling=1)
            with patch.dict(os.environ, {"LEGENDS_GITHUB_OFFLINE": "0"}):
                with self.assertRaisesRegex(ValueError, 'exceeds'):
                    research.collect_research(Path('.'), keywords=['a'], execute=True, ceiling=0)
        request.assert_not_called()

    def test_failed_task_retained_and_no_next_call(self):
        request = Mock(return_value={'status_code': 20000, 'cost': .01212,
                                    'tasks': [{'status_code': 40000}]})
        with tempfile.TemporaryDirectory() as tmp, patch.object(research, 'repo_output_dir', return_value=Path(tmp)), \
             patch.dict(os.environ, {"LEGENDS_GITHUB_OFFLINE": "0"}), \
             patch.dict(sys.modules, {"legends_dataforseo": SimpleNamespace(api_request=request)}):
            with self.assertRaisesRegex(ValueError, 'failed'):
                research.collect_research(Path('.'), keywords=['a'], serp_keywords=['a'], execute=True, ceiling=.02)
            receipt = json.loads(next(Path(tmp).glob('*/receipt.json')).read_text())
            self.assertEqual(receipt['status'], 'partial')
            self.assertEqual(receipt['reported_cost_usd'], .01212)
            self.assertTrue(next(Path(tmp).glob('*/demand.json')).is_file())
        request.assert_called_once()

    def test_exports_and_receipt_on_success(self):
        request = Mock(side_effect=[{'status_code': 20000, 'cost': .01212, 'tasks': [{'status_code': 20000}]},
                                    {'status_code': 20000, 'cost': .002, 'tasks': [{'status_code': 20000}]}])
        with tempfile.TemporaryDirectory() as tmp, patch.object(research, 'repo_output_dir', return_value=Path(tmp)), \
             patch.dict(os.environ, {"LEGENDS_GITHUB_OFFLINE": "0"}), \
             patch.dict(sys.modules, {"legends_dataforseo": SimpleNamespace(api_request=request)}):
            result = research.collect_research(Path('.'), keywords=['a'], serp_keywords=['a'], execute=True, ceiling=.02)
            self.assertEqual(result['status'], 'collected')
            self.assertEqual(result['reported_cost_usd'], .01412)
            self.assertTrue(Path(result['serp_data'][0]).is_file())
        self.assertEqual(request.call_count, 2)
        self.assertAlmostEqual(request.call_args.kwargs['max_cost_usd'], .00788)

    def test_authorized_no_ceiling_retains_cost_and_finite_calls(self):
        request = Mock(return_value={'status_code': 20000, 'cost': 2.0, 'tasks': [{'status_code': 20000}]})
        with tempfile.TemporaryDirectory() as tmp, patch.object(research, 'repo_output_dir', return_value=Path(tmp)), \
             patch.dict(os.environ, {'LEGENDS_GITHUB_OFFLINE': '0'}), \
             patch.dict(sys.modules, {'legends_dataforseo': SimpleNamespace(api_request=request)}):
            result = research.collect_research(Path('.'), keywords=['a'], execute=True, no_cost_ceiling=True)
            self.assertEqual(result['reported_cost_usd'], 2.0)
            self.assertIsNone(result['cost_ceiling_usd'])
        request.assert_called_once()
        self.assertIsNone(request.call_args.kwargs['max_cost_usd'])

    def test_no_ceiling_cannot_be_combined_with_budget(self):
        with self.assertRaisesRegex(ValueError, 'not both'):
            research.collect_research(Path('.'), keywords=['a'], ceiling=1, no_cost_ceiling=True)

    def test_no_ceiling_does_not_bypass_offline(self):
        with patch.dict(os.environ, {'LEGENDS_GITHUB_OFFLINE': '1'}):
            with self.assertRaisesRegex(ValueError, 'offline'):
                research.collect_research(Path('.'), keywords=['a'], execute=True, no_cost_ceiling=True)
