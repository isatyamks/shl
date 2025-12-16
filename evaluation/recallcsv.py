import pandas as pd

GROUND_TRUTH_CSV = "data/result/val.csv"
PREDICTIONS_CSV = "data/result/val_result.csv"
K = 10

def normalize_url(url: str) -> str:
    if not url or pd.isna(url):
        return ""

    url = str(url).strip().lower().rstrip("/")
    return url.split("/")[-1]

gt_df = pd.read_csv(GROUND_TRUTH_CSV)
pred_df = pd.read_csv(PREDICTIONS_CSV)

print(f"Ground truth rows: {len(gt_df)}")
print(f"Prediction rows: {len(pred_df)}\n")

gt_map = {}
for _, row in gt_df.iterrows():
    q = row["Query"]
    slug = normalize_url(row["Assessment_url"])

    if not slug:
        continue

    if q not in gt_map:
        gt_map[q] = set()

    gt_map[q].add(slug)

pred_map = {}
for _, row in pred_df.iterrows():
    q = row["Query"]
    slug = normalize_url(row["Assessment_url"])

    if not slug:
        continue

    if q not in pred_map:
        pred_map[q] = []

    pred_map[q].append(slug)

def recall_at_k(predicted_slugs, relevant_slugs, k):
    if not relevant_slugs:
        return 0.0
    return len(set(predicted_slugs[:k]) & relevant_slugs) / len(relevant_slugs)

recalls = []

for query, relevant_slugs in gt_map.items():
    predicted_slugs = pred_map.get(query, [])

    recall = recall_at_k(predicted_slugs, relevant_slugs, K)
    recalls.append(recall)

    print(
        f"Recall@{K}: {recall:.3f} | "
        f"Relevant: {len(relevant_slugs):2d} | "
        f"Predicted: {len(predicted_slugs):2d} | "
        f"{query[:80]}..."
    )


mean_recall = sum(recalls) / len(recalls) if recalls else 0.0

print("\n" + "=" * 80)
print(f"Mean Recall@{K}: {mean_recall:.4f}")
print(f"Evaluated on {len(recalls)} unique queries")
