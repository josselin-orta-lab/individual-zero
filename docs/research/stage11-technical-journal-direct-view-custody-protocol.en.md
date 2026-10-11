# Stage 11: direct technical-journal views must not expose mutable causal history

**Registered 2026-10-11 before implementation.** Development-only software regression contract. The normative authority remains `docs/architecture/reference/en/mvp-specification-v1.2.1.md` (17.1, 17.4–17.5, INV-22/33/44/49); no modification to that specification, Golden, held-out scientific result or Stage 9 NO-GO verdict is authorized.

## Discovered remaining exposure

The preceding [journal input/export ownership protocol](stage11-technical-journal-payload-ownership-protocol.en.md) established deep copies at `HashChainedJournal.append` and `JournalEntry.as_dict`, but `journal.entries`, `journal.get(event_id)` and the entry returned by `append` all expose **the same `JournalEntry.causal_event` object**. The dataclass is frozen, but its dict/list fields are not. A caller can still mutate an event *after it has been hashed* via e.g. `journal.entries[0].causal_event["data"]["position"]["x"] = 100` or `journal.get(id).causal_event["evidence_refs"].append("fabricated")`. The next `verify()` will reject the broken chain, but the protected history should not have been mutated in the first place.

## Fixed interface and invariants

1. A `JournalEntry` retains a private, detached nested causal mapping. Expose `causal_event` through an ordinary `Mapping` read-only facade. Every nested read, including `[]`, `.get`, `.items`, `.values` and `.copy`, must return detached dictionaries/lists. Direct assignment to a key in the top-level view must fail.
2. Keep `JournalEntry` as a frozen, slotted dataclass with its existing public constructor (`index, event_id, previous_hash, event_hash, causal_event`) and public scalar fields. Existing `HashChainedJournal.append`, `.get`, `.entries` must keep returning **the identical entry instance** for a given occurrence. No replacement copies of the entry or lost `_by_id` identity may be introduced.
3. Preserve JSON-like types on nested reads. Specifically, `isinstance(event.causal_event.get("event_refs"), list)` must remain true for existing autobiographical consumers; maps remain maps, lists remain lists; no change to learned cognition, journal projection policies, source flags or WorldBody.
4. `JournalEntry.as_dict()` returns a writable detached ordinary dict, exactly as before. Unchanged events must produce **byte-identical canonical journal lines, hashes and deterministic identities** compared to the previous code, including independent reexecution. The in-memory technical order and append-only semantics remain unchanged.
5. Retain intentional tamper-test behavior: private test replacement of a stored `JournalEntry` with an inconsistent hash still makes `journal.verify()` fail; duplicate IDs and unencodable events still fail atomically.
6. Deliberately bypassing Python privacy through `journal._entries`, altering a custom private view's internal buffer or monkeypatching internal attributes is outside this public-API custody gate. This is not a claim of a sandbox/security boundary against hostile Python code in the same process.

## Frozen local unit fixtures

- Two nested events: `perceptual_capture` with `data.position.{x,y}` plus `evidence_refs`, and `auto_segment_commit` with `event_refs`. Mutate copies obtained through `entries`, `get` and `append`, through `.get`, `.items` and exported `.as_dict()`. Stored history, `canonical_bytes()`, `head_hash` and `verify()` stay unchanged.
- Assert entry instance identity through all access paths; top-level writes are refused; existing list-type checks work on detached nested results.
- Compare before/after implementation over a fixed deterministic multi-entry technical journal with nested lists/maps, Boolean, float and Unicode causal inputs; exact byte and hash equality, without changing any hashes in golden reference files.
- Explicitly distinguish isolated local Python tests from whole-repository unit CI. The latter is **not** claimed until run against its exact SHA. No blind rerun of GitHub Actions while runner admission remains blocked.

**Stage 11 IN PROGRESS, Stage 9 scientific NO-GO. PR #25 remains Draft, open and unmerged.**
