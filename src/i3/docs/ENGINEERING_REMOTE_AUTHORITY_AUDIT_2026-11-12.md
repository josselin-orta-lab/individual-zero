# I3 R2.4: audit-chain consistency for the loopback monotonic authority

**Date:** 12 November 2026. **Parent:** [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339), and its R1/R2 [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331). **Baseline:** `main` `288b42f1c9c23616d759c7218b722f1b29b0b56e` / [PR #1338](https://github.com/josselin-orta-lab/individual-zero/pull/1338). **Mode:** engineering, loopback, source-pinned software only. **Not:** a born individual, an independently deployed M11, an authorized scientific World, or a Stage-2 survival conclusion.

## Exact problem and falsifiers

The existing remote CAS authority saves the latest `seq/head/phase/terminal` in a **single mutable SQLite row**. A privileged local operator or accidental corruption can edit that row without preserving the original transitions. Because this server is only loopback test infrastructure, nothing outside its rollback domain attests to which head was most recently committed.

**Hypothesis H1, narrow engineering:** preserving a second, hash-chained transition record inside the same SQLite transaction permits the test server to detect **partial** modifications of its current head or its original transition log, without affecting the native I3 decision path. A `register`, `prepare` or `commit` must atomically publish the new CAS state and its linked audit event, or neither. `verify` must validate both but must not append. A damaged chain or header must refuse the next network command and refuse service startup.

**H1 falsifiers:** a changed live head with an unchanged audit history is accepted; a removed, reordered, gapped, or modified audit event is accepted; a changed authority identifier is accepted; a failed audit still lets CAS advance; or history crosses a death/terminal/horizon boundary.

**Critical independent-anchor falsifier H2:** restoring a **complete old copy of the same SQLite file**, including both latest-head and audit rows, remains accepted. H2 is an intentionally **negative** result, showing that this implementation **does not** satisfy #1339's off-host, non-common-rollback-domain requirement. A SHA-256 chain is not a signature, a permission system, a trusted timestamp, or protected monotonic memory.

## Contract and changes

- `i3.lab.engineering_remote_authority.AuthorityStore` moves the **engineering test-only** DB schema from `i3-remote-cas-authority-store/v1` to `v2`, with a new `audit(ordinal, previous_sha256, event_json, event_sha256)` table. **No migration or silent acceptance of the old v1 store**: separate archived test databases remain non-executable for this new source. This does not modify historical experiments or I3 generation identity.
- `register`, `prepare`, and `commit` append a canonical JSON event **within the same `BEGIN IMMEDIATE` SQLite transaction** as the CAS update. Each event links to the previous SHA-256; the first event uses a publicly derived, authority-ID-specific genesis digest. No new network endpoint or new response property is introduced.
- Before every command, on server startup, and again before committing any new transition, a strict verifier validates the schema and authority identity, ordinal continuity, canonical bytes and hash links, typed transition chronology, terminal/horizon invariants, and an exact projection of the last event **per I3 identity** to the current rows in `histories`. Events for different engineering life claims may interleave in the one authority-wide chain. Invalid history raises `PermissionError`; the signed HTTP test server returns a refusal instead of a new custody receipt.
- No code path constructs a new `Mind`, `World` or scientific life, alters `World.step`, imposes a motor or changes P1.3 `CognitiveBudget`. `src/i3/runtime/engineering_remote_witness.py` retains its original protocol format and trust assumptions. I1 stays the registered active engine and I3 stays an unregistered architectural reference.

**Terminology warning:** “append-only” refers to the **normal application writer**. A privileged SQLite operator can update/delete rows or rewrite every digest and the matching head. It is neither storage-enforced immutability nor an independently authenticated append service.

## Verification and negative control

The new `tests/i3/test_engineering_remote_audit.py` runs no World or Mind. It exercises an actual signed loopback HTTP refusal on a corrupted authority row and covers a clean `register -> prepare -> commit` and cold reopening; changed live head; changed audit digest; removed final event; changed event ordinal; changed authority metadata; interleaving two independent engineering claims; terminal death; and, crucially, **acceptance of a fully rolled-back authority database**. The last test must not be interpreted as a security PASS: it deliberately reproduces the missing anti-rollback guarantee.

During isolated local development with Python 3.13, **20/20 tests passed**: the 10 new audit/HTTP tests plus the 10 existing subprocess-backed remote transport tests. This is **not repository-wide CI**; full GitHub I3 software checks on Python 3.11 and 3.12 must validate the exact PR source before merge. Historical native integration tests, old original study sources, authority lists, and source-index authorizations are unchanged.

**Preliminary environment-dependent microbenchmark (no World/Mind or network):** the server's register + two SQLite CAS transitions per step at horizon <=100 took roughly 4–11 ms/step in the local Python 3.13 container for sample lengths 10–100. The pre-audit local reference produced similar magnitudes on this same run; these one-off figures are **not hardware-normalized, reproducible throughput limits, i3 cognitive costs, or an improvement claim**. The audit verifier scans historical events before each write, so total verification work grows superlinearly with history length. The older I3 step-ledger also performs full-chain validation. Do not deploy a large lineage from this path without a separately justified, measured bounded-state/periodic audit design and custody-preserving proof.

## Decision and exact next release gate

**ACCEPTABLE narrow result:** local signed-CAS test service detects partial history/state corruption and fails closed before issuing more motor permission. **NOT_ISSUED:** independent monotonic M11 authority, source/writer attestation, external motor exactly-once, remote database rollback protection, authenticated long-lived individual, and scientific Stage 2.1 value.

Next, #1339 must establish a **separately administered off-host trust domain**, protected server identity and managed key rotation, external immutable/high-water witness or secure monotonic counter, and crash/partition/credential/rollback experiments. The primary negative control is still full server-database rollback with all credentials and local files. A real positive claim requires that this combined attack be rejected **because of independent evidence**, not by renaming the local SQLite audit chain.

Existing P1.3 funded-v2, native action authority, all original Stage-2 cohort locks, `reference_generation=I3`, `active_generation=I1`, `src/i3/engine.json` proposal/no entrypoints, and scientific `NOT_ISSUED` remain unchanged. **New scientific Worlds: 0.**
