"""Three ways to turn a raw model output into a conclusion category (yes / no / maybe / INVALID).

E1_strict      the whole output, lower-cased and stripped of surrounding punctuation/whitespace,
               must be exactly 'yes', 'no' or 'maybe'. Anything else is INVALID.
E2_substring   the published pipeline's extractor (clinical-llm-eval, src/inference.py,
               extract_answer_pubmedqa), re-implemented verbatim: 'yes' substring, else 'no'
               substring, else 'maybe' substring, else UNKNOWN. Note 'no' matches inside
               'not', 'cannot', 'know', 'provided'...
E3_wordboundary  whole-word first mention of yes/no/maybe; explicit hedges ('not sure',
               'unclear', 'cannot be determined', 'insufficient', 'not enough', 'inconclusive')
               count as maybe; otherwise INVALID. Rules written on DEV items only (frozen before test).
"""
import re

INVALID = "INVALID"


def e1_strict(raw):
    s = (raw or "").strip().lower().strip(" .,:;!\"'`*()[]")
    return s if s in ("yes", "no", "maybe") else INVALID


def e2_substring(raw):
    raw = (raw or "").lower().strip()
    if "yes" in raw:
        return "yes"
    if "no" in raw:
        return "no"
    if "maybe" in raw:
        return "maybe"
    return INVALID           # the original pipeline calls this UNKNOWN


HEDGE = re.compile(r"\b(not sure|unsure|unclear|uncertain|cannot be determined|can't be determined|"
                   r"cannot determine|insufficient|not enough|inconclusive|possibly|perhaps|it depends)\b")
WORD = re.compile(r"\b(yes|no|maybe)\b")


def e3_wordboundary(raw):
    s = (raw or "").lower()
    m = WORD.search(s)
    h = HEDGE.search(s)
    if m and (not h or m.start() < h.start()):
        return m.group(1)
    if h:
        return "maybe"
    return INVALID


EVALUATORS = {"E1_strict": e1_strict, "E2_substring": e2_substring, "E3_wordboundary": e3_wordboundary}
