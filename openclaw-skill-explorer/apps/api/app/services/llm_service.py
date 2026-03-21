from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings


def _extract_output_text(payload: dict) -> str:
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    output_items = payload.get("output")
    if isinstance(output_items, list):
        texts: list[str] = []
        for item in output_items:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                if part.get("type") in {"output_text", "text"}:
                    value = part.get("text")
                    if isinstance(value, str) and value.strip():
                        texts.append(value.strip())
        if texts:
            return "\n".join(texts).strip()

    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first_choice = choices[0]
        if isinstance(first_choice, dict):
            message = first_choice.get("message", {})
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()
    return ""


def _strip_markdown_wrappers(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```") and cleaned.endswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return cleaned


def _call_model(model_name: str, prompt: str) -> str:
    if not settings.openai_api_key:
        return ""

    url = f"{settings.openai_base_url.rstrip('/')}/responses"
    body = {
        "model": model_name,
        "input": prompt,
        "temperature": 0.2,
    }
    request = Request(
        url=url,
        method="POST",
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(body).encode("utf-8"),
    )

    with urlopen(request, timeout=settings.openai_timeout_seconds) as response:
        raw = response.read().decode("utf-8")
    payload = json.loads(raw)
    return _strip_markdown_wrappers(_extract_output_text(payload))


def call_llm(prompt: str) -> str:
    if not prompt.strip():
        return ""

    try:
        text = _call_model(settings.openai_model, prompt)
        if text:
            return text
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError):
        pass

    try:
        return _call_model(settings.openai_fallback_model, prompt)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return ""

