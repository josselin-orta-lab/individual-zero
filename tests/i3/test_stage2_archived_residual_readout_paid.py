"""Source-locked, no-World, modeled-paid prior-error laboratory readouts."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_archived_residual_readout_paid as E
from i3.modules.world import World


class ArchivedResidualModelPaidReadoutTests(unittest.TestCase):
    def test_all_frozen_320_events_two_arms_and_model_parity_no_world(self):
        with patch.object(World, "__init__",
                          side_effect=AssertionError("World not permitted")), patch(
                              "i3.runtime.life.run_life",
                              side_effect=AssertionError("new life not permitted")):
            result = E.audit()
        compact = {k: v for k, v in result.items() if k != "full_rows"}
        print("I3_ARCHIVED_RESIDUAL_MODEL_PAID_READOUT="
              +json.dumps(compact, sort_keys=True, separators=(",", ":")))
        self.assertEqual(result["status"],
                         "ARCHIVED_RESIDUAL_MODEL_PAID_READOUT_PASS")
        self.assertEqual(result["assigned_events"], 320)
        self.assertEqual(result["arm_attempts"], 640)
        self.assertEqual(result["funded_events"]+result["denied_events"],320)
        self.assertEqual(result["zero_history_events"],4)
        self.assertEqual(result["original_source_sha256"],E.SOURCE_DIGEST)
        self.assertEqual(result["derivative_source_sha256"],E.DERIVATIVE_SHA)
        self.assertEqual(len(result["sidecar_checksum"]),64)
        self.assertEqual(len(result["deterministic_aggregate_sha256"]),64)
        self.assertEqual(result["worlds_opened"],0)
        self.assertEqual(result["scientific_lives"],0)
        self.assertEqual(result["scientific_verdict"],"NOT_ISSUED")
        self.assertTrue(result["no_action_mediation_claim"])
        self.assertFalse(result["actual_native_World_debit"])
        self.assertFalse(result["full_host_CPU_price_calibrated"])
        self.assertEqual(len(result["full_rows"]),320)
        for row in result["full_rows"]:
            self.assertEqual(row["scan_visits"],
                             row["prior_records"] if row["status"] ==
                             "MODEL_AUTHORIZED_READOUT" else 0)
            if row["status"]=="MODEL_AUTHORIZED_READOUT":
                self.assertEqual(row["visible_risk"],row["computed_discarded_risk"])
            else:
                self.assertIsNone(row["visible_risk"])
                self.assertIsNone(row["computed_discarded_risk"])

    def test_no_optional_history_scan_before_failed_funding(self):
        # Preserve every unfunded case, including energy and vigilance.
        from i3.modules.body import BodyLaws
        for body in ((0.01,60.,60.,90.,80.),(70.,60.,60.,90.,0.01)):
            with self.subTest(body=body), patch.object(
                    E, "_read_prior",
                    side_effect=AssertionError("unfunded history read")):
                for mode in E.MODES:
                    x = E._attempt((("dormir",4.0),),action="attendre",
                                   body_after_native_choice=body,mode=mode)
                    self.assertEqual(x["status"],"DENIED_BEFORE_HISTORY_READ")
                    self.assertEqual(x["scan_visits"],0)
                    self.assertIsNone(x["observer_visible_action_risk"])
                    self.assertEqual(x["model_work"],{
                        "cycles":0,"simulated_steps":0,
                        "memory_items":0,"replays":0})

    def test_real_work_in_both_arms_visible_and_discarded(self):
        body=(70.,60.,60.,90.,80.)
        previous=(("boire",2.),("dormir",4.),("boire",8.))
        actual=E._read_prior
        calls=[]
        def observe(items, action):
            calls.append((tuple(items), action))
            return actual(items, action)
        with patch.object(E,"_read_prior",side_effect=observe):
            left=E._attempt(previous,action="boire",
                            body_after_native_choice=body,mode="VISIBLE")
            right=E._attempt(previous,action="boire",
                             body_after_native_choice=body,mode="PAID_DISCARD")
        self.assertEqual(len(calls),2)
        self.assertEqual(left["scan_visits"],3)
        self.assertEqual(right["scan_visits"],3)
        self.assertEqual(left["model_work"],right["model_work"])
        self.assertEqual(left["modeled_energy"],right["modeled_energy"])
        self.assertEqual(left["modeled_vigilance"],right["modeled_vigilance"])
        self.assertEqual(left["observer_visible_action_risk"],
                         right["internal_computed_action_risk"])
        self.assertIsNone(right["observer_visible_action_risk"])
        self.assertTrue(right["computed_but_discarded"])

    def test_past_only_mean_before_current_or_future_target(self):
        earlier=(("boire",2.),("dormir",4.),("boire",8.))
        frozen=E._read_prior(earlier,"boire")
        self.assertAlmostEqual(frozen["pooled_risk"],14./3)
        self.assertAlmostEqual(frozen["action_risk"],(10.+14./3)/3)
        self.assertEqual(frozen["same_action_count"],2)
        # The current event's outcome is neither an argument nor included
        # in prior records before this snapshot is made.
        self.assertEqual(frozen,E._read_prior(earlier,"boire"))
        self.assertEqual(E._read_prior((), "attendre")["scan_visits"],0)

    def test_forged_original_body_cost_or_history_rejected(self):
        src=json.loads(E.DATASET.read_text(encoding="utf-8"))
        side=json.loads(E.SIDECAR.read_text(encoding="utf-8"))
        for kind in ("source","identity","cost","missing","seal","body"):
            bad=deepcopy(side)
            if kind=="source":
                bad["source_aggregate_sha256"]="0"*64
            elif kind=="identity":
                bad["worlds"][0]["seed"] += 1
            elif kind=="cost":
                bad["worlds"][0]["events"][0]["world_decision_bill"]["energy"]["paid"]=-1
            elif kind=="missing":
                bad["worlds"][0]["events"].pop()
            elif kind=="seal":
                bad["worlds"][0]["events"][0]["preoutcome_forecast_sha256"]="0"*64
            elif kind=="body":
                bad["worlds"][0]["events"][0]["body_before"][0]=120.
            with self.subTest(kind=kind):
                with self.assertRaises(ValueError):
                    E.reduce_sources(src,bad)

    def test_source_and_receipts_are_read_only_and_deterministic(self):
        before=(E.DATASET.read_bytes(),E.SIDECAR.read_bytes())
        a,b=E.audit(),E.audit()
        self.assertEqual(a,b)
        self.assertEqual(before,(E.DATASET.read_bytes(),E.SIDECAR.read_bytes()))


if __name__ == "__main__":
    unittest.main()
