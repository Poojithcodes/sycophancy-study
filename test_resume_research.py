import copy
import io
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
import research_run as study
from resume_research import Replay, load_calls, digest

class ResumeTests(unittest.TestCase):
    def test_replay_then_live(self):
        live = Mock(return_value={'new': True})
        saved = {'request': {'model': 'x'}, 'response': {'old': True}}
        replay = Replay([saved], live)
        self.assertEqual(replay('chat', {'model': 'x'}), {'old': True})
        live.assert_not_called()
        self.assertEqual(replay('chat', {'model': 'x'}), {'new': True})
        live.assert_called_once()

    def test_mismatch_stops(self):
        live = Mock()
        replay = Replay([{'request': {'model': 'old'}, 'response': {}}], live)
        with self.assertRaises(ValueError):
            replay('chat', {'model': 'new'})
        live.assert_not_called()

    def test_truncated_tail_and_corruption(self):
        row = {'call_id': 1, 'request': {}, 'response': {'message': {'content': '{}'}}}
        raw = (json.dumps(row) + '\n').encode()
        with patch.object(Path, 'read_bytes', return_value=raw + b'{"call_id":'):
            self.assertEqual(load_calls(Path('unused')), [row])
        with patch.object(Path, 'read_bytes', return_value=b'bad\n' + raw):
            with self.assertRaises(ValueError):
                load_calls(Path('unused'))

    def test_model_digest(self):
        self.assertEqual(digest({'models': [{'name': 'x', 'digest': 'abc'}]}, 'x'), 'abc')
        with self.assertRaises(ValueError):
            digest({'models': []}, 'x')

    def test_mid_branch_resume_matches_uninterrupted(self):
        item = {'id': 'x', 'dataset': 'mmlu', 'correct': 'A', 'wrong': 'B',
                'options': {'A': 'yes', 'B': 'no'}}
        history = [{'role': 'user', 'content': 'Question'}]
        def run(api):
            logs, records = io.StringIO(), io.StringIO()
            with patch.object(Path, 'open', side_effect=[logs, records]), patch.object(study, 'api', api):
                runner = study.Runner(Path('unused'), 'qwen2.5:7b')
                runner.branch(item, copy.deepcopy(history), 0, 'none', 'disagreement', 'first')
            return logs.getvalue(), records.getvalue()
        def live(path, payload):
            return {'message': {'content': json.dumps({'answer': 'B'})}}
        full_log, full_records = run(live)
        saved = [json.loads(line) for line in full_log.splitlines()][:2]
        remaining = Mock(side_effect=live)
        resumed_log, resumed_records = run(Replay(saved, remaining))
        self.assertEqual(resumed_log, full_log)
        self.assertEqual(resumed_records, full_records)
        self.assertEqual(remaining.call_count, 3)

if __name__ == '__main__':
    unittest.main()
