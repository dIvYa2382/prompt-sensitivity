#!/usr/bin/env bash
# Fetch the public raw outputs used in this study (data only; no code from the repository is executed).
# Source: Hariprasad (2026), arXiv:2603.00917 -- https://github.com/shravani-01/clinical-llm-eval
set -euo pipefail
cd "$(dirname "$0")/.."
COMMIT=4c82a7b6baac175ea2de77e7a78804b8a7018943
DEST=data_raw/clinical-llm-eval
mkdir -p data_raw
if [ ! -d "$DEST/.git" ]; then
  git clone --quiet https://github.com/shravani-01/clinical-llm-eval "$DEST"
fi
git -C "$DEST" checkout --quiet "$COMMIT"
echo "pinned commit: $(git -C "$DEST" rev-parse HEAD)"
sha256sum "$DEST/data/prompts/pubmedqa_prompts.json" "$DEST"/results/raw/pubmedqa_*.json "$DEST/results/summary/master_summary.csv"
