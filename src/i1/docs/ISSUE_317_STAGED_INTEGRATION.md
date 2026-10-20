# Issue #317: selective main integration, stable memory candidate identity

This document records a **software integration decision**, not a new scientific or behavioural demonstration. The frozen research branch PR #318 is not merged wholesale.

## Approved isolated change

For a remembered, personally witnessed entity-place, the local one-hop option ID is now `option:place-memory:{target.ref}`. The canonical `SpatialReturnTarget.ref` encodes the observed entity-place, current origin and immediately perceived next hop. It deliberately does **not** encode the latest world-step number. Across successive cycles, unchanged local intentions can therefore retain bounded, previously accumulated Competition evidence rather than being re-created with a fresh key at every step.

Only identifiers change in this lot. The current capture and `source_t_monde` remain checked by Planning and Stage11; each proposed hop still passes the one-step local simulator, Action Control, and current Competition admission. Material plan changes reset non-engaged evidence; route changes and alternate observed entities receive different IDs. Candidate invalidation, finite expiry, capacity, active-goal matching, M11 and irreversible death remain unchanged.

This lot intentionally **does not** promote PR #318's additional frontier-key changes, goal-independent memory motivations, multi-hop residual carryover, experimental relevance/TD adapters, alert sleep guard or population scripts. Those are separately reviewable. Existing merged PR #320 already isolates fallback adjudication.

## Technical validation

`tests/i1/test_i1_317_stable_memory_identity.py` executes against the generated I1 sources. It checks same-local-hop identity across steps, distinct options for changed hops and personal sightings, rejection of stale time, current-offer matching, Competition evidence retention and invalidation on goal change. The exact-source Git blob pins for the three modified owners must pass `scripts/test_i1_artifact_parity.py` in standard I1 CI (Python 3.11/3.12).

Unit and integration tests are software evidence only. They do not establish useful behaviour, survival gains, physically completed remembered routes or scientific GO; no further population or behavioural campaign is part of this integration.
