"""Normative Stage-8 DC-06 / INV-01, 05, 26, 27, 33, 43 tests."""
import unittest

from i0.modules.active_kappa import ActiveKappa, KappaConfig, KappaVerification
from i0.modules.gatekeeper import Gatekeeper
from i0.contracts import Contribution
from lab.stage8_reference_fixture import build_stage8_reference_runtime


def verification(identifier="v1", **changes):
    fields = dict(
        identifier=identifier,
        equipment_or_module_version="E-v1",
        module="perception",
        contribution_type="observation",
        signal_family="world_symbolic",
        declared_confidence=0.9,
        emission_step=1,
        observation_step=2,
        outcome="confirmee",
        observation_anchor="monde",
        independent_family="body_telemetry",
        physical_consequence=False,
        provenance_independent=True,
    )
    fields.update(changes)
    return KappaVerification(**fields)


def model():
    return ActiveKappa(KappaConfig("p33-test-v1", 4, 2.0, {}))


def reliability(k, **changes):
    params = dict(version="E-v1", module="perception",
                  contribution_type="observation", family="world_symbolic",
                  confidence=0.9)
    params.update(changes)
    return k.reliability(**params)


class KappaTests(unittest.TestCase):
    def test_neutral_prior_and_phase_boundary(self):
        k = model()
        self.assertEqual(reliability(k), 0.5)
        k.integrate(verification())
        self.assertEqual(reliability(k), 0.5)  # INV-05
        self.assertEqual(k.publish()[0][2], 2 / 3)
        self.assertEqual(reliability(k), 2 / 3)

    def test_same_family_repetition_and_provenance_do_not_train(self):
        k = model()
        invalid = [
            dict(independent_family="world_symbolic"),
            dict(observation_anchor="derive"),
            dict(observation_step=1),
            dict(provenance_independent=False),
            dict(oracle_derived=True),
            dict(rollback_cancelled=True),
            dict(outcome="stabilite_meme_canal"),
            dict(outcome="indeterminee"),
            dict(outcome="non_verifiable"),
            dict(outcome="contrefactuelle_non_verifiee"),
        ]
        for n, changes in enumerate(invalid):
            k.integrate(verification(f"invalid-{n}", **changes))
        self.assertEqual(k.publish(), ())
        self.assertEqual(reliability(k), 0.5)  # INV-26/27/43

    def test_independent_contradiction_and_version_segment(self):
        k = model()
        k.integrate(verification("contradiction", outcome="contredite"))
        k.publish()
        self.assertEqual(reliability(k), 1 / 3)
        self.assertEqual(reliability(k, version="E-v2"), 0.5)
        self.assertEqual(reliability(k, family="body_telemetry"), 0.5)
        self.assertEqual(reliability(k, module="memory"), 0.5)
        self.assertEqual(reliability(k, contribution_type="alert"), 0.5)

    def test_physical_consequence_without_independent_modality(self):
        k = model()
        k.integrate(verification(independent_family=None, physical_consequence=True))
        self.assertEqual(len(k.publish()), 1)

    def test_snapshot_restore_pending_and_determinism(self):
        first = model()
        first.integrate(verification("v2", outcome="contredite"))
        first.integrate(verification("v1"))
        checkpoint = first.export_causal_state()
        restored = model()
        restored.restore_causal_state(checkpoint)
        self.assertEqual(checkpoint, restored.export_causal_state())
        self.assertEqual(first.publish(), restored.publish())
        self.assertEqual(first.export_causal_state(), restored.export_causal_state())

    def test_gatekeeper_consumes_versioned_reliability_without_legacy_regression(self):
        runtime = build_stage8_reference_runtime()
        contribution = Contribution(
            id="stage8-gate-alert", schema_version="mvp-v1.2.1",
            type="alert", summary="observed local event",
            subject_ref="local:event", emitter_module="perception",
            signal_family="world_symbolic", confidence=0.8,
            urgency=0.4, risk=0.6, value=0.2,
            production_t=1, production_cycle=1, expires_at_step=5,
            payload={"anchor": "world"},
        )
        contribution.validate()
        scoring = dict(active_goal=None, occupant=False,
                       subjects_present_before_new=set())
        stage8 = runtime.gatekeeper
        legacy = Gatekeeper(stage8.config)
        before = stage8._score(contribution, **scoring).score
        original = legacy._score(contribution, **scoring).score
        self.assertEqual(before, original * 0.5)
        verified = verification(
            "physically-confirmed-alert",
            equipment_or_module_version=runtime._config.version,
            module="perception", contribution_type="alert",
            declared_confidence=0.8,
            independent_family="body_telemetry",
        )
        runtime.integrate_kappa_verification(verified)
        self.assertEqual(stage8._score(contribution, **scoring).score, before)
        runtime.kappa_active.publish()
        after = stage8._score(contribution, **scoring).score
        self.assertEqual(after, original * (2 / 3))
        self.assertEqual(legacy._score(contribution, **scoring).score, original)

    def test_unknown_family_rejected_and_duplicates_rejected(self):
        k = model()
        with self.assertRaises(ValueError):
            k.integrate(verification(signal_family="new_undeclared_family"))
        k.integrate(verification())
        with self.assertRaises(ValueError):
            k.integrate(verification())
        k.publish()
        with self.assertRaises(ValueError):
            k.integrate(verification())


if __name__ == "__main__":
    unittest.main()
