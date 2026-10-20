"""Check experimental controls and structured scoring without model inference."""
import json
from pathlib import Path
import unittest
from research_run import make_context, parse, pressure
from analyze_research import metrics, paired, survival


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.items = json.loads(Path('data/multidataset_items.json').read_text())
        self.item = self.items[-1]
        self.filler = json.loads(Path('data/frozen_filler.json').read_text())

    def test_unknown_and_invalid_are_not_answers(self):
        self.assertIsNone(parse({'message': {'content': '{"answer":"UNKNOWN"}'}}, self.item['options']))
        self.assertIsNone(parse({'message': {'content': '{bad json'}}, self.item['options']))
        self.assertEqual(parse({'message': {'content': '{"answer":"A"}'}}, self.item['options']), 'A')

    def test_evidence_position_preserves_content(self):
        contexts = [make_context(self.item, self.filler, 15, pos) for pos in ('start','middle','recent')]
        self.assertTrue(all(len(x) == len(contexts[0]) for x in contexts))
        self.assertEqual(sorted(x['content'] for x in contexts[0]), sorted(x['content'] for x in contexts[2]))
        self.assertNotEqual(contexts[0], contexts[2])

    def test_no_correction_leaks_before_update(self):
        baseline = make_context(self.item, self.filler, 0, 'start')
        self.assertNotIn(self.item['correction'], json.dumps(baseline))
        self.assertIn(self.item['correction'], pressure(self.item, 'genuine', 'first'))
        self.assertNotIn(self.item['correction'], pressure(self.item, 'disagreement', 'first'))

    def test_item_counts_and_targets(self):
        self.assertEqual(len(self.items), 106)
        for item in self.items:
            self.assertNotEqual(item['correct'], item['wrong'])
            self.assertIn(item['wrong'], item['options'])

    def test_first_flip_recovery_and_censoring(self):
        branch = {'item_id':'x', 'correct':'A', 'wrong':'B', 'answers':['A','B','A',None,'B']}
        observed = metrics(branch)
        self.assertEqual(observed['exact_first_wrong'], 2)
        self.assertEqual(observed['known_adjacent_transitions'], 2)
        self.assertTrue(observed['spontaneous_recovery'])
        branch['answers'] = [None,'B','B','B','B']
        self.assertIsNone(metrics(branch)['exact_first_wrong'])
        self.assertEqual(survival([branch])[0]['at_risk'], 0)

    def test_paired_comparison_excludes_unmatched_and_unknown(self):
        a = {'item_id':'x', 'correct':'A', 'wrong':'B', 'answers':['A']*5}
        b = {**a, 'answers':['B']*5}
        result = paired([a], [b])
        self.assertEqual(result['right_minus_left'], 1)
        self.assertEqual(result['complete_pairs'], 1)
        result = paired([a], [{**b, 'answers':[None]*5}])
        self.assertEqual(result['complete_pairs'], 0)


if __name__ == '__main__':
    unittest.main()
