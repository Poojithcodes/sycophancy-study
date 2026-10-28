# UNKNOWN diagnostic: prepared, execution blocked

Status on 2026-10-28: the local Ollama tags endpoint was reachable and listed the original Qwen2.5:3B model digest. The NVIDIA utility detected the RTX 3050 6GB. No new model responses were saved in this attempt, so there are no new experimental conclusions.

Automatic approval review blocked execution after detecting an unexpected telemetry request to dc.services.visualstudio.com. The payload and origin were not established. The diagnostic code itself uses the existing local Ollama API helper; it does not intentionally contact that domain. Do not infer that Ollama itself caused the telemetry. Resolve the approval/environment issue before retrying through the agent.

## Fixed diagnostic design

Use the first four items from each of the three datasets in the existing frozen item file. Replay their zero-filler baselines and any available first-round control, disagreement and weak-argument requests. Follow-up availability depends on the original baseline filter. Selection does not depend on new responses.

For each saved request compare three arms:

1. Original constrained JSON schema, with original decoding settings.
2. Identical request without the schema constraint, still requesting JSON.
3. No schema constraint and a system instruction requesting only an answer label.

All arms allow UNKNOWN. Keep the historical messages fixed, including prior assistant JSON. Rotate arm execution order. Preserve raw requests, outputs, source call IDs, script and source hashes, runtime version and model metadata. Report UNKNOWN, invalid formatting, correct, wrong and truncated outputs separately.

The first two arms isolate the schema constraint within this small selected replay sample. The third arm changes the format instruction too. This is a single-turn diagnostic, not a fresh multi-turn study or a new sycophancy-rate estimate. The runtime may differ from the original run; use the contemporaneous schema arm as the comparison, and inspect reproduction differences. A 32-token budget is retained for comparability; truncation must be reviewed before interpreting invalid outputs.

## Running after the environment issue is resolved

From the repository directory, with local Ollama available:

```powershell
python -m unittest test_diagnose_unknown.py
python diagnose_unknown.py --output experiments/unknown-diagnostic-next-run
```

Use a new output path each time; the script refuses to overwrite existing folders. A completed run writes `summary.json`, `manifest.json` and compressed raw calls. Existing incomplete local folders are preserved and are not presented as completed results.

Next, review the matched responses and parsing/truncation counts before deciding whether to revise the main protocol. Do not remove the abstention option just to make the apparent results look better. Freeze the revised protocol before using new held-out questions or comparing other models.

