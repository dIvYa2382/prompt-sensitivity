# Research Decisions Log (continued)
Project: Lab 02 – AI Tools for Research
Topic: Prompt sensitivity and the stability of LLM-generated research conclusions
Author: Divya Joshi (MDE2026014)

The evidence labels are the same as in the 21 October 2026 log:
* **VERIFIED**: confirmed in a source or an executed run, with the log file named.
* **INFERRED**: an interpretation.
* **UNKNOWN**: no evidence yet.

## Earlier decisions (from the 21 Oct log) and how they were closed
| ID | Decision | Status now |
|---|---|---|
| D-01 | Stay within prompt sensitivity and the stability of research conclusions | Kept. G1 and G2 were chosen from research_gaps.md. |
| D-02 | Verify the primary publications [3], [4], [5], [6], [11], [12], [17] | Done for [3], [5], [6], [17] plus the 3 new sources (paper/bib_verification.md). [4], [11], [12] are cited only for their topic. |
| D-03 | Treat Eq. 3, Eq. 7 and the CSI as conceptual; define D explicitly | Done. D_cat and D_ord are defined, and C̄ is the distance minimiser (paper §3.4). |
| D-04 | Defer novelty claims | Kept. The paper claims no new method, only a measurement. |
| D-05 | Provisionally favour Pathway B | Confirmed (D-07). |

## New decisions
| ID | Date | Decision | Alternatives considered | Rationale | Evidence |
|---|---|---|---|---|---|
| D-06 | 17 Nov | Use public, recorded outputs instead of generating new ones | (a) call an API: no access or budget in this environment; (b) run a local model: no GPU, and the sandbox could not install torch; (c) DOVE predictions: Hugging Face blocked, and they cover multiple-choice benchmarks, not conclusions | Prompts 09 and 13 forbid invented outputs. The clinical-llm-eval PubMedQA data fit the review's P=(I,Q,C,F) exactly: C and Q fixed, I and F varied, and the answer is a conclusion | VERIFIED, logs/03 |
| D-07 | 17 Nov | Pathway B: compare three parsers and two distances on identical outputs; RQ3 (structured-evidence prompt, Pathway C) dropped | Pathway C needs new generations | This answers G1 and G2 directly and needs no model access | INFERRED |
| D-08 | 17 Nov | Read only the source repository's JSON/CSV files; never import or run its code | Run its scorer | This is safer, and it makes our reproduction independent. Our re-implementation matched its stored labels 5,000/5,000 | VERIFIED, logs/03 |
| D-09 | 17 Nov | Do not redistribute the raw outputs; fetch them at a pinned commit | Commit a copy | The source repository has no licence file | VERIFIED |
| D-10 | 17 Nov | Item-level split, seed 2026: 50 dev / 150 test. Parser rules are written on dev only | Use all 200 items | The parser is our own instrument, so tuning it on test items would bias RQ2 | VERIFIED, data/split.csv |
| D-11 | 17 Nov | Primary parser E3 (word boundary + hedge → maybe). E1 and E2 are comparators | Make E2 primary because it is published | E2 maps "Maybe … not …" to "no" (observed on dev items) | VERIFIED, logs/05 |
| D-12 | 17 Nov | One dev-phase parser change: added "does not provide enough …" as a hedge | None | It was seen in Gemma 2 dev outputs. The change was made before the freeze, and the diff is kept | VERIFIED, logs/05 |
| D-13 | 17 Nov | INVALID counts as its own category in S_p; the published definition is reported alongside | Drop INVALID outputs | Dropping them would hide format failures. Reporting both shows the definition artifact (Meditron 0.996 vs 0.004) | VERIFIED, results/tables |
| D-14 | 17 Nov | Split instability into polarity reversal, uncertainty shift and format instability; add D_ord | Report a single S_p | The review's inferential-stability argument needs this distinction | INFERRED → results show it matters |
| D-15 | 17 Nov | Freeze before the test run: SHA-256 of parsers, loader and config, with H1–H3 thresholds in the config | None | Assignment requirement | VERIFIED, logs/06 |
| D-16 | 17 Nov | Bootstrap over items (10,000 resamples), paired when comparing parsers | Treat model × item outputs as independent | The item is the sampling unit; the outputs of one item are not independent | VERIFIED |
| D-17 | 17 Nov | CSI: report its components separately and test ranking robustness under Dirichlet(1,1,1) weights; do not compute a single CSI | Pick equal weights | The review gives no weights; the evidence and semantic components are not measurable from 10-token outputs | VERIFIED, summary.json |
| D-18 | 17 Nov | Fix the H2 threshold comparison after the run (floating point: 3/150 evaluated below 0.02) | Leave H2 as "not supported" | That would be a code bug, not a result. The fix, the old log and the new log are all kept, and the paper calls H2 weak | VERIFIED, logs/08, 08b, 09 |
| D-19 | 17 Nov | Treat item 65's leakage-check hit as a false positive, and keep a robustness row without it | Exclude the item | Manual inspection showed it was the intervention name, not the conclusion | VERIFIED, logs/03b |
| D-20 | 17 Nov | Robustness: drop roleplay (persona + no "only" format line; review §8.5) | Drop the direct style too | Pre-planned in Prompt 07 as the only equivalence concern raised | VERIFIED, results/tables/robustness.csv |
| D-21 | 17 Nov | Post-hoc descriptive add-ons, labelled as such: label distributions, stable-wrong detail, per-style valid rates, accuracy range | None | They explain the RQ3 results; no hypothesis depends on them | VERIFIED, logs/10 |
| D-22 | 17 Nov | Human annotation is left to the author: a seeded 100-output sample with a sealed key | Let Claude label | Labels written by the AI that built the parser would not validate it | VERIFIED, annotation/ |
| D-23 | 17 Nov | G3 (sampling variance) is declared untestable and kept as the first follow-up | Estimate it from model disagreement | There is a single temperature-0 run per prompt | VERIFIED |

## Order of work (honest timeline)
* Data validation, split, dev inspection, parser change and freeze came **before** any test metric.
* The unit tests and the starter-code check were written **after** the main run. They test the frozen code, which was not changed for them.
* The log numbers follow pipeline order, not clock order.
