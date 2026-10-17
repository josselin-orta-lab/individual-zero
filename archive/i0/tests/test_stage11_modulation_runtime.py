"""I0-vNext Stage-11 live wiring tests; public fixtures only, no EXP."""
import unittest

from i0.contracts import Contribution
from i0.modules.gatekeeper import Gatekeeper
from lab.stage9_reference_fixture import build_stage9_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime


def novel_signal():
    return Contribution(
        id="modulation:sample", schema_version="mvp-v1.2.1",
        type="observation", summary="novel nonrisk sample",
        subject_ref="entity:unique:nonrisk", emitter_module="perception",
        signal_family="world_symbolic", confidence=1.0, urgency=0.0,
        risk=0.0, value=0.0, production_t=1, production_cycle=1,
        expires_at_step=20, payload={"entity_type": "berry_a"},
    )


class Stage11ModulationRuntimeTests(unittest.TestCase):
    def test_stage11_profile_is_frozen_and_published_in_st(self):
        runtime = build_stage11_reference_runtime()
        self.assertEqual(runtime.modulation.profile, "normal")
        owners = [owner.owner_id for owner in runtime.causal_owners]
        self.assertEqual(owners.count("global_modulation"), 1)
        self.assertEqual(len(owners), len(set(owners)))
        self.assertEqual(runtime.run_step().execution_status, "applied")
        fixed = runtime.s_t.current.fixed
        self.assertEqual(fixed["profile"]["name"], "normal")
        self.assertIn("modulation_signals", fixed)
        self.assertEqual(runtime.modulation.export_causal_state()["profile"], "normal")
        self.assertTrue(runtime.journal.verify())

    def test_baseline_stage9_uses_no_modulation_fields(self):
        stage9 = build_stage9_reference_runtime()
        self.assertEqual(stage9.run_step().execution_status, "applied")
        self.assertEqual(stage9.s_t.current.fixed["profile"], {"name": "normal"})
        self.assertNotIn("modulation_signals", stage9.s_t.current.fixed)
        self.assertTrue(stage9.journal.verify())

    def test_gatekeeper_scores_use_ephemeral_weights_only(self):
        baseline = build_stage9_reference_runtime()
        old_config = baseline.gatekeeper.config
        first = Gatekeeper(old_config)
        second = Gatekeeper(old_config)
        contribution = novel_signal()
        contribution.validate()
        neutral = first.select(
            (contribution,), active_goal=None, t_monde=1,
        )
        higher_novelty = second.select(
            (contribution,), active_goal=None, t_monde=1,
            profile_multipliers={
                "b": 1, "n": 1.5, "urg": 1, "risk": 1, "value": 1,
            },
        )
        self.assertEqual(len(neutral.elements), 1)
        self.assertEqual(len(higher_novelty.elements), 1)
        self.assertGreater(higher_novelty.elements[0].score,
                           neutral.elements[0].score)
        self.assertEqual(second.config, old_config)
        with self.assertRaises(ValueError):
            Gatekeeper(old_config).select(
                (contribution,), active_goal=None, t_monde=1,
                profile_multipliers={
                    "b": 1, "n": 1, "urg": 1, "risk": -1, "value": 1,
                },
            )

    def test_new_runtime_exact_reexecution_with_cycle_profile(self):
        first = build_stage11_reference_runtime()
        second = build_stage11_reference_runtime()
        for runtime in (first, second):
            for _ in range(3):
                self.assertEqual(runtime.run_step().execution_status, "applied")
        self.assertEqual(first.journal.canonical_bytes(), second.journal.canonical_bytes())
        self.assertEqual(first.modulation.export_causal_state(),
                         second.modulation.export_causal_state())


if __name__ == "__main__":
    unittest.main()
