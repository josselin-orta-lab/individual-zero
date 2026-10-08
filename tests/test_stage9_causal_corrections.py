"""Stage-9 §12.3 / INV-25 correction-layer contract.

A fake *read-only* canonical view supplies pre-established rules. These tests
do not pretend the unfinished intervention producer can establish new rules.
"""
import unittest

from i0.interfaces import PrimitiveCommand
from i0.equipment import train_exact_transition_table
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
