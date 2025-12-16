import json
from scraper.parser import parse_assessment

with open("data/raw/assessment_links.json") as f:
    links = json.load(f)

catalog = []
for i, url in enumerate(links):
    print(f"Scraping [{i+1}/{len(links)}]: {url}")
    try:
        item = parse_assessment(url)
        if item["name"]:
            item["id"] = f"shl_{i:04d}"
            catalog.append(item)
            print(f"  Success: {item['name']}")
    except Exception as e:
        print(f"  Failed: {e}")

with open("data/raw/catalog_raw.json", "w") as f:
    json.dump(catalog, f, indent=2)

print("Total assessments:", len(catalog))
