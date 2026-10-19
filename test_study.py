"""Offline checks using simulated responses, not experimental evidence."""
import json
from pathlib import Path
import unittest
from study import extract_answer, run_item, summarize, validate


class StudyTests(unittest.TestCase):
    def test_parser_ambiguity(self):
        self.assertEqual(extract_answer('Explanation.\nFinal answer: B'), 'B')
        self.assertIsNone(extract_answer('Final answer: A\nFinal answer: B'))
        self.assertIsNone(extract_answer('Maybe A or B'))

    def test_branch_isolation_and_metrics(self):
        item = json.loads(Path('data/demo_items.json').read_text())[0]
        requests = []
        def fake(messages, config):
            requests.append(json.loads(json.dumps(messages)))
            answer = 'B' if 'I disagree' in messages[-1]['content'] else 'A'
            return 'Final answer: ' + answer, {'simulated': True}
        record = run_item(item, {'rounds': 2}, fake)
        self.assertEqual([len(m) for m in requests], [2, 4, 6, 4, 6, 4, 6])
        self.assertNotIn('I disagree', json.dumps(requests[-1]))
        stats = summarize([record])['conditions']
        self.assertEqual(stats['control']['observed_switch_rate'], 0)
        self.assertEqual(stats['disagreement']['observed_switch_rate'], 1)

    def test_incorrect_baseline_is_excluded(self):
        item = json.loads(Path('data/demo_items.json').read_text())[0]
        record = run_item(item, {'rounds': 5}, lambda m, c: ('Final answer: B', {}))
        self.assertFalse(record['eligible'])
        self.assertEqual(record['branches'], {})

    def test_invalid_key_rejected(self):
        items = json.loads(Path('data/demo_items.json').read_text())
        items[0]['wrong'] = items[0]['correct']
        with self.assertRaises(ValueError):
            validate(items)


if __name__ == '__main__':
    unittest.main()
