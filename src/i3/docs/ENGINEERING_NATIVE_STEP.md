# I3 R2/R3: a native-reference, paid engineering step with local two-phase custody

**Date:** 11 November 2026. **Scope:** isolated software integration of the existing P1.3 `Mind`, `World`, `CognitiveBudget`, funded outcome learning and the R2 local `PREPARED` / `POST_PAID_LEARNING` journal, under [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331). **Not** a scientific experiment, production engine activation, an authenticated M11 journal or a cold-resumable organism.

## The technical question and a falsifier

Can **one real in-process native P1.3 action** be selected using only I3's first-person capture, pre-declared and paid from its own E/V allowances, applied once by the native `World.step`, followed by prepaid learning, with its actual post-paid body/terminal receipt sealed into an independent local ledger? If an exception occurs after PREPARED and before sealing, the same session must fail closed rather than replay the uncertain motor.

**Falsifiers:** a caller chooses the motor outside `Mind.decide`; the first-person Mind sees hidden `WorldSpec` data; `World.step` occurs before durable `prepare`; cognition is learned before it is paid; the sealed body differs from the native World's actual body; a second motor executes after a failed/incomplete/terminal step; an altered in-memory Mind/World is accepted without an evidence mismatch; or a different genome/world/source can reuse the same engineering claim.

## Implementation boundary

`src/i3/runtime/native_engineering_session.py` adds one deliberately **ephemeral** `NativeEngineeringSession.begin(...)` / `.step()` path. A fresh session binds a local claim to the exact on-disk I3 `.py` source checksum, genome, world spec and life seed; the world spec is available only to the **constructor/observer**, not to Mind. The exact P1.3 reference `Mind` and `World` are constructed with no experimental policy or observer influence. The ledger requires a previously consumed one-shot engineering slot, but no scientific source/index permission is minted.

Each `.step()` checks local ledger head, tick and previous body, plus the prior committed *fingerprints* of the existing in-memory Mind/World. Then it:

1. captures `World.capture()` and calls `Mind.decide(capture, CognitiveBudget(...))`;
2. writes a `PREPARED` intention with actual native decision-work counters **before** the one `World.step`;
3. observes the real motor result, prepares a second budget for outcome learning, pays it through `World.pay_cognition` **before** calling `Mind.learn_from_outcome` (only when alive and funded);
4. derives the two E/V payment receipts and real post-learning body/death from the native World, calculates read-only deterministic Mind/World/RNG state hashes, then calls `seal` for `POST_PAID_LEARNING`;
5. permanently stops the in-process session on any exception or terminal event. No rollback, new motor, or recovery override exists in this API.

The native state checksums are strictly typed/canonical JSON fingerprints for the explicit current I3 reference objects, with RNG `getstate`, deque and typed mapping keys, and finite floats only. They **cannot** deserialize or reconstruct a Mind or World. Source bytes/Git status, local SQLite files and hash chains are **not independently authenticated** or resistant to an off-process rollback of all files. A prepared-but-unsealed step **intentionally blocks** cold continuation.

The original, evidence-pinned `src/i3/runtime/life.py` is **unchanged**. Its ordinary native reference decision -> motor -> paid learning chronology is used for short-run parity tests. No experimental replay-gate admission or consumed original is ever called by the new implementation.

## Engineering test matrix

`tests/i3/test_native_engineering_session.py` covers:

- three real native World/Mind steps with postpaid E/V, hash and ledger-state parity, horizon closure;
- action, motor parameter, per-step body and final body parity against a **separate** one-shot `run_life(..., decision_policy="reference")` execution using the existing `dev_long_corridor()` fixture, never a scientific Stage-2 source;
- injected fault in the native `World.step` **after durable PREPARED**, followed by fail-closed local inspection, in-process refusal and rejection of the same claimed birth index;
- mismatched source/world/genome before reserving any slot;
- in-memory learned-state tampering caught **before** another World motor;
- real physical death at the first action and no postmortem continuation/learning;
- absence of cross-generation runtime, pickle, or any `recover`/`resume` entrypoint.

**CI acceptance:** Python 3.11 and Python 3.12 complete I3 proposal software suites on the exact PR SHA, all 7 new integration tests included. If any test fails, diagnose and fix without changing the archived original runner or scientific cohorts. Local isolated syntax/fail-closed checks do **not** replace repository CI.

## Addendum: source-pinned deterministic local reconstruction

A later engineering-only implementation adds [`NativeEngineeringSession.reconstruct`](ENGINEERING_DETERMINISTIC_RECONSTRUCTION.md), which repeats the **previously sealed** reference motor/learning path on a detached World and verifies every historical intent and receipt before returning a new in-process session. A real second Python process test exercises this route. It does **not** persist an authenticated M11 state or allow interrupted PREPARED steps or terminal lives to continue. The original one-shot engineering result and its limitations remain historically applicable to its initial SHA.

## Remaining R2/R3 requirements before production I3

A genuinely release-ready native generation still needs an **explicitly versioned, safe-to-load codec** for the full mutable Mind/World/RNG, a generation-owned writer and independently anchored monotonic receipt/anti-rollback control, crash injection on both sides of native motor/payment/commit, source-locked cold-process reconstruction and exact continuation parity, and performance instrumentation avoiding the present full-chain O(n²) total verification cost. M11 and active-engine registration remain NOT DEMONSTRATED.

I3 remains the **owner-selected development reference**, while `active_generation=I1`, I3's registered `entrypoints={}` and `scientific Stage 2.1 = NOT_ISSUED` remain unchanged. This engineering fixture creates only new, isolated **technical test worlds**, never a scientific population, registered individual, E3 rerun or permitted new research cohort.
