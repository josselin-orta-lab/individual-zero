from __future__ import annotations

import unittest

from i0.interfaces import PrimitiveCommand
from i0.modules import (
    ActionControl,
    ActionControlConfig,
    Admissibility,
    PerceivedCell,
    PerceptualCapture,
    PreparedCommand,
    StaticSafetyFacts,
)


def capture_with_creature(*, creature_direction: str | None = "east") -> PerceptualCapture:
    cells = []
    coordinates = {
        "north": (2, 1),
        "south": (2, 3),
        "east": (3, 2),
        "west": (1, 2),
    }
    for direction in ("north", "south", "east", "west"):
        x, y = coordinates[direction]
        cells.append(
            PerceivedCell(
                direction=direction,
                x=x,
                y=y,
                passable=True,
                water_source=False,
                resources=(),
                creature=direction == creature_direction,
            )
        )
    return PerceptualCapture(
        t_monde=1,
        x=2,
        y=2,
        body={
            "energy": 50.0,
            "food": 60.0,
            "water": 60.0,
            "integrity": 100.0,
        },
        current_water_source=False,
        current_resources=(),
        adjacent=tuple(cells),
    )


def control(
    *,
    facts: StaticSafetyFacts | None = None,
    masked=None,
) -> ActionControl:
    return ActionControl(
        config=ActionControlConfig(
            safety_policy_version="mvp-v1.2.1",
            protected_integrity_threshold=20.0,
        ),
        safety_facts=facts or StaticSafetyFacts(),
        protocol_mask=masked or (lambda command: False),
    )


class ReflexTests(unittest.TestCase):
    def test_adjacent_creature_triggers_move_away(self) -> None:
        proposal = control().reflex(capture_with_creature(creature_direction="east"))

        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.prepared.source, "reflex")
        self.assertEqual(proposal.prepared.command.primitive, "se_deplacer")
        self.assertEqual(
            proposal.prepared.command.parameters["direction"],
            "west",
        )
        self.assertEqual(proposal.stimulus["kind"], "adjacent_creature")

    def test_no_adjacent_creature_means_no_reflex(self) -> None:
        proposal = control().reflex(capture_with_creature(creature_direction=None))

        self.assertIsNone(proposal)

    def test_reflex_tie_break_is_canonical(self) -> None:
        capture = capture_with_creature(creature_direction="east")
        # north and south are equally farther than staying near east;
        # west is farthest, so make west unavailable to expose tie-break.
        cells = tuple(
            PerceivedCell(
                direction=cell.direction,
                x=cell.x,
                y=cell.y,
                passable=False if cell.direction == "west" else cell.passable,
                water_source=cell.water_source,
                resources=cell.resources,
                creature=cell.creature,
            )
            for cell in capture.adjacent
        )
        tied = PerceptualCapture(
            t_monde=capture.t_monde,
            x=capture.x,
            y=capture.y,
            body=capture.body,
            current_water_source=False,
            current_resources=(),
            adjacent=cells,
        )

        proposal = control().reflex(tied)

        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.prepared.command.parameters["direction"], "north")


class VetoAndAdmissibilityTests(unittest.TestCase):
    def test_known_lethal_zone_is_vetoed_before_protocol_mask(self) -> None:
        facts = StaticSafetyFacts(
            known_lethal_positions=frozenset({(3, 2)}),
        )
        instance = control(facts=facts, masked=lambda command: True)
        prepared = PreparedCommand(
            command=PrimitiveCommand(
                "se_deplacer",
                {"direction": "east"},
            ),
            source="decision",
        )

        result = instance.admit(
            capture=capture_with_creature(creature_direction=None),
            prepared=prepared,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.rule_id, "lethal_zone_movement")
        self.assertEqual(result.rule_type, "semantic_prohibition")
        self.assertEqual(result.policy_version, "mvp-v1.2.1")

    def test_known_toxic_item_is_vetoed(self) -> None:
        facts = StaticSafetyFacts(
            known_toxic_resources=frozenset({"berry_b"}),
        )
        prepared = PreparedCommand(
            command=PrimitiveCommand("manger", {"target": "berry_b"}),
            source="decision",
        )

        result = control(facts=facts).admit(
            capture=capture_with_creature(creature_direction=None),
            prepared=prepared,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.rule_id, "toxic_item_consumption")

    def test_established_integrity_violation_is_vetoed(self) -> None:
        prepared = PreparedCommand(
            command=PrimitiveCommand("attendre"),
            source="decision",
            established_integrity_after=10.0,
        )

        result = control().admit(
            capture=capture_with_creature(creature_direction=None),
            prepared=prepared,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.rule_id, "protected_invariant_violation")

    def test_unknown_zone_is_indeterminate_but_not_vetoed(self) -> None:
        prepared = PreparedCommand(
            command=PrimitiveCommand(
                "se_deplacer",
                {"direction": "east"},
            ),
            source="decision",
        )
        instance = control()

        status = instance.verifier_admissibilite(
            capture=capture_with_creature(creature_direction=None),
            prepared=prepared,
        )
        admission = instance.admit(
            capture=capture_with_creature(creature_direction=None),
            prepared=prepared,
        )

        self.assertEqual(status, Admissibility.INDETERMINATE)
        self.assertTrue(admission.ok)

    def test_protocol_mask_blocks_after_semantic_veto_checks(self) -> None:
        prepared = PreparedCommand(
            command=PrimitiveCommand("attendre"),
            source="decision",
        )
        instance = control(masked=lambda command: True)

        result = instance.admit(
            capture=capture_with_creature(creature_direction=None),
            prepared=prepared,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.rule_id, "rollback_sequence_mask")
        self.assertEqual(result.rule_type, "protocol")

    def test_dispatch_never_sends_vetoed_command(self) -> None:
        facts = StaticSafetyFacts(
            known_toxic_resources=frozenset({"berry_b"}),
        )
        prepared = PreparedCommand(
            command=PrimitiveCommand("manger", {"target": "berry_b"}),
            source="decision",
        )
        sends = []

        admission, result = control(facts=facts).dispatch_if_admitted(
            capture=capture_with_creature(creature_direction=None),
            prepared=prepared,
            sender=lambda command: sends.append(command),
        )

        self.assertFalse(admission.ok)
        self.assertIsNone(result)
        self.assertEqual(sends, [])

    def test_dispatch_sends_admitted_command_exactly_once(self) -> None:
        prepared = PreparedCommand(
            command=PrimitiveCommand("attendre"),
            source="decision",
        )
        sends = []

        admission, result = control().dispatch_if_admitted(
            capture=capture_with_creature(creature_direction=None),
            prepared=prepared,
            sender=lambda command: sends.append(command) or "sent",
        )

        self.assertTrue(admission.ok)
        self.assertEqual(result, "sent")
        self.assertEqual(len(sends), 1)


if __name__ == "__main__":
    unittest.main()
