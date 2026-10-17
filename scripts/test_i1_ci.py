#!/usr/bin/env python3
"""Current-I1 software validation. No historical A2 experiment is an oracle.

SMOKE is the PR gate. FULL exercises more independent mortal identities.
A seed selects a reproducible birth identity; the current actor uses no
invented random hazard knowledge. Python unittest remains the assertion engine.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import time
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate

SEED = 0


class CurrentI1(unittest.TestCase):
    """Observable physical contracts of the current canonical natural actor."""

    @classmethod
    def setUpClass(cls):
        cls._build_home = TemporaryDirectory(prefix="i1-ci-build-")
        cls._generated = Path(cls._build_home.name) / "generated"
        generate(cls._generated)
        sys.path.insert(0, str(cls._generated))

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(str(cls._generated))
        cls._build_home.cleanup()

    def setUp(self):
        self._home = TemporaryDirectory(prefix="i1-ci-life-")
        self.addCleanup(self._home.cleanup)
        self._births = 0

    def born(self, *, life_id=None, body=None, resource=True, water=True):
        from i1lab.i1_birth import birth_i1
        from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
        from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
        from i1lab.world import WorldLayout
        from i1.modules.stage12_detectors import Stage12DetectionPolicy

        self._births += 1
        base = build_stage11_reference_runtime(autonomous_mortal=True)
        sleep = build_stage10_reference_runtime(autonomous_mortal=True)
        physical = replace(
            base.world.config,
            version="i1-ci-current-physical-v1",
            initial_body=body or replace(base.world.config.initial_body,
                energy=70.0, food=30.0, water=30.0, integrity=80.0),
        )
        position = physical.initial_position
        layout = WorldLayout(
            resources=((position, "berry_b", 4),) if resource else (),
            water_sources=frozenset({position}) if water else frozenset(),
            oracle_canary="HIDDEN-HAZARD-CI-CANARY",
        )
        stage10 = replace(
            sleep._stage10_config, stage9=base._stage11_config.stage9,
        )
        detector = Stage12DetectionPolicy(
            version="i1-ci-current-diagnostic-v1",
            window=12, stagnation_steps=3, stagnation_tolerance=0.05,
            loop_repetitions=2, loop_max_period=2,
            entropy_min_samples=3, entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75,
        )
        name = life_id or ("i1:ci:" + str(SEED) + ":" +
                           self._testMethodName + ":" + str(self._births))
        wal = str(Path(self._home.name) / ("life-" + str(self._births) + ".wal"))
        life = birth_i1(
            life_id=name, wal_path=wal, world_config=physical, layout=layout,
            safety_config=base.stage3.substrate.safety._config,
            safety_facts=base._canonical_safety._innate,
            protected_integrity_threshold=(
                base.stage3.control._config.protected_integrity_threshold),
            stage11_config=base._stage11_config, stage10_config=stage10,
            equipment=base.equipment, detector_policy=detector,
        )
        return life, wal

    def test_birth_identity_and_custody(self):
        from i1lab.i1_natural_runtime import I1Runtime
        life, _ = self.born()
        self.assertIs(type(life), I1Runtime)
        self.assertTrue(life.individual_id.startswith("i1:ci:"))
        self.assertTrue(life.journal.durable_wal_enabled)
        self.assertIsNone(life.stage3.substrate.bench)
        self.assertIsNone(life.stage3.substrate.evaluation_trace)
        owners = [item.owner_id for item in life.causal_owners]
        self.assertEqual(len(owners), len(set(owners)), owners)
        for owner in ("value_and_needs", "causal_model", "perception",
                      "metacognition_health"):
            self.assertEqual(owners.count(owner), 1)
        self.assertGreater(life.world.config.food_decay_per_step, 0)
        self.assertGreater(life.world.config.water_decay_per_step, 0)
        self.assertGreater(
            life.world.config.starvation_integrity_damage_per_step, 0)
        self.assertGreater(
            life.world.config.dehydration_integrity_damage_per_step, 0)

    def test_complete_natural_architecture_is_enabled(self):
        """No historical test flags or disabled current-I1 cognitive modules.

        Validate the real canonical birth without ablation, mocks, forced
        decisions or altered policy weights. Old external predictors are NOT
        part of the present first-person architecture.
        """
        from i1lab.i1_active_value_needs import I1ActiveValueNeeds
        from i1lab.i1_water_runtime import CONSIDER, ACQUIRE
        from i1lab.i1_active_runtime import I1_AFFORDANCE_OPERATION

        life, _ = self.born()
        self.assertIs(type(life.value_needs), I1ActiveValueNeeds)
        self.assertTrue(life._i1_unknown_action_enabled)
        self.assertTrue(life._i1_water_probe_enabled)
        self.assertTrue(life._i1_water_learning_enabled)
        self.assertTrue(life._goal_agency_enabled)
        self.assertTrue(life._dual_scope_enabled)
        self.assertTrue(life._spatial_goal_enabled)
        self.assertIsNotNone(life.exploration.geographic)
        self.assertIsNotNone(life._water_learner)
        self.assertIsNotNone(life.goal_manager)
        self.assertIsNotNone(life.memory)
        self.assertIsNotNone(life.planning)
        self.assertIsNotNone(life.competition)
        self.assertIsNotNone(life.causal_model)
        self.assertIsNotNone(life.slow_history)
        self.assertIsNotNone(life.sleep_health)
        self.assertIsNotNone(life.modulation)
        self.assertEqual(
            set(life._i1_active_owner_views),
            {"causal_model", "perception", "metacognition_health"},
        )
        config = life._stage11_config
        self.assertTrue(config.cycle_occurrence_guard_enabled)
        self.assertTrue(config.geographic_capacity_guard_enabled)
        self.assertIsNotNone(config.geographic)
        self.assertTrue(
            config.stage9.stage8.stage7.stage6.planning.progressive_subgoals)
        sleep = life._stage10_config.sleep
        self.assertGreater(sleep.fatigue_gain, 0)
        self.assertGreater(sleep.consolidation_weight, 0)
        self.assertGreater(sleep.night_weight, 0)
        costs = life.compute_budget._config.operation_costs
        for operation in (
            I1_AFFORDANCE_OPERATION, CONSIDER, ACQUIRE,
            "i1_private_procedure_recall", "stage12_diagnostic_sample",
            "goal_agency_assessment", "goal_outcome_responsibility_assessment",
        ):
            self.assertIn(operation, costs, operation)
            self.assertGreater(costs[operation], 0, operation)
        self.assertTrue(life.journal.verify())

    def test_active_modules_participate_in_real_step(self):
        """Witness a genuine charged cognitive pass, without selecting actions."""
        life, _ = self.born()
        before = len(life.journal.entries)
        outcome = life.run_step()
        self.assertIn(outcome.execution_status,
                      ("applied", "dead", "safety_block"))
        self.assertGreater(len(life.journal.entries), before)
        kinds = [entry.causal_event["kind"]
                 for entry in life.journal.entries[before:]]
        self.assertIn("compute_charge", kinds)
        self.assertIsNotNone(life.stage3._capture)
        self.assertTrue(life.journal.verify())

    def test_local_perception_excludes_hidden_truth(self):
        life, _ = self.born()
        local = life.world.capture_local(t_monde=1).as_dict()
        self.assertEqual(local["position"], life.world.position.as_dict())
        self.assertIn("berry_b", local["current_resources"])
        self.assertTrue(local["current_water_source"])
        self.assertEqual(len(local["adjacent"]), 4)
        self.assertNotIn("HIDDEN-HAZARD-CI-CANARY", str(local))
        for hidden in ("lethal_zones", "danger_zones", "oracle_canary"):
            self.assertNotIn(hidden, local)

    def test_real_steps_and_wal(self):
        from i1lab.journal import HashChainedJournal
        life, wal = self.born()
        outcomes = []
        for _ in range(3):
            outcome = life.run_step()
            self.assertIn(outcome.execution_status,
                          ("applied", "dead", "safety_block"))
            outcomes.append(outcome)
            if outcome.execution_status != "applied":
                break
        self.assertTrue(outcomes)
        self.assertGreaterEqual(life.scheduler.t_monde, 1)
        self.assertTrue(life.journal.verify())
        audit = HashChainedJournal.audit_durable_wal(wal)
        self.assertEqual(audit["head_hash"], life.journal.head_hash)
        self.assertEqual(audit["verified_entries"], len(life.journal.entries))
        self.assertTrue(all(0 <= x <= 100 for x in life.world.telemetry().values()))

    def test_collect_eat_and_drink_are_physically_possible(self):
        """Operator physical controls, not scripted individual decisions."""
        from i1lab.world import WorldBody, WorldLayout
        from i1.interfaces import PrimitiveCommand
        life, _ = self.born()
        at = life.world.config.initial_position
        physical = WorldBody(
            config=life.world.config,
            layout=WorldLayout(
                resources=((at, "berry_b", 3),),
                water_sources=frozenset({at}),
            ),
        )
        before = physical.inventory()["berry_b"]
        collected = physical.apply(
            PrimitiveCommand("collecter", {"target": "berry_b"}), t_monde=1)
        self.assertGreater(physical.inventory()["berry_b"], before)
        self.assertGreater(collected.effects["collected"]["quantity"], 0)
        before_food = physical.telemetry()["food"]
        eaten = physical.apply(
            PrimitiveCommand("manger", {"target": "berry_b"}), t_monde=2)
        self.assertEqual(eaten.effects["ate"], "berry_b")
        self.assertEqual(physical.inventory()["berry_b"], before)
        self.assertGreater(physical.telemetry()["food"], before_food)
        before_water = physical.telemetry()["water"]
        drank = physical.apply(PrimitiveCommand("boire", {}), t_monde=3)
        self.assertTrue(drank.effects["drank"])
        self.assertGreater(physical.telemetry()["water"], before_water)

    def test_missing_resources_fail_without_inventing_food(self):
        from i1lab.world import WorldBody, WorldLayout
        from i1.interfaces import PrimitiveCommand
        life, _ = self.born(resource=False, water=False)
        physical = WorldBody(config=life.world.config, layout=WorldLayout())
        ate = physical.apply(
            PrimitiveCommand("manger", {"target": "berry_b"}), t_monde=1)
        gathered = physical.apply(
            PrimitiveCommand("collecter", {"target": "berry_b"}), t_monde=2)
        drank = physical.apply(PrimitiveCommand("boire", {}), t_monde=3)
        self.assertEqual(ate.effects["ate"], "unavailable")
        self.assertEqual(gathered.effects["collected"]["quantity"], 0)
        self.assertFalse(drank.effects["drank"])
        self.assertEqual(physical.inventory()["berry_b"], 0)

    def test_deprivation_has_real_physical_cost(self):
        from i1lab.world import WorldBody, WorldLayout
        from i1.interfaces import PrimitiveCommand
        from i1lab.world import BodyState
        life, _ = self.born(body=BodyState(
            energy=40.0, food=0.0, water=0.0, integrity=40.0))
        physical = WorldBody(config=life.world.config, layout=WorldLayout())
        before = physical.telemetry()["integrity"]
        step = physical.apply(PrimitiveCommand("attendre", {}), t_monde=1)
        self.assertEqual(physical.telemetry()["food"], 0.0)
        self.assertEqual(physical.telemetry()["water"], 0.0)
        self.assertLess(physical.telemetry()["integrity"], before)
        charges = step.effects["deprivation_integrity_damage"]
        self.assertGreater(charges["starvation"], 0)
        self.assertGreater(charges["dehydration"], 0)

    def test_terminal_death_cannot_resume_or_rewind(self):
        from i1lab.world import BodyState
        from i1.interfaces import PrimitiveCommand
        life, _ = self.born(body=BodyState(
            energy=40.0, food=0.0, water=0.0, integrity=0.25))
        result = life.run_step()
        self.assertEqual(result.execution_status, "dead")
        self.assertEqual(life.stage3.substrate.mortal_status.value, "dead")
        self.assertTrue(life.journal.verify())
        frozen = life.world.telemetry()
        with self.assertRaises(RuntimeError):
            life.run_step()
        with self.assertRaises(RuntimeError):
            life.world.apply(PrimitiveCommand("attendre", {}),
                             t_monde=life.scheduler.t_monde + 1)
        with self.assertRaises(RuntimeError):
            life.world.restore_causal_state(life.world.export_causal_state())
        self.assertEqual(frozen, life.world.telemetry())

    def test_individual_temperament_changes_live_parameters(self):
        from i1lab.i1_birth_temperament import temperament_for_life
        life, _ = self.born()
        other, _ = self.born()
        self.assertNotEqual(
            temperament_for_life(life.individual_id),
            temperament_for_life(other.individual_id))
        self.assertEqual(
            life.temperament_parameters.mapping_version,
            other.temperament_parameters.mapping_version)
        self.assertNotEqual(
            life.temperament_parameters.exploration_coefficient,
            other.temperament_parameters.exploration_coefficient)
        self.assertEqual(
            dict(life.value_needs.config.weights),
            dict(life.temperament_parameters.body_weights))
        self.assertNotEqual(
            dict(life.value_needs.config.weights),
            dict(other.value_needs.config.weights))

    def test_active_publication_has_one_non_authoritative_owner(self):
        from i1lab.i1_active_value_needs import validate_advisory_rows
        life, _ = self.born()
        active = life.value_needs.active_observed_procedures()
        self.assertEqual(active, [])
        self.assertEqual(validate_advisory_rows(active), None)
        with self.assertRaises(ValueError):
            validate_advisory_rows([{"safety_certified": True}])
        history = life.slow_history.read_committed()
        self.assertIn("forms", history)
        self.assertEqual(history["forms"], {})
        self.assertTrue(life.journal.verify())

    def test_uncertainty_is_not_hidden_safety_knowledge(self):
        life, _ = self.born()
        self.assertIsNone(life.stage3.substrate.bench)
        self.assertNotIn("i1_a239_food_first_risk_review",
                         life.compute_budget._config.operation_costs)
        self.assertNotIn("i1_a238_unknown_commitment_review",
                         life.compute_budget._config.operation_costs)
        self.assertTrue(life.journal.verify())


class FullI1(CurrentI1):
    """Additional seeds and horizons. Only included in FULL mode."""

    def test_multiple_independent_lives(self):
        from i1lab.journal import HashChainedJournal
        for offset in range(3):
            with self.subTest(seed=SEED + offset):
                life, path = self.born(
                    life_id="i1:ci:full:" + str(SEED + offset))
                for _ in range(8):
                    result = life.run_step()
                    if result.execution_status != "applied":
                        break
                self.assertTrue(life.journal.verify())
                audit = HashChainedJournal.audit_durable_wal(path)
                self.assertEqual(audit["head_hash"], life.journal.head_hash)


class DeliberateFailures(unittest.TestCase):
    """Only selected with --self-test: CI must reject both failure types."""

    def test_detect_false_assertion(self):
        self.assertEqual(1, 2, "controlled assertion violation")

    def test_detect_exception(self):
        raise RuntimeError("controlled harness exception")


def write_junit(result, elapsed, filename, seed, mode):
    root = ET.Element("testsuite", {
        "name": "i1-" + mode,
        "tests": str(result.testsRun),
        "failures": str(len(result.failures)),
        "errors": str(len(result.errors)),
        "skipped": str(len(result.skipped)),
        "time": str(round(elapsed, 3)),
        "seed": str(seed),
    })
    faults = {test.id(): ("failure", tb) for test, tb in result.failures}
    faults.update({test.id(): ("error", tb) for test, tb in result.errors})
    ignored = {test.id(): reason for test, reason in result.skipped}
    for test in result._observed:
        case = ET.SubElement(root, "testcase", {
            "classname": test.__class__.__name__, "name": test._testMethodName,
        })
        if test.id() in faults:
            kind, text = faults[test.id()]
            ET.SubElement(case, kind, {"message": kind}).text = text
        if test.id() in ignored:
            ET.SubElement(case, "skipped").text = ignored[test.id()]
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


class TrackedResult(unittest.TextTestResult):
    def startTest(self, test):
        self._observed.append(test)
        super().startTest(test)


class TrackedRunner(unittest.TextTestRunner):
    resultclass = TrackedResult

    def _makeResult(self):
        result = super()._makeResult()
        result._observed = []
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--junit", required=True, type=Path)
    parser.add_argument("--self-test", action="store_true",
                        help="deliberate test failures; must return nonzero")
    args = parser.parse_args()
    global SEED
    SEED = args.seed
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(
        DeliberateFailures if args.self_test else (
            FullI1 if args.mode == "full" else CurrentI1))
    started = time.monotonic()
    result = TrackedRunner(verbosity=2).run(suite)
    write_junit(result, time.monotonic() - started, args.junit,
                args.seed, "self-test" if args.self_test else args.mode)
    print("I1 mode=%s seed=%s tests=%s failures=%s errors=%s junit=%s" %
          (args.mode, args.seed, result.testsRun, len(result.failures),
           len(result.errors), args.junit), flush=True)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
