from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from rag.retriever import retrieve
from rag.utils import rerank, infer_intent

app = FastAPI()

TEST_TYPE_MAPPING = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behaviour",
    "S": "Simulations"
}

def map_test_types(test_types: List[str]) -> List[str]:
    return [TEST_TYPE_MAPPING.get(t, t) for t in test_types]

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/recommend")
def recommend(req: QueryRequest):
    intent = infer_intent(req.query)
    
    retrieval_k = 60
    candidates = retrieve(req.query, k=retrieval_k)

    queries_to_add = []
    
    if "sales" in intent["categories"]:
        queries_to_add.append("sales negotiation business development commercial awareness")
    
    if "leadership" in intent["categories"]:
        queries_to_add.append("leadership management executive strategy people management opq")
    
    if "admin" in intent["categories"]:
        queries_to_add.append("administrative clerical data entry typing microsoft office")
        
    if "marketing" in intent["categories"]:
        queries_to_add.append("marketing digital brand strategy creative")
    
    if "tech" in intent["categories"]:
        queries_to_add.extend(intent["explicit_keywords"])

    if intent["behavioral"]:
        queries_to_add.append("workplace collaboration interpersonal skills teamwork communication culture")

    for q_add in queries_to_add:
         candidates.extend(retrieve(q_add, k=20))

    seen = set()
    unique_candidates = []
    for item in candidates:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique_candidates.append(item)

    ranked = rerank(unique_candidates, req.query, top_k=req.top_k)
    
    if not ranked and unique_candidates:
        ranked = unique_candidates[:req.top_k]

    recommended_assessments = []
    for item in ranked:
        recommended_assessments.append({
            "url": item["url"],
            "name": item["name"],
            "adaptive_support": item["adaptive_support"],
            "description": item["description"],
            "duration": item["duration"],
            "remote_support": item["remote_support"],
            "test_type": map_test_types(item["test_type"])
        })

    return {"recommended_assessments": recommended_assessments}

@app.get("/health")
def health():
    return {"status": "healthy"}