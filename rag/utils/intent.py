import os
from typing import Optional, Dict, Any

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama import ChatOllama

from rag.utils.models import UserIntent


# Use environment variables with defaults for EC2 Ubuntu
# For Docker: set OLLAMA_BASE_URL=http://host.docker.internal:11434
# For EC2 Ubuntu (native): use default http://localhost:11434
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


def infer_intent_with_langchain(query: str) -> Optional[Dict[str, Any]]:
    try:
        llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            format="json",
            temperature=0,
        )

        parser = JsonOutputParser(pydantic_object=UserIntent)

        prompt = PromptTemplate(
            template="""You are an expert intent classifier for a job assessment recommendation system.

Analyze this user query:
"{query}"

Extract the following information into a strictly formatted JSON object:
{format_instructions}

Return ONLY the JSON.
""",
            input_variables=["query"],
            partial_variables={
                "format_instructions": parser.get_format_instructions()
            },
        )

        chain = prompt | llm | parser
        result = chain.invoke({"query": query})

        # normalize
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
        "is_entry_level": False,
    }
