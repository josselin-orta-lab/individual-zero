# I3 R2.10: strict custom TLS context on engineering remote CAS writer, exact CI results

**Date:** 13 November 2026. **Bounded software result:** `R210_CUSTOM_TLS_WRITER_CONTEXT_FAIL_CLOSED_PASS`. **Independent off-host M11:** `NOT_ATTESTED`, prior coherent `FAIL_INDEPENDENT_M11` unchanged. **Science:** Stage 2.1 `NOT_ISSUED / HOLD_NO_VERDICT`.

## Preannounced source and independent CI check

- [R2.10 preflight](R210_TLS_CAS_WRITER_CONTEXT_PREFLIGHT_2026-11-13.md) was committed **before code** at `83d0a5a93dcfe323ac03e51ff5b3e8eacf546b19` from main `d3662d2e7e0ce7b0f3ea218312826cdfb88a4940`.
- [PR #1386](https://github.com/josselin-orta-lab/individual-zero/pull/1386), exact CI-tested source head `384d3312fce31de4cdcaf7dccbe68df5dbd4ac5e`, squash merged to `main` as `3c4c129b6ea268574930540ff9d06c95ddd30c2b`.
- [GitHub Actions #43496420728](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43496420728) **SUCCESS** at that exact head:
  - Python **3.11** job `132130594144`: **1,402 / 1,402 I3 tests PASS**, 169.674 s, all eight R2.10 tests executed and passed, generation ownership/contracts PASS, entrypoint navigation 540 checks PASS.
  - Python **3.12** job `132130594396`: **1,402 / 1,402 I3 tests PASS**, 147.688 s, all eight R2.10 tests executed and passed, generation ownership/contracts PASS. Navigation step is conditional on 3.11 in this workflow.
  - All scientific developmental cohort jobs remained skipped; no new scientific World, Mind experiment, original or source-index permission was opened.
- This post-merge report is **documentation-only**, not part of the software CI head. No direct local I3 tests ran in the agent execution container (GitHub DNS unavailable).

## Exact software behavior and falsifiers

`RemoteEngineeringWitness` already required HTTPS outside a deliberately opted-in `127.0.0.1` HTTP test. Before this fix it accepted an injected `ssl.SSLContext` after checking only its type, so `HTTPSHandler` could use an unverified context without certificate or hostname checking. R2.10 checks an explicitly supplied context **before any request**: `verify_mode == CERT_REQUIRED`, `check_hostname is True`, and explicit `minimum_version >= TLSv1_2`. An explicitly supplied TLS context is rejected on plain HTTP even in test-only loopback. HTTPS without a custom context continues using Python's default verified HTTPS handler; no transport or CAS wire schema changed.

| Precommitted control | Exact software observation |
| --- | --- |
| Strict CA/hostname-verifying TLS context with explicitly configured minimum TLS 1.2 | **ACCEPT construction** for HTTPS, no network/motor executed in constructor test |
| Custom context with `CERT_NONE` / disabled hostname verification | **REJECT before network** |
| Custom context with `CERT_REQUIRED` but disabled hostname check | **REJECT before network** |
| Context minimum TLS 1.1 or unbounded supported minimum | **REJECT before network** |
| Non-`SSLContext` object | **REJECT before network** |
| Explicit TLS context paired with test HTTP loopback | **REJECT** (no false TLS assurance) |
| No custom context on HTTPS | **ACCEPT construction**, actual HTTPS handshake not performed by these new tests |
| Bare HTTP outside explicit loopback opt-in | **REJECT**; opt-in test loopback still constructs |
| Existing remote CAS registration/prepare/commit, nonce, two-phase native motor and terminal suite | **PASS** under both Python interpreters; software-only |
| Actual external mTLS writer, operator-pinned CA, distinct host, protected monotonic store, rollback/crash/partition evidence | **NOT_RUN / NOT_ATTESTED** |
| Coherent rollback of local stores + loopback authority/witness state | Previous **ACCEPT** negative remains `FAIL_INDEPENDENT_M11` |

## R2/M11 release decision

**Accept R2.10 as a narrowly scoped transport security correction only.** It does not prove an authenticated external witness service, CA pinning to an independently vetted operator, a loaded mTLS writer identity, secret rotation/revocation, protected key custody, non-rewindable remote high-water, cold full Mind/World/RNG/body recovery or native motor exactly-once across arbitrary power loss.

The operational dependency now has a [concrete off-host release and fault matrix](OFFHOST_M11_INDEPENDENCE_RELEASE_GATE_2026-11-13.md), published in [PR #1387](https://github.com/josselin-orta-lab/individual-zero/pull/1387) as `d59887bce506edfe81ec92d1064d6b171f3d376b`. This specifies independent administrative domains A/B/C and the mandatory primary test: restore local stores and server working state while a separately governed high-water remains newer, then demonstrate **STOP before native motor**. This operational evidence has **not been executed**; the gate stays `STOP_NO_INDEPENDENT_M11`. Do not schedule another local signature/hash micro-proof as a substitute for protected operator custody.

Keep [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339) and parent [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) **OPEN**. `reference_generation=I3`, `active_generation=I1`; I3 `proposal/NOT_REGISTERED_NOT_EXECUTABLE`. P1.3 funded-v2 scientific Stage 2.1 `NOT_ISSUED / HOLD_NO_VERDICT`, all new scientific World/cohort/source-index permissions false.
