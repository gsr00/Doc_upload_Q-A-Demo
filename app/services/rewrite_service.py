"""Rewrite service built on top of the LLM gateway."""
from __future__ import annotations

from app import prompts
from app.services.llm_gateway import generate_text

GOALS_MAX_CHARS = 500
NOTES_MAX_CHARS = 1000


def _clean_goals(goals: list[str] | None) -> list[str]:
    if not goals:
        return []
    cleaned = [goal.strip() for goal in goals if goal.strip()]
    total_chars = sum(len(goal) for goal in cleaned)
    if total_chars > GOALS_MAX_CHARS:
        raise ValueError("Goals too long; please keep under 500 characters total.")
    return cleaned


def _validate_notes(notes: str | None) -> str | None:
    if notes is None:
        return None
    cleaned = notes.strip()
    if len(cleaned) > NOTES_MAX_CHARS:
        raise ValueError("Notes too long; please keep under 1000 characters.")
    return cleaned or None


def _build_user_prompt(text: str, goals: list[str], notes: str | None) -> str:
    parts = ["Rewrite the document below.\n", "Document:\n", text.strip(), "\n"]
    if goals:
        goals_block = "\n".join(f"- {goal}" for goal in goals)
        parts.extend(["Goals:\n", goals_block, "\n"])
    if notes:
        parts.extend(["User notes:\n", notes.strip(), "\n"])
    parts.append("Return only the rewritten document text.")
    return "\n".join(parts)


def rewrite_document(text: str, goals: list[str] | None = None, notes: str | None = None) -> str:
    if not text or not text.strip():
        raise ValueError("Document text is empty.")
    cleaned_goals = _clean_goals(goals)
    cleaned_notes = _validate_notes(notes)
    prompt = _build_user_prompt(text, cleaned_goals, cleaned_notes)
    llm_response = generate_text(prompt, system=prompts.REWRITE_PROMPT)
    return llm_response.content
