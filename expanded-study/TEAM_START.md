# Start here: teammate runs

The completed Qwen results are preserved in `expanded300-complete.zip`. Use the new `run_model.py` for other models; the original `run_300.py` remains unchanged for reproducibility.

## Setup

Install Python 3.10+ and Ollama. Open Ollama. Clone or pull the latest `main` branch, then run the commands below from the repository root. No pip packages or paid API keys are required. The runner restores the checked dataset from the included ZIP automatically; do not extract the whole archive over your working files.

### Swastik: Llama 3.1 8B
```powershell
ollama pull llama3.1:8b
python expanded-study/run_model.py --model llama3.1:8b --output expanded-study/results/swastik-llama --limit 20
python expanded-study/run_model.py --model llama3.1:8b --output expanded-study/results/swastik-llama
```

### Sanjana: Mistral 7B
```powershell
ollama pull mistral:7b
python expanded-study/run_model.py --model mistral:7b --output expanded-study/results/sanjana-mistral --limit 20
python expanded-study/run_model.py --model mistral:7b --output expanded-study/results/sanjana-mistral
```

### Affan: Phi-4-mini
```powershell
ollama pull phi4-mini:3.8b
python expanded-study/run_model.py --model phi4-mini:3.8b --output expanded-study/results/affan-phi --limit 20
python expanded-study/run_model.py --model phi4-mini:3.8b --output expanded-study/results/affan-phi
```

First run only the command ending in `--limit 20` after downloading. Check the saved answers and model name. Then run the last command to resume through all 300 questions. Keep the laptop awake and plugged in. If interrupted, repeat the same command; saved responses are reused. Do not update Ollama, change model downloads or edit code midway through a run. A settings mismatch stops instead of mixing experiments.

Each run saves its own REPORT.md, analysis.json, calls.jsonl, records.jsonl and manifests in the selected output folder. Send the whole folder plus five example conversations to Poojith. Keep UNKNOWN answers. More responses simply means more initially correct questions received follow-ups.

Shambavi: independently review sampled answer keys and conversations, and summarise related papers as described in the team document. Poojith: validate incoming results and compare shared initially correct questions. Affan's alternative-wording and shuffled-option experiments remain a separate follow-up task; this runner performs the unchanged main protocol only.

## Validation and limits

Automated tests cover model routing, pause/resume, replay without new calls, output protection, dataset restoration, UNKNOWN, and the original protocol. Real Llama/Mistral/Phi inference has not been run from this environment. Each teammate's 20-question trial is the live compatibility check. Invalid/truncated JSON stops the run; report it rather than silently increasing limits. Different hardware can run at different speeds.

The initial trial uses the first 20 questions, not a representative benchmark. Complete all 300 before reporting final results. Cross-model comparisons must match baseline-correct question IDs and show abstentions separately.

Run the test suite after the dataset is restored:
```powershell
python -m unittest discover -s expanded-study -p "test_*.py"
```
