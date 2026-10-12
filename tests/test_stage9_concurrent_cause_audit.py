"""Stage-9 adversarial first-person DC-05 contrasts, genuine WorldBody physics.

These software checks never ask an Oracle which physical cause is real.
The independent verifier attests canonical journal consistency, *not* the
physical truth of a confounded episode. Stage 9 remains SCIENTIFIC NO-GO.
"""
from __future__ import annotations

from dataclasses import replace
import importlib.abc
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from i0.config import MVP_CYCLE_PHASE_COMPONENT_ORDER
from i0.modules import SymbolicPerception
from i0.modules.causal_model import CausalModel, CausalModelConfig
from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes
from lab.safety_protocol import SafetyProtocolConfig
from lab.stage2_runtime import ScriptedStage2Runtime
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import BerryEffect, Command, Position, WorldLayout


def _perceive(runtime, t_monde):
    # Perception's actual public input (not WorldBody.ground_truth).
    world = runtime.world
    return SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=t_monde).as_dict(),
        telemetry=world.telemetry(),
    )


def _lived_pair(runtime, t_monde):
    projected = runtime.autobiographical_view()
    pair = tuple(
        row for row in projected
        if row.get("t_monde") == t_monde
        and row.get("kind") in {
            "command_experienced", "world_transition_experienced",
        }
    )
    if len(pair) != 2:
        raise AssertionError(f"expected one genuine lived pair at {t_monde}")
    return pair


def _exercise_physics(kind):
    """Three real mortal steps; adversity is applied after a clean wait.

    The dynamic invisible hazard and actually toxic berry are different
    physical worlds producing indistinguishable first-person food outcomes.
    The visible creature is detectable through local Perception, but its
    *actual injury amount* stays technical/oracle-inaccessible.
    """
    if kind not in {"dynamic_hidden_zone", "toxic_berry", "visible_creature", "clean"}:
        raise ValueError(kind)
    baseline = build_stage4_reference_runtime(autonomous_mortal=True)
    effects = dict(baseline.world.config.berry_effects)
    if kind == "toxic_berry":
        effects["berry_a"] = BerryEffect(10.0, -10.0)
    physics = replace(
        baseline.world.config,
        version=f"stage9-concurrent-cause-{kind}-v1",
        night_start_step=0, creature_damage=10.0,
        berry_effects=effects,
    )
    substrate = ScriptedStage2Runtime(
        config=physics,
        layout=WorldLayout(water_sources=frozenset({Position(4, 2)})),
        phase_component_order=MVP_CYCLE_PHASE_COMPONENT_ORDER,
        safety_config=SafetyProtocolConfig(
            version="stage4-reference-safety-v1",
            lethal_max=2, mode="campaign",
        ),
        autonomous_mortal=True,
    )
    assert substrate.bench is None
    world = substrate.world
    here = world.position.as_dict()
    world.apply_scenario_event(
        "place_resource", {"position": here, "kind": "berry_a", "quantity": 1},
    )
    model = CausalModel(CausalModelConfig(f"stage9-perceived-{kind}-v1", 2, 2, 2, 2))

    substrate.open_step()
    collected = substrate.execute(Command("collecter", {"target": "berry_a"}))
    assert collected.status == "applied" and world.inventory()["berry_a"] == 1

    before_wait = _perceive(substrate, 2)
    model.record_applied_ambient_integrity_control(
        t_monde=2, option_ref="wait:2",
        position=(before_wait.x, before_wait.y),
        integrity_before=float(before_wait.body["integrity"]),
    )
    substrate.open_step()
    waited = substrate.execute(Command("attendre"))
    assert waited.status == "applied"
    after_wait = _perceive(substrate, 3)
    model.observe_followup_capture(
        t_monde=3, integrity=float(after_wait.body["integrity"]),
    )
    waited_events = _lived_pair(substrate, 2)
    assert model.ingest_closed_autobiographical_episode(
        episode_ref="episode:wait:2",
        event_refs=tuple(e["event_id"] for e in waited_events),
        autobiographical_events=waited_events,
    ) == ()

    # Make the competing physical injury arrive only at the meal step.
    # The clean prior wait remains a *real* control, but cannot attest what
    # happens next when the hazard itself changes with simulated time.
    if kind == "dynamic_hidden_zone":
        world.apply_scenario_event(
            "set_danger_zone", {"position": here, "active": True},
        )
    if kind == "visible_creature":
        world.apply_scenario_event(
            "place_creature", {"position": {"x": here["x"] + 1, "y": here["y"]}},
        )

    before_food = _perceive(substrate, 3)
    model.record_applied_food_exposure(
        t_monde=3, resource_kind="berry_a",
        option_ref="option:lived-food", motive_ref="goal:food",
        integrity_before=float(before_food.body["integrity"]),
        position_before=(before_food.x, before_food.y),
        body_before=dict(before_food.body),
        visible_creature_at_exposure=bool(before_food.adjacent_creatures),
    )
    substrate.open_step()
    eaten = substrate.execute(Command("manger", {"target": "berry_a"}))
    assert eaten.status == "applied"
    after_food = _perceive(substrate, 4)
    model.observe_followup_capture(
        t_monde=4, integrity=float(after_food.body["integrity"]),
    )
    food_events = _lived_pair(substrate, 3)
    admitted = model.ingest_closed_autobiographical_episode(
        episode_ref="episode:food:3",
        event_refs=tuple(e["event_id"] for e in food_events),
        autobiographical_events=food_events,
    )
    model.publish()
    raw = substrate.journal.canonical_bytes()
    assert substrate.journal.verify()
    # The external auditor can verify the complete technical archive; it
    # cannot infer an unobserved physical hazard from cryptographic hashes.
    audited = audit_export_bytes(
        raw, expected_head=substrate.journal.head_hash,
        expected_count=len(substrate.journal.entries),
    )
    assert audited.world_steps_closed == 3
    assert audited.terminal_deaths == 0
    assert audited.autobiographical_commits == 3
    assert audited.as_dict()["physical_truth_verified"] is False
    return {
        "kind": kind,
        "model": model,
        "before_food": before_food,
        "after_food": after_food,
        "before_wait": before_wait,
        "waited": waited_events,
        "lived": substrate.autobiographical_view(),
        "admitted": admitted,
        "journal": substrate.journal,
        "audit": audited,
        "raw": raw,
    }


class Stage9ConcurrentCauseRegressionTests(unittest.TestCase):
    def test_visible_creature_is_perceived_competing_cause_not_food_safety_evidence(self):
        for birth in (1, 2):
            with self.subTest(birth=birth):
                trial = _exercise_physics("visible_creature")
                self.assertTrue(trial["before_food"].adjacent_creatures)
                self.assertLess(trial["after_food"].body["integrity"], 100)
                self.assertEqual(trial["admitted"], ())
                self.assertEqual(trial["model"].pending_causal_observations(), ())
                self.assertEqual(
                    trial["model"].export_causal_state()["pending_numeric_witnesses"], [],
                )
                self.assertIsNone(trial["model"].get("toxic:berry_a"))
                self.assertTrue(any(
                    e.causal_event.get("kind") == "world_transition_experienced"
                    and e.causal_event.get("t_monde") == 3
                    and e.causal_event.get("effects", {}).get("creature_damage", 0) > 0
                    for e in trial["journal"].entries
                ))
                self.assertNotIn("creature_damage", repr(trial["lived"]))
                self.assertNotIn("danger_zone_damage", repr(trial["lived"]))
                self.assertNotIn("oracle_canary", repr(trial["lived"]))

    def test_hidden_dynamic_zone_and_toxic_berry_are_lived_indistinguishably(self):
        zone = _exercise_physics("dynamic_hidden_zone")
        poison = _exercise_physics("toxic_berry")
        self.assertFalse(zone["before_food"].adjacent_creatures)
        self.assertFalse(poison["before_food"].adjacent_creatures)
        self.assertEqual(
            canonical_causal_bytes(zone["lived"]),
            canonical_causal_bytes(poison["lived"]),
        )
        self.assertEqual(zone["before_food"].body, poison["before_food"].body)
        self.assertEqual(zone["after_food"].body, poison["after_food"].body)
        self.assertLess(zone["after_food"].body["integrity"], 100)
        self.assertNotEqual(zone["raw"], poison["raw"])
        self.assertNotIn("danger_zone_damage", repr(zone["lived"]))
        self.assertNotIn("creature_damage", repr(poison["lived"]))
        # A matched clean prior wait is still insufficient to distinguish a
        # hazard that appears only at the food step. This is an explicit
        # science limitation, not a claim of absence of confounders.
        self.assertEqual(len(zone["admitted"]), len(poison["admitted"]))
        self.assertNotEqual(zone["audit"].head_hash, poison["audit"].head_hash)
        self.assertEqual(zone["model"].get("toxic:berry_a").safety_status, "aucun")

    def test_standalone_operator_verifier_checks_both_contrast_histories(self):
        for kind in ("visible_creature", "dynamic_hidden_zone", "toxic_berry"):
            with self.subTest(kind=kind), TemporaryDirectory() as directory:
                trial = _exercise_physics(kind)
                path = Path(directory) / "life.jsonl"
                path.write_bytes(trial["raw"])
                # Execute in a new process with a guard against any import
                # of I0, Oracle or Bench by the read-only verification path.
                code = r"""
import importlib.abc, json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[2])
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name == "i0" or name.startswith("i0.") or name in ("lab.oracle", "lab.bench"):
            raise ImportError("forbidden scientific/cognitive import: " + name)
        return None
sys.meta_path.insert(0, Block())
from lab.independent_journal_audit import audit_export_file
result = audit_export_file(
    Path(sys.argv[1]), expected_head=sys.argv[3], expected_count=int(sys.argv[4]),
)
assert result.world_steps_closed == 3
assert result.autobiographical_commits == 3
assert result.terminal_deaths == 0
assert result.as_dict()["physical_truth_verified"] is False
assert "i0" not in sys.modules
assert "lab.oracle" not in sys.modules
assert "lab.bench" not in sys.modules
print(json.dumps(result.as_dict(), sort_keys=True))
"""
                cmd = [
                    sys.executable, "-c", code, str(path),
                    str(Path(__file__).resolve().parents[1] / "src"),
                    trial["journal"].head_hash,
                    str(len(trial["journal"].entries)),
                ]
                verified = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(verified.returncode, 0, verified.stderr)
                result = json.loads(verified.stdout)
                self.assertEqual(result["head_hash"], trial["journal"].head_hash)
                self.assertFalse(result["physical_truth_verified"])

    def test_visible_competitor_snapshot_is_versioned_and_rejects_forgery(self):
        import copy
        model = CausalModel(CausalModelConfig("stage9-perceived-snapshot-v1", 2, 2, 2, 2))
        model.record_applied_food_exposure(
            t_monde=2, resource_kind="berry_a",
            option_ref="option:2", motive_ref="goal:food",
            integrity_before=100.0,
            visible_creature_at_exposure=True,
        )
        state = model.export_causal_state()
        self.assertTrue(
            state["lived_food_exposures"][0]["visible_creature_at_exposure"]
        )
        reconstructed = CausalModel(model.config)
        reconstructed.restore_causal_state(state)
        self.assertEqual(reconstructed.export_causal_state(), state)
        forged = copy.deepcopy(state)
        forged["lived_food_exposures"][0]["visible_creature_at_exposure"] = 1
        with self.assertRaises(ValueError):
            reconstructed.restore_causal_state(forged)
        self.assertEqual(reconstructed.export_causal_state(), state)


if __name__ == "__main__":
    unittest.main()
