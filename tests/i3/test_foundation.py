"""Technical controls on development fixtures only; no held-out study."""
import copy
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab.dev_worlds import dev_long_corridor, dev_open_field
from i3.modules.body import BodyLaws, CognitiveWork, cognitive_cost, transition
from i3.modules.genome import generation_zero, midpoint
from i3.modules.mind import Mind
from i3.modules.world import World
from i3.runtime.life import run_life
from i3.runtime.provenance import build_manifest, digest, source_snapshot, world_snapshot


class CognitiveAccountingTests(unittest.TestCase):
    def test_work_refuses_negative_noninteger_and_boolean_counts(self):
        for name in ("cycles", "simulated_steps", "memory_items", "replays"):
            for value in (-1, 1.5, True, "1", float("nan"), float("inf")):
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    CognitiveWork(**{name: value})

    def test_cost_refuses_nonfinite_or_negative_rates_and_overflow(self):
        for rate in (-0.1, float("nan"), float("inf")):
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                cognitive_cost(BodyLaws(energy_per_cycle=rate), CognitiveWork())
        with self.assertRaises(ValueError):
            cognitive_cost(BodyLaws(), CognitiveWork(cycles=10 ** 1000))

    def test_invalid_bill_does_not_advance_world(self):
        for work in (None, {"cycles": 1}, CognitiveWork(cycles=10 ** 1000)):
            world = World(dev_open_field())
            before = copy.deepcopy(world.__dict__)
            with self.assertRaises((ValueError, TypeError)):
                world.step("attendre", None, work)
            self.assertEqual(world.__dict__, before)

    def test_full_payment_and_observation_do_not_change_physics(self):
        body = (50., 60., 40., 90., 50.)
        work = CognitiveWork(10, 100, 500, 10)
        audit = {"stale": True}
        expected = transition(body, "attendre", BodyLaws(), work)
        observed = transition(body, "attendre", BodyLaws(), work, accounting=audit)
        self.assertEqual(expected, observed)
        self.assertEqual(set(audit), {"energy", "vigilance"})
        for channel, bill in zip(("energy", "vigilance"), cognitive_cost(BodyLaws(), work)):
            self.assertEqual(audit[channel], {"requested": bill, "paid": bill, "unpaid": 0.})

    def test_exhausted_energy_is_not_reported_as_paid(self):
        audit = {}
        out, _ = transition((0.1, 60., 40., 90., 50.), "attendre", BodyLaws(),
                            CognitiveWork(cycles=10), accounting=audit)
        self.assertEqual(out[0], 0.)
        self.assertEqual(audit["energy"], {"requested": 0.2, "paid": 0., "unpaid": 0.2})

    def test_vigilance_shortfall_is_reported_separately(self):
        audit = {}
        transition((50., 60., 40., 90., 0.1), "attendre", BodyLaws(),
                   CognitiveWork(cycles=10), accounting=audit)
        self.assertAlmostEqual(audit["vigilance"]["unpaid"], 0.4)
        self.assertEqual(audit["energy"]["unpaid"], 0.)

    def test_zero_work_has_no_cognitive_debt(self):
        audit = {}
        transition((0., 60., 40., 90., 0.), "attendre", BodyLaws(),
                   CognitiveWork(), accounting=audit)
        for values in audit.values():
            self.assertEqual(values, {"requested": 0., "paid": 0., "unpaid": 0.})

    def test_runtime_marks_shortfall_instead_of_claiming_full_payment(self):
        def oversized(mind, cap):
            mind.last = (cap["body"], ("attendre",), "attendre", None)
            return "attendre", None, CognitiveWork(cycles=100000), {"option": "unit-wait"}
        with patch.object(Mind, "decide", oversized):
            result = run_life(midpoint(), dev_open_field(), 1, 1)
        audit = result["cognitive_accounting"]
        self.assertEqual(audit["status"], "SHORTFALL")
        self.assertEqual(audit["shortfall_steps"], 1)
        self.assertGreater(audit["totals"]["energy"]["unpaid"], 0.)
        self.assertEqual(result["terminal"], "censored")  # Not an invented death cause.

    def test_accounting_is_not_in_first_person_capture(self):
        world = World(dev_open_field())
        result = world.step("attendre", None, CognitiveWork(cycles=1))
        self.assertIn("cognitive_accounting", result)
        self.assertEqual(set(world.capture()), {"body", "inventory", "here", "neighbors"})


class SensorimotorTests(unittest.TestCase):
    def test_disabling_learned_updates_keeps_applied_movement(self):
        mind = Mind(midpoint(), 1)
        body = (80., 60., 60., 100., 100.)
        mind.last = (body, ("se_deplacer",), "se_deplacer", "E")
        with patch.object(mind, "learn_from_outcome", return_value=0) as update:
            mind.learn({"body": body, "moved": True, "dead": ()})
        update.assert_called_once()
        self.assertEqual(mind.pos, (1, 0))
        self.assertEqual(mind.effects.stats, {})
        self.assertEqual(list(mind.buffer), [])

    def test_failed_movement_does_not_move_internal_position(self):
        mind = Mind(midpoint(), 1)
        mind.last = ((80., 60., 60., 100., 100.), ("se_deplacer",), "se_deplacer", "W")
        mind.observe_outcome({"moved": False})
        self.assertEqual(mind.pos, (0, 0))

    def test_learning_only_does_not_repeat_sensorimotor_update(self):
        mind = Mind(midpoint(), 1)
        body = (80., 60., 60., 100., 100.)
        mind.last = (body, ("se_deplacer",), "se_deplacer", "E")
        result = {"body": (78., 59.8, 59.6, 100., 100.), "moved": True, "dead": ()}
        mind.observe_outcome(result)
        mind.learn_from_outcome(result)
        self.assertEqual(mind.pos, (1, 0))
        self.assertIn(("se_deplacer",), mind.effects.stats)


class ProvenanceTests(unittest.TestCase):
    def test_same_inputs_and_protocol_are_reproducible(self):
        args = (midpoint(), dev_open_field(), 2, 20, "unit-only")
        a, b = build_manifest(*args), build_manifest(*args)
        self.assertEqual(digest(a), digest(b))
        self.assertEqual(a["world_sha256"], digest(a["world"]))
        self.assertNotIn("mean_step_ms", a)

    def test_same_name_different_hidden_world_has_different_identity(self):
        first = dev_open_field()
        second = copy.deepcopy(first)
        second.changes = ((999, "water_stock", next(iter(second.water)), 0),)
        a = run_life(midpoint(), first, 1, 1)
        b = run_life(midpoint(), second, 1, 1)
        self.assertEqual(a["trace_head"], b["trace_head"])
        self.assertNotEqual(a["manifest_id"], b["manifest_id"])
        self.assertNotEqual(a["evidence_head"], b["evidence_head"])

    def test_world_snapshot_covers_laws_effects_stocks_and_body(self):
        base = dev_open_field()
        variants = [replace(base, laws=replace(base.laws, water_decay=0.5)),
                    replace(base, body=(79., *base.body[1:])),
                    replace(base, spawn=(0, 0))]
        stock = copy.deepcopy(base)
        next(iter(stock.water.values())).gain += 1.
        variants.append(stock)
        effect = copy.deepcopy(base)
        token = next(iter(effect.token_effects))
        effect.token_effects[token] = (99., -1.)
        variants.append(effect)
        original = digest(world_snapshot(base))
        for spec in variants:
            self.assertNotEqual(original, digest(world_snapshot(spec)))

    def test_world_snapshot_is_detached_and_mapping_order_independent(self):
        base = dev_open_field()
        other = copy.deepcopy(base)
        other.water = dict(reversed(list(other.water.items())))
        other.food = dict(reversed(list(other.food.items())))
        other.token_effects = dict(reversed(list(other.token_effects.items())))
        snapshot = world_snapshot(base)
        self.assertEqual(snapshot, world_snapshot(other))
        next(iter(base.water.values())).gain += 1.
        self.assertNotEqual(snapshot, world_snapshot(base))

    def test_source_hashes_match_real_bytes(self):
        snapshot = source_snapshot()
        root = Path(__file__).resolve().parents[2] / "src/i3"
        self.assertIn("modules/mind.py", snapshot["files"])
        for name, value in snapshot["files"].items():
            self.assertEqual(value, sha256((root / name).read_bytes()).hexdigest())
        self.assertEqual(snapshot["sha256"], digest(snapshot["files"]))

    def test_manifest_is_available_without_git(self):
        with patch("i3.runtime.provenance.subprocess.run", side_effect=FileNotFoundError):
            snapshot = source_snapshot()
        self.assertIsNone(snapshot["git_head"])
        self.assertIsNone(snapshot["working_tree_dirty"])
        self.assertTrue(snapshot["files"])

    def test_protocol_and_seed_validation(self):
        for value in (None, "", 2):
            with self.subTest(protocol=value), self.assertRaises(ValueError):
                run_life(midpoint(), dev_open_field(), 1, 1, protocol=value)
        with self.assertRaises(ValueError):
            run_life(midpoint(), dev_open_field(), True, 1)

    def test_evidence_chain_includes_work_accounting_and_final_pending_bill(self):
        result = run_life(generation_zero(2), dev_open_field(), 4, 100, keep_trace=True)
        head = digest(result["manifest"])
        for row in result["trace"]:
            record = {k: v for k, v in row.items()
                      if k not in ("info", "cognitive_work", "cognitive_accounting")}
            head = digest({"previous": head, "record": record,
                           "work": row["cognitive_work"], "accounting": row["cognitive_accounting"]})
        head = digest({"previous": head, "terminal": result["terminal"],
                       "accounting": result["cognitive_accounting"]})
        self.assertEqual(head, result["evidence_head"])
        self.assertEqual(result["cognitive_accounting"]["status"], "PENDING_REPLAY")
        self.assertGreater(result["cognitive_accounting"]["pending_energy"], 0.)

    def test_observer_trace_and_protocol_do_not_change_decisions(self):
        a = run_life(midpoint(), dev_open_field(), 1, 20, keep_trace=True, protocol="unit-A")
        b = run_life(midpoint(), dev_open_field(), 1, 20, protocol="unit-B")
        self.assertEqual(a["trace_head"], b["trace_head"])
        self.assertNotEqual(a["manifest_id"], b["manifest_id"])
        c = run_life(midpoint(), dev_open_field(), 1, 20, protocol="unit-A")
        self.assertEqual(a["evidence_head"], c["evidence_head"])


class BaselineParityTests(unittest.TestCase):
    def test_original_development_trajectories_are_unchanged(self):
        # Generated from ac71bef2 source BEFORE this refactor. No held-out seeds.
        cases = [(dev_open_field, 2, "b9d9812f3091d5b0a8d7d0a0e7e449d9b78743220e71d63460f0c349b4afe981"),
                 (dev_open_field, 9, "edb6a9007a302fbf27e83750b9069b5da11b9edca5137d87780526fa44526ad5"),
                 (dev_long_corridor, 2, "3e8631fc3e62a34ea4881d572a5e4a53e26cd88657b8997989ae49896fb35894"),
                 (dev_long_corridor, 9, "8440caa65a1f19a1dfef6de7b8a99776231da7c0009e336ca931fb141fd2d2b3")]
        for factory, seed, expected in cases:
            with self.subTest(world=factory.__name__, seed=seed):
                result = run_life(generation_zero(seed), factory(), 4, 100)
                self.assertEqual(result["trace_head"], expected)


if __name__ == "__main__":
    unittest.main()
