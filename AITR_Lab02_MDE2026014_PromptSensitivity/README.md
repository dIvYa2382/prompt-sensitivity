# Same Evidence, Different Conclusion?
### Measuring conclusion-level prompt stability and its evaluation artifacts on public model outputs

Author: **Divya Joshi (MDE_14, enrolment MDE2026014)**. Course: AI Tools for Research, post-mid-semester implementation paper.
Earlier review: *Prompt Sensitivity and Its Effect on the Stability of LLM-Generated Research Conclusions* (ACM acmsmall format).
Pathway: **B, a controlled comparison** of evaluators and stability definitions on identical, real model outputs (Prompts 07 and 12), applied to the review's gaps G1 (conclusion-level stability) and G2 (evaluation artifacts). G5 (CSI weights) is tested as far as the data allow. G3 (prompt versus sampling variance) cannot be tested on these data and is reported as a limitation.

## What was done
No model was called. We reuse the **public raw outputs** of Hariprasad (2026, arXiv:2603.00917):
* 5 small open models answered 200 PubMedQA questions.
* Each question came with a fixed abstract and was asked in 5 prompt styles, giving 5,000 outputs.
* Within an item, the evidence and the question are byte-identical across styles (verified 200/200).
* Each answer is a research conclusion: yes = supports, no = contradicts, maybe = insufficient.

Protocol:
* 50 development items were used to write the answer parser.
* The parser, the config and the hypotheses H1–H3 were then frozen with SHA-256 hashes.
* The 150 test items were analysed once.

## Headline results (150 test items, primary parser E3; 95% bootstrap CIs over items)
| Model | S_p (D_cat) | Changed conclusion | Polarity reversal | Uncertainty shift | Valid answers | Accuracy |
|---|---|---|---|---|---|---|
| Phi-3 Mini | 0.827 [0.80, 0.85] | 60.7% | 10.0% | 50.7% | 100.0% | 42.9% |
| Llama 3.2 | 0.795 [0.76, 0.83] | 56.0% | 31.3% | 20.7% | 96.5% | 60.3% |
| Gemma 2 | 0.843 [0.81, 0.87] | 50.7% | 0.7% | 42.0% | 98.0% | 34.7% |
| Mistral | 0.845 [0.81, 0.88] | 46.0% | 0.0% | 23.3% | 91.1% | 37.1% |
| Meditron | 0.996 [0.99, 1.00] | 2.0% | 0.0% | 0.0% | 0.4% | 0.3% |

* **Baseline reproduced exactly.** All 100/100 cells of the source study's published PubMedQA summary were recomputed, both from the stored labels and from raw text.
* **RQ1 – conclusions change.** With the evidence fixed, each instruction-following model changed its conclusion on 46–61% of items. Most changes are uncertainty shifts. Llama 3.2 alone reverses polarity often.
* **RQ2 – the parser matters.**
  * Strict exact-match scoring lowers S_p by up to 0.31 and accuracy by up to 31 points, and it reorders the models.
  * The published substring parser reads "Maybe. The text does not provide…" as **no**. This happens in 41 test outputs, plus 21 non-answers read as "no".
  * The effect on S_p is small (≤ 0.013), but Mistral's uncertainty-shift rate rises by 10 points and accuracy rises by up to 2.1 points.
* **Distance and non-answer artifact.** Meditron answers almost nothing, yet its S_p is 0.996 under one definition and 0.004 under the published one.
* **RQ3 – stability ≠ accuracy.**
  * Stability and accuracy rank the four working models in exactly reverse order (Kendall τ = −0.67).
  * Gemma 2 and Mistral are "stable" mostly because they consistently answer "maybe". They are stable but wrong on 46 and 43 of 150 items.
  * Two models disagree more than two prompts do: 0.47 vs. 0.28 of pairs.
  * Under random CSI weights, 7 different model rankings appear.
* **Hypotheses.** H1 supported. H2 supported only at its threshold (one model, 3 items). H3 supported.

## Layout
```
configs/experiment.json        frozen protocol, metrics and H1–H3 (hash in results/logs/06_freeze_hashes.log)
src/data.py                    loads the public JSON outputs (data only)
src/parsers.py                 E1 strict, E2 published substring (re-implemented), E3 word-boundary (ours)
src/metrics.py                 S_p (review Eq. 7) with D_cat / D_ord, flags, Errica et al. metrics
scripts/fetch_data.sh          clones the source repo at the pinned commit
scripts/validate_data.py       Gate: structure, evidence identity, leakage, extractor replay, dev/test split
scripts/reproduce_published.py baseline reproduction of the published summary
scripts/analyze.py             all test-split analyses (RQ1–RQ3, robustness, CSI weights, hypotheses)
scripts/run_starter_check.sh   runs the AI starter code (Prompts 08/09/13) unchanged on real labels
scripts/describe_labels.py     label distributions (post-hoc descriptive add-on)
scripts/make_figures.py, make_tables.py, run_all.sh
tests/test_metrics.py          6 unit tests (Prompt 09 toy cases + real-output parser cases)
starter_ai_code/               AI-generated code from Prompts 08, 09, 13, unchanged
annotation/                    100-output sample for blind human labelling + sealed key + guidelines
results/                       tables/*.csv, summary.json, logs/ (numbered, incl. both debug episodes)
paper/                         main.tex, references.bib, bib_verification.md, generated/, figures/, main.pdf
docs/research_brief.md         one-page brief
research_decisions.md  baseline_validation.md  ai_assistance_log.md
```

## Reproduce
A fresh copy reproduced all 28 generated files byte for byte; see `results/logs/12_fresh_copy_reproduction.log`.
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt     # [TEST REQUIRED] not run here; packages were preinstalled
bash scripts/fetch_data.sh          # git clone at commit 4c82a7b6 into data_raw/ (only JSON/CSV files are read)
bash scripts/run_all.sh             # < 10 s on a laptop CPU
cd paper && pdflatex main && bibtex main && pdflatex main && pdflatex main   # or upload paper/ to Overleaf
```
* No GPU, no API keys and no model calls.
* Seed 2026 is used for the split, the bootstrap, the CSI weights and the annotation sample.

## Data and licence
* Raw outputs: https://github.com/shravani-01/clinical-llm-eval (commit `4c82a7b6`). The paper is CC BY 4.0, but the repository has **no licence file**. Its outputs are therefore **not redistributed** here: `data/` is created by the scripts, and `fetch_data.sh` downloads the source.
* PubMedQA: Jin et al. (2019), MIT licence.
* The source repository's Python code is never imported or executed.

## Author to-dos before submission
1. Fill in department and institute in `paper/main.tex` (`\affiliation`).
2. Label `annotation/human_annotation_sample.csv` blind, following `annotation/guidelines.md`, then compare with the key. This validates the parser. It is optional, but it is the cheapest strengthening.
3. Check the remaining `[TO VERIFY]` items in `paper/bib_verification.md`. The review's Liu et al. (2024) author list has been corrected there.
4. Push this folder to GitHub as `AITR_Lab02_MDE2026014_PromptSensitivity`.
