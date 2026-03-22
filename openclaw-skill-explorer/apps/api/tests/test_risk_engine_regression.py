from __future__ import annotations

import unittest

from app.services.risk_benchmark import load_labeled_dataset
from app.services.risk_engine import CAPABILITY_ORDER, RISK_POLICY_VERSION, scan_text


class RiskEngineRegressionTests(unittest.TestCase):
    def test_labeled_dataset_regressions(self) -> None:
        dataset = load_labeled_dataset()
        self.assertGreater(len(dataset), 0)

        for case in dataset:
            with self.subTest(case_id=case["id"]):
                result = scan_text(
                    case["text"],
                    metadata_context=case.get("metadata_context"),
                )
                self.assertEqual(result["policy_version"], RISK_POLICY_VERSION)
                self.assertEqual(result["risk_level"], case["expected_risk_level"])
                for capability in CAPABILITY_ORDER:
                    expected = bool(case["expected_flags"].get(capability, False))
                    actual = bool(result["flags"].get(capability, False))
                    self.assertEqual(
                        actual,
                        expected,
                        msg=f"{case['id']} capability mismatch for {capability}",
                    )

    def test_detected_capabilities_emit_reasons(self) -> None:
        result = scan_text(
            "This automation can run command steps, use powershell for setup, and call api services "
            "with a long review guide describing expected outputs, approval checkpoints, validation "
            "notes, operator boundaries, rollback handling, and maintenance safeguards."
        )
        self.assertEqual(result["risk_level"], "HIGH")
        self.assertTrue(result["flags"]["shell_exec"])
        self.assertTrue(result["flags"]["network_access"])
        self.assertGreaterEqual(len(result["reasons"]), 2)
        self.assertGreaterEqual(len(result["evidence_snippets"]), 2)


if __name__ == "__main__":
    unittest.main()
