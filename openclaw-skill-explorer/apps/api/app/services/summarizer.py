from __future__ import annotations

from app.services.llm_service import call_llm


def _fallback_summary(text: str, max_chars: int = 240) -> str:
    trimmed = " ".join(text.split())
    if len(trimmed) <= max_chars:
        return trimmed
    return f"{trimmed[:max_chars].rstrip()}..."


def summarize_readme(text: str) -> str:
    if not text or not text.strip():
        return ""

    prompt = (
        "Summarize this OpenClaw skill README.\n"
        "Focus on what it does, key capabilities, and any obvious risks.\n"
        "Keep it concise, factual, and under 120 words.\n"
        "Only use the provided information. Do not assume missing capabilities.\n\n"
        f"README:\n{text}"
    )
    summary = call_llm(prompt).strip()
    if not summary:
        return _fallback_summary(text)

    words = summary.split()
    if len(words) > 120:
        summary = " ".join(words[:120]).strip()
    return summary

