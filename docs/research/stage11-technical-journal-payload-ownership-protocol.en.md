# Stage 11: technical journal payload ownership at ingestion and export

**Software-only regression contract, recorded before implementation on 2026-10-11.** Sole normative authority: `docs/architecture/reference/en/mvp-specification-v1.2.1.md` §§4.6, 5.1, 17.1, 17.4–17.5 and INV-33/44/49. This is not a scientific preregistration, held-out observation, Golden result or a Stage 9 verdict.

## Existing bug and exact scope

`HashChainedJournal.append` computes a SHA-256 link from the full canonical nested `causal_event` but then stores only `dict(causal_event)`; `JournalEntry.as_dict` likewise returns a shallow copy. A caller still holding nested dicts/lists can change the already appended content without calling the append-only API. The journal's hash-chain verification subsequently fails although no authorized append occurred. A caller changing the nested contents of a separately returned `JournalEntry.as_dict()` has the same effect.

Stage 11 already copies `InjectedScenario` event payloads defensively. That only protects one producer; other world, Perception, Memory, scheduler and experiment events also use the same journal. Journal ownership must be enforced at this common boundary, not through a growing list of producer-specific copies.

## Frozen minimum implementation

1. On `append`, validate the original complete causal event against the normative canonical encoder **before** modifying entries or the occurrence index, then retain a detached **deep copy** whose canonical bytes are identical to those used for hashing. Hash the retained copy to avoid a mismatch between the data hashed and stored. No new causal fields, timestamps or sort changes are allowed.
2. `JournalEntry.as_dict()` must return a detached deep copy of the nested causal event; callers must not be able to mutate journal history indirectly by altering an exported ordinary dictionary.
3. Preserve `HashChainedJournal.entries`, `get`, `verify`, unique occurrence IDs, the technical journal/AutoSegmentCommit interface, canonical bytes and the previous positive historical fixture hashes on unchanged inputs. The JournalEntry object itself continues to expose its `causal_event` mapping as a trusted in-process technical view; preventing mutation through deliberate direct access to that view is a **separate stronger immutability gate** and is not claimed here.
4. The journal remains append-only and never rolls back. The new copy operation is a non-semantic ownership boundary, **not** a new scientific provenance guarantee.

## Frozen unit cases

- Append an event with nested `{"data":{"position":{"x":3,"y":2}},"evidence_refs":["source-1"]}`; capture its canonical bytes and head hash; mutate the original nested dictionary and list. `get`, `entries`, canonical bytes and hash verification must remain unchanged.
- Export the entry with `JournalEntry.as_dict()`; mutate nested position and refs in the exported structure. The stored entry and the hash must remain unchanged.
- Two independently constructed journals containing identical untouched events must have equal bytes and hashes.
- Invalid unencodable nested causal input must fail before mutating journal state.
- Existing tests of journal identity, append uniqueness and autobiographical projections must remain behaviorally unchanged.

**Validation status: UNTESTED until the exact-source commit's tests run.** Stage 11 IN PROGRESS; Stage 9 scientific NO-GO; PR #25 remains Draft/unmerged. Full Python 3.11 and Goldens remain distinct.
