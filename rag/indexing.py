import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

CATALOG_PATH = "data/processed/catalog.json"
INDEX_PATH = "data/processed/faiss.index"
META_PATH = "data/processed/faiss_meta.json"


model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    device='cpu'
)

def build_embedding_text(item):
    types_str = ", ".join(item.get("test_type", []))
    
    return (
        f"Assessment Name: {item['name']}\n"
        f"Category: {types_str}\n"
        f"Description: {item['description']}\n"
        f"Features: Remote Support: {item.get('remote_support', 'No')}, "
        f"Adaptive: {item.get('adaptive_support', 'No')}"
    )

def main():
    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            catalog = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {CATALOG_PATH}. Make sure you ran the crawler first.")
        return

    print(f"Indexing {len(catalog)} items...")
    
    texts = [build_embedding_text(i) for i in catalog]

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    
    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"Successfully indexed {index.ntotal} items to {INDEX_PATH}")

if __name__ == "__main__":
    main()