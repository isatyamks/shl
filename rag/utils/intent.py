from typing import Optional, Dict, Any

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama import ChatOllama

from rag.utils.models import UserIntent

def infer_intent_with_langchain(query: str) -> Optional[Dict[str, Any]]:
    try:
        llm = ChatOllama(model="llama3", format="json", temperature=0)
        parser = JsonOutputParser(pydantic_object=UserIntent)
        prompt = PromptTemplate(
            template="""You are an expert intent classifier for a job assessment recommendation system.
            
            Analyze this user query: "{query}"
            
            Extract the following information into a strictly formatted JSON object:
            {format_instructions}
            
            Return ONLY the JSON.
            """,
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | llm | parser
        result = chain.invoke({"query": query})
        result["categories"] = set(result.get("categories", []))
        return result

    except Exception as e:
        print(f"GenAI Intent Error: {e}. Falling back to manual logic.")
        return None

def infer_intent(query: str) -> Dict[str, Any]:
    intent = infer_intent_with_langchain(query)
    if intent:
        return intent
    
    return {
        "categories": set(),
        "explicit_keywords": [],
        "behavioral": False,
        "duration_max": None,
        "is_entry_level": False
    }
