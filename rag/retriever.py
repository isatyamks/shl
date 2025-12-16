import json
import os
import faiss
import torch
import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR) 
INDEX_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "faiss.index")
META_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "faiss_meta.json")

_index = None
_catalog = None
_model = None

def load_resources():
    global _index, _catalog, _model
    
    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading embedding model on {device}...")
        _model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            device=device
        )

    if _index is None:
        if not os.path.exists(INDEX_PATH):
            raise FileNotFoundError(
                f"FAISS index not found at {INDEX_PATH}. "
                "Please run 'indexing.py' first."
            )
        _index = faiss.read_index(INDEX_PATH)

    if _catalog is None:
        if not os.path.exists(META_PATH):
            raise FileNotFoundError(
                f"Catalog meta not found at {META_PATH}. "
                "Please run 'indexing.py' first."
            )
        with open(META_PATH, "r", encoding="utf-8") as f:
            _catalog = json.load(f)

def retrieve(query: str, k: int = 20):
    load_resources()
    
    q_emb = _model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    D, I = _index.search(q_emb, k)
    
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx != -1:
            item = _catalog[idx].copy()
            item["vector_score"] = float(score) 
            results.append(item)
            
    return results