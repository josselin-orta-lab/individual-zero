"""Synthetic-only exact host-compute coverage and control parity tests."""
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_compact_host_operator_coverage as E
from i3.lab import stage2_replay_predictive_negative_control as NEG
from i3.lab.stage2_compact_distress_shadow import (
    CompactPersonalDistressHead, work_envelope)
from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.world import World
from i3.modules.stage2_replay_content_selection import random_content_indices


class CompactHostOperatorCoverageTests(unittest.TestCase):
    def test_existing_adverse_discard_compute_gap_and_new_equal_count_proposal(self):
        # Explicit World construction guard: the audit must only use fake
        # memory-bearing Minds and never retry a closed G0/engineering source.
        with patch.object(World, "__init__",
                          side_effect=AssertionError("World creation forbidden")):
            report = E.audit()
        print("I3_COMPACT_HOST_OPERATION_COVERAGE_RESULT="+json.dumps(
            report, sort_keys=True))
        self.assertEqual(report["synthetic_fixture_cells"], 10)
        self.assertEqual(report["worlds_opened"], 0)
        self.assertEqual(report["scientific_lives"], 0)
        self.assertEqual(report["scientific_verdict"], "NOT_ISSUED")
        self.assertFalse(report["stage2_2_activation"])
        self.assertFalse(report["native_model_tariff_is_full_host_cpu_calibration"])
        self.assertTrue(report["native_model_price_equal_but_host_readout_counts_unequal"])
        self.assertEqual(report["historical_discard_inference_shortfall_per_event"], 1)
        self.assertTrue(report["proposed_balanced_forecast_and_weights_exact"])
        self.assertTrue(report["proposed_balanced_inference_call_counts_equal"])
        self.assertTrue(report["hmac_identity_messages_equal_eligible_memory_count"])
        self.assertEqual(len(report["unmapped_host_operation_coverage_includes"]),4)
        for row in report["rows"]:
            n=row["personal_memory_records"]
            self.assertIn(n,E.SIZES)
            self.assertIn(row["unrelated_map_effect_entries"],E.EXTRA_STATES)
            self.assertEqual(row["selector_coverage"]["priority_key_visits"],n)
            self.assertEqual(row["selector_coverage"]["hmac_identity_messages"],n)
            self.assertEqual(row["selector_coverage"]["hmac_digest_output_bytes"],32*n)
            self.assertGreater(row["selector_coverage"]["hmac_message_payload_bytes"],n)
            self.assertEqual(row["historical_predict_calls"],
                             {"priority":5,"random":5,"discard":4})
            self.assertEqual(row["balanced_predict_calls"],
                             {"priority":5,"random":5,"discard":5})
            self.assertEqual(row["all_three_training_updates"],
                             {"priority":3,"random":3,"discard":3})
            self.assertEqual(row["native_price"]["cycles"],7)
            self.assertEqual(row["native_price"]["replays"],3)
            self.assertEqual(row["native_price"]["memory_items"],4*n+6)
            self.assertGreater(row["external_only_provenance_host_measure"]
                               ["peak_traced_bytes"],0)
            self.assertGreaterEqual(row["external_only_provenance_host_measure"]
                                    ["host_elapsed_ns"],0)
        for n in E.SIZES:
            low, high=(next(row for row in report["rows"]
                            if row["personal_memory_records"]==n
                            and row["unrelated_map_effect_entries"]==extra)
                       for extra in (0,256))
            self.assertEqual(low["native_price"],high["native_price"])
            self.assertEqual(low["balanced_predict_calls"],
                             high["balanced_predict_calls"])
            self.assertEqual(low["selector_coverage"],high["selector_coverage"])

    def test_48_existing_synthetic_personal_histories_keep_exact_forecast(self):
        for trial in range(48):
            source=NEG.synthetic_personal_mind(trial)
            original=E._source_seal(source)
            memory=tuple(source.buffer)
            n=len(memory)
            priority=tuple(sorted(range(n),key=lambda i:-memory[i][0])[:3])
            random=random_content_indices(
                eligible=n,count=3,life_seed=E.SEED+trial,sleep_ordinal=1)
            for mode in E.MODES:
                selected=priority if mode=="priority" else random
                old=CompactPersonalDistressHead(source)
                old_before=old.predict(E.BODY)
                old.apply(memory,selected)
                old_forecast=(old_before if mode=="discard"
                              else old.predict(E.BODY))
                new=CompactPersonalDistressHead(source)
                counter=0
                original_predict=CompactPersonalDistressHead.predict

                def spy(head,body):
                    nonlocal counter
                    counter+=1
                    return original_predict(head,body)

                with patch.object(CompactPersonalDistressHead,"predict",spy):
                    output=E.balanced_refit_forecast(
                        head=new,memory=memory,indices=selected,
                        body=E.BODY,mode=mode)
                self.assertEqual(counter,5)
                self.assertEqual(output["forecast"],old_forecast)
                self.assertTrue(output["posttraining_forecast_computed"])
                self.assertEqual(output["updates"],3)
                self.assertEqual(new.weights,old.weights)
                self.assertEqual(new.trained_indices,old.trained_indices)
            self.assertEqual(E._source_seal(source),original)

    def test_forged_sources_and_bad_modes_fail_before_training(self):
        source=NEG.synthetic_personal_mind(7)
        head=CompactPersonalDistressHead(source)
        memory=tuple(source.buffer)
        with self.assertRaises(ValueError):
            E.balanced_refit_forecast(
                head=head,memory=memory,indices=(0,1,2),
                body=E.BODY,mode="adaptive_magic")
        self.assertEqual(head.training_updates,0)
        with self.assertRaises(PermissionError):
            E.balanced_refit_forecast(
                head=head,memory=memory+((1.,E.BODY,E.BODY,False),),
                indices=(0,1,2),body=E.BODY,mode="priority")
        self.assertEqual(head.training_updates,0)
        with self.assertRaises(ValueError):
            E.balanced_refit_forecast(
                head=head,memory=memory,indices=(0,0,1),
                body=E.BODY,mode="priority")
        self.assertEqual(head.training_updates,0)
        with self.assertRaises(ValueError):
            E.balanced_refit_forecast(
                head=head,memory=memory,indices=(0,1,2),
                body=(float("nan"),60.,50.,90.,80.),mode="priority")
        self.assertEqual(head.training_updates,0)
        with self.assertRaises(TypeError):
            E.balanced_refit_forecast(
                head=source,memory=memory,indices=(0,1,2),
                body=E.BODY,mode="priority")

    def test_failed_body_authorization_cannot_invoke_head(self):
        source=NEG.synthetic_personal_mind(5)
        original=E._source_seal(source)
        for body,action in (
            ((.1,60.,50.,90.,80.),"attendre"),
            ((2.12,60.,50.,90.,80.),"se_deplacer"),
            ((70.,60.,50.,90.,.05),"attendre")):
            from i3.lab.stage2_repeated_paid_distress_prequential_engineering import RepeatedPaidWitness
            b=CognitiveBudget(body,BodyLaws())
            witness=RepeatedPaidWitness(mode="discard",seed=E.SEED)
            with patch("i3.lab.stage2_repeated_paid_distress_prequential_engineering."
                       "CompactPersonalDistressHead",
                       side_effect=AssertionError("unfunded learner run")):
                witness.after_choice(source,{"body":body},b,
                                     action,None,CognitiveWork())
            self.assertEqual(witness.report()["unfunded_slots"],1)
            self.assertEqual(b.work,CognitiveWork())
            self.assertEqual(E._source_seal(source),original)


if __name__=="__main__":
    unittest.main()
