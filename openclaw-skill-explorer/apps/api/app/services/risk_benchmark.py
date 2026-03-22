from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.risk_engine import CAPABILITY_ORDER, RISK_POLICY_VERSION, scan_text

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "scripts" / "data" / "risk_eval_dataset.json"
DEFAULT_REPORT_DIR = PROJECT_ROOT / "scripts" / "reports"


def load_labeled_dataset(dataset_path: Path | None = None) -> list[dict[str, Any]]:
    path = dataset_path or DEFAULT_DATASET_PATH
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, list):
        raise ValueError("Risk evaluation dataset must be a list.")
    return [item for item in payload if isinstance(item, dict)]


def evaluate_risk_dataset(dataset: list[dict[str, Any]]) -> dict[str, Any]:
    per_capability = {
        capability: {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
        for capability in CAPABILITY_ORDER
    }
    case_results: list[dict[str, Any]] = []
    exact_flag_matches = 0
    exact_risk_level_matches = 0
    false_positive_total = 0
    false_negative_total = 0
    policy_versions: set[str] = set()

    for case in dataset:
        result = scan_text(case.get("text", ""), metadata_context=case.get("metadata_context"))
        policy_versions.add(result.get("policy_version", RISK_POLICY_VERSION))
        expected_flags = case.get("expected_flags", {})
        predicted_flags = result.get("flags", {})

        mismatched_flags: list[dict[str, Any]] = []
        for capability in CAPABILITY_ORDER:
            expected = bool(expected_flags.get(capability, False))
            predicted = bool(predicted_flags.get(capability, False))
            if expected and predicted:
                per_capability[capability]["tp"] += 1
            elif (not expected) and predicted:
                per_capability[capability]["fp"] += 1
                false_positive_total += 1
            elif expected and (not predicted):
                per_capability[capability]["fn"] += 1
                false_negative_total += 1
            else:
                per_capability[capability]["tn"] += 1

            if expected != predicted:
                mismatched_flags.append(
                    {
                        "capability": capability,
                        "expected": expected,
                        "predicted": predicted,
                    }
                )

        risk_level_match = result.get("risk_level") == case.get("expected_risk_level")
        if not mismatched_flags:
            exact_flag_matches += 1
        if risk_level_match:
            exact_risk_level_matches += 1

        case_results.append(
            {
                "id": case.get("id"),
                "title": case.get("title"),
                "expected_risk_level": case.get("expected_risk_level"),
                "predicted_risk_level": result.get("risk_level"),
                "risk_level_match": risk_level_match,
                "expected_flags": expected_flags,
                "predicted_flags": predicted_flags,
                "mismatched_flags": mismatched_flags,
                "risk_score": result.get("risk_score"),
            }
        )

    total_cases = len(dataset)
    capability_metrics: dict[str, dict[str, Any]] = {}
    for capability, stats in per_capability.items():
        tp = stats["tp"]
        fp = stats["fp"]
        fn = stats["fn"]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        capability_metrics[capability] = {
            **stats,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
        }

    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "policy_version": sorted(policy_versions)[-1] if policy_versions else RISK_POLICY_VERSION,
        "dataset_path": str(DEFAULT_DATASET_PATH),
        "total_cases": total_cases,
        "aggregate": {
            "exact_flag_matches": exact_flag_matches,
            "exact_flag_match_rate": round(exact_flag_matches / total_cases, 4) if total_cases else 0.0,
            "exact_risk_level_matches": exact_risk_level_matches,
            "exact_risk_level_match_rate": (
                round(exact_risk_level_matches / total_cases, 4) if total_cases else 0.0
            ),
            "false_positive_total": false_positive_total,
            "false_negative_total": false_negative_total,
        },
        "per_capability": capability_metrics,
        "cases": case_results,
    }


def write_evaluation_report(
    report: dict[str, Any],
    report_dir: Path | None = None,
) -> Path:
    output_dir = report_dir or DEFAULT_REPORT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = output_dir / f"risk_eval_{timestamp}.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")
    return report_path


def build_trend_summary(report_dir: Path | None = None) -> dict[str, Any]:
    output_dir = report_dir or DEFAULT_REPORT_DIR
    history: list[dict[str, Any]] = []
    by_policy_version: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for report_path in sorted(output_dir.glob("risk_eval_*.json")):
        try:
            raw = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        aggregate = raw.get("aggregate", {})
        summary_row = {
            "report_file": report_path.name,
            "generated_at": raw.get("generated_at"),
            "policy_version": raw.get("policy_version", RISK_POLICY_VERSION),
            "exact_flag_match_rate": aggregate.get("exact_flag_match_rate", 0.0),
            "exact_risk_level_match_rate": aggregate.get("exact_risk_level_match_rate", 0.0),
            "false_positive_total": aggregate.get("false_positive_total", 0),
            "false_negative_total": aggregate.get("false_negative_total", 0),
        }
        history.append(summary_row)
        by_policy_version[summary_row["policy_version"]].append(summary_row)

    policies_summary = []
    for policy_version, rows in sorted(by_policy_version.items()):
        policies_summary.append(
            {
                "policy_version": policy_version,
                "runs": len(rows),
                "latest_generated_at": rows[-1]["generated_at"],
                "latest_exact_flag_match_rate": rows[-1]["exact_flag_match_rate"],
                "latest_exact_risk_level_match_rate": rows[-1]["exact_risk_level_match_rate"],
                "latest_false_positive_total": rows[-1]["false_positive_total"],
                "latest_false_negative_total": rows[-1]["false_negative_total"],
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "history": history,
        "by_policy_version": policies_summary,
    }


def write_trend_summary(summary: dict[str, Any], report_dir: Path | None = None) -> Path:
    output_dir = report_dir or DEFAULT_REPORT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "risk_eval_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
    return summary_path
