import os
import json
from typing import Dict, Any
from app.utils.logger import setup_logger
from app.models import ResumeData
from langchain_groq import ChatGroq
from langchain.output_parsers import PydanticOutputParser
from pydantic import ValidationError

logger = setup_logger(os.getenv("LOG_LEVEL", "INFO"))

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

PROMPT_BODY = """
Extract structured resume fields from the text below and return JSON exactly matching the requested schema.

Text:
\"\"\"{text}\"\"\"
"""


def call_groq_langchain(prompt: str) -> str:
    """
    Call Groq LLM via LangChain to get a response for the given prompt.
    """
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY must be set for Groq provider.")
    
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=0,
        max_tokens=4096,
    )
    response = llm.invoke([
        ("system", "You are a JSON-only extraction engine. Always return valid JSON."),
        ("human", prompt)
    ])
    return getattr(response, "content", None) or str(response)


def extract_structured_json(text: str) -> Dict[str, Any]:
    """
    Extract structured resume JSON from text using LLM and Pydantic validation.
    Always returns a dict matching ResumeData or includes '_raw' if parsing fails.
    """
    parser = PydanticOutputParser(pydantic_object=ResumeData)
    format_instructions = parser.get_format_instructions()
    prompt = f"{format_instructions}\n\n{PROMPT_BODY.format(text=text)}"

    if LLM_PROVIDER != "groq":
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

    raw = call_groq_langchain(prompt)
    logger.info("LLM output received (truncated): %s", raw[:500])

    try:
        parsed_obj = parser.parse(raw)
        validated = parsed_obj.model_dump()
        logger.info("LLM output successfully validated with Pydantic")
        return validated
    except ValidationError as ve:
        logger.warning("Pydantic validation failed: %s", ve)
    except Exception as exc:
        logger.exception("Unexpected error during Pydantic parsing: %s", exc)

    # Fallback: attempt naive JSON extraction
    try:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(raw[start:end+1])
        return json.loads(raw)
    except Exception:
        logger.exception("Fallback JSON parsing failed, returning raw output")
        return {"_raw": raw}
