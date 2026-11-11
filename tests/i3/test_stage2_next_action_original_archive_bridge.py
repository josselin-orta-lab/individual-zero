"""No new World: old 24-pair archive attestation vs detached alternative."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from i3.lab import stage2_next_action_original_archive_bridge as B
from i3.modules.world import World
from i3.modules.mind import Mind


def synthetic_rows():
    """Never evidence. Only fake data to falsify the pure downstream reducer."""
    families = ("stable",)*8 + ("depletion",)*10 + ("pulse",)*6
    rows = []
    for i, family in enumerate(families):
        shared = {
            "pair_id": f"next-decision-{i:06d}",
            "index": 560000+i,
            "family": family, "terminal": "censored",
        }
        rows.append({
            **shared, "policy": B.ORIGINAL.POLICIES[0],
            "next_decision_receipt": None,
        })
        witness = {
            "status": "NO_DIFFERENT_FUNDED_REPLAY",
            "first_fork": None,
        }
        if i < 20:
            # Exactly one fixed DETACHED alternative differs, not a World run.
            priority = "manger" if i == 0 else "attendre"
            living = "collecter" if i == 0 else "attendre"
            same = priority == living
            choice = {
                "priority_action": priority, "priority_param": None,
                "priority_option": "priority-option" if not same else "common",
                "random_action": living, "random_param": None,
                "random_option": "random-option" if not same else "common",
                "same_admitted_action_and_param": same,
                "same_decision_option": same,
                "priority_work": {"cycles": 1, "simulated_steps": 4,
                                  "memory_items": 1, "replays": 0},
                "random_work": {"cycles": 1, "simulated_steps": 4,
                                "memory_items": 1, "replays": 0},
                "random_branch_matches_actual_live_decision_and_work": True,
                "observer_extra_physical_cost": False,
            }
            witness = {
                "status": "FIRST_FORK_AND_NEXT_DECISION_CAPTURED",
                "first_fork": {"next_decision": choice},
            }
        rows.append({
            **shared, "policy": B.ORIGINAL.POLICIES[1],
            "next_decision_receipt": witness,
        })
    return rows


class OldOriginalNextActionBridgeTests(unittest.TestCase):
    def test_old_archive_sha_and_policy_scope_stay_pinned(self):
        self.assertEqual(
            B.ARCHIVE_COMMIT,
            "20ca7efbf7797fa7b1f12983ce68906b754b312c")
        self.assertEqual(B.ORIGINAL.PAIRS, 24)
        self.assertEqual(len(B.ORIGINAL.MANIFEST_SHA), 64)
        self.assertEqual(
            B.ORIGINAL.POLICIES,
            ("p13_replay_gate_v1", "p13_replay_gate_random_content_v1"))
        self.assertEqual(B.SCHEMA.split("/")[1], "v1")

    def test_fake_shape_classifier_is_not_original_attestation(self):
        with patch.object(World, "__init__",
                          side_effect=AssertionError("NO WORLD")), patch(
                         "i3.runtime.life.run_life",
                          side_effect=AssertionError("NO LIVING SOURCE")), patch.object(
                         Mind, "decide",
                         side_effect=AssertionError("NO LIVING ACTION")):
            result = B._classify_verified_rows(synthetic_rows())
        self.assertEqual(result["assigned_original_pairs"], 24)
        self.assertEqual(result["different_funded_replay"], 20)
        self.assertEqual(result["no_different_fork"], 4)
        self.assertEqual(result["living_random_next_claim"], 20)
        self.assertEqual(result["priority_detached_next_claim"], 20)
        self.assertEqual(result["same_detached_priority_and_living_random_action"], 19)
        self.assertEqual(result["different_detached_priority_alternative"], 1)
        self.assertEqual(result["priority_alternative_executed_in_world"], 0)
        self.assertEqual(
            [result["by_family"][f]["assigned"] for f in B.ORIGINAL.FAMILIES],
            [8, 10, 6])
        self.assertNotIn("existing_original_archive_content_verified", result)
        self.assertNotIn("causal_information_benefit", result)

    def test_tampered_original_next_action_assertions_rejected(self):
        source = synthetic_rows()
        choice = source[1]["next_decision_receipt"]["first_fork"]["next_decision"]
        for mutation in (
            lambda x: x.update({"random_branch_matches_actual_live_decision_and_work": False}),
            lambda x: x.update({"observer_extra_physical_cost": True}),
            lambda x: x.update({"same_admitted_action_and_param": True}),
            lambda x: x.update({"same_decision_option": True}),
            lambda x: x.update({"priority_executed_in_world": True}),
            lambda x: x.update({"random_work": {"cycles": -1}}),
            lambda x: x.pop("priority_work"),
            lambda x: x.update({"random_action": []}),
        ):
            mutated = deepcopy(source)
            x = mutated[1]["next_decision_receipt"]["first_fork"]["next_decision"]
            mutation(x)
            with self.subTest(changed=x), self.assertRaises(ValueError):
                B._classify_verified_rows(mutated)
        self.assertIsNotNone(choice)

    def test_denominator_no_fork_and_policy_order_cannot_disappear(self):
        original = synthetic_rows()
        bad = []
        x = deepcopy(original)
        x.pop()
        bad.append(x)
        x = deepcopy(original)
        x[0]["policy"] = B.ORIGINAL.POLICIES[1]
        bad.append(x)
        x = deepcopy(original)
        x[1]["pair_id"] = "replaced-pair"
        bad.append(x)
        x = deepcopy(original)
        x[1]["next_decision_receipt"]["first_fork"] = None
        bad.append(x)
        x = deepcopy(original)
        x[47]["next_decision_receipt"] = {
            "status": "FIRST_FORK_WITHOUT_SUBSEQUENT_LIVE_DECISION",
            "first_fork": {"next_decision": None}}
        bad.append(x)
        x = deepcopy(original)
        x[1]["next_decision_receipt"]["first_fork"]["next_decision"][
            "priority_action"] = "attendre"
        bad.append(x)
        x = deepcopy(original)
        x[1]["family"] = "invented"
        bad.append(x)
        for rows in bad:
            with self.subTest(count=len(rows)), self.assertRaises(ValueError):
                B._classify_verified_rows(rows)

    def test_no_archive_or_forged_original_audit_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                B.audit(tmp)
        # Do not read summary records if archive verifier rejected originals.
        with tempfile.TemporaryDirectory() as tmp, patch.object(
                B.ORIGINAL, "audit",
                side_effect=PermissionError("source sha mismatch")):
            with self.assertRaises(PermissionError):
                B.audit(tmp)

    def test_reduced_row_mutation_during_original_audit_is_not_accepted(self):
        # No actual archive is needed to prove that a changing result cannot
        # be laundered into an authentic post-audit action count.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reduced = root / "REDUCED_ROWS.json"
            reduced.write_text("[]")
            def modify(_):
                reduced.write_text("[ ]")
                return {"status": "READ_ONLY_ALL_ORIGINALS_AND_REDUCTIONS_PASS",
                        "packed_sha_verified": 48,
                        "unpacked_sha_verified": 48,
                        "complete_matched_pairs": 24,
                        "manifest_sha256": B.ORIGINAL.MANIFEST_SHA}
            with patch.object(B.ORIGINAL, "audit", side_effect=modify):
                with self.assertRaisesRegex(ValueError, "changed during"):
                    B.audit(root)


if __name__ == "__main__":
    unittest.main()
