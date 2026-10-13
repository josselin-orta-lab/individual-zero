"""Lossless M11 OPT2: old normative bytes vs fast paths and journal custody."""
from __future__ import annotations
from collections import UserDict
from copy import deepcopy
import json
import math
import random
import unittest
import unicodedata

from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.journal import HashChainedJournal


def reference_normalize(value):
    """Original pre-OPT2 normative algorithm, kept as test-only oracle."""
    from typing import Mapping
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite floats are forbidden in causal data")
        normalized = 0.0 if value == 0.0 else value
        return {"$f64": normalized.hex().lower()}
    if isinstance(value, Mapping):
        normalized = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("causal mapping keys must be strings")
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in normalized:
                raise ValueError("causal mapping keys collide after NFC normalization")
            normalized[normalized_key] = reference_normalize(item)
        return normalized
    if isinstance(value, (list, tuple)):
        return [reference_normalize(item) for item in value]
    if isinstance(value, (set, frozenset)):
        raise TypeError("unordered collections are forbidden in causal data")
    raise TypeError(f"unsupported causal type: {type(value).__name__}")


def reference_bytes(value):
    return json.dumps(
        reference_normalize(value), ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


class NormalizationEquivalence(unittest.TestCase):
    def compare(self, value):
        try:
            expected = reference_bytes(value)
        except (TypeError, ValueError) as exc:
            with self.assertRaises(type(exc)) as observed:
                canonical_causal_bytes(value)
            self.assertEqual(str(observed.exception), str(exc))
        else:
            self.assertEqual(canonical_causal_bytes(value), expected)
            self.assertEqual(sha256_hex(canonical_causal_bytes(value)),
                             sha256_hex(expected))

    def test_scalar_float_unicode_and_adversarial_containers(self):
        class ForeignString(str):
            pass
        class ForeignDict(dict):
            pass
        class ForeignList(list):
            pass
        class ForeignInt(int):
            pass
        cases = [
            None, True, False, 0, -1, 10000000000,
            ForeignInt(12), "", "e\u0301", "\u00e9", "🐙",
            ForeignString("e\u0301"), -0.0, 0.0, 1e-15, 1e100,
            float("nan"), float("-inf"), float("inf"),
            {}, [], (), ("A", {"x": [False, -0.0]}),
            {"a": {"b": [1, 2.4, "e\u0301"]}},
            UserDict({"nested": [{"b": 4.0}]}),
            ForeignDict({"outer": ForeignList([ForeignInt(2), "c"])}),
            {2: "invalid key"}, {"e\u0301": 1, "\u00e9": 2},
            set(), frozenset({"x"}), object(),
        ]
        for value in cases:
            with self.subTest(value=repr(value)):
                self.compare(value)

    def test_deterministic_nested_corpus(self):
        rng = random.Random(10331)
        pool = [None, True, False, 0, 1, -3, 0.0, -0.0,
                1.25001, 1e-25, "e\u0301", "é", "❤️", "x"]
        for _ in range(250):
            data = {}
            for i in range(rng.randrange(0, 14)):
                key = f"entry{i:02d}"
                data[key] = [
                    {"inner": rng.choice(pool)},
                    (rng.choice(pool), rng.choice(pool)),
                    UserDict({"deep": rng.choice(pool)}),
                ]
            self.compare(data)


class DetachedJournalEquivalence(unittest.TestCase):
    def test_export_mutation_does_not_alter_current_or_past(self):
        journal = HashChainedJournal()
        contents = {
            "kind": "test_nested",
            "t_monde": 1,
            "data": {"refs": ["a", {"b": [2, -0.0]}],
                     "nested": {"a": [1, 2, 3]}},
        }
        entry = journal.append(event_id="event:0", causal_event=contents)
        original_head = journal.head_hash
        original_bytes = journal.canonical_bytes()
        contents["data"]["refs"][1]["b"].append(999)
        first = entry.as_dict()
        second = entry.as_dict()
        self.assertEqual(first, second)
        first["causal_event"]["data"]["refs"][1]["b"].append(3)
        second["causal_event"]["data"]["nested"]["a"].clear()
        self.assertEqual(journal.canonical_bytes(), original_bytes)
        self.assertEqual(journal.head_hash, original_head)
        self.assertTrue(journal.verify())
        self.assertEqual(entry.as_dict()["causal_event"]["data"]["refs"][1]["b"], [2, -0.0])
        self.assertEqual(entry.as_dict()["causal_event"]["data"]["nested"]["a"], [1, 2, 3])

    def test_causal_chain_byte_equivalence_multiple_events(self):
        journal = HashChainedJournal()
        previous = "0" * 64
        records = []
        for i in range(90):
            causal = {"kind": "test_m11_opt2",
                      "t_monde": i + 1,
                      "data": {"refs": [i, "e\u0301", (0.0, -0.0)],
                               "state": {"index": i}}}
            eid = f"event:{i}"
            digest = sha256_hex(bytes.fromhex(previous) + reference_bytes(
                {"event_id": eid, "causal_event": causal}))
            ref = {
                "index": i, "event_id": eid, "previous_hash": previous,
                "event_hash": digest, "causal_event": causal,
            }
            records.append(reference_bytes(ref))
            entry = journal.append(event_id=eid, causal_event=deepcopy(causal))
            self.assertEqual(entry.event_hash, digest)
            previous = digest
        self.assertEqual(journal.canonical_bytes(), b"\n".join(records))
        self.assertTrue(journal.verify())


if __name__ == "__main__":
    unittest.main()
