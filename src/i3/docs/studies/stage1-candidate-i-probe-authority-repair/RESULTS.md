# Candidate-I probe-restore authority repair: software PASS

Protocol:
[STAGE1_CANDIDATE_I_PROBE_AUTHORITY_REPAIR.md](../../STAGE1_CANDIDATE_I_PROBE_AUTHORITY_REPAIR.md).

**SOFTWARE ONLY. ZERO NEW LIVES. NO 62/63 REPLAY.**

Final frozen verdict:

`CANDIDATE_I_PROBE_AUTHORITY_REPAIR_PASS`

Repair-code authority:
`5ca8f2dcb7f87c18880ea3c45b773eec0daab2d4`.

GitHub Actions:
`42517714784`.

Python 3.11 and 3.12 both pass. The Python 3.11 job ran **965 tests** plus
the repository navigation check.

## U0-U9

All frozen rules pass:

- U0 custody / no 62/63 verdict;
- U1 legacy stale-authority resurrection reproduced in pure software;
- U2 rollback snapshot contains no learning authority;
- U3 prior authority is empty before the rollback snapshot;
- U4 both PROBE_UNFUNDED exits restore reversible perception/RNG state only;
- U5 FALLBACK creates fresh current-decision authority;
- U6 RELEVANT creates fresh current-decision authority;
- U7 post-contact Candidate-H parity is unchanged;
- U8 no physics, cost or scientific-rule change;
- U9 software-only authority boundary.

The frozen reproducer demonstrates the old failure mode directly: an old
rollback snapshot can restore stale `last` after the matching branch settlement
receipt has been cleared, and the repaired learning boundary correctly rejects
that mismatch.

The production repair changes the ownership boundary, not the scientific rule:

- prior decision/learning authority is cleared before the first-contact rollback
  snapshot is taken;
- `last`, pending branch storage, branch settlement and pending opportunity
  authority are absent from the rollback snapshot;
- PROBE_UNFUNDED clears any probe-created authority;
- FALLBACK restores reversible state, clears authority again, then lets the one
  real addend-free final decision create fresh current-decision authority;
- that real FALLBACK perception also recreates the current-step opportunity-
  presence receipt, matched to the lived `map/visible` perception rather than
  the detached Stage-A probe;
- RELEVANT creates current-decision authority directly;
- post-contact remains Candidate-H #1163 semantics.

The gate found a valid RELEVANT software fixture at body
`(80,20,80,80,80)`; its branch settlement is aligned with the current
decision and the persistent projector returns to `reference/chunk_end`.

## What this does not do

This PASS does **not**:

- complete 60/61 or 62/63;
- create J1-J7 evidence;
- authorize a retry of either exposed panel;
- select omega;
- alter RMS scale, V2-R1/R2, BodyLaws or cognitive prices;
- advance Stage 2.

60/61 and 62/63 remain permanently exposed and closed.

## Handoff

Two successive fresh panels were consumed by distinct engineering defects that
were invisible to shorter preflights. Before allocating another fresh
DEVELOPMENT panel, add one prospectively frozen **lifecycle-custody stress
gate** using only already-exposed software/development fixtures.

That gate should exercise, across many consecutive steps rather than isolated
single decisions:

- first-contact RELEVANT and FALLBACK routes;
- PROBE_UNFUNDED exits;
- post-contact Candidate-H routing;
- prepare-learning / learn-from-outcome;
- branch storage and opportunity storage;
- same-genome omega0 arm;
- revision reduction;
- state/settlement authority continuity across decision boundaries.

It must not use 60/61 or 62/63 originals as acceptance fixtures and must not
open any fresh World.

Only after that stress gate passes should a new fresh lived protocol be frozen.
