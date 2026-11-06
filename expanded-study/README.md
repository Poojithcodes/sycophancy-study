# Expanded 300-question study

## New teammate runs

Follow [TEAM_START.md](TEAM_START.md) for exact Llama, Mistral and Phi commands. `run_model.py` automatically restores only the frozen data files from the archive; it never extracts old code or completed results over your working files. Run each model in its own output folder.

The original `run_300.py` and archive are unchanged snapshots of the Qwen experiment. Use `run_model.py` for new runs. The old README_300.md describes the original two-Qwen workflow.

## Completed Qwen results

Both models finished all 300 questions: 2,918 responses for 3B and 4,254 for 7B. [Read the report](results/expanded300-v1/REPORT.md).

[expanded300-complete.zip](expanded300-complete.zip) contains the complete 35-file snapshot: code, dataset, source CSVs and licenses, raw logs, records, model/runtime manifests and analyses. [SHA256SUMS.json](SHA256SUMS.json) records the archived file hashes. To inspect the original experiment, extract the archive into a separate empty directory, not over the current repository.

These are exploratory findings. UNKNOWN abstentions complicate rankings, human answer review remains pending, and synthetic items come from ten template families. Ten automated tests pass; real teammate-model inference has not been performed here.
