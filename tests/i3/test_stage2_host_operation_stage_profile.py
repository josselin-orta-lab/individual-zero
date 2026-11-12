"""No-World host-stage profiler safeguards; Stage 2.1 scientific HOLD."""
import unittest
from unittest.mock import patch

from i3.lab import stage2_host_operation_stage_profile as P
from i3.lab import stage2_compact_host_operator_coverage as OLD
from i3.lab.stage2_compact_distress_shadow import CompactPersonalDistressHead
from i3.modules.body import CognitiveWork
from i3.modules.mind import Mind
from i3.modules.world import World


class Stage2HostOperationStageProfileTests(unittest.TestCase):
    def test_all_predeclared_structural_cells_are_modeled_equal_paid(self):
        with patch.object(World, "__init__",
                          side_effect=AssertionError("World forbidden")), patch(
                              "i3.runtime.life.run_life",
                              side_effect=AssertionError("born life forbidden")):
            report = P.audit()
        self.assertEqual(report["status"], "STAGE_PROFILE_PARITY_PASS")
        self.assertEqual(report["predeclared_cells"], 10)
        self.assertEqual(report["modeled_arms"],
                         ["priority", "random", "discard"])
        self.assertEqual(report["repeats_per_arm"], 2)
        self.assertEqual(report["stage_names"], list(P.STAGES))
        self.assertEqual(len(report["rows"]), 30)
        self.assertEqual(len(report["deterministic_structural_sha256"]), 64)
        self.assertEqual(report["native_World_debits_observed"], 0)
        self.assertEqual(report["scientific_lives"], 0)
        self.assertEqual(report["worlds_opened"], 0)
        self.assertEqual(report["scientific_verdict"], "NOT_ISSUED")
        self.assertFalse(report["host_cpu_joules_calibrated"])
        for row in report["rows"]:
            n = row["memories"]
            self.assertTrue(row["source_and_rng_unchanged"])
            self.assertFalse(row["native_World_debit_occurred"])
            self.assertEqual(row["native_model_work"], {
                "cycles": 7, "simulated_steps": 0,
                "memory_items": 4*n+6, "replays": 3})
            counts = row["counts"]
            self.assertEqual(counts["head_records_copied"], n)
            self.assertEqual(counts["snapshot_items_read"], n)
            self.assertEqual(counts["priority_key_visits"], n)
            self.assertEqual(counts["hmac_identity_messages"], n)
            self.assertGreater(counts["hmac_payload_bytes"], n)
            self.assertEqual(counts["learning_updates"], 3)
            self.assertEqual(counts["forecast_calls"], 5)
            self.assertEqual(row["optional_host_stages_executed"], 4)
            self.assertEqual(set(row["stage_diagnostics"]), set(P.STAGES))
            for d in row["stage_diagnostics"].values():
                self.assertGreaterEqual(d["median_elapsed_ns"], 0)
                self.assertGreater(d["median_peak_traced_bytes"], 0)

    def test_low_energy_or_vigilance_refuses_before_head_or_selection(self):
        for body in ((0.2,60.,50.,90.,80.),
                     (70.,60.,50.,90.,0.1)):
            with self.subTest(body=body), patch.object(
                    CompactPersonalDistressHead, "__init__",
                    side_effect=AssertionError("unfunded head")), patch.object(
                    P, "_both_selectors",
                    side_effect=AssertionError("unfunded selection")):
                result = P.profile_once(6, 0, "priority", body=body)
            self.assertEqual(result["status"], "REFUSED_NOT_EXECUTED")
            self.assertEqual(result["optional_host_stages_executed"], 0)
            self.assertEqual(result["native_model_work"], {
                "cycles": 0, "simulated_steps": 0,
                "memory_items": 0, "replays": 0})
            self.assertEqual(result["worlds"], 0)
            self.assertEqual(result["lives"], 0)

    def test_original_model_and_rng_are_unmodified(self):
        # Source integrity uses the same existing lab-only full seal.
        original = P._source_seal
        with patch.object(P, "_source_seal", wraps=original) as seal:
            result = P.profile_once(12, 256, "discard")
        self.assertEqual(seal.call_count, 2)
        self.assertTrue(result["source_and_rng_unchanged"])
        self.assertEqual(result["counts"]["forecast_calls"], 5)
        self.assertEqual(result["counts"]["learning_updates"], 3)

    def test_wrong_operator_counts_fail_closed(self):
        original = P._both_selectors
        def tamper(memory):
            value = original(memory)
            return {**value, "hmac_identity_messages": len(memory)-1}
        with patch.object(P, "_both_selectors", side_effect=tamper):
            # A forged selector receipt cannot be called full parity.
            with self.assertRaisesRegex(RuntimeError, "parity defect"):
                P.audit()

    def test_balance_mismatch_is_detected_not_hidden_by_equal_model_ticket(self):
        actual = P.balanced_refit_forecast
        def drop_post(*, head, memory, indices, body, mode):
            r = actual(head=head, memory=memory, indices=indices,
                       body=body, mode=mode)
            return {**r, "posttraining_forecast_computed": False}
        with patch.object(P, "balanced_refit_forecast",
                          side_effect=drop_post):
            with self.assertRaisesRegex(RuntimeError, "unequal actual"):
                P.profile_once(6, 0, "discard")

    def test_frozen_domain_rejects_invalid_inputs(self):
        for kwargs in (
            {"n":5,"extras":0,"mode":"priority"},
            {"n":6,"extras":1,"mode":"priority"},
            {"n":6,"extras":0,"mode":"oracle"},
            {"n":True,"extras":0,"mode":"priority"},
            {"n":6,"extras":0,"mode":None}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    P.profile_once(**kwargs)


if __name__ == "__main__":
    unittest.main()
