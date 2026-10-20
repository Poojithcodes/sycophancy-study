"""Package the unchanged pilot transcripts and a clearly qualified summary for Git."""
import gzip
import json
from pathlib import Path
import shutil


def main():
    """Keep raw outputs compressed; generate the report from recorded scores."""
    source = Path('results/truthfulqa50-qwen3b-002')
    target = Path('experiments/truthfulqa50-qwen3b-002')
    target.mkdir(parents=True, exist_ok=True)
    for name in ('manifest.json', 'summary.json'):
        shutil.copyfile(source / name, target / name)
    (target / 'transcripts.jsonl.gz').write_bytes(gzip.compress((source / 'transcripts.jsonl').read_bytes(), mtime=0))
    summary = json.loads((source / 'summary.json').read_text())
    text = '# Exploratory TruthfulQA-derived pilot\n\n'
    text += f"Asked {summary['items']} questions. Baseline correct and parsed: {summary['eligible']}; unparsed: {summary['baseline_unparsed']}; parsed incorrect: {summary['items'] - summary['eligible'] - summary['baseline_unparsed']}.\n\n"
    text += '| Condition | Observed wrong switches | Conversations with unparsed replies |\n|---|---:|---:|\n'
    for name, stats in summary['conditions'].items():
        text += f"| {name} | {stats['observed_incorrect_switches']}/{stats['conversations']} | {stats['conversations_with_unparsed']} |\n"
    text += '\nA switch means any scored wrong answer within five rounds, even if the model later recovers. Missing labels are not counted as correct; rates above are only observed events and may undercount. Neutral reconsideration also causes switches, so not every switch under pressure can be attributed to sycophancy. Do not rank conditions confidently with unequal missingness.\n\n'
    text += 'Protocol: two options; source best correct and best incorrect answers; no supplied evidence; balanced labels; 50 seeded sampled items; Qwen2.5-3B Q4_K_M; final-label-only prompt; temperature zero; 32 output tokens. This is not official TruthfulQA scoring. Items have not been independently reviewed. No significance or generalization claim is made.\n\n'
    text += 'An earlier diagnostic run was stopped due to explanation truncation and is excluded. This export preserves the completed run unchanged; gunzip transcripts.jsonl.gz to inspect full requests and responses.\n'
    (target / 'REPORT.md').write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
