# I3 R2.5 / #1339: source-admitted atomic checkpoint-publication prototype, preflight

**Frozen 13 November 2026, prior to implementation.** Engineering-only demonstration; 0 scientific World, 0 life, no active I3 engine, no remote host, no protected private key, no independent M11 release. Baseline: [R2.4 signed receipt results](R24_SIGNED_CHECKPOINT_RECEIPT_RESULTS_2026-11-13.md), exact-source #1374/#1375.

## Falsifiable engineering question

Can a **test-only** signing owner maintain one serialized, durable and authenticated publication chain in a **separate SQLite file** while refusing conflicting writers, uncommitted/pending CAS states, foreign claim sources and stale publication expectations? The existing signed receipt verifier accepts an asserted `source_sha256`; before a publication is signed, each canonical `histories.claim_json` source in the *same audited read snapshot* must match the pinned issuer source. This is **local claim consistency**, NOT independent source authentication.

## Mechanism and immutable boundaries

- Preserve current `i3-remote-cas-checkpoint-probe/v1` and signed receipt `i3-remote-cas-signed-checkpoint-receipt/v1` formats. Extend `capture_exact_checkpoint(..., expected_source_sha256=...)` as an **optional read-only, fail-closed** check inside the existing read transaction. Default call behavior and all older tests unchanged.
- Add `i3.lab.engineering_remote_checkpoint_publisher` with class `TestOnlyCheckpointPublisher`, **explicitly test-only**. It accepts a callable signer and 32-byte pinned public key; never stores or loads a private key, never serves a network port, never chooses a motor, never publishes a scientific World. Publisher SQLite v1 must be a **distinct file** with strict application ID/metadata, bound authority/source/key ID/public-key digest. No implicit migration or replacement of foreign files.
- `publish(expected_previous_receipt_sha256)` performs `BEGIN IMMEDIATE` on publisher SQLite, validates every prior envelope / contiguous chain and monotonically advancing counters, requires caller's expected previous **full signed receipt** hash (64 zero characters for genesis), checks existing authority v3 with a **full read-only audit** and every stored claim's pinned source, rejects PREPARED, signs only the newly captured checkpoint with **test-supplied** ephemeral Ed25519 signer, verifies its signature against the pinned public key, enforces the forward transition and writes publication index/raw/digest in the same publisher transaction. Return only after COMMIT.
- `latest()` must verify the publication chain under a read-only publisher transaction. An unacknowledged but committed receipt can be inspected; do not silently auto-retry a paid motor. No pruning, no O(1) claim, and no cross-database ACID between authority and publisher.
- Fail closed on missing/foreign/tampered publisher, lost signer or credential mismatch, duplicate index, changed source, journal regression, noncanonical signed bytes and ambiguous pending phase. Do not implement rotation or automatic pin reset.

## Frozen fault matrix (source-local software only)

1. Genesis and next publication after a fresh accepted `verify`: exactly two stored signed receipts; indexes 1/2, correct previous full-receipt digest, key/source/authority pins, independent checkpoint equality.
2. Cold restart with retained publisher DB and same externally supplied test signer: latest verifiable; stale caller prior digest rejected.
3. Two concurrent `publish` calls with identical expected digest: exactly **one** succeeds, one fails; no duplicate index or sign-then-commit race accepted.
4. Error injected into signer or verification: no publisher row committed; later valid request can succeed with the same expected prior.
5. Pending PREPARED, foreign source claim, tampered authority journal, absent authority / replaced publisher DB: reject without new signed publication or scientific action.
6. Publisher row substitution/hash alteration and wrong key/source/authority metadata: refuse reopening; no silent initialization of foreign databases.
7. Authority SQLite restored beneath a retained newer publisher latest / external high-water: latest retained; attempting to publish stale state fails. Durable publication protects only when its **DB and external expected digest survive**.
8. **Negative:** restore authority SQLite **and** publisher SQLite to an old mutually consistent snapshot; use the old external expectation, or restore it too. Old valid state gets accepted again. This is **FAIL_INDEPENDENT_M11** despite passing the regression.
9. Actual separately administered host, protected HSM/KMS signer, authenticated transport/source release, immutable audit service, fault recovery/credential rotation: **NOT_RUN / NOT_ATTESTED**.

## Acceptance and stop

Source-exact Python 3.11 and 3.12 I3 full software CI + navigation and engine contracts must PASS before merge. Document real failures, fix and rerun at new SHA; no test masks. No key material in repo/logs. All scientific `World`/source/index/cohort permissions and P1.3 funded-v2 remain unchanged; I3 reference and I1 active; Stage 2.1 `NOT_ISSUED / HOLD_NO_VERDICT`; #1339/#1331 remain OPEN. A software PASS does not prove actual independent M11.
