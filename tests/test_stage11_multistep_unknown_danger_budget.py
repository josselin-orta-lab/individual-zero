"""Public Stage 11 multi-step corridor and unknown-hazard boundary regression.

Software development fixture only; no held-out seed, oracle feedback or
scientific acceptance. See the prospective protocol in docs/research.
"""
from dataclasses import replace
from unittest import TestCase

from i0.modules.action_control import StaticSafetyFacts
from lab.stage11_degraded_budget_probe import _strict_stage11_config
from lab.stage11_geographic_probe import START_BODY, _positions
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage11_runtime import Stage11Runtime
from lab.world import Position


CORRIDOR = frozenset({(2, 2), (3, 2), (4, 2)})
WALLS = frozenset(
    Position(x, y) for x, y in (
        (2, 1), (2, 3), (1, 2), (3, 1),
        (3, 3), (4, 1), (4, 3), (5, 2),
    )
)
DANGER = Position(3, 2)


def _runtime(*, hidden_danger=False, no_planning_uc=False):
    reference = build_stage11_reference_runtime(enable_geography=True)
    config = (
        _strict_stage11_config(reference, variant="planning_0")
        if no_planning_uc else reference._stage11_config
    )
    layout = replace(
        reference.world._layout,
        obstacles=WALLS,
        water_sources=frozenset(),
        resources=(),
        creatures=frozenset(),
        danger_zones=frozenset({DANGER}) if hidden_danger else frozenset(),
        lethal_zones=frozenset(),
        oracle_canary="public-lab-only-not-an-individual-observation",
    )
    world = replace(
        reference.world.config,
        version=reference.world.config.version + "+public-corridor-v1",
        initial_body=START_BODY,
        initial_position=Position(2, 2),
        danger_zone_damage=5.0,
    )
    return Stage11Runtime(
        world_config=world, layout=layout,
        safety_config=reference.stage3.substrate.safety._config,
        safety_facts=StaticSafetyFacts(),
        protected_integrity_threshold=(
            reference.stage3.control._config.protected_integrity_threshold
        ),
        config=config,
        equipment=reference.equipment,
    )


def _run(*, hidden_danger=False, no_planning_uc=False):
    owner = _runtime(
        hidden_danger=hidden_danger, no_planning_uc=no_planning_uc,
    )
    # This must remain the canonical individual's initial knowledge, not
    # the Lab's ground-truth hazard list.
    initial_status = owner._canonical_safety.zone_status(x=3, y=2)
    outputs = tuple(owner.run_step() for _ in range(8))
    events = tuple(entry.causal_event for entry in owner.journal.entries)
    positions = _positions(owner)
    visits = {
        tuple(row[:2])
        for row in owner.exploration.geographic.export_causal_state()["visits"]
    }
    planning_charges = tuple(
        e["data"] for e in events
        if e.get("kind") == "compute_charge"
        and e.get("data", {}).get("module") == "planning"
    )
    return owner, {
        "initial_status": initial_status,
        "first_action": (
            outputs[0].execution_status,
            outputs[0].command_primitive,
            outputs[0].option_ref,
        ),
        "positions": positions,
        "visits": visits,
        "applied_geography": sum(
            o.execution_status == "applied"
            and o.option_ref is not None
            and o.option_ref.startswith("option:geographic:")
            for o in outputs
        ),
        "planning_charges": planning_charges,
        "final_integrity": owner.world.body.integrity,
        "journal": owner.journal.canonical_bytes(),
        "offered": owner.exploration.geographic.offered,
    }


class Stage11PublicLongitudinalBoundaryTests(TestCase):
    def test_hidden_danger_does_not_create_initial_safety_knowledge(self):
        clear, a = _run()
        exposed, b = _run(hidden_danger=True)
        self.assertEqual(a["initial_status"], "unknown")
        self.assertEqual(b["initial_status"], "unknown")
        self.assertEqual(a["first_action"], b["first_action"])
        for owner, row in ((clear, a), (exposed, b)):
            self.assertTrue(owner.journal.verify())
            self.assertEqual(set(row["positions"]), row["visits"])
            self.assertTrue(set(row["positions"]) <= CORRIDOR)
            self.assertEqual(row["positions"][0], (2, 2))
        # The hazard is real to the lab, but no automatic danger
        # recognition or successful long-horizon escape is asserted.
        # If both trajectories encounter it, the differential remains a
        # physical outcome and cannot be fed back as initial knowledge.
        if (3, 2) in b["positions"]:
            self.assertLessEqual(
                b["final_integrity"], a["final_integrity"],
            )

    def test_zero_planning_budget_fails_closed_across_eight_steps(self):
        owner, row = _run(hidden_danger=True, no_planning_uc=True)
        self.assertTrue(owner.journal.verify())
        self.assertEqual(row["initial_status"], "unknown")
        self.assertEqual(row["applied_geography"], 0)
        self.assertEqual(row["offered"], ())
        self.assertEqual(
            sum(
                entry["requested_uc"] for entry in row["planning_charges"]
                if entry["operation"] == "geographic_admissibility_preflight"
                and entry["accepted"] is True
            ), 0,
        )
        self.assertEqual(set(row["positions"]), row["visits"])
        self.assertTrue(set(row["positions"]) <= CORRIDOR)

    def test_public_conditions_reexecute_exactly(self):
        for flags in (
            {},
            {"hidden_danger": True},
            {"hidden_danger": True, "no_planning_uc": True},
        ):
            with self.subTest(**flags):
                first_owner, a = _run(**flags)
                second_owner, b = _run(**flags)
                self.assertTrue(first_owner.journal.verify())
                self.assertTrue(second_owner.journal.verify())
                self.assertEqual(a, b)
                self.assertEqual(
                    first_owner.exploration.export_causal_state(),
                    second_owner.exploration.export_causal_state(),
                )
