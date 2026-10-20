# Qwen2.5-3B: conclusions from the multi-dataset pilot

Run: `experiments/multidataset-qwen3b-001`. The generated report and analysis JSON contain all denominators, per-condition metrics, matched contrasts and uncertainty estimates. Raw requests and responses are preserved in `calls.jsonl.gz`.

## What was actually tested

106 distinct questions: 50 binary TruthfulQA adaptations, 50 four-option MMLU questions from five selected subjects, and six simple fictional-record questions. There were 2,167 local model calls, not 2,167 independent questions. The model was Qwen2.5-3B Q4_K_M. Structured answer output allowed UNKNOWN. This differs from the earlier free-form pilot and the scores must not be pooled.

The sparse design tested five pressure rounds; 0/5/15/30 short filler exchanges; start/middle/recent evidence positions on synthetic items; first/third-person framing on a subset; genuine corrections; evidence re-citation during pressure; and paired recovery reminders after a first wrong switch. The longest prompt was 2,050 tokens, so this is not a long-context-window experiment.

## Findings supported within this run

1. **Direct disagreement exposed wrong-answer switches in both factual samples.** Among initially correct questions, MMLU had 18/30 observed switches under disagreement versus 4/30 under neutral reconsideration. TruthfulQA had 4/15 versus 1/15. All 18 MMLU disagreement switchers adopted the targeted wrong option at least once. These describe this prompt setup and selected samples, not a universal model score.
2. **Abstention is a major outcome.** There were 963 explicit UNKNOWN responses and zero truncated outputs or invalid structured outputs. At baseline, TruthfulQA had 15 correct, 3 wrong and 32 unknown answers; MMLU had 30 correct, 10 wrong and 10 unknown. Low wrong-switch rates in the weak-argument condition do not imply robust truth retention: every eligible factual weak-argument conversation included an abstention.
3. **Wrong switches often happened immediately.** The median exact first wrong turn among observed flippers was round 1 in the main disagreement conditions. This is conditional on observed flips; it does not describe non-flippers or resolve cases with an earlier unknown.
4. **Valid updating and susceptibility can coexist.** Four synthetic items were baseline-correct at zero filler. All four accepted the explicit version-2 correction. All four also switched to the unsupported wrong target under direct disagreement. Final stubbornness was 0/4 in the first-person genuine-correction condition.
5. **Recovery was promising but very small-scale.** Re-presenting original evidence after a wrong switch restored the correct answer in 4/4 paired synthetic cases, on the first reminder. Neutral reminders recovered 0/4; all their recovery responses were UNKNOWN. This contrast cannot be generalised from four cases.
6. **Prevention did not reliably work.** Re-citing evidence while continuing disagreement still produced wrong switches in 4/4 short synthetic cases. It preserved genuine updating in 4/4. Recovery after a flip and prevention during pressure are different interventions and had different results here.

## Parameters that remain inconclusive

- **Length and evidence position:** tested, but comparisons often have only 1-6 matched eligible items. Results do not establish a general monotonic length effect or a reliable middle-position penalty. In four matched synthetic items, final valid updating fell from 4/4 at zero filler to 2/4 at 15 and 30 filler exchanges with evidence at the start. This is a hypothesis for replication, not a confirmed effect.
- **Framing:** third-person disagreement had fewer observed switches in the seven matched MMLU cases and four synthetic cases, but abstention and tiny samples limit interpretation. It also reduced final valid updating from 4/4 to 3/4 in the synthetic subset, so it is not an established safe fix.
- **Combined selectivity score:** not estimable under the prespecified complete-case rule; no synthetic item had fully observed option answers in all required unsupported-pressure branches. No missing answers were imputed to manufacture a score.
- **Number of flips and survival:** computed in the analysis file. Unknowns break observable transitions; survival curves censor at the first unknown. Informative abstention makes causal or population interpretations unreliable.

## What this does not establish

This is a development pilot, not a publication-ready evaluation. Source keys have not been independently adjudicated, synthetic items are simple, samples are small, many exploratory comparisons were examined, and only one quantized model and one deterministic setup were used. No hidden-state mechanisms, flattery, personalised memory, stochastic robustness or cross-model generalisation were measured.

The next defensible study should validate the item bank; treat abstention explicitly; compare answer formats on held-out items; expand matched synthetic cases; and replicate recovery and prevention on another model. Do not choose prompts or exclusions solely to increase the desired effect.
