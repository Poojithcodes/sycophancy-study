"""Run the frozen 300-question protocol on one explicitly selected Ollama model."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import zipfile
import run_300 as core


def ensure_data():
    """Restore only missing data files, never code or completed results."""
    archive = core.ROOT / 'expanded300-complete.zip'
    if not archive.exists():
        if core.ITEMS.exists():
            return
        raise ValueError('Missing dataset and expanded300-complete.zip; download the full repository.')
    checks = core.read(core.ROOT / 'SHA256SUMS.json')
    with zipfile.ZipFile(archive) as z:
        for name, expected in checks.items():
            if not name.startswith('expanded-study/data/'):
                continue
            relative = Path(name).relative_to('expanded-study')
            target = (core.ROOT / relative).resolve()
            if not target.is_relative_to((core.ROOT / 'data').resolve()):
                raise ValueError('Invalid archive path')
            data = target.read_bytes() if target.exists() else z.read(name)
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError('Dataset checksum mismatch: ' + name)
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)


@contextmanager
def lock_output(folder):
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / 'run.lock').open('a+b') as lock:
        if lock.tell() == 0:
            lock.write(b'0'); lock.flush()
        lock.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def report(folder, model):
    records = [json.loads(s) for s in (folder / 'records.jsonl').read_text().splitlines()]
    lines = [f'# 300-question results: {model}', '',
             'Exploratory evaluation. UNKNOWN is abstention, not a correct answer.', '',
             '| Dataset | Questions | Initially correct | Initial UNKNOWN |',
             '|---|---:|---:|---:|']
    for dataset in sorted({r['dataset'] for r in records}):
        rows = [r for r in records if r['record_type'] == 'baseline' and r['dataset'] == dataset]
        lines.append(f"| {dataset} | {len(rows)} | {sum(r['answer']==r['correct'] for r in rows)} | {sum(r['answer'] is None for r in rows)} |")
    lines += ['', '| Dataset / condition | Eligible | Observed wrong switches / valid updates | Any UNKNOWN |', '|---|---:|---:|---:|']
    groups = sorted({(r['dataset'], r['kind']) for r in records if r['record_type'] == 'branch'})
    for dataset, kind in groups:
        rows = [r for r in records if r['record_type']=='branch' and r['dataset']==dataset and r['kind']==kind]
        event = 'genuine_update_final' if kind == 'genuine' else 'observed_wrong_switch'
        count = sum(core.stats.metrics(r)[event] for r in rows)
        lines.append(f"| {dataset} / {kind} | {len(rows)} | {count} | {sum(None in r['answers'] for r in rows)} |")
    lines += ['', 'Genuine rows count valid final updates. Other rows count any wrong option across five rounds. Counts can overlap with UNKNOWN.',
              'Eligibility depends on this model answering the baseline correctly. Cross-model comparisons must match shared question IDs; do not directly rank these rates.',
              'Synthetic questions use ten template families. Human answer review remains pending. See analysis.json for detailed uncertainty and recovery results.']
    (folder / 'REPORT.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True, help='Exact installed tag, e.g. llama3.1:8b')
    parser.add_argument('--output', required=True, type=Path, help='Separate folder for this model run')
    parser.add_argument('--limit', type=int, help='Pause after N questions; remove to resume all 300')
    args = parser.parse_args(argv)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/:\-]*:[A-Za-z0-9._\-]+', args.model):
        parser.error('Use an explicit model:tag, such as phi4-mini:3.8b')
    if args.limit is not None and not 1 <= args.limit <= 300:
        parser.error('--limit must be 1..300')
    ensure_data()
    items = core.read(core.ITEMS)
    if len(items) != 300 or core.sha(core.ITEMS) != core.read(core.ROOT/'data/expanded300_manifest.json')['items_sha256']:
        raise ValueError('Frozen dataset changed')
    with lock_output(args.output):
        settings = args.output/'study_manifest.json'
        if not settings.exists() and any(p.name != 'run.lock' for p in args.output.iterdir()):
            raise ValueError('Output folder is not empty; choose a new folder')
        frozen = {**core.fingerprint([args.model]), **core.metadata([args.model]),
                  'selected_models': [args.model], 'entrypoint': 'run_model.py',
                  'entrypoint_sha256': core.sha(Path(__file__))}
        if settings.exists():
            if core.read(settings) != frozen:
                raise ValueError('Model, code, runtime, dataset or settings changed; choose a new folder')
        else:
            core.atomic(settings, frozen)
        if core.evaluate(args.output, args.model, items, frozen, args.limit):
            report(args.output, args.model)
            print('Complete: ' + str(args.output/'REPORT.md'))
        else:
            print('Paused. Repeat the same command without --limit to finish.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'STOPPED: {exc}. Saved responses are retained.', file=sys.stderr)
        sys.exit(1)
