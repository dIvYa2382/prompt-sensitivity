"""Unit tests: the toy cases demanded by Prompt 09/10 plus parser cases taken from real outputs.
Run: python -I tests/test_metrics.py   (or pytest)"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from metrics import s_p, d_cat, d_ord, item_flags, majority, published_consistency, norm_entropy, gini_disagreement
from parsers import e1_strict, e2_substring, e3_wordboundary


def close(a, b):
    return abs(a - b) < 1e-12


def test_prompt09_cases():
    assert close(s_p(["yes", "yes", "yes"]), 1.0)                 # normal
    assert close(s_p(["yes", "yes", "maybe"]), 2 / 3)             # disagreement
    assert close(s_p(["yes"]), 1.0)                               # single variant (flag as insufficient)
    assert close(s_p(["yes", "no", "maybe", "INVALID"]), 0.25)    # four-way tie -> max share


def test_ordinal_distance():
    assert d_ord("yes", "no") == 1 and d_ord("yes", "maybe") == 0.5 and d_ord("maybe", "INVALID") == 1
    # C-bar under D_ord can be 'maybe' even when it is not the majority: yes,yes,no,no,maybe
    assert close(s_p(["yes", "yes", "no", "no", "maybe"], d_ord), 1 - (0.5 * 4) / 5)
    assert close(s_p(["yes", "yes", "no", "no", "maybe"], d_cat), 0.4)


def test_flags():
    f = item_flags(["yes", "no", "yes", "yes", "yes"]); assert f["reversal"] and not f["uncertainty_shift"]
    f = item_flags(["yes", "maybe", "yes", "yes", "yes"]); assert f["uncertainty_shift"] and not f["reversal"]
    f = item_flags(["yes"] * 5); assert f["full_stable"]
    f = item_flags(["INVALID"] * 5); assert f["all_invalid"] and not f["full_stable"]
    f = item_flags(["INVALID", "yes", "yes", "yes", "yes"]); assert f["format_instability"]


def test_majority_and_published():
    assert majority(["yes", "no", "yes", "INVALID", "maybe"]) == "yes"
    assert majority(["yes", "no", "INVALID", "INVALID", "INVALID"]) == "TIE"
    # published docstring example: majority B (3 votes) -> 3/5
    assert close(published_consistency(["A", "B", "B", "B", "A"]), 0.6)
    assert close(published_consistency(["INVALID"] * 4 + ["yes"]), 0.2)


def test_entropy_gini():
    assert close(norm_entropy(["yes"] * 5), 0.0)
    assert close(gini_disagreement(["yes", "yes", "no"]), 2 / 3)


def test_parsers_on_real_strings():
    s = "Maybe. The text does not provide a definitive"           # real phi3_mini output
    assert e2_substring(s) == "no" and e3_wordboundary(s) == "maybe" and e1_strict(s) == "INVALID"
    s = "The excerpt doesn't provide enough information to definitively"   # real gemma2 output
    assert e2_substring(s) == "no" and e3_wordboundary(s) == "maybe"
    s = "Yes, the excerpt suggests that some Pap"                 # real output
    assert e2_substring(s) == e3_wordboundary(s) == "yes"
    assert e1_strict("No.") == "no" and e1_strict(" yes ") == "yes"
    assert e3_wordboundary("A chat between a curious user and an artificial intelligence") == "INVALID"
    assert e2_substring("Based on the provided excerpt, it appears") == "INVALID"


if __name__ == "__main__":
    n = 0
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            f(); n += 1; print("PASS", k)
    print(f"{n} tests passed")
