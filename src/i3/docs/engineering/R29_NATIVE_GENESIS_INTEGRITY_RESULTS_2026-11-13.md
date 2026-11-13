# I3 R2.9: native genesis full-state guard, exact-source engineering results

**Date:** 13 November 2026. **Engineering result:** `R29_VIRGIN_NATIVE_STATE_INTEGRITY_SOFTWARE_PASS`. **Independent M11:** `NOT_ATTESTED` and previous full-domain `FAIL_INDEPENDENT_M11` remains unchanged. **Science:** Stage 2.1 `NOT_ISSUED`, general `HOLD_NO_VERDICT`.

## Precommitted issue, source and actual checks

- [R29 preflight](R29_NATIVE_GENESIS_INTEGRITY_PREFLIGHT_2026-11-13.md) was committed **before** source/test changes on branch commit `0bac923cac1f63c5e4ddabb651a9718bf3c69373`, from main `3f3a7efcbaecdd7dcd8ad401185619b177762f60`.
- [Code PR #1384](https://github.com/josselin-orta-lab/individual-zero/pull/1384) exact tested head `51683beaf9b0becb0a8afbffe81411271fc74d41`, squash merged as `f59e896d9586809f557395bd4f9779424c066368`.
- [GitHub Actions #43488834234](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43488834234) **SUCCESS** for the exact PR head:
  - Python 3.11 job `132104306675`: **1,394/1,394 tests PASS**, 137.215 s test run; source ownership/engine contract PASS; entrypoint navigation **540 checks PASS**, zero errors/warnings.
  - Python 3.12 job `132104307048`: **1,394/1,394 tests PASS**, 171.560 s test run; source ownership/engine contract PASS and entrypoint navigation PASS.
  - Three new `tests/i3/test_native_engineering_session.py` tests actually executed under both interpreters. Scientific cohort jobs were skipped. No scientific World index or cohort was opened.
- No local test execution occurred: the separate execution container could not resolve `github.com` for cloning. The GitHub Actions result is the verified software evidence. This report is authored **after** the tested code merge, not part of its tested SHA.

## Actual code change and controls

In `src/i3/runtime/native_engineering_session.py`, constructor `__init__` retains process-local `state_hash(world)` and `state_hash(mind)` of the newly constructed native state. In `step()`, when the ledger has **no sealed events** yet, the complete live World and Mind fingerprints must still match **before** invoking `_native_decide`, `prepare` or `World.step`. After the first sealed event the existing per-event full-state fingerprint check still governs. On exceptions, the one-shot session remains stopped.

| Precommitted falsifier / control | Exact software observation | Scope |
| --- | --- | --- |
| Unpaid `Mind.values` mutation after `begin()`, before first step | **REJECT**, no `World.step`, ledger sequence 0/events empty | Changed private cognitive state denied before the virgin motor |
| Hidden `World.effects` mutation with unchanged body/tick/head | **REJECT**, no `World.step`, ledger sequence 0/events empty | Changed unobserved environment denied before virgin motor |
| Unpaid `Mind.values` mutation after virgin `reconstruct()` | **REJECT**, no `World.step`, ledger sequence 0 | Same guard covers detached reconstruction before the first new motor |
| Untouched native P1.3 `run_life` parity and paid motor/learning receipt tests | **PASS** in existing I3 suite | No intentional changes to motor authority, paid two-currency cognition or ordinary behavior |
| Mutated in-process `Mind` after an already sealed step | **REJECT** in retained regression | Sealed-state guard retained |
| Production off-host monotonic witness, issuer/operator independence, full Mind/World/RNG/body durable cold-recovery equivalence | **NOT_RUN / NOT_ATTESTED** | Not addressed by process-local fingerprints |
| Dual-local + loopback responder store coherent rollback | Prior **ACCEPT** negative remains `FAIL_INDEPENDENT_M11` | New guard does not claim independent anti-rollback |

## Interpretation and limits

**Accept only a narrow safety correction in an isolated engineering session.** It closes the specific uncovered pre-first-action in-memory drift path at sequence zero, before a fresh `PREPARED` event or paid native motor. A stored Python attribute is mutable by sufficiently privileged in-process code; it is **not an adversary-proof trust anchor**. There is no external source authentication, independent M11 operator, off-host protected high-water, mTLS writer authorization, production key custody, cross-host rollback/failure matrix, postmortem resumption or newly authorized cognitive/scientific work.

Continue [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) and [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339) as **OPEN**: the next decisive R2 proof must use a separately administered, non-rewindable remote authority with independently controlled signing identity/storage and cross-host fault injection, then separate full native cold-recovery and performance checks. Another local SHA/nonce signature test cannot establish that proof.

**Governance unchanged:** `reference_generation=I3`, `active_generation=I1`; I3 `proposal`, `entrypoints={}`, `NOT_REGISTERED_NOT_EXECUTABLE`. P1.3 funded-v2 remains scientific reference, Stage 2.1 general result `NOT_ISSUED / HOLD_NO_VERDICT`; all new scientific World, cohort and source/index permissions remain closed.
