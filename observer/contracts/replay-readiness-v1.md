# Replay read model proposal (not a Phase 2 implementation)

Status: **design only**, approval of Phase 1 required before implementation.

The Phase 1 reader has four mutually distinct sources: `journal` (canonical I0
technical journal), `oracle` (external authorized truth), `evaluation_trace`
(independent bench) and `lab_events` (bootstrap Lab telemetry). A source label
is not a scientific attestation. The reader returns the **unaltered JSON
record** together with a read-only display projection.

## Temporal identity and indexing

- Canonical journal entries carry `index`, `event_id`, `previous_hash`,
  `event_hash` and `causal_event`. `causal_event.t_monde` is the world step when
  recorded; it is **not** necessarily a wall-clock timestamp.
- `LabEvent.cycle` is a bootstrap cycle and cannot be equated to `t_monde`.
- Imported Oracle records must retain original schema and time identity.
  Do **not** join Oracle/world truth to cognition by incidental array offset.
- Phase 2 requires an explicit binding `(individual_id, life_generation,
  attempt_ref, t_monde)` plus provenance and a validated mapping of event
  occurrence indices to authoritative step boundaries.

## Reconstruction strategy

1. Independently audit full canonical journal, including death/seal and
   step closure, and check expected head/count against separately trusted
   receipts before declaring a replay complete.
2. Index immutable occurrences and recorded state anchors; never reopen a
   simulator, run cognition or project past knowledge using present state.
3. For each requested step, prefer an explicit, uniquely identified world/body
   state anchor; apply only historically **recorded** changes where the
   versioned delta semantics permit deterministic application.
4. Mark missing anchor, incomplete transition, uncertain crash suffix,
   unknown payload semantics and absent external Oracle source as gaps.
5. After a confirmed death, expose only terminal history. Never treat a
   predeath snapshot as permission to continue the same identity.

## 2D map required data

Dimension and coordinate reference system, grid-versus-continuous topology,
terrain and obstacle geometry, resource/danger entities and IDs, positions,
orientations (if recorded), step-boundary world updates, I0 pose, and their
provenance. Do not invent these from qualitative event names. The existing
Stage11 diagnostic may record partial positions but its summary report is
**not** a full map source.

## Known gaps in inspected `main` (2026-10-12)

- The Oracle is capability-scoped and has no general-purpose export service.
  `EvaluationTrace` is currently in-memory; no normative Oracle JSONL schema
  is provided. `observer-source-v1` only describes **custody paths and
  categories**, not a fabricated core-export schema.
- The Stage11 autonomous diagnostic emits a summary to stdout. It does not
  independently publish a full journal or ground-truth timeline on disk.
- WAL journaling is not an atomic, coherent restorable runtime state; MVP
  v1.3.1 M-11 remains an open integration gate.
- Complete maps/geometry and unambiguous state reconstruction contracts
  require further primary-source inspection and operator validation.

Proposed Phase 2 UI: time scrubber, separate world/observation/belief/Oracle
panels, geospatial canvas only when exact coordinates exist, terminal banner,
integrity alert rail and historical-provenance inspector. No Phase 2 code is
present in Phase 1.

## Proposed frame export contract (Phase 2)

See `observer-world-frames-v1.schema.json`. It requires explicit identity,
committed `t_monde` boundaries, bounded integer grid coordinates, unique
entity identities (to be checked by the consumer), and an independent
attestation naming the canonical journal head/count and source digest.

**A manifest attestation is a claim, not verification.** A file satisfying
this schema alone MUST NOT enable an authoritative map. Before map rendering,
the consumer must independently verify the complete canonical journal, trusted
head/count, source hash, frame ordering/uniqueness, bounds, and consistency of
identity and committed step boundaries. The existing geometry endpoint
intentionally returns `available: false` until that independent verifier is
implemented. Oracle and cognition must remain separately labeled.
