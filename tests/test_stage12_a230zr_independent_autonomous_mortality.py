"""Independent ZR falsification tests. Original ZQ/ZB CI archives are READ ONLY.

No new I0 births, no run_step, no physical action or simulator search.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230zr_autonomous_mortality import (
    ZQ_SUMMARY_SHA,PAIR_SHA,load_one,load_sources,
    verify_12_original_birth_roots,verify_original_life,
    review_source,validate_visible_state,
)
from lab.independent_journal_audit import audit_export_bytes


class IndependentZQAutonomousMortalityReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots={
            "zq311":Path(os.environ["A230ZR_ZQ311"]),
            "zq312":Path(os.environ["A230ZR_ZQ312"]),
            "zb311":Path(os.environ["A230ZR_ZB311"]),
            "zb312":Path(os.environ["A230ZR_ZB312"]),
        }
        cls.source,cls.zb=load_sources(
            cls.roots["zq311"],cls.roots["zq312"],
            cls.roots["zb311"],cls.roots["zb312"],
        )
        cls.old=verify_12_original_birth_roots(cls.zb)
        cls.all311=[
            (p.parent,json.loads(p.read_bytes()))
            for p in sorted(cls.roots["zq311"].rglob("a230zq-life.json"))
        ]
        cls.deceased=next((p,l) for p,l in cls.all311
                          if l["mortal_status"]=="dead")
        cls.survivor=next((p,l) for p,l in cls.all311
                          if l["mortal_status"]=="experiment_stopped")

    def original_review(self,version="3.11"):
        summary,pairs,path=self.source[version]
        return review_source(path,summary,pairs,self.old)

    def audit_life(self,folder,life):
        return verify_original_life(
            folder,deepcopy(life),self.old
        )

    def test_two_original_python_sources_and_expected_archive_counts(self):
        for version in ("3.11","3.12"):
            rows,self_consistent,paired=self.original_review(version)
            self.assertEqual(rows["births"],24)
            self.assertEqual(rows["real_autonomous_steps"],408)
            self.assertEqual(rows["terminal_deaths"],12)
            self.assertEqual(rows["firstperson_invisible_motor_deaths"],12)
            self.assertEqual(rows["paired_hazard_contrasts"],12)
            self.assertEqual(rows["motor_east_actions"],274)
            self.assertEqual(rows["B_collections"],0)
            self.assertEqual(rows["B_eats"],0)
            self.assertEqual(rows["stage6_actual_searches"],208)
            self.assertEqual(rows["accepted_UC_requests"],7954)
            self.assertEqual(rows["refused_UC_requests"],0)
            self.assertEqual(rows["dual_scope_judgements"],20)
            self.assertEqual(rows["proximal_self"],12)
            self.assertEqual(rows["proximal_unknown"],8)
            self.assertEqual(rows["genuine_missing_firstperson_capture_steps"],46)
            self.assertEqual(len(self_consistent),24)
            self.assertEqual(len(paired),12)
            self.assertTrue(all(
                r["command_and_firstperson_parity_through_second_move"]
                for r in paired
            ))

    def test_known_source_sha_originals(self):
        for v in ("3.11","3.12"):
            summary,pairs,path=self.source[v]
            self.assertEqual(
                load_one(path,"a230zq-summary.json",ZQ_SUMMARY_SHA[v]),
                summary
            )
            self.assertEqual(
                load_one(path,"a230zq-pairing.json",PAIR_SHA),pairs
            )

    def test_full_visible_state_rejects_hidden_cause_in_sensation(self):
        hidden=deepcopy(self.deceased[1]["initial_accessible_projection"])
        hidden["hidden_lethal_zone_external_only"]=True
        with self.assertRaisesRegex(ValueError,"hidden"):
            validate_visible_state(hidden)

    def test_falsified_original_sha_rejected(self):
        raw=next(self.roots["zq311"].rglob("a230zq-summary.json")).read_bytes()
        with TemporaryDirectory(prefix="zr-hash-negative-") as p:
            fake=Path(p)/"a230zq-summary.json"
            fake.write_bytes(raw+b"\n")
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                load_one(p,"a230zq-summary.json",ZQ_SUMMARY_SHA["3.11"])

    def test_renamed_birth_cannot_reuse_historical_i0(self):
        directory,life=self.deceased
        changed=deepcopy(life)
        historical=self.old[(
            changed["profile"],changed["layout"],
            changed["hidden_B_external_only"]
        )]["historical_birth_id"]
        changed["birth_id"]=historical
        with self.assertRaisesRegex(ValueError,"historical|birth"):
            self.audit_life(directory,changed)

    def test_injected_false_safety_claim_rejected(self):
        directory,life=self.survivor
        changed=deepcopy(life)
        changed["berry_B_safety_certified"]=True
        with self.assertRaisesRegex(ValueError,"autonomous mortal birth"):
            self.audit_life(directory,changed)

    def test_external_death_reason_cannot_be_erased(self):
        directory,life=self.deceased
        changed=deepcopy(life)
        changed["terminal_causes_external_only"]=["voluntary_choice"]
        with self.assertRaisesRegex(ValueError,"external death reason"):
            self.audit_life(directory,changed)

    def test_missing_firstperson_capture_cannot_be_filled_from_physics(self):
        directory,life=self.survivor
        changed=deepcopy(life)
        row=next(x for x in changed[
            "preaction_commands_with_firstperson_receipts"
        ] if x["preaction_firstperson_capture"] is None)
        row["preaction_firstperson_capture"]={
            "position":row[
                "preaction_position_from_physical_chain_external_only"
            ],
            "visible_adjacent":[],
        }
        with self.assertRaisesRegex(ValueError,"subjective sensation"):
            self.audit_life(directory,changed)

    def test_forged_lived_motor_command_rejected(self):
        directory,life=self.deceased
        changed=deepcopy(life)
        changed["preaction_commands_with_firstperson_receipts"][1][
            "parameters"]={"direction":"west"}
        with self.assertRaisesRegex(ValueError,"subjective sensation"):
            self.audit_life(directory,changed)

    def test_forged_uc_charge_rejected_by_raw_receipt_count(self):
        directory,life=self.survivor
        changed=deepcopy(life)
        changed["actual_accepted_UC_requests_total"]+=1
        with self.assertRaisesRegex(ValueError,"UC use"):
            self.audit_life(directory,changed)

    def test_forged_stage6_plan_count_rejected(self):
        directory,life=self.survivor
        changed=deepcopy(life)
        changed["stage6_searches"]+=5
        with self.assertRaisesRegex(ValueError,"planning/agency"):
            self.audit_life(directory,changed)

    def test_terminal_individual_must_have_wal_and_no_revival(self):
        directory,life=self.deceased
        report=self.audit_life(directory,life)
        self.assertEqual(report["world_steps"],2)
        self.assertEqual(report["terminal_reason_external"],["lethal_zone"])
        self.assertEqual(report["first_motor_hazard_cell_entry"],2)
        self.assertEqual(report["real_dual_scope_outcomes"],0)
        self.assertEqual(report["real_proximal_self"],0)
        self.assertEqual(report["real_proximal_unknown"],0)
        with TemporaryDirectory(prefix="zr-no-wal-") as p:
            # Copy only canonical + summary, not the WAL. Fail closed.
            for file in ("canonical.jsonl","a230zq-life.json"):
                (Path(p)/file).write_bytes((directory/file).read_bytes())
            with self.assertRaisesRegex(ValueError,"WAL"):
                self.audit_life(Path(p),life)

    def test_forged_pair_survival_contrast_rejected(self):
        summary,pairs,path=self.source["3.11"]
        bad=deepcopy(pairs)
        bad[0]["physical_survival_contrast_established"]=False
        with self.assertRaisesRegex(ValueError,"pair"):
            review_source(path,summary,bad,self.old)

    def test_canonical_bitflip_is_detected(self):
        directory,life=self.deceased
        raw=(directory/"canonical.jsonl").read_bytes()
        fake=raw[:-4]+b"FAKE"
        with self.assertRaises(Exception):
            audit_export_bytes(
                fake,expected_head=life["journal_head"],
                expected_count=life["journal_count"],
            )

    def test_source_does_not_execute_new_physics_or_import_zq(self):
        text_source=(
            Path(__file__).resolve().parents[1]/
            "scripts/audit_stage12_issue110_b_a230zr_autonomous_mortality.py"
        ).read_text()
        self.assertNotIn("run_stage12_issue110_b_a230zq_autonomous_hidden_motor",text_source)
        self.assertNotIn("from lab.world import",text_source)
        self.assertNotIn("from i0.equipment import",text_source)
        self.assertNotIn("Stage12Runtime(",text_source)
        self.assertNotIn("WorldBody(",text_source)
        self.assertNotIn("SimulatorPlanner(",text_source)
        self.assertNotIn(".run_step(",text_source)


if __name__=="__main__":
    unittest.main()
