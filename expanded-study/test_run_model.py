import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import run_model as entry


class ModelEntryTests(unittest.TestCase):
    def test_pause_resume_and_changed_model_rejected(self):
        calls = []
        def api(path, payload=None):
            if path == 'tags':
                return {'models': [{'name': m, 'digest': m} for m in ['llama3.1:8b', 'mistral:7b']]}
            if path == 'version': return {'version': 'test'}
            if path == 'show': return {'details': {'quantization_level': 'Q4_K_M'}}
            calls.append(payload)
            return {'done': True, 'done_reason': 'stop', 'message': {'content': '{"answer":"UNKNOWN"}'}}
        with tempfile.TemporaryDirectory(dir=entry.core.ROOT) as tmp:
            args = ['--model', 'llama3.1:8b', '--output', tmp]
            with patch.object(entry.core.study, 'api', side_effect=api):
                entry.main(args + ['--limit', '2'])
                original = (Path(tmp)/'calls.jsonl').read_bytes()
                with self.assertRaisesRegex(ValueError, 'changed'):
                    entry.main(['--model','mistral:7b','--output',tmp])
                self.assertEqual(len(calls), 2)
                entry.main(args)
                self.assertEqual(len(calls), 300)
                self.assertTrue((Path(tmp)/'calls.jsonl').read_bytes().startswith(original))
                entry.main(args)
                self.assertEqual(len(calls), 300)
            self.assertTrue(all(c['model']=='llama3.1:8b' for c in calls))
            self.assertIn('llama3.1:8b', (Path(tmp)/'REPORT.md').read_text())
            self.assertEqual(entry.core.read(Path(tmp)/'manifest.json')['status'], 'complete')

    def test_existing_unmanaged_results_protected(self):
        with tempfile.TemporaryDirectory(dir=entry.core.ROOT) as tmp:
            (Path(tmp)/'calls.jsonl').write_text('preserve')
            with self.assertRaisesRegex(ValueError, 'not empty'):
                entry.main(['--model','phi4-mini:3.8b','--output',tmp])
            self.assertEqual((Path(tmp)/'calls.jsonl').read_text(), 'preserve')

    def test_archive_restores_only_data_and_rejects_changed_data(self):
        import hashlib
        import zipfile
        with tempfile.TemporaryDirectory(dir=entry.core.ROOT) as tmp:
            root=Path(tmp); name='expanded-study/data/example.json'; data=b'[]'
            (root/'SHA256SUMS.json').write_text(json.dumps({name:hashlib.sha256(data).hexdigest()}))
            with zipfile.ZipFile(root/'expanded300-complete.zip','w') as z:
                z.writestr(name,data); z.writestr('expanded-study/run_300.py','overwrite')
            with patch.object(entry.core,'ROOT',root):
                entry.ensure_data()
                self.assertEqual((root/'data/example.json').read_bytes(),data)
                self.assertFalse((root/'run_300.py').exists())
                (root/'data/example.json').write_text('changed')
                with self.assertRaisesRegex(ValueError,'checksum'): entry.ensure_data()

if __name__ == '__main__': unittest.main()
