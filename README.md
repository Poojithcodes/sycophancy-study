# sycophancy-study

Evaluating how open-weight LLMs respond to multi-turn user pressure: measuring incorrect answer changes, evidence-based updates, and recovery through reproducible experiments.

## Current status

Initial behavioural runner implemented. No real model results yet. Two fictional demo items test the plumbing only; they are not a research dataset. Genuine corrections, longer filler conversations, recovery, model internals and MCP integration are planned, not implemented.

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

The baseline is generated once and shared across branches. This pilot does not yet randomize option order or estimate confidence intervals. Demo correct labels are balanced A/B. Research runs need counterbalanced labels, validated items, fixed model revisions, common-item comparisons and uncertainty estimates. Temperature zero does not guarantee identical GPU outputs.

## Next milestones

- Select and license-check a question dataset, then review answer keys and pressure prompts.
- Add schema checks and human review for genuine evidence corrections.
- Record local model/server provenance and benchmark runtime before larger runs.
- Add answer adjudication, human agreement checks and item-level bootstrap intervals.
- Implement evidence-position and length factors from the project protocol.
- Add recovery and internal probes after behavioural validation.

Claims that correction selectivity or multi-turn sycophancy have never been studied must not be made: related work already covers both. The precise contribution remains to be established through literature review.
