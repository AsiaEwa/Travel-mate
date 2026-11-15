"""Optional LLM enhancement; never used to invent locations or travel times."""
from __future__ import annotations
import os


def describe_itinerary(city: str, mode: str, minutes: int, stops: list[dict], language: str) -> str | None:
    if not os.getenv("OPENAI_API_KEY"):
        return None
    try:
        from openai import OpenAI
        client = OpenAI(timeout=12.0, max_retries=0)
        prompt = ("Write 2-3 short, friendly sentences about this itinerary. "
                  "Use ONLY the factual stop list and time estimates supplied below. "
                  "Do not add attractions, opening hours, schedules, accessibility or guaranteed times. "
                  "Do not alter the order. Answer in " + ("Polish" if language == "pl" else "English") + ".\n"
                  f"City: {city}\nTransport: {mode}\nAvailable minutes: {minutes}\n"
                  f"Stops (name, visit minutes, travel minutes): "
                  + repr([(s['name'], s['visit_minutes'], s['travel_minutes']) for s in stops]))
        result = client.responses.create(model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"), input=prompt,
                                         max_output_tokens=150, store=False)
        return result.output_text.strip() or None
    except Exception:
        return None
