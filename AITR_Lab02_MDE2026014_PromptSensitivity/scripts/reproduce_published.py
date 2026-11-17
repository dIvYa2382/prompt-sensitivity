"""Baseline validation (Gate G3): recompute the published PubMedQA summary of clinical-llm-eval
(results/summary/master_summary.csv) from the raw outputs, twice:
  (a) from the stored 'extracted' field, (b) from raw text with our re-implementation of the
published extractor (E2_substring). Both use the published consistency definition.
Usage: python -I scripts/reproduce_published.py --repo ../data_raw/clinical-llm-eval
"""
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import pandas as pd, numpy as np
from data import MODELS, STYLES
from metrics import published_consistency, majority
from parsers import e2_substring

ap = argparse.ArgumentParser(); ap.add_argument("--repo", required=True); a = ap.parse_args()
pub = pd.read_csv(os.path.join(a.repo, "results", "summary", "master_summary.csv"))
pub = pub[pub.dataset == "pubmedqa"].set_index("model")
df = pd.read_csv("data/outputs_long.csv")
df["E2"] = df.raw.map(e2_substring)
df["stored"] = df.extracted_orig.replace("UNKNOWN", "INVALID")
rows = []
for src in ["stored", "E2"]:
    for m in MODELS:
        d = df[df.model == m]
        w = d.pivot(index="item_id", columns="variant", values=src)[STYLES]
        gold = d.drop_duplicates("item_id").set_index("item_id").gold.loc[w.index]
        cons = w.apply(lambda r: published_consistency(list(r)), axis=1)
        # published majority: most_common over non-UNKNOWN, ties -> first encountered (Counter order)
        from collections import Counter
        def pmaj(r):
            xs = [x for x in r if x != "INVALID"]
            return Counter(xs).most_common(1)[0][0] if xs else "INVALID"
        maj = w.apply(lambda r: pmaj(list(r)), axis=1)
        rec = {"source": src, "model": m,
               "mean_consistency": round(cons.mean(), 3), "std_consistency": round(cons.std(), 3),
               "fully_consistent": int((cons == 1).sum()),
               "overall_accuracy": round((maj == gold).mean() * 100, 1),
               "unknown_rate": round((w == "INVALID").values.mean() * 100, 1)}
        for s in STYLES:
            rec[f"acc_{s}"] = round((w[s] == gold).mean() * 100, 1)
        rows.append(rec)
out = pd.DataFrame(rows)
cols = ["mean_consistency", "std_consistency", "fully_consistent", "overall_accuracy", "unknown_rate"] + [f"acc_{s}" for s in STYLES]
n_match, n_all = 0, 0
for _, r in out.iterrows():
    p = pub.loc[r.model]
    diffs = {c: (r[c], p[c]) for c in cols if not np.isclose(r[c], p[c], atol=0.051 if c != "fully_consistent" else 0)}
    n_all += len(cols); n_match += len(cols) - len(diffs)
    print(f"{r.source:6s} {r.model:9s} cons={r.mean_consistency:.3f} full={r.fully_consistent:3d} acc={r.overall_accuracy:5.1f} "
          f"unk={r.unknown_rate:5.1f} | mismatches vs published: {diffs if diffs else 'none'}")
print(f"published PubMedQA cells reproduced: {n_match}/{n_all}")
os.makedirs("results/tables", exist_ok=True)
out.to_csv("results/tables/reproduction_published.csv", index=False)
