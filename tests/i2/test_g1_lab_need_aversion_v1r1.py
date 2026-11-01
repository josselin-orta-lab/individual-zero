"""Frozen owner-authorized v1-r1 G1-LAB 4x4 factorial, NON-LIVING.

Only this test runs the 16 bounded subjects, 8 captures maximum each.
The test is a deterministic verification repeated by CI Python runtimes,
not 16 independent biological replicates or proof of emergent hunger.
"""
from __future__ import annotations
from dataclasses import asdict
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
from i2.lab.integrated_loop import (  # noqa: E402
    IntegratedLab, LabRefusal, COLLECT, EAT, DRINK, REGIMES,
)
from i2.lab.need_aversion_policy import ARMS, PROTOCOL_BLOB  # noqa: E402

LETTERS = {COLLECT:"C", EAT:"E", DRINK:"D", None:"_"}


def one_shot_factorial():
    cells={}
    with tempfile.TemporaryDirectory(prefix="g1lab-v1r1-one-owner-each-") as root:
        for energy in (17,60):
            for aversion in (0,4):
                name=("L" if energy==17 else "H")+str(aversion)
                arms={}
                for arm in ARMS:
                    path=Path(root)/f"{name}-{arm}.sqlite"
                    lab=IntegratedLab.create(
                        path, life_ref=f"lab:v1r1:{name}:{arm}",
                        genesis_ref=f"lab:v1r1:genesis:{name}:{arm}",
                        learning=True, deltas=REGIMES["stable"],
                        initial_energy=energy, initial_uc=60,
                        resources=12, revisit=False,
                        study_arm=arm, sensory_signal=aversion,
                    )
                    trace=[]
                    failure=None
                    for _ in range(8):
                        try: step=lab.step()
                        except LabRefusal as e:
                            failure=f"{type(e).__name__}: {e}"
                            break
                        trace.append(asdict(step))
                        if step.terminal: break
                    audited=lab.audit()
                    with sqlite3.connect(path) as db:
                        rows=[dict(zip(("seq","action","energy_before","metabolism",
                                        "nutrition","aversion","energy_after"),
                                       row)) for row in db.execute(
                             "SELECT seq,action_ref,before_energy,metabolic_debit,"
                             "nutrition_gain,aversive_signal,energy "
                             "FROM g1_lab_steps ORDER BY seq")]
                        events=[json.loads(r[0]) for r in db.execute(
                            "SELECT event_json FROM events ORDER BY seq")]
                    observed=[x["action"] for x in rows[:3]]
                    exposure=EAT in observed
                    matched=(len(rows)>=4 and observed==[COLLECT,EAT,COLLECT] and
                             EAT in trace[3]["visible"] and failure is None)
                    arms[arm]={
                        "actions":"".join(LETTERS[x["chosen"]] for x in trace),
                        "steps":len(trace),
                        "uc_spent":audited["actual_synthetic_uc_spent"],
                        "final_energy":audited["energy"],
                        "terminal":audited["terminal"],
                        "failure":failure,
                        "capture4_action":LETTERS[trace[3]["chosen"]] if matched else None,
                        "capture4_identifiable":matched,
                        "reason":("MATCHED" if matched else
                                  "NOT_IDENTIFIABLE_NO_EXPOSURE" if not exposure else
                                  "NOT_IDENTIFIABLE_UNMATCHED_PREHISTORY"),
                        "physical_evidence":rows,
                        "captured_valuations":[
                            {v["candidate_ref"]:v["value"] for v in e["advice"]["values"]}
                            if e["advice"] else {} for e in events],
                        "first_person_claims":[e["claim"] for e in events],
                    }
                    assert not audited["m11_authenticated"]
                    assert audited["motor_authority"]=="NONE"
                    assert not audited["birth_authorized"]
                cells[name]=arms
    return {"protocol_blob":PROTOCOL_BLOB,
            "status":"G1_LAB_ONLY_NOT_BORN",
            "claim":"ENGINEERED_MECHANISM_NOT_NATURAL_LEARNING",
            "models":16, "max_captures":128, "cells":cells}


class V1R1Experiment(unittest.TestCase):
    def test_frozen_factorial_no_hidden_provenance_and_measured_all_arms(self):
        report=one_shot_factorial()
        self.assertEqual(set(report["cells"]),{"L0","L4","H0","H4"})
        total=0
        for cell, arms in report["cells"].items():
            self.assertEqual(set(arms),set(ARMS))
            for name, result in arms.items():
                total+=result["steps"]
                self.assertLessEqual(result["steps"],8)
                self.assertGreaterEqual(result["uc_spent"],0)
                self.assertLessEqual(result["uc_spent"],60)
                for i,row in enumerate(result["physical_evidence"]):
                    self.assertEqual(row["energy_after"],
                                     max(0,min(100,row["energy_before"]-
                                                   row["metabolism"]+row["nutrition"])))
                    self.assertEqual(row["aversion"],
                                     (int(cell[-1]) if row["action"]==EAT else 0))
                    if row["action"]!=EAT:
                        self.assertEqual(row["nutrition"],0)
                    else:
                        self.assertEqual(row["nutrition"],8)
                    claim=result["first_person_claims"][i]
                    self.assertIn(
                        f"evidence:lab:body-energy:{row['energy_before']}",
                        claim["subjective_evidence_refs"])
                    if i==0:
                        self.assertNotIn(EAT,claim["capture"]["accessible_semantics"])
                    if i>0:
                        self.assertNotIn(
                            f"evidence:lab:result:{i+1}",
                            claim["subjective_evidence_refs"])
        self.assertLessEqual(total,128)
        # Result publication includes ALL negative, null, and incomplete arms.
        print("I2_G1LAB_V1R1_ONE_SHOT="+json.dumps(report,sort_keys=True))

if __name__=="__main__":
    unittest.main()
