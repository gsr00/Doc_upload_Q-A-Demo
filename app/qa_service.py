"""Q&A service built on top of the LLM gateway."""

from __future__ import annotations

from app import prompts
from app.llm_gateway import generate_text


def answer_question(question: str) -> str:
    """Generate an answer for a general drafting question using the persona prompt."""
    user_prompt = (
        f"{question}\n\n"
        "Respond succinctly in 3-6 sentences."
    )
    llm_response = generate_text(user_prompt, system=prompts.PERSONA_PROMPT)
    return llm_response.content
