"""Replay an interrupted run's saved responses, then infer only missing calls."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import research_run as study


def load_calls(path):
    rows = path.read_bytes().splitlines(keepends=True)
    calls = []
    for i, row in enumerate(rows):
        try:
            call = json.loads(row)
        except (ValueError, UnicodeDecodeError):
            if i == len(rows) - 1 and not row.endswith(b'\n'):
                print('Ignoring incomplete final log line; retrying that call.')
                break
            raise ValueError(f'Corrupt log line {i + 1}')
        if call.get('call_id') != len(calls) + 1:
            raise ValueError('Nonconsecutive call IDs')
        if not isinstance(call.get('request'), dict):
            raise ValueError('Missing request')
        if not isinstance(call.get('response', {}).get('message', {}).get('content'), str):
            raise ValueError('Missing response content')
        calls.append(call)
    if not calls:
        raise ValueError('No complete saved calls')
    return calls


class Replay:
    def __init__(self, calls, live):
        self.calls, self.live = calls, live
        self.index = 0
        self.new_calls = 0

    def __call__(self, path, payload=None):
        if path != 'chat':
            return self.live(path, payload)
        if self.index < len(self.calls):
            saved = self.calls[self.index]
            if saved['request'] != payload:
                raise ValueError(f'Request mismatch at call {self.index + 1}; stopped before new inference')
            self.index += 1
            if self.index == len(self.calls):
                print(f'Reused {self.index} saved responses. Continuing new inference.', flush=True)
            return saved['response']
        self.new_calls += 1
        return self.live(path, payload)


def digest(tags, model):
    values = [m.get('digest') for m in tags.get('models', [])
              if model in (m.get('name'), m.get('model'))]
    if len(values) != 1 or not values[0]:
        raise ValueError(f'Cannot identify model digest: {model}')
    return values[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    source, output = Path(args.source), Path(args.output)
    if output.exists():
        raise ValueError('Output exists; choose a new directory')
    manifest = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))
    for key, path in (
        ('runner_sha256', Path(study.__file__)),
        ('items_sha256', Path('data/multidataset_items.json')),
        ('filler_sha256', Path('data/frozen_filler.json')),
    ):
        if hashlib.sha256(path.read_bytes()).hexdigest() != manifest.get(key):
            raise ValueError(f'{path} changed since the original run; restore the original file')
    calls = load_calls(source / 'calls.jsonl')
    model = calls[0]['request']['model']
    if any(c['request']['model'] != model for c in calls):
        raise ValueError('Mixed models in log')
    if digest(manifest['model'], model) != digest(study.api('tags'), model):
        raise ValueError('Installed model weights changed')
    if manifest['runtime'] != study.api('version'):
        raise ValueError('Ollama version changed')
    if manifest['model_details'] != study.api('show', {'model': model}):
        raise ValueError('Model configuration changed')
    replay = Replay(calls, study.api)
    old_api, old_argv = study.api, sys.argv
    provenance = {
        'source': str(source.resolve()), 'source_manifest': manifest,
        'source_calls_sha256': hashlib.sha256((source / 'calls.jsonl').read_bytes()).hexdigest(),
        'saved_calls': len(calls),
        'method': 'Exact request replay followed by new inference',
    }
    if (source / 'resume.json').exists():
        provenance['previous_resume'] = json.loads((source / 'resume.json').read_text(encoding='utf-8'))
    print(f'Replaying {len(calls)} saved responses without inference.', flush=True)
    succeeded = False
    try:
        study.api = replay
        sys.argv = ['research_run.py', '--model', model, '--output', str(output)]
        study.main()
        if replay.index != len(calls):
            raise ValueError('Runner ended before replay consumed all saved calls')
        succeeded = True
    finally:
        study.api, sys.argv = old_api, old_argv
        if output.exists():
            provenance.update(replayed_calls=replay.index, new_calls_attempted=replay.new_calls)
            (output / 'resume.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
            if not succeeded and (output / 'manifest.json').exists():
                current = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
                current['status'] = 'interrupted_or_failed'
                (output / 'manifest.json').write_text(json.dumps(current, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
