# I3 R2.9 preflight: complete native genesis state before first PREPARED motor

**Declared before code/tests, 13 November 2026.** Exact starting `main` commit: `3f3a7efcbaecdd7dcd8ad401185619b177762f60` (R2.8 documentary merge #1383). Engineering-only follow-up to [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331), independent M11 blocker [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339). **Do not change the scientific programme.**

## Falsifiable discrepancy

`NativeEngineeringSession.step()` checks the last sealed receipt's complete `World` and `Mind` fingerprints **only when events already exist**. At sequence zero it checks ledger head, tick and body, but there is no prior sealed receipt. A laboratory caller can mutate an in-memory hidden `World` effect or learned `Mind.values` **after `begin()` and before the first `step()`**, while tick/body/head stay unchanged. The first new paid motor can consequently consume a state not issued by the native birth. Later detached replay may reject it, but the invalid first motor has already executed.

**Question:** can an engineering-only native birth deny *any* such changed complete state **before** the first ledger `PREPARED` write or `World.step`, without changing reference cognition, costs or an ordinary native outcome?

**Falsifier:** one changed, otherwise type-valid native genesis is allowed to reach `World.step`; a failed virgin step leaves a `PREPARED` event or increments the sequence; an untouched first step changes action/outcome relative to native P1.3; a resumed already sealed state loses its existing receipt verification; or an error silently retries/reauthorizes the birth.

## Minimal intervention

- In `src/i3/runtime/native_engineering_session.py`, at construction from `begin()` or `reconstruct()`, remember the **full deterministic in-process fingerprints** of both the native `World` and `Mind` using the already available `state_hash`. On the virgin ledger path, verify both hashes **before** decision, payment intent, PREPARED or motor. Keep the existing full sealed-receipt checks for all later steps and all source/claim/witness preconditions.
- In `tests/i3/test_native_engineering_session.py`, test an uncharged learned-value mutation and an unobserved World-effect mutation independently, while proving `World.step` was never reached, zero ledger events were prepared and the session is fail-closed. Test virgin reconstructed state too. Existing one-shot paid-motor/reference-parity, second-step mutation, crash and terminal tests remain controls.
- No new production entrypoint, native policy, source/world/genome admission, I1/I2 import, registry/manifest/permission change or scientific life. No new source or World indices. Do not modify frozen E3 or Stage-2 studies.

## Explicit limits and evidence standard

A fingerprint retained in the **same mutable Python process** is an accidental-drift guard, **not** a trusted authority against malicious code with access to the object's private attributes, not external source authentication and not a cold-resume token. It does not fix simultaneous rollback of local stores and the remote signer. Independent monotonic off-host M11, source/writer custody, operational disaster recovery and R1/R2 production release remain `NOT_ATTESTED`. `reference_generation=I3`, `active_generation=I1`; I3 `proposal/NOT_REGISTERED_NOT_EXECUTABLE`, P1.3 funded-v2, Stage 2.1 `NOT_ISSUED / HOLD_NO_VERDICT`, no scientific World permission.

**Check plan:** focused native session tests first, then source-exact I3 CI on Python 3.11 and 3.12 and generation/navigation checks; report `PASS/FAIL/NOT_RUN` and exact SHA. A green CI is software evidence only.
