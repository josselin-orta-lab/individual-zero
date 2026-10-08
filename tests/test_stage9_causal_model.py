"""Stage-9 DC-05 canonical safety: episode deduplication and sole read source."""
import unittest

from i0.modules.action_control import (
    ActionControl, ActionControlConfig, PreparedCommand, StaticSafetyFacts, Admissibility
)
from i0.interfaces import PrimitiveCommand
from i0.modules.causal_model import (
    CausalModel, CausalModelConfig, SafetyEvidence, CanonicalSafetyFacts
)
from test_action_control import capture


def model():
    return CausalModel(CausalModelConfig("stage9-dc05-test-v1", 2, 2, 2, 2))


def evidence(identifier="e1", **kwargs):
    args = dict(
        identifier=identifier,
        contingency_ref="toxic:berry_b",
        predicate="toxic_item", subject_ref="berry_b",
        context_signature="global",
        episode_ref=f"episode:{identifier}",
        observation_ref=f"physical:{identifier}",
        emission_step=1, observation_step=2,
        harm_observed=True, source="monde",
        independent_episode=True, comparable_context=True,
        alternative_cause_sufficient=False,
        exposure_motivated_independently=True,
    )
    args.update(kwargs)
    return SafetyEvidence(**args)


class CanonicalCausalSafetyTests(unittest.TestCase):
    def test_distinct_lived_episodes_promote_only_at_phase_closure(self):
        m = model()
        m.integrate(evidence())
        self.assertIsNone(m.get("toxic:berry_b"))
        self.assertEqual(m.publish(), ())
        self.assertEqual(m.get("toxic:berry_b").safety_status, "aucun")
        m.integrate(evidence("e2"))
        self.assertEqual(m.get("toxic:berry_b").safety_status, "aucun")
        changes = m.publish()
        self.assertEqual(len(changes), 1)
        fact = m.get("toxic:berry_b")
        self.assertEqual(fact.safety_status, "etabli_pour_securite")
        self.assertEqual(fact.causal_status, "aucun")  # INV-25

    def test_single_episode_and_repeated_observation_never_promote(self):
        m = model()
        m.integrate(evidence("first", episode_ref="same", observation_ref="same"))
        m.integrate(evidence("second", episode_ref="same", observation_ref="same"))
        m.publish()
        self.assertEqual(m.get("toxic:berry_b").safety_status, "aucun")
        self.assertEqual(len(m.get("toxic:berry_b").evidence_refs), 1)

    def test_contradiction_resets_unestablished_run(self):
        m = model()
        m.integrate(evidence("one"))
        m.publish()
        m.integrate(evidence("noharm", harm_observed=False))
        m.publish()
        m.integrate(evidence("three"))
        m.publish()
        self.assertEqual(m.get("toxic:berry_b").safety_status, "aucun")
        m.integrate(evidence("four"))
        m.publish()
        self.assertEqual(m.get("toxic:berry_b").safety_status, "etabli_pour_securite")

    def test_incidental_demotion_requires_two_distinct_safe_episodes(self):
        m = model()
        for name in ("harm1", "harm2"):
            m.integrate(evidence(name))
            m.publish()
        self.assertEqual(m.get("toxic:berry_b").safety_status, "etabli_pour_securite")
        m.integrate(evidence("safe1", harm_observed=False))
        m.publish()
        self.assertEqual(m.get("toxic:berry_b").safety_status, "etabli_pour_securite")
        m.integrate(evidence("safe2", harm_observed=False))
        m.publish()
        self.assertEqual(m.get("toxic:berry_b").safety_status, "aucun")

    def test_oracle_rollback_counterfactual_and_unmotivated_probes_rejected(self):
        for override in (
            {"oracle_derived": True},
            {"rollback_cancelled": True},
            {"counterfactual": True},
            {"independent_episode": False},
            {"exposure_motivated_independently": False},
            {"alternative_cause_sufficient": True},
        ):
            m = model()
            before = m.export_causal_state()
            with self.assertRaises(ValueError):
                m.integrate(evidence(**override))
            self.assertEqual(before, m.export_causal_state())

    def test_canonical_adapter_changes_veto_without_causal_establishment(self):
        m = model()
        adapter = CanonicalSafetyFacts(innate=StaticSafetyFacts(), causal_model=m)
        control = ActionControl(
            config=ActionControlConfig("mvp-v1.2.1", 15.0),
            safety_facts=adapter, protocol_mask=lambda cmd: False,
        )
        prepared = PreparedCommand(
            command=PrimitiveCommand("manger", {"target": "berry_b"}),
            source="decision",
        )
        prior = control.admit(capture=capture(), prepared=prepared)
        self.assertTrue(prior.ok)
        for name in ("harm1", "harm2"):
            m.integrate(evidence(name))
            m.publish()
        self.assertEqual(adapter.item_status(resource_kind="berry_b"), "known_toxic")
        veto = control.admit(capture=capture(), prepared=prepared)
        self.assertFalse(veto.ok)
        self.assertEqual(veto.rule_id, "toxic_item_consumption")
        self.assertEqual(m.get("toxic:berry_b").causal_status, "aucun")

    def test_snapshot_pending_and_replay_are_identical(self):
        m = model()
        m.integrate(evidence("first"))
        checkpoint = m.export_causal_state()
        twin = model()
        twin.restore_causal_state(checkpoint)
        self.assertEqual(twin.export_causal_state(), checkpoint)
        self.assertEqual(m.publish(), twin.publish())
        self.assertEqual(m.export_causal_state(), twin.export_causal_state())


if __name__ == "__main__":
    unittest.main()
