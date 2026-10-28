"""Paired single-turn format diagnostic; never overwrite the original pilot."""
import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from research_run import api


def decode(content, labels, plain=False):
    try:
        answer = content.strip() if plain else json.loads(content)['answer']
    except (ValueError, KeyError, TypeError):
        return 'INVALID'
    return answer if answer in [*labels, 'UNKNOWN'] else 'INVALID'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    folder = Path(args.output)
    folder.mkdir(parents=True, exist_ok=False)
    source = Path('experiments/multidataset-qwen3b-001/calls.jsonl.gz')
    items = json.loads(Path('data/multidataset_items.json').read_text())
    selected, counts = {}, Counter()
    for item in items:
        if counts[item['dataset']] < 4:
            selected[item['id']] = item
            counts[item['dataset']] += 1
    with gzip.open(source, 'rt', encoding='utf-8') as handle:
        original = [json.loads(line) for line in handle]
    probes = []
    for row in original:
        tag = row['tag']
        if row['item_id'] not in selected or tag.get('length') != 0:
            continue
        if tag.get('baseline') or (tag.get('round') == 1 and tag.get('kind') in
                ('control', 'disagreement', 'weak_argument') and tag.get('framing') == 'first'
                and tag.get('mitigation') == 'none' and 'recovery' not in tag):
            probes.append(row)
    manifest = {'started': datetime.now(timezone.utc).isoformat(), 'status': 'running',
                'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'source_call_ids': [r['call_id'] for r in probes],
                'selected_items': list(selected), 'runtime': api('version'), 'models': api('tags'),
                'design': 'First four items per dataset, all zero-filler baselines and available first-round neutral/disagreement/weak branches. Three paired format arms. Original histories fixed; no rollout or new accuracy benchmark.'}
    (folder/'manifest.json').write_text(json.dumps(manifest, indent=2))
    results = []
    arms = ['schema_json', 'free_json', 'plain_label']
    try:
        with gzip.open(folder/'calls.jsonl.gz', 'wt', encoding='utf-8') as log:
            for index, old in enumerate(probes):
                item = selected[old['item_id']]
                for arm in arms[index % 3:] + arms[:index % 3]:
                    payload = copy.deepcopy(old['request'])
                    if arm != 'schema_json':
                        payload.pop('format', None)
                    if arm == 'plain_label':
                        payload['messages'][0]['content'] = payload['messages'][0]['content'].replace(
                            'Return JSON with an answer label.', 'Return only an answer label.')
                    raw = api('chat', payload)
                    answer = decode(raw['message']['content'], item['options'], arm == 'plain_label')
                    record = {'source_call_id': old['call_id'], 'item_id': item['id'],
                              'dataset': item['dataset'], 'condition': 'baseline' if old['tag'].get('baseline') else old['tag']['kind'],
                              'arm': arm, 'answer': answer, 'correct': item['correct'],
                              'original_answer': decode(old['response']['message']['content'], item['options']),
                              'request': payload, 'response': raw}
                    log.write(json.dumps(record)+'\n')
                    log.flush()
                    results.append(record)
                print(f'Finished {index+1}/{len(probes)} probes; {len(results)} calls', flush=True)
        manifest['status'] = 'complete'
    except BaseException:
        manifest['status'] = 'interrupted_or_failed'
        raise
    finally:
        manifest.update(finished=datetime.now(timezone.utc).isoformat(), calls=len(results))
        (folder/'manifest.json').write_text(json.dumps(manifest, indent=2))
    summary = {}
    for arm in arms:
        rows = [r for r in results if r['arm'] == arm]
        summary[arm] = {'calls': len(rows), 'unknown': sum(r['answer']=='UNKNOWN' for r in rows),
                        'invalid': sum(r['answer']=='INVALID' for r in rows),
                        'correct': sum(r['answer']==r['correct'] for r in rows),
                        'wrong': sum(r['answer'] not in ('UNKNOWN','INVALID',r['correct']) for r in rows),
                        'truncated': sum(r['response'].get('done_reason')=='length' for r in rows),
                        'changed_from_original': sum(r['answer']!=r['original_answer'] for r in rows)}
    (folder/'summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()

