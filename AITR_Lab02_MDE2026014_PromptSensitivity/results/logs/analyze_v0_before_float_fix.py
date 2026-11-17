"""Main analysis on the TEST items (150), run once after the freeze (results/logs/06_freeze_hashes.log).
Writes results/tables/*.csv and results/summary.json.
Usage: python -I scripts/analyze.py
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from collections import Counter
from itertools import combinations
import numpy as np, pandas as pd
from data import MODELS, STYLES
from parsers import EVALUATORS
from metrics import s_p, d_cat, d_ord, item_flags, majority, published_consistency, errica, gini_disagreement, VALID

cfg = json.load(open("configs/experiment.json"))
B, SEED = 10000, cfg["uncertainty"]["seed"] if "seed" in cfg["uncertainty"] else 2026
rng = np.random.default_rng(SEED)
os.makedirs("results/tables", exist_ok=True)
df = pd.read_csv("data/outputs_long.csv").merge(pd.read_csv("data/split.csv"), on="item_id")
for k, f in EVALUATORS.items():
    df[k] = df.raw.map(f)
test = df[df.split == "test"].copy()
ITEMS = np.sort(test.item_id.unique())
GOLD = test.drop_duplicates("item_id").set_index("item_id").gold.loc[ITEMS]
N = len(ITEMS)
print("test items:", N, "| outputs:", len(test))


def wide(d, ev, styles=STYLES):
    return d.pivot(index="item_id", columns="variant", values=ev).loc[ITEMS, styles]


def per_item(w):
    """Item-level metric table for one model/evaluator."""
    rows = []
    for i, r in w.iterrows():
        L = list(r)
        f = item_flags(L)
        maj = majority(L)
        rows.append({"item_id": i, "S_cat": s_p(L, d_cat), "S_ord": s_p(L, d_ord), **f,
                     "pub_cons": published_consistency(L), "valid_share": np.mean([x in VALID for x in L]),
                     "acc_mean": np.mean([x == GOLD[i] for x in L]), "maj_correct": maj == GOLD[i],
                     "n_cats": len(set(L))})
    return pd.DataFrame(rows).set_index("item_id")


def boot(x, stat=np.mean):
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), (B, len(x)))
    v = stat(x[idx], axis=1) if stat is np.mean else np.array([stat(x[j]) for j in idx])
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


SUM = {"n_test_items": int(N), "n_outputs_test": int(len(test))}
# ---------------- RQ1 + evaluator comparison (all models x evaluators)
main_rows, items_store = [], {}
for ev in EVALUATORS:
    for m in MODELS:
        w = wide(test[test.model == m], ev)
        it = per_item(w)
        items_store[(ev, m)] = (w, it)
        rec = {"evaluator": ev, "model": m}
        for c in ["S_cat", "S_ord", "full_stable", "reversal", "uncertainty_shift", "format_instability", "all_invalid", "valid_share", "acc_mean", "maj_correct", "pub_cons"]:
            rec[c] = float(it[c].mean())
        rec["S_cat_lo"], rec["S_cat_hi"] = boot(it.S_cat)
        rec["rev_lo"], rec["rev_hi"] = boot(it.reversal)
        rec["acc_lo"], rec["acc_hi"] = boot(it.acc_mean)
        rec["any_change"] = float((it.n_cats > 1).mean())
        rec["sens_errica"], rec["cons_errica"] = errica([list(r) for _, r in w.iterrows()], list(GOLD))
        for s in STYLES:
            rec[f"acc_{s}"] = float((w[s] == GOLD).mean())
            rec[f"valid_{s}"] = float(w[s].isin(VALID).mean())
        main_rows.append(rec)
main = pd.DataFrame(main_rows)
main.to_csv("results/tables/main_by_evaluator_model.csv", index=False)
P = "E3_wordboundary"
print(main[main.evaluator == P][["model", "S_cat", "S_cat_lo", "S_cat_hi", "S_ord", "full_stable", "reversal", "uncertainty_shift", "format_instability", "valid_share", "acc_mean", "maj_correct"]].round(3).to_string(index=False))

# paired bootstrap: E2 - E3 differences per model
diff_rows = []
for m in MODELS:
    a, b = items_store[("E2_substring", m)][1], items_store[(P, m)][1]
    for c in ["S_cat", "reversal", "uncertainty_shift", "acc_mean", "valid_share"]:
        dlt = (a[c].astype(float) - b[c].astype(float)).values
        lo, hi = boot(dlt)
        diff_rows.append({"model": m, "metric": c, "E2": float(a[c].mean()), "E3": float(b[c].mean()),
                          "diff": float(dlt.mean()), "lo": lo, "hi": hi})
    a1 = items_store[("E1_strict", m)][1]
    for c in ["S_cat", "reversal", "acc_mean", "valid_share"]:
        dlt = (a1[c].astype(float) - b[c].astype(float)).values
        lo, hi = boot(dlt)
        diff_rows.append({"model": m, "metric": "E1-" + c, "E2": float(a1[c].mean()), "E3": float(b[c].mean()),
                          "diff": float(dlt.mean()), "lo": lo, "hi": hi})
diffs = pd.DataFrame(diff_rows)
diffs.to_csv("results/tables/evaluator_diffs.csv", index=False)

# label transitions E2 -> E3 (output level, test)
tr = test.groupby(["E2_substring", P]).size().rename("n").reset_index()
tr.to_csv("results/tables/transitions_E2_E3.csv", index=False)
tr_model = test[test.E2_substring != test[P]].groupby(["model", "E2_substring", P]).size().rename("n").reset_index()
tr_model.to_csv("results/tables/transitions_E2_E3_by_model.csv", index=False)
SUM["E2_E3_disagree_outputs"] = int((test.E2_substring != test[P]).sum())
SUM["E2_E3_maybe_to_no"] = int(((test.E2_substring == "no") & (test[P] == "maybe")).sum())
SUM["E2_E3_invalid_to_no"] = int(((test.E2_substring == "no") & (test[P] == "INVALID")).sum())
SUM["E1_invalid_share"] = float((test.E1_strict == "INVALID").mean())
SUM["E1_invalid_share_excl_meditron"] = float((test[test.model != "meditron"].E1_strict == "INVALID").mean())
print("E2 vs E3 transitions:\n", tr[tr.E2_substring != tr[P]].to_string(index=False))

# ---------------- per-variant effects (primary evaluator)
var_rows = []
for m in MODELS:
    w, it = items_store[(P, m)]
    for s in STYLES:
        others = w.drop(columns=s)
        dev, n = 0, 0
        for i in ITEMS:
            mo = majority(list(others.loc[i]), valid_only=False)
            if mo in ("TIE",):
                continue
            n += 1
            dev += w.loc[i, s] != mo
        var_rows.append({"model": m, "variant": s, "acc": float((w[s] == GOLD).mean()),
                         "valid": float(w[s].isin(VALID).mean()), "maybe_rate": float((w[s] == "maybe").mean()),
                         "deviates_from_others": dev / n if n else np.nan, "n_with_clear_others": n})
var = pd.DataFrame(var_rows)
var.to_csv("results/tables/variant_effects.csv", index=False)
print(var.pivot(index="model", columns="variant", values="deviates_from_others").round(3))

# ---------------- accuracy-stability matrix (review Table 4)
mat_rows = []
for m in MODELS:
    w, it = items_store[(P, m)]
    st = it.full_stable
    ac = it.maj_correct
    mat_rows.append({"model": m, "stable_correct": int((st & ac).sum()), "stable_wrong": int((st & ~ac).sum()),
                     "unstable_correct": int((~st & ac).sum()), "unstable_wrong": int((~st & ~ac).sum())})
mat = pd.DataFrame(mat_rows)
mat.to_csv("results/tables/accuracy_stability_matrix.csv", index=False)
print(mat.to_string(index=False))

# stable-but-wrong breakdown by gold class (functional models)
sbw = []
for m in MODELS:
    w, it = items_store[(P, m)]
    for g in ["yes", "no", "maybe"]:
        msk = (GOLD == g).values
        sbw.append({"model": m, "gold": g, "n": int(msk.sum()), "stable": int(it.full_stable.values[msk].sum()),
                    "stable_wrong": int((it.full_stable.values & ~it.maj_correct.values & msk).sum())})
pd.DataFrame(sbw).to_csv("results/tables/stable_wrong_by_gold.csv", index=False)

# ---------------- prompt- vs model-induced disagreement (review Eq. 6 proxy)
vd_rows = []
for subset_name, mods in [("all5", MODELS), ("excl_meditron", [m for m in MODELS if m != "meditron"])]:
    cube = {m: items_store[(P, m)][0] for m in mods}
    pr = [gini_disagreement(list(cube[m].loc[i])) for m in mods for i in ITEMS]
    mo = [gini_disagreement([cube[m].loc[i, s] for m in mods]) for s in STYLES for i in ITEMS]
    pr_i = np.array([np.mean([gini_disagreement(list(cube[m].loc[i])) for m in mods]) for i in ITEMS])
    mo_i = np.array([np.mean([gini_disagreement([cube[m].loc[i, s] for m in mods]) for s in STYLES]) for i in ITEMS])
    d = mo_i - pr_i
    lo, hi = boot(d)
    vd_rows.append({"subset": subset_name, "prompt_induced": float(np.mean(pr)), "model_induced": float(np.mean(mo)),
                    "diff_model_minus_prompt": float(d.mean()), "lo": lo, "hi": hi})
vd = pd.DataFrame(vd_rows)
vd.to_csv("results/tables/prompt_vs_model.csv", index=False)
print(vd.round(3).to_string(index=False))

# ---------------- robustness: drop roleplay; drop leak item; evaluator choice already above
rob = []
LEAK = 65
for m in MODELS:
    w, it = items_store[(P, m)]
    w4 = w[[s for s in STYLES if s != "roleplay"]]
    it4 = per_item(w4)
    rob.append({"model": m, "setting": "primary (5 variants)", "S_cat": it.S_cat.mean(), "reversal": it.reversal.mean(), "full_stable": it.full_stable.mean()})
    rob.append({"model": m, "setting": "without roleplay (4 variants)", "S_cat": it4.S_cat.mean(), "reversal": it4.reversal.mean(), "full_stable": it4.full_stable.mean()})
    keep = it.index != LEAK
    rob.append({"model": m, "setting": f"without item {LEAK}", "S_cat": it.S_cat[keep].mean(), "reversal": it.reversal[keep].mean(), "full_stable": it.full_stable[keep].mean()})
robdf = pd.DataFrame(rob)
robdf.to_csv("results/tables/robustness.csv", index=False)
print(robdf.pivot(index="model", columns="setting", values="S_cat").round(3))

# ---------------- CSI-style ranking under random weights (review Eq. 8; G5)
FUNC = [m for m in MODELS if m != "meditron"]
comp = pd.DataFrame({m: {"A_inf": main[(main.evaluator == P) & (main.model == m)].S_cat.item(),
                         "A_unc": 1 - main[(main.evaluator == P) & (main.model == m)].uncertainty_shift.item(),
                         "A_fact": main[(main.evaluator == P) & (main.model == m)].acc_mean.item(),
                         "A_valid": main[(main.evaluator == P) & (main.model == m)].valid_share.item()} for m in MODELS}).T
comp.to_csv("results/tables/csi_components.csv")
W = rng.dirichlet(np.ones(3), 10000)
X = comp.loc[FUNC, ["A_inf", "A_unc", "A_fact"]].values
scores = W @ X.T
top = Counter(np.array(FUNC)[scores.argmax(1)])
ranks = (-scores).argsort(1)
orders = Counter(" > ".join(np.array(FUNC)[r]) for r in ranks)
csi = {"top_share": {m: top.get(m, 0) / len(W) for m in FUNC}, "n_distinct_orders": len(orders),
       "most_common_orders": [(o, c / len(W)) for o, c in orders.most_common(4)],
       "equal_weight_order": " > ".join(np.array(FUNC)[(-(X.mean(1))).argsort()])}
for a in ["A_inf", "A_unc", "A_fact"]:
    csi[f"order_by_{a}"] = " > ".join(comp.loc[FUNC, a].sort_values(ascending=False).index)
SUM["csi"] = csi
print(json.dumps(csi, indent=1))

# ---------------- hypotheses (prespecified in configs/experiment.json)
e3 = main[main.evaluator == P].set_index("model")
e2 = main[main.evaluator == "E2_substring"].set_index("model")
h1 = {m: float(e3.loc[m, "any_change"]) for m in MODELS}
h2 = {m: {"dS": float(e2.loc[m, "S_cat"] - e3.loc[m, "S_cat"]), "drev": float(e2.loc[m, "reversal"] - e3.loc[m, "reversal"])} for m in MODELS}
SUM["H1_any_change_share"] = h1
SUM["H1_supported"] = all(v > 0 for v in h1.values())
SUM["H2_diffs"] = h2
SUM["H2_supported"] = any(abs(v["dS"]) >= 0.02 or abs(v["drev"]) >= 0.02 for v in h2.values())
acc_rank = list(e3.loc[FUNC].acc_mean.sort_values(ascending=False).index)
stab_rank = list(e3.loc[FUNC].S_cat.sort_values(ascending=False).index)
SUM["H3_acc_rank"], SUM["H3_stab_rank"] = acc_rank, stab_rank
SUM["H3_supported"] = acc_rank != stab_rank
from scipy.stats import kendalltau
SUM["H3_kendall_tau"] = float(kendalltau([acc_rank.index(m) for m in FUNC], [stab_rank.index(m) for m in FUNC])[0])
SUM["prompt_vs_model"] = vd.to_dict("records")
print("H1", SUM["H1_supported"], h1); print("H2", SUM["H2_supported"], h2); print("H3", SUM["H3_supported"], acc_rank, stab_rank, SUM["H3_kendall_tau"])

# ---------------- examples for the paper (real outputs)
ex = []
for m in FUNC:
    w, it = items_store[(P, m)]
    for i in it[it.reversal].index[:2]:
        d = test[(test.model == m) & (test.item_id == i)].set_index("variant")
        ex.append({"model": m, "item_id": int(i), "gold": GOLD[i], **{s: d.loc[s, "raw"] for s in STYLES}, **{f"lab_{s}": d.loc[s, P] for s in STYLES}})
pd.DataFrame(ex).to_csv("results/tables/reversal_examples.csv", index=False)

# ---------------- human-annotation sample (left for the author; no labels invented)
ann_rng = np.random.default_rng(2026)
dis = test[test.E2_substring != test[P]]
rest = test[(test.E2_substring == test[P]) & (test.model != "meditron")]
samp = pd.concat([dis.sample(min(40, len(dis)), random_state=2026), rest.sample(60, random_state=2026)])
samp = samp.sample(frac=1, random_state=2026)[["model", "item_id", "variant", "raw"]]
samp["human_label(yes/no/maybe/invalid)"] = ""
samp["annotator_note"] = ""
os.makedirs("annotation", exist_ok=True)
samp.to_csv("annotation/human_annotation_sample.csv", index=False)
key = test.loc[samp.index, ["model", "item_id", "variant", "E1_strict", "E2_substring", P]]
key.to_csv("annotation/annotation_key_DO_NOT_OPEN_BEFORE_LABELLING.csv", index=False)
SUM["annotation_sample_n"] = int(len(samp))

json.dump(SUM, open("results/summary.json", "w"), indent=1, default=float)
print("wrote results/summary.json")
