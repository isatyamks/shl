import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time


BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/products/product-catalog/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (SHL-Catalog-Scraper)"
}

PAGE_SIZE = 12
TYPE = 1

session = requests.Session()
session.headers.update(HEADERS)

def safe_get(url, params, retries=5, timeout=30):
    for attempt in range(retries):
        try:
            r = session.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            wait = 5 * (attempt + 1)
            print(f"[WARN] {e} → retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError("Max retries exceeded")


def yes_no_from_td(td):

    span = td.select_one("span")
    if not span:
        return "No"

    classes = " ".join(span.get("class", [])).lower()
    if "yes" in classes:
        return "Yes"
    return "No"

def scrape_page(start):
    params = {
        "start": start,
        "type": TYPE
    }

    r = safe_get(CATALOG_URL, params=params)
    soup = BeautifulSoup(r.text, "lxml")

    records = []

    rows = soup.select("tr[data-entity-id]")
    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 4:
            continue

        link = tds[0].select_one("a[href*='/product-catalog/view/']")
        if not link:
            continue

        url = urljoin(BASE_URL, link["href"])
        name = link.get_text(strip=True)

        remote_support = yes_no_from_td(tds[1])
        adaptive_support = yes_no_from_td(tds[2])

        test_types = []
        for span in tds[3].select("span.product-catalogue__key"):
            code = span.get_text(strip=True)
            if code:
                test_types.append(code)

        records.append({
            "url": url,
            "name": name,
            "remote_support": remote_support,
            "adaptive_support": adaptive_support,
            "test_types": test_types
        })

    return records


def scrape_all():
    all_records = {}
    start = 1

    while True:
        print(f"Scraping{start}")
        records = scrape_page(start)

        if not records:
            print("No more rows")
            break

        for r in records:
            all_records[r["url"]] = r 

        print(f"  Total products collected: {len(all_records)}")

        start += PAGE_SIZE
        time.sleep(2) 

    return list(all_records.values())


if __name__ == "__main__":
    data = scrape_all()
    print("\nFINAL COUNT:", len(data))

    with open("data/raw/catalog_metadata.json", "w") as f:
        json.dump(data, f, indent=2)
