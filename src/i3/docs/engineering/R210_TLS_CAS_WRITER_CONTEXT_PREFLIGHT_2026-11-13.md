# I3 R2.10 preflight: reject non-verifying TLS contexts in the CAS writer client

**Frozen before code/tests on 13 November 2026.** Baseline `main`: `d3662d2e7e0ce7b0f3ea218312826cdfb88a4940` (R2.9 results). Engineering-only source: `src/i3/runtime/engineering_remote_witness.py`. Related release blockers: [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339), [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331).

## Falsifiable security defect and expected observation

The CAS network client `RemoteEngineeringWitness` currently accepts an injected `ssl.SSLContext` after checking only its Python type. For `https://` a caller can supply an unverified context (`CERT_NONE` / `check_hostname=False`) and this same object is used by `urllib.request.HTTPSHandler`. The engineering writer could therefore contact a substituted TLS peer even though its source claims HTTPS. HMAC application authentication still has separate properties; HTTPS transport identity is **not** enforced as described. This is a defect in source/tooling security assumptions, not a biological or cognitive observation.

**Question:** can an HTTPS writer reject disabled certificate verification, hostname verification, and obsolete TLS minimums at construction, without changing authenticated message bytes, native motor sequencing, loopback test transport or model cognition?

**Falsifier / stop:** any explicitly supplied unverified context reaches a network request; a valid certificate-verifying TLS context is rejected; HTTP is newly accepted outside explicit `127.0.0.1` test opt-in; an HTTP-only test context is incorrectly used to infer HTTPS protection; an existing CAS/ledger/terminal test regresses; or documentation labels a protected off-host M11 release.

## Narrow change and precommitted tests

- Validate any explicitly supplied HTTPS `ssl.SSLContext` before installing it: `verify_mode is CERT_REQUIRED`, `check_hostname is True` and `minimum_version >= TLSv1_2`. No client private key or certificate is loaded or stored by this code. Existing default `HTTPSHandler(context=None)` still relies on Python's default verified context; it is not an operator-pinned CA.
- Reject an explicitly supplied TLS context on the **HTTP loopback** test path to prohibit mistaking it for a security check. Do not alter `RemoteEngineeringWitness` operations, HMAC, nonce, `NativeEngineeringSession`, source World/Mind or database schema.
- Add constructor-only no-World regression tests in `tests/i3/test_engineering_remote_witness.py`: valid TLS-client context accepted for an HTTPS origin; `CERT_NONE`/hostname-disabled denied; a TLS client with deprecated minimum denied; a TLS object on loopback HTTP denied; a wrong-type context denied. Preserve existing separate-process CAS and exact remote-before-motor tests.

**Ablation/control:** the unchanged default verified HTTPS path and the already opt-in plain HTTP loopback positive control. No new test World, identity, scientific run or source index.

## Trust limits and acceptance

This closes the client-side **custom SSL context** bypass only. It does not establish a separately administered host, operator-supplied CA pin, client mTLS/writer certificate, key revocation, protected remote storage, HSM/KMS, immutable high-water, external disaster recovery or a complete native Mind/World/RNG/body cold release. Default public CA trust is not an independent M11 source attestation. The existing coherent local + server rollback negative remains `FAIL_INDEPENDENT_M11` and must not be relabeled positive.

Required software evidence: Python 3.11/3.12 source-exact full I3 CI (focused regression plus existing CAS suite and navigation) after edits. Report PASS/FAIL/NOT_RUN, tested commit SHA, observed test count and exact authority of changed files. `reference_generation=I3`, `active_generation=I1`; I3 `proposal/NOT_REGISTERED_NOT_EXECUTABLE`, P1.3 funded-v2, Stage 2.1 `NOT_ISSUED / HOLD_NO_VERDICT`, all new World/cohort/source permissions false.
