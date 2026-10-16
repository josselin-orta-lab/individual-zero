# I1 autonomous experimental descendant: isolation and activation record

**I0 source anchor:** `main` SHA `8ce8711b2d5f86b184d66fcee1d95a3e39f30836`.  
**I1 baseline:** 71 exact source blobs copied to `src/i1`, with immutable byte-parity assertions against I0.  
**Policy version:** `i1-stage6-live-partial-prebirth-v1`.  
**Normative source:** MVP v1.3.3 V133-MDL-01..10; software research activation only, not an unconditional Stage6/9/12 GO.

## Isolation architecture

- The checked-in `src/i0` and `src/lab` modules remain untouched.
- `scripts/build_i1_fork.py` constructs `i1` and `i1lab` namespaces in a separate generated directory with a manifest of SHA-256 source/generated Python bytes; no writes into `src/`.
- The initial `i1` source snapshot deliberately remains byte-identical. `src/i1_overlays/i1_active_runtime.py` is a separate experimental Stage12 descendant built into `i1lab`; no second world command sender exists.
- `i1lab` uses copied physics with unchanged parameters/algorithms, separated from `lab`. The generated I1 M11 coordinator recognizes the I1 Stage12 descendant and explicitly walks `i1.` and `i1lab.` owner modules to preserve frozen mappingproxy custody. The original I0 M11 source remains unchanged.
- Distinct birth identities start with `i1:`, and M11 cold birth fingerprints pin the full immutable partial-model tuple, digest, cost and opt-in policy. An activation-cost mismatch must reject recovery.

## What activation currently means

`ExperimentalI1Stage12Runtime` requires a distinct mortal I1 life identity, explicit `i1_model_enabled=True`, an already-frozen, separately labeled `external_lab` factorized corpus and a positive versioned UC cost. The experimental adapter does **not** turn a six-variable forecast into `SimulationState` or a `EquipmentPrediction` and never claims safety, terminality, future adjacency or distal causal authorship.

When the original Stage6 planner cannot form a proposal, an I1-specific candidate may be offered for a **directly perceived** eligible local `berry_b` collection or visible east movement toward B, and only for a food goal. It pays the new planning charge, records a preaction forecast, and makes a one-step instrumental candidate whose risk status stays `unknown`. The candidate competes through the existing Competition accumulator and is admitted only by the existing Action Control with Stage9 causal/safety protections. It cannot ingest a berry merely from a numerical prediction. Unknown harms may still kill a mortal I1; such deaths must be measured honestly.

The auxiliary evaluator is transient only during competition; it is not an unregistered persistent cognitive owner. No new canonical owner, no extra physics transition, no unpriced operation and no external lab record is labeled as the individual's lived memory. Nothing automatically enables the option for I0 or other I1 births.

## Software evidence

| Gate | Executable test |
|---|---|
| I0/I1 bitwise source parity | `tests/test_i1_source_snapshot.py` |
| Reproducible separate build and I0 physics parity | `tests/test_i1_generated_isolation.py` |
| At least one genuine I1 Stage6 physical transition and independent journal audit | `tests/test_i1_first_physical_step.py` |
| Stage12 I1 mortal birth with enabled/disabled candidate and versioned UC declaration | `tests/test_i1_active_birth.py` |
| Distinct M11 birth fingerprint on model enablement and UC cost | `tests/test_i1_model_m11_contract.py` |
| Two committed I1 M11 world steps with cold recovery and wrong-cost refusal | `tests/test_i1_m11_cold_recovery.py` |
| Python 3.11 and 3.12 | `.github/workflows/i1-isolation.yml` |

Every CI result applies only to the exact tested PR SHA. The general CI workflow currently skips draft PRs, so it must not be represented as full MVP-wide regression.

## Scientific status / unresolved validation

**I0: reference control, unchanged. I1 active model: prototype enabled only for deliberately opted-in test births.** These tests demonstrate construction, one-step physical execution, declared computation debit and M11 serialization boundaries. They **do not yet prove** that a candidate based on the partial model wins Competition, changes an autonomous decision, improves genuine goals, calibrates uncertainty, or survives/adapts to lethal hidden hazards over long lives. The current source record includes synthetic test artifacts; a SHA-shaped digest does not authenticate an actual laboratory training corpus.

Before a scientific claim, freeze a new I1-only prospective protocol and authentic corpus custody, implement decision-witness tests and adversarial hidden-intervention mortal cohorts, independently score full WorldBody outcomes without leaking them to I1, audit UC and survival bias, verify long-horizon M11/consolidation and failure recovery, and compare against exact I0 control under matched births. Do not reclassify Stage9 scientific NO-GO or Stage12 PARTIAL until the operator explicitly approves evidence.

**PR disposition:** keep #219 in Draft until complete red-team regressions, technical review and a reliable exact-head CI. Never merge for convenience or reconfigure scientific thresholds after failures.
