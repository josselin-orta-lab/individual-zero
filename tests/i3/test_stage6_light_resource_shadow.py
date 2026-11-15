"""Source-only deterministic resource shadow and native trace parity tests.

All inputs are fabricated. The only native reference executed in this test is
pure BodyLaws/transition; World, Mind, birth and run_life are never imported.
"""
from __future__ import annotations

import ast
from collections import Counter
from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
import inspect
import json
from pathlib import Path
import runpy
import unittest

from i3.lab import stage6_light_resource_shadow as shadow


def small_snapshot():
    return {"name": "invented-enclosure", "width": 4, "height": 3,
            "spawn": [0, 0], "body": [60, 60, 5, 60, 60],
            "laws": {},
            "water": [[[0, 0], {"gain": 5.0, "stock": 2,
                                  "max_stock": 2, "restock_every": 3}]],
            "food": [[[1, 0], {"token": "berry", "quantity": 2,
                                "max_quantity": 2, "restock_every": 3}]],
            "token_effects": [["berry", [12.0, 1.0]]],
            "changes": [[2, "water_stock", [0, 0], 0],
                        [3, "water_stock", [0, 0], 2],
                        [4, "token_effect", "berry", [3.0, -2.0]]]}


class SourceOnlyResourceShadowTests(unittest.TestCase):
    def test_restock_then_pulse_change_order(self):
        world = shadow.initialize(small_snapshot())
        self.assertEqual(shadow.declared_step(world, "boire", None, 1)["water_gain"], 5.0)
        self.assertEqual(world["water"][(0, 0)]["stock"], 1)
        shadow.declared_step(world, None, None, 2)
        self.assertEqual(world["water"][(0, 0)]["stock"], 0)
        shadow.declared_step(world, None, None, 3)
        self.assertEqual(world["water"][(0, 0)]["stock"], 2)
        self.assertEqual(shadow.declared_step(world, "boire", None, 4)["water_gain"], 5.0)
        self.assertEqual(world["water"][(0, 0)]["stock"], 1)

    def test_food_collection_inventory_and_later_effect(self):
        world = shadow.initialize(small_snapshot())
        self.assertEqual(shadow.declared_step(world, "se_deplacer", "E", 1)["pos"], [1, 0])
        shadow.declared_step(world, "collecter", "berry", 2)
        self.assertEqual(world["inventory"], {"berry": 1})
        eaten = shadow.declared_step(world, "manger", "berry", 3)
        self.assertEqual((eaten["food_gain"], eaten["integrity_delta"]), (12.0, 1.0))
        self.assertEqual(world["inventory"]["berry"], 0)
        shadow.declared_step(world, None, None, 4)
        self.assertEqual(world["effects"]["berry"], (3.0, -2.0))

    def test_changed_gain_applies_next_step_not_previous(self):
        fixture = small_snapshot()
        fixture["changes"] = [[1, "water_gain", [0, 0], 2.0]]
        world = shadow.initialize(fixture)
        self.assertEqual(shadow.declared_step(world, "boire", None, 1)["water_gain"], 5.0)
        self.assertEqual(shadow.declared_step(world, "boire", None, 2)["water_gain"], 2.0)

    def test_invalid_command_rolls_back_inventory_and_tick(self):
        world = shadow.initialize(small_snapshot())
        old = deepcopy(world)
        for action, param in (("manger", "berry"), ("collecter", "berry"),
                              ("se_deplacer", "W"), ("boire", "unwanted")):
            with self.subTest(action=action), self.assertRaises(ValueError):
                shadow.declared_step(world, action, param, 1)
            self.assertEqual(world, old)
        shadow.declared_step(world, "boire", None, 1)
        with self.assertRaises(ValueError):
            shadow.declared_step(world, "boire", None, 3)

    def test_no_water_stock_is_no_free_drink(self):
        fixture = small_snapshot()
        fixture["water"][0][1]["stock"] = 0
        world = shadow.initialize(fixture)
        with self.assertRaises(ValueError):
            shadow.declared_step(world, "boire", None, 1)
        self.assertEqual(world["t"], 0)

    def test_bad_snapshots_and_foreign_events_are_rejected(self):
        original = small_snapshot()
        cases = [
            lambda v: v["water"].append(deepcopy(v["water"][0])),
            lambda v: v["water"][0][1].update({"stock": True}),
            lambda v: v["food"][0][1].update({"token": ""}),
            lambda v: v["changes"].append([10, "water_stock", [3, 2], 2]),
            lambda v: v["changes"].append([10, "oracle", "berry", 4]),
            lambda v: v["token_effects"].append(deepcopy(v["token_effects"][0])),
            lambda v: v["water"][0][1].update({"gain": float("nan")}),
            lambda v: v["water"][0][1].update({"restock_every": 1, "max_stock": None}),
        ]
        for modify in cases:
            fixture = deepcopy(original)
            modify(fixture)
            with self.subTest(modify=modify), self.assertRaises(ValueError):
                shadow.initialize(fixture)

    def test_never_executes_native_world_or_life(self):
        source = inspect.getsource(shadow)
        imported = []
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        self.assertFalse(any(n.startswith(("i3.modules", "i3.runtime")) for n in imported))
        for func in (shadow.open_world, shadow.run_life, shadow.authorize_science):
            with self.assertRaises(PermissionError):
                func()


def synthetic_resource_original():
    """Invented fatal trace with water/food/collection, not an I3 run."""
    from i3.lab import stage6_light_trace_funding_preflight as auditor
    from i3.modules.body import BodyLaws, CognitiveWork, transition
    helpers = runpy.run_path(str(Path(__file__).with_name(
        "test_stage6_light_native_custody_preflight.py")))
    pin, _ = helpers["_source"]()
    identity, life = helpers["native_case"](0, 0, "shared", 0, "stable", 0, pin)
    spec = small_snapshot()
    spec["laws"] = asdict(BodyLaws())
    # Do not invent a scientific origin or use any World instance.
    spec["changes"] = []
    spec["water"][0][1]["restock_every"] = 0
    spec["food"][0][1]["restock_every"] = 0
    life["manifest"]["world"] = spec
    identity["world_sha256"] = auditor.custody._digest(spec)
    life["manifest"]["world_sha256"] = identity["world_sha256"]
    life["world"] = spec["name"]
    life["manifest_id"] = auditor.custody._digest(life["manifest"])
    before = list(spec["body"])
    laws = BodyLaws()
    work = {"cycles": 1, "simulated_steps": 0, "memory_items": 0, "replays": 0}
    empty = {k: 0 for k in work}
    one_bill = {c: {"requested": amt, "paid": amt, "unpaid": 0.0}
                for c, amt in (("energy", 0.02), ("vigilance", 0.05))}
    zero_bill = {c: {"requested": 0.0, "paid": 0.0, "unpaid": 0.0}
                 for c in ("energy", "vigilance")}
    evidence_head = life["manifest_id"]
    trace_head = sha256(json.dumps([life["genome"], life["world"], life["life_seed"],
                                    life["horizon"]], separators=(",", ":")).encode()).hexdigest()
    trace = []
    action_counts = Counter()
    pos = [0, 0]
    first_drink = None
    for tick in range(1, 200):
        action, param = {1: ("boire", None), 2: ("se_deplacer", "E"),
                         3: ("collecter", "berry"), 4: ("manger", "berry")}.get(tick, (None, None))
        if tick == 2:
            pos = [1, 0]
        kw = {"water_gain": 5.0} if tick == 1 else {
            "food_gain": 12.0, "integrity_delta": 1.0} if tick == 4 else {}
        after, dead = transition(before, action, laws, CognitiveWork(cycles=1), **kw)
        funded = before[:]
        funded[0] -= 0.02
        funded[4] -= 0.05
        phys = list(after)
        phases = {
            "decision": {"work": deepcopy(work), "accounting": deepcopy(one_bill),
                         "body_before": before[:], "body_after_debit": funded},
            "learning": {"work": deepcopy(empty), "accounting": deepcopy(zero_bill),
                         "body_before": phys[:], "body_after_debit": phys[:]},
        }
        base = {"t": tick, "action": action, "param": param, "option": None,
                "body": phys[:], "pos": pos[:], "dead": list(dead)}
        trace_head = sha256((trace_head + json.dumps(base, separators=(",", ":"),
                                                    sort_keys=True)).encode()).hexdigest()
        evidence_head = auditor.custody._digest({"previous": evidence_head,
            "record": base, "work": work, "accounting": one_bill,
            "funding_phases": phases})
        trace.append({**base, "cognitive_work": deepcopy(work),
                      "cognitive_accounting": deepcopy(one_bill),
                      "funding_phases": phases, "info": {"toy": True}})
        action_counts[action if action is not None else "physical_inactivity"] += 1
        if action == "boire":
            first_drink = tick
        before = phys[:]
        if dead:
            break
    n = len(trace)
    assert n < 400 and trace[-1]["dead"]
    life.update({"trace": trace, "steps_lived": n,
                 "terminal": "dead", "death_causes": list(dead),
                 "trace_head": trace_head, "actions": dict(sorted(action_counts.items())),
                 "drinks": 1, "meals": 1, "first_drink_step": first_drink,
                 "final_body": [round(x, 6) for x in before]})
    life["cognitive_accounting"] = {"schema": "i3-cognitive-funding/v2",
        "status": "SETTLED_FOR_DECLARED_WORK", "totals": {
            c: {"requested": amount * n, "paid": amount * n, "unpaid": 0.0}
            for c, amount in (("energy", 0.02), ("vigilance", 0.05))},
        "shortfall_steps": 0, "pending_replays": 0,
        "pending_energy": 0.0, "pending_vigilance": 0.0,
        "learning_updates": 0, "replays_executed": 0,
        "inactive_steps": action_counts["physical_inactivity"]}
    life["evidence_head"] = auditor.custody._digest({
        "previous": evidence_head, "terminal": "dead",
        "accounting": life["cognitive_accounting"]})
    return identity, life, pin


def reseal_fake(identity, life):
    """Attacker can recompute ALL self-declared hashes after editing resources."""
    from i3.lab import stage6_light_trace_funding_preflight as auditor
    world = life["manifest"]["world"]
    identity["world_sha256"] = auditor.custody._digest(world)
    life["manifest"]["world_sha256"] = identity["world_sha256"]
    life["manifest_id"] = auditor.custody._digest(life["manifest"])
    head = life["manifest_id"]
    for row in life["trace"]:
        base = {k: row[k] for k in auditor.BASE_FIELDS}
        head = auditor.custody._digest({"previous": head, "record": base,
             "work": row["cognitive_work"],
             "accounting": row["cognitive_accounting"],
             "funding_phases": row["funding_phases"]})
    life["evidence_head"] = auditor.custody._digest({
        "previous": head, "terminal": life["terminal"],
        "accounting": life["cognitive_accounting"]})


class NativeTraceResourceIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example = synthetic_resource_original()

    def audit(self, fixture=None):
        from i3.lab import stage6_light_trace_funding_preflight as auditor
        identity, life, pin = deepcopy(self.example if fixture is None else fixture)
        return auditor.inspect_traced_life(identity, life,
                expected_protocol="FAKE_NATIVE_SHAPE_NOT_APPROVED",
                source_pin=pin, source_head="c" * 40)

    def test_valid_invented_resource_actions_do_not_imply_native_birth(self):
        result = self.audit()
        self.assertEqual(result["resource_steps_not_physically_replayed"], 0)
        self.assertEqual(result["declared_resource_actions_replayed"], 2)
        self.assertTrue(result["declared_action_world_dynamics_recomputed"])
        self.assertFalse(result["motor_decision_causality_or_world_physics_replayed"])
        self.assertEqual(result["new_lives_created"], 0)
        self.assertFalse(result["independent_original_source_and_time_attested"])

    def test_false_water_gain_resealed_after_outcome_is_rejected(self):
        fixture = deepcopy(self.example)
        fixture[1]["manifest"]["world"]["water"][0][1]["gain"] = 0.0
        reseal_fake(fixture[0], fixture[1])
        with self.assertRaises(ValueError):
            self.audit(fixture)

    def test_zero_stock_resealed_after_outcome_is_rejected(self):
        fixture = deepcopy(self.example)
        fixture[1]["manifest"]["world"]["water"][0][1]["stock"] = 0
        reseal_fake(fixture[0], fixture[1])
        with self.assertRaises(ValueError):
            self.audit(fixture)

    def test_false_food_effect_resealed_after_outcome_is_rejected(self):
        fixture = deepcopy(self.example)
        fixture[1]["manifest"]["world"]["token_effects"][0][1][0] = 0.0
        reseal_fake(fixture[0], fixture[1])
        with self.assertRaises(ValueError):
            self.audit(fixture)

    def test_missing_food_patch_resealed_after_outcome_is_rejected(self):
        fixture = deepcopy(self.example)
        fixture[1]["manifest"]["world"]["food"] = []
        reseal_fake(fixture[0], fixture[1])
        with self.assertRaises(ValueError):
            self.audit(fixture)


if __name__ == "__main__":
    unittest.main()
