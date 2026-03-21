from __future__ import annotations

import json

from app.services.llm_service import call_llm


def refine_risk_explanation(
    *,
    flags: dict[str, bool],
    matched_keywords: dict[str, list[str]],
    base_reasons: list[str],
) -> str:
    fallback = " ".join(base_reasons).strip()
    prompt = (
        "You are refining a deterministic security scan explanation for a software skill.\n"
        "Write a concise explanation (max 120 words) of why the skill may be risky.\n"
        "Use only the provided data and capabilities.\n"
        "Only use the provided information. Do not assume missing capabilities.\n\n"
        f"Flags:\n{json.dumps(flags, ensure_ascii=True)}\n\n"
        f"Matched Keywords:\n{json.dumps(matched_keywords, ensure_ascii=True)}\n\n"
        f"Base Reasons:\n{json.dumps(base_reasons, ensure_ascii=True)}\n"
    )
    refined = call_llm(prompt).strip()
    return refined or fallback

