# I3 R2.4: response-custody strictness and common-domain rollback negative control

**Date:** 13 November 2026. **Type:** prospective software-only engineering falsifier, no new scientific source, Life, cohort, World or release authorization. **Parent:** [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339), [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331).

## Baseline and trust model

The existing [R2.4 committed-anchor result](R24_COMMITTED_ANCHOR_CONTRACT_RESULTS_2026-11-13.md) used a **volatile in-memory test pin**, not an off-host trusted M11 service. The same process can supply or overwrite the pin. The remote loopback authority continues to hold a rollbackable SQLite database and shares an HMAC test key with the client. HMAC verifies only within that assumed key trust boundary; it cannot attest independent operators, secure storage, or external motor exactly-once.

No changes may touch `Mind`, `World`, `BodyLaws`, original scientific cohorts, source indices, registration, or the existing `commit_anchor=None` behavior.

## Frozen falsifiers before writing the tests

1. **Signed response state confusion.** A syntactically canonical, correctly HMAC-signed remote response with a `COMMITTED` phase must have **both** pending fields exactly `null`. A `PREPARED` response must have `terminal=OPEN`, a strictly integer pending sequence exactly one after the committed sequence (not `True` masquerading as `1`), and a 64-character pending intent digest. Any violation is a fail-closed protocol error even if an artificial test server signs it.
2. **Cross-request response replay.** A response authenticated to nonce N1 must fail if replayed with an otherwise valid new request using nonce N2. No caller should reach a motor from such a reply. Tests synthesize signatures with a **test key only**, not a real security credential.
3. **Whole trust-domain rollback negative control.** Capture legitimate local birth, local journal, remote authority SQLite and volatile test pin after native sequence 1. After sequence 2, replace **all four** with the old version. The currently unprotected software boundary is expected to **accept** the old coherent view. Label this `FAIL_INDEPENDENT_M11`, never anti-rollback PASS. If an implementation unexpectedly refuses the old state, identify the other hidden surviving state before promoting any claim. No new operating system trust domain is provided.
4. **Positive control.** The existing test which restores the three SQLite stores but retains a newer pin must continue to **reject** pre-motor; loss of the pin and an ambiguous remote commitment must continue fail-closed without silently retrying a native action.

## Smallest source modification

Tighten the response value validation in `src/i3/runtime/engineering_remote_witness.py` only; no wire-schema update, no new privilege, no implicit retries. Add source-isolated pure software response tests and one additional explicit common-domain rollback negative control to the existing engineering fixture.

## Acceptance and stopping

Exact commit Python 3.11 and 3.12 I3 software CI and navigation should PASS. Keep a detailed fault matrix `PASS` (protocol checks), `FAIL_INDEPENDENT_M11` (deliberate common-domain rollback counterexample), and `NOT_RUN` (real off-host host/secrets/backup/throughput). No M11 release or I3 engine activation regardless of CI green. Preserve Stage 2.1 scientific `NOT_ISSUED`, P1.3 funded-v2 and I1 active.

If protocol hardening breaks existing legitimate remote responses, do not weaken the state invariants; investigate the schema mismatch and stop until corrected. 
