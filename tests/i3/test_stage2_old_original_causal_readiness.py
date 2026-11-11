"""Read-only Stage-2 old-source sufficiency; NO source births or World."""
from pathlib import Path
import gzip
import json
import tempfile
import unittest
from unittest.mock import patch

from i3.lab import stage2_old_original_causal_readiness as R
from i3.modules.world import World


def write_two_originals(root, *, prefix, with_observer):
    root = Path(root)
    originals = root / "originals"
    originals.mkdir(parents=True)
    files = []
    for index in range(2):
        identity = {
            "pair_id": prefix + "000000",
            "policy": R.CONTENT.POLICIES[index],
        }
        life = {
            "terminal": "censored",
            "cognitive_accounting": {"status": "SETTLED_FOR_DECLARED_WORK"},
        }
        if with_observer and index == 1:
            life["observer_next_decision_replay"] = {
                "status": "FIRST_FORK_AND_NEXT_DECISION_CAPTURED",
                "first_fork": {
                    "next_decision": {
                        "random_branch_matches_actual_live_decision_and_work": True,
                        "observer_extra_physical_cost": False,
                        "same_admitted_action_and_param": False,
                    }
                }
            }
        filename = f"life-{index:03d}.json.gz"
        (originals / filename).write_bytes(
            gzip.compress(json.dumps({"identity": identity, "life": life}
                                     ).encode("utf-8")))
        files.append({"file": filename, "identity": identity})
    (originals / "MANIFEST.json").write_text(
        json.dumps({"files": files}), encoding="utf-8")
    return root


class OldSourceCausalReadiness(unittest.TestCase):
    def test_frozen_source_commit_and_manifest_identities(self):
        self.assertEqual(R.EXPECTED_ORIGINALS, 144)
        self.assertEqual(R.CONTENT.PAIRS, 48)
        self.assertEqual(R.NEXT.PAIRS, 24)
        self.assertEqual(len(R.CONTENT_COMMIT), 40)
        self.assertEqual(len(R.NEXT_COMMIT), 40)
        self.assertNotEqual(R.CONTENT_COMMIT, R.NEXT_COMMIT)
        self.assertEqual(
            R.CONTENT.MANIFEST_SHA,
            "75d0b29136d6c872fcf379ae76498d02b7c77989c3f3e337dca42098e5d98a36")
        self.assertEqual(
            R.NEXT.MANIFEST_SHA,
            "53fdea10f56994a9171d274ecc6388a3301128503b98c1572052ee4b780196b5")

    def test_missing_roots_cannot_be_mistaken_for_a_scientific_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                R.audit(root, root)
            with self.assertRaises(FileNotFoundError):
                R.audit(root / "not-content", root / "not-next")

    def test_old_shape_inventory_requires_claimed_observer_and_no_delivery(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = write_two_originals(Path(tmp) / "content",
                                    prefix="content-dev-", with_observer=False)
            n = write_two_originals(Path(tmp) / "next",
                                    prefix="next-decision-", with_observer=True)
            # This private classifier is tested with synthetic source shapes.
            # It is NOT authentication; R.audit() always calls both exact
            # independent byte auditors before invoking this classifier.
            a = R._scan_verified_originals(
                c, count=2, identity_prefix="content-dev-", next_receipt=False)
            b = R._scan_verified_originals(
                n, count=2, identity_prefix="next-decision-", next_receipt=True)
            self.assertEqual(a["old_originals"], 2)
            self.assertEqual(b["old_originals"], 2)
            self.assertEqual(b["historical_next_perception_with_shadow"], 1)
            self.assertEqual(b["detached_alternative_motor_differences"], 1)
            for report in (a, b):
                self.assertEqual(report["new_paid_information_readout_deliveries"], 0)
                self.assertEqual(report["new_equal_paid_visible_discard_pairs"], 0)
                self.assertEqual(
                    report["new_counterfactual_motors_executed_after_same_capture"], 0)
                self.assertEqual(
                    report["new_mediated_post_paid_learning_pair_outcomes"], 0)

    def test_forged_new_delivery_claim_in_historical_original_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_two_originals(Path(tmp) / "originals",
                                       prefix="content-dev-",
                                       with_observer=False)
            path = root / "originals" / "life-001.json.gz"
            payload = json.loads(gzip.decompress(path.read_bytes()))
            payload["life"]["controller_readout_delivery"] = {
                "native_living_choice_verified": True}
            path.write_bytes(gzip.compress(json.dumps(payload).encode()))
            with self.assertRaisesRegex(ValueError, "new experimental delivery"):
                R._scan_verified_originals(
                    root, count=2, identity_prefix="content-dev-",
                    next_receipt=False)

    def test_auditors_run_before_original_shape_interpretation(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
                World, "__init__", side_effect=AssertionError("NO WORLD")):
            root = Path(tmp)
            with patch.object(R.CONTENT, "audit",
                              side_effect=ValueError("bad source manifest")
                              ) as first, patch.object(R.NEXT, "audit") as second, \
                    patch.object(R, "_scan_verified_originals") as scan:
                with self.assertRaisesRegex(ValueError, "bad source manifest"):
                    R.audit(root / "content", root / "next")
                first.assert_called_once()
                second.assert_not_called()
                scan.assert_not_called()

    def test_readonly_archive_cannot_promote_stage_on_fake_auditor_results(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
                World, "__init__", side_effect=AssertionError("NO WORLD")):
            root = Path(tmp)
            a = {
                "status": "READ_ONLY_ALL_ORIGINALS_AND_REDUCTIONS_PASS",
                "source": R.CONTENT.SOURCE,
                "manifest_sha256": R.CONTENT.MANIFEST_SHA,
                "packed_sha_verified": 96, "unpacked_sha_verified": 96,
                "complete_matched_pairs": 48, "no_new_World_or_life": True,
                "iid_attested": False, "scientific_go": False,
                "primary": {
                    "both_survive": 16, "priority_only_survives": 1,
                    "random_content_only_survives": 7,
                },
            }
            b = {
                **a, "source": R.NEXT.SOURCE,
                "manifest_sha256": R.NEXT.MANIFEST_SHA,
                "packed_sha_verified": 48, "unpacked_sha_verified": 48,
                "complete_matched_pairs": 24,
                "primary": {
                    "assigned_pairs": 24,
                    "first_different_funded_memory_fork": 20,
                    "different_next_admitted_action_or_param": 1,
                },
            }
            shape_content = {
                "old_originals": 96,
                "new_paid_information_readout_deliveries": 0,
            }
            shape_next = {
                "old_originals": 48,
                "historical_next_perception_with_shadow": 20,
                "detached_alternative_motor_differences": 1,
                "old_no_fork": 4,
                "new_paid_information_readout_deliveries": 0,
            }
            with patch.object(R.CONTENT, "audit", return_value=a), \
                    patch.object(R.NEXT, "audit", return_value=b), \
                    patch.object(R, "_scan_verified_originals",
                                 side_effect=(shape_content, shape_next)):
                # This is only a classifier unit test on mocks, not a source
                # validity claim. Full authenticity comes from actual old
                # 144 packed/unpacked originals in the separate read-only CI.
                result = R.audit(root / "content", root / "next")
                self.assertEqual(
                    result["eligibility"],
                    "OLD_ORIGINALS_INSUFFICIENT_FOR_PAID_INFORMATION_CAUSAL_TEST")
                self.assertFalse(result["causal_net_information_gain_identifiable"])
                self.assertFalse(result["new_equal_paid_visible_discard_source"])
                self.assertFalse(result["new_action_relevant_paid_information_delivered"])
                self.assertEqual(result["historical_born_lives_reverified"], 144)
                self.assertEqual(result["new_worlds_opened"], 0)
                self.assertEqual(result["new_lives_created"], 0)
                self.assertEqual(result["scientific_verdict"], "NOT_ISSUED")
                self.assertFalse(result["stage2_2_go"])
                self.assertEqual(len(result["aggregate_sha256"]), 64)

    def test_partial_verified_auditor_receipt_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = {
                "status": "READ_ONLY_ALL_ORIGINALS_AND_REDUCTIONS_PASS",
                "source": R.CONTENT.SOURCE,
                "manifest_sha256": R.CONTENT.MANIFEST_SHA,
                "packed_sha_verified": 95, "unpacked_sha_verified": 96,
                "complete_matched_pairs": 48,
                "no_new_World_or_life": True,
                "iid_attested": False, "scientific_go": False,
            }
            with patch.object(R.CONTENT, "audit", return_value=a), \
                    patch.object(R.NEXT, "audit", return_value=a), \
                    patch.object(R, "_scan_verified_originals") as scan:
                with self.assertRaisesRegex(ValueError, "independently authenticate"):
                    R.audit(Path(tmp)/"content", Path(tmp)/"next")
                scan.assert_not_called()


if __name__ == "__main__":
    unittest.main()
