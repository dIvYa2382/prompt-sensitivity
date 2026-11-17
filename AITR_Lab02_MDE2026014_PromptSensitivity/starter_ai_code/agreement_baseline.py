import pandas as pd

# Required columns: item_id, prompt_variant, conclusion_category
# Each row must come from an actual model output and a documented annotation.
df = pd.read_csv("results/conclusion_labels.csv")

required = {"item_id", "prompt_variant", "conclusion_category"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {sorted(missing)}")
if df[list(required)].isna().any().any():
    raise ValueError("Missing item, variant, or conclusion labels detected.")

# Per-item agreement: largest category count / number of variants.
def item_agreement(group):
    counts = group["conclusion_category"].value_counts()
    return counts.max() / len(group)

summary = (
    df.groupby("item_id")
      .apply(item_agreement, include_groups=False)
      .rename("conclusion_category_agreement")
      .reset_index()
)
summary.to_csv("results/item_agreement.csv", index=False)
print(summary)
print("Mean item-level agreement:", summary["conclusion_category_agreement"].mean())

