# Completed 300-question Qwen study

Both Qwen2.5 models completed all 300 questions on 5 November 2026: 3B generated 2,918 responses and 7B generated 4,254 (7,172 total). This expanded study is separate from the earlier 106-question pilot.

- [Read the comparison report](results/expanded300-v1/REPORT.md)
- [Download complete experiment and raw results](expanded300-complete.zip)
- [Protocol and run instructions](README_300.md)
- [SHA-256 checksums of all archived files](SHA256SUMS.json)

## Get the full data

The ZIP contains the exact code, frozen dataset, source CSVs and licenses, raw request/response logs, records, model/runtime manifests, progress, analyses and comparison report (35 files). Extract it into the repository root: it contains an `expanded-study/` directory. Code and summary files are also provided here for browsing. The full raw logs and dataset are in the archive, not separate GitHub files. Temporary locks and Python caches are excluded.

From the repository root, extraction can be done with:

```powershell
python -m zipfile -e expanded-study/expanded300-complete.zip .
python -m unittest discover -s expanded-study -p test_expanded.py
```

All seven tests passed before upload. The completed logs were replayed offline on 5 November: reconstructed records and analyses matched the saved outputs exactly. No new model inference was used for that check.

## Interpretation

On 76 MMLU questions both initially answered correctly, neutral wrong-switch counts were 5 (3B) and 4 (7B), compared with 37 and 75 under disagreement. A wrong switch is any wrong option across five follow-ups. UNKNOWN is explicit abstention and must be reported separately; 3B abstained much more often. These findings do not establish a general model-size ranking. Synthetic questions use ten template families; independent answer review and broader validation remain pending.

## Teammate readiness

This is the exact Qwen experiment snapshot. The runner and comparison are still fixed to Qwen 3B/7B. General model-selection support and teammate-specific commands remain to be implemented and tested. Do not silently change this archived run's settings or overwrite its results.
