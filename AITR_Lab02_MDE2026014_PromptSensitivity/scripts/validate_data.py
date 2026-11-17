"""Data validation + dev/test split (Gate G2).

Checks: 5 models x 200 items x 5 styles present; item ids, questions and gold labels agree
across models and with the sampled PubMedQA CSV; the evidence text inserted in the five
prompt styles is identical for every item; the gold label never appears in a prompt;
our re-implementation of the published extractor reproduces its stored 'extracted' field.
Writes data/outputs_long.csv and data/split.csv.
Usage: python -I scripts/validate_data.py --repo ../data_raw/clinical-llm-eval
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import numpy as np, pandas as pd
from data import load_long, load_prompts, load_sample, MODELS, STYLES
from parsers import e2_substring

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
a = ap.parse_args()
cfg = json.load(open("configs/experiment.json"))
df = load_long(a.repo)
P = load_prompts(a.repo)
S = load_sample(a.repo)
print("rows:", len(df), "| models:", df.model.nunique(), "| items/model:", df.groupby("model").item_id.nunique().unique(),
      "| styles:", sorted(df.variant.unique()))
assert len(df) == len(MODELS) * 200 * len(STYLES)
g = df.groupby("item_id").agg(q=("question", "nunique"), gold=("gold", "nunique"))
print("items whose question or gold label differs across models:", int(((g.q > 1) | (g.gold > 1)).sum()))
gold_csv = dict(zip(range(len(S)), S.final_decision))
q_csv = dict(zip(range(len(S)), S.question))
first = df.drop_duplicates("item_id").set_index("item_id")
print("gold label == sampled CSV final_decision (row order):", int(sum(first.gold[i] == gold_csv[i] for i in first.index)), "/ 200")
print("question == sampled CSV question (row order):", int(sum(first.question[i] == q_csv[i] for i in first.index)), "/ 200")
LBL = {"original": "Context: ", "formal": "Abstract: ", "simplified": "Text: ", "roleplay": "Excerpt: ", "direct": "Context: "}
same, lens, leak = 0, [], 0
for p in P:
    ev = set()
    for k, s in p["prompts"].items():
        i = s.find(LBL[k]) + len(LBL[k])
        j = s.find("\n\nQ:", i) if k == "direct" else s.find("\n\n", i)
        ev.add(s[i:j])
    same += len(ev) == 1
    lens.append(len(next(iter(ev))))
    long_ans = S.long_answer.iloc[p["id"]]
    leak += any(str(long_ans)[:60] in s for s in p["prompts"].values())
print(f"identical evidence across the 5 styles: {same}/200 | evidence chars min/median/max: {min(lens)}/{int(np.median(lens))}/{max(lens)} "
      f"| evidence cut at 1000 chars: {sum(l >= 990 for l in lens)} | long_answer (author conclusion) text found in a prompt: {leak}")
rep = (df.raw.map(e2_substring).replace("INVALID", "UNKNOWN") == df.extracted_orig)
print("published extractor re-implemented: matches stored 'extracted' field in", int(rep.sum()), "/", len(df))
print("gold distribution:", first.gold.value_counts().to_dict())
df.to_csv("data/outputs_long.csv", index=False)
rng = np.random.default_rng(cfg["split"]["seed"])
perm = rng.permutation(np.arange(200))
dev = set(perm[:cfg["split"]["n_dev"]].tolist())
pd.DataFrame({"item_id": range(200), "split": ["dev" if i in dev else "test" for i in range(200)]}).to_csv("data/split.csv", index=False)
print("split: dev", len(dev), "test", 200 - len(dev))
