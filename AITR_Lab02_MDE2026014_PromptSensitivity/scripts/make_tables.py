"""LaTeX tables and number macros generated from results/ (every result number in the paper comes from here)."""
import json, os, re
import pandas as pd

OUT = "paper/generated"; os.makedirs(OUT, exist_ok=True)
S = json.load(open("results/summary.json"))
mm = pd.read_csv("results/tables/main_by_evaluator_model.csv")
dif = pd.read_csv("results/tables/evaluator_diffs.csv")
mat = pd.read_csv("results/tables/accuracy_stability_matrix.csv").set_index("model")
var = pd.read_csv("results/tables/variant_effects.csv")
vd = pd.read_csv("results/tables/prompt_vs_model.csv").set_index("subset")
rob = pd.read_csv("results/tables/robustness.csv")
comp = pd.read_csv("results/tables/csi_components.csv", index_col=0)
rep = pd.read_csv("results/tables/reproduction_published.csv")
lab = pd.read_csv("results/tables/label_distribution.csv", index_col=0)
types = pd.read_csv("results/tables/item_types.csv", index_col=0)
sw = pd.read_csv("results/tables/stable_wrong_detail.csv")
tr = pd.read_csv("results/tables/transitions_E2_E3_by_model.csv")
MODELS = ["phi3_mini", "llama3.2", "gemma2", "mistral", "meditron"]
FUNC = MODELS[:4]
NICE = {"phi3_mini": "Phi-3 Mini", "llama3.2": "Llama 3.2", "gemma2": "Gemma 2", "mistral": "Mistral", "meditron": "Meditron"}
MAC = {"phi3_mini": "Phi", "llama3.2": "Llama", "gemma2": "Gemma", "mistral": "Mistral", "meditron": "Meditron"}
EVN = {"E1_strict": "E1 strict", "E2_substring": "E2 substring", "E3_wordboundary": "E3 word-boundary"}
mac = {}


def sg(s): return re.sub(r"(?<![\d\-])-(\d)", r"$-$\1", str(s))
def f2(x): return f"{x:.2f}"
def f3(x): return f"{x:.3f}"
def pc(x): return f"{100*x:.1f}\\%"
def p0(x): return f"{100*x:.0f}\\%"


E3 = mm[mm.evaluator == "E3_wordboundary"].set_index("model")
E2 = mm[mm.evaluator == "E2_substring"].set_index("model")
E1 = mm[mm.evaluator == "E1_strict"].set_index("model")
for m in MODELS:
    k = MAC[m]; r = E3.loc[m]
    mac.update({f"Sp{k}": f3(r.S_cat), f"SpLo{k}": f2(r.S_cat_lo), f"SpHi{k}": f2(r.S_cat_hi), f"SpOrd{k}": f3(r.S_ord),
                f"Full{k}": pc(r.full_stable), f"Rev{k}": pc(r.reversal), f"Unc{k}": pc(r.uncertainty_shift),
                f"Fmt{k}": pc(r.format_instability), f"Valid{k}": pc(r.valid_share), f"Acc{k}": pc(r.acc_mean),
                f"AccLo{k}": pc(r.acc_lo), f"AccHi{k}": pc(r.acc_hi), f"Maj{k}": pc(r.maj_correct),
                f"Change{k}": pc(r.any_change), f"Pub{k}": f3(r.pub_cons),
                f"SpEone{k}": f3(E1.loc[m].S_cat), f"AccEone{k}": pc(E1.loc[m].acc_mean), f"ValidEone{k}": pc(E1.loc[m].valid_share),
                f"SpEtwo{k}": f3(E2.loc[m].S_cat), f"AccEtwo{k}": pc(E2.loc[m].acc_mean), f"RevEtwo{k}": pc(E2.loc[m].reversal),
                f"UncEtwo{k}": pc(E2.loc[m].uncertainty_shift),
                f"Maybe{k}": pc(lab.loc[m, "maybe"]), f"No{k}": pc(lab.loc[m, "no"]), f"Yes{k}": pc(lab.loc[m, "yes"]),
                f"TypeStable{k}": p0(types.loc[m, "fully stable"]), f"TypeUnc{k}": p0(types.loc[m, "uncertainty shift"]),
                f"TypeRev{k}": p0(types.loc[m, "polarity reversal"]), f"TypeFmt{k}": p0(types.loc[m, "format only"]),
                f"SW{k}": int(mat.loc[m, "stable_wrong"]), f"SC{k}": int(mat.loc[m, "stable_correct"]),
                f"UC{k}": int(mat.loc[m, "unstable_correct"]), f"UW{k}": int(mat.loc[m, "unstable_wrong"])})
    d = dif[(dif.model == m)].set_index("metric")
    mac.update({f"dSpEtwo{k}": sg(f"{d.loc['S_cat','diff']:+.3f}"), f"dRevEtwo{k}": sg(f"{100*d.loc['reversal','diff']:+.1f}"),
                f"dUncEtwo{k}": sg(f"{100*d.loc['uncertainty_shift','diff']:+.1f}"), f"dAccEtwo{k}": sg(f"{100*d.loc['acc_mean','diff']:+.1f}"),
                f"dAccEtwoLo{k}": sg(f"{100*d.loc['acc_mean','lo']:+.1f}"), f"dAccEtwoHi{k}": sg(f"{100*d.loc['acc_mean','hi']:+.1f}"),
                f"dUncEtwoLo{k}": sg(f"{100*d.loc['uncertainty_shift','lo']:+.1f}"), f"dUncEtwoHi{k}": sg(f"{100*d.loc['uncertainty_shift','hi']:+.1f}"),
                f"dSpEone{k}": sg(f"{d.loc['E1-S_cat','diff']:+.3f}"), f"dAccEone{k}": sg(f"{100*d.loc['E1-acc_mean','diff']:+.1f}")})
    for s in ["original", "formal", "simplified", "roleplay", "direct"]:
        v = var[(var.model == m) & (var.variant == s)].iloc[0]
        mac[f"Dev{k}{s.capitalize()}"] = f2(v.deviates_from_others)
        mac[f"AccVar{k}{s.capitalize()}"] = pc(v.acc)
mac.update(NTest=S["n_test_items"], NOutTest=f"{S['n_outputs_test']:,}", NDev=50, NItems=200, NOutAll="5,000",
           EtwoEthreeDis=S["E2_E3_disagree_outputs"], EtwoMaybeNo=S["E2_E3_maybe_to_no"], EtwoInvalidNo=S["E2_E3_invalid_to_no"],
           EoneInvalid=pc(S["E1_invalid_share"]), EoneInvalidFunc=pc(S["E1_invalid_share_excl_meditron"]),
           PromptInd=f3(vd.loc["excl_meditron", "prompt_induced"]), ModelInd=f3(vd.loc["excl_meditron", "model_induced"]),
           PMdiff=f3(vd.loc["excl_meditron", "diff_model_minus_prompt"]), PMlo=f3(vd.loc["excl_meditron", "lo"]), PMhi=f3(vd.loc["excl_meditron", "hi"]),
           PromptIndAll=f3(vd.loc["all5", "prompt_induced"]), ModelIndAll=f3(vd.loc["all5", "model_induced"]),
           HthreeTau=sg(f"{S['H3_kendall_tau']:.2f}"), CSIorders=S["csi"]["n_distinct_orders"],
           CSItopLlama=p0(S["csi"]["top_share"]["llama3.2"]), CSItopMistral=p0(S["csi"]["top_share"]["mistral"]),
           AnnN=S["annotation_sample_n"], ReproCells="100/100",
           SWGemmaNoMaybe=int(sw[(sw.model == "gemma2") & (sw.gold == "no") & (sw.label == "maybe")].n.sum()),
           SWMistralNoMaybe=int(sw[(sw.model == "mistral") & (sw.gold == "no") & (sw.label == "maybe")].n.sum()),
           SWLlamaNoYes=int(sw[(sw.model == "llama3.2") & (sw.gold == "no") & (sw.label == "yes")].n.sum()),
           TrPhiMaybeNo=int(tr[(tr.model == "phi3_mini") & (tr.E3_wordboundary == "maybe")].n.sum()),
           TrMistralMaybeNo=int(tr[(tr.model == "mistral") & (tr.E3_wordboundary == "maybe")].n.sum()))
for m in FUNC:
    r = rob[(rob.model == m)].set_index("setting")
    mac[f"SpNoRole{MAC[m]}"] = f3(r.loc["without roleplay (4 variants)", "S_cat"])
    mac[f"RevNoRole{MAC[m]}"] = pc(r.loc["without roleplay (4 variants)", "reversal"])
for m in FUNC:
    v = var[var.model == m]
    mac[f"AccRange{MAC[m]}"] = f"{100*(v.acc.max()-v.acc.min()):.1f}"
    mac[f"AccMin{MAC[m]}"] = pc(v.acc.min()); mac[f"AccMax{MAC[m]}"] = pc(v.acc.max())
    for s_ in ["original", "formal", "simplified", "roleplay", "direct"]:
        mac[f"ValidVar{MAC[m]}{s_.capitalize()}"] = pc(v[v.variant == s_].valid.item())
with open(f"{OUT}/numbers.tex", "w") as f:
    for k, v in mac.items():
        f.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")

# ---- Table: main (primary evaluator)
L = []
for m in MODELS:
    r = E3.loc[m]
    L.append(f"{NICE[m]} & {f3(r.S_cat)} [{f2(r.S_cat_lo)}, {f2(r.S_cat_hi)}] & {f3(r.S_ord)} & {pc(r.any_change)} & {pc(r.full_stable)} & "
             f"{pc(r.reversal)} & {pc(r.uncertainty_shift)} & {pc(r.format_instability)} & {pc(r.valid_share)} & {pc(r.acc_mean)} \\\\")
open(f"{OUT}/tab_main.tex", "w").write("\n".join(L) + "\n")

# ---- Table: evaluators
L = []
for m in MODELS:
    for j, ev in enumerate(["E1_strict", "E2_substring", "E3_wordboundary"]):
        r = mm[(mm.evaluator == ev) & (mm.model == m)].iloc[0]
        name = NICE[m] if j == 0 else ""
        L.append(f"{name} & {EVN[ev]} & {pc(r.valid_share)} & {f3(r.S_cat)} & {f3(r.pub_cons)} & {pc(r.reversal)} & {pc(r.uncertainty_shift)} & "
                 f"{pc(r.acc_mean)} & {f2(r.sens_errica)} & {f2(r.cons_errica)} \\\\")
    if m != MODELS[-1]:
        L.append("\\midrule")
open(f"{OUT}/tab_evaluators.tex", "w").write("\n".join(L) + "\n")

# ---- Table: accuracy-stability matrix
L = []
for m in FUNC:
    r = mat.loc[m]
    L.append(f"{NICE[m]} & {r.stable_correct} & {r.stable_wrong} & {r.unstable_correct} & {r.unstable_wrong} & {pc(lab.loc[m,'yes'])} & {pc(lab.loc[m,'no'])} & {pc(lab.loc[m,'maybe'])} \\\\")
open(f"{OUT}/tab_matrix.tex", "w").write("\n".join(L) + "\n")

# ---- Table: CSI components and rankings
L = []
for m in FUNC:
    r = comp.loc[m]
    L.append(f"{NICE[m]} & {f3(r.A_inf)} & {f3(r.A_unc)} & {f3(r.A_fact)} & {p0(S['csi']['top_share'][m])} \\\\")
open(f"{OUT}/tab_csi.tex", "w").write("\n".join(L) + "\n")

# ---- Table: robustness
L = []
for m in FUNC:
    r = rob[rob.model == m].set_index("setting")
    L.append(f"{NICE[m]} & {f3(r.loc['primary (5 variants)','S_cat'])} & {f3(r.loc['without roleplay (4 variants)','S_cat'])} & "
             f"{f3(E2.loc[m].S_cat)} & {f3(E1.loc[m].S_cat)} & {pc(r.loc['primary (5 variants)','reversal'])} & {pc(r.loc['without roleplay (4 variants)','reversal'])} \\\\")
open(f"{OUT}/tab_robust.tex", "w").write("\n".join(L) + "\n")

# ---- Table: reproduction of published numbers
pub = pd.read_csv("results/tables/reproduction_published.csv")
L = []
for m in MODELS:
    r = pub[(pub.source == "E2") & (pub.model == m)].iloc[0]
    L.append(f"{NICE[m]} & {r.mean_consistency:.3f} & {int(r.fully_consistent)} & {r.overall_accuracy:.1f} & {r.unknown_rate:.1f} & "
             f"{r.acc_original:.1f} & {r.acc_formal:.1f} & {r.acc_simplified:.1f} & {r.acc_roleplay:.1f} & {r.acc_direct:.1f} \\\\")
open(f"{OUT}/tab_repro.tex", "w").write("\n".join(L) + "\n")

# ---- Table: real reversal examples
ex = pd.read_csv("results/tables/reversal_examples.csv")
def tex(s):
    s = " ".join(str(s).split())
    for a, b in [("\\", ""), ("&", "\\&"), ("%", "\\%"), ("_", "\\_"), ("#", "\\#"), ("**", ""), ("$", "\\$")]:
        s = s.replace(a, b)
    return s if len(s) <= 34 else s[:33] + "\\ldots"
L = []
pick = [("phi3_mini", 40), ("llama3.2", 3), ("llama3.2", 4)]
for m, i in pick:
    r = ex[(ex.model == m) & (ex.item_id == i)].iloc[0]
    for s in ["original", "formal", "simplified", "roleplay", "direct"]:
        first = f"\\multirow{{5}}{{*}}{{\\shortstack[l]{{{NICE[m]}\\\\item {i}\\\\gold: {r.gold}}}}}" if s == "original" else ""
        L.append(f"{first} & {s} & \\texttt{{\\small {tex(r[s])}}} & {r['lab_'+s]} \\\\")
    if (m, i) != pick[-1]:
        L.append("\\midrule")
open(f"{OUT}/tab_examples.tex", "w").write("\n".join(L) + "\n")
print(f"wrote {len(mac)} macros and tables to {OUT}")
