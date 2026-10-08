"""Stage-9 live integration tests: DC-05 phase-5, INV-01/25/27/33."""
import unittest

from i0.interfaces import PrimitiveCommand
from i0.modules.action_control import PreparedCommand
from i0.modules.causal_model import SafetyEvidence
from lab.stage9_reference_fixture import build_stage9_reference_runtime
from test_action_control import capture_with_creature


def observed(identifier):
    return SafetyEvidence(
        identifier=identifier,
        contingency_ref="toxic:berry_b",
        predicate="toxic_item",
        subject_ref="berry_b",
        context_signature="global",
        episode_ref=f"episode:{identifier}",
        observation_ref=f"world:{identifier}",
        emission_step=0, observation_step=1,
        harm_observed=True, source="monde",
        independent_episode=True, comparable_context=True,
        alternative_cause_sufficient=False,
        exposure_motivated_independently=True,
    )


class Stage9IntegrationTests(unittest.TestCase):
    def test_causal_owner_and_snapshot_are_separate(self):
        runtime = build_stage9_reference_runtime()
        owners = runtime.causal_owners
        self.assertEqual(sum(o.owner_id == "causal_model" for o in owners), 1)
        state = runtime.causal_model.export_causal_state()
        self.assertEqual(runtime.causal_model.version, 0)
        runtime.causal_model.restore_causal_state(state)
        self.assertEqual(runtime.causal_model.export_causal_state(), state)

    def test_phase_five_status_changes_veto_only_on_published_status(self):
        runtime = build_stage9_reference_runtime()
        action = PreparedCommand(
            command=PrimitiveCommand("manger", {"target": "berry_b"}),
            source="decision",
        )
        capture = capture_with_creature(creature_direction=None)
        control = runtime.stage3.control
        self.assertTrue(control.admit(capture=capture, prepared=action).ok)
        runtime.causal_model.integrate(observed("episode1"))
        runtime.causal_model.integrate(observed("episode2"))
        self.assertTrue(control.admit(capture=capture, prepared=action).ok)
        self.assertEqual(runtime.run_step().execution_status, "applied")
        self.assertFalse(control.admit(capture=capture, prepared=action).ok)
        fact = runtime.causal_model.get("toxic:berry_b")
        self.assertEqual(fact.safety_status, "etabli_pour_securite")
        self.assertEqual(fact.causal_status, "aucun")
        self.assertIn(
            b"causal_safety_status_published",
            runtime.journal.canonical_bytes(),
        )


if __name__ == "__main__":
    unittest.main()
