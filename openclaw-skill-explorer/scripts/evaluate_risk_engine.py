#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = PROJECT_ROOT / "apps" / "api"
os.chdir(API_ROOT)
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.services.risk_benchmark import (
    build_trend_summary,
    evaluate_risk_dataset,
    load_labeled_dataset,
    write_evaluation_report,
    write_trend_summary,
)


def main() -> None:
    dataset = load_labeled_dataset()
    report = evaluate_risk_dataset(dataset)
    report_path = write_evaluation_report(report)
    trend_summary = build_trend_summary()
    trend_path = write_trend_summary(trend_summary)

    aggregate = report["aggregate"]
    print(f"policy_version: {report['policy_version']}")
    print(f"total_cases: {report['total_cases']}")
    print(f"exact_flag_match_rate: {aggregate['exact_flag_match_rate']}")
    print(f"exact_risk_level_match_rate: {aggregate['exact_risk_level_match_rate']}")
    print(f"false_positive_total: {aggregate['false_positive_total']}")
    print(f"false_negative_total: {aggregate['false_negative_total']}")
    print(f"report: {report_path}")
    print(f"trend_summary: {trend_path}")


if __name__ == "__main__":
    main()
