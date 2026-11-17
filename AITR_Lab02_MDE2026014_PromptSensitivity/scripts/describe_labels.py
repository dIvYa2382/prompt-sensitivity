"""Descriptive add-on (written after the main run, logged as such): label distribution per model and
the conclusion that stable-but-wrong items converge on. Test items, primary evaluator E3."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import pandas as pd
from parsers import e3_wordboundary
from data import MODELS
df = pd.read_csv("data/outputs_long.csv").merge(pd.read_csv("data/split.csv"), on="item_id")
t = df[df.split == "test"].copy(); t["lab"] = t.raw.map(e3_wordboundary)
dist = t.groupby("model").lab.value_counts(normalize=True).unstack(fill_value=0).loc[MODELS]
dist.to_csv("results/tables/label_distribution.csv"); print(dist.round(3))
w = t.pivot_table(index=["model", "item_id"], columns="variant", values="lab", aggfunc="first")
st = w.nunique(axis=1) == 1
g = t.drop_duplicates(["model", "item_id"]).set_index(["model", "item_id"]).gold
lab = w.iloc[:, 0]
sw = pd.DataFrame({"stable": st, "label": lab, "gold": g})
sw = sw[sw.stable & (sw.label != sw.gold) & (sw.label != "INVALID")]
x = sw.groupby(["model", "gold", "label"]).size().rename("n").reset_index()
x.to_csv("results/tables/stable_wrong_detail.csv", index=False); print(x.to_string(index=False))
