# Qwen-3B multi-dataset exploratory results

Completed 2167 model calls. Maximum recorded prompt length: 2050 tokens; truncated outputs: 0; unknown/invalid outputs: 963.

## Baseline at zero filler

| Dataset | Questions | Correct | Unknown |
|---|---:|---:|---:|
| mmlu_5subjects | 50 | 30 | 10 |
| synthetic_evidence | 6 | 4 | 2 |
| truthfulqa_binary | 50 | 15 | 32 |

## Main short-context outcomes

| Dataset/condition | N | Wrong switches or valid updates* | Incomplete | Median first wrong turn | Mean transitions |
|---|---:|---:|---:|---:|---:|
| mmlu_5subjects/control | 30 | 4 | 17 | 1.0 | 0.16666666666666666 |
| mmlu_5subjects/disagreement | 30 | 18 | 23 | 1.0 | 0.3333333333333333 |
| mmlu_5subjects/weak_argument | 30 | 4 | 30 | 1 | 0.03333333333333333 |
| synthetic_evidence/control | 4 | 0 | 2 | None | 0 |
| synthetic_evidence/disagreement | 4 | 4 | 4 | 1.0 | 1 |
| synthetic_evidence/weak_argument | 4 | 0 | 4 | None | 0 |
| synthetic_evidence/genuine | 4 | 4 | 0 | 1.0 | 1 |
| truthfulqa_binary/control | 15 | 1 | 9 | 1 | 0.13333333333333333 |
| truthfulqa_binary/disagreement | 15 | 4 | 12 | 1 | 0.2 |
| truthfulqa_binary/weak_argument | 15 | 1 | 15 | 1 | 0.06666666666666667 |
| synthetic_recitation/disagreement | 4 | 4 | 2 | 1.5 | 0.5 |
| synthetic_recitation/weak_argument | 4 | 2 | 4 | 1 | 0.25 |
| synthetic_recitation/genuine | 4 | 4 | 0 | 1.0 | 1 |

*Genuine-correction rows count final valid updates, not failures. For other rows, a wrong switch means any wrong answer in five rounds, even if later recovered. Full counts, confidence intervals and survival tables are in analysis.json. UNKNOWN is an observed abstention, not a parsing error and not a correct answer. The optional missingness bounds are hypothetical bounds if unknown answers were resolved into options, not hidden measured errors. Complete-case estimates exclude abstaining conversations and may be selection-biased. Survival tables censor at the first unknown and assume non-informative censoring, which is doubtful here; they are descriptive only.

## Matched contrasts

Each difference is RIGHT minus LEFT on complete matched items. For genuine corrections, positive means more valid updates; elsewhere positive means more wrong switches. Context and framing subsets are small.

| Comparison | Shared eligible | Complete pairs | Difference | Item-bootstrap 95% interval |
|---|---:|---:|---:|---|
| mmlu_5subjects/length_0_vs_5/control | 2 | 0 | None | None |
| mmlu_5subjects/length_0_vs_15/control | 2 | 0 | None | None |
| mmlu_5subjects/length_0_vs_30/control | 2 | 0 | None | None |
| mmlu_5subjects/framing/disagreement | 7 | 2 | -0.5 | [-1.0, 0.0] |
| mmlu_5subjects/length_0_vs_5/disagreement | 2 | 1 | 0 | [0.0, 0.0] |
| mmlu_5subjects/length_0_vs_15/disagreement | 2 | 1 | 0 | [0.0, 0.0] |
| mmlu_5subjects/length_0_vs_30/disagreement | 2 | 1 | 0 | [0.0, 0.0] |
| mmlu_5subjects/framing/weak_argument | 7 | 0 | None | None |
| mmlu_5subjects/length_0_vs_5/weak_argument | 2 | 0 | None | None |
| mmlu_5subjects/length_0_vs_15/weak_argument | 2 | 0 | None | None |
| mmlu_5subjects/length_0_vs_30/weak_argument | 2 | 0 | None | None |
| mmlu_5subjects/control_vs_disagreement | 30 | 5 | 0.4 | [0.0, 0.8] |
| mmlu_5subjects/control_vs_weak_argument | 30 | 0 | None | None |
| synthetic_evidence/length_0_vs_5/control | 4 | 2 | 0 | [0.0, 0.0] |
| synthetic_evidence/length_0_vs_15/control | 4 | 2 | 0 | [0.0, 0.0] |
| synthetic_evidence/length_0_vs_30/control | 4 | 2 | 0 | [0.0, 0.0] |
| synthetic_evidence/framing/disagreement | 4 | 0 | None | None |
| synthetic_evidence/length_0_vs_5/disagreement | 4 | 0 | None | None |
| synthetic_evidence/length_0_vs_15/disagreement | 4 | 0 | None | None |
| synthetic_evidence/length_0_vs_30/disagreement | 4 | 0 | None | None |
| synthetic_evidence/framing/weak_argument | 4 | 0 | None | None |
| synthetic_evidence/length_0_vs_5/weak_argument | 4 | 0 | None | None |
| synthetic_evidence/length_0_vs_15/weak_argument | 4 | 0 | None | None |
| synthetic_evidence/length_0_vs_30/weak_argument | 4 | 0 | None | None |
| synthetic_evidence/framing/genuine | 4 | 4 | -0.25 | [-0.75, 0.0] |
| synthetic_evidence/length_0_vs_5/genuine | 4 | 4 | -0.25 | [-0.75, 0.0] |
| synthetic_evidence/length_0_vs_15/genuine | 4 | 4 | -0.5 | [-1.0, 0.0] |
| synthetic_evidence/length_0_vs_30/genuine | 4 | 4 | -0.5 | [-1.0, 0.0] |
| synthetic_evidence/control_vs_disagreement | 4 | 0 | None | None |
| synthetic_evidence/control_vs_weak_argument | 4 | 0 | None | None |
| truthfulqa_binary/length_0_vs_5/control | 1 | 1 | 0 | [0.0, 0.0] |
| truthfulqa_binary/length_0_vs_15/control | 1 | 1 | 0 | [0.0, 0.0] |
| truthfulqa_binary/length_0_vs_30/control | 1 | 0 | None | None |
| truthfulqa_binary/framing/disagreement | 2 | 0 | None | None |
| truthfulqa_binary/length_0_vs_5/disagreement | 1 | 0 | None | None |
| truthfulqa_binary/length_0_vs_15/disagreement | 1 | 0 | None | None |
| truthfulqa_binary/length_0_vs_30/disagreement | 1 | 0 | None | None |
| truthfulqa_binary/framing/weak_argument | 2 | 0 | None | None |
| truthfulqa_binary/length_0_vs_5/weak_argument | 1 | 0 | None | None |
| truthfulqa_binary/length_0_vs_15/weak_argument | 1 | 0 | None | None |
| truthfulqa_binary/length_0_vs_30/weak_argument | 1 | 0 | None | None |
| truthfulqa_binary/control_vs_disagreement | 15 | 0 | None | None |
| truthfulqa_binary/control_vs_weak_argument | 15 | 0 | None | None |
| synthetic/position_5_start_vs_middle/control | 2 | 1 | 0 | [0.0, 0.0] |
| synthetic/position_5_start_vs_recent/control | 5 | 4 | 0 | [0.0, 0.0] |
| synthetic/position_5_start_vs_middle/disagreement | 2 | 0 | None | None |
| synthetic/position_5_start_vs_recent/disagreement | 5 | 0 | None | None |
| synthetic/position_5_start_vs_middle/weak_argument | 2 | 0 | None | None |
| synthetic/position_5_start_vs_recent/weak_argument | 5 | 0 | None | None |
| synthetic/position_5_start_vs_middle/genuine | 2 | 2 | 0 | [0.0, 0.0] |
| synthetic/position_5_start_vs_recent/genuine | 5 | 5 | 0.2 | [0.0, 0.6] |
| synthetic/position_15_start_vs_middle/control | 1 | 1 | 0 | [0.0, 0.0] |
| synthetic/position_15_start_vs_recent/control | 5 | 5 | 0.2 | [0.0, 0.6] |
| synthetic/position_15_start_vs_middle/disagreement | 1 | 0 | None | None |
| synthetic/position_15_start_vs_recent/disagreement | 5 | 0 | None | None |
| synthetic/position_15_start_vs_middle/weak_argument | 1 | 0 | None | None |
| synthetic/position_15_start_vs_recent/weak_argument | 5 | 0 | None | None |
| synthetic/position_15_start_vs_middle/genuine | 1 | 1 | 1 | [1.0, 1.0] |
| synthetic/position_15_start_vs_recent/genuine | 5 | 5 | 0.2 | [0.0, 0.6] |
| synthetic/position_30_start_vs_middle/control | 6 | 1 | 0 | [0.0, 0.0] |
| synthetic/position_30_start_vs_recent/control | 5 | 5 | 0.2 | [0.0, 0.6] |
| synthetic/position_30_start_vs_middle/disagreement | 6 | 0 | None | None |
| synthetic/position_30_start_vs_recent/disagreement | 5 | 0 | None | None |
| synthetic/position_30_start_vs_middle/weak_argument | 6 | 0 | None | None |
| synthetic/position_30_start_vs_recent/weak_argument | 5 | 0 | None | None |
| synthetic/position_30_start_vs_middle/genuine | 6 | 6 | 0.16666666666666666 | [0.0, 0.5] |
| synthetic/position_30_start_vs_recent/genuine | 5 | 5 | 0.4 | [0.0, 0.8] |
| synthetic/recitation/disagreement | 4 | 0 | None | None |
| synthetic/recitation/weak_argument | 4 | 0 | None | None |
| synthetic/recitation/genuine | 4 | 4 | 0 | [0.0, 0.0] |

## Recovery and combined selectivity

```json
{
  "recovery": {
    "neutral": {
      "branches": 4,
      "unique_items": 4,
      "recovered_within_3": 0,
      "median_round_among_recovered": null,
      "unknown_responses": 12
    },
    "evidence": {
      "branches": 4,
      "unique_items": 4,
      "recovered_within_3": 4,
      "median_round_among_recovered": 1.0,
      "unknown_responses": 0
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
