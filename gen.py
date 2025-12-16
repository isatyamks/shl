import pandas as pd
import requests

API_URL = "http://localhost:8000/recommend"

INPUT_CSV = "data/train/val.csv"
OUTPUT_CSV = "data/train/result.csv"
TOP_K = 10


def fetch_recommendations(query: str, top_k: int = 10):
    try:
        r = requests.post(
            API_URL,
            json={"query": query, "top_k": top_k},
            timeout=30
        )
        r.raise_for_status()
        data = r.json()

        if isinstance(data, list):
            return [item["url"] for item in data if "url" in item]

        elif isinstance(data, dict) and "recommended_assessments" in data:
            return [item["url"] for item in data["recommended_assessments"]]

        else:
            print(f"Unexpected response format for query: {query[:60]}...")
            return []

    except Exception as e:
        print(f"ERROR calling API for query: {query[:60]}... → {e}")
        return []


def main():
    df = pd.read_csv(INPUT_CSV)

    unique_queries = df["Query"].unique()

    print(f"Total rows in input CSV: {len(df)}")
    print(f"Unique queries found: {len(unique_queries)}\n")

    rows = []

    for query in unique_queries:
        print(f"Processing query: {query[:80]}...")
        urls = fetch_recommendations(query, TOP_K)

        if not urls:
            print("No recommendations returned\n")
            continue

        for url in urls:
            rows.append({
                "Query": query,
                "Assessment_url": url
            })

        print(f"  Retrieved {len(urls)} recommendations\n")

    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUTPUT_CSV, index=False)

    print(f"API responses written to: {OUTPUT_CSV}")
    print(f"Total output rows: {len(out_df)}")
    print(f"Rows per query (expected): {TOP_K}")


if __name__ == "__main__":
    main()
