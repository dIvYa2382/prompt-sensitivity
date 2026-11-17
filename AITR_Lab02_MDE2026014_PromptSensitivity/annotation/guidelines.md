# Blind annotation guidelines (parser validation)
File: `human_annotation_sample.csv` contains 100 test outputs, seed 2026:
* 40 outputs where the published parser (E2) and our parser (E3) disagree;
* 60 random outputs from the four instruction-following models.

Do **not** open `annotation_key_DO_NOT_OPEN_BEFORE_LABELLING.csv` until you finish.

For each `raw` output (the first 10 tokens the model produced), write in `human_label`:
* **yes**: the output commits to yes / the evidence supports the claim;
* **no**: the output commits to no / the evidence contradicts it;
* **maybe**: the output says the answer is uncertain, unclear, or that the evidence is insufficient or not provided;
* **invalid**: there is no conclusion (prompt echo, chatter, or an answer cut off before any conclusion).

Rules:
* Judge only what the text says. Do not look up the question, and do not guess what the model would have said with more tokens.
* If the output says "Maybe" and then explains why, label it maybe.
* Use `annotator_note` for hard cases.

Afterwards, compute agreement with each parser: accuracy, and Cohen's kappa if two people label. Report it in §7 (Parser validity) of the paper.
