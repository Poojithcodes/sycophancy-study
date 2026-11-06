import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import run_300 as run
import prepare_300 as prep

class ExpandedTests(unittest.TestCase):
    def test_dataset_disjoint_and_counts(self):
        from collections import Counter
        items=run.read(run.ITEMS)
        pilot=run.read(prep.DATA/'multidataset_items.json')
        self.assertEqual(Counter(i['dataset'] for i in items),{'mmlu_5subjects':150,'truthfulqa_binary':100,'synthetic_evidence':50})
        self.assertFalse({prep.norm(i['question']) for i in items}&{prep.norm(i['question']) for i in pilot})
        self.assertEqual(len({i['id'] for i in items}),300)
        self.assertEqual(len({prep.norm(i['question']) for i in items}),300)
        self.assertEqual(run.sha(run.ITEMS),run.read(prep.DATA/'expanded300_manifest.json')['items_sha256'])
    def test_genuine_correction_not_in_baseline(self):
        for i in run.read(run.ITEMS):
            messages=run.study.make_context(i,[],0,'start')
            self.assertNotIn(i.get('correction','IMPOSSIBLE_SENTINEL'),[m['content'] for m in messages])
    def test_mmlu_preserves_original_choice_order(self):
        import csv
        for i in run.read(run.ITEMS):
            if i['dataset']!='mmlu_5subjects': continue
            path=prep.DATA/'sources'/f"{i['category']}.csv"
            with path.open(encoding='utf-8',newline='') as f: row=list(csv.reader(f))[i['source_row']]
            self.assertEqual(list(i['options'].values()),row[1:5]); self.assertEqual(i['correct'],row[5])
    def test_mid_branch_resume_keeps_original_responses(self):
        item=next(i for i in run.read(run.ITEMS) if i['dataset']=='synthetic_evidence')
        def fake(path,payload):
            last=payload['messages'][-1]['content']
            answer=item['wrong'] if last.startswith('I believe') or 'official correction' in last else item['correct']
            return {'done':True,'done_reason':'stop','prompt_eval_count':100,'model':'fake','message':{'content':json.dumps({'answer':answer})}}
        with tempfile.TemporaryDirectory(dir=run.ROOT) as td:
            root=Path(td); complete=root/'complete'; resumed=root/'resumed'
            with patch.object(run.study,'api',side_effect=fake): run.evaluate(complete,'fake',[item],{},None)
            lines=(complete/'calls.jsonl').read_bytes().splitlines(keepends=True)
            resumed.mkdir(); (resumed/'calls.jsonl').write_bytes(b''.join(lines[:3])+b'{"partial":')
            with patch.object(run.study,'api',side_effect=fake): run.evaluate(resumed,'fake',[item],{},None)
            self.assertEqual((complete/'calls.jsonl').read_bytes(),(resumed/'calls.jsonl').read_bytes())
            self.assertEqual((complete/'records.jsonl').read_bytes(),(resumed/'records.jsonl').read_bytes())
            self.assertEqual(run.read(complete/'analysis.json'),run.read(resumed/'analysis.json'))
            with patch.object(run.study,'api',side_effect=AssertionError('Must not infer again')):
                run.evaluate(resumed,'fake',[item],{},None)
    def test_changed_prompt_stops_before_inference(self):
        item=run.read(run.ITEMS)[0]
        with tempfile.TemporaryDirectory(dir=run.ROOT) as td:
            folder=Path(td)
            (folder/'calls.jsonl').write_text(json.dumps({'call_id':1,'item_id':item['id'],'tag':{},'request':{}})+'\n')
            runner=run.Runner(folder,'fake')
            try:
                with patch.object(run.study,'api',side_effect=AssertionError('No inference')):
                    with self.assertRaisesRegex(ValueError,'mismatch'): runner.ask([],item,{})
            finally: runner.log.close(); runner.records.close()
    def test_unknown_is_valid_abstention(self):
        item=run.read(run.ITEMS)[0]
        raw={'done':True,'done_reason':'stop','message':{'content':'{"answer":"UNKNOWN"}'}}
        with tempfile.TemporaryDirectory(dir=run.ROOT) as td:
            runner=run.Runner(Path(td),'fake')
            try:
                with patch.object(run.study,'api',return_value=raw): self.assertIsNone(runner.ask([],item,{})['answer'])
            finally: runner.log.close();runner.records.close()
    def test_corrupt_interior_log_rejected(self):
        with tempfile.TemporaryDirectory(dir=run.ROOT) as td:
            path=Path(td)/'calls.jsonl'; path.write_bytes(b'bad\n{}\n')
            with self.assertRaises(ValueError): run.load_calls(path)

if __name__=='__main__': unittest.main()

