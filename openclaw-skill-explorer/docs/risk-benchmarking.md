# Risk Benchmarking

## Goal

This project uses a small labeled dataset to keep the deterministic risk engine stable as rules evolve.

## Dataset

- Dataset file: `scripts/data/risk_eval_dataset.json`
- Coverage:
  - file read
  - file write
  - network access
  - shell execution
  - secrets access
  - external download
  - app access
  - unclear documentation

## Run Evaluation

Generate a benchmark report and update trend history:

```bash
python scripts/evaluate_risk_engine.py
```

Outputs:

- timestamped report: `scripts/reports/risk_eval_*.json`
- rolling trend summary: `scripts/reports/risk_eval_summary.json`

## Run Regression Tests

```bash
cd apps/api
python -m unittest discover -s tests -p "test_*.py"
```

## What We Track

- exact flag match rate
- exact risk level match rate
- false positive total
- false negative total
- per-capability precision and recall
