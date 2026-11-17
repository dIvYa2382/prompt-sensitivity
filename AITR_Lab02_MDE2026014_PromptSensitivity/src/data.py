"""Load the public PubMedQA prompt-variation outputs of Hariprasad (2026), clinical-llm-eval.

Only JSON/CSV data files are read; no code from that repository is imported or executed.
Long format, one row per (model, item, prompt variant):
  model, item_id, variant, raw, extracted_orig, gold, question
"""
import json, os
import pandas as pd

MODELS = ["phi3_mini", "llama3.2", "gemma2", "mistral", "meditron"]
STYLES = ["original", "formal", "simplified", "roleplay", "direct"]
LABELS = ["yes", "no", "maybe"]


def load_long(repo):
    rows = []
    for m in MODELS:
        for rec in json.load(open(os.path.join(repo, "results", "raw", f"pubmedqa_{m}.json"))):
            for s in STYLES:
                r = rec["responses"][s]
                rows.append({"model": m, "item_id": int(rec["id"]), "variant": s, "raw": r["raw"],
                             "extracted_orig": r["extracted"], "gold": rec["correct_answer"],
                             "question": rec["question"]})
    return pd.DataFrame(rows)


def load_prompts(repo):
    return json.load(open(os.path.join(repo, "data", "prompts", "pubmedqa_prompts.json")))


def load_sample(repo):
    return pd.read_csv(os.path.join(repo, "data", "processed", "pubmedqa_sample.csv"))
