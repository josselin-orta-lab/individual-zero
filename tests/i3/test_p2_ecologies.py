"""P2 software fences only; these tests are never selection/validation studies."""
import copy
from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p2_ecologies as eco
from i3.lab import p2_validation as val
from i3.lab.probes import IDLE, _funded_step, reference_survival
from i3.modules.body import CognitiveWork, cognitive_cost
from i3.modules.genome import generation_zero
from i3.modules.world import World


class P2EcologyContractTests(unittest.TestCase):
    def test_frozen_disjoint_ranges_and_old_g2e_exclusion(self):
        m = eco.partition_manifest()
        self.assertEqual(m, eco.partition_manifest())
        self.assertEqual(set(m["evolution_mix"]), set(eco.FAMILIES))
        self.assertEqual(len(set(eco.FAMILIES)), 3)
        ranges = list(eco.COHORTS.values())
        for i, a in enumerate(ranges):
            for b in ranges[i + 1:]:
                self.assertTrue(a.stop <= b.start or b.stop <= a.start)
            self.assertNotIn(100, a)
            self.assertNotIn(1_000_200, a)
        self.assertEqual(sum(eco.EVOLUTION_MIX.values()), 3)

    def test_reserved_worlds_are_locked(self):
        with self.assertRaises(PermissionError):
            eco.world_for("stable", "reserve", 0)
        with self.assertRaises(ValueError):
            eco.world_for("stable", "development", -1)
        with self.assertRaises(ValueError):
            eco.world_for("stable", "development", 100)
        with self.assertRaises(ValueError):
            eco.world_for("stable", "selection", True)
        with self.assertRaises(ValueError):
            eco.world_for("R", "selection", 0)
        with self.assertRaises(ValueError):
            eco.world_for("stable", "unknown", 0)

    def test_worlds_are_reproducible_and_distinct(self):
        hashes = {}
        for family in eco.FAMILIES:
            spec = eco.world_for(family, "development", 0)
            self.assertEqual(eco.fingerprint(spec), eco.fingerprint(
                eco.world_for(family, "development", 0)))
            self.assertNotEqual(eco.fingerprint(spec), eco.fingerprint(
                eco.world_for(family, "development", 1)))
            self.assertEqual(spec.name.split("-")[1], family)
            hashes[family] = eco.fingerprint(spec)
        self.assertEqual(len(set(hashes.values())), len(eco.FAMILIES))

    def test_mechanisms_are_real_not_just_new_seeds(self):
        stable = eco.world_for("stable", "development", 1)
        depletion = eco.world_for("depletion", "development", 1)
        pulse = eco.world_for("pulse", "development", 1)
        self.assertFalse(stable.changes)
        self.assertTrue(all(s.stock is None for s in stable.water.values()))
        self.assertEqual(sum(s.stock is None for s in depletion.water.values()), 1)
        self.assertEqual(sum(s.stock is not None for s in depletion.water.values()), 1)
        self.assertTrue(all(s.restock_every == 0 for s in depletion.water.values()))
        self.assertTrue(pulse.changes)
        self.assertIn(0, {x[3] for x in pulse.changes})
        self.assertIn(3, {x[3] for x in pulse.changes})
        self.assertTrue(all(s.stock is not None for s in pulse.water.values()))

    def test_corrupted_resources_are_rejected(self):
        spec = eco.world_for("stable", "development", 2)
        with self.assertRaises(ValueError):
            eco.validate_ecology(replace(spec, water={}), "stable")
        with self.assertRaises(ValueError):
            eco.validate_ecology(replace(spec, food={}), "stable")
        bad = replace(spec, water={(spec.width, 0): next(iter(spec.water.values()))})
        with self.assertRaises(ValueError):
            eco.validate_ecology(bad, "stable")

    def test_no_world_fact_enters_first_person_capture(self):
        for family in eco.FAMILIES:
            spec = eco.world_for(family, "development", 3)
            visible = World(spec).capture()
            self.assertEqual(set(visible), {"body", "inventory", "here", "neighbors"})
            self.assertNotIn("changes", str(visible))
            self.assertNotIn("token_effects", str(visible))


class P2PaidProbeTests(unittest.TestCase):
    def test_fixed_paid_probe_work_is_identical_to_declared_tariff(self):
        spec = eco.world_for("stable", "development", 4)
        decision = CognitiveWork(cycles=3, simulated_steps=2)
        learning = CognitiveWork(cycles=1, simulated_steps=2)
        schedule = ((decision, learning),) * 8
        audit = []
        steps = reference_survival(spec, 8, work_schedule=schedule, audit=audit)
        self.assertEqual(steps, 8)
        self.assertEqual(len(audit), 8)
        self.assertTrue(all(x["status"] == "MATCHED" for x in audit))
        self.assertTrue(all(x["paid_decision"] == decision for x in audit))
        self.assertTrue(all(x["paid_learning"] == learning for x in audit))
        energy = sum(cognitive_cost(spec.laws, x["paid_decision"])[0] +
                     cognitive_cost(spec.laws, x["paid_learning"])[0] for x in audit)
        self.assertAlmostEqual(energy, 8 * sum(cognitive_cost(spec.laws, x)[0]
                                               for x in (decision, learning)))

    def test_no_free_probe_action_or_learning_with_zero_tariff(self):
        spec = eco.world_for("stable", "development", 5)
        audit = []
        steps = reference_survival(spec, 5, work_schedule=((IDLE, IDLE),) * 5,
                                   audit=audit)
        self.assertEqual(steps, 5)
        self.assertTrue(all(x["command"] is None for x in audit))
        self.assertTrue(all(x["paid_decision"] == IDLE and
                            x["paid_learning"] == IDLE for x in audit))

    def test_unfunded_tariff_is_reported_not_forgiven(self):
        spec = eco.world_for("stable", "development", 6)
        w = World(replace(spec, body=(0.05, 50.0, 50.0, 90.0, 0.01)))
        audit = []
        _funded_step(w, "dormir", None, decision_work=CognitiveWork(cycles=100),
                     audit=audit)
        self.assertEqual(audit[0]["status"], "UNFUNDED_DECISION")
        self.assertIsNone(audit[0]["command"])
        self.assertEqual(audit[0]["paid_decision"], IDLE)

    def test_reference_exhausted_is_not_fabricated_as_death(self):
        spec = eco.world_for("stable", "development", 7)
        audit = []
        self.assertEqual(reference_survival(spec, 30, work_schedule=((IDLE, IDLE),) * 3,
                                            audit=audit), 3)
        self.assertEqual(len(audit), 3)

    def test_pair_reports_actual_paid_costs_and_incomplete_comparisons(self):
        spec = eco.world_for("stable", "development", 8)
        out = val.assess_pair(generation_zero(6000), spec, 8, 35)
        self.assertEqual(out["probe"], "reference")
        self.assertEqual(out["information"], "capture_only")
        self.assertEqual(out["compared_ticks"], len(out["probe_audit"]))
        self.assertEqual(out["unmatched_ticks"],
                         out["compared_ticks"] - out["exactly_matched_ticks"])
        for channel in ("energy", "vigilance"):
            self.assertGreaterEqual(out["costs_requested"][channel] + 1e-9,
                                    out["costs_paid"][channel])
        if not out["full_cost_match"]:
            self.assertEqual(out["interpretation"],
                             "partial_or_unfunded_not_a_fair_survival_ceiling")
        self.assertEqual(out["world_sha256"], eco.fingerprint(spec))

    def test_no_hidden_world_info_in_reference_audit(self):
        spec = eco.world_for("depletion", "development", 9)
        out = val.assess_pair(generation_zero(6000), spec, 9, 15)
        self.assertEqual(out["information"], "capture_only")
        self.assertTrue(all("token_effects" not in row and "changes" not in row
                            for row in out["probe_audit"]))


if __name__ == "__main__":
    unittest.main()
