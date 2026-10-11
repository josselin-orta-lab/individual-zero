# Stage 11: atomic rejection of invalid external inputs at world-step opening

**Software-only protocol, registered before implementation on 2026-10-11.** Normative authority is exclusively `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, particularly §§3.4, 4.6, 17.4, 17.6 and INV-33. Not a scientific preregistration, Golden, real-hazard trial or Stage 9 acceptance.

## Observed code gap

`ScriptedStage2Runtime.open_step()` opens the scheduler before applying scheduled `InjectedScenario` inputs. Each external event is journaled before WorldBody application, but an invalid operation raises while the scheduler is still active. For multiple events at the same simulated instant, earlier operations and the scenario cursor may already have changed the world. There is no `external_input_rejected` event despite normative §4.6 distinguishing reception, application and rejection.

## Frozen software contract

1. Events remain versioned, ordered by `(t_monde, sequence)`, and recorded as `external_input_received` *before* each application. No hidden cognition or oracle access is introduced.
2. For each world's step-opening batch, record the pre-batch WorldBody causal state and scenario cursor before application. On a failed application, restore **the full WorldBody pre-batch state** and original scenario cursor, including prior successful events from that same step. Report the input rejection and, if earlier events were applied, report their rollback in the append-only technical journal. The existing successful-input journal representation must remain unchanged.
3. A rejected batch closes the open scheduler attempt with existing `external_stop` semantics: zero commands, zero world transitions. No Perception capture, cognition, autobiographical commit or implicit learned danger is credited. The exception remains visible to the caller, not replaced with a normal world-step result.
4. The rejected schedule is immutable. The branch is **fail-stopped** rather than moving on to `t+1`, which would skip a causal external input. Further `open_step` calls must fail without advancing clock or journal. The halt marker is part of the scenario's restorable causal state (conditional, absent from all successful historical snapshots). A corrected schedule requires a separate initialized branch, not silently editing a running scenario.
5. If recovery of WorldBody's pre-batch state itself fails, report an explicit critical error. Never report a successful rollback. Keep the technical journal append-only. Do not hide application errors as an individual decision, veto, safety fact, or scientific verdict.

## Snapshot halt-marker cursor-coherence addendum (2026-10-11, preimplementation)

The existing fail-stop marker's `rejected_event` is meaningful only with the cursor rewound to the **first scheduled external event for the rejected world step**. A syntactically valid but inconsistent `rejected_event` plus `next_index` can silently represent a different branch. Restore MUST reject such combinations before changing `_next_index` or `_rejected_event`; check that the marker references a registered event and that the cursor is the index of the earliest event for its `t_monde` in the sorted immutable program. Earlier valid snapshots without a rejection marker remain unaffected. Include malformed-marker and shifted-cursor unit tests; no extra scientific claim.

## Frozen public fixtures

- Use the existing public `junction_open` Stage11 runtime, with no active world dangers and no change to the normative Action Control policy.
- Execute world step 1 normally. At step 2 schedule a valid `set_danger_zone` at `(2,3)` (sequence 0), then an invalid external `set_position` at the impassable border `(0,2)` (sequence 1). Verify before/after WorldBody equality including hazards, scenario cursor rewind, `external_input_received` for both, `external_input_applied` for the earlier valid event followed by `external_input_rejected` and explicit batch rollback, and `step_closed(external_stop,0,0)`. No step-2 Perception or command. A second run reproduces exactly the same normalized causal journal and owner states.
- Independently inject a single invalid exterior position at step 1, checking rejection without any applied input or command, branch fail-stop and unchanged world.
- Exercise two valid same-step inputs to ensure normal execution and unchanged ordering/provenance.
- Exercise direct scenario owner snapshot round-trip for halt marker and its reset to a verified pre-failure state; do **not** reuse a previous journal occurrence ID in the same life by re-executing a cancelled step after snapshot rewind.
- Do not claim full general recovery from arbitrary Python faults outside the scenario input boundary.

**Prior status:** Stage 11 IN PROGRESS; Stage 9 scientific NO-GO. PR #25 draft/unmerged. Python 3.11 full, Goldens and held-out remain separate. This contract has no software-validation claim until its own SHA-pinned CI passes.
