"""P5c posthoc mortality diagnostics: pure synthetic ledgers, no worlds."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p5c_posthoc_mortality


def life(censored, steps, causes, early, inactive=0):
    return {
        "terminal": "censored" if censored else "dead",
        "censored": censored, "steps_lived": steps, "inactive_steps": inactive,
        "death_causes": causes,
        "early_witness": [{"action": a} for a in early],
        "decision_status": {
            "action_admitted": steps - inactive,
            "no_processing_budget": inactive},
        "paid": {"energy": 1.5, "vigilance": 2.0},
    }


class P5cOriginalOnlyMortalityTests(unittest.TestCase):
    def test_death_cause_multiplicity_and_horizon_are_explicit(self):
        a = life(False, 90, ["food", "water"], ["se_deplacer", "manger"], 0)
        b = life(True, 400, [], [None, "attendre", "boire"], 3)
        r = p5c_posthoc_mortality._group([a, b])
        self.assertEqual(r["lives"], 2)
        self.assertEqual(r["deaths"], 1)
        self.assertEqual(r["censored"], 1)
        self.assertEqual(r["death_causes_multi_label"], {"food":1,"water":1})
        self.assertEqual(r["dead_by_horizon"]["100"], 1)
        self.assertEqual(r["dead_by_horizon"]["400"], 1)
        self.assertEqual(r["first_12_step_action_families"],
                         {"movement":1, "resource":2, "no_action":1,
                          "rest_or_wait":1})
        self.assertEqual(r["first_12_steps_observed"], 5)
        self.assertEqual(r["total_inactive_steps"], 3)

    def test_action_family_is_only_what_original_witness_records(self):
        self.assertEqual(p5c_posthoc_mortality._action_family("se_deplacer"),
                         "movement")
        self.assertEqual(p5c_posthoc_mortality._action_family(None),
                         "no_action")
        self.assertEqual(p5c_posthoc_mortality._action_family("boire"),
                         "resource")
        self.assertEqual(p5c_posthoc_mortality._action_family("dormir"),
                         "rest_or_wait")
        self.assertEqual(p5c_posthoc_mortality._action_family("other"),
                         "other")

    def test_missing_original_corpus_cannot_be_presented_as_result(self):
        with patch.object(p5c_posthoc_mortality.p5c_custody, "verify",
                          return_value={"raw_canonical_sha256":"fake",
                                        "source_sha":"fake"}):
            with self.assertRaises(ValueError):
                p5c_posthoc_mortality.analyze({"lives":[]})


if __name__ == "__main__":
    unittest.main()
