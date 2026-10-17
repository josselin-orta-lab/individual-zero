"""Adversarial original mortal first-person / UC tests for A2.30-ZQ.

Tests REAUDIT the single 24-life produced cohort from the preceding workflow
step. They NEVER execute a new I0 birth or physical command.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_b_a230zq_autonomous_hidden_motor import (
    CANDIDATE_FATAL_POSITION, EXPECTED_LIVES, MAX_WORLD_STEPS, MOTOR,
    PROFILES, LAYOUTS, B_HIDDEN, digest, verify_pairs, score_study,
)
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import HashChainedJournal


class AutonomousMortalityRealLifeAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=Path(os.environ["A230ZQ_OUTPUT"])
        cls.summary=json.loads((cls.folder/"a230zq-summary.json").read_text())
        cls.pairs=json.loads((cls.folder/"a230zq-pairing.json").read_text())
        cls.lives=[]
        for dir in sorted(cls.folder.iterdir()):
            if (dir.is_dir() and
                (dir/"a230zq-life.json").is_file()):
                cls.lives.append(json.loads(
                    (dir/"a230zq-life.json").read_text()
                ))
        cls.by_id={x["birth_id"]:x for x in cls.lives}

    def score(self,lives=None,pairs=None):
        source=self.lives if lives is None else lives
        paired=self.pairs if pairs is None else pairs
        return score_study(deepcopy(source),deepcopy(paired))

    def test_real_24_independent_births_and_aggregate_bounds(self):
        s=self.score()
        self.assertEqual(s["new_independently_born_I0"],24)
        self.assertEqual(s["original_ZB_I0_births_used_as_readonly_initial_refs"],12)
        self.assertEqual(s["maximum_preregistered_autonomous_world_steps"],768)
        self.assertLessEqual(s["real_autonomous_world_steps"],768)
        self.assertEqual(len(self.lives),24)
        self.assertEqual(len(set(self.by_id)),24)
        self.assertEqual(len(self.pairs),12)
        self.assertEqual(sum(x["world_steps"] for x in self.lives),
                         self.summary["real_autonomous_world_steps"])
        self.assertFalse(s["B_food_safety_proven"])
        self.assertFalse(s["hidden_motor_safety_proven"])
        self.assertFalse(s["subjective_attribution_of_cause_of_death_proven"])
        self.assertFalse(s["new_model_transitions_or_I0_cognitive_changes"])
        self.assertEqual(s["issue110_administrative_status"],"CLOSED")
        self.assertEqual(s["scientific_Stage12_status"],"PARTIAL")

    def test_24_original_durable_wals_and_p48_physical_closures(self):
        for life in self.lives:
            stem=self.folder/(
                life["profile"]+"-"+life["layout"]+"-"+
                life["hidden_B_external_only"]+"-"+
                life["ZQ_motor_treatment_external_only"]
            )
            raw=(stem/"canonical.jsonl").read_bytes()
            self.assertEqual(sha256(raw).hexdigest(),life["journal_sha256"])
            audited=audit_export_bytes(
                raw,expected_head=life["journal_head"],
                expected_count=life["journal_count"],
            )
            self.assertEqual(audited.world_steps_closed,life["world_steps"])
            self.assertEqual(
                audited.terminal_deaths,
                int(life["mortal_status"]=="dead"),
            )
            wal=HashChainedJournal.audit_durable_wal(str(stem/"life.wal"))
            self.assertEqual(wal["head_hash"],life["journal_head"])
            self.assertEqual(wal["verified_entries"],life["journal_count"])
            self.assertTrue(life["independent_WAL_P48_dual_agency_audits"])
            self.assertTrue(life["motor_commands_from_original_I0_only"])
            self.assertFalse(life["berry_B_safety_certified"])
            self.assertFalse(life["postterminal_revival"])

    def test_full_firstperson_births_match_control_across_hidden_motor(self):
        for pair in self.pairs:
            a=self.by_id[pair["clear_birth_id"]]
            b=self.by_id[pair["hidden_lethal_birth_id"]]
            self.assertEqual(
                a["initial_accessible_projection"],
                b["initial_accessible_projection"]
            )
            self.assertEqual(
                a["equipment_sha256_A_only"],
                b["equipment_sha256_A_only"],
            )
            self.assertTrue(pair["initial_full_sensory_and_model_parity"])
            self.assertNotEqual(a["birth_id"],b["birth_id"])
            self.assertNotEqual(
                a["world_birth_configuration_external"]["layout_sha256_external_only"],
                b["world_birth_configuration_external"]["layout_sha256_external_only"]
            )

    def test_hidden_zone_never_published_to_subjective_capture(self):
        for life in self.lives:
            self.assertEqual(
                set(life["initial_accessible_projection"]),
                {"schema_version","x","y","body","inventory",
                 "current_resources","current_water_source","adjacent",
                 "known_shelter_here","is_night"}
            )
            for c in life["preaction_commands_with_firstperson_receipts"]:
                perception=c["preaction_firstperson_capture"]
                if perception is None:
                    self.assertEqual(
                        c["preaction_firstperson_receipt_status"],
                        "unavailable_in_canonical_journal"
                    )
                    self.assertIsNone(c["preaction_firstperson_sha256"])
                else:
                    self.assertEqual(
                        c["preaction_firstperson_receipt_status"],"available"
                    )
                    self.assertEqual(digest(perception),
                                     c["preaction_firstperson_sha256"])
                    self.assertTrue(all(
                        "hidden" not in repr(v) and "lethal" not in repr(v)
                        for v in perception["visible_adjacent"]
                    ))
                self.assertFalse(c["lab_chose_or_dispatched_this_primitive"])
                self.assertFalse(c["postdeath_subjective_comparison_generated"])

    def test_hidden_motor_death_is_never_lived_postmortem(self):
        for life in self.lives:
            story=life["preaction_commands_with_firstperson_receipts"]
            self.assertEqual(len(story),life["world_steps"])
            if life["mortal_status"]=="dead":
                final=story[-1]["t_monde"]
                self.assertEqual(final,life["world_steps"])
                self.assertEqual(life["journal_causal_event_kinds"].get(
                    "individual_death_confirmed",0),1)
                self.assertTrue(
                    life["death_receipt_joined_to_final_autonomous_primitive"])
                if life["motor_zone_death_observed"]:
                    self.assertIn("lethal_zone",
                                  life["terminal_causes_external_only"])
                    self.assertEqual(
                        life["operator_hidden_physics_external_only"][
                            "death_external_receipt"]["reasons"],
                        life["terminal_causes_external_only"])
                self.assertNotIn("technical_halt",
                                 life["actual_execution_statuses"])
            else:
                self.assertEqual(life["journal_causal_event_kinds"].get(
                    "individual_death_confirmed",0),0)
            self.assertTrue(life["terminal_only_in_external_causal_journal"])
            self.assertTrue(life["not_promoting_proximal_self_to_distal_death_cause"])

    def test_first_motor_zone_entry_is_actually_autonomous_east(self):
        for life in self.lives:
            entry=life["first_hidden_test_cell_entry_step"]
            if entry is None:continue
            target=life["preaction_commands_with_firstperson_receipts"][entry-1]
            self.assertEqual(target["primitive"],"se_deplacer")
            self.assertEqual(target["parameters"],{"direction":"east"})
            self.assertEqual(
                target["preaction_position_from_physical_chain_external_only"],
                {"x":2,"y":1})
            self.assertIsNotNone(target["preaction_firstperson_capture"])
            self.assertEqual(target["preaction_firstperson_capture"][
                "position"],{"x":2,"y":1})
            self.assertEqual(target["verified_physical_position_after"],
                CANDIDATE_FATAL_POSITION.as_dict())
            if life["ZQ_motor_treatment_external_only"]=="motor_hidden_lethal":
                self.assertTrue(life["motor_zone_death_observed"])
            else:
                self.assertFalse(life["motor_zone_death_observed"])

    def test_UC_is_actual_requested_receipts_not_inferred_per_step(self):
        for life in self.lives:
            self.assertIsInstance(life["actual_accepted_UC_requests_total"],int)
            self.assertIsInstance(life["actual_denied_UC_requests_total"],int)
            self.assertGreaterEqual(life["actual_accepted_UC_requests_total"],0)
            self.assertGreaterEqual(life["actual_denied_UC_requests_total"],0)
            self.assertIsInstance(life["real_UC_receipt_counts"],dict)
        self.assertEqual(self.summary["actual_accepted_UC_requests_total"],
            sum(life["actual_accepted_UC_requests_total"] for life in self.lives))
        self.assertEqual(self.summary["actual_denied_UC_requests_total"],
            sum(life["actual_denied_UC_requests_total"] for life in self.lives))

    def test_counterfactual_is_a_new_birth_not_a_same_person_restore(self):
        for pair in self.pairs:
            self.assertTrue(pair["distinct_births_not_personally_restored_counterfactual"])
            self.assertTrue(pair["not_subjectively_attributing_exogenous_death_to_self"])

    def test_falsified_external_safety_claim_rejected(self):
        lives=deepcopy(self.lives)
        lives[0]["berry_B_safety_certified"]=True
        with self.assertRaisesRegex(ValueError,"scientific claim"):
            self.score(lives=lives)

    def test_fake_oracle_feedback_rejected(self):
        lives=deepcopy(self.lives)
        lives[0]["no_world_truth_or_oracle_data_to_I0"]=False
        with self.assertRaisesRegex(ValueError,"scientific claim"):
            self.score(lives=lives)

    def test_forced_I0_command_label_rejected(self):
        lives=deepcopy(self.lives)
        lives[0]["no_forced_commands"]=False
        with self.assertRaisesRegex(ValueError,"scientific claim"):
            self.score(lives=lives)

    def test_postterminal_revival_claim_rejected(self):
        lives=deepcopy(self.lives)
        lives[0]["postterminal_revival"]=True
        with self.assertRaisesRegex(ValueError,"scientific claim"):
            self.score(lives=lives)

    def test_reused_birth_identity_rejected(self):
        lives=deepcopy(self.lives)
        lives[1]["birth_id"]=lives[0]["birth_id"]
        with self.assertRaisesRegex(ValueError,"duplicate mortal I0 identity"):
            self.score(lives=lives)

    def test_missing_original_life_rejected(self):
        lives=deepcopy(self.lives[:-1])
        with self.assertRaisesRegex(ValueError,"independently preregistered births"):
            self.score(lives=lives)

    def test_hazard_death_fabricated_in_motor_clear_rejected(self):
        lives=deepcopy(self.lives)
        target=next(x for x in lives if
                    x["ZQ_motor_treatment_external_only"]=="motor_clear")
        target["motor_zone_death_observed"]=True
        with self.assertRaisesRegex(ValueError,"invented motor-zone mortality|zone deaths exceed physical terminal births"):
            self.score(lives=lives)

    def test_accepted_UC_negative_not_accepted(self):
        lives=deepcopy(self.lives)
        lives[0]["mortal_status"]="technically_halted"
        with self.assertRaisesRegex(ValueError,"scientific claim"):
            self.score(lives=lives)

    def test_original_durable_canonical_bitflip_detected(self):
        life=self.lives[0]
        stem=self.folder/(
            life["profile"]+"-"+life["layout"]+"-"+
            life["hidden_B_external_only"]+"-"+
            life["ZQ_motor_treatment_external_only"]
        )
        original=(stem/"canonical.jsonl").read_bytes()
        corrupt=original[:-3]+b"XXX"
        with self.assertRaises(Exception):
            audit_export_bytes(corrupt,
                expected_head=life["journal_head"],
                expected_count=life["journal_count"])

    def test_counting_lived_proximal_as_death_causation_rejected(self):
        lives=deepcopy(self.lives)
        lives[0]["not_promoting_proximal_self_to_distal_death_cause"]=False
        with self.assertRaisesRegex(ValueError,"scientific claim"):
            self.score(lives=lives)

    def test_no_normative_or_cognitive_mutation_in_runner(self):
        source=(Path(__file__).resolve().parents[1]/
                "scripts/run_stage12_issue110_b_a230zq_autonomous_hidden_motor.py"
            ).read_text()
        self.assertNotIn("life.stage3.world.apply(",source)
        self.assertNotIn("life.stage3.substrate.world.apply(",source)
        self.assertNotIn("life.motors.send(",source)
        self.assertNotIn("Stage12Runtime.run_step =",source)
        self.assertNotIn("Oracle(",source)


if __name__=="__main__":
    unittest.main()
