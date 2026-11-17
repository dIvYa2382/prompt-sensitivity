# data/
This folder is **generated**; nothing in it is committed from the source.
* `outputs_long.csv`: one row per (model, item, prompt variant) with the raw output, the source's stored label, the gold label and the question. Written by `scripts/validate_data.py` from `data_raw/clinical-llm-eval` (fetched by `scripts/fetch_data.sh` at commit 4c82a7b6).
* `split.csv`: item-level dev/test split (seed 2026; 50/150).

The source repository has no licence file, so do not commit `outputs_long.csv` to a public repository. Add `data/*.csv` and `data_raw/` to `.gitignore` (already done).
