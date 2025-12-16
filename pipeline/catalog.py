import json
import time
import requests
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (SHL-Catalog-Builder)"
}

INPUT_FILE = "data/raw/catalog_table_metadata.json"
OUTPUT_FILE = "data/processed/catalog.json"
REQUEST_DELAY = 1.5
TIMEOUT = 30



def des_dura(url):
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    container = None
    for cls in ["product-detail", "product-content", "product-main"]:
        container = soup.find("div", class_=cls)
        if container:
            break
    if not container:
        container = soup

    description = ""
    for p in container.find_all("p"):
        text = p.get_text(strip=True)
        if (
            len(text) > 80
            and "cookie" not in text.lower()
            and "browser" not in text.lower()
        ):
            description = text
            break

    duration = None
    full_text = container.get_text(" ", strip=True)

    match = re.search(
        r"Approximate Completion Time in minutes\s*=\s*(\d+)",
        full_text,
        re.IGNORECASE
    )

    if match:
        duration = int(match.group(1))

    return description, duration


def cata_build():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        base_items = json.load(f)

    total = len(base_items)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("[\n")

        for idx, item in enumerate(base_items, start=1):
            print(f"[{idx}/{total}] Fetching → {item['name']}")

            try:
                description, duration = des_dura(item["url"])
            except Exception as e:
                print(f"Error: {e}")
                description, duration = "", None

            record = {
                "url": item["url"],
                "name": item["name"],
                "adaptive_support": item["adaptive_support"],
                "description": description,
                "duration": duration,
                "remote_support": item["remote_support"],
                "test_type": item["test_types"]
            }
            json.dump(record, out, indent=2)
            if idx < total:
                out.write(",\n")
            else:
                out.write("\n")

            out.flush()   
            time.sleep(REQUEST_DELAY)

        out.write("]\n")

    print(f"\nCatalog built successfully: {total} items")
    print(f"Output saved at: {OUTPUT_FILE}")



if __name__ == "__main__":
    cata_build()
