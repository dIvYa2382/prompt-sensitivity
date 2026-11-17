"""Conclusion-stability metrics. One 'item' = one PubMedQA question with fixed evidence, answered
under K prompt variants by one model. Labels are yes / no / maybe / INVALID.

Review mapping (Joshi, 2026): S_p is Eq. 7 with an explicit distance D; C-bar is the category that
minimises the mean distance to the K outputs (for D_cat this is the majority category).
"""
import math
from collections import Counter
from itertools import combinations
import numpy as np

CATS = ["yes", "no", "maybe", "INVALID"]
VALID = ("yes", "no", "maybe")


def d_cat(a, b):
    return 0.0 if a == b else 1.0


def d_ord(a, b):
    if a == b:
        return 0.0
    if "INVALID" in (a, b):
        return 1.0
    if {a, b} == {"yes", "no"}:
        return 1.0
    return 0.5


def s_p(labels, D=d_cat):
    """Prompt-stability score (review Eq. 7): 1 - mean_i D(C_i, C-bar), C-bar = argmin_c sum_i D(C_i, c)."""
    best = min(sum(D(x, c) for x in labels) for c in CATS)
    return 1.0 - best / len(labels)


def item_flags(labels):
    s = set(labels)
    return {
        "full_stable": len(s) == 1 and labels[0] in VALID,
        "reversal": "yes" in s and "no" in s,
        "uncertainty_shift": "maybe" in s and bool(s & {"yes", "no"}) and not ("yes" in s and "no" in s),
        "format_instability": "INVALID" in s and bool(s & set(VALID)),
        "all_invalid": s == {"INVALID"},
    }


def majority(labels, valid_only=True):
    xs = [x for x in labels if x in VALID] if valid_only else list(labels)
    if not xs:
        return "INVALID"
    c = Counter(xs).most_common()
    top = [k for k, v in c if v == c[0][1]]
    return top[0] if len(top) == 1 else "TIE"


def published_consistency(labels):
    """clinical-llm-eval definition: majority over non-UNKNOWN answers, share of ALL variants agreeing."""
    xs = [x for x in labels if x != "INVALID"]
    if not xs:
        return 0.0
    m = Counter(xs).most_common(1)[0][0]
    return sum(1 for x in xs if x == m) / len(labels)


def norm_entropy(labels, k=len(CATS)):
    c = Counter(labels)
    n = len(labels)
    h = -sum((v / n) * math.log(v / n) for v in c.values())
    return h / math.log(k)


def dist(labels):
    c = Counter(labels)
    return np.array([c.get(k, 0) / len(labels) for k in CATS])


def gini_disagreement(labels):
    """Share of unordered pairs that disagree."""
    pairs = list(combinations(labels, 2))
    return sum(a != b for a, b in pairs) / len(pairs)


def errica(item_labels, gold):
    """Errica et al. (NAACL 2025): sensitivity = mean normalised entropy over rephrasings (label-free);
    consistency = 1 - mean pairwise TVD between output distributions of items sharing a gold class
    (averaged over classes)."""
    sens = float(np.mean([norm_entropy(l) for l in item_labels]))
    by = {}
    for l, g in zip(item_labels, gold):
        by.setdefault(g, []).append(dist(l))
    cons = []
    for g, ds in by.items():
        if len(ds) < 2:
            continue
        tv = [0.5 * np.abs(a - b).sum() for a, b in combinations(ds, 2)]
        cons.append(1 - float(np.mean(tv)))
    return sens, float(np.mean(cons))
