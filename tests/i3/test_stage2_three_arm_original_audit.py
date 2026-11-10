"""Read-only archival auditor tests. Synthetic dictionaries, no Worlds/lives."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from i3.lab import stage2_three_arm_original_audit as A


class ThreeArmArchiveAuditTests(unittest.TestCase):
    def test_exact_source_pins(self):
        self.assertEqual(A.UNITS,64)
        self.assertEqual(A.HORIZON,400)
        self.assertEqual(len(A.SOURCE),40)
        self.assertEqual(len(A.MANIFEST_SHA256),64)
        self.assertEqual(A.POLICIES[2],
                         "p13_replay_gate_random_equal_mean_v1")

    def test_original_row_reconstructed_from_actual_payment_not_nominal(self):
        identity={"index":360000,"pair_id":"three-dev-000000",
                  "cohort":"development","family":"stable",
                  "world_seed":121,"genome_seed":122,"life_seed":123,
                  "policy":A.POLICIES[2]}
        schedule={"draws_funded":2,"nominal_replays_scheduled":13,
                  "eligible_replays_scheduled":11,"actual_replays_paid":10,
                  "lived_sleep_ordinals":2,"mean_numerator":5532,
                  "mean_denominator":867}
        life={
            "manifest":{"source":{"sha256":"source"},"genome":{"a":1},
                        "life_seed":123,"world_sha256":"world",
                        "experimental_policy":{"name":A.POLICIES[2]}},
            "admission_receipt":{
                "cohort":"development","family":"stable","index":360000,
                "world_seed":121,"world_sha256":"world","world_name":"name",
                "transport_fingerprint":A.SOURCE_FINGERPRINT},
            "world":"name","steps_lived":400,"terminal":"dead",
            "death_causes":["zero_water"],"actions":{"dormir":2},
            "cognitive_accounting":{
                "status":"SETTLED_FOR_DECLARED_WORK","shortfall_steps":0,
                "replays_executed":10,"inactive_steps":0,
                "totals":{"energy":{"unpaid":0.,"paid":23.},
                          "vigilance":{"unpaid":0.,"paid":19.}}},
            "replay_gate":{"random_schedule":schedule}}
        published={
            **identity,"terminal":"dead","steps_lived":400,
            "death_causes":["zero_water"],"dead_at_400":True,
            "paid_energy":23.,"paid_vigilance":19.,
            "replays_paid":10,"sleep_steps":2,"inactive_steps":0,
            "random_schedule":{k:schedule[k] for k in A.RANDOM_KEYS},
            "world_sha256":"world",
            "genome_sha256":A._hash(A._canonical({"a":1})),
            "source_sha256":"source",
        }
        self.assertEqual(A._original_row(identity,life,published,
                                          A.SOURCE_FINGERPRINT),published)
        for key,value in (("actual_replays_paid",11),
                          ("eligible_replays_scheduled",9),
                          ("nominal_replays_scheduled",15),
                          ("draws_funded",3),
                          ("mean_denominator",866)):
            bad=deepcopy(life)
            bad["replay_gate"]["random_schedule"][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                A._original_row(identity,bad,published,A.SOURCE_FINGERPRINT)
        wrong=deepcopy(published)
        wrong["paid_vigilance"]=19.1
        with self.assertRaises(ValueError):
            A._original_row(identity,life,wrong,A.SOURCE_FINGERPRINT)
        wrong=deepcopy(published)
        wrong["terminal"]="censored"
        with self.assertRaises(ValueError):
            A._original_row(identity,life,wrong,A.SOURCE_FINGERPRINT)

    def test_missing_original_manifest_must_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                A.audit(Path(d))

    def test_tree_comparison_never_silently_drops_adverse_groups(self):
        expected={"stable":{"target_only_survives":2},
                  "depletion":{"comparator_only_survives":3}}
        A._same_tree(expected,deepcopy(expected),"families")
        for found in ({"stable":{"target_only_survives":2}},
                      {"stable":{"target_only_survives":2},
                       "depletion":{"comparator_only_survives":2}},
                      {"stable":{"target_only_survives":2},
                       "depletion":{"comparator_only_survives":3},
                       "pulse":{"target_only_survives":1}}):
            with self.subTest(found=found),self.assertRaises(ValueError):
                A._same_tree(expected,found,"families")


if __name__=="__main__":
    unittest.main()
