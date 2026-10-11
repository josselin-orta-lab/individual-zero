# Stage 11: external physical arrival beyond geographic ledger capacity

**Technical test contract recorded before its implementation, 2026-10-11.** Public deterministic software-development fixture only. Not a scientific preregistration, held-out observation, Golden, safety certification or Stage 9 verdict. The normative authority remains `docs/architecture/reference/en/mvp-specification-v1.2.1.md` (world/scenario input separation, physical provenance, DC-07, DC-08, INV-08, life snapshots).

## Failure and scope

The geographic `max_distinct_sites` parameter bounds Exploration's *record of distinct sites*. It does **not** determine where WorldBody may physically be, and is not a body movement capability. Direct `GeographicExploration.observe_capture` currently rejects a novel site at full capacity atomically, but `Stage11Runtime.run_step` propagates that exception after opening the physical step. No completed world step, safe continuation, or full-owner snapshot was established for an external physical arrival beyond the cap.

## Fixed software contract

1. An explicitly scheduled, logged *world-only* external `set_position` scenario input may put the physical body at a valid unobstructed interior location. It is not an autonomous `se_deplacer` command or a learned ability; malformed, out-of-bounds or obstacle positions must fail without mutating WorldBody. The external input must appear in the causal journal before the immutable local Perception capture.
2. Preserve the existing atomic **owner-level** `ValueError` on over-cap new site, including pending transit and the existing bounded snapshot. Use a distinct exception type so the runtime can recognize capacity overflow without swallowing malformed chronology or captures.
3. At the Stage11 **runtime** boundary, account for the actual Perception capture even if its novel position cannot fit into the bounded Exploration registry. Log an explicit, per-step `unregistered physical capture at capacity` event. Do not invent an owned visit, local survey, route target, intrinsic reward, canonical hazard status, or autonomous movement. Invalidate any stale optional geographic offers. Preserve the real WorldBody/Perception position and continue ordinary Action Control, reflexes and other owners.
4. The owner snapshot continues to reflect the last *registered* physical site, while WorldBody's causal snapshot records its actual current position and the scenario owner records the external input cursor. A complete SnapshotManager checkpoint after the step must round-trip all owners exactly; the append-only journal is never rolled back.
5. Demand-driven route search must remain suppressed at a full visit ledger with no route UC spent. On subsequent real captures of previously registered positions the owner may resume ordinary registered-site observation; on further unknown over-cap captures there is no false registered visit or reward. Stage9/default geography-disabled behavior remains unchanged.

## Fixed public unit inputs

- Start from the existing known-public `junction_open` observed-routing fixture with survey refresh; set the Stage11 geographic ledger cap to **one** before birth, with a separately versioned config.
- Run world step 1 from (2,2). At **world step 2**, inject `ScenarioEvent(sequence=1, operation="set_position", payload={"position":{"x":4,"y":2}})`; (4,2) is the publicly declared eastern dead-end site. Run through **world step 3**.
- Check external-input provenance and real Perception position for step 2, single bounded registered visit with no unearned reward, no route-search UC, one capacity diagnostic for the step, and hash-chain integrity.
- Take a full-owner periodic snapshot at the step-2 boundary, advance, restore and compare all causal owners exactly. Verify two independently instantiated runs of the same scenario produce identical normalized journal bytes and owner states.
- Independently check that an invalid exterior/obstacle/malformed `set_position` is rejected without WorldBody mutation, and an owner-level over-cap new capture remains atomic.

No claim is made about arbitrary real-world teleports, unknown dangers, lethal scenario insertion, generalization, Python 3.11 reference, long Goldens, or independent Stage9 held-out acceptance.

**Before implementation: unverified. Stage 11 IN PROGRESS. Stage 9 scientific NO-GO. PR stays draft/unmerged.**
