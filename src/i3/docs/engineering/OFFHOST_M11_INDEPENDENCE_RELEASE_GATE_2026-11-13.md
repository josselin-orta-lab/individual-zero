# I3 R2 / M11: off-host independence release gate (proposed operational contract)

**13 November 2026. Status: DEPLOYMENT NOT ATTESTED, not an execution permit.**
Starting source `main d3662d2e7e0ce7b0f3ea218312826cdfb88a4940`.
Parent [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331), critical-path [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339); [ADR-0020](../../../../docs/decisions/ADR-0020-i3-owner-selected-development-reference.md).
This narrows the *deployment evidence needed for independent M11*. No cloud account, physical host, operator, key, source approval, World, life or new authority has been created by this document. It is not a replacement for the accepted engine contract, native recovery, or scientific studies.

## 1. Actual negative that must be defeated

[R2.8 results](R28_ONLINE_WITNESS_CHALLENGE_RESULTS_2026-11-13.md) establish a **FAIL_INDEPENDENT_M11** counterexample: restore both local SQLite stores **and** the loopback responder's latest receipt to an older internally consistent version, then let a valid online key sign a *new* nonce. TLS, challenge signature and publisher signature all verify, and the old state is accepted. The [R2.9 process-local native fingerprint](R29_NATIVE_GENESIS_INTEGRITY_RESULTS_2026-11-13.md) has a different, deliberately narrower purpose. Another in-process hash, nonce or self-signed badge cannot remove the common-administrator rollback threat.

**Primary operational falsifier:** while an independently retained newer high-water state exists, rollback of local identity/journal plus the remote working DB/online responder and a live signing key must be denied **before any new native motor**. All-state rollback including the purported external high-water must be administratively and technically prevented or independently detectable under the declared operator adversary. If the same principal can restore *every* store and key, independent M11 is **FAIL**, irrespective of green CI.

## 2. Three explicit trust domains, no phantom independence

| Domain | Owns | Must not control | Required evidence |
| --- | --- | --- | --- |
| A: native I3 writer | New I3 birth identity, first-person Mind/World/body/RNG, local two-phase ledger, bounded writer client credential | Off-host append-only anchor, witness issuer/online responder private keys, recovery authority | Native source/build SHA, isolated I3 credentials, exact one-motor PREPARED and post-paid COMMITTED trace |
| B: remote witness service | Authentication of one authorized writer/source, CAS phase and sequence, online responder, application audit | Ability to erase, decrement or replace the independently protected high-water without detection; I3 motor/World oracle | Different host and administrative identity from A, CA/endpoint pin, credential rotation and revocation, crash/partition traces |
| C: protected monotonic custody | Non-rewindable per-authority/per-life publication sequence and signed append history, independently secured backup/retention | A or B's rollback, machine reset, routine DB restore, unilateral deletion/retention shortening | Separate administrative security principal and immutable high-water witness that survives tested rollback of A **and** B |

**Operator decision still required:** record actual host/provider/administrative identity, service principal and storage mechanism, independent key custody, retention/backup regime, and who can change IAM/policy. Candidate technical primitives include compliance-mode WORM/versioned object retention or a verified protected monotonic append service, **only after** access-policy and disaster-recovery tests prove its exact guarantees. Ordinary SQLite WAL, a second SQLite file, Git blob SHA, HMAC/shared key, an independent *process*, a TLS CA alone, or a signer attached to rollbackable data do **not** satisfy C. Do not name a cloud service as already selected or deployed.

## 3. Minimum wire/state contract for deployment review

- Bind each append and acknowledged read to `I3`, exact born identity, authorized *writer principal*, source/build digest independently reconciled to an approved release, monotonically increasing `(publication_index, sequence, head_sha256)`, `phase`, irreversible `terminal`, predecessor receipt digest and full receipt digest. Sender-supplied source SHA alone is an assertion.
- Writer admission: an independently provisioned **mutually authenticated** TLS client identity (or documented equivalent), pinned server CA/hostname/origin and authorized role/namespace. No test `--key-hex` CLI secret or shared signer exposed to the I3 writer. Revoke stale writers; do not assume certificate validity alone assigns life ownership.
- `PREPARED` (before `World.step`) may be acknowledged only after the off-host monotonic authority durably records the exact pending identity, digest and intended sequence. `COMMITTED` may follow only after one local `POST_PAID_LEARNING` event, and its high-water append must be durable **before** success ACK. No remote success on an unanchored database write.
- Ambiguity has one outcome: **STOP**. Lost ACK after a durable remote write, a partition during motor, stale writer, concurrent conflicting writer, corrupt/older checkpoint or an observed terminal state must **never** trigger automatic replay of the uncertain motor. A read-only inspection may classify state, not confer motor authority.
- Any authority/anchor mismatch blocks new action and cold recovery; no fallback to loopback, local publisher or a second rollbackable key. The protected log must be consulted on *all* genesis/resume/motor admission paths and must not allow a locally restored older high-water to become truth.

These are **requirements**, not a claim that today's `engineering_remote_authority.py` or `engineering_remote_online_challenge_witness.py` already implements a production deployment. Existing `serve_test_loopback` binds `127.0.0.1` and uses a test HMAC key and rollbackable SQLite; it must not be redeployed under a production-sounding name.

## 4. Prospective off-host acceptance matrix and original custody

All following cases need independently preserved source/configuration IDs, operator inventory, failure-injection command, exact log/receipt SHA, before/after sequence/head/phase/terminal, observed paid motor and modeled E/V receipt, source-specific tests and a dated verifier. Report all assigned cases including negative and irrecoverable STOP, not only successful recoveries.

| Precommitted fault | Required observation | Current evidence |
| --- | --- | --- |
| Same source, two genuinely new I3 engineering births with distinct identities | Independent registration; no inherited episodic memories or shared state | Source/lab tests only |
| Local birth store or local ledger restored alone | STOP before motor against remote/anchor | Loopback software controls, not off-host |
| **Both** local stores restored together, remote state newer | STOP before motor | Loopback software controls, not off-host |
| **Both locals + remote service working DB/online responder restored**, C remains newer | STOP due protected C, no valid newly issued lower receipt | **NOT_RUN off-host; primary release falsifier** |
| Attempt to roll back C with service/admin privileges held by A or B | DENIED or independently detected; exact operator privileges and evidence | **NOT_RUN** |
| Crash after local PREPARED, before remote PREPARED | STOP, zero new native motor | Loopback software controls only |
| Crash after remote PREPARED, before/during native motor | STOP on ambiguous action, never repeat | Loopback software controls only |
| Crash after local COMMITTED but before remote COMMITTED/ACK | STOP/reconcile read-only, never replay the motor | Loopback software controls only |
| Network partition, stale writer, concurrent conflict, revoked writer/key, foreign CA/source, terminal life | STOP without fallback or resurrection | Incomplete off-host evidence |
| Cold restore with immutable born I3 source, exact Mind/World/RNG/body and all energy/vigilance debits | Independent same-identity parity and sealed terminal; no oracle or I1 fallback | **NOT_ESTABLISHED** |
| Long-lived time/size benchmark, state growth, network and protected append overhead | Bounded operational cost with separate host CPU/network from body E/V | **NOT_RUN** |

## 5. Release decision and handoff

**Current decision: `STOP_NO_INDEPENDENT_M11`.** Independent R2 evidence is not available; no single process or shared CI runner may close #1339 or activate I3. The next *substantive* task is to provision and attest domains B/C under different administrators and execute the above fault matrix, **not** to add more local cryptographic decorations. Separate code review must then prove native cold reconstruction and exactly-once authority; a **distinct activation PR** and production readiness review remain necessary. Before actual deployment an operator must supply secure off-repository credentials and confirm the provider/storage/privilege design, rather than an agent guessing it.

Preserve `reference_generation=I3`, `active_generation=I1`; I3 `proposal/NOT_REGISTERED_NOT_EXECUTABLE`; P1.3 funded-v2 Stage 2.1 `NOT_ISSUED / HOLD_NO_VERDICT`. All new scientific World, cohort, reserve and source/index permissions are false. Successful technical release would **not** change the scientific verdict.
