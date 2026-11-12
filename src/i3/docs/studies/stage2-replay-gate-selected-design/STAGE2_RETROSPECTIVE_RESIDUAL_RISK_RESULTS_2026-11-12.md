# Individual Zero Stage 2.1: retrospective past-only native forecast-error risk source screen (12 November 2026)

**Technical result: `RETROSPECTIVE_RISK_EVALUATION_PASS`. Exploratory source-merit screen: `TRUE` in the exact retrospective four-life fixture. Scientific verdict: `NOT_ISSUED`.** This report is NOT a pre-exposure prediction test, an independent replication, a paid mental operation or a demonstration that additional reflection changes a native motor or improves survival.

## Source, preflight, sequence and testing

- Main baseline `f86e29aee71facc27def33bb4e6a0f90c09348d2`, source-first [analysis preflight](STAGE2_RETROSPECTIVE_RESIDUAL_RISK_PREFLIGHT_2026-11-12.md) commit `1eccd362ee9657d940625d02f5d11cb8e4a0defe` **before implementation**. It explicitly states analysis is *retrospective*, because the original 320 events and outcomes were already available and inspected.
- Original first-person-effect prequential source is [PR #1347](https://github.com/josselin-orta-lab/individual-zero/pull/1347), exact head `7f32f33172c4773bf4c5630ff945f0b1df6dbb8e`, [Actions #43209682555](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43209682555), original receipt SHA `86f7db8524783a249ec2e1363c3f149f94af1eed1dc09ba32724a9c9bade8373`. Read-only all-320-event derivative source is [the existing posthoc zero-control extract](STAGE2_POSTHOC_ZERO_BASELINE_SOURCE_EXTRACT_2026-11-12.json), derivative SHA `09c09804f5100edd5664d649cd5f3c0234dd4c182e1c89d8e2761b34a0b9a5b4`.
- [PR #1349](https://github.com/josselin-orta-lab/individual-zero/pull/1349), exact tested head `593fb7e88b1fd60100ffad46e7ba851bb74f7e80`, merged as `498d3bb1450697811b68b3896e926c1eca69f4fa`. It adds [read-only analysis](../../../lab/stage2_retrospective_residual_risk.py) and [four fail-closed tests](../../../../../tests/i3/test_stage2_retrospective_residual_risk.py); no modification to Mind, genome, Action Control, BodyLaws, World, runtime policy, registry or scientific source permissions.
- [Exact-source GitHub Actions #43240764597](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43240764597) **SUCCESS**: Python 3.11 1,247/1,247 tests in 91.558 seconds, Python 3.12 1,247/1,247 in 107.065 seconds. Both emitted the same deterministic receipt SHA `23fef911abcb9eff07c7262f723b113eb719d3633edc567b4f54f0dcee55fb19`, status `RETROSPECTIVE_RISK_EVALUATION_PASS`. No new World was created by this retrospective reducer; no new scientific lives, held-out World access or cohort.
- An exact code/source receipt SHA demonstrates software consistency of this analysis, not an independently authenticated empirical population or fresh out-of-distribution predictive performance.

## Method and outcomes

For each native factual step, let `z_t` be the **five-channel mean squared error of the original forecast** frozen before its real World consequence. Estimate the risk of z_t from **only earlier errors in the same technical trajectory**. Pooled witness `G_t = mean(z_<t)` (zero before any history). Per-action-label witness `A_t=(sum_{past same action} z + G_t)/(1+n_past_same_action)`, using a single pooled-mean pseudorecord fixed in the preflight. Both predicted risks are frozen before reading the corresponding actual z_t; the action was already selected by native Mind, and no estimate is delivered to the controller. This is a diagnostic **about forecast-error risk**, not action quality, motor selection, or the value of buying additional computation.

| DEV World / seed | N | Squared-risk gain, pooled minus action | Absolute-risk gain, pooled minus action |
| --- | ---: | ---: | ---: |
| dev-open-field / 840061 | 80 | +43.8167 | +1.7504 |
| dev-open-field / 840062 | 80 | **-73.1446** | +2.5762 |
| dev-failing-well / 840061 | 80 | +68.3086 | +5.6951 |
| dev-failing-well / 840062 | 80 | +69.9820 | +5.7768 |
| **All 320 temporally dependent events** | **320** | **+27.2407** | **+3.9496** |

Pooled squared-risk loss **568.6743**, action-conditioned squared-risk loss **541.4336**. Pooled absolute-risk loss **11.7246**, action-conditioned absolute-risk loss **7.7749**. All 320 events included; 296 had earlier error records for the same motor action and 24 did not. Because it estimates the next event's **loss magnitude**, a good result does not imply a more accurate next *body delta* prediction.

The exact preflight source-merit screen required improvements on **both** losses in at least **3 of the 4 complete technical trajectories**. Observed: squared-risk favorable in 3/4, absolute-risk favorable in 4/4; **screen passed**. One trajectory is adverse on the squared metric and remains in the aggregate. Four technical trajectories from only two developer Worlds are **not independent ecological population units**, and 320 successive steps are highly correlated. No p-value, confidence interval or independence claim is justified.

## Scientific limitations, competing hypotheses and next bounded action

The source is **different from E3's outcome-distribution readout**: it concerns prior self-observed prediction errors conditional on native action labels. Yet this analysis does **not** prove that the individual should fund this mechanism: its output is generated by unpaid observer CPU; it is not costed with native `CognitiveBudget`, and it does not change any legal motor. As seen in the earlier zero-change study, severe native predictive misses are possible despite frequent small improvements; selecting an option based on a risk score derived from four known histories would dangerously reuse the endpoint.

Alternative explanations to test independently: different action mixes and step timing, world/stationarity effects, heavy-tail leverage, and using only action labels instead of native action/token keys. The preflight one-pseudorecord estimator is a screening convention, not an established cognitive architecture or calibrated tail-probability distribution.

**Decision:** preserve the action-conditioned residual-history source as **one specifically justified hypothesis for an independent future study**, not as a new behavior rule. The shortest next **software-only** gate, if implemented, is to derive a native-budget-compatible readout of prior personally experienced residuals and show that it can be computed and genuinely paid, then that its *visibility* changes a **later admissible native decision** against same-operator `PAID_DISCARD` under frozen and genuinely distinct conditions. E3's frozen null must not be retuned or reused. Without native action mediation and a prospective independently sourced comparison, stop and keep `Stage 2.1 / NOT_ISSUED`.

No stage 2.2/2.3 GO, no scientific World authority, no I3 activation. Continue separately the cost calibration #1283, first-person mechanism and proper-score source #1276, and scientific value-of-computation objective #1062.
