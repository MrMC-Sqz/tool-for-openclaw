from __future__ import annotations

import json

from app.services.llm_service import call_llm


def _parse_recommendations(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    parsed: list[str] = []
    for line in lines:
        cleaned = line.lstrip("-*0123456789. ").strip()
        if cleaned and cleaned not in parsed:
            parsed.append(cleaned)
    return parsed


def enhance_recommendations(
    *,
    risk_level: str,
    flags: dict[str, bool],
    base_recommendations: list[str],
) -> list[str]:
    prompt = (
        "Rewrite the following security recommendations to be clearer and actionable.\n"
        "Keep them grounded in the provided risk level and capability flags.\n"
        "Return 3-6 short bullet points.\n"
        "Only use the provided information. Do not assume missing capabilities.\n\n"
        f"Risk Level: {risk_level}\n"
        f"Flags: {json.dumps(flags, ensure_ascii=True)}\n"
        f"Base Recommendations: {json.dumps(base_recommendations, ensure_ascii=True)}\n"
    )
    enhanced = call_llm(prompt).strip()
    if not enhanced:
        return base_recommendations

    parsed = _parse_recommendations(enhanced)
    return parsed or base_recommendations

