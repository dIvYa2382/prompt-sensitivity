from pathlib import Path
import pandas as pd
import numpy as np

INPUT = Path("results/conclusion_labels.csv")
OUTDIR = Path("results/tables")
OUTDIR.mkdir(parents=True, exist_ok=True)

required = ["item_id", "prompt_variant", "conclusion_category"]
df = pd.read_csv(INPUT)

missing_cols = [c for c in required if c not in df.columns]
if missing_cols:
    raise ValueError(f"Missing required columns: {missing_cols}")

if df[required].isna().any().any():
    raise ValueError("Missing required values detected.")
if (df["item_id"].astype(str).str.strip() == "").any():
    raise ValueError("Blank item_id detected.")
if (df["prompt_variant"].astype(str).str.strip() == "").any():
    raise ValueError("Blank prompt_variant detected.")

# A duplicate item/variant is suspicious unless repeated runs are explicitly represented.
if df.duplicated(["item_id", "prompt_variant"]).any():
    raise ValueError("Duplicate item_id/prompt_variant pairs; add run_id or resolve duplicates.")

def agreement(group):
    counts = group["conclusion_category"].value_counts()
    return counts.max() / len(group)

item = (
    df.groupby("item_id")
      .apply(agreement, include_groups=False)
      .rename("category_agreement")
      .reset_index()
)
item.to_csv(OUTDIR / "item_agreement.csv", index=False)

summary = pd.DataFrame([{
    "n_items": int(item["item_id"].nunique()),
    "mean_item_agreement": float(item["category_agreement"].mean()),
    "median_item_agreement": float(item["category_agreement"].median()),
    "min_item_agreement": float(item["category_agreement"].min()),
    "max_item_agreement": float(item["category_agreement"].max())
}])
summary.to_csv(OUTDIR / "summary_metrics.csv", index=False)

print("Saved:", OUTDIR / "item_agreement.csv")
print("Saved:", OUTDIR / "summary_metrics.csv")
print(summary.to_string(index=False))

