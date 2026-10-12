"""A rehashed archive cannot invent, skip or elevate an operator control."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest

from lab.determinism import canonical_causal_bytes, deterministic_id
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import GENESIS_HASH, HashChainedJournal
from lab.stage12_operator_control_audit import audit_stage12_operator_control


_POLICY = "stage12-independent-operator-test-v1"
_NAMESPACE = "stage12-external-operator-event-v1"


def _append_control(
    journal: HashChainedJournal, *, kind: str, t: int,
    data: dict[str, object], ordinal: int,
) -> None:
    journal.append(
        event_id=deterministic_id(_NAMESPACE, _POLICY, t, kind, ordinal),
        causal_event={
            "emitter": "operator_console", "kind": kind, "t_monde": t,
            "data": data,
        },
    )


def _append_blocked(journal: HashChainedJournal, t: int) -> None:
    attempt = f"blocked-attempt-{t}"
    journal.append(
        event_id=f"opened-{t}",
        causal_event={
            "kind": "step_opened", "emitter": "scheduler",
            "t_monde": t, "attempt_ref": attempt,
        },
    )
    journal.append(
        event_id=f"closed-{t}",
        causal_event={
            "kind": "step_closed", "emitter": "scheduler",
            "t_monde": t, "attempt_ref": attempt,
            "data": {
                "outcome": "blocked", "applied_command_count": 0,
                "world_advance_count": 0,
            },
        },
    )


def _archive(*, cap: int | None = 2, steps: int = 2,
             stop: bool = True, raise_cap: bool = False) -> bytes:
    journal = HashChainedJournal()
    ordinal = 0
    _append_control(
        journal, kind="operator_console_configured", t=0,
        data={"mode": "campaign", "policy_version": _POLICY},
        ordinal=ordinal,
    )
    ordinal += 1
    if cap is not None:
        _append_control(
            journal, kind="operator_step_cap_set", t=0,
            data={
                "maximum_world_steps": cap, "previous_cap": None,
                "policy_version": _POLICY,
            },
            ordinal=ordinal,
        )
        ordinal += 1
    if raise_cap:
        _append_control(
            journal, kind="operator_step_cap_set", t=0,
            data={
                "maximum_world_steps": 3, "previous_cap": cap,
                "policy_version": _POLICY,
            },
            ordinal=ordinal,
        )
        ordinal += 1
    for t in range(1, steps + 1):
        _append_blocked(journal, t)
    if stop:
        _append_control(
            journal, kind="experiment_stopped", t=steps,
            data={
                "reason": (
                    "world_step_cap_reached"
                    if cap is not None and not raise_cap else "manual_operator_stop"
                ),
                "policy_version": _POLICY, "mode": "campaign",
                "maximum_world_steps": 3 if raise_cap else cap,
                "world_rewound": False, "physical_death": False,
            },
            ordinal=ordinal,
        )
    return journal.canonical_bytes()


def _rechain(rows: list[dict]) -> bytes:
    previous = GENESIS_HASH
    for i, row in enumerate(rows):
        row["index"] = i
        row["previous_hash"] = previous
        previous = sha256(
            bytes.fromhex(previous) + canonical_causal_bytes({
                "event_id": row["event_id"],
                "causal_event": row["causal_event"],
            })
        ).hexdigest()
        row["event_hash"] = previous
    return b"\n".join(canonical_causal_bytes(row) for row in rows)


class Stage12OperatorControlIndependentAuditTests(unittest.TestCase):
    def test_valid_config_cap_two_closed_steps_and_terminal_stop(self):
        raw = _archive()
        report = audit_stage12_operator_control(raw)
        self.assertTrue(report.configured)
        self.assertTrue(report.experiment_stopped)
        self.assertEqual(report.last_closed_step, 2)
        self.assertEqual(report.maximum_world_steps, 2)
        self.assertEqual(report.cap_changes, 1)
        self.assertEqual(report.operator_events, 3)
        self.assertEqual(report.stop_reason, "world_step_cap_reached")
        self.assertEqual(report.occurrences, audit_export_bytes(raw).occurrences)
        self.assertFalse(report.as_dict()["operator_intent_independently_verified"])

    def test_unconfigured_partial_life_is_not_a_fake_operator_stop(self):
        j = HashChainedJournal()
        _append_blocked(j, 1)
        report = audit_stage12_operator_control(j.canonical_bytes())
        self.assertFalse(report.configured)
        self.assertFalse(report.experiment_stopped)
        self.assertIsNone(report.maximum_world_steps)

    def test_rehashed_elevated_cap_and_stale_previous_cap_fail(self):
        raised = _archive(raise_cap=True)
        self.assertGreater(audit_export_bytes(raised).occurrences, 0)
        with self.assertRaisesRegex(ValueError, "step cap was raised"):
            audit_stage12_operator_control(raised)
        raw = _archive()
        rows = [json.loads(row) for row in raw.split(b"\n")]
        receipt = next(
            row["causal_event"]["data"] for row in rows
            if row["causal_event"]["kind"] == "operator_step_cap_set"
        )
        receipt["previous_cap"] = 99
        forged = _rechain(rows)
        self.assertEqual(audit_export_bytes(forged).occurrences, len(rows))
        with self.assertRaisesRegex(ValueError, "step cap was raised"):
            audit_stage12_operator_control(forged)

    def test_rehashed_cap_reached_stop_must_match_closed_step(self):
        raw = _archive()
        rows = [json.loads(row) for row in raw.split(b"\n")]
        rows[-1]["causal_event"]["t_monde"] = 3
        forged = _rechain(rows)
        self.assertEqual(audit_export_bytes(forged).occurrences, len(rows))
        with self.assertRaisesRegex(ValueError, "closed step boundary"):
            audit_stage12_operator_control(forged)

    def test_rehashed_omitted_config_and_modified_event_id_rejected(self):
        rows = [json.loads(row) for row in _archive().split(b"\n")]
        missing = _rechain(deepcopy(rows[1:]))
        self.assertGreater(audit_export_bytes(missing).occurrences, 0)
        with self.assertRaisesRegex(ValueError, "no earlier configuration"):
            audit_stage12_operator_control(missing)
        changed = deepcopy(rows)
        changed[0]["event_id"] = "f" * 64
        rewritten = _rechain(changed)
        self.assertEqual(audit_export_bytes(rewritten).occurrences, len(rows))
        with self.assertRaisesRegex(ValueError, "identity or sequence"):
            audit_stage12_operator_control(rewritten)

    def test_step_beyond_operator_cap_fails_even_with_valid_hash_chain(self):
        raw = _archive(cap=1, steps=2, stop=False)
        self.assertEqual(audit_export_bytes(raw).world_steps_closed, 2)
        with self.assertRaisesRegex(ValueError, "beyond the operator's cap"):
            audit_stage12_operator_control(raw)

    def test_rehashed_postterminal_cognitive_event_is_not_a_new_life(self):
        rows = [json.loads(row) for row in _archive().split(b"\n")]
        extra = deepcopy(rows[-1])
        extra["event_id"] = "post-stop-control-data"
        extra["causal_event"] = {
            "emitter": "scheduler", "kind": "technical_burst",
            "t_monde": 2, "data": {},
        }
        rows.append(extra)
        forged = _rechain(rows)
        # The standalone control verifier must also enforce the terminal
        # barrier, even if the base journal auditor is replaced externally.
        with self.assertRaisesRegex(ValueError, "after (experiment|operator) stop"):
            audit_stage12_operator_control(forged)

    def test_offline_module_never_imports_i0_or_living_runtime(self):
        source = (
            Path(__file__).resolve().parents[1] /
            "src/lab/stage12_operator_control_audit.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "from i0", "import i0", "import WorldBody",
            "import Oracle", "import Bench", "import Stage12Runtime",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
