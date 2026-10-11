"""Independent, read-only canonical audit of I0's COMPLETE causal event journal.

This module imports only the Python standard library. It never constructs
Individual Zero, WorldBody, Oracle, Bench or a journal owner. It verifies what
the EXPORT claims, not whether the physical world actually matched its claims.

A self-contained hash chain cannot prove that its final tail wasn't removed:
supply a trusted head hash and occurrence count to detect suffix truncation.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Mapping
from unicodedata import normalize

from .epistemic_guard import has_external_truth, project_lived_field


GENESIS_HASH = "00" * 32
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_FIELDS = frozenset({"index", "event_id", "previous_hash", "event_hash", "causal_event"})
_STAGE2_ALLOWED = frozenset({"command_experienced", "world_transition_experienced"})
_STAGE7_ALLOWED = _STAGE2_ALLOWED | frozenset({
    "active_goal_changed", "s_t_published", "agency_comparison",
    "episode_closed", "memory_recall_proposed",
    "intention_created", "intention_triggered",
})
_POLICIES = {
    "stage2-autobio-v1": _STAGE2_ALLOWED,
    "stage7-autobio-v1": _STAGE7_ALLOWED,
}
# Only explicit laboratory-truth imports are prohibited here. An ordinary
# technical statement that oracle_access=False is NOT secret oracle evidence.
_FORBIDDEN_KINDS = frozenset({
    "oracle_read", "oracle_annotation", "oracle_ground_truth",
    "benchmark_truth_injected",
})
_FORBIDDEN_KEYS = frozenset({"oracle_canary", "oracle_ground_truth"})


def _unique_pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON mapping key")
        result[key] = value
    return result


def _bad_constant(value):
    raise ValueError("non-finite JSON constant is forbidden")


def _check_nfc_and_types(value):
    if value is None or type(value) in (bool, int):
        return
    if type(value) is float:
        raise ValueError("raw float is not canonical causal data")
    if isinstance(value, str):
        if normalize("NFC", value) != value:
            raise ValueError("non-NFC causal string")
        return
    if isinstance(value, list):
        for item in value:
            _check_nfc_and_types(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or normalize("NFC", key) != key:
                raise ValueError("non-canonical mapping key")
            _check_nfc_and_types(item)
        return
    raise ValueError("unsupported canonical JSON value")


def _canonical(value) -> bytes:
    _check_nfc_and_types(value)
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _entry_id(row, *, expected_index):
    if not isinstance(row, dict) or set(row) != _FIELDS:
        raise ValueError("invalid technical event schema")
    if type(row["index"]) is not int or row["index"] != expected_index:
        raise ValueError("missing, reordered or duplicate journal index")
    event_id = row["event_id"]
    if not isinstance(event_id, str) or not event_id:
        raise ValueError("invalid occurrence event ID")
    if not isinstance(row["causal_event"], dict):
        raise ValueError("technical occurrence has no causal mapping")
    for field in ("previous_hash", "event_hash"):
        if type(row[field]) is not str or _HASH.fullmatch(row[field]) is None:
            raise ValueError("invalid lowercase SHA-256 hash")
    return event_id


@dataclass(frozen=True)
class JournalAuditResult:
    occurrences: int
    head_hash: str
    world_steps_closed: int
    terminal_deaths: int
    autobiographical_commits: int
    consolidation_publications: int
    unexamined_event_kinds: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "individual-zero-independent-audit-v1",
            "valid": True,
            "occurrences": self.occurrences,
            "head_hash": self.head_hash,
            "world_steps_closed": self.world_steps_closed,
            "terminal_deaths": self.terminal_deaths,
            "autobiographical_commits": self.autobiographical_commits,
            "consolidation_publications": self.consolidation_publications,
            "unexamined_event_kinds": list(self.unexamined_event_kinds),
            "physical_truth_verified": False,
            "warning": (
                "Cryptographic consistency is not independent proof of "
                "the world's physical truth."
            ),
        }


def audit_export_bytes(
    content: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> JournalAuditResult:
    """Verify a complete canonical export without creating any living owner.

    No leading or trailing record separator is accepted: this reproduces the
    immutable HashChainedJournal.canonical_bytes() output exactly.
    """
    if type(content) is not bytes or not content:
        raise ValueError("canonical journal export must be nonempty bytes")
    if content.endswith(b"\n") or content.startswith(b"\n"):
        raise ValueError("canonical journal has extra outer line separator")
    if expected_head is not None and (
        type(expected_head) is not str or _HASH.fullmatch(expected_head) is None
    ):
        raise ValueError("expected head must be lowercase SHA-256")
    if expected_count is not None and (
        type(expected_count) is not int or expected_count < 1
    ):
        raise ValueError("expected count must be a positive integer")

    by_id: dict[str, tuple[int, dict, str]] = {}
    rows: list[dict] = []
    attempts: dict[tuple[int, str], dict[str, list[tuple[int, dict]]]] = {}
    closed_steps: dict[int, str] = {}
    open_steps: dict[int, str] = {}
    previous = GENESIS_HASH
    prior_step = -1
    death_index: int | None = None
    death_attempt: tuple[int, str] | None = None
    commits = publications = deaths = 0
    # Only committed, chronologically consecutive SlowHistory versions are
    # accepted; technical claims do not themselves prove a semantic learning.
    latest_history_version: str | None = None
    activated_versions: set[str] = set()
    activated_transactions: set[str] = set()
    examined = set()
    all_kinds = set()

    for number, raw in enumerate(content.split(b"\n")):
        try:
            row = json.loads(
                raw.decode("utf-8"),
                object_pairs_hook=_unique_pairs,
                parse_constant=_bad_constant,
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid canonical journal JSON") from exc
        if _canonical(row) != raw:
            raise ValueError("journal entry is not byte-canonical")
        event_id = _entry_id(row, expected_index=number)
        if event_id in by_id:
            raise ValueError("duplicate causal occurrence ID")
        if row["previous_hash"] != previous:
            raise ValueError("broken predecessor hash, missing or reordered event")
        digest = sha256(
            bytes.fromhex(previous) + _canonical({
                "event_id": event_id, "causal_event": row["causal_event"],
            })
        ).hexdigest()
        if row["event_hash"] != digest:
            raise ValueError("corrupted technical event payload or hash")
        previous = digest
        event = row["causal_event"]
        kind = event.get("kind")
        if not isinstance(kind, str) or not kind:
            raise ValueError("missing causal event kind")
        if (
            kind in _FORBIDDEN_KINDS
            or any(k in _FORBIDDEN_KEYS for k in event)
            or has_external_truth(event)
        ):
            raise ValueError("external oracle evidence leaked into I0 journal")
        all_kinds.add(kind)
        if death_index is not None and kind != "step_closed":
            raise ValueError("technical/cognitive event occurred after death")
        t = event.get("t_monde")
        if t is not None:
            if type(t) is not int or t < 0 or t < prior_step:
                raise ValueError("nonmonotonic or invalid world-step occurrence")
            prior_step = t
        attempt = event.get("attempt_ref")
        if kind in {
            "step_opened", "step_closed", "command_experienced",
            "world_transition_experienced", "auto_segment_commit",
            "individual_death_confirmed",
        }:
            examined.add(kind)
            if type(t) is not int or t < 1 or not isinstance(attempt, str) or not attempt:
                raise ValueError("physical/terminal event missing world attempt provenance")
            key = (t, attempt)
            attempts.setdefault(key, {}).setdefault(kind, []).append((number, event))
            if kind == "step_opened":
                if t in open_steps or t in closed_steps:
                    raise ValueError("duplicate opened world step")
                if open_steps and t != max(open_steps) + 1:
                    raise ValueError("missing physical world step")
                open_steps[t] = attempt
            if kind == "step_closed":
                if open_steps.get(t) != attempt or t in closed_steps:
                    raise ValueError("closed world step lacks unique opening")
                closed_steps[t] = attempt
            if kind == "individual_death_confirmed":
                if death_index is not None:
                    raise ValueError("duplicate individual death")
                reasons = event.get("reasons")
                if not isinstance(reasons, list) or not reasons:
                    raise ValueError("death requires documented lethal causes")
                death_index, death_attempt = number, key
                deaths += 1

        if kind == "auto_segment_commit":
            commits += 1
            policy = _POLICIES.get(event.get("filter_version"))
            if policy is None:
                raise ValueError("unknown autobiographical projection policy")
            refs = event.get("event_refs")
            if not isinstance(refs, list) or len(refs) != len(set(refs)):
                raise ValueError("invalid or duplicate autobiographical source refs")
            for ref in refs:
                source = by_id.get(ref)
                if source is None or source[0] >= number:
                    raise ValueError("missing/future autobiographical source")
                origin = source[1]
                if (
                    origin.get("kind") not in policy
                    or origin.get("attempt_ref") != attempt
                    or origin.get("t_monde") != t
                ):
                    raise ValueError("technical/oracle event exposed as lived source")
                # Apply the same Stage-2 and Stage-7 nested-lived schemas
                # as the live boundary. Unknown technical metadata is retained
                # in the audit record, never handed to Memory.
                source_kind = origin["kind"]
                if source_kind == "command_experienced":
                    lived_fields = ("parameters",)
                elif source_kind == "world_transition_experienced":
                    lived_fields = ("position_after", "body_after", "effects")
                else:
                    lived_fields = ("data",)
                for field in lived_fields:
                    if field in origin:
                        project_lived_field(
                            kind=source_kind, field=field, value=origin[field],
                        )

        if kind == "stage10_consolidation_version_activated":
            examined.add(kind)
            publications += 1
            if event.get("emitter") != "scheduler":
                raise ValueError("consolidation activation must be scheduler-owned")
            data = event.get("data")
            if not isinstance(data, dict):
                raise ValueError("consolidation has no provenance data")
            source_version = data.get("source_history_version")
            new_version = data.get("new_history_version")
            transaction_id = data.get("consolidation_id")
            if any(type(item) is not str or not item for item in (
                source_version, new_version, transaction_id,
            )):
                raise ValueError("consolidation missing history version or transaction")
            if (source_version == new_version
                    or new_version in activated_versions
                    or transaction_id in activated_transactions):
                raise ValueError("duplicate/reused consolidation version or transaction")
            if (latest_history_version is not None
                    and source_version != latest_history_version):
                raise ValueError("consolidated history version lineage is broken")
            for digest_name in ("batch_digest", "candidate_digest"):
                digest_value = data.get(digest_name)
                if (type(digest_value) is not str
                        or _HASH.fullmatch(digest_value) is None):
                    raise ValueError("consolidation has an invalid digest")
            batch = data.get("batch")
            if (not isinstance(batch, list)
                    or any(type(ref) is not str or not ref for ref in batch)
                    or len(set(batch)) != len(batch)):
                raise ValueError("consolidation batch needs unique episode references")
            cut = data.get("cut")
            if not isinstance(cut, dict):
                raise ValueError("consolidation has no verified cut")
            ci, cid, ch = (
                cut.get("journal_index"), cut.get("journal_event_id"),
                cut.get("journal_hash"),
            )
            if type(ci) is not int or ci < 0 or ci >= number:
                raise ValueError("invalid consolidation journal cut index")
            if rows[ci]["event_id"] != cid or rows[ci]["event_hash"] != ch:
                raise ValueError("false consolidation cut identity or hash")
            cut_step = cut.get("world_step")
            origin_step = rows[ci]["causal_event"].get("t_monde")
            if (type(cut_step) is not int or cut_step < 1
                    or type(t) is not int or cut_step > t
                    or type(origin_step) is not int
                    or not 1 <= origin_step <= cut_step):
                raise ValueError("invalid consolidation cut world-step provenance")
            if cut.get("history_version") != source_version:
                raise ValueError("consolidation cut history version does not match source")
            end_index = data.get("postcut_journal_end_index")
            end_hash = data.get("postcut_journal_end_hash")
            # Stage10PublicationCoordinator.publish() validates that no
            # event, including a learned post-cut delta, arrived after its
            # frozen end. Its activation must directly follow that end.
            if (type(end_index) is not int or
                    end_index < ci or end_index != number - 1 or
                    rows[end_index]["event_hash"] != end_hash):
                raise ValueError("Stage10 postcut freeze is not the latest causal head")
            if data.get("commit_index") != number:
                raise ValueError("consolidation activation index mismatch")
            latest_history_version = new_version
            activated_versions.add(new_version)
            activated_transactions.add(transaction_id)

        by_id[event_id] = (number, event, digest)
        rows.append(row)

    if expected_count is not None and len(rows) != expected_count:
        raise ValueError("export differs from trusted occurrence count")
    if expected_head is not None and previous != expected_head:
        raise ValueError("export differs from trusted full-life head hash")

    for (step, ref), kinds in attempts.items():
        opens = kinds.get("step_opened", [])
        closes = kinds.get("step_closed", [])
        commands = kinds.get("command_experienced", [])
        transitions = kinds.get("world_transition_experienced", [])
        autobios = kinds.get("auto_segment_commit", [])
        terminal = kinds.get("individual_death_confirmed", [])
        if not opens or not closes or len(opens) != 1 or len(closes) != 1:
            raise ValueError("unclosed or invalid physical world step")
        if len(commands) > 1 or len(transitions) > 1 or len(autobios) > 1:
            raise ValueError("multiple accepted commands/transitions or autobiographical commits")
        data = closes[0][1].get("data")
        if not isinstance(data, dict):
            raise ValueError("physical step closure missing counters")
        outcome = data.get("outcome")
        if outcome in ("normal", "dead"):
            if (len(commands), len(transitions)) != (1, 1):
                raise ValueError("applied step missing command/transition pair")
            if (data.get("applied_command_count"),
                    data.get("world_advance_count")) != (1, 1):
                raise ValueError("invalid applied-world advancement accounting")
            if not (opens[0][0] < commands[0][0] < transitions[0][0] < closes[0][0]):
                raise ValueError("command and physical effect order invalid")
            if outcome == "dead":
                if len(terminal) != 1 or len(autobios) != 0 or death_attempt != (step, ref):
                    raise ValueError("death lacks technical terminal record or has postmortem cognition")
                if not transitions[0][0] < terminal[0][0] < closes[0][0]:
                    raise ValueError("death confirmation misplaced")
                confirmed = terminal[0][1]
                transition = transitions[0][1]
                command = commands[0][1]
                if (confirmed.get("command_hash") != command.get("command_hash")
                        or confirmed.get("position_after") != transition.get("position_after")
                        or confirmed.get("body_after") != transition.get("body_after")):
                    raise ValueError("terminal physical state disagrees with recorded outcome")
            elif terminal or (death_index is not None and step >= death_attempt[0]):
                raise ValueError("nonterminal step or cognition after a death")
            if outcome == "normal":
                if len(autobios) != 1:
                    raise ValueError("nonlethal physical step lacks autobiographical commit")
                commit_index, commit_event = autobios[0]
                if not transitions[0][0] < commit_index < closes[0][0]:
                    raise ValueError("autobiographical commitment precedes physical effect")
                refs = commit_event.get("event_refs")
                required = {
                    rows[commands[0][0]]["event_id"],
                    rows[transitions[0][0]]["event_id"],
                }
                if not isinstance(refs, list) or not required.issubset(refs):
                    raise ValueError(
                        "applied physical Memory commit omits command/transition"
                    )
        elif outcome in ("blocked", "external_stop"):
            if (data.get("applied_command_count"),
                    data.get("world_advance_count")) != (0, 0):
                raise ValueError("stopped step claims nonexistent world advance")
            if transitions or terminal:
                raise ValueError("stopped step contains physical terminal transition")
        else:
            raise ValueError("unknown world-step closure status")
    if sorted(open_steps) != sorted(closed_steps):
        raise ValueError("missing world step closure")
    if open_steps and sorted(open_steps) != list(range(1, max(open_steps) + 1)):
        raise ValueError("physical world step sequence has gaps")
    if deaths and (not rows or rows[-1]["causal_event"].get("kind") != "step_closed"):
        raise ValueError("terminal event was not cleanly closed")
    return JournalAuditResult(
        occurrences=len(rows), head_hash=previous,
        world_steps_closed=len(closed_steps), terminal_deaths=deaths,
        autobiographical_commits=commits,
        consolidation_publications=publications,
        unexamined_event_kinds=tuple(sorted(all_kinds - examined)),
    )


def audit_export_file(
    path: Path, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> JournalAuditResult:
    """Read in place, without writing to the export or the live runtime."""
    source = Path(path)
    if not source.is_file() or source.is_symlink():
        raise ValueError("journal must be a regular non-symlink file")
    return audit_export_bytes(
        source.read_bytes(), expected_head=expected_head,
        expected_count=expected_count,
    )
