"""Paper figures, regenerated from data/ and results/tables (test items only).
Also writes results/tables/item_types.csv (mutually exclusive item-level outcome classes)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
from data import MODELS, STYLES
from parsers import e3_wordboundary
from metrics import item_flags

OUT = "paper/figures"; os.makedirs(OUT, exist_ok=True)
BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6"
INK, MUTED, GRID, LIGHT = "#0b0b0b", "#52514e", "#e4e3df", "#c9c8c1"
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans", "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
                     "legend.frameon": False, "savefig.bbox": "tight", "savefig.dpi": 300})
NICE = {"phi3_mini": "Phi-3 Mini", "llama3.2": "Llama 3.2", "gemma2": "Gemma 2", "mistral": "Mistral", "meditron": "Meditron"}
FUNC = [m for m in MODELS if m != "meditron"]

df = pd.read_csv("data/outputs_long.csv").merge(pd.read_csv("data/split.csv"), on="item_id")
t = df[df.split == "test"].copy(); t["lab"] = t.raw.map(e3_wordboundary)

# ---- item types (priority order: all-invalid, fully stable, reversal, uncertainty shift, format only)
rows = []
for m in MODELS:
    w = t[t.model == m].pivot(index="item_id", columns="variant", values="lab")[STYLES]
    for i, r in w.iterrows():
        f = item_flags(list(r))
        k = ("all invalid" if f["all_invalid"] else "fully stable" if f["full_stable"] else
             "polarity reversal" if f["reversal"] else "uncertainty shift" if f["uncertainty_shift"] else "format only")
        rows.append({"model": m, "item_id": i, "type": k})
it = pd.DataFrame(rows)
TYPES = ["fully stable", "uncertainty shift", "polarity reversal", "format only", "all invalid"]
tab = it.groupby("model").type.value_counts(normalize=True).unstack(fill_value=0).reindex(index=MODELS, columns=TYPES, fill_value=0)
tab.to_csv("results/tables/item_types.csv")

# Fig 1: what kind of instability
fig, ax = plt.subplots(figsize=(5.2, 2.0))
cols = {"fully stable": BLUE, "uncertainty shift": AQUA, "polarity reversal": ORANGE, "format only": VIOLET, "all invalid": LIGHT}
y = np.arange(len(MODELS))[::-1]
left = np.zeros(len(MODELS))
for k in TYPES:
    v = tab[k].values
    ax.barh(y, v, left=left, color=cols[k], height=0.62, edgecolor="white", linewidth=1.2, label=k)
    for yi, l, vi in zip(y, left, v):
        if vi >= 0.07:
            ax.text(l + vi / 2, yi, f"{vi:.0%}", ha="center", va="center", fontsize=6.5,
                    color="white" if k in ("fully stable", "polarity reversal", "format only") else INK)
    left += v
ax.set_yticks(y, [NICE[m] for m in MODELS]); ax.set_xlim(0, 1); ax.grid(axis="y", visible=False)
ax.set_xlabel("share of the 150 test questions")
ax.legend(ncol=5, loc="lower center", bbox_to_anchor=(0.45, 1.0), fontsize=6.5, handlelength=1.2, columnspacing=1.0)
fig.savefig(f"{OUT}/fig_item_types.pdf")

# Fig 2: evaluator choice
mm = pd.read_csv("results/tables/main_by_evaluator_model.csv")
EV = [("E1_strict", "E1 strict match", MUTED, "s"), ("E2_substring", "E2 published substring", ORANGE, "D"),
      ("E3_wordboundary", "E3 word-boundary (ours)", BLUE, "o")]
fig, axs = plt.subplots(1, 2, figsize=(5.6, 2.1), sharey=True)
yy = np.arange(len(MODELS))[::-1]
for j, (ev, lab, c, mk) in enumerate(EV):
    d = mm[mm.evaluator == ev].set_index("model").loc[MODELS]
    off = (j - 1) * 0.22
    axs[0].errorbar(d.S_cat, yy + off, xerr=[d.S_cat - d.S_cat_lo, d.S_cat_hi - d.S_cat], fmt=mk, ms=4, color=c,
                    elinewidth=0.9, capsize=0, mec="white", mew=0.6, label=lab)
    axs[1].errorbar(d.acc_mean, yy + off, xerr=[d.acc_mean - d.acc_lo, d.acc_hi - d.acc_mean], fmt=mk, ms=4, color=c,
                    elinewidth=0.9, capsize=0, mec="white", mew=0.6)
axs[0].set_yticks(yy, [NICE[m] for m in MODELS]); axs[0].set_xlabel(r"prompt stability $S_p$ ($D_{cat}$)")
axs[1].set_xlabel("accuracy (mean over the 5 prompts)")
axs[0].set_xlim(0.45, 1.02); axs[1].set_xlim(-0.02, 0.7)
for a in axs: a.grid(axis="y", visible=False)
axs[0].legend(ncol=3, loc="lower center", bbox_to_anchor=(1.05, 1.0), fontsize=6.5, handletextpad=0.3)
fig.savefig(f"{OUT}/fig_evaluators.pdf")

# Fig 3: accuracy vs stability (functional models)
d = mm[mm.evaluator == "E3_wordboundary"].set_index("model").loc[FUNC]
fig, ax = plt.subplots(figsize=(3.3, 2.4))
ax.errorbar(d.S_cat, d.acc_mean, xerr=[d.S_cat - d.S_cat_lo, d.S_cat_hi - d.S_cat],
            yerr=[d.acc_mean - d.acc_lo, d.acc_hi - d.acc_mean], fmt="o", ms=5, color=BLUE, ecolor="#86b6ef", elinewidth=1.0, capsize=0, mec="white", mew=0.7)
offs = {"phi3_mini": (-6, 6, "right"), "llama3.2": (6, 4, "left"), "gemma2": (-8, -10, "right"), "mistral": (8, 7, "left")}
for m in FUNC:
    dx, dy, ha = offs[m]
    ax.annotate(NICE[m], (d.S_cat[m], d.acc_mean[m]), xytext=(dx, dy), textcoords="offset points", fontsize=7, ha=ha, color=INK)
ax.set_xlabel(r"prompt stability $S_p$ (higher = more stable)"); ax.set_ylabel("accuracy")
ax.set_xlim(0.74, 0.9); ax.set_ylim(0.25, 0.7)
fig.savefig(f"{OUT}/fig_acc_vs_stability.pdf")

# Fig 4: which prompt variant departs from the other four
v = pd.read_csv("results/tables/variant_effects.csv")
M = v[v.model.isin(FUNC)].pivot(index="model", columns="variant", values="deviates_from_others").loc[FUNC, STYLES]
fig, ax = plt.subplots(figsize=(4.4, 1.8))
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list("blue", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
im = ax.imshow(M.values, cmap=cmap, vmin=0, vmax=0.4, aspect="auto")
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        val = M.values[i, j]
        ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=6.5, color="white" if val > 0.2 else INK)
ax.set_xticks(range(len(STYLES)), STYLES); ax.set_yticks(range(len(FUNC)), [NICE[m] for m in FUNC]); ax.grid(False)
for s in ax.spines.values(): s.set_visible(False)
cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02); cb.outline.set_visible(False); cb.ax.tick_params(labelsize=6)
cb.set_label("disagrees with the other 4", fontsize=6.5)
fig.savefig(f"{OUT}/fig_variant_deviation.pdf")
for f in sorted(os.listdir(OUT)): print("figure:", f)
print(tab.round(3))
