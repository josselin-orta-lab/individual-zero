"""Stage-9 §12.3 / INV-25 correction-layer contract.

A fake *read-only* canonical view supplies pre-established rules. These tests
do not pretend the unfinished intervention producer can establish new rules.
"""
import unittest
from dataclasses import replace

from lab.determinism import canonical_causal_bytes, sha256_hex
from i0.interfaces import PrimitiveCommand
from i0.equipment import EquipmentPrediction, train_exact_transition_table
from i0.modules.simulator import Simulator, SimulatorConfig
from i0.modules.causal_corrections import (
    NumericPredictionCorrection, CausalCorrectionConflict,
    correct_equipment_prediction,
)
from test_stage6_equipment import state, corpus


class PublishedEstablishedRules:
    def __init__(self, rules=()):
        self.rules = tuple(rules)

    def established_prediction_corrections(self):
        return self.rules


def correction(ref="established:1", *, observed=45.0, target=None):
    return NumericPredictionCorrection(
        contingency_ref=ref,
        intervention_ref="lived-intervention:" + ref,
        agency_evidence_ref="physical-comparison:" + ref,
        command_primitive="se_deplacer",
        command_target=target,
        variable="energy",
        observed_after=observed,
    )


def simulator(source=None):
    return Simulator(
        config=SimulatorConfig("stage9-corrections-test-v1", r_max=2, h_max=2),
        equipment=train_exact_transition_table(
            corpus=corpus(), equipment_version="E-v1-test",
        ),
        corrections=source,
    )


def run(source=None):
    return simulator(source).rollout(
        initial_state=state(x=2),
        commands=(PrimitiveCommand("se_deplacer", {"direction": "east"}),),
        r_eff=1, h_eff=1,
    )


class EstablishedCorrectionTests(unittest.TestCase):
    def test_no_correction_is_bitwise_equivalent_to_stage6(self):
        self.assertEqual(run(), run(PublishedEstablishedRules()))
        self.assertEqual(
            run().completed_rollouts[0].predictions[0].next_state.body["energy"],
            50.0,
        )

    def test_established_numeric_rule_only_changes_covered_variable(self):
        result = run(PublishedEstablishedRules((correction(),)))
        self.assertTrue(result.complete)
        prediction = result.completed_rollouts[0].predictions[0]
        self.assertEqual(prediction.next_state.body["energy"], 45.0)
        self.assertEqual(prediction.next_state.body["integrity"], 100.0)
        self.assertEqual(prediction.equipment_version, "E-v1-test")
        self.assertEqual(prediction.confidence, 1.0)
        self.assertEqual(run().completed_rollouts[0].predictions[0].next_state.body["energy"], 50.0)

    def test_unresolved_equal_specificity_is_unavailable(self):
        result = run(PublishedEstablishedRules((
            correction("a", observed=45), correction("b", observed=35),
        )))
        self.assertFalse(result.complete)
        self.assertEqual(result.reason, "unresolved_causal_correction_conflict")
        self.assertEqual(result.completed_rollouts, ())


    def test_exact_physical_context_outweighs_primitive_wide_rule(self):
        # Full accessible-state matching is narrower than matching only
        # body/position, which is narrower than no physical context.
        before = state(x=2)
        body_context = dict(
            observed_before_body=tuple(sorted(before.body.items())),
            observed_before_position=(before.x, before.y),
        )
        generic = correction("generic", observed=45.0)
        measured = replace(
            correction("measured", observed=35.0), **body_context,
        )
        exact = replace(
            correction("full-state", observed=25.0),
            **body_context,
            observed_before_state_digest=sha256_hex(
                canonical_causal_bytes(before.as_dict())
            ),
        )
        for rules, winner, value in (
            ((generic, measured), "measured", 35.0),
            ((generic, measured, exact), "full-state", 25.0),
            ((exact, measured, generic), "full-state", 25.0),
        ):
            with self.subTest(winner=winner, rules=tuple(r.contingency_ref for r in rules)):
                outcome = run(PublishedEstablishedRules(rules))
                self.assertTrue(outcome.complete)
                self.assertEqual(
                    outcome.completed_rollouts[0].predictions[0].next_state.body["energy"],
                    value,
                )
                self.assertEqual(outcome.corrected_contingency_refs, (winner,))

        # Exact-context observations never propagate into unobserved states.
        # Keep the frozen Equipment prediction object intact on fallback.
        command = PrimitiveCommand("se_deplacer", {"direction": "east"})
        frozen_prediction = train_exact_transition_table(
            corpus=corpus(), equipment_version="E-frozen-context-control",
        ).predict(state=before, command=command)
        changed = state(x=3)
        unchanged, refs = correct_equipment_prediction(
            source=PublishedEstablishedRules((measured, exact)),
            command=command, state=changed, prediction=frozen_prediction,
        )
        self.assertIs(unchanged, frozen_prediction)
        self.assertEqual(refs, ())

    def test_incomparable_target_and_state_evidence_does_not_choose_arbitrarily(self):
        before = state(x=2)
        command = PrimitiveCommand("manger", {"target": "berry_b"})
        base_prediction = EquipmentPrediction(
            equipment_version="E-frozen-test",
            state_schema_version=before.schema_version,
            horizon=1,
            command=command,
            next_state=before,
            effects=(),
            confidence=0.8,
        )
        context = dict(
            observed_before_body=tuple(sorted(before.body.items())),
            observed_before_position=(before.x, before.y),
        )
        target_only = replace(
            correction("target-only", observed=40.0, target="berry_b"),
            command_primitive="manger",
        )
        body_only = replace(
            correction("body-only", observed=35.0),
            command_primitive="manger",
            **context,
        )
        with self.assertRaises(CausalCorrectionConflict):
            correct_equipment_prediction(
                source=PublishedEstablishedRules((target_only, body_only)),
                command=command, state=before, prediction=base_prediction,
            )
        # A rule constrained by *both* dimensions really is more specific.
        both = replace(
            correction("target-and-body", observed=25.0, target="berry_b"),
            command_primitive="manger",
            **context,
        )
        corrected, refs = correct_equipment_prediction(
            source=PublishedEstablishedRules((body_only, target_only, both)),
            command=command, state=before, prediction=base_prediction,
        )
        self.assertEqual(refs, ("target-and-body",))
        self.assertEqual(corrected.next_state.body["energy"], 25.0)
        self.assertEqual(base_prediction.next_state.body["energy"], 50.0)

        # Incomparable matching facts that agree numerically do not create
        # a conflict. The credited source remains deterministic under reorder.
        agreeing = replace(body_only, observed_after=40.0)
        for rules in (
            (target_only, agreeing), (agreeing, target_only),
        ):
            same, credited = correct_equipment_prediction(
                source=PublishedEstablishedRules(rules),
                command=command, state=before, prediction=base_prediction,
            )
            self.assertEqual(same.next_state.body["energy"], 40.0)
            self.assertEqual(credited, ("body-only",))

    def test_unregistered_context_and_variable_are_not_silently_supported(self):
        with self.assertRaises(ValueError):
            NumericPredictionCorrection(
                contingency_ref="c", intervention_ref="i",
                agency_evidence_ref="a", command_primitive="attendre",
                command_target=None, variable="position_x", observed_after=1,
            ).validate()
        with self.assertRaises(ValueError):
            NumericPredictionCorrection(
                contingency_ref="c", intervention_ref="i",
                agency_evidence_ref="a", command_primitive="attendre",
                command_target=None, variable="energy", observed_after=1,
                application_context="non_global",
            ).validate()


if __name__ == "__main__":
    unittest.main()
