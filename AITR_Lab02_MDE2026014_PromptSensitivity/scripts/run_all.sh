#!/usr/bin/env bash
# Full pipeline. Needs data_raw/clinical-llm-eval (run scripts/fetch_data.sh first).
# Every script reads only data files and runs with python -I (isolated mode).
set -euo pipefail
cd "$(dirname "$0")/.."
REPO=${REPO:-data_raw/clinical-llm-eval}
mkdir -p results/logs results/tables
PY="python3 -I"
$PY tests/test_metrics.py                         | tee results/logs/01_unit_tests.log
$PY scripts/validate_data.py --repo "$REPO"       | tee results/logs/03_data_validation.log
sha256sum src/parsers.py src/data.py configs/experiment.json | tee results/logs/06_freeze_hashes_check.log
$PY scripts/reproduce_published.py --repo "$REPO" | tee results/logs/07_baseline_reproduction.log
$PY scripts/analyze.py                            > results/logs/08b_test_analysis_after_float_fix.log
bash scripts/run_starter_check.sh                 | tee results/logs/02_starter_code_runs.log
$PY scripts/describe_labels.py                    > results/logs/10_label_description.log
$PY scripts/make_figures.py                       > results/logs/11_figures.log
$PY scripts/make_tables.py
echo "done. Compile the paper: cd paper && pdflatex main && bibtex main && pdflatex main && pdflatex main"
