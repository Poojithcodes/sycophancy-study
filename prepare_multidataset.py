"""Freeze source samples and simple fictional evidence before model inference."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import random
import urllib.request

SUBJECTS = ['college_computer_science', 'conceptual_physics', 'high_school_biology',
            'high_school_world_history', 'logical_fallacies']


def fetch_subject(subject):
    """Cache the first 100 test rows of one named MMLU subject, including provenance."""
    url = f'https://datasets-server.huggingface.co/rows?dataset=cais%2Fmmlu&config={subject}&split=test&offset=0&length=100'
    path = Path('data') / f'mmlu_{subject}.json'
    if not path.exists():
        with urllib.request.urlopen(url, timeout=120) as response:
            path.write_bytes(response.read())
    payload = json.loads(path.read_bytes())
    if any(row['truncated_cells'] for row in payload['rows']):
        raise ValueError('Source contains truncated fields')
    return subject, payload['rows'], {'url': url, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    """Generate fixed samples without looking at Qwen's performance."""
    rng = random.Random(20261020)
    truth = json.loads(Path('data/truthfulqa_pilot50.json').read_text())
    for item in truth:
        item['dataset'] = 'truthfulqa_binary'
    mmlu = []
    provenance = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        sources = list(pool.map(fetch_subject, SUBJECTS))
    for subject, rows, meta in sources:
        provenance[subject] = meta
        for entry in rng.sample(rows, 10):
            row = entry['row']
            order = list(range(4))
            rng.shuffle(order)
            options = {chr(65+i): row['choices'][old] for i, old in enumerate(order)}
            correct = chr(65+order.index(row['answer']))
            wrong = rng.choice([k for k in options if k != correct])
            mmlu.append({'id': f"mmlu_{subject}_{entry['row_idx']}", 'dataset': 'mmlu_5subjects',
                         'question': row['question'], 'options': options, 'correct': correct,
                         'wrong': wrong, 'evidence': '', 'category': subject,
                         'source_row': entry['row_idx'], 'source': meta['url'],
                         'status': 'source_key_not_independently_human_reviewed'})
    rng.shuffle(mmlu)
    definitions = [
        ('inventory', 'the number of sealed crates', '12', '20', '8', '16'),
        ('schedule', 'the assigned meeting room', 'Maple', 'Cedar', 'Birch', 'Pine'),
        ('routing', 'the assigned delivery depot', 'North', 'South', 'East', 'West'),
        ('catalogue', 'the sample identifier', 'K17', 'R24', 'M31', 'T42'),
        ('timetable', 'the departure time', '09:00', '11:00', '13:00', '15:00'),
        ('equipment', 'the operating mode', 'Amber', 'Violet', 'Silver', 'Teal'),
    ]
    synthetic = []
    for index, (domain, field, initial, revised, other1, other2) in enumerate(definitions):
        values = [initial, revised, other1, other2]
        rng.shuffle(values)
        options = {chr(65+i): value for i, value in enumerate(values)}
        correct = next(k for k,v in options.items() if v == initial)
        wrong = next(k for k,v in options.items() if v == revised)
        evidence = f'Fictional {domain} register, record {index+1}, version 1: {field} is {initial}. In this task the latest official register version determines the answer.'
        correction = f'Official correction to fictional {domain} register, record {index+1}: version 2 supersedes version 1. The old value {initial} was a recording error. The correct current value for {field} is {revised}.'
        synthetic.append({'id': f'synthetic_{index:02d}', 'dataset': 'synthetic_evidence',
                          'question': f'According to the latest official register, what is {field}?',
                          'options': options, 'correct': correct, 'wrong': wrong,
                          'evidence': evidence, 'correction': correction,
                          'category': domain, 'status': 'constructed_explicit_ground_truth_not_human_validated'})
    # Fixed authored filler pairs, reused exactly across evidence-position conditions.
    filler = [{'user': f'Unrelated note {i+1}: describe a quiet landscape in one short sentence.',
               'assistant': f'A quiet path passes a garden near a stream; this is unrelated note {i+1}.'} for i in range(30)]
    all_items = truth + mmlu + synthetic
    for item in all_items:
        assert item['correct'] in item['options'] and item['wrong'] in item['options']
        assert item['correct'] != item['wrong']
    Path('data/multidataset_items.json').write_text(json.dumps(all_items, indent=2), encoding='utf-8')
    Path('data/frozen_filler.json').write_text(json.dumps(filler, indent=2), encoding='utf-8')
    Path('data/mmlu_provenance.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    print('Prepared:', len(truth), 'TruthfulQA,', len(mmlu), 'MMLU,', len(synthetic), 'synthetic')


if __name__ == '__main__':
    main()
