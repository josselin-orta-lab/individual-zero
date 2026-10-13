"""Stage-9 INV-25: established-only *canonical* numerical correction tests.

Controlled typed observations are deliberately not a claim that an autonomous
intervention policy is complete. Every candidate correction must join a closed
DC-09 world transition with a published agency report and independently
confirmed canonical interventions.
"""
from __future__ import annotations

import unittest
from dataclasses import replace

from i0.interfaces import PrimitiveCommand
from i0.equipment import (
    EquipmentCorpus, EquipmentCorpusExample, train_exact_transition_table,
)
from i0.modules.simulator import Simulator, SimulatorConfig
from i0.equipment import EquipmentPrediction, PredictedEffect
from i0.modules.causal_model import (
    CausalModel, CausalModelConfig, SafetyEvidence,
)
from i0.modules.causal_lifecycle import (
    CausalObservation, CausalHypothesisReview, CausalIntervention,
)
from i0.modules.causal_corrections import (
    LivedNumericOutcome, correct_equipment_prediction,
)
from lab.stage9_reference_fixture import build_stage9_reference_runtime
from test_stage6_equipment import state
from lab.determinism import canonical_causal_bytes, sha256_hex

REF = "toxic:berry_b"


def model():
    return CausalModel(CausalModelConfig(
        version="stage9-canonical-numeric-v1",
        n1=2, n2=2, n_sec=2, m_sec=2,
    ))


def physical_meal(m, *, step=2, option="option:meal"):
    """Unit-seed an already-authorized lived food witness.

    Issue #89 deliberately prevents the runtime ingestion path from creating
    this witness from an observationally ambiguous post-meal injury. These
    canonical-correction tests isolate the downstream INV-25 machinery, so the
    test seeds the typed witness and matching causal observation explicitly.
    Integration regressions separately prove that ambiguous meals cannot do so.
    """
    before = state(x=2)
    suffix = "" if step == 2 else f":{step}"
    episode_ref = "episode:meal" + suffix
    command_ref = "cmd:meal" + suffix
    transition_ref = "world:meal" + suffix
    witness = LivedNumericOutcome(
        identifier=f"numeric-witness:unit-authorized:{step}:{option}",
        contingency_ref=REF,
        episode_ref=episode_ref,
        command_event_ref=command_ref,
        transition_event_ref=transition_ref,
        option_ref=option,
        sent_t_monde=step,
        observed_t_monde=step + 1,
        command_primitive="manger",
        command_target="berry_b",
        variable="integrity",
        observed_before_body=tuple(
            (name, float(before.body[name])) for name in sorted(before.body)
        ),
        observed_before_position=(before.x, before.y),
        observed_before_state_digest=sha256_hex(
            canonical_causal_bytes(before.as_dict())
        ),
        observed_after=90.0,
    )
    witness.validate()
    m._pending_numeric_witnesses.append(witness)
    m.integrate_causal_observation(CausalObservation(
        identifier=f"causal-observation:{episode_ref}:{transition_ref}",
        contingency_ref=REF,
        predicate="toxic_item",
        subject_ref="berry_b",
        application_context="global",
        observation_context="food_consumption",
        episode_ref=episode_ref,
        observation_ref=transition_ref,
        observed_step=step + 1,
        cause_present=True,
        effect_present=True,
        controlled_variables=(("primitive", "manger"),),
    ))
    return before


def agency_report(m, name, *, step, option, observed, predicted, conforms):
    eid = "agency:" + name
    episode = "episode:agency:" + name
    status = "conforming" if conforms else "nonconforming"
    event = {
        "event_id": eid, "kind": "agency_comparison",
        "t_monde": step + 1,
        "data": {
            "option_ref": option, "sent_t_monde": step,
            "observed_t_monde": step + 1,
            "status": status,
            "attribution": "self_compatible" if conforms else "uncertain",
            "effects": [{
                "variable": "integrity", "status": status,
                "predicted": predicted, "observed": observed,
                "precision": 0.0, "comparator_version": "p47-test-v1",
            }],
        },
    }
    (report,) = m.ingest_closed_agency_comparisons(
        episode_ref=episode, event_refs=(eid,),
        autobiographical_events=(event,),
    )
    m.publish_causal_inference()
    return report


def hypothesis(m):
    m.integrate_causal_observation(CausalObservation(
        identifier="observation:second", contingency_ref=REF,
        predicate="toxic_item", subject_ref="berry_b",
        application_context="global",
        observation_context="food_consumption",
        episode_ref="episode:second",
        observation_ref="world:second", observed_step=4,
        cause_present=True, effect_present=True,
        controlled_variables=(("primitive", "manger"),),
    ))
    m.integrate_causal_observation(CausalObservation(
        identifier="observation:control", contingency_ref=REF,
        predicate="toxic_item", subject_ref="berry_b",
        application_context="global",
        observation_context="food_consumption",
        episode_ref="episode:control",
        observation_ref="world:control", observed_step=5,
        cause_present=False, effect_present=False,
        controlled_variables=(("primitive", "manger"),),
    ))
    assert [c.after for c in m.publish_causal_inference()] == [
        "correlation_observee"
    ]
    m.integrate_hypothesis_review(CausalHypothesisReview(
        identifier="review:food", contingency_ref=REF,
        alternatives=("different_food",),
        contrasting_pairs=((
            "causal-observation:episode:meal:world:meal",
            "observation:control",
        ),),
    ))
    assert [c.after for c in m.publish_causal_inference()] == [
        "hypothese_causale"
    ]


def intervention(m, name, *, step, context, linked=True):
    option = "option:" + name
    report = (
        agency_report(m, name, step=step, option=option,
                      observed=95.0, predicted=95.0, conforms=True)
        if linked else None
    )
    m.integrate_causal_intervention(CausalIntervention(
        identifier="intervention:" + name,
        contingency_ref=REF,
        episode_ref="episode:agency:" + name,
        observation_ref="observed-intervention:" + name,
        command_ref=option,
        comparator_ref=(
            report.identifier if report else "nonexistent-comparison:" + name
        ),
        context_signature=context,
        emitted_step=step, observed_step=step + 1,
        observed_effect=True, comparator_status="conforming",
        attribution="self_compatible",
        controlled_variables=(("primitive", "manger"),),
        action_applied=True,
    ))
    return m.publish_causal_inference()


class CanonicalCorrectionTests(unittest.TestCase):
    def test_snapshot_cannot_inject_or_retarget_numeric_food_witness(self):
        from copy import deepcopy
        m = model()
        physical_meal(m)
        m.publish_causal_inference()
        snapshot = m.export_causal_state()
        self.assertEqual(len(snapshot["numeric_witnesses"]), 1)
        forged = deepcopy(snapshot)
        forged["numeric_witnesses"][0]["transition_event_ref"] = "world:forged"
        clone = model()
        with self.assertRaisesRegex(
            ValueError, "numeric snapshot witness lacks matching lived causal observation",
        ):
            clone.restore_causal_state(forged)

    def test_all_three_provenance_layers_are_mandatory(self):
        m = model()
        physical_meal(m)
        self.assertEqual(len(m.export_causal_state()["pending_numeric_witnesses"]), 1)
        self.assertEqual(len(m.export_causal_state()["numeric_witnesses"]), 0)
        self.assertEqual(m.established_prediction_corrections(), ())
        m.publish_causal_inference()
        self.assertEqual(len(m.export_causal_state()["numeric_witnesses"]), 1)
        hypothesis(m)
        self.assertEqual(m.established_prediction_corrections(), ())
        with self.assertRaisesRegex(ValueError, "published DC-09 agency comparison"):
            intervention(m, "first", step=5, context="zone1", linked=False)
        # An unlinked declaration cannot even change the canonical status;
        # the simulator's existing correction gate is no substitute.
        self.assertEqual(m.get(REF).causal_status, "hypothese_causale")
        self.assertEqual(m.export_causal_state()["causal_interventions"], [])
        self.assertEqual(m.established_prediction_corrections(), ())

    def test_published_physical_witness_corrects_only_its_exact_context(self):
        m = model()
        before = physical_meal(m)
        m.publish_causal_inference()
        self.assertEqual(m.established_prediction_corrections(), ())
        hypothesis(m)
        agency_report(m, "meal", step=2, option="option:meal",
                      observed=90.0, predicted=100.0, conforms=False)
        self.assertEqual(
            [x.after for x in intervention(m, "first", step=5,
                                            context="zone1")],
            ["testee_par_intervention"],
        )
        self.assertEqual(m.established_prediction_corrections(), ())
        self.assertEqual(
            [x.after for x in intervention(m, "second", step=7,
                                            context="zone2")],
            ["etablie"],
        )
        (rule,) = m.established_prediction_corrections()
        self.assertEqual(rule.contingency_ref, REF)
        self.assertEqual(rule.observed_after, 90.0)
        self.assertIsNotNone(rule.observed_before_body)
        self.assertEqual(rule.observed_before_position, (2, 2))
        command = PrimitiveCommand("manger", {"target": "berry_b"})
        prediction = EquipmentPrediction(
            equipment_version="E-reference-immutable",
            state_schema_version=before.schema_version,
            horizon=1, command=command, next_state=before,
            effects=(PredictedEffect("integrity", 100.0, 100.0, 0.8),),
            confidence=0.8,
        )
        corrected, sources = correct_equipment_prediction(
            source=m, command=command, state=before, prediction=prediction,
        )
        self.assertEqual(sources, (REF,))
        self.assertEqual(corrected.next_state.body["integrity"], 90.0)
        self.assertEqual(corrected.equipment_version, prediction.equipment_version)
        self.assertEqual(corrected.confidence, 0.8)
        self.assertEqual(prediction.next_state.body["integrity"], 100.0)

        # The same canonical owner is really consumed by Simulator, not only
        # by the isolated correction function. The frozen equipment remains
        # identical, and its prediction returns after causal refutation.
        equipment = train_exact_transition_table(
            corpus=EquipmentCorpus(
                version="stage9-canonical-food-corpus-v1",
                examples=(EquipmentCorpusExample(
                    family="lived_food_controlled",
                    state=before,
                    command=command,
                    observed_next_state=before,
                    terminal=False,
                ),),
            ),
            equipment_version="E-stage9-immutable-test",
        )
        simulator = Simulator(
            config=SimulatorConfig(
                version="stage9-canonical-simulator-v1", r_max=1, h_max=1,
            ),
            equipment=equipment,
            corrections=m,
        )
        control = Simulator(
            config=SimulatorConfig(
                version="stage9-base-simulator-v1", r_max=1, h_max=1,
            ),
            equipment=equipment,
        )

        def predicted_integrity(sim):
            result = sim.rollout(
                initial_state=before, commands=(command,), r_eff=1, h_eff=1,
            )
            self.assertTrue(result.complete)
            return result.completed_rollouts[0].predictions[0].next_state.body["integrity"]

        self.assertEqual(predicted_integrity(control), 100.0)
        self.assertEqual(predicted_integrity(simulator), 90.0)
        self.assertEqual(predicted_integrity(control), 100.0)
        annotated = simulator.rollout(
            initial_state=before, commands=(command,), r_eff=1, h_eff=1,
        )
        self.assertEqual(annotated.corrected_contingency_refs, (REF,))
        self.assertEqual(
            control.rollout(
                initial_state=before, commands=(command,), r_eff=1, h_eff=1,
            ).corrected_contingency_refs,
            (),
        )
        changed_context = replace(before, x=5)
        fallback, refs = correct_equipment_prediction(
            source=m, command=command, state=changed_context,
            prediction=prediction,
        )
        self.assertIs(fallback, prediction)
        self.assertEqual(refs, ())
        # Matching position/body alone cannot authorize a correction when
        # inventory or other accessible environmental state differs.
        changed_inventory = replace(
            before, inventory={**before.inventory, "berry_b": 1},
        )
        fallback, refs = correct_equipment_prediction(
            source=m, command=command, state=changed_inventory,
            prediction=prediction,
        )
        self.assertIs(fallback, prediction)
        self.assertEqual(refs, ())

        checkpoint = m.export_causal_state()
        twin = model()
        twin.restore_causal_state(checkpoint)
        self.assertEqual(twin.export_causal_state(), checkpoint)
        self.assertEqual(
            twin.established_prediction_corrections(),
            m.established_prediction_corrections(),
        )

        # A later conflicting lived intervention can revoke establishment;
        # the Simulator's read-only correction disappears immediately.
        failed_report = agency_report(
            m, "failed", step=9, option="option:failed",
            observed=85.0, predicted=95.0, conforms=False,
        )
        m.integrate_causal_intervention(CausalIntervention(
            identifier="intervention:failed", contingency_ref=REF,
            episode_ref=failed_report.episode_ref,
            observation_ref="world:failed", command_ref="option:failed",
            comparator_ref=failed_report.identifier,
            context_signature="zone3",
            emitted_step=9, observed_step=10, observed_effect=False,
            comparator_status="nonconforming", attribution="uncertain",
            controlled_variables=(("primitive", "manger"),),
            action_applied=True,
        ))
        self.assertEqual(m.established_prediction_corrections(), (rule,))
        m.publish_causal_inference()
        self.assertEqual(m.get(REF).causal_status, "hypothese_causale")
        self.assertEqual(m.established_prediction_corrections(), ())
        self.assertEqual(predicted_integrity(simulator), 100.0)
        self.assertEqual(
            simulator.rollout(
                initial_state=before, commands=(command,), r_eff=1, h_eff=1,
            ).corrected_contingency_refs,
            (),
        )

    def test_reestablished_correction_cannot_cite_stale_intervention(self):
        m = model()
        physical_meal(m)
        m.publish_causal_inference()
        hypothesis(m)
        agency_report(
            m, "meal", step=2, option="option:meal",
            observed=90.0, predicted=100.0, conforms=False,
        )
        intervention(m, "first", step=5, context="zone1")
        intervention(m, "second", step=7, context="zone2")
        self.assertEqual(m.get(REF).causal_status, "etablie")
        (original,) = m.established_prediction_corrections()
        self.assertEqual(original.intervention_ref, "intervention:first")

        # A later physically supported counterexample revokes the rule.
        # Its earlier positive interventions are no longer valid witnesses
        # to the new revision's causal establishment.
        negative = agency_report(
            m, "failed", step=9, option="option:failed",
            observed=85.0, predicted=95.0, conforms=False,
        )
        m.integrate_causal_intervention(CausalIntervention(
            identifier="intervention:failed", contingency_ref=REF,
            episode_ref=negative.episode_ref,
            observation_ref="world:failed", command_ref="option:failed",
            comparator_ref=negative.identifier,
            context_signature="zone3",
            emitted_step=9, observed_step=10,
            observed_effect=False, comparator_status="nonconforming",
            attribution="uncertain",
            controlled_variables=(("primitive", "manger"),),
            action_applied=True,
        ))
        self.assertEqual(
            [x.after for x in m.publish_causal_inference()],
            ["hypothese_causale"],
        )
        self.assertEqual(m.established_prediction_corrections(), ())
        self.assertEqual(
            [x.after for x in intervention(
                m, "recovery1", step=11, context="zone1",
            )], ["testee_par_intervention"],
        )
        self.assertEqual(m.established_prediction_corrections(), ())
        self.assertEqual(
            [x.after for x in intervention(
                m, "recovery2", step=13, context="zone2",
            )], ["etablie"],
        )
        # Fresh P-35 interventions restore the *causal* fact, but cannot
        # reuse the pre-refutation body measurement as a current numerical
        # Simulator correction. Only a newly lived outcome can enable it.
        self.assertEqual(m.established_prediction_corrections(), ())
        no_numeric = m.export_causal_state()
        without_new_value = model()
        without_new_value.restore_causal_state(no_numeric)
        self.assertEqual(without_new_value.export_causal_state(), no_numeric)
        self.assertEqual(without_new_value.established_prediction_corrections(), ())

        physical_meal(m, step=15, option="option:meal:recovery")
        self.assertEqual(m.established_prediction_corrections(), ())
        m.publish_causal_inference()
        self.assertEqual(m.established_prediction_corrections(), ())
        agency_report(
            m, "meal-recovery", step=15, option="option:meal:recovery",
            observed=90.0, predicted=100.0, conforms=False,
        )
        (reestablished,) = m.established_prediction_corrections()
        self.assertEqual(reestablished.contingency_ref, REF)
        self.assertEqual(reestablished.observed_after, 90.0)
        self.assertEqual(reestablished.intervention_ref, "intervention:recovery1")
        self.assertNotEqual(reestablished.intervention_ref, original.intervention_ref)
        self.assertNotEqual(reestablished.agency_evidence_ref, original.agency_evidence_ref)

        snapshot = m.export_causal_state()
        replay = model()
        replay.restore_causal_state(snapshot)
        self.assertEqual(replay.export_causal_state(), snapshot)
        self.assertEqual(replay.established_prediction_corrections(), (reestablished,))

    def test_numeric_witness_needs_exact_published_comparator_value_and_identity(self):
        for option, step, observed in (
            ("option:meal", 2, 89.0),  # different bodily observation
            ("option:unrelated", 2, 90.0),  # different executed option
            ("option:meal", 1, 90.0),  # different world-step lineage
        ):
            with self.subTest(option=option, step=step, observed=observed):
                m = model()
                physical_meal(m)
                m.publish_causal_inference()
                hypothesis(m)
                agency_report(
                    m, "meal", step=step, option=option, observed=observed,
                    predicted=100.0, conforms=False,
                )
                intervention(m, "first", step=5, context="zone1")
                intervention(m, "second", step=7, context="zone2")
                self.assertEqual(m.get(REF).causal_status, "etablie")
                self.assertEqual(m.established_prediction_corrections(), ())

    def test_safety_status_alone_never_produces_simulator_rule(self):
        m = model()
        # Unit-only typed evidence isolates INV-25. The production food
        # ingestion path is fail-closed by the issue #89 regressions.
        for index in (1, 2):
            m.integrate(SafetyEvidence(
                identifier=f"dc05:unit-safety:{index}", contingency_ref=REF,
                predicate="toxic_item", subject_ref="berry_b",
                context_signature="global",
                episode_ref=f"episode:unit-safety:{index}",
                observation_ref=f"world:unit-safety:{index}",
                emission_step=index * 2 - 1, observation_step=index * 2,
                harm_observed=True, source="monde",
                independent_episode=True, comparable_context=True,
                alternative_cause_sufficient=False,
                exposure_motivated_independently=True,
            ))
            m.publish()
        self.assertEqual(m.get(REF).safety_status, "etabli_pour_securite")
        self.assertEqual(m.get(REF).causal_status, "aucun")
        self.assertEqual(m.established_prediction_corrections(), ())
        # INV-25's observable test is a differential simulator prediction,
        # not merely the absence of a correction descriptor. A real safety
        # status must not silently alter any frozen-Equipment prediction.
        before = state(x=2)
        command = PrimitiveCommand("manger", {"target": "berry_b"})
        equipment = train_exact_transition_table(
            corpus=EquipmentCorpus(
                version="stage9-safety-inv25-control-v1",
                examples=(EquipmentCorpusExample(
                    family="physical_safety_control",
                    state=before, command=command,
                    observed_next_state=before, terminal=False,
                ),),
            ),
            equipment_version="E-stage9-safety-control",
        )
        config = SimulatorConfig(
            version="stage9-safety-inv25-v1", r_max=1, h_max=1,
        )
        frozen = Simulator(config=config, equipment=equipment)
        with_safety = Simulator(config=config, equipment=equipment, corrections=m)
        params = dict(
            initial_state=before, commands=(command,), r_eff=1, h_eff=1,
        )
        control_result = frozen.rollout(**params)
        safety_result = with_safety.rollout(**params)
        self.assertTrue(control_result.complete)
        self.assertEqual(safety_result, control_result)
        self.assertEqual(safety_result.corrected_contingency_refs, ())

    def test_stage9_runtime_attaches_only_one_canonical_reader(self):
        r = build_stage9_reference_runtime()
        self.assertIs(r.simulator._corrections, r.causal_model)
        self.assertEqual(r.causal_model.established_prediction_corrections(), ())
        with self.assertRaises(ValueError):
            r.simulator.attach_established_correction_source(r.causal_model)


if __name__ == "__main__":
    unittest.main()
