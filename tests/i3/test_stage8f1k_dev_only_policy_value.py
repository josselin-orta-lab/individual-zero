"""F1K development-only tests. NEVER compute K01..K16 reserved heldouts.

The heavy native/cold/adversarial tests run only in the dedicated DEV workflow.
Cheap main-suite smoke verifies SHA pins and denial of premature release.
"""
from __future__ import annotations

from copy import deepcopy
import inspect
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1k_policy_cost_value_prospective as P
from tools import stage8f1k_independent_policy_value_cold_audit as Cold
from tools.stage8f1j_fixed_round_paid_competition import F1JFixedRoundMind


def reseal(report):
    """Even forged, re-signed receipt trees cannot fool independent equations."""
    for row in report["rows"]:
        src=row["source"]
        for step in src["source_steps"]:
            step["receipt_sha256"]=C.digest({
                k:v for k,v in step.items() if k!="receipt_sha256"})
        src["source_receipt_sha256"]=C.digest({
            k:v for k,v in src.items() if k!="source_receipt_sha256"})
        for arm in row["arms"].values():
            for step in arm["steps"]:
                post=step["postaction"]
                post["learning_receipt_sha256"]=C.digest({
                    k:v for k,v in post.items() if k!="learning_receipt_sha256"})
                step["receipt_sha256"]=C.digest({
                    k:v for k,v in step.items() if k!="receipt_sha256"})
            arm["trajectory_sha256"]=C.digest({
                k:v for k,v in arm.items() if k!="trajectory_sha256"})
        row["case_sha256"]=C.digest({
            k:v for k,v in row.items() if k!="case_sha256"})
    report["provenance_sha256"]=C.digest({
        "phase":report["phase"],
        "grid_blob":report["grid_blob_sha"],
        "protocol_blob":report["protocol_blob_sha"],
        "case_receipts":[r["case_sha256"] for r in report["rows"]],
    })


class F1KStaticNoExposure(unittest.TestCase):
    def test_immutable_preregistration_blobs_without_running_a_life(self):
        self.assertEqual(P.PREEXPOSURE_MAIN,
                         "212d656f71ed5f4011c069575f9235b5b11d30fd")
        self.assertEqual(P.git_blob_sha(Path(P.GRID).read_bytes()),
                         P.GRID_BLOB)
        self.assertEqual(P.git_blob_sha(Path(P.PROTOCOL).read_bytes()),
                         P.PROTOCOL_BLOB)
        grid=P.release_grid()
        self.assertEqual(len(grid["origins"]),16)
        self.assertEqual({r["seed"] for r in grid["origins"]},
                         set(range(202611219101,202611219117)))
        self.assertEqual(grid["frozen_prior_results"]["F1I"],
                         "INCONCLUSIVE_COST_GATE")

    def test_two_dev_roots_disjoint_from_all_reserved_k_sources(self):
        dev=P.validate_dev(P.dev_grid())
        science=P.release_grid()  # only READ preregistration, not exposure
        self.assertEqual(dev["phase"],"DEV_ONLY")
        self.assertEqual(dev["final_tick"],9)
        self.assertFalse(
            {r["seed"] for r in dev["origins"]} &
            {r["seed"] for r in science["origins"]})
        self.assertFalse(
            {e["id"] for e in dev["ecologies"]} &
            {e["id"] for e in science["ecologies"]})

    def test_p13_remains_real_original_mind_and_f1j_only_changes_class(self):
        reference=Mind(midpoint(),202611219201,observer_full_competition=True)
        candidate=P.fork_owned_mind(reference,"fixed_round_f1j")
        self.assertIs(type(reference),Mind)
        self.assertIs(type(candidate),F1JFixedRoundMind)
        self.assertEqual(C.seal_mind(reference)["data"]["private"],
                         C.seal_mind(candidate)["data"]["private"])
        self.assertIsNot(reference,candidate)
        self.assertNotIn("run_life(",inspect.getsource(P.produce))
        self.assertEqual(P.ARMS,("reference_p13","reference_sham","fixed_round_f1j"))

    def test_science_cannot_accidentally_run_dev_roots_or_without_release(self):
        with patch.object(P,"new_world",side_effect=AssertionError(
            "forbidden World.step in test")):
            with self.assertRaises(ValueError):
                P.produce(P.dev_grid(),"F1K_HELDOUT_RELEASE")
        with self.assertRaises(ValueError):
            P.validate_dev(P.release_grid())
        self.assertNotIn(P.RELEASE_ENV,os.environ)


@unittest.skipUnless(os.getenv("I3_F1K_DEV_CI")=="1",
                     "F1K native/cold DEV_ONLY tests run only in dedicated job")
class F1KDevNativeAndCold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid=P.dev_grid()
        cls.native=P.produce(cls.grid,"DEV_ONLY")
        cls.cold=Cold.audit(cls.native,cls.grid)

    def test_real_personal_experience_comes_from_born_empty_mind(self):
        self.assertEqual(self.native["origin_count"],2)
        for row in self.native["rows"]:
            self.assertTrue(row["source"]["valid_paid_personal_source"])
            self.assertEqual(len(row["source"]["source_steps"]),4)
            self.assertEqual(row["source"]["genesis"]["mind"]["data"]["class"],
                             "Mind")
            self.assertEqual(Cold.effects(row["source"]["genesis"]["mind"]),{})
            self.assertTrue(Cold.effects(row["source"]["source_tick4_mind"]))
            self.assertTrue(all(s["postaction"]["status"]=="PAID_LEARNED"
                                for s in row["source"]["source_steps"]))

    def test_exact_source_state_before_policy_switch_and_free_native_actions(self):
        for row in self.native["rows"]:
            arms=row["arms"]
            a=arms["reference_p13"]["steps"][0]
            b=arms["fixed_round_f1j"]["steps"][0]
            self.assertEqual(a["before_world"],b["before_world"])
            self.assertEqual(a["before_mind"]["data"]["private"],
                             b["before_mind"]["data"]["private"])
            self.assertEqual(b["before_mind"]["data"]["class"],
                             "F1JFixedRoundMind")
            self.assertEqual(arms["reference_p13"]["steps"],
                             arms["reference_sham"]["steps"])
            for arm in arms.values():
                self.assertTrue(all(s["no_experimental_action_override"]
                                    for s in arm["steps"]))
                self.assertTrue(all(s["readout_mode"]=="full" for s in arm["steps"]))

    def test_cold_verifies_real_two_currency_cost_and_native_physiology(self):
        self.assertEqual(self.cold["cold_verdict"],"DEV_ONLY_NOT_SCIENTIFIC")
        self.assertGreater(self.cold["native_paid_steps_verified"],8)
        self.assertGreater(self.cold["competition_rounds_verified"],0)
        self.assertIsNone(self.native["scientific_verdict"])
        self.assertFalse(self.cold["preexposure_blobs_verified"])
        self.assertEqual(self.cold["F1I_frozen"],"INCONCLUSIVE_COST_GATE")

    def test_forged_and_resigned_real_motor_bill_is_rejected(self):
        bad=deepcopy(self.native)
        x=bad["rows"][0]["arms"]["reference_p13"]["steps"][0]
        x["native_motor"]["cognitive_accounting"]["energy"]["paid"]=0.
        reseal(bad)
        with self.assertRaises(ValueError):
            Cold.audit(bad,self.grid)

    def test_forged_and_resigned_food_stock_is_rejected(self):
        bad=deepcopy(self.native)
        x=bad["rows"][0]["source"]["source_steps"][0]
        x["after_motor_world"]["food_cells"][0][2]+=1
        reseal(bad)
        with self.assertRaises(ValueError):
            Cold.audit(bad,self.grid)

    def test_forged_paid_fixed_round_is_rejected(self):
        bad=deepcopy(self.native)
        found=False
        for row in bad["rows"]:
            for s in row["arms"]["fixed_round_f1j"]["steps"]:
                witness=s["decision_info"].get("observer",{}).get("competition_witness")
                if witness and witness["actual_substantive_round_snapshots"]:
                    item=witness["actual_substantive_round_snapshots"][0]
                    item[next(iter(item))]+=0.42
                    found=True
                    break
            if found:
                break
        self.assertTrue(found,"DEV fixture did not execute substantive F1J evidence rounds")
        reseal(bad)
        with self.assertRaises(ValueError):
            Cold.audit(bad,self.grid)

    def test_forged_p13_early_stop_claim_is_rejected(self):
        bad=deepcopy(self.native)
        found=False
        for row in bad["rows"]:
            for s in row["source"]["source_steps"]:
                witness=s["decision_info"].get("observer",{}).get("competition_witness")
                if witness:
                    witness["paid_competition_cycles"]+=1
                    found=True
                    break
            if found:
                break
        self.assertTrue(found,"DEV fixture has no native P1.3 competition receipt")
        reseal(bad)
        with self.assertRaises(ValueError):
            Cold.audit(bad,self.grid)

    def test_changed_reference_sham_cannot_be_called_neutral(self):
        bad=deepcopy(self.native)
        bad["rows"][0]["arms"]["reference_sham"]["steps"][0]["action"]="manger"
        reseal(bad)
        with self.assertRaises(ValueError):
            Cold.audit(bad,self.grid)


if __name__=="__main__":
    unittest.main()
