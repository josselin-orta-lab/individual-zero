"""Offline journal auditor rejects cryptographically valid missing world evidence.

A forged exported terminal event missing the same fields on both sides of
the comparison must not pass merely because Python considers None == None.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import unittest

from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import Command


def reseal(rows):
    prior = "00" * 32
    for index, row in enumerate(rows):
        row["index"] = index
        row["previous_hash"] = prior
        prior = sha256(
            bytes.fromhex(prior) + canonical_causal_bytes({
                "event_id": row["event_id"], "causal_event": row["causal_event"],
            })
        ).hexdigest()
        row["event_hash"] = prior
    return b"\n".join(canonical_causal_bytes(row) for row in rows)


class IndependentPhysicalReceiptFieldsTests(unittest.TestCase):
    @staticmethod
    def terminal_rows():
        individual = build_stage4_reference_runtime(autonomous_mortal=True)
        individual.world.apply_scenario_event("set_lethal_zone", {
            "position": individual.world.position.as_dict(), "active": True,
        })
        substrate = individual.stage3.substrate
        substrate.open_step()
        assert substrate.execute(Command("attendre")).status == "dead"
        image = individual.journal.canonical_bytes()
        assert audit_export_bytes(image).terminal_deaths == 1
        return [json.loads(line) for line in image.split(b"\n")]

    def test_fully_recorded_physical_death_passes(self):
        rows = self.terminal_rows()
        report = audit_export_bytes(reseal(rows))
        self.assertEqual(report.world_steps_closed, 1)
        self.assertEqual(report.terminal_deaths, 1)

    def test_resealed_terminal_archive_missing_required_physical_receipts_fails(self):
        cases = (
            ("command_digest", ("command_experienced",
                                "individual_death_confirmed"), "command_hash"),
            ("command_primitive", ("command_experienced",), "primitive"),
            ("command_parameters", ("command_experienced",), "parameters"),
            ("final_position", ("world_transition_experienced",
                                "individual_death_confirmed"), "position_after"),
            ("final_body", ("world_transition_experienced",
                            "individual_death_confirmed"), "body_after"),
        )
        authentic = self.terminal_rows()
        for title, kinds, field in cases:
            with self.subTest(forgery=title):
                forged = deepcopy(authentic)
                for row in forged:
                    if row["causal_event"]["kind"] in kinds:
                        row["causal_event"].pop(field, None)
                payload = reseal(forged)
                # The attack recomputes every SHA-256 link, not only the
                # invalid middle record. Semantic receipt checks must fail.
                with self.assertRaisesRegex(ValueError, "provenance|position/body|digest"):
                    audit_export_bytes(payload)


if __name__ == "__main__":
    unittest.main()
