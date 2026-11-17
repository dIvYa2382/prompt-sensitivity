# AI Assistance Log
This log follows the assignment's disclosure requirement: what the AI produced, what was accepted, modified or rejected, and how it was checked.

| # | Stage | Tool | What the AI produced | Decision | Verification |
|---|---|---|---|---|---|
| 1 | Prompts 01–02 | ChatGPT (author's sessions) | Gap matrix (G1–G5) and decision log D-01…D-05 | Accepted as the planning basis | Re-checked against the review text |
| 2 | Prompts 03–07 | ChatGPT | Pathway B plan, RQ1/RQ2 wording, frozen-protocol checklist | Accepted. Optional RQ3 (structured-evidence prompt) dropped, because no generation was possible (D-07) | — |
| 3 | Prompt 08 | ChatGPT | Environment smoke test | Accepted unchanged (`starter_ai_code/environment_test.py`) | Ran: PASS, Python 3.13, pandas 3.0.5, NumPy 2.5.3 (logs/02) |
| 4 | Prompt 09 | ChatGPT | Agreement baseline (majority share) | Accepted unchanged | Ran on real labels. Equals our S_p(D_cat) to machine precision (logs/02) |
| 5 | Prompt 13 | ChatGPT | Evaluation template with schema and duplicate checks | Accepted unchanged | Ran on real labels: n_items 150, mean 0.827 (logs/02) |
| 6 | Prompts 10, 11, 14 | ChatGPT | Validation, debugging and interpretation templates | Used as structure for `baseline_validation.md`, the debug logs and the Results/Discussion sections | Filled only with logged evidence |
| 7 | Data search | Claude (this session) | Found the clinical-llm-eval public raw outputs and checked that they fit P=(I,Q,C,F) | Accepted after the evidence-identity check (200/200) | logs/03 |
| 8 | Code | Claude | `src/`, `scripts/`, `tests/` | Accepted after tests and reproduction | 6 unit tests; 100/100 published cells reproduced; fresh-copy run 28/28 identical |
| 9 | Debugging | Claude | Bug 1: `df.style` is a pandas accessor → column renamed `variant` | Fixed before any result existed | logs/04 |
| 10 | Debugging | Claude | Bug 2: H2 threshold compared in floating point (3/150 < 0.02) | Fixed with a tolerance. Old and new logs kept; the paper calls H2 weak | logs/08, 08b, 09 |
| 11 | Parser design | Claude | E3 rules, plus one dev-phase hedge rule | Accepted. Frozen before the test run | logs/05, logs/06 |
| 12 | Literature check | Claude + web search | Verified bibliographic data for Hua, Errica, ProSA, POSIX, DOVE, Hariprasad, PubMedQA. Corrected two author names in the review's Liu et al. (2024) | Accepted | paper/bib_verification.md |
| 13 | Writing | Claude | Draft of paper, README and reports | The author must read and edit everything before submission | All numbers are macros generated from results (paper/generated) |
| 14 | Rejected | — | Claude producing the human labels for the annotation sample | Rejected | The parser's author must not validate it. Left for the student (D-22) |
| 15 | Rejected | — | Computing a single CSI with arbitrary weights | Rejected | Replaced by the weight-sensitivity analysis (D-17) |

**Safety note.** The source repository was cloned as data only. None of its Python code was imported or executed; all scripts run with `python -I`.
