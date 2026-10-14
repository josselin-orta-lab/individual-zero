"""GA-08 independent semantic auditor vs correctly rehashed source forgeries.

Uses a short, autonomously chosen, actual Stage12/WorldBody goal execution.
This is a technical regression, not additional scientific population data.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_stage12_issue110_ga08_return_goal_science as experiment

from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import GENESIS_HASH
from lab.stage12_spatial_provenance_audit import audit_stage12_spatial_provenance
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs


def rechain(rows):
    prev = GENESIS_HASH
    for i, row in enumerate(rows):
        row["index"] = i
        row["previous_hash"] = prev
        prev = sha256(
            bytes.fromhex(prev) + canonical_causal_bytes({
                "event_id": row["event_id"],
                "causal_event": row["causal_event"],
            }),
        ).hexdigest()
        row["event_hash"] = prev
    return b"\n".join(canonical_causal_bytes(row) for row in rows)


class RehashedSpatialAuditorTests(unittest.TestCase):
    def test_real_return_to_resource_and_rehash_adversarial_cases(self):
        # MAX_STEPS is a technical fixture bound only. It cannot feed a
        # recommendation or label to the autonomous command selector.
        with TemporaryDirectory() as temp, patch.object(
            experiment, "MAX_STEPS", 6,
        ):
            row = experiment.run_life(Path(temp), label="water_spatial")
            self.assertIsNone(row["failure"], row["failure"])
            self.assertIsNone(row["audit_error"], row["audit_error"])
            self.assertGreater(row["audits"]["spatial"]["preregistered"], 0)
            self.assertGreater(row["audits"]["spatial"]["verified_successes"], 0)
            self.assertGreater(row["audits"]["spatial"]["judgements_self"], 0)
            raw = (Path(temp) / "canonical.jsonl").read_bytes()
            clean = audit_stage12_spatial_provenance(raw)
            self.assertGreaterEqual(clean.verified_successes, 1)
            audit_stage12_goal_progress(raw)
            audit_stage12_first_person_agency(raw)
            audit_stage12_attribution_pairs(raw)
            rows = [json.loads(line) for line in raw.splitlines()]
            pre = next(
                i for i, r in enumerate(rows)
                if r["causal_event"]["kind"] ==
                   "stage12_goal_progress_preregistered"
                and r["causal_event"]["data"].get("contract_version", "").endswith("-ga08-v1")
            )
            intent = rows[pre]["causal_event"]
            sent = intent["t_monde"]
            attempt = intent["attempt_ref"]
            captures = [
                i for i, r in enumerate(rows)
                if r["causal_event"]["kind"] == "perceptual_capture"
                and r["causal_event"]["t_monde"] == sent
                and r["causal_event"]["attempt_ref"] == attempt
            ]
            self.assertEqual(len(captures), 1)
            command_index = next(
                i for i, r in enumerate(rows)
                if r["causal_event"]["kind"] == "command_experienced"
                and r["causal_event"]["t_monde"] == sent
            )
            cases = []
            fake = deepcopy(rows)
            fake[pre]["causal_event"]["data"]["target"] = [7, 2]
            cases.append(("substituted_target", fake))
            fake = deepcopy(rows)
            fake[pre]["causal_event"]["data"]["direction"] = "west"
            cases.append(("substituted_direction", fake))
            fake = deepcopy(rows)
            cell = next(c for c in fake[captures[0]]["causal_event"]["data"]["agency_visible_adjacent"]
                        if c["direction"] == "south")
            cell["passable"] = False
            cases.append(("rehashed_obstacle", fake))
            fake = deepcopy(rows)
            fake.pop(command_index)
            cases.append(("omitted_action_control_receipt", fake))
            fake = deepcopy(rows)
            fake[pre]["causal_event"]["data"]["destination_passable_before"] = False
            cases.append(("forged_original_blockage", fake))
            fake = deepcopy(rows)
            fake[pre]["causal_event"]["data"]["life_id"] = "other_dead_individual"
            cases.append(("foreign_identity", fake))
            for name, distorted in cases:
                with self.subTest(name=name):
                    rebuilt = rechain(distorted)
                    # The pure hash chain is valid for every mutation.
                    # Deleting an executed-command source also violates
                    # the older autobiographical audit, which is an even
                    # earlier legitimate rejection than GA-08 semantics.
                    if name == "omitted_action_control_receipt":
                        with self.assertRaisesRegex(
                            ValueError, "missing/future autobiographical source",
                        ):
                            audit_export_bytes(rebuilt)
                    else:
                        self.assertGreater(audit_export_bytes(rebuilt).occurrences, 0)
                    with self.assertRaises(ValueError):
                        audit_stage12_spatial_provenance(rebuilt)


if __name__ == "__main__":
    unittest.main()
