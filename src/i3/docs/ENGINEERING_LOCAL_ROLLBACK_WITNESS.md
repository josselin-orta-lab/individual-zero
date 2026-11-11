# I3 R2: separate-local-directory two-phase rollback witness

**Research/engineering boundary, 12 November 2026.** I3 is the owner-selected development reference (`reference_generation=I3`), while I1 remains the registered active runtime. **This is an engineering-only witness of local custody order, not an external authority, M11, native promotion, new scientific World or survival result.** It complements the deterministic native cold reconstruction and the original two-phase ledger in [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331).

## Exact question and bounded result

Previously, a completely valid *old* copy of the ledger and birth reservation could replace newer local files; deterministic replay would then reproduce the old history without knowing that a later motor was ever sealed. A *second, independently managed local directory* can detect this particular failure **only when its own state is not rolled back**. The new `engineering_rollback_witness` records the expected latest committed `(identity, source, genome, world, seed, horizon, sequence, head, terminal)` and a PREPARED marker before the next native `World.step`.

The native engineering session now has an **opt-in, mode-bound** `witness_directory` argument for `begin` and `reconstruct`. The updated R2 step ledger records `witness_mode` at genesis and includes it in its hash root. A previously witness-bound session **cannot be reconstructed or stepped via this native API without the witness**; an explicitly UNANCHORED engineering session retains its old local-only semantics. This is a fail-closed schema revision (`i3-engineering-step-ledger/v2`): pre-existing v1 engineering ledger files are **not silently migrated** to v2, and no authenticated original history is rewritten. There is no activation or production API.

## Pre-action and post-action chronology

| Phase | Durable local ledger | Separately located witness | Next action? |
| --- | --- | --- | --- |
| Genesis | COMMITTED sequence 0 | register same source/identity/head/sequence | Yes, only if both match |
| Before action | PREPARED intent | still prior COMMITTED | **No motor yet**, failure blocks local ledger |
| Before action, phase 2 | PREPARED intent | PREPARED matching intent digest and prior head | **Now** native motor may run once |
| After native motor + paid learning | COMMITTED post-paid receipt, new head | still PREPARED | **No** continuation while witness lags |
| After witness commit | COMMITTED new head | COMMITTED same new head and terminal | Next action only if open, fully matched |
| Crash/mismatch | any missing/uncertain phase | mismatched or unavailable | **Fail closed**; no automatic reconciliation |

The intent digest is a canonical SHA-256 of immutable prior head, identity, sequence and full proposed native intent; it is **not a signature**. The witness's own SQLite database uses a separate file, `I3WT` application ID, strict schema, WAL + `synchronous=FULL` and `BEGIN IMMEDIATE` CAS transitions. The witness directory must preexist, be different and non-nested relative to the life directory, and cannot be a symlink. Both stores retain independent local transactions. There is deliberately no automatic catch-up from a prepared or lagging witness because it is not generally possible to prove whether an action actually happened after a crash.

## Adversarial falsifiers, including an explicit negative limit

1. If the **ledger alone** is restored from a valid snapshot of sequence 1 after sequence 2 was witnessed, the local ledger passes its own checks but reconstruction is **rejected by the witness**.
2. If **PREPARED** is written in either store and the process crashes before sealing the outcome in *both*, continuation is rejected. A crash before the witness PREPARED can leave a pending ledger, but the native path has not yet executed the new motor.
3. If the native motor completes and the ledger seals, but the witness commit fails, the completely sealed ledger **still cannot be reconstructed** through the witness-bound API. This sacrifices availability in favor of an honest unknown outcome.
4. A foreign, altered, missing or same-directory witness is rejected. A terminal death/horizon prevents a further action through the existing native ledger gate.
5. **Explicit negative capability test:** roll back *both* independent-looking local SQLite files to a mutually matching previous snapshot. They still match! This is **not detected**. Nothing in these files proves global monotonicity or prevents a privileged actor from replacing both; an off-host durable append authority, trusted hardware counter or similarly independent witness would be required to claim genuine anti-rollback.

## Verification and nonclaims

Focused isolated tests exercise the ledger and witness without constructing Worlds; native tests additionally use the **existing isolated development world** and actual `Mind.decide -> World.step -> prepaid learning`, comparing source/receipt history and a second Python process. The exact-source Python 3.11/3.12 CI result is the acceptance gate, not local syntax checks. These are software/engineering studies only; **no scientific cohort was authorized**.

The witness adds two more full-synchronous SQLite state changes per native tick (four durable transitions across the pair), plus full-chain validation in the ledger. It is **not** a measured performance improvement or a scalable long-lineage M11 replacement; throughput and repeated reconstruction costs must be measured and reduced without erasing correctness.

**Technical successor:** separate machine/service-backed monotonic publication with immutable externally controlled credentials, crash-boundary tests across the network, no replay of external motor side effects, root-to-head authentication and validated source/attestation; plus a durable native state codec or bounded deterministic checkpoint strategy. Only then can an independent release proposal consider an active I3 entrypoint. The Stage 2.1 scientific verdict remains `NOT_ISSUED`, and E3's candidate-specific negative results stand.
