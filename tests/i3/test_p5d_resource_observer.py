"""P5d observer-only resource uptake falsifiers; DEVELOPMENT worlds only."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p2_ecologies
from i3.modules.body import CognitiveWork
from i3.modules.genome import generation_zero
from i3.modules.world import FoodPatch, WaterSource, World, WorldSpec
from i3.runtime.life import run_life
from i3.runtime.resource_observer import ResourceObserver


class P5dResourceObserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = p2_ecologies.world_for("stable", "development", 32)
        cls.genome = generation_zero(901)

    def test_observer_opt_in_preserves_original_life_evidence_and_paid_work(self):
        for mode in ("normal", "discard_curiosity_bonus"):
            kwargs = dict(score_addend_mode=mode, keep_trace=True)
            control = run_life(self.genome, self.spec, 7032, 48, **kwargs)
            observed = run_life(
                self.genome, self.spec, 7032, 48,
                observer_resource_acquisition=True, **kwargs)
            for key in ("trace_head", "evidence_head", "actions", "terminal",
                        "final_body", "genome", "outcome_model_sha256",
                        "cognitive_accounting", "steps_lived"):
                # Outcome-model signature is only emitted when separately
                # requested: absence on both sides is a valid parity result.
                self.assertEqual(control.get(key), observed.get(key), (mode, key))
            self.assertNotIn("observer_resource_acquisition", control)
            receipt = observed["observer_resource_acquisition"]
            self.assertEqual(receipt["summary"]["lived_steps"], observed["steps_lived"])
            self.assertEqual(len(receipt["steps"]), observed["steps_lived"])
            self.assertEqual(
                sum(row["resource_options_scored"] for row in receipt["steps"]),
                receipt["summary"]["resource_options_scored"])
            self.assertEqual(receipt["summary"]["physical_resource_contacts"],
                             sum(observed["actions"].get(k, 0)
                                 for k in ("boire", "collecter", "manger")))
            self.assertEqual(observed["cognitive_accounting"]["shortfall_steps"], 0)
            self.assertEqual(observed["cognitive_accounting"]["pending_replays"], 0)
            for step in observed["trace"]:
                for phase in ("decision", "learning"):
                    for channel in ("energy", "vigilance"):
                        bill = step["funding_phases"][phase]["accounting"][channel]
                        self.assertAlmostEqual(bill["requested"], bill["paid"])
                        self.assertEqual(bill["unpaid"], 0)
                if step["dead"]:
                    self.assertFalse(any(step["funding_phases"]["learning"]["work"].values()))

    def test_only_unused_development_worlds_are_allocated(self):
        from i3.lab import p5d_development
        plan = p5d_development.manifest()
        self.assertEqual(plan["cohort"], "DEVELOPMENT_ONLY")
        self.assertEqual(plan["validation"], "NOT_OPENED")
        self.assertEqual(plan["reserve"], "LOCKED")
        self.assertEqual({row["development_index"] for row in plan["allocation"]},
                         set(range(32, 38)))
        self.assertEqual(len(plan["allocation"]), 6)

    def test_invalid_observer_flags_fail_before_world_construction(self):
        with self.assertRaises(TypeError):
            run_life(self.genome, self.spec, 7, 5,
                     observer_resource_acquisition="yes")

    def test_all_zero_uptake_is_not_falsely_reported_as_success(self):
        spec = WorldSpec(
            "zero-gain", 1, 1, (0, 0), (60., 60., 60., 60., 60.),
            water={(0, 0): WaterSource(0., 1, 1)},
            food={(0, 0): FoodPatch("t", 1, 1)},
            token_effects={"t": (0., -2.)})
        observer = ResourceObserver()
        class LocalMind:
            pos = (0, 0)
            hist = {(0, 0): [1, 1., {}]}
        def pending(world, action, param=None):
            return observer.prepare(
                cap=world.capture(), mind=LocalMind(),
                info={"observer": {
                    "score_witness": [], "scored_families": {"resource": 0},
                    "offered_families": {"resource": 0},
                    "decision_outcome": "action_admitted"},
                    "funding": "FUNDED", "option": action},
                action=action, param=param)
        def commit(world, action, param=None):
            before = pending(world, action, param)
            result = world.step(action, param, CognitiveWork())
            phases = {
                k: {"work": {"cycles": 0}, "accounting": {
                    c: {"paid": 0.} for c in ("energy", "vigilance")}}
                for k in ("decision", "learning")}
            observer.commit(before, world=world, physical_body=result["body"],
                            dead=result["dead"], phases=phases)
            return observer.steps[-1]
        world = World(spec)
        drank = commit(world, "boire")
        self.assertTrue(drank["physical_resource_contact"])
        self.assertFalse(drank["positive_water_uptake"])
        self.assertAlmostEqual(drank["water_uptake_above_decay"], 0.)
        collected = commit(world, "collecter", "t")
        self.assertTrue(collected["collected_inventory"])
        ate = commit(world, "manger", "t")
        self.assertTrue(ate["consumed_inventory"])
        self.assertFalse(ate["positive_food_uptake"])
        self.assertLess(ate["eating_integrity_delta"], 0.)
        report = observer.report()["summary"]
        self.assertEqual(report["physical_resource_contacts"], 3)
        self.assertEqual(report["collected_inventory"], 1)
        self.assertEqual(report["positive_water_uptakes"], 0)
        self.assertEqual(report["positive_food_uptakes"], 0)

    def test_unfunded_or_invalid_physical_contact_cannot_be_committed(self):
        world = World(WorldSpec(
            "empty", 1, 1, (0, 0), (60., 60., 60., 60., 60.)))
        with self.assertRaises(ValueError):
            world.step("boire", None, CognitiveWork())
        with self.assertRaises(ValueError):
            world.step("collecter", "absent", CognitiveWork())
        self.assertEqual(world.t, 0)


if __name__ == "__main__":
    unittest.main()
