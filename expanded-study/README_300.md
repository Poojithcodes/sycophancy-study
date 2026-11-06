# 300 new questions: local Qwen evaluation

This is an expanded exploratory behavioural evaluation, not training and not a claim of publication readiness. It uses 150 MMLU questions (30 in each of five subjects), 100 TruthfulQA binary adaptations, and 50 constructed evidence cases (10 task families, 5 variants each). None of the question texts overlap with the 106-item pilot. Selection was fixed before inference using seed 20261103. Benchmark source keys are not independently human-adjudicated; record that review in data/expanded300_review.csv. Automated checks are not a substitute for human review.

## Start

Start Ollama and ensure qwen2.5:3b and qwen2.5:7b are installed. Python uses only its standard library. Double-click START_300.cmd, or run from this folder:

```powershell
python run_300.py
```

The script runs 3B and then 7B, saves each response immediately, and generates results/expanded300-v1/REPORT.md and comparison.json after both finish. Keep the laptop awake and plugged in. Closing ChatGPT does not stop a separately launched terminal process. Closing the terminal or sleeping the laptop interrupts progress; run the same command again to resume.

For a shorter first batch on both models:

```powershell
python run_300.py --limit 20
```

Then run without --limit to continue using the saved responses. The first 20 are a fixed shuffled subset of the actual evaluation, not additional questions. Do not tune the protocol after seeing their outcomes and then pool results. Runtime estimates should use elapsed time and completed work, not response counts alone.

## Frozen design

Each question gets one baseline. Only baseline-correct items receive three independent five-round branches: neutral reconsideration, unsupported disagreement, and appeal-to-popularity weak argument. All branches start from the same baseline. Synthetic cases additionally receive five genuine-correction rounds. After the first wrong answer in each eligible synthetic unsupported branch (including neutral control if it fails), the runner forks two three-round recovery probes: neutral reminder and original-evidence reminder. Genuine corrections are valid updates, not sycophancy failures.

There is no filler, persona contrast, recitation mitigation, or evidence-position factor in this batch. These choices reduce compute and focus the study. Main conditions retain the pilot wording and system prompt. Seed is 20261103; temperature 0; context 4096; output limit 32 tokens; constrained JSON options plus UNKNOWN. MMLU option order is preserved to avoid corrupting option references. TruthfulQA correct labels are balanced 50/50; constructed-case labels are near-balanced. Explicit UNKNOWN is preserved in raw logs and counted as abstention separately from wrong options. Any invalid or truncated output stops execution for inspection.

Upper bound per model: 300 baselines + 4500 main follow-ups + 250 genuine-correction follow-ups + 900 recovery calls = 5950 calls. Baseline exclusions and absence of failures usually reduce this. There is no measured overnight runtime yet.

The study manifest locks code, dataset, model digests/configuration, and Ollama version across both models and all resumes. Keep Ollama and model weights unchanged until both finish. A mismatch stops before new inference; use a new output folder for a deliberately different setup. Run-folder locking prevents simultaneous writers. A complete log is replayed without new inference; it regenerates records and analysis, including after an interrupted export.

## Analysis and limits

Per-model analysis.json includes baseline performance, pressure versus neutral paired contrasts, wrong-option events, abstentions, and recovery. The combined report compares only questions both models initially answered correctly. Report all questions and exclusions as well. Complete-case contrasts can be biased because they exclude abstaining conversations. Individual turns are not independent samples. Synthetic variants share ten templates; item-bootstrap intervals for them do not account for template clustering and are descriptive. More questions do not establish novelty, generalisation to free dialogue, or an internal motive. This adaptation is not official TruthfulQA MC1/MC2 or full MMLU scoring.

## Source provenance

MMLU is by Hendrycks and collaborators: https://github.com/hendrycks/test . CSVs were retrieved from the pinned OpenNMT mirror URLs in data/sources/urls.json. All 50 pilot MMLU questions, answer choices and answer-key texts match this mirror; new items are sampled from the full selected subject test files, not just their first 100 rows. Duplicate stems are excluded before sampling. MMLU-LICENSE.txt is retained.

TruthfulQA is by Lin, Hilton and Evans: https://github.com/sylinrl/TruthfulQA . The source CSV is pinned to commit d71c110897f5d31c5d7f309e7bc316c152f6f031. Best Answer and Best Incorrect Answer form the binary task. TruthfulQA-LICENSE.txt is retained. Source hashes and row indexes are stored. These questions are held out from our pilot, not guaranteed absent from model pretraining.

Rebuild only before a run with python prepare_300.py. That command recreates the review CSV; preserve completed reviews before using it. Never rebuild or edit the frozen dataset midway through an evaluation.

## Validation

```powershell
python -m unittest -v test_expanded
```

Tests use fake responses, not model inference. They cover dataset composition/disjointness, option order, genuine-correction isolation, interrupted-call recovery, prompt-change refusal, explicit UNKNOWN handling and corrupt logs. Live Ollama access must be checked on the laptop; a restricted Codex session may be unable to open the local socket.
