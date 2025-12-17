from typing import Optional, Dict, Any
import json
import time

from groq import Groq

from rag.utils.models import UserIntent

def infer_intent_with_langchain(query: str) -> Optional[Dict[str, Any]]:
    max_retries = 3
    base_delay = 1

    for attempt in range(max_retries):
        try:
            client = Groq()

            format_instructions = """{
    "categories": ["array of strings from: tech, sales, admin, leadership, marketing, general, finance, hr, operations"],
    "explicit_keywords": ["array of strings - specific hard skills (e.g. Java, Excel, Accounting) or soft skills found in the query"],
    "behavioral": "boolean - true if the user asks for soft skills, collaboration, personality, or culture fit",
    "duration_max": "null or integer - maximum duration in minutes. Convert hours to minutes (e.g. 1 hour = 60)",
    "is_entry_level": "boolean - true if query mentions graduate, fresher, entry level, or 0-2 years"
}"""

            prompt = f"""You are an expert intent classifier for a job assessment recommendation system.

Analyze this user query: "{query}"

Extract the following information into a strictly formatted JSON object:
{format_instructions}

Return ONLY the JSON, no additional text or markdown formatting."""

            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                max_completion_tokens=8192,
                top_p=1,
                reasoning_effort="medium",
                stream=True,
                stop=None
            )

            response_text = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    response_text += chunk.choices[0].delta.content

            response_text = response_text.strip()

            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            result = json.loads(response_text)

            validated_result = UserIntent(**result).model_dump()
            validated_result["categories"] = set(validated_result.get("categories", []))
            return validated_result

        except Exception as e:
            error_str = str(e)

            is_retryable = (
                "503" in error_str or
                "429" in error_str or
                "overloaded" in error_str.lower() or
                "UNAVAILABLE" in error_str or
                "rate limit" in error_str.lower()
            )

            if is_retryable and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"GenAI Intent Error (attempt {attempt + 1}/{max_retries}): {error_str}")
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                continue

            if is_retryable:
                print(f"GenAI Intent Error: Model overloaded after {max_retries} attempts. Falling back to manual logic.")
            else:
                print(f"GenAI Intent Error: {error_str}. Falling back to manual logic.")
            return None

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
