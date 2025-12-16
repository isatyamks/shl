from typing import List, Dict

from rag.utils.intent import infer_intent
from rag.utils.keywords import normalize_keywords

def rerank(results: List[Dict], query: str, top_k: int = 5) -> List[Dict]:
    intent = infer_intent(query)
    q = query.lower()
    
    search_keywords = normalize_keywords(intent["explicit_keywords"])
    
    if "java script" in q or "javascript" in q:
        if "javascript" not in [k.lower() for k in search_keywords]:
            search_keywords.append("javascript")
    elif "java" in q:
        if "javascript" not in q and "java script" not in q:
            if "java" not in [k.lower() for k in search_keywords]:
                search_keywords.append("java")
    
    other_langs = ["python", "sql", "c++", "c#", ".net", "react", "node.js", "js"]
    for lang in other_langs:
        if lang in q and lang not in [k.lower() for k in search_keywords]:
            search_keywords.append(lang)
    
    search_keywords = normalize_keywords(search_keywords)
    
    scored = []

    for item in results:
        score = 0.0
        name = item.get("name", "").lower()
        desc = item.get("description", "").lower()
        test_types = item.get("test_type", [])
        
        for kw in search_keywords:
            kw_lower = kw.lower()
            
            if kw_lower in ["javascript", "js"]:
                if "javascript" in name:
                    score += 30.0
                elif "javascript" in desc:
                    score += 10.0
            elif kw_lower == "java":
                if "javascript" not in name and "java" in name:
                    score += 30.0
                elif "javascript" not in desc and "java" in desc:
                    score += 10.0
            else:
                if kw_lower in name:
                    score += 30.0
                elif kw_lower in desc:
                    score += 10.0

        if "tech" in intent["categories"]:
            if "K" in test_types: score += 5.0
            if "S" in test_types and ("coding" in name or "automata" in name): score += 15.0
            if any(x in name for x in ["development", "engineering", "programming"]): score += 5.0

        if "sales" in intent["categories"]:
            if "sales" in name: score += 20.0
            if "negotiation" in name or "commercial" in name: score += 10.0

        if "leadership" in intent["categories"]:
            if any(x in name for x in ["manager", "leader", "executive", "strategic"]): score += 15.0
            if "opq" in name or "leadership" in name: score += 15.0

        if "admin" in intent["categories"]:
            if any(x in name for x in ["admin", "clerical", "typing", "data entry", "office", "outlook", "word"]): score += 20.0

        if "marketing" in intent["categories"]:
            if any(x in name for x in ["marketing", "brand", "advertising", "seo", "digital"]): score += 20.0

        if "finance" in intent["categories"] or "accounting" in q:
            if any(x in name for x in ["accounting", "financial", "payable", "receivable", "money"]): score += 20.0

        if "hr" in intent["categories"]:
            if "human resources" in name or "training" in name: score += 20.0

        if "general" in intent["categories"] or any(x in q for x in ["aptitude", "reasoning", "cognitive", "ability"]):
            if "verify" in name or "reasoning" in name or "calculation" in name or "comprehension" in name:
                score += 25.0
            if "A" in test_types: score += 10.0

        if intent["behavioral"]:
            if "P" in test_types or "B" in test_types or "C" in test_types: score += 15.0
            if any(x in name for x in ["communication", "team", "interpersonal", "motivation", "personality"]): score += 15.0

        if intent["is_entry_level"]:
            if any(x in name for x in ["graduate", "entry level", "screen", "fundamental", "basic"]):
                score += 15.0

        if intent["duration_max"]:
            dur = item.get("duration")
            if dur:
                if dur <= intent["duration_max"]: score += 10.0
                elif dur <= intent["duration_max"] + 15: score += 0.0
                else: score -= 15.0

        if "tech" in intent["categories"] and not {"admin", "sales"}.intersection(intent["categories"]):
            if "customer service" in name or "call center" in name:
                score -= 20.0

        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    
    final_results = []
    
    if intent["categories"] and intent["behavioral"]:
        hard_bucket = []
        soft_bucket = []
        others = []

        for _, item in scored:
            t_types = item.get("test_type", [])
            name_lower = item.get("name", "").lower()
            
            is_soft = "P" in t_types or "B" in t_types or "C" in t_types or "communication" in name_lower
            is_hard = "K" in t_types or "S" in t_types or "A" in t_types
            
            if is_soft:
                soft_bucket.append(item)
            elif is_hard:
                hard_bucket.append(item)
            else:
                others.append(item)
        
        while len(final_results) < top_k:
            if hard_bucket: final_results.append(hard_bucket.pop(0))
            if len(final_results) >= top_k: break
            
            if soft_bucket: final_results.append(soft_bucket.pop(0))
            if len(final_results) >= top_k: break
            
            if not hard_bucket and not soft_bucket:
                if others: final_results.append(others.pop(0))
                else: break
    else:
        final_results = [item for _, item in scored[:top_k]]

    return final_results
