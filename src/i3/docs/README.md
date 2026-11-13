# I3 documentation entrypoint

I3 is an independent research proposal. It is not a registered active engine;
I1 remains active.

For current work, do not browse this directory chronologically. Use the small
operational surface below.

## Current

- **13-Nov RP-A1/RP-A2 documentary decision:** [internal source/estimand matrix](STAGE2_C01_INTERNAL_DISPOSITION_2026-11-13.md) and [ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md) remove the **mandatory external C01 reviewer** and record general Stage-2 `HOLD_NO_VERDICT`, scientific `NOT_ISSUED`. E1/E3 negative candidate gates and P1.3 remain unchanged. No scientific birth/World authorization; proceed only with separately scoped I3 R1/R2 M11 engineering under ADR-0020. The [global coordinator](../../../docs/engineering/RESEARCH_COORDINATOR.md) routes there without claiming active I3 release.

- **RP-A2 / S2-C07 initial-specification concordance (13 November):** [traceability matrix, T/E/S/Tr verdicts, inherited `n_base`/`h_max`, candidate negatives, DÉC-2 decision boundary and C01 reopening gates](STAGE2_C07_INITIAL_SPEC_TRACEABILITY_2026-11-13.md). The accepted [ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md) is **unchanged on substance**: documentary `HOLD_NO_VERDICT` without scientific closeout, no optional roadmap DÉC-2 adoption, no World authority and #1062 open.

- **Current Stage-2 stop/methods decision:** [12-Nov critical-path audit](STAGE2_POST_COST_SPLIT_AUDIT_AND_CRITICAL_PATH_2026-11-12.md) and [internal C01 futility triage](STAGE2_C01_INTERNAL_FUTILITY_REVIEW_2026-11-12.md) are the primary scientific handoff; Stage 2.1 remains `NOT_ISSUED` with original E1/E3 negatives retained. [Future forecast custody](studies/stage2-replay-gate-selected-design/STAGE2_FUTURE_PREQUENTIAL_CUSTODY_RESULTS_2026-11-12.md) is **software-only**, not a newly proven benefit. **No further synthetic Stage-2 candidate without a genuinely new, prospectively justified source; no scientific birth permission.** The new 13-Nov C01 disposition supersedes the historical *mandatory reviewer* part for documentation only.

- **R2.9 native genesis-state integrity before first motor (13 November):** [precommitted falsifier](engineering/R29_NATIVE_GENESIS_INTEGRITY_PREFLIGHT_2026-11-13.md) and [source-exact results](engineering/R29_NATIVE_GENESIS_INTEGRITY_RESULTS_2026-11-13.md) from [PR #1384](https://github.com/josselin-orta-lab/individual-zero/pull/1384): **1,394/1,394 I3 tests PASS on Python 3.11 and 3.12**. Changed in-process native Mind/World state at unsealed sequence zero is denied before PREPARED or motor, including virgin detached reconstruction. This is a process-local guard, **not** independent M11; full-domain rollback remains `FAIL_INDEPENDENT_M11`. No new scientific authorization, I3 registration or Stage-2 verdict.

- **R2.8 nonce-bound online signed-witness challenge (13 November):** [preannounced fault contract](engineering/R28_ONLINE_WITNESS_CHALLENGE_PREFLIGHT_2026-11-13.md) and [exact-source results](engineering/R28_ONLINE_WITNESS_CHALLENGE_RESULTS_2026-11-13.md) from [PR #1382](https://github.com/josselin-orta-lab/individual-zero/pull/1382): **1,391/1,391 I3 tests PASS on Python 3.11 and Python 3.12**, including 13 new real-loopback TLS checks. A fresh nonce and separate online Ed25519 reply signature prevent replay of a *captured response*, while independently checking the original signed receipt. **A live signer can still sign an old receipt under the new nonce after full-domain rollback** (`FAIL_INDEPENDENT_M11`); no independent external high-water, motor or scientific release.

- **R2.7 real-loopback TLS signed-witness retrieval (13 November):** [preannounced HTTPS contract](engineering/R27_HTTPS_LATEST_WITNESS_PREFLIGHT_2026-11-13.md) and [exact-source results](engineering/R27_HTTPS_LATEST_WITNESS_RESULTS_2026-11-13.md) from [PR #1380](https://github.com/josselin-orta-lab/individual-zero/pull/1380): **1,378/1,378 I3 tests PASS under Python 3.11 and 3.12**, including ten real loopback HTTPS/Ed25519 fault controls. Strict operator-supplied CA/hostname and signature pins, 200/no-store/bounded payload, no redirect or retry, feeds R2.6 read-only reconciliation. **Rollback of both local SQLite stores and the loopback HTTPS reply is still accepted** (`FAIL_INDEPENDENT_M11`). No independently managed authority, native motor or scientific GO.

- **R2.6 required signed-witness reconciliation, test-only (13 November):** [frozen adversarial protocol](engineering/R26_REQUIRED_WITNESS_RECONCILIATION_PREFLIGHT_2026-11-13.md) and [exact-source results](engineering/R26_REQUIRED_WITNESS_RECONCILIATION_RESULTS_2026-11-13.md) from [PR #1378](https://github.com/josselin-orta-lab/individual-zero/pull/1378), **1,368/1,368 I3 software tests PASS on both Python 3.11 and 3.12**. An injected *required* latest signed witness must match the local publication tip and fully audited OPEN target before a **read-only diagnostic**; absent/older/foreign witnesses STOP with no local fallback. Full rollback of both SQLite stores **and the assumed witness callback** still ACCEPTS old state: `FAIL_INDEPENDENT_M11`. No real external witness, cold recovery, motor GO or scientific promotion.

- **R2.5 serialized signed publication, test-only (13 November):** [frozen fault matrix](engineering/R25_ATOMIC_RECEIPT_PUBLICATION_PREFLIGHT_2026-11-13.md) and [exact-source results](engineering/R25_ATOMIC_RECEIPT_PUBLICATION_RESULTS_2026-11-13.md) from [PR #1376](https://github.com/josselin-orta-lab/individual-zero/pull/1376): **1,357/1,357 software tests PASS on Python 3.11 and 3.12**. A test signer and separate local publisher SQLite serialize receipt publications; source SHA is checked against every local birth claim. A complete rollback of both stores and caller-held high-water still **ACCEPTS old state** (`FAIL_INDEPENDENT_M11`): not a protected remote authority or science/engine release.

- **R2.4 signed checkpoint receipts (13 November):** [preannounced Ed25519 receipt contract](engineering/R24_SIGNED_CHECKPOINT_RECEIPT_PREFLIGHT_2026-11-13.md) and [source-exact results](engineering/R24_SIGNED_CHECKPOINT_RECEIPT_RESULTS_2026-11-13.md) from [PR #1374](https://github.com/josselin-orta-lab/individual-zero/pull/1374): **1,346/1,346 I3 software tests PASS on both Python 3.11 and 3.12**. A pinned public key authenticates receipt bytes and a separately retained latest receipt prevents signed replay/fork. **Restoring all rollback domains including the retained high-water still defeats it: `FAIL_INDEPENDENT_M11`.** Test-only signer, no off-host operator, no engine or science GO. #1339 remains OPEN.

- **R2.4 checkpoint SQL read-only correction (13 November):** [preflight](engineering/R24_READONLY_CHECKPOINT_INSPECTION_PREFLIGHT_2026-11-13.md) and [exact-source results](engineering/R24_READONLY_CHECKPOINT_INSPECTION_RESULTS_2026-11-13.md) from [PR #1372](https://github.com/josselin-orta-lab/individual-zero/pull/1372), **1,336 I3 software tests PASS** on both Python 3.11 and 3.12. Existing v3 checkpoint capture now uses `mode=ro` and a verified read transaction, without the prior `BEGIN IMMEDIATE` constructor. Public pin rollback together with SQLite still passes as a deliberate **FAIL_INDEPENDENT_M11** negative control. #1339 remains open.

- **R2.4 exact-state checkpoint falsifier (13 November):** [preannounced safety protocol](engineering/R24_EXACT_STATE_CHECKPOINT_PREFLIGHT_2026-11-13.md) and [source-locked results](engineering/R24_EXACT_STATE_CHECKPOINT_RESULTS_2026-11-13.md) from [PR #1370](https://github.com/josselin-orta-lab/individual-zero/pull/1370): **1,332/1,332 I3 software tests PASS per Python 3.11/3.12**. Retained newer checkpoint detects older SQLite; restoring **both** SQLite and its public checkpoint is accepted and still **FAIL_INDEPENDENT_M11**. Not a hot-path speedup, off-host anchor or scientific claim. #1339 stays OPEN.

- **R2.4 authority-v3 cost observations (13 November):** [source-exact no-World CAS throughput and storage profile](engineering/R24_AUTHORITY_COST_PROBE_RESULTS_2026-11-13.md) from [PR #1367](https://github.com/josselin-orta-lab/individual-zero/pull/1367), with [frozen preflight](engineering/R24_AUTHORITY_COST_PROBE_PREFLIGHT_2026-11-13.md), **1,323 I3 software tests PASS per Python 3.11 and 3.12**. For 8/32/80 synthetic CAS steps, audit events are 17/65/161 and accepted nonce rows 25/97/241; storage observed 48/108/232 KiB. Median host-only step latency grows in these CI samples, but no World, energy tariff or production performance guarantee is established. Independent off-host M11 remains **NOT_ATTESTED**; issues #1339/#1331 OPEN.

- **Latest R2.4 signed-request anti-replay (13 November):** [source-frozen v3 nonce journal results](engineering/R24_DURABLE_REQUEST_NONCE_RESULTS_2026-11-13.md), with [preflight](engineering/R24_DURABLE_REQUEST_NONCE_PREFLIGHT_2026-11-13.md) committed before implementation. [PR #1365](https://github.com/josselin-orta-lab/individual-zero/pull/1365) passed **1,320/1,320 I3 software tests on both Python 3.11 and 3.12**. Signed HTTP request nonces now persist across ordinary loopback-server restart and prevent duplicate acceptance under the same retained SQLite; rejected CAS requests do not consume their nonce. **Full rollback of the authority DB, including nonces, remains accepted**, so independent M11 is **NOT_ATTESTED**, #1339 stays open and no World/engine activation follows.

- **13-Nov R2.4 exact response-custody and full rollback counterexample:** [signed CAS response/nonce fault matrix and four-state rollback results](engineering/R24_RESPONSE_CUSTODY_FAULT_RESULTS_2026-11-13.md), predeclared [here](engineering/R24_RESPONSE_CUSTODY_FAULT_PREFLIGHT_2026-11-13.md), passed **1,310 I3 software tests on Python 3.11 and 3.12** (PR #1363). **Negative trust result:** if both local stores, authority SQLite and the volatile pin are restored together, an old technical action is accepted again. This explicitly **fails independent M11 anti-rollback**; #1339 stays open, I3 unregistered and no scientific World authority.

- **Earlier R2.4 committed-anchor software result:** [13-Nov committed-anchor software results](engineering/R24_COMMITTED_ANCHOR_CONTRACT_RESULTS_2026-11-13.md) test remote + dual-local rollback against a volatile separately retained pin. Independently anchored off-host M11 **NOT_ATTESTED**, so I3 remains unregistered, I1 active. Release issue [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339) remains OPEN.


- **R2.4 authority-side audit consistency (12 November 2026):** [server-side CAS transition audit and full-store-rollback falsifier](ENGINEERING_REMOTE_AUTHORITY_AUDIT_2026-11-12.md) adds a canonical SHA-256-linked normal-writer log alongside the loopback server's head. New tests distinguish **partial corruption detection** from the **still-accepted rollback of the entire authority SQLite file**. Engineering-only local tests pass; exact-source Python 3.11/3.12 CI is required. **No M11 claim, production activation or scientific cohort permission**; release blocker [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339) remains open.

- **R2 remote monotonic engineering witness (12 November 2026):** [network CAS authority protocol and narrow trust boundary](ENGINEERING_REMOTE_MONOTONIC_AUTHORITY.md) add a separately running signed-message authority for PREPARED/COMMITTED high-water control around genuine P1.3 native engineering steps. Tests demonstrate rejection of simultaneous rollback of both local I3 SQLite files while a separate service retains the newer head. The supplied server is **loopback/test-only**, not an independently deployed, protected off-host M11 authority. No old cohorts or scientific Worlds reopened; [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) remains OPEN pending actual independent release authority and cost review.

- **R2 conditional local rollback witness (12 November 2026):** [separate-directory two-phase witness](ENGINEERING_LOCAL_ROLLBACK_WITNESS.md) binds local PREPARED and COMMITTED custody to native I3 motor execution and detects a previous intact ledger file substituted without rolling back its witness. Explicit negative test: if **both** local stores are rolled back, they still match. This is **not** off-host authentication, independent M11 anti-rollback, a production I3 engine or scientific World permission. See [R1/R2 issue #1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331).

- **R2 deterministic cold reconstruction (11 November 2026):** [source-bound replay of previously sealed native engineering steps](ENGINEERING_DETERMINISTIC_RECONSTRUCTION.md) verifies every original native decision, E/V-paid outcome and Mind/World/RNG digest on a new detached World. A separate Python process can continue only from a fully **COMMITTED**, nonterminal history; interrupted PREPARED or dead/censored sessions remain closed. This is **not** independent M11, off-host anti-rollback, an active I3 production engine or scientific cohort permission. [R1/R2 issue #1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) remains open.

- **R2/R3 native paid engineering integration (11 November 2026):** [one-shot native P1.3 `Mind`/`World` step with R2 journal custody](ENGINEERING_NATIVE_STEP.md). A fresh, isolated technical World runs one actual first-person decision, funded motor and prepaid learning before writing native state and bodily receipts to the local journal. This is **not** an active I3 engine, an M11 cold recovery, independent source attestation or authorization to create scientific Worlds. [R1/R2 issue #1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) remains the release dependency.

- **R2 native release engineering, step custody (11 November 2026):** [two-phase PREPARED -> POST_PAID_LEARNING ledger](ENGINEERING_STEP_LEDGER.md) builds on the [birth-slot reservation](ENGINEERING_BIRTH_RESERVATION.md) to detect incomplete, duplicate, stale and terminal steps without creating a World. This is an **engineering-only storage protocol**: the actual Mind/World state, cold continuation, externally anchored anti-rollback and scientific cost/benefit remain unproven. See [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331).

- **Native-I3 release R1 engineering slice (11 November 2026):** [engineering-only birth-slot reservation](ENGINEERING_BIRTH_RESERVATION.md), merged via [PR #1332](https://github.com/josselin-orta-lab/individual-zero/pull/1332). SQLite WAL/FULL one-shot *local* claim and tamper checks passed full I3 software CI on Python 3.11/3.12, but **NO actual birth, durable M11, recovery, scientific World authorization or active-engine cutover**. [Issue #1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) tracks genuine native owner identity and cold-recovery proof. The reference selection is [ADR-0020](../../../docs/decisions/ADR-0020-i3-owner-selected-development-reference.md).

- **Owner-selected reference for new development (11 November 2026):** [ADR-0020](../../../docs/decisions/ADR-0020-i3-owner-selected-development-reference.md) records the owner's decision that I3 is the project's reference engine for future architecture. This is a reference-selection decision, not active runtime activation: `reference_generation=I3`, `active_generation=I1`, I3 contract still proposal/no entrypoints. P1.3 funded-v2 remains the internal reference, Stage 2.1 scientific `NOT_ISSUED`, closed cohorts unchanged. Prioritize native generation-owned identity, persistent ownership and cold-recovery verification before source-specific runtime promotion.


- **B1 family-heterogeneity post-hoc arithmetic (11 November 2026):** [source-frozen count-only conditional risk-bound sensitivity](studies/stage2-replay-gate-selected-design/B1_POSTHOC_FAMILY_RISK_BOUND_SENSITIVITY_2026-11-11.md) rechecks the three known F0 family discordance tables (35/31/30 matched units). Under hypothetical iid assumptions the nominal one-sided 95% lower differences are **-11.714/-24.381/-7.815 percentage points**, all below an **unapproved 5pp** loss margin, whereas the pooled conditional lower is **-4.325pp**. No family-wise NI or general transfer GO follows; no new Worlds/lives or external review. This is retrospective numerical sensitivity, not preregistered science.

- **Stage-2 scientific completion audit, current-main update:** [post-E3 audit addendum and critical-path decision (11 November 2026)](STAGE2_POST_E3_AUDIT_ADDENDUM_2026-11-11.md), merged via [PR #1327](https://github.com/josselin-orta-lab/individual-zero/pull/1327). This reconciles the [earlier full completion audit](STAGE2_COMPLETION_AUDIT_AND_ROADMAP_2026-11-11.md) with E3's source-specific negative and the subsequent methods decision envelope. The minimum next step is a **bounded independent scientific methods/futility disposition**; no new World, Stage 2.2/2.3 controller or general survival claim is authorized.

- **Post-E3 inferential false-closure audit (11 November 2026):** [frozen methods preflight](studies/stage2-replay-gate-selected-design/POST_E3_INFERENCE_DECISION_ENVELOPE_PREFLIGHT_2026-11-11.md) and [exact-source negative decision envelope](studies/stage2-replay-gate-selected-design/POST_E3_INFERENCE_DECISION_ENVELOPE_RESULTS_2026-11-11.md), [PR #1325](https://github.com/josselin-orta-lab/individual-zero/pull/1325), [Actions #43094305191](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43094305191) PASS **1,161 I3 tests on each Python 3.11/3.12**. Four distinct DEVELOPMENT survival contrasts preserved, never pooled. B1 conditional iid-only lower **−4.325pp** could numerically pass an unapproved 5pp NI inequality, but actual independent ecology/margin/methods review are absent: **NO scientific NI GO**. E3 0/2 fixed synthetic motors and E1 0/12 distinct artificial states are **scoped negatives only**, not general useless-thought proofs. Stage 2.1 scientific verdict **NOT_ISSUED**, P1.3 retained, Worlds/lives **0**, no Stage 2.2/2.3 GO. Next cost-effective action: bounded **external independent methods/futility disposition**, not synthetic retuning.

- **Post-E3 Stage-2 scientific stop review (11 November 2026):** [source-locked closure-readiness assessment](studies/stage2-replay-gate-selected-design/STAGE2_POST_E3_SCIENTIFIC_STOP_ASSESSMENT_2026-11-11.md) concludes **E3 exact lab candidate CLOSED NEGATIVE** (1/2 informed source shapes changed an option score, **0/2** changed a native motor; exact [CI #43065730480](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43065730480) PASS 1,148 I3 tests per Python). Stage-2 full scientific completion remains **NOT_ISSUED**, not a general negative proof: no cost-complete endogenous choice to think, no real paid-information-to-living-action-to-body mechanism, no independent ecological NI. **Stop E3 synthetic retuning and replaying old cohorts**, keep P1.3 funded-v2/Stage 2.1/I3 unregistered; only a new source-independent action-relevant mechanism or an independently defensible bounded scientific negative closeout may reopen the critical path. New Worlds/lives 0, registry authorization unchanged.

- **Stage 2 E3, 11 November 2026: native option score changed, native motor did not.** [Precommitted no-World visible-vs-paid-discard protocol](studies/stage2-replay-gate-selected-design/E3_NATIVE_PAID_BRANCH_DELIVERY_PREFLIGHT_2026-11-11.md) and [exact-source result](studies/stage2-replay-gate-selected-design/E3_NATIVE_PAID_BRANCH_DELIVERY_RESULTS_2026-11-11.md). [PR #1321](https://github.com/josselin-orta-lab/individual-zero/pull/1321), [Actions #43065730480](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43065730480) PASS **1,148/1,148 tests on each Python 3.11/3.12**, same result SHA `f078899c348944b076bd0038987c434f411571cc0c44aeba5f32bc9f005b4b01`. The lab-only subclass uses existing paid action-keyed memories and real `Mind.decide`/Competition/Action Control, full parity of actual optional operators/model work in VISIBLE and PAID_DISCARD. **Spread** 1/2 informed shapes changed a native *option score*, but **0/2** changed a native *admitted motor*, plus 0/1 empty-source null. No actual World/lived payment or survival effect. **Stop this frozen E3 source/transform candidate NEGATIVE**; do not tune histories/seed/body after exposure. P1.3 reference, Stage 2.1 scientific `NOT_ISSUED`, I3 unregistered and no new World authority unchanged.

- **Stage 2 E2, 11 November 2026: existing action-keyed empirical support is distinct from P1.3 means.** [Prospectively frozen preflight](studies/stage2-replay-gate-selected-design/PAID_PERSONAL_BRANCH_SOURCE_COMPLEMENT_PREFLIGHT_2026-11-11.md) and [exact-source software results](studies/stage2-replay-gate-selected-design/PAID_PERSONAL_BRANCH_SOURCE_COMPLEMENT_RESULTS_2026-11-11.md), merged code [PR #1318](https://github.com/josselin-orta-lab/individual-zero/pull/1318), [Actions #43061617485](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43061617485) PASS **1,140/1,140 I3 tests on each Python 3.11 and 3.12**. Two predeclared SYNTHETIC/UNPAID action histories have **identical native EffectsModel means and forecasts**, yet the existing modeled-paid ReferenceBranchMemory retains **different empirical bodily outcome distributions** at identical storage/read work. E2 software source capacity only: **not** an independently born source, actual World debit, delivered native choice, general reflection benefit, or Stage 2.2 GO. No new memory/predictor needed for this source hypothesis. P1.3 funded-v2 stays the reference, I3 Stage 2.1 unregistered; next candidate requires separately frozen equal-real-work VISIBLE/PAID_DISCARD delivery to native decision before any born-source gate.

- **Stage 2.1 original-only causal readiness, 11 November 2026:** [precommitted protocol](studies/stage2-replay-gate-selected-design/OLD_ORIGINALS_CAUSAL_READINESS_PREFLIGHT_2026-11-11.md) and [exact-source 144-old-original audit result](studies/stage2-replay-gate-selected-design/OLD_ORIGINALS_CAUSAL_READINESS_RESULTS_2026-11-11.md). [Actions #43049277536](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43049277536) PASS **1,133 I3 tests each on Python 3.11 and 3.12**, plus **96+48** previously born source-original lives independently byte-checked (144 packed + 144 unpacked hashes) with **zero** new Worlds/lives. Actual paid native *additional-information* VISIBLE-vs-PAID-DISCARD delivery is **not present** in either source; prior **one** changed priority choice remains a **detached** alternative, not a second executed same-capture motor. Verdict `OLD_ORIGINALS_INSUFFICIENT_FOR_PAID_INFORMATION_CAUSAL_TEST`. Stop mining these archives as new causal readout evidence; historical prior conclusions remain intact. Stage 2.1 scientific verdict NOT_ISSUED, P1.3 funded-v2 retained, I3 unregistered, no Stage 2.2/2.3 GO.

- **Stage 2 E1 native-decision discrimination (11 November 2026):** [frozen protocol](studies/stage2-replay-gate-selected-design/NATIVE_OPTION_SET_DEPTH_DECISION_PREFLIGHT_2026-11-11.md) and [exact-source negative results](studies/stage2-replay-gate-selected-design/NATIVE_OPTION_SET_DEPTH_DECISION_RESULTS_2026-11-11.md). [Actions #43043257219](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43043257219) PASS **1,126 I3 tests each** under Python 3.11 and 3.12 on PR #1314 source: 48 native software Mind.decide calls, 24 fully comparable depth contrasts, 3 changed score vectors, **0 changed admissible options and 0 changed real native action choices**; no funding confounds. The fixed candidate returns NO_DECISION_DISCRIMINATION_ON_FROZEN_GRID and its stop rule applies. All fixtures synthetic/unpaid, Worlds/births **0**, science **NOT_ISSUED**; P1.3 funded-v2 stays the reference, I3 unregistered, no Stage 2.2/2.3 GO. Do not restart a synthetic-grid search for favorable actions.

- **Stage 2 E0/E1 campaign, 11 November 2026:** [evidence reconciliation and replay-readout source NO_GO](studies/stage2-replay-gate-selected-design/STAGE2_E0_E1_CAMPAIGN_LAUNCH_2026-11-11.md), and [independently cross-Python software characterization of paid Competition vs simulation horizon](studies/stage2-replay-gate-selected-design/PAID_COMPETITION_VS_HORIZON_SOFTWARE_RESULTS_2026-11-11.md), [Actions #43032049684](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43032049684) PASS **1,121/1,121 I3 tests each on Python 3.11 and 3.12**. On 3 synthetic bodies, depth changed predictions **3/3** but changed the raw top of two proposed plans **0/3**; nine fixed-score Competition cases were model-prepaid. This is a **SOFTWARE ONLY** capacity/negative-rank observation, not use of paid personal information in later real native action, generalized value-of-computation, survival NI, or Stage 2.2/2.3 GO. **Zero** new scientific Worlds/lives; P1.3 funded-v2 remains the reference, all old cohorts CLOSED_NO_RETRY, I3 unregistered. Next must be a separately frozen real-native-option decision-discrimination gate before a prospective scientific source can be considered.

- **Next first-person replay decision study completed:** [24 NEW matched units, 48 original G/R lives](studies/stage2-replay-gate-selected-design/NEXT_DECISION_24_RESULTS_2026-11-10.md), source-claimed Actions #42837992463. At the first differing paid replay content, **20/24** units observed a fork and next common first-person perception; only **1/24** showed different hypothetical physical next action, with 4/24 no admissible fork. Secondary survival TD priority **12/24**, random content **13/24**. Both sources of physical costs archived; next decision and TD residual are observer-only, not proof of predictive utility or survival mediation. Source and runner hard-closed NO_RETRY; **independent original 48/48 packed+unpacked SHA audit PASS** ([Actions #42839406230](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42839406230), [PR #1275](https://github.com/josselin-orta-lab/individual-zero/pull/1275)) without World recreation. No iid or Stage 2.2 promotion.


- **First real-state replay memory fork completed:** [48 new full-life originals, 24 assigned matched units](studies/stage2-replay-gate-selected-design/REALSTATE_FORK_24_RESULTS_2026-11-10.md). From identical actual pre-replay learned Mind states, equal-count priority vs random-content TD updates differed in **17/24 assigned units**; **7/24 no applicable fork**, retained as null. Secondary horizon survivors TD priority 8/24, random content 10/24. Original source consumed once and permanently closed; source-bound **independent 48/48 original packed+unpacked gzip audit PASS** ([Actions #42820936462](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42820936462)); both the source executor and main-push trigger are hard-closed NO_RETRY. No iid or biological survival mediation claim.


- **Water/replay causal hypothesis instrumentation and prospective 24-pair observation:** [48 complete new-source original lives, first replay selection difference at equal learned state in 18/24, then water-belief and decision divergence in 16/24](studies/stage2-replay-gate-selected-design/WATER_DIVERGENCE_24_RESULTS_2026-11-10.md). Secondary survival priority 8/24 vs random memory 10/24. All previous cohorts and the new 24-pair source closed; no causal mediation or independent iid claim. Independent original-only audit **48 packed and 48 unpacked SHA-256s, first divergence and all paid receipts PASS** in [PR #1266 / Actions #42810066826](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42810066826), with no new organism.


- **New 48-pair replay memory-*content* developmental finding:** [96 full lives, original custody and complete F0 observations](studies/stage2-replay-gate-selected-design/CONTENT_48_EXPLORATORY_RESULTS_2026-11-10.md). TD-prioritized GATE survived 17/48 vs genuinely randomized memory identities 23/48, with 1 vs 7 exclusive survivors; priority−random −12.5pp finite panel. Full original evidence archived and one-shot source closed; not an externally confirmed general survival effect. Independent read-only **96/96 packed/unpacked original SHA audit PASS** ([Actions #42794879073](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42794879073)), followed by new-World, nonintrusive water-memory divergence design [#1258](https://github.com/josselin-orta-lab/individual-zero/issues/1258).


- **New replay-content mechanism result:** [48 matched synthetic Mind snapshots](studies/stage2-replay-gate-selected-design/CONTENT_SELECTION_LOCAL_RESULTS_2026-11-10.md) comparing 3 real P1.3 TD replay updates from prioritized versus genuinely random *memory positions*. Selection differs 48/48, final values 47/48, at identical model costs and no World. No biological viability evidence. Next mechanism-identification design: [issue #1258](https://github.com/josselin-orta-lab/individual-zero/issues/1258).


- **Methodological correction and new original-only audit:** [RANDOM EQUAL MEAN randomizes the replay count, not TD-prioritized memory identity](studies/stage2-replay-gate-selected-design/RANDOM_CONTROL_SEMANTICS_AND_NEXT_FALSIFIER_2026-11-10.md). A new read-only SHA-256 audit independently rechecks every archived original and outcome on CI without reopening Worlds. Next study must separate replay content choice from replay quantity, under the individual's unchanged physical budget.


- **New completed three-arm 64-unit DEVELOPMENT original evidence (10 November):** [FIXED/GATE/paid-RANDOM 192-life source-bound results](studies/stage2-replay-gate-selected-design/THREE_ARM_EXPLORATORY_RESULTS_2026-11-10.md). Primary GATE−RANDOM horizon survival 0/64 (4 GATE-only vs 4 RANDOM-only); GATE lives longer on average but pays more cognitive energy/vigilance than RANDOM. All 192 originals and 64 triplets are permanently archived on [independent evidence ref](https://github.com/josselin-orta-lab/individual-zero/tree/evidence/i3-three-arm-development-64-20261110-originals/archive/i3/stage2-three-arm-development-2026-11-10). Cohort and original runner **CLOSED_NO_RETRY**; no confirmatory GO.


- **Three-arm funded G/R engineering now complete:** [FIXED/GATE/RANDOM exact-source 24 unused new-F0 units](studies/stage2-replay-gate-selected-design/THREE_ARM_ENGINEERING_WITNESS_2026-11-10.md), 72/72 lives sealed/reduced in each Python version, zero structural failures. No biological outcomes published or scientific claim.


- **Permanent B1 original evidence now on an independent [Git evidence branch](https://github.com/josselin-orta-lab/individual-zero/tree/evidence/i3-b1-96pair-development-20261110-originals/archive/i3/stage2-b1-development-2026-11-10)**, SHA-pinned and verified 192/192 in [Actions #42775154043](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42775154043). See [original-only post-hoc survival/cognition decomposition](studies/stage2-replay-gate-selected-design/B1_POSTHOC_SURVIVAL_COST_DECOMPOSITION_2026-11-10.md). No repeat births, confirmatory claim or engine activation.

- **New completed B1 DEVELOPMENT 96-pair cohort (10 November):** [192/192 original G/R results and limitations](studies/stage2-replay-gate-selected-design/B1_EXPLORATORY_DEVELOPMENT_RESULTS_2026-11-10.md) with 38 GATE versus 30 FIXED survivors, conditional *unattested* statistics and full adverse cost/ecology reporting. Original artifact expires February 2027; immediate priority is permanent archival. Exhausted runner is now closed.

- **Reference:** P1.3 on funded v2.
- **Stage 1:** closed negative under ADR-0018.
- **Current stage:** Stage 2.1 replay gate.
- **Canonical status:** `REPLAY_GATE_CAPACITY_SHOWN`.
- **ADR-0017:** owner-lifted for exact transport `dcada9e2…f1` and frozen DEVELOPMENT 80/81 only.
- **B1 verified new-world execution:** [96 paired public-synthetic future-type F0 worlds / 192 funded engineering lives, G/R 192/192 in Python 3.11 and 3.12](studies/stage2-replay-gate-selected-design/B1_NEW_WORLD_GR_WITNESS_2026-11-10.md); source guard corrected, all 14 invariant categories zero, no survival evidence.
- **B1 live-system research engineering:** [Fixed first-96 synthetic new-world paired FIXED/GATE G/R](studies/stage2-replay-gate-selected-design/B1_NEW_WORLDS_PAIRED_GR.md), 192 temporary technical lives, no biological evidence or science opening.
- **B1 synthetic WorldSpec preflight:** [1,500 F0-world structural-parity and name-independent collision checks](studies/stage2-replay-gate-selected-design/B1_PROSPECTIVE_WORLDSPEC_PREFLIGHT.md); no biological lives or source authorization.
- **B1 prospective pair sampling:** [1,500-pair metadata-only preflight](studies/stage2-replay-gate-selected-design/B1_PROSPECTIVE_SAMPLING_PREFLIGHT.md); cryptographic seed separation and collision checks are not proof of independent populations or scientific approval.
- **B1 execution witness:** [24/24 engineering G/R structural PASS, Python 3.11/3.12](studies/stage2-replay-gate-selected-design/B1_ENGINEERING_WITNESS_2026-11-09.md), after a retained 21/24 motor-funding FAIL; no scientific cohort opened.
- **Autonomous B1 research execution:** [Exact paired survival study and engineering-only launch](studies/stage2-replay-gate-selected-design/SURVIVAL_B1_LAUNCH.md) runs numerical statistical scenarios and 24 temporary engineering G/R lives; **scientific cohort remains locked**, not a prospective survival verdict.
- **Survival study launched (statistical phase only):** [Confirmatory survival power and sampling review](studies/stage2-replay-gate-selected-design/CONFIRMATORY_SURVIVAL_POWER_STUDY.md); independent-cluster target, loss margin and World opening remain unapproved.
- **Current analysis campaign:** [Phase-A historical reanalysis](studies/stage2-replay-gate-selected-design/ANALYSIS_CAMPAIGN_2026-11-09.md) reads all sealed 80/81 originals, exposes survival/cognition/heterogeneity and keeps the old owner lift consumed.
- **Current next action (13 November):** preserve the RP-A1/RP-A2 internal HOLD, pursue only I3 engineering for independent M11 custody/rollback resistance (issues #1331/#1339), and keep any future scientific cohort blocked pending a distinct source, source-frozen method, independent sampling and new owner World/index authorization. Historical mechanism-first v3 and DEVELOPMENT 80/81 are closed/non-admissible; no C01 reviewer is needed for this documentary decision.

Start here:

1. [STATUS.md](STATUS.md) — current research/governance state.
2. [ACTIVE_SURFACE.md](ACTIVE_SURFACE.md) — what is active versus historical.
3. [STAGE2_REPLAY_GATE.md](STAGE2_REPLAY_GATE.md) — frozen Stage-2.1 protocol.
4. [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) — stage ordering and dependencies.

[Code and dependency audit (9 November 2026)](I3_DEPENDENCY_AUDIT_2026-11-09.md)
records source integrity, archived dependencies and remaining custody boundaries.

[Proposed Stage-2.1 inference revision](studies/stage2-replay-gate-selected-design/PROTOCOL_REVISION_V2.md)
documents why the original eight-population sign-test design cannot certify
mean survival non-inferiority. The associated software arithmetic is conditional
and does not authorize any World. Independent review and a separate owner
decision remain required.

[Proposed finite-panel receipt check](studies/stage2-replay-gate-selected-design/FINITE_PANEL_RECEIPTS.md)
validates the candidate 1,200-cell F0 layout without constructing
Worlds or claiming mean survival non-inferiority. It does not
authenticate originals or grant selection/validation authority.

[Read-only sealed selection/validation preflight](studies/stage2-replay-gate-selected-design/SEALED_SELECTION_BRIDGE.md)
reconstructs prospective founder ranking from complete original
selection receipts, then checks validation originals against the selected
IDs. External digest pins are required; consistency cannot independently
certify source provenance or authorize a new study.

[Stage-2.1 mechanism-first design alternative](studies/stage2-replay-gate-selected-design/MECHANISM_FIRST_CANDIDATE_V3.md)
proposes a 720-life fixed-newborn-G0 matched policy comparison, avoiding
selection confounding while giving up evolutionary and ecological
generalization claims. It is NOT an authorization or a revised frozen protocol.

[Mechanism-first v3 sealed original reader](studies/stage2-replay-gate-selected-design/MECHANISM_FIRST_SEALED_READOUT.md)
is read-only, checks 720 candidate G0 lives against a separate v3
source-lock schema, and never executes a World or issues a scientific verdict.

## Stage 2.1 engineering custody

- [Hardened 36/36 sealed rehearsal](studies/stage2-replay-gate-development-80-81/HARDENED_REHEARSAL.md): structural PASS under ADR-0019, **not** an ADR-0017 lift.
- [Uploaded bundle integration audit](studies/stage2-replay-gate-development-80-81/INTEGRATION_AUDIT.md).

- [Completed 80/81 DEVELOPMENT result](studies/stage2-replay-gate-development-80-81/RESULTS.md):
  36/36 G/R PASS, replay-cost reduction observed, survival non-inferiority
  **not** established.
- [Frozen future RANDOM-EQUAL-MEAN parameter](studies/stage2-replay-gate-development-80-81/RANDOM_EQUAL_MEAN_PARAMETER.md):
  5,532/867, no additional World authorized.

## Stage 2.1 evidence

- [Canonical software result](studies/stage2-replay-gate-software/RESULTS.md):
  `REPLAY_GATE_CAPACITY_SHOWN`, R0-R4 PASS, no World/life.
- [Supplied software result](studies/stage2-replay-gate-software/SUPPLIED_RESULTS.md):
  preserved custody evidence, not canonical because the supplied denominator
  diverged from the frozen protocol.
- [Supplied 68/69 result](studies/stage2-replay-gate-development-68-69/RESULTS.md):
  descriptive development evidence only.
- [Package custody](studies/stage2-replay-gate-development-68-69/PACKAGE_CUSTODY.md).

## Historical material

Stage-1 evidence remains under `studies/` at stable citation paths. Retired
Stage-1 scientific runners/tests are under
`archive/i3/stage1-2026-11-09/`.

Stage-1 candidate implementations are under `src/i3/archive/stage1/`;
retained tests and historical opt-in runtime paths import this package. Its presence
does not reopen Stage 1. See [ACTIVE_SURFACE.md](ACTIVE_SURFACE.md).

Translation originals are preserved under
`archive/i3/original-language-records-2026-11-09/`. See
[translation custody](TRANSLATION_CUSTODY.md). The closed Stage-1 candidate
implementations live under [archive/stage1](../archive/stage1/README.md),
with the [historical document catalogue](../archive/stage1/DOCUMENTS.md).
The [archived Stage-2.1 68/69 runner](../archive/stage2/README.md) is not a
valid prospective transport.

The pre-rationalization navigation ledgers are preserved under
`archive/i3/navigation-pre-stage2-rationalization-2026-11-09/`.

## Principle

An I3 stage is a scientific question, not a feature that must succeed. Failed
mechanisms remain failed, evidence remains immutable, and the next stage should
not inherit historical machinery unless the dependency is explicit and
scientifically necessary.
