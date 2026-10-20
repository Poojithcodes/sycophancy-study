# sycophancy-study

Evaluating how open-weight LLMs respond to multi-turn user pressure: measuring incorrect answer changes, evidence-based updates, and recovery through reproducible experiments.

## Current status

Initial behavioural runner implemented and exercised locally on Qwen2.5-3B. Two fictional demo items test the plumbing only; they are not a research dataset. A provisional TruthfulQA-derived 50-item pilot is available. Genuine corrections, longer filler conversations, recovery, model internals and MCP integration are planned, not implemented.

## Run offline checks

Python 3.11+; the runner uses only the standard library.

```powershell
python -m unittest -v
```

## Run a real local experiment

1. Start a local inference server exposing the OpenAI-compatible `/v1/chat/completions` endpoint. The server supplies model execution; this repository does not install or launch it.
2. Load a small instruction-tuned quantized model appropriate for available VRAM. Initial hardware: RTX 3050 Laptop, 6 GB VRAM. Model fit and speed have not yet been measured.
3. Edit `config.json`: endpoint, server model identifier, exact weight revision and quantization. Record server version and chat template alongside your run before using it in research. Defaults are placeholders.
4. Run from this repository directory:

```powershell
python study.py --output results/first-local-run
```

Use a new output directory for every run; existing runs are never overwritten. Optional endpoint authentication comes from the `INFERENCE_API_KEY` environment variable and is not written to transcripts. Local endpoints are recommended; remote endpoint costs depend on the provider.

## What it measures

Ask a baseline question. Exclude baseline-incorrect and unparsed answers from the pressure experiment while retaining their records. Fork three independent branches from the same correct response: neutral reconsideration, unsupported disagreement and a weak argument. Repeat the fixed message up to five times in each branch. Save full requests, outputs and server metadata.

The summary reports conversations with any parsed incorrect answer, targeted wrong-option agreement, and unparsed-response counts. Observed switch rates are incomplete when outputs cannot be parsed: inspect those transcripts before drawing conclusions. A flip after pressure is behavioural evidence, not proof of an internal motive. Compare pressure outcomes against the neutral control.

The baseline is generated once and shared across branches. Demo correct labels are balanced A/B. Research runs need counterbalanced labels, validated items, fixed model revisions, common-item comparisons and uncertainty estimates. Temperature zero does not guarantee identical GPU outputs.

## TruthfulQA exploratory pilot

Source: https://github.com/sylinrl/TruthfulQA and https://huggingface.co/datasets/truthfulqa/truthful_qa . Authors: Stephanie Lin, Jacob Hilton and Owain Evans, *TruthfulQA: Measuring How Models Mimic Human Falsehoods* (2022). Source license: Apache-2.0; retained in `data/TruthfulQA-LICENSE.txt`.

The downloaded authors' CSV contains 790 rows, while the Hugging Face card lists 817. This pilot samples the CSV version; `data/truthfulqa_manifest.json` pins its SHA-256 and sample seed. Do not conflate the versions. The selected 50 items are retained in Git; the preparation script downloads the raw CSV if missing and rejects a changed checksum.

```powershell
python prepare_truthfulqa.py
python study.py --config config.truthfulqa.json --items data/truthfulqa_pilot50.json --output results/truthfulqa-new-run
```

This is an adapted binary-choice pressure experiment, NOT the official TruthfulQA MC1/MC2 benchmark. Each question pairs the source's best answer with its best incorrect answer. Correct labels are assigned to A/B with a seeded balanced shuffle (25 each). No correct answer or source key is disclosed to the model, and no supporting evidence passage is supplied. The weak-argument branch uses a fixed appeal-to-popularity template, not individually authored factual arguments. The sample is drawn before inference; all baseline failures and unparsed responses must be reported.

The dedicated config requests a final label only to avoid explanation truncation. A diagnostic run using the earlier explanation-friendly prompt was stopped after identifying truncation; never pool it with the new protocol. The output cap is 32 tokens. Explicitly requesting short answers may affect behaviour and must be reported.

Items retain the original source links and category tags, but have NOT been independently checked by human reviewers. Some source questions are ambiguous, time-dependent or context-dependent. Treat this as exploratory engineering validation; do not present these rates as publication-ready or infer a model's motive. Complete item review and uncertainty analysis before a research claim. The current pilot does not test valid updating or stubbornness.

## Next milestones

- Select and license-check a question dataset, then review answer keys and pressure prompts.
- Add schema checks and human review for genuine evidence corrections.
- Record local model/server provenance and benchmark runtime before larger runs.
- Add answer adjudication, human agreement checks and item-level bootstrap intervals.
- Implement evidence-position and length factors from the project protocol.
- Add recovery and internal probes after behavioural validation.

Claims that correction selectivity or multi-turn sycophancy have never been studied must not be made: related work already covers both. The precise contribution remains to be established through literature review.
