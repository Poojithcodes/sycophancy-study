# Qwen-3B multi-dataset exploratory results

Completed 3074 model calls. Maximum recorded prompt length: 2035 tokens; truncated outputs: 0; unknown/invalid outputs: 622.

## Baseline at zero filler

| Dataset | Questions | Correct | Unknown |
|---|---:|---:|---:|
| mmlu_5subjects | 50 | 40 | 1 |
| synthetic_evidence | 6 | 6 | 0 |
| truthfulqa_binary | 50 | 30 | 12 |

## Main short-context outcomes

| Dataset/condition | N | Wrong switches or valid updates* | Incomplete | Median first wrong turn | Mean transitions |
|---|---:|---:|---:|---:|---:|
| mmlu_5subjects/control | 40 | 2 | 4 | 1.0 | 0.25 |
| mmlu_5subjects/disagreement | 40 | 39 | 8 | 2 | 1.225 |
| mmlu_5subjects/weak_argument | 40 | 11 | 34 | 2 | 0.5 |
| synthetic_evidence/control | 6 | 0 | 0 | None | 0 |
| synthetic_evidence/disagreement | 6 | 6 | 3 | 2 | 0.6666666666666666 |
| synthetic_evidence/weak_argument | 6 | 0 | 6 | None | 0 |
| synthetic_evidence/genuine | 6 | 6 | 0 | 1.0 | 1 |
| truthfulqa_binary/control | 30 | 2 | 11 | 1.0 | 0.16666666666666666 |
| truthfulqa_binary/disagreement | 30 | 28 | 3 | 1.0 | 0.9333333333333333 |
| truthfulqa_binary/weak_argument | 30 | 13 | 22 | 1.0 | 0.36666666666666664 |
| synthetic_recitation/disagreement | 6 | 4 | 4 | 2.0 | 1.6666666666666667 |
| synthetic_recitation/weak_argument | 6 | 0 | 6 | None | 0 |
| synthetic_recitation/genuine | 6 | 6 | 0 | 1.0 | 1 |

*Genuine-correction rows count final valid updates, not failures. For other rows, a wrong switch means any wrong answer in five rounds, even if later recovered. Full counts, confidence intervals and survival tables are in analysis.json. UNKNOWN is an observed abstention, not a parsing error and not a correct answer. The optional missingness bounds are hypothetical bounds if unknown answers were resolved into options, not hidden measured errors. Complete-case estimates exclude abstaining conversations and may be selection-biased. Survival tables censor at the first unknown and assume non-informative censoring, which is doubtful here; they are descriptive only.

## Matched contrasts

Each difference is RIGHT minus LEFT on complete matched items. For genuine corrections, positive means more valid updates; elsewhere positive means more wrong switches. Context and framing subsets are small.

| Comparison | Shared eligible | Complete pairs | Difference | Item-bootstrap 95% interval |
|---|---:|---:|---:|---|
| mmlu_5subjects/length_0_vs_5/control | 3 | 3 | 0 | [0.0, 0.0] |
| mmlu_5subjects/length_0_vs_15/control | 3 | 3 | 0 | [0.0, 0.0] |
| mmlu_5subjects/length_0_vs_30/control | 3 | 3 | 0 | [0.0, 0.0] |
| mmlu_5subjects/framing/disagreement | 8 | 7 | -0.42857142857142855 | [-0.8571428571428571, -0.14285714285714285] |
| mmlu_5subjects/length_0_vs_5/disagreement | 3 | 3 | 0 | [0.0, 0.0] |
| mmlu_5subjects/length_0_vs_15/disagreement | 3 | 3 | 0 | [0.0, 0.0] |
| mmlu_5subjects/length_0_vs_30/disagreement | 3 | 3 | 0 | [0.0, 0.0] |
| mmlu_5subjects/framing/weak_argument | 8 | 1 | -1 | [-1.0, -1.0] |
| mmlu_5subjects/length_0_vs_5/weak_argument | 3 | 0 | None | None |
| mmlu_5subjects/length_0_vs_15/weak_argument | 3 | 0 | None | None |
| mmlu_5subjects/length_0_vs_30/weak_argument | 3 | 0 | None | None |
| mmlu_5subjects/control_vs_disagreement | 40 | 30 | 0.9666666666666667 | [0.9, 1.0] |
| mmlu_5subjects/control_vs_weak_argument | 40 | 6 | 1 | [1.0, 1.0] |
| synthetic_evidence/length_0_vs_5/control | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic_evidence/length_0_vs_15/control | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic_evidence/length_0_vs_30/control | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic_evidence/framing/disagreement | 6 | 2 | -1 | [-1.0, -1.0] |
| synthetic_evidence/length_0_vs_5/disagreement | 6 | 3 | 0 | [0.0, 0.0] |
| synthetic_evidence/length_0_vs_15/disagreement | 6 | 2 | 0 | [0.0, 0.0] |
| synthetic_evidence/length_0_vs_30/disagreement | 6 | 3 | 0 | [0.0, 0.0] |
| synthetic_evidence/framing/weak_argument | 6 | 0 | None | None |
| synthetic_evidence/length_0_vs_5/weak_argument | 6 | 0 | None | None |
| synthetic_evidence/length_0_vs_15/weak_argument | 6 | 0 | None | None |
| synthetic_evidence/length_0_vs_30/weak_argument | 6 | 0 | None | None |
| synthetic_evidence/framing/genuine | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic_evidence/length_0_vs_5/genuine | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic_evidence/length_0_vs_15/genuine | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic_evidence/length_0_vs_30/genuine | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic_evidence/control_vs_disagreement | 6 | 3 | 1 | [1.0, 1.0] |
| synthetic_evidence/control_vs_weak_argument | 6 | 0 | None | None |
| truthfulqa_binary/length_0_vs_5/control | 3 | 2 | 0 | [0.0, 0.0] |
| truthfulqa_binary/length_0_vs_15/control | 3 | 2 | 0 | [0.0, 0.0] |
| truthfulqa_binary/length_0_vs_30/control | 3 | 2 | 0 | [0.0, 0.0] |
| truthfulqa_binary/framing/disagreement | 8 | 6 | -0.5 | [-0.8333333333333334, -0.16666666666666666] |
| truthfulqa_binary/length_0_vs_5/disagreement | 3 | 3 | 0 | [0.0, 0.0] |
| truthfulqa_binary/length_0_vs_15/disagreement | 3 | 3 | 0 | [0.0, 0.0] |
| truthfulqa_binary/length_0_vs_30/disagreement | 3 | 3 | 0 | [0.0, 0.0] |
| truthfulqa_binary/framing/weak_argument | 8 | 2 | 0 | [0.0, 0.0] |
| truthfulqa_binary/length_0_vs_5/weak_argument | 3 | 1 | 0 | [0.0, 0.0] |
| truthfulqa_binary/length_0_vs_15/weak_argument | 3 | 0 | None | None |
| truthfulqa_binary/length_0_vs_30/weak_argument | 3 | 1 | 0 | [0.0, 0.0] |
| truthfulqa_binary/control_vs_disagreement | 30 | 18 | 0.8333333333333334 | [0.6666666666666666, 1.0] |
| truthfulqa_binary/control_vs_weak_argument | 30 | 7 | 0.5714285714285714 | [0.14285714285714285, 0.8571428571428571] |
| synthetic/position_5_start_vs_middle/control | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic/position_5_start_vs_recent/control | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic/position_5_start_vs_middle/disagreement | 6 | 5 | 0 | [0.0, 0.0] |
| synthetic/position_5_start_vs_recent/disagreement | 6 | 4 | 0 | [0.0, 0.0] |
| synthetic/position_5_start_vs_middle/weak_argument | 6 | 0 | None | None |
| synthetic/position_5_start_vs_recent/weak_argument | 6 | 0 | None | None |
| synthetic/position_5_start_vs_middle/genuine | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic/position_5_start_vs_recent/genuine | 6 | 6 | -0.16666666666666666 | [-0.5, 0.0] |
| synthetic/position_15_start_vs_middle/control | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic/position_15_start_vs_recent/control | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic/position_15_start_vs_middle/disagreement | 6 | 4 | 0 | [0.0, 0.0] |
| synthetic/position_15_start_vs_recent/disagreement | 6 | 2 | 0 | [0.0, 0.0] |
| synthetic/position_15_start_vs_middle/weak_argument | 6 | 0 | None | None |
| synthetic/position_15_start_vs_recent/weak_argument | 6 | 0 | None | None |
| synthetic/position_15_start_vs_middle/genuine | 6 | 6 | -0.16666666666666666 | [-0.5, 0.0] |
| synthetic/position_15_start_vs_recent/genuine | 6 | 6 | -0.16666666666666666 | [-0.5, 0.0] |
| synthetic/position_30_start_vs_middle/control | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic/position_30_start_vs_recent/control | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic/position_30_start_vs_middle/disagreement | 6 | 5 | 0 | [0.0, 0.0] |
| synthetic/position_30_start_vs_recent/disagreement | 6 | 5 | 0 | [0.0, 0.0] |
| synthetic/position_30_start_vs_middle/weak_argument | 6 | 0 | None | None |
| synthetic/position_30_start_vs_recent/weak_argument | 6 | 0 | None | None |
| synthetic/position_30_start_vs_middle/genuine | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic/position_30_start_vs_recent/genuine | 6 | 6 | 0 | [0.0, 0.0] |
| synthetic/recitation/disagreement | 6 | 1 | 0 | [0.0, 0.0] |
| synthetic/recitation/weak_argument | 6 | 0 | None | None |
| synthetic/recitation/genuine | 6 | 6 | 0 | [0.0, 0.0] |

## Recovery and combined selectivity

```json
{
  "recovery": {
    "neutral": {
      "branches": 6,
      "unique_items": 6,
      "recovered_within_3": 6,
      "median_round_among_recovered": 1.0,
      "unknown_responses": 1
    },
    "evidence": {
      "branches": 6,
      "unique_items": 6,
      "recovered_within_3": 6,
      "median_round_among_recovered": 1.0,
      "unknown_responses": 1
    }
  },
  "selectivity": {
    "none": {
      "items": 0,
      "score": null,
      "item_bootstrap95": null
    },
    "recitation": {
      "items": 0,
      "score": null,
      "item_bootstrap95": null
    }
  }
}
```

## Limits

This is one quantized model, a development TruthfulQA binary adaptation, five selected MMLU subjects, and six simple synthetic items. The source keys are not independently human-validated. Repeated conditions are not independent questions. Structured output changes the task relative to free dialogue. Short repetitive filler tests turn count, not a 16k context. No hidden-state, attention, flattery, personalisation or multi-seed experiments were performed. Bootstrap intervals can be degenerate with tiny samples; main proportions also include Wilson intervals. Many exploratory comparisons were made without multiplicity correction; do not interpret individual intervals as confirmatory significance tests. No publication or generalisation claim follows from this pilot.
