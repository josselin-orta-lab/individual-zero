"""Read-only canonical hash-chain preflight, not full independent causal audit.

Never treats a self-contained journal as proof of a complete life.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import unicodedata

HASH = re.compile(r"[0-9a-f]{64}\Z")
MAX_BYTES = 32 * 1024 * 1024
MAX_RECORDS = 100_000


def check_chain(path: Path, *, expected_head: str | None = None,
                expected_count: int | None = None) -> dict:
    result = {"chain_valid": False, "trusted_tail_verified": False,
              "full_causal_audit": False, "map_authorized": False,
              "head_hash": None, "occurrences": 0, "error": None}
    def fail(reason):
        result["error"] = reason
        return result
    if expected_head is not None and (not isinstance(expected_head, str) or not HASH.fullmatch(expected_head)):
        return fail("invalid_expected_head")
    if expected_count is not None and (type(expected_count) is not int or expected_count < 1):
        return fail("invalid_expected_count")
    try:
        with path.open("rb") as stream:
            content = stream.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            return fail("journal_too_large")
        if not content or content.startswith(b"\n") or content.endswith(b"\n"):
            return fail("invalid_canonical_envelope")
        previous = "00" * 32
        ids = set()
        records = content.split(b"\n")
        if len(records) > MAX_RECORDS:
            return fail("too_many_records")
        def canonical(value):
            if value is None or type(value) in (bool, int):
                return
            if type(value) is str:
                if unicodedata.normalize("NFC", value) != value:
                    raise ValueError("non_nfc")
                return
            if isinstance(value, list):
                for x in value: canonical(x)
                return
            if isinstance(value, dict):
                for k, v in value.items():
                    canonical(k)
                    canonical(v)
                return
            raise ValueError("non_canonical_type")
        def pairs(values):
            d = {}
            for k, v in values:
                if k in d:
                    raise ValueError("duplicate_key")
                d[k] = v
            return d
        for index, raw in enumerate(records):
            entry = json.loads(raw, object_pairs_hook=pairs,
                               parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non_finite")))
            canonical(entry)
            def encode(x):
                return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
            if encode(entry) != raw or not isinstance(entry, dict) or set(entry) != {"index", "event_id", "previous_hash", "event_hash", "causal_event"}:
                return fail("noncanonical_entry")
            eid = entry["event_id"]
            if type(entry["index"]) is not int or entry["index"] != index or not isinstance(eid, str) or not eid or eid in ids:
                return fail("invalid_index_or_identity")
            ids.add(eid)
            if entry["previous_hash"] != previous or not isinstance(entry["event_hash"], str) or not HASH.fullmatch(entry["event_hash"]) or not isinstance(entry["causal_event"], dict):
                return fail("invalid_link")
            digest = hashlib.sha256(bytes.fromhex(previous) + encode({"event_id": eid, "causal_event": entry["causal_event"]})).hexdigest()
            if digest != entry["event_hash"]:
                return fail("invalid_event_hash")
            previous = digest
        result["chain_valid"] = True
        result["head_hash"] = previous
        result["occurrences"] = len(records)
        result["trusted_tail_verified"] = expected_head is not None and expected_count is not None and expected_head == previous and expected_count == len(records)
        if expected_head is not None and expected_head != previous:
            return fail("trusted_head_mismatch")
        if expected_count is not None and expected_count != len(records):
            return fail("trusted_count_mismatch")
        return result
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, OverflowError):
        return fail("unreadable_or_invalid_journal")
