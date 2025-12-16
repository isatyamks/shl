import pandas as pd
import requests
import sys
import time
from pathlib import Path

API_URL = "http://localhost:8000/recommend"
TOP_K = 10
MAX_RETRIES = 3
RETRY_DELAY = 2


def fetch_recommendations(query: str, top_k: int = 10, retries: int = MAX_RETRIES):
    for attempt in range(retries):
        try:
            r = requests.post(
                API_URL,
                json={"query": query, "top_k": top_k},
                timeout=60
            )
            r.raise_for_status()
            data = r.json()

            urls = []
            if isinstance(data, list):
                urls = [item["url"] for item in data if "url" in item]
            elif isinstance(data, dict) and "recommended_assessments" in data:
                urls = [item["url"] for item in data["recommended_assessments"]]
            else:
                print(f"  Warning: Unexpected response format for query: {query[:60]}...")
                if attempt < retries - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return []

            if len(urls) < top_k:
                print(f"  Warning: Only {len(urls)} recommendations returned (expected {top_k})")
            
            return urls

        except requests.exceptions.Timeout:
            print(f"  Timeout on attempt {attempt + 1}/{retries}")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            return []
        
        except requests.exceptions.RequestException as e:
            print(f"  Request error on attempt {attempt + 1}/{retries}: {e}")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            return []
        
        except Exception as e:
            print(f"  Error on attempt {attempt + 1}/{retries}: {e}")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            return []
    
    return []


def validate_input_csv(df: pd.DataFrame) -> bool:
    if "Query" not in df.columns:
        print("Error: Input CSV must contain 'Query' column")
        return False
    if len(df) == 0:
        print("Error: Input CSV is empty")
        return False
    return True


def main():
    if len(sys.argv) > 1:
        input_csv = sys.argv[1]
    else:
        input_csv = "data/result/test.csv"
    
    if len(sys.argv) > 2:
        output_csv = sys.argv[2]
    else:
        input_path = Path(input_csv)
        output_csv = str(input_path.parent / f"{input_path.stem}_result.csv")
    
    if not Path(input_csv).exists():
        print(f"Error: Input file not found: {input_csv}")
        sys.exit(1)
    
    print(f"Reading input from: {input_csv}")
    print(f"Output will be written to: {output_csv}")
    print(f"API endpoint: {API_URL}")
    print(f"Top K: {TOP_K}\n")
    
    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    if not validate_input_csv(df):
        sys.exit(1)
    
    unique_queries = df["Query"].unique()
    total_queries = len(unique_queries)

    print(f"Total rows in input CSV: {len(df)}")
    print(f"Unique queries found: {total_queries}\n")

    rows = []
    failed_queries = []

    for idx, query in enumerate(unique_queries, 1):
        print(f"[{idx}/{total_queries}] Processing query: {query[:80]}...")
        
        urls = fetch_recommendations(query, TOP_K)

        if not urls:
            print(f"  ERROR: No recommendations returned for this query\n")
            failed_queries.append(query)
            continue

        for url in urls:
            rows.append({
                "Query": query,
                "Assessment_url": url
            })

        print(f"  Success: Retrieved {len(urls)} recommendations\n")

    if failed_queries:
        print(f"\nWarning: {len(failed_queries)} queries failed to return recommendations")
        for q in failed_queries:
            print(f"  - {q[:80]}...")

    out_df = pd.DataFrame(rows)
    
    if len(out_df) == 0:
        print("\nError: No recommendations generated. Please check your API and input data.")
        sys.exit(1)
    
    out_df.to_csv(output_csv, index=False)

    print("\n" + "=" * 80)
    print(f"Results written to: {output_csv}")
    print(f"Total output rows: {len(out_df)}")
    print(f"Successful queries: {total_queries - len(failed_queries)}/{total_queries}")
    
    if len(unique_queries) > 0:
        avg_recommendations = len(out_df) / (total_queries - len(failed_queries)) if (total_queries - len(failed_queries)) > 0 else 0
        print(f"Average recommendations per query: {avg_recommendations:.1f}")
        print(f"Expected: {TOP_K} recommendations per query")
    
    if failed_queries:
        print(f"\nFailed queries: {len(failed_queries)}")
    else:
        print("\nAll queries processed successfully!")


if __name__ == "__main__":
    main()
