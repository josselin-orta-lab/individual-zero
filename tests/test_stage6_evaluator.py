from __future__ import annotations

import unittest
from dataclasses import replace

from i0.equipment import (
    EquipmentCorpus,
    EquipmentCorpusExample,
    train_exact_transition_table,
)
from i0.interfaces import PrimitiveCommand
from i0.modules.competition import (
    Competition,
    CompetitionConfig,
)
from i0.modules.simulator import Simulator, SimulatorConfig
from i0.modules.stage6_evaluator import (
    Stage6EvaluationConfig,
    Stage6OptionEvaluator,
)
from i0.modules.value_needs import ValueNeedsConfig

from test_stage4_modules import proposal
from test_stage6_equipment import state


def needs_config() -> ValueNeedsConfig:
    return ValueNeedsConfig(
        version="stage6-needs-test-v1",
        setpoints={
            "energy": 50.0,
            "food": 60.0,
            "water": 60.0,
            "integrity": 100.0,
        },
        weights={
            "energy": 1.0,
            "food": 1.0,
            "water": 1.0,
            "integrity": 1.0,
        },
        normalization_scales={
            "energy": 100.0,
            "food": 100.0,
            "water": 100.0,
            "integrity": 100.0,
        },
        p_min=0.1,
        contribution_ttl_steps=5,
    )


def evaluator_with_drink_transition(
    *,
    include_wait: bool = False,
) -> Stage6OptionEvaluator:
    before = replace(
        state(),
        body={
            "energy": 50.0,
            "food": 60.0,
            "water": 20.0,
            "integrity": 100.0,
        },
        current_water_source=True,
    )
    after = replace(
        before,
        body={
            "energy": 50.0,
            "food": 60.0,
            "water": 60.0,
            "integrity": 100.0,
        },
    )
    examples = [
        EquipmentCorpusExample(
            family="drinking",
            state=before,
            command=PrimitiveCommand("boire"),
            observed_next_state=after,
            terminal=False,
        ),
    ]
    if include_wait:
        examples.append(
            EquipmentCorpusExample(
                family="wait",
                state=before,
                command=PrimitiveCommand("attendre"),
                observed_next_state=before,
                terminal=False,
            )
        )
    corpus = EquipmentCorpus(
        version="stage6-eval-corpus-v1",
        examples=tuple(examples),
    )
    equipment = train_exact_transition_table(
        corpus=corpus,
        equipment_version="E-v1-test",
    )
    return Stage6OptionEvaluator(
        config=Stage6EvaluationConfig(
            version="stage6-eval-test-v1",
            evidence_scale=10.0,
            beta=0.8,
            r_eff=3,
            h_eff=1,
        ),
        simulator=Simulator(
            config=SimulatorConfig(
                version="sim-test-v1",
                r_max=3,
                h_max=2,
            ),
            equipment=equipment,
        ),
        needs_config=needs_config(),
    )


class Stage6OptionEvaluatorTests(unittest.TestCase):
    def test_homeostatic_improvement_produces_positive_simulated_evidence(self) -> None:
        evaluator = evaluator_with_drink_transition()
        initial = replace(
            state(),
            body={
                "energy": 50.0,
                "food": 60.0,
                "water": 20.0,
                "integrity": 100.0,
            },
            current_water_source=True,
        )

        result = evaluator.evaluate(
            proposal=proposal("drink", "boire"),
            initial_state=initial,
            cycle=1,
            t_monde=1,
        )

        self.assertEqual(result.evaluation.status, "evaluated")
        self.assertEqual(result.evaluation.simulated_value_status, "computed")
        self.assertEqual(result.evaluation.simulated_value, 40.0)
        self.assertIsNotNone(result.evidence)
        self.assertGreater(result.evidence, 0.9)

    def test_unseen_transition_is_not_evaluated_without_zero_substitution(self) -> None:
        evaluator = evaluator_with_drink_transition()

        result = evaluator.evaluate(
            proposal=proposal("move", "se_deplacer"),
            initial_state=state(),
            cycle=1,
            t_monde=1,
        )

        self.assertEqual(result.evaluation.status, "not_evaluated")
        self.assertEqual(result.evaluation.simulated_value_status, "unavailable")
        self.assertIsNone(result.evidence)

    def test_revised_plan_above_delta_is_improved_under_same_budget(self) -> None:
        evaluator = evaluator_with_drink_transition(include_wait=True)
        initial = replace(
            state(),
            body={
                "energy": 50.0,
                "food": 60.0,
                "water": 20.0,
                "integrity": 100.0,
            },
            current_water_source=True,
        )

        comparison = evaluator.compare_revised_plans(
            old_proposal=proposal("same", "attendre"),
            new_proposal=proposal("same", "boire"),
            initial_state=initial,
            delta_plan=5.0,
            cycle=1,
            t_monde=1,
        )

        self.assertEqual(comparison.status, "improved")
        self.assertEqual(comparison.old_value, 0.0)
        self.assertEqual(comparison.new_value, 40.0)
        self.assertEqual(comparison.delta, 40.0)
        self.assertEqual(comparison.r_eff, 3)
        self.assertEqual(comparison.h_eff, 1)

    def test_revised_plan_below_delta_is_not_improved(self) -> None:
        evaluator = evaluator_with_drink_transition(include_wait=True)
        initial = replace(
            state(),
            body={
                "energy": 50.0,
                "food": 60.0,
                "water": 20.0,
                "integrity": 100.0,
            },
            current_water_source=True,
        )

        comparison = evaluator.compare_revised_plans(
            old_proposal=proposal("same", "attendre"),
            new_proposal=proposal("same", "boire"),
            initial_state=initial,
            delta_plan=50.0,
            cycle=1,
            t_monde=1,
        )

        self.assertEqual(comparison.status, "not_improved")
        self.assertEqual(comparison.delta, 40.0)

    def test_unavailable_revised_plan_is_never_declared_better(self) -> None:
        evaluator = evaluator_with_drink_transition(include_wait=True)
        initial = replace(
            state(),
            body={
                "energy": 50.0,
                "food": 60.0,
                "water": 20.0,
                "integrity": 100.0,
            },
            current_water_source=True,
        )

        comparison = evaluator.compare_revised_plans(
            old_proposal=proposal("same", "attendre"),
            new_proposal=proposal("same", "se_deplacer"),
            initial_state=initial,
            delta_plan=0.0,
            cycle=1,
            t_monde=1,
        )

        self.assertEqual(comparison.status, "unavailable")
        self.assertIsNone(comparison.delta)

    def test_not_evaluated_candidate_freezes_accumulator(self) -> None:
        comp = Competition(
            CompetitionConfig(
                version="stage6-comp-test-v1",
                c_max=3,
                urgency_max=2.0,
                urgency_scale_cycles=2.0,
                leak=0.1,
                noise_sigma=0.0,
                gain=1.0,
                base_threshold=1.0,
                threshold_floor=0.1,
                inertia=0.2,
                residual=0.5,
                options_max=4,
                substitution_evidence={"boire": 0.6},
            )
        )
        p = proposal("drink", "boire")
        comp.register(p, active_goal_id=None, t_monde=1)
        comp.open_deliberation(active_goal_id=None, t_monde=1)
        first = comp.evaluate(cycle=1, t_monde=1)
        before = first.traces[0].accumulator_after

        unavailable = evaluator_with_drink_transition().evaluate(
            proposal=proposal("move", "se_deplacer"),
            initial_state=state(),
            cycle=2,
            t_monde=1,
        )
        # Rebind the typed unavailable status to the actual registered option.
        from i0.contracts import EvaluationOption
        from i0.modules.competition import OptionEvidenceInput

        ev = unavailable.evaluation
        supplied = OptionEvidenceInput(
            evaluation=EvaluationOption(
                option_ref=p.option.id,
                option_version=p.option.version,
                cycle=2,
                t_monde=1,
                status=ev.status,
                learned_value_status=ev.learned_value_status,
                learned_value=ev.learned_value,
                simulated_value_status=ev.simulated_value_status,
                simulated_value=ev.simulated_value,
                intrinsic_status=ev.intrinsic_status,
                intrinsic_value=ev.intrinsic_value,
                risk_status=ev.risk_status,
                risk=ev.risk,
                safety_uncertainty=ev.safety_uncertainty,
                protection=ev.protection,
                signal_ids=ev.signal_ids,
                producers=ev.producers,
            ),
            evidence=None,
        )
        second = comp.evaluate(
            cycle=2,
            t_monde=1,
            evidence_inputs={p.option.id: supplied},
        )

        self.assertEqual(second.traces[0].accumulator_before, before)
        self.assertEqual(second.traces[0].accumulator_after, before)
        self.assertIsNone(second.traces[0].evidence)


if __name__ == "__main__":
    unittest.main()
