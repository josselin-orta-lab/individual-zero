# Stage 11: ownership of nested external-scenario input payloads

**Preimplementation software-only regression protocol, 2026-10-11.** Normative authority: `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, §§4.6, 5.1, 17.1–17.6, INV-33. This contract does not establish scientific provenance or replace Stage 9 NO-GO.

## Proven code risk before the change

The frozen `ScenarioEvent` dataclass currently contains a mutable `Mapping` payload. `InjectedScenario.__init__` retains the caller's original event objects; `ScenarioEvent.as_dict` copies only the outer mapping. A caller mutating a nested `payload.position` after program creation, after reading `export_causal_state()`, or after receiving the events returned by `apply_for_step` can silently rewrite an already versioned causal schedule. The same aliased nested mapping can enter `external_input_received` in the hash-chained technical journal because `HashChainedJournal.append` performs only an outer copy.

## Frozen software contract

1. `InjectedScenario` takes private deep copies of the versioned incoming event program before execution. Later caller mutations to original event dictionaries MUST NOT alter the scheduled input, WorldBody position, scenario snapshot fingerprint or journal provenance.
2. `ScenarioEvent.as_dict` returns a detached copy, including nested dictionaries and lists; mutating an exported snapshot or a caller-owned event must not change the owner's internal program.
3. `apply_for_step` returns detached event copies, never mutable aliases to the scenario's internal future or historical program. The technical `external_input_received` record owns its own deep-copied payload, not a reference that callers can rewrite after hashing.
4. No new cognitive channel, operator intervention, world oracle, internal action, reward or safety claim. Existing fully valid input schedules MUST yield unchanged canonical journals, commands and world states under normal execution.
5. This covers ordinary supported JSON-like nested scenario payloads. Arbitrary hostile mutation of private Python internals or of a public JournalEntry itself is not included in this specific contract.

## Admission-time canonical-input validation addendum (2026-10-11, preimplementation)

Inputs that cannot be encoded in the normative canonical causal format cannot be safely written to the mandatory pre-application journal event. Validate the event schedule at `InjectedScenario` construction: each item is a `ScenarioEvent`, its `t_monde` is an exact positive integer, `sequence` an exact non-negative integer, `operation` a non-empty string, `payload` a mapping, and its complete detached `as_dict()` is accepted by `canonical_causal_bytes` (reject NaN/Infinity, sets, invalid map keys and unsupported causal types). Unknown but serializable operation names and semantically invalid world positions remain injectable for the **runtime** rejection protocol, which must log reception and rejection. Reject malformed/unserializable scenario programs before a world step or journal input is started; do not substitute a dropped event, coerce a bad timestamp or advance the scheduler. Add unit tests for malformed timestamps, Boolean sequence/timestamp, and unencodable payloads.

## Physical body and resource input-fidelity addendum (2026-10-11, before implementation)

An independent review found two other silent coercions in the existing `WorldBody.apply_scenario_event` interface: `place_resource.quantity` is passed through `int(...)` (so `1.9`, `"2"`, and `True` can change the number of resources while the original input is journaled), and `set_body` accepts `float(...)` for external body fields (so `"50"` and `True` become purported physical measurements). The external state may therefore differ from the *literal* logged input.

**Frozen contract:** `place_resource.kind` must be an actual supported string kind, and `quantity` a literal non-negative integer, not Boolean, fractional, text or null. `set_body` may change only recognized energy/food/water/integrity fields; for any supplied recognized field, require an actual int or float (not bool, text or null), convert the value to the existing binary64 BodyState field, then apply the existing finite [0,100] validation **before assignment**. No other WorldBody state, cognition, knowledge or command contract changes. Historical valid integer resource quantities and numeric body states continue to work identically.

**Fixed checks:** direct WorldBody calls reject each lossy input with no physical-owner mutation; an injected invalid but canonically encodable `place_resource.quantity` or `set_body` is logged as received, rejected with `world_recovered=true`, and stopped before Perception/command, preserving the entire pre-step body/world state and journal. Valid integer quantities and numeric body values still apply. These are public development-only cases, not evidence of acquired ability or independent scientific results.

## Fixed public unit inputs

- Schedule a `set_position` input at the public junction's world step 2 to `(4,2)`, with a nested caller-provided position dictionary. After constructing the runtime, mutate that caller dictionary to `(0,2)`; independently mutate the `events` in an exported causal-state copy to another position. The owner must keep its originally scheduled `(4,2)` and execute that world-only arrival on step 2. Hash-chain verification and source/reference hashes must remain stable.
- In an isolated external-scenario owner, apply one valid input then mutate the `ScenarioEvent` returned to the caller, including its nested position. Compare the live owner's export and the technical journal bytes to the pre-mutation values.
- Independently execute two identical unmodified scenarios and assert exact journals and causal-owner states.

**Unverified until SHA-pinned CI.** Stage 11 remains IN PROGRESS, Stage 9 scientific NO-GO, PR #25 stays draft/unmerged. Full Python 3.11, Goldens and held-out remain separate.
