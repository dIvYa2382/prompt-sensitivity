# Research brief (one page)
**Question.** If an LLM is given the same evidence and the same research question, does rewording the prompt change the conclusion it draws? And how much does the measured answer depend on how outputs are scored?

**Data.** We use 5,000 recorded outputs from Hariprasad (2026):
* 5 small open models × 200 PubMedQA abstracts × 5 prompt styles;
* the evidence and the question are identical across styles;
* each answer is a yes/no/maybe conclusion.

**Method.**
* Reproduce the published summary.
* Split into 50 dev / 150 test items.
* Write the parser on dev, then freeze it.
* On test, measure S_p (review Eq. 7) with an explicit distance, and separate polarity reversals from uncertainty shifts.
* Compare three parsers on identical outputs.
* Relate stability to accuracy; compare prompt-induced with model-induced disagreement; test CSI weight sensitivity.

**Findings.**
1. Conclusions change on 46–61% of items for every instruction-following model. Most changes are uncertainty shifts; Llama 3.2 reverses polarity on 31%.
2. Strict matching cuts measured stability by up to 0.31. The published substring parser turns hedges into "no", which changes the type of instability and inflates accuracy.
3. Stability and accuracy rank the models in reverse order. The most stable models mostly answer "maybe" (stable abstention).
4. Model choice causes more disagreement than wording (0.47 vs 0.28 of pairs).
5. CSI rankings depend on the weights: 7 orderings appeared.

**Implications for the review.**
* Report reversal and uncertainty-shift rates separately.
* Fix D, C̄ and the handling of non-answers in Eq. 7.
* Always report the valid-answer rate and accuracy next to stability.
* Justify the CSI weights.

**Not tested.** Sampling variance (G3; single temperature-0 run), and human validation of the parser (sample prepared).
