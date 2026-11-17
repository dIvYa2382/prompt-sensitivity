#!/usr/bin/env bash
# Runs the AI-generated starter code (Prompts 08, 09, 13) unchanged on real labels and checks
# that its mean agreement equals our S_p(D_cat) for the same model/evaluator/items.
set -euo pipefail
cd "$(dirname "$0")/.."
W=results/starter_check; rm -rf "$W"; mkdir -p "$W/results"
python3 -I - <<'PY'
import sys; sys.path.insert(0,'src')
import pandas as pd
from parsers import e3_wordboundary
df = pd.read_csv('data/outputs_long.csv').merge(pd.read_csv('data/split.csv'), on='item_id')
d = df[(df.split=='test') & (df.model=='phi3_mini')].copy()
d['conclusion_category'] = d.raw.map(e3_wordboundary)
d.rename(columns={'variant':'prompt_variant'})[['item_id','prompt_variant','conclusion_category','raw','model']] \
  .to_csv('results/starter_check/results/conclusion_labels.csv', index=False)
PY
cd "$W"
echo "--- Prompt 08 environment_test.py"; python3 -I ../../starter_ai_code/environment_test.py
echo "--- Prompt 09 agreement_baseline.py"; python3 -I ../../starter_ai_code/agreement_baseline.py | tail -2
echo "--- Prompt 13 evaluate_template.py"; python3 -I ../../starter_ai_code/evaluate_template.py | tail -2
cd ../..
python3 -I -c "
import pandas as pd
a=pd.read_csv('results/starter_check/results/item_agreement.csv').conclusion_category_agreement.mean()
m=pd.read_csv('results/tables/main_by_evaluator_model.csv'); b=m[(m.evaluator=='E3_wordboundary')&(m.model=='phi3_mini')].S_cat.item()
print(f'starter mean agreement {a:.6f} | our S_p(D_cat) {b:.6f} | equal: {abs(a-b)<1e-12}')"
