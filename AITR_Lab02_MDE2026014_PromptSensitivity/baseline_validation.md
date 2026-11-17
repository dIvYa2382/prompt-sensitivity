# Baseline Validation Report
This report completes the template from Prompt 10. The status labels are VERIFIED, UNCERTAIN and NEEDS CORRECTION.

**Baseline**: the PubMedQA results of Hariprasad (2026), arXiv:2603.00917. They come from the public repository `shravani-01/clinical-llm-eval` at commit `4c82a7b6`:
* raw outputs in `results/raw/pubmedqa_<model>.json`;
* published summary in `results/summary/master_summary.csv`;
* extractor `extract_answer_pubmedqa` and scorer `consistency_scorer.py`. We read these as text and did not run them.

## Checklist (Prompt 10 §2)
| Area | Question | Status | Evidence |
|---|---|---|---|
| Source fidelity | Does our implementation match the original operational definitions? | VERIFIED | Extractor re-implemented verbatim: 5,000/5,000 labels match the stored `extracted` field (logs/03). Published consistency, majority and accuracy definitions re-implemented: 100/100 summary cells match (logs/07). |
| Data | Are items and variants linked by IDs? | VERIFIED | 5 models × 200 items × 5 styles. Questions and gold labels agree across models and with `pubmedqa_sample.csv` (200/200) (logs/03). |
| Prompt equivalence | Do variants keep the question, evidence and output requirement? | VERIFIED (Q, C) / UNCERTAIN (I, F) | The evidence and question strings are identical in all 5 styles for 200/200 items. Styles differ in persona and in the answer-format line; roleplay and direct lack "only". Robustness without roleplay is in results/tables/robustness.csv. |
| Model/version | Are the exact model identifiers recorded? | UNCERTAIN | The source names Ollama tags (phi3_mini, llama3.2, gemma2, mistral, meditron). Exact Ollama digests and the inference date are not in the repository. |
| Settings | Are the decoding settings consistent? | VERIFIED as reported | temperature 0, `num_predict` 10, one run per prompt (source `src/inference.py`, read only). |
| Metrics | Are the agreement calculations correct? | VERIFIED | 6 unit tests incl. the Prompt 09 toy cases (logs/01). The starter `agreement_baseline.py` gives the same value as our S_p(D_cat) (logs/02). |
| Reproducibility | Can the summary be regenerated without calling a model? | VERIFIED | A fresh copy reproduced 28/28 generated files byte for byte (logs/12). |
| Factuality | Are conclusions checked against evidence? | VERIFIED (against gold) / NOT TESTED (human) | Accuracy against the PubMedQA expert labels is reported. The human check of our parser is pending (annotation/). |

## Sanity tests (Prompt 10 §3)
| Test | Result |
|---|---|
| Schema | Every record has id, question, gold label, and raw + extracted output for 5 styles. **PASS** |
| Alignment | Each output maps to one (model, item, style). The pivot has no duplicates. **PASS** |
| Duplicates | No duplicate (model, item, style) rows; the starter `evaluate_template.py` duplicate check passed. **PASS** |
| Metric toy cases | supports×3 → 1.0; 2 of 3 → 0.667; single variant → 1.0; 4-way tie → 0.25. **PASS** |
| Leakage | The gold label is never in a prompt. The authors' conclusion text was searched in all prompts: 1 hit (item 65), which on inspection was the intervention name, a false positive (logs/03b). **PASS** |
| Re-run from saved outputs | Yes: all results are computed from saved outputs. **PASS** |

## Reproduced numbers (all 200 items; identical from stored labels and from raw text)
| Model | Consistency | Fully consistent | Accuracy % | UNKNOWN % | orig | formal | simpl | role | direct |
|---|---|---|---|---|---|---|---|---|---|
| Phi-3 Mini | 0.830 | 82 | 48.0 | 0.0 | 42.5 | 53.5 | 52.5 | 47.5 | 31.0 |
| Llama 3.2 | 0.807 | 91 | 65.0 | 2.8 | 59.5 | 51.0 | 64.5 | 65.0 | 56.5 |
| Gemma 2 | 0.845 | 101 | 33.0 | 1.3 | 28.0 | 41.5 | 47.5 | 27.0 | 30.5 |
| Mistral | 0.825 | 99 | 42.5 | 7.2 | 39.5 | 39.5 | 45.5 | 34.5 | 45.5 |
| Meditron | 0.010 | 0 | 2.0 | 99.0 | 0.0 | 0.0 | 1.5 | 0.0 | 0.5 |

All 100/100 values equal `master_summary.csv` (tolerance 0.05 for rounded values; integer counts exact).

## Discrepancies and caveats found during validation
* **NEEDS CORRECTION (in the source's interpretation, not in its numbers).** The published extractor checks for the substring "no" before "maybe". Hedged answers such as "Maybe. The text does not provide…" are therefore scored "no". On the 150 test items this happens in 41 outputs, and in 21 more a non-answer becomes "no" (results/tables/transitions_E2_E3.csv). We keep the extractor for the reproduction and use E3 as the primary parser.
* **UNCERTAIN.** The published consistency excludes UNKNOWN from the vote but divides by all 5 styles, so a model that fails to answer gets consistency near 0. With a categorical distance, the same model would get near 1. Both are reported.
* **UNCERTAIN.** The evidence is truncated at 1,000 characters (177/200 items) and keeps a `{'contexts': [...]` wrapper. Every style sees the same text, so within-item comparisons are fair, but accuracy is affected.
* **UNCERTAIN.** Outputs are capped at 10 tokens, so some answers stop before the conclusion and count as INVALID.

## Gate decision
The baseline passes the input validation, metric unit tests, settings logging and reproduction checks. Prompt equivalence is verified for C and Q and partly for I and F, so a robustness analysis was added. Parser validity awaits human labels. The extension (test-split analysis) proceeded after the freeze on this basis.
