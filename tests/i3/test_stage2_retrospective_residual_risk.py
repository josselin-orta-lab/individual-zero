"""Chronological read-only error-risk screening; no Worlds or policy."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_retrospective_residual_risk as E
from i3.modules.world import World


class RetrospectiveResidualRiskTests(unittest.TestCase):
    def test_full_fixed_320_event_analysis_no_new_world(self):
        with patch.object(World, "__init__",
                          side_effect=AssertionError("World forbidden")), patch(
                              "i3.runtime.life.run_life",
                              side_effect=AssertionError("new life forbidden")):
            r = E.audit()
        print("I3_STAGE2_RETROSPECTIVE_RESIDUAL_RISK=" +
              json.dumps(r, sort_keys=True, separators=(",", ":")))
        self.assertEqual(r["status"], "RETROSPECTIVE_RISK_EVALUATION_PASS")
        self.assertEqual(r["source_ci_sha256"], E.SOURCE_DIGEST)
        self.assertEqual(r["source_extract_sha256"], E.DERIVATIVE_SHA)
        self.assertEqual(r["technical_units"], 4)
        self.assertEqual(r["all_assigned_events"], 320)
        self.assertEqual(r["aggregate"]["n"], 320)
        self.assertEqual(r["worlds_opened"], 0)
        self.assertEqual(r["scientific_lives"], 0)
        self.assertEqual(r["scientific_verdict"], "NOT_ISSUED")
        self.assertTrue(r["retrospective_not_independent_validation"])
        self.assertTrue(r["past_only_online_estimators"])
        self.assertTrue(r["action_is_already_chosen_no_optional_funding"])
        self.assertEqual(len(r["deterministic_digest"]), 64)
        self.assertEqual(
            [(row["world"], row["seed"]) for row in r["rows"]],
            list(E.GRID))
        self.assertTrue(all(row["n"] == 80 for row in r["rows"]))
        self.assertEqual(sum(row["prior_action_available"] +
                             row["no_prior_action"] for row in r["rows"]), 320)
        self.assertEqual(r["merit_gate_met"],
                         r["unit_positive_squared_risk"] >= 3 and
                         r["unit_positive_absolute_risk"] >= 3)
        self.assertTrue(all(0 <= r[k] <= 4 for k in (
            "unit_positive_squared_risk", "unit_positive_absolute_risk")))

    def test_past_only_risk_math_and_cold_action_fallback(self):
        self.assertEqual(E.risk_before_outcome(0, 0., (0,0.)), (0.,0.))
        self.assertEqual(E.risk_before_outcome(2, 10., (0,0.)), (5.,5.))
        self.assertEqual(E.risk_before_outcome(2, 10., (1,8.)), (5.,6.5))
        # Current target can be arbitrary: the frozen past-only function
        # takes no present/future body or outcome argument whatsoever.
        for bad in ((-1,0.,(0,0.)), (2,-1.,(0,0.)),
                    (2,10.,(3,1.)), (2,10.,(1,float("nan")))):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    E.risk_before_outcome(*bad)

    def test_no_source_reselection_missing_step_or_target_repair(self):
        origin = json.loads(E.DATASET.read_text(encoding="utf-8"))
        for label in ("source", "missing", "target", "reorder", "future"):
            wrong = deepcopy(origin)
            if label == "source":
                wrong["source_ref"]["head_sha"] = "0"*40
            elif label == "missing":
                wrong["worlds"][0]["events"].pop()
            elif label == "target":
                wrong["worlds"][0]["events"][0]["actual_delta"][0] = float("nan")
            elif label == "reorder":
                wrong["worlds"][0]["events"].reverse()
            elif label == "future":
                wrong["worlds"][0]["events"][0]["action"] = None
            with self.subTest(label=label):
                with self.assertRaises(ValueError):
                    E.reduce_dataset_risk(wrong)

    def test_source_is_read_only_and_results_deterministic(self):
        original = E.DATASET.read_bytes()
        a, b = E.audit(), E.audit()
        self.assertEqual(original, E.DATASET.read_bytes())
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
