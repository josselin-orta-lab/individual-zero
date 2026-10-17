"""Stage-9 spontaneous hydration observations: physical and autobiographical."""
from __future__ import annotations
from dataclasses import replace
import unittest

from i0.modules.causal_model import CausalModelConfig
from lab.stage9_reference_fixture import build_stage9_reference_runtime
from lab.stage9_runtime import Stage9Runtime


def runtime(*, gain=40.0):
    base=build_stage9_reference_runtime()
    config=replace(base._stage9_config, causal=CausalModelConfig(
        version="stage9-autonomous-water-evidence-v1",
        n1=2,n2=2,n_sec=2,m_sec=2,
        causal_predicates=("hydration_effect",),
        safe_test_actions=(("hydration_effect","water","boire"),),
    ))
    return Stage9Runtime(
        world_config=replace(base.world.config,drink_water_gain=gain),
        layout=base.world._layout,
        safety_config=base.stage3.substrate.safety._config,
        safety_facts=base._canonical_safety._innate,
        protected_integrity_threshold=base.stage3.control._config.protected_integrity_threshold,
        config=config,equipment=base.equipment,
    )


class HydrationObservationsTests(unittest.TestCase):
    def test_real_unseeded_drink_becomes_observation_not_intervention(self):
        individual=runtime()
        self.assertEqual(individual.causal_model.contingencies(),())
        self.assertEqual(individual.run_step().command_primitive,"boire")
        self.assertEqual(individual.causal_model.contingencies(),())
        for _ in range(5):
            individual.run_step()
        state=individual.causal_model.export_causal_state()
        rows=[row for row in state["causal_observations"] if row["predicate"]=="hydration_effect"]
        self.assertTrue(rows)
        self.assertTrue(any(row["cause_present"] and row["effect_present"] for row in rows))
        self.assertEqual(state["causal_interventions"],[])
        self.assertTrue(state["hydration_observation_witnesses"])
        self.assertTrue(individual.journal.verify())

    def test_null_world_records_absent_effect_without_fake_causality(self):
        individual=runtime(gain=0.0)
        self.assertEqual(individual.run_step().command_primitive,"boire")
        for _ in range(5):
            individual.run_step()
        rows=[row for row in individual.causal_model.export_causal_state()["causal_observations"] if row["predicate"]=="hydration_effect"]
        self.assertTrue(rows)
        self.assertTrue(any(row["cause_present"] and not row["effect_present"] for row in rows))
        self.assertNotEqual(individual.causal_model.get("causal:hydration").causal_status,"etablie")
        self.assertEqual(individual.causal_model.export_causal_state()["causal_interventions"],[])

    def test_snapshot_restores_passive_pending_observation(self):
        first=runtime()
        first.run_step()
        original=first.causal_model.export_causal_state()
        self.assertEqual(len(original["lived_hydration_exposures"]),1)
        second=runtime()
        second.causal_model.restore_causal_state(original)
        self.assertEqual(second.causal_model.export_causal_state(),original)


if __name__=="__main__":
    unittest.main()
