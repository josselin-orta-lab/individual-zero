# I1: experimental descendant of I0 (initial immutable-source snapshot)

**Source:** `main` at `8ce8711b2d5f86b184d66fcee1d95a3e39f30836`.  
**Copied tree:** 71 I0 source files, byte-identical, under `src/i1/`.  
**Branch:** `experiment/i1-isolated-model-fork-20261016`.

## What this commit establishes

This is a **baseline fork**, not a separately functioning autonomous cognitive individual yet. Each copied `src/i1/<relative-path>` starts with the exact blob of `src/i0/<relative-path>`. In particular, existing absolute Python imports inside the copies may still point to `i0`, and `src/lab` currently assembles I0 modules. Consequently, it would be **false** to run I1 as a supposedly independent actor at this stage. Do not activate a new predictor by relabeling a Stage12 I0 life as I1.

I0's packages, normative v1.3.3 specification, active planner, WorldBody laws, M11 persistence, Stage 9 DC-05 and Action Control are not changed by this snapshot.

## Implementation gates before an autonomous I1 birth

1. Audit and rewrite all internal I1 imports and runtime wiring, covering `i0`, `lab` and serialization identities. Shared physical *interfaces* may be reused without sharing an individual's cognitive owners.
2. Establish an explicitly distinct I1 runtime factory, individual/life ID namespace, separate journal/WAL or SQLite store, checkpoint identity and cryptographic custody. No I0 memory state may enter an I1 birth.
3. Keep WorldBody physics, mortality, irreversible command execution, Oracle/Bench separation, six cognitive phases, canonical ownership, atomic recovery, UC and Stage 9 safety identical until independently reviewed.
4. Provide I1-only opt-in predictive model at birth and a versioned, positive UC cost; never import hidden physics or unrelated laboratory examples into lived cognition. No second command sender. Unknown terminality and safety must remain unknown.
5. Add import-closure tests, genesis/cold-recovery anti-cross-identity tests, adversarial hidden-hazard and mortality tests, and paired autonomous I0-vs-I1 comparisons.
6. Run Python 3.11 and 3.12 regression gates on the exact candidate SHA. Publish results and request review **before** releasing I1 for an independent new scientific campaign.

## Disposition

**I0:** unchanged baseline.  
**I1 source snapshot:** created.  
**I1 independently wired runtime:** not yet implemented.  
**I1 new predictive model enabled:** NO.  
**I1 independent scientific GO:** not claimed.

The staged approach avoids changing the already established reference individual and makes every model change, import rewrite and behavioral deviation attributable to a separate PR and test.
