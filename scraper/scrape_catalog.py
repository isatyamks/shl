import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/products/product-catalog/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (SHL-Assessment-Scraper)"
}

PAGE_SIZE = 12  # SHL uses 12 products per page
TYPE = 1     # Individual Test Solutions ONLY

def scrape_page(start):
    params = {
        "start": start,
        "type": TYPE
    }

    r = requests.get(CATALOG_URL, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    links = set()
    for a in soup.select("a[href]"):
        href = a["href"]
        if "/products/product-catalog/view/" in href:
            full_url = urljoin(BASE_URL, href)
            print(f"  Found: {full_url}")
            links.add(full_url)

    return links

def scrape_all():
    all_links = set()
    start = 1

    while True:
        print(f"Scraping page with start={start}")
        links = scrape_page(start)

        if not links:
            print("No more products found. Stopping.")
            break

        before = len(all_links)
        all_links.update(links)
        after = len(all_links)

        print(f"  Found {len(links)} links | Total unique: {after}")

        start += PAGE_SIZE
        time.sleep(1)

    return sorted(all_links)

if __name__ == "__main__":
    links = scrape_all()
    print("\nFINAL COUNT:", len(links))

    with open("data/raw/assessment_links.txt", "w") as f:
        for link in links:
            f.write(link + "\n")
