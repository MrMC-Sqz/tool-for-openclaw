from __future__ import annotations

from app.services.risk_keywords import RISK_KEYWORDS, RISK_WEIGHTS
from app.services.text_utils import safe_lower

RISK_POLICY_VERSION = "v1.0.0"
CAPABILITY_ORDER = [
    "file_read",
    "file_write",
    "network_access",
    "shell_exec",
    "secrets_access",
    "external_download",
    "app_access",
    "unclear_docs",
]


def detect_capabilities(text: str, metadata_context: dict | None = None) -> tuple[dict[str, bool], dict[str, list[str]]]:
    lowered_text = safe_lower(text)
    flags: dict[str, bool] = {}
    matched_keywords: dict[str, list[str]] = {}

    for capability in CAPABILITY_ORDER:
        if capability == "unclear_docs":
            continue
        terms = RISK_KEYWORDS.get(capability, [])
        matched = [term for term in terms if term in lowered_text]
        flags[capability] = len(matched) > 0
        matched_keywords[capability] = matched

    context = metadata_context or {}
    description_text = safe_lower(context.get("description"))
    readme_text = safe_lower(context.get("readme"))
    unclear_due_to_short_text = len(lowered_text) < 180
    unclear_due_to_missing_docs = (not description_text) and (len(readme_text) < 120)

    flags["unclear_docs"] = unclear_due_to_short_text or unclear_due_to_missing_docs
    matched_keywords["unclear_docs"] = (
        ["short_or_vague_documentation"] if flags["unclear_docs"] else []
    )

    return flags, matched_keywords


def calculate_risk_score(flags: dict[str, bool]) -> int:
    total = 0
    for capability in CAPABILITY_ORDER:
        if flags.get(capability):
            total += RISK_WEIGHTS.get(capability, 0)
    return total


def classify_risk_level(score: int) -> str:
    if score <= 19:
        return "LOW"
    if score <= 39:
        return "MEDIUM"
    if score <= 69:
        return "HIGH"
    return "CRITICAL"


def compare_policy_versions(current_version: str, target_version: str) -> int:
    def _parse(version: str) -> tuple[int, int, int]:
        normalized = version.lower().strip().lstrip("v")
        parts = normalized.split(".")
        major = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
        minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        return (major, minor, patch)

    current = _parse(current_version)
    target = _parse(target_version)
    if current < target:
        return -1
    if current > target:
        return 1
    return 0


def generate_reasons(flags: dict[str, bool], matched_keywords: dict[str, list[str]]) -> list[str]:
    reasons: list[str] = []

    if flags.get("file_read"):
        reasons.append("The skill appears able to read local files or directories.")
    if flags.get("file_write"):
        reasons.append("The skill appears able to write, edit, or delete local files.")
    if flags.get("network_access"):
        reasons.append("The skill appears able to communicate with external services.")
    if flags.get("shell_exec"):
        reasons.append("The skill appears able to execute shell or system commands.")
    if flags.get("secrets_access"):
        reasons.append("The skill appears able to access secrets or credentials.")
    if flags.get("external_download"):
        reasons.append("The skill appears able to download remote files or packages.")
    if flags.get("app_access"):
        reasons.append("The skill appears able to access third-party apps or personal data.")
    if flags.get("unclear_docs"):
        reasons.append("Documentation is too limited or vague for confident behavior assessment.")

    for capability in CAPABILITY_ORDER:
        keywords = matched_keywords.get(capability, [])
        if keywords and capability != "unclear_docs":
            reasons.append(f"Detected {capability} signals: {', '.join(keywords[:3])}.")

    return reasons


def generate_recommendations(flags: dict[str, bool], level: str) -> list[str]:
    recommendations: list[str] = ["Review the repository code before use."]

    if flags.get("secrets_access"):
        recommendations.append("Avoid granting secrets unless they are strictly necessary.")
    if flags.get("shell_exec"):
        recommendations.append("Avoid granting unrestricted shell access.")
    if flags.get("network_access"):
        recommendations.append("Review and restrict outbound network destinations.")
    if flags.get("file_write"):
        recommendations.append("Use least-privilege file system permissions.")
    if flags.get("external_download"):
        recommendations.append("Verify remote downloads and pin trusted sources.")
    if flags.get("app_access"):
        recommendations.append("Limit third-party app scopes to only required data.")
    if flags.get("unclear_docs"):
        recommendations.append("Request clearer documentation before enabling broad permissions.")
    if level in {"HIGH", "CRITICAL"}:
        recommendations.append("Test this skill in an isolated environment first.")

    deduped: list[str] = []
    for item in recommendations:
        if item not in deduped:
            deduped.append(item)
    return deduped


def generate_evidence_snippets(matched_keywords: dict[str, list[str]]) -> list[str]:
    snippets: list[str] = []
    for capability in CAPABILITY_ORDER:
        keywords = matched_keywords.get(capability, [])
        for keyword in keywords[:2]:
            snippet = f"{capability}:{keyword}"
            if snippet not in snippets:
                snippets.append(snippet)
    return snippets


def scan_text(text: str, metadata_context: dict | None = None) -> dict:
    flags, matched_keywords = detect_capabilities(text, metadata_context=metadata_context)
    score = calculate_risk_score(flags)
    level = classify_risk_level(score)
    reasons = generate_reasons(flags, matched_keywords)
    recommendations = generate_recommendations(flags, level)
    evidence_snippets = generate_evidence_snippets(matched_keywords)
    return {
        "policy_version": RISK_POLICY_VERSION,
        "risk_level": level,
        "risk_score": score,
        "flags": flags,
        "matched_keywords": matched_keywords,
        "evidence_snippets": evidence_snippets,
        "reasons": reasons,
        "recommendations": recommendations,
    }
