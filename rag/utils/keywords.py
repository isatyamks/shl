from typing import List

def normalize_keywords(keywords: List[str]) -> List[str]:
    expanded = set(keywords)
    mapping = {
        "js": "javascript",
        "java script": "javascript",
        "react": "reactjs",
        "node": "node.js",
        "dotnet": ".net",
        "c#": "c#",
        "cpp": "c++",
        "qa": "testing",
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "db": "database",
        "admin": "administration",
        "hr": "human resources",
        "accountant": "accounting",
        "aptitude": "verify",
        "reasoning": "verify"
    }
    
    for k in keywords:
        lower_k = k.lower()
        if lower_k in mapping:
            expanded.add(mapping[lower_k])
    
    return list(expanded)
