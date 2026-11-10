"""Pure software falsifier of full-Mind copy and compact predictor parity."""
import unittest
from copy import deepcopy
from collections import deque
from math import isfinite

from i3.lab import stage2_compact_shadow_cost_audit as AUDIT
from i3.lab import stage2_replay_predictive_negative_control as NEG
from i3.lab import stage2_replay_content_local as LOCAL
from i3.lab.stage2_personal_distress_forecast_shadow import PersonalDistressHead
from i3.lab.stage2_compact_distress_shadow import (
    CompactPersonalDistressHead, work_envelope, preauthorize)
from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost
from i3.modules.stage2_replay_content_selection import random_content_indices


class CompactDistressCostTests(unittest.TestCase):
    def test_48_existing_synthetic_cases_priority_random_zero_and_terminal_exact(self):
        for trial in range(48):
            source = NEG.synthetic_personal_mind(trial)
            old = NEG._mind_seal(source)
            memory = tuple(source.buffer)
            priority = tuple(sorted(range(len(memory)),
                                    key=lambda i: -memory[i][0])[:3])
            random = random_content_indices(
                eligible=len(memory), count=3,
                life_seed=LOCAL.MIND_SEED_START+trial,
                sleep_ordinal=trial+1)
            for selection in ((), priority, random):
                a, b = PersonalDistressHead(source), CompactPersonalDistressHead(source)
                a.apply(memory, selection)
                b.apply(memory, selection)
                self.assertEqual(a.weights, b.weights)
                self.assertEqual(a.trained_indices, b.trained_indices)
                self.assertEqual(a.training_updates, b.training_updates)
                for body in (LOCAL.BODY, AUDIT.BODY):
                    self.assertEqual(a.predict(body), b.predict(body))
                    for terminal in (False, True):
                        self.assertEqual(
                            a.target_from_actual_outcome(body, terminal),
                            b.target_from_actual_outcome(body, terminal))
            self.assertEqual(old, NEG._mind_seal(source))

    def test_unchanged_forecast_when_only_unrelated_spatial_effects_vary(self):
        for n in (6, 12, 32, 128, 512):
            a, b = AUDIT.fixture(n, 0), AUDIT.fixture(n, 256)
            old_a, old_b = NEG._mind_seal(a), NEG._mind_seal(b)
            h_a, h_b = CompactPersonalDistressHead(a), CompactPersonalDistressHead(b)
            self.assertEqual(h_a._eligible_records,h_b._eligible_records)
            indexes=(0,1,2)
            h_a.apply(tuple(a.buffer),indexes)
            h_b.apply(tuple(b.buffer),indexes)
            self.assertEqual(h_a.weights,h_b.weights)
            self.assertEqual(h_a.predict(AUDIT.BODY),h_b.predict(AUDIT.BODY))
            self.assertEqual(old_a,NEG._mind_seal(a))
            self.assertEqual(old_b,NEG._mind_seal(b))
            self.assertFalse(hasattr(h_b,"map"))
            self.assertFalse(hasattr(h_b,"hist"))
            self.assertFalse(hasattr(h_b,"effects"))
            self.assertFalse(hasattr(h_b,"rng"))
            self.assertFalse(hasattr(h_b,"values"))

    def test_fail_closed_on_future_records_duplicate_indices_and_invalid_bodies(self):
        source=NEG.synthetic_personal_mind(7)
        head=CompactPersonalDistressHead(source)
        memory=tuple(source.buffer)
        with self.assertRaises(PermissionError):
            head.apply(memory+((0.,AUDIT.BODY,AUDIT.BODY,False),),(0,))
        for selection in ((0,0),(-1,),(True,),(999,)):
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                head.apply(memory,selection)
        bad=list(memory)
        bad[1]=(0.,AUDIT.BODY,(float("nan"),)*5,False)
        with self.assertRaises(PermissionError):
            head.apply(tuple(bad),(1,))
        with self.assertRaises(ValueError):
            head.predict((0.,0.,float("nan"),0.,0.))
        with self.assertRaises(TypeError):
            head.target_from_actual_outcome(AUDIT.BODY,1)
        head.apply(memory,(0,1,2))
        with self.assertRaises(ValueError):
            head.apply(memory,(0,))
        self.assertEqual(head.training_updates,3)
        self.assertEqual(head.trained_indices,(0,1,2))

    def test_predecision_payment_refusal_is_atomic_and_reserves_motor(self):
        tariff=work_envelope(12,3)
        self.assertEqual(tariff,CognitiveWork(cycles=7,memory_items=54,replays=3))
        e,v=cognitive_cost(BodyLaws(),tariff)
        self.assertTrue(e>0 and v>0)
        for body,action in (
            ((e/2,65.,55.,90.,80.),"attendre"),
            ((2. + e/2,65.,55.,90.,80.),"se_deplacer"),
            ((60.,65.,55.,90.,v/2),"attendre")):
            b=CognitiveBudget(body,BodyLaws())
            self.assertFalse(preauthorize(b,n=12,k=3,action=action))
            self.assertEqual(b.work,CognitiveWork())
            self.assertEqual(b.remaining,body)
        b=CognitiveBudget((80.,65.,55.,90.,80.),BodyLaws())
        self.assertTrue(preauthorize(b,n=12,k=3,action="se_deplacer"))
        self.assertEqual(b.work,tariff)
        self.assertAlmostEqual(80.-b.remaining[0],e)
        self.assertAlmostEqual(80.-b.remaining[4],v)

    def test_model_work_bounds_and_no_free_controls(self):
        for bad in ((5,3),(513,3),(12,17),(12,13),(-1,0),(12,True),(True,0)):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                work_envelope(*bad)
        for n in (6,12,32,128,512):
            work=work_envelope(n,3)
            self.assertEqual(work.memory_items,4*n+6)
            self.assertEqual(work.replays,3)
            self.assertEqual(work.cycles,7)
        b=CognitiveBudget((80.,60.,60.,90.,80.),BodyLaws())
        with self.assertRaises(ValueError):
            preauthorize(b,n=12,k=3,action="invented_action")
        self.assertEqual(b.work,CognitiveWork())

    def test_runtime_measurement_is_exploratory_and_defect_is_falsifiable(self):
        result=AUDIT.audit()
        print("I3_COMPACT_SHADOW_COST_FALSIFIER="+__import__("json").dumps(result,sort_keys=True))
        self.assertEqual(len(result["rows"]),10)
        self.assertTrue(result["all_compact_predictions_exact_equal"])
        self.assertTrue(result["structural_full_copy_defect_at_12_and_512"])
        self.assertEqual(result["worlds_opened"],0)
        self.assertEqual(result["scientific_lives"],0)
        self.assertEqual(result["scientific_verdict"],"NOT_ISSUED")
        self.assertFalse(result["stage2_2_approved"])
        self.assertTrue(result["host_timing_is_not_organism_energy"])
        self.assertTrue(result["tariff_is_operator_category_proposal_not_cpu_calibration"])
        for row in result["rows"]:
            self.assertTrue(row["same_forecast_training_and_memory_selection"])
            self.assertGreater(row["legacy_median_peak_bytes"],0)
            self.assertGreater(row["compact_median_peak_bytes"],0)
            self.assertGreater(row["compact_provisional_energy"],0)
            self.assertGreater(row["compact_provisional_vigilance"],0)


if __name__=="__main__":
    unittest.main()
