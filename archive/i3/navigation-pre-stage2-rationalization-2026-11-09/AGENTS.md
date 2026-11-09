# I3 development-agent instructions

These instructions govern repository work, never the individual's mind.
Read the root instructions, then [current status](docs/STATUS.md) and the
[single development plan](docs/DEVELOPMENT_PLAN.md). Inspect live HEAD, relevant
open issues/PRs and checks on the exact SHA before editing. The current
reference is **P1.3 on funded v2**; older descriptions of P1.1 as current or
P3 as not executed are historical, not the present source/evidence state.

## Approved direction and next work

[ADR-0016](../../docs/decisions/ADR-0016-i3-generalization-without-imposed-rules.md)
remains the governing direction. P1.3 on funded v2 remains the reference and I3
remains unregistered.


[ADR-0017](../../docs/decisions/ADR-0017-i3-moratoire-deux-phases-repetition-scellee.md)
now governs execution custody. **Do not open any new I3 World index in any
cohort.** This moratorium supersedes every older handoff below that would
otherwise authorize proposing, freezing or executing a fresh lived panel.

Allowed work during the moratorium:

- execute/finalize software-only gates such as lifecycle-custody stress v3;
- inspect already-archived originals only within their existing read-only
  forensic boundaries;
- implement the two-phase G/R living-panel pipeline;
- add a disjoint non-evidentiary `engineering` cohort;
- implement and run full-scale sealed rehearsals on that engineering cohort.

For any future living panel after the moratorium, generation must finish and
seal all originals before reduction starts. A generation exception still stops
and closes the panel. A reduction exception after sealed generation becomes
`REDUCTION_DEFECT_PENDING_REPAIR`: no partial result may be read or published,
no new life may be generated, and at most two blind reducer-repair cycles may
rerun reduction against byte-identical originals.

Do not lift the moratorium merely because software tests or W0-W9 pass. Lifting
requires the two-phase pipeline, declared engineering cohort, a full-scale
sealed rehearsal PASS on the exact next transport SHA, and an explicit owner
entry in `docs/STATUS.md`.


**Stage 1 is closed negative (9 November 2026).** The single Candidate-J software
falsifier returned `CANDIDATE_J_DEFECT`: J0 failed for both declared
projectors against the frozen oracle criterion. [Results](docs/studies/stage1-candidate-j-software-falsifier/RESULTS.md)
are final under [ADR-0018](../../docs/decisions/ADR-0018-i3-cloture-etape-1.md).

P1.3 remains the reference. **Do not** change J0 tolerance/projector, rerun the
falsifier, create Candidate-K, or implement a lived Candidate-J path. Stage 2 is
the current scientific stage on P1.3. ADR-0017 still governs every lived panel.

Lifecycle-custody stress v3 W0-W9 may remain as an ADR-0017 engineering
regression, not as Stage-1 scientific continuation. All lower Candidate F-I
handoffs are historical custody records and do not override this closure.

**Stage 2 is the current scientific stage.** Read
[STAGE2_LAUNCH.md](docs/STAGE2_LAUNCH.md), the frozen
[Stage-2.1 replay gate](docs/STAGE2_REPLAY_GATE.md), and the
[package audit](docs/studies/stage2-replay-gate-software/RESULTS.md).

The uploaded package contained a useful implementation, engineering pipeline and
descriptive 68/69 pilot, but its software execution is **not** the canonical
Stage-2.1 verdict. It used `audited_decisions` in the denominator of `r_hat`
instead of the frozen all-decisions denominator. The integrated code corrects
that divergence.

Next scientific action: execute the corrected R0-R4 software falsifier exactly
once. Do not tune the formula, fixtures, controls, thresholds or verdict table
from the supplied results. Do not use 68/69 to set a validation margin or
reinterpret it as prospective evidence.

ADR-0017 remains active. The package's quoted owner-lift is not authenticated
by the repository ledger. The two-phase G/R and engineering-cohort code may be
developed and rehearsed, but no fresh lived Stage-2 World may open until an
explicit owner lift is recorded in STATUS.md.

**Current handoff after 58/59 exposure:** run `42484179997` opened the frozen
Candidate-H DEVELOPMENT panel and then stopped on a post-life reduction
engineering error. The evidence branch is
`evidence/i3-stage1-candidate-h-58-59-c2f63445ce8a`. Per the frozen no-retry
rule, 58/59 are exposed and closed. There is no H1-H6 Candidate-H verdict.
Do not rerun, replace seeds, repair the reducer and replay the panel, or use the
partial Candidate-H original to tune cognition.

The 56/57 read-only first-contact audit is now part of the handoff. It observes
that a never-performed action receives the paid unsupported-effect prior on the
imagined frontier path but not when the resource is directly perceived.
Exploration without P1.3's designer addend is also sparse. These are descriptive
findings on immutable originals, not permission to tune 56/57.

The frozen shared-first-contact-prior gate is now implemented and passes
([result](docs/studies/stage1-shared-first-contact-prior/RESULTS.md)):
D0-D7 PASS and R1 holds. P80 relevance rises 48/80 -> 56/80 -> 72/80 as
positive omega increases. However, every newly relevant P80 state is an
energy/vigilance state, not a water-deficit state; F108 saturates, and K80 is
non-monotone. Treat this as **generic inherited first-contact capacity**, not a
water-specific adaptation.

The two previously frozen prerequisites now PASS:

- Candidate-I shared-prior integration: I0-I9 PASS, zero fallback identity,
  addend, accounting or renaming failures;
- composite-funding reducer repair: R0-R6 PASS, with 58/59 still permanently
  exposed/closed and no retroactive verdict.

The first frozen runtime generalization
[STAGE1_CANDIDATE_I_RUNTIME_INTEGRATION.md](docs/STAGE1_CANDIDATE_I_RUNTIME_INTEGRATION.md)
is now **closed as DEFECT**. Its top-set-change relevance rule disagreed with
#1170 on 700/1,128 one-trial states. Do not repair or merge that branch and do
not reinterpret the failure as an organism result.

Candidate-I runnable multi-option v2 now passes S0-S11
([result](docs/studies/stage1-candidate-i-runtime-integration-v2/RESULTS.md)).
The final software authority is source
`9c5ef3e2657c1d2be1e0e8f0b592b6a957dcff6b`, Actions `42500166929`.

The #1170 one-trial reduction is exact (0/1,128 mismatches); runtime inventory
permutation/external-token renaming, common Candidate-F geometry, legacy P1.3
finalizer identity, complete Stage-A fallback custody, post-contact parity,
same-genome omega=0 ablation, composite reducer custody and forced-failure state
restoration all pass.

The
[fresh Candidate-I 60/61 protocol](docs/studies/stage1-candidate-i-development-60-61/PROTOCOL.md)
is now prospectively frozen. Its machine-readable plan digest is
`a8e8dc955a3324e3f78986b4e4de8d8894f8196e1ba7321b89f295016dc1c876`.

The frozen 60/61 pilot has now been opened once and stopped after five completed
lives on a Candidate-H branch-memory settlement error. It is classified
`ENGINEERING_FAILURE_NOT_A_DEATH`; 60/61 are permanently exposed and closed.
Do not rerun, resume, replace seeds/horizon, infer J1-J7, or use the partial
panel to tune cognition.

The frozen branch-decision settlement gate now passes B0-B9
([result](docs/studies/stage1-branch-decision-settlement-repair/RESULTS.md));
merged repair `5ee25b3b0f39050321b0b5c6147bdae0e3e68ec5`). The repair preserves
full paid Candidate-H/I Stage-A + Stage-B work and only aligns that work with
its actual decision-start body.

60/61 remain permanently exposed and closed with no J1-J7 verdict.

The fresh 62/63 panel was opened once by #1187 after the runner #1186
passed its software checks. It stopped after 18 completed lives on
`RuntimeError: missing branch decision settlement start body` in native
Candidate-I. The originals are archived on
`evidence/i3-stage1-candidate-i-62-63-81f05a7fb79c`; #1187 is closed and
unmerged. **62/63 are permanently exposed and closed. There is no J1-J7
verdict.** Do not rerun, resume, replace conditions or use partial lived metrics
to tune Candidate-I.

Source inspection identifies the current defect as stale learning authority
restored by Candidate-I's detached probe rollback: the pre-probe snapshot can
capture the previous `last`, while the matching branch settlement receipt is
cleared. On an unfunded Stage-A exit, restoring that snapshot can revive
`last` without its receipt.

The frozen
[Candidate-I probe-restore authority repair](docs/studies/stage1-candidate-i-probe-authority-repair/RESULTS.md)
now **PASSes U0-U9** on repair-code authority
`5ca8f2dcb7f87c18880ea3c45b773eec0daab2d4`, Actions
`42517714784`. Rollback may restore perception/map/token/RNG state but never
`last`, pending branch storage, branch-settlement authority or pending
opportunity commits. A funded FALLBACK must then recreate opportunity-
presence authority from its one real final perception before learning.

The frozen
[Candidate-I lifecycle-custody stress](docs/studies/stage1-candidate-i-lifecycle-custody-stress/RESULTS.md)
now **PASSes L0-L11** on tested source
`1bdca27ae95509e9b54817bd25b2c0a21872c069`, Actions
`42518978398`, merged authority
`5e85106157afa6c600dd1983efde94fb80032977`. Nine already-exposed
DEVELOPMENT-0 smokes plus the F/R/N/P/Z lifecycle micro-cycles complete with
zero custody failure.

The fresh
[Candidate-I 64/65](docs/studies/stage1-candidate-i-development-64-65/RESULTS.md)
panel has now been opened once and stopped after 35 admitted reductions. The
36th original completed, then the Stage-0 revision reducer rejected a valid
multi-phase receipt with
`ValueError: processing status contradicts paid base block`.
Evidence is archived on
`evidence/i3-stage1-candidate-i-64-65-427eedd37457` at
`f09806130d0ea0d9d9a66a12d6baa3afe5b66d15`. #1195 is closed/unmerged.

**64/65 are permanently exposed and closed. There is no J1-J7 verdict.**
Do not rerun, resume, replace the failing life, complete the remaining cases or
use partial metrics to tune Candidate-I.

The current defect is reducer ownership: a paid Candidate-H/I Stage A may be
followed by a zero-work P1.3 Stage B whose public status is
`NO_PROCESSING_BUDGET`. Total work remains physically paid, but R-depletion
processing semantics belong to Stage B.

The frozen
[multi-phase processing reducer repair](docs/studies/stage1-multiphase-processing-reducer-repair/RESULTS.md)
now **PASSes M0-M9** on tested source
`252419ff099fbb95990fb7a19426864c0a5a8346`, Actions
`42523805013`. Total decision work remains the full physical bill; only the
authenticated route-specific processing owner is tested against public funding.

64/65 remain permanently closed. The read-only archived-life confirmation is
forensic only and creates no J1-J7 evidence.

The successor
[Candidate-I lifecycle-custody stress v2](docs/studies/stage1-candidate-i-lifecycle-custody-stress-v2/RESULTS.md)
now **PASSes V0-V8** on tested source
`f9544cf2e22f69a953fdd4141adc6991547c7e16`, Actions
`42524858889`, merged authority
`fbaecde68d6fbcb5a9ec8c6d5908b4b1880137bd`. Historical L0-L11 remain
unchanged. The paid-Stage-A / zero-Stage-B boundary is exercised through actual
H/I production decisions and the repaired Stage-0 reducer.

The fresh
[Candidate-I 66/67](docs/studies/stage1-candidate-i-development-66-67/RESULTS.md)
panel has now been opened once by #1205. Ten lives were admitted; the eleventh
Candidate-I native original completed runtime but Stage-0 revision reduction
stopped on `invalid Candidate-I post-contact processing receipt`. Evidence:
`evidence/i3-stage1-candidate-i-66-67-9db49f8c3b52`,
commit `18a7e27bd79de81280e171fdf682f8a5f4195830`.

**66/67 are permanently exposed/closed with no J1-J7 verdict.** Do not rerun,
resume, complete or retroactively admit archived lives after repair. Do not use
partial lived metrics to tune Candidate-I.

The
[post-contact probe reducer repair](docs/studies/stage1-post-contact-probe-reducer-repair/RESULTS.md)
now **PASSes Q0-Q9** on tested source
`78d09c98127fb55aebb5eca729fa4ce4795d007a`, Actions
`42533323063`, merged authority
`4bcb2f28488f289625558960cd93c7c65c69b107`. Direct H and I post-contact
share one processing-owner definition; complete H uses Stage B and H
`PROBE_UNFUNDED` uses authenticated Stage A with zero Stage B.

**Do not propose another fresh panel yet.** The next gate is prospectively
frozen in
[STAGE1_CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V3.md](docs/STAGE1_CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V3.md).
Implement W0-W9 exactly. Use the fixed ten-value energy ladder and actual
production H/I classes; do not alter the ladder to obtain both incomplete
funding classes. The gate is software-only and may not read 66/67 originals as
acceptance fixtures.

Do not widen omega, rescale RMS, add resource-specific inherited coefficients,
alter K80/P80/F108 or reuse 56/57/58/59. Selection, validation, reserve and
Stage 2 remain blocked.

The full frozen Stage-1 genomic-omega Candidate-F gate has now completed.
Read [the final result](docs/studies/stage1-omega-adr0015/RESULTS.md) before any
Stage-1 edit.

Observed validation:

- P1.3 reference: **82/240 survivors**;
- Candidate-F + inherited omega: **0/240**;
- same selected candidate genomes with `omega=0`: **0/240**;
- candidate revision: **0 reacquisitions**, pooled complete rank 401.0;
- reference revision: **35 reacquisitions**, pooled complete rank 282.5875;
- omega selection shift positive in **6/8**, below frozen 7/8;
- G1-G5 FAIL; G6 custody PASS.

This is a clean scientific rejection of the current Candidate-F/omega
architecture on F0. Preserve all earlier software falsifiers as bounded evidence,
but do not use them to override the live gate.

**Current post-gate interpretation:** the 54/55 cost-versus-policy diagnostic
is complete. Candidate-F and the deliberately overcharged P1.3-choice control
both have 0/12 survivors; ordinary P1.3 has 4/12. The preregistered strict
survival counterexample to universal cost sufficiency was not observed.

Do not misread that null. The upper-cost control pays Candidate-F shadow
cognition **plus** P1.3 cognition, so it is not cost matched and cannot prove
that cost alone causes Candidate-F mortality.

Secondary paired evidence implicates policy as well:

- upper-cost lives longer than Candidate-F in 7/12 blocks, shorter in 1, ties 4;
- aggregate water uptake is 25 upper-cost versus 4 Candidate-F;
- in all four reference-survivor blocks, Candidate-F obtains zero water while
  upper-cost obtains water and outlives Candidate-F;
- shadow and actual P1.3 motor choices differ on 510/2395 upper-cost decisions.

Cost remains severe: upper-cost has 868 P1.3 NO_PROCESSING_BUDGET steps and
36.24% physical inactivity.

**DRIFT DETECTED:** Candidate-F/omega is scientifically rejected. Do not tune
omega, reopen 54/55, change the frozen gate, or build a free-cognition,
reimbursed-body or forced-action control merely to isolate mediation. A further
causal control is justified only if it preserves paid cognition and physical
state without hidden rescue. Otherwise close this decomposition as **cost and
policy both implicated; exact mediation unresolved**, and return Stage 1 to a
new architecture hypothesis.

Do not reopen selection/validation 72..167 or the P4 reserve. Do not launch
Stage 2 to rescue the rejected candidate.

**Update after #1155:** the canonical high-precision audit resolves the
Candidate-F residual
([results](docs/studies/stage1-candidate-g-canonical-numeric-audit/RESULTS.md)).
At the same 1288-step cost as historical per-step, canonical numerics select
24 states / 0 water, **exactly the Candidate-F selected set**. The historical
eight water selections are repeated-float boundary artifacts. Do not design
projection refinements to recover them. Candidate-F's event-local projector is
the current canonical Stage-1 projection target on #1146 at mean 470.05
simulated steps/state.

#1156 completed the bounded no-omega Candidate-G software gate. The subsequent
frozen 56/57 DEVELOPMENT pilot is now complete
([result](docs/studies/stage1-candidate-g-development-56-57/RESULTS.md)).

Frozen continuation verdict:
**`CANDIDATE_G_56_57_ENGINEERING_CONTINUATION_FAIL`**.

Observed:

- 368 information-active decisions and 1213 reference-only decisions;
- energy/lived-step 0.9161 Candidate-G vs 2.1983 rejected Candidate-F;
- vigilance/lived-step 1.2723 vs 3.1118;
- frozen R5 FAIL: `NO_PROCESSING_BUDGET` 2.8463% vs 2.0436%;
- descriptive survival: Candidate-G 0/12 censored, P1.3 3/12;
- positive water uptake: 16 Candidate-G vs 196 P1.3.

The posthoc fact that total non-funded decisions are lower for Candidate-G
(9.1082% vs 21.4578%) does not replace R5. It only identifies different
failure-mode composition: Candidate-F often fails at `NO_FUNDED_SCORE`, while
Candidate-G reaches processing failure more often.

**DRIFT DETECTED:** 56/57 are exposed. Do not tune recurrence support,
activation frequency, projector choice, funding thresholds, seeds, horizon or
the R5 definition on them. Do not open another live panel to rescue this
candidate. Close the Candidate-G live path and return to read-only evidence
analysis or a new software-only architecture falsifier. Preserve no-omega,
personal-observation-only cognition, paid work and P1.3 reference. Selection,
validation, reserve, adoption and Stage 2 remain blocked.

The support-vs-relevance defect is now followed by a bounded
[first-contact Candidate-H software PASS](docs/studies/stage1-candidate-h-relevance-fallback/RESULTS.md):
all 56 fallback states are fundable, same-body P1.3 score identity is exact,
and all 20/20 #1161 projector-drift states return to their pre-probe P1.3 top
set. The extra fallback work is physically charged.

The first H4 result was a verifier defect, not candidate tuning: the verifier
used the completed outer-loop `level=50` instead of each row's stored level.
The corrected immutable-row check passes on Python 3.11/3.12 without changing
Candidate-H or H0-H5.

The post-contact relevance gate now also passes
([result](docs/studies/stage1-candidate-h-post-contact-relevance/RESULTS.md)):
68/80 states are decision-relevant; the remaining 12 have positive information
but no top-set effect, and all 12/12 fund an exact P1.3 fallback with zero
pre-probe top changes.

The unified Candidate-H software integration is now complete and passes
([result](docs/studies/stage1-candidate-h-unified-integration/RESULTS.md)):
U0-U9 are all PASS under Python 3.11/3.12. The fixed routing panel contains
37 P1.3 final routes and 23 Candidate-F final routes, observes all five required
routing classes, has zero omega mismatches and zero fallback identity failures.

**Historical handoff after #1164:** the unified software PASS authorized a
prospectively frozen DEVELOPMENT-only protocol. #1165 froze it and #1168 later
opened it once. That live handoff is now superseded by the exposed engineering
failure above. Do not create a replacement DEVELOPMENT panel.

**History after #1154:** exact cache/reward reuse cannot reach Candidate-F cost
parity even under an impossible free-memo lower bound
([results](docs/studies/stage1-distress-reuse-diagnostic/RESULTS.md)). That route
is closed.

**History after #1153:** exact death truncation is valid and useful
([results](docs/studies/stage1-death-truncated-per-step/RESULTS.md)): 853.3
simulated steps/state at exact 32/8/24/40 decisions, but no Candidate-F cost
parity.

**History after #1152:** the full stored-trace cache is fundable but physically
wasteful ([results](docs/studies/stage1-separable-cache-accounting/RESULTS.md)):
only 7.6% trace hits and even its lower arm costs 7.759 energy / 3.532 vigilance.
Do not revive that representation or choose its lower tariff post hoc.

**History after #1151:** exact separability/reuse is real at numerical-noise
accuracy ([structural result](docs/studies/stage1-separable-projection-cache/RESULTS.md)).
The failure is physical representation cost, not projection accuracy.

**History after #1149/#1150:** local-sensitivity reuse (drink error 1.91) and
decision-time anchored chunks (bias 0.215) fail feasibility; do not retry them
([probes](docs/studies/stage1-affordable-projection-probes/RESULTS.md)).

**Update after #1146:** a declared diagnostic shows Candidate-G's 1/80
epistemic pass is a projection effect. The Candidate-F projection gives 24/80
at ×8.9 paid simulation, per-step 32/80 at ×24. The next architecture question
is an affordable consistent projection
([results](docs/studies/stage1-candidate-g-projection-dependence/RESULTS.md)).
Do not build a live Candidate-G on the reference projection expecting a
behavioral effect.

Stage 0 #1060, individuality #1026 and historical P5d uncertainty #1054 remain
open in parallel. Stage 2 stays blocked.

## Boundaries

- I1 active; I3 unregistered. Do not modify the registry or another generation's
  runtime. ADR-0001 and ADR-0014 remain binding.
- Personal observations only; no true hidden stocks, unseen sources, scheduled
  changes or oracle outcome distributions in Mind. Generic inherited traits
  only, invariant to renaming. No learned weights/maps/memories across births.
- Genuine prepaid computation, including information branches and metareasoning;
  no fabricated charges or work after death. Preserve motor authority and
  irreversible mortality. No body/memory reset to manufacture a common challenge.
- New validation must be prospectively source-locked and previously unopened,
  indices >=120 with collision checks. P4 reserve 1200000..1200199 stays sealed.
  Repeated worlds and extra genomes from the old four populations are not new
  independent replication. No held-out tuning of tariffs, genes or thresholds.
- The report's 7/8 Stage-6 directional criterion is not a significance claim.
  Read the plan's explicit statistical, family-R and zero-cost clarifications.
  Probes remain descriptive until actual cost equivalence is demonstrated.

## Minimal intervention and verification

Before editing record issue, baseline SHA, files, one question, falsifier,
control/ablation, observable and expected software versus scientific scope.
For a docs-only change, do not invent a need for new scientific lives. Run
`python tools/check_repo_navigation.py --scope entrypoints` in a full checkout.
For code changes use [TEST_PLAN.md](docs/TEST_PLAN.md), the smallest relevant
I3 tests and generation guards, then mandatory CI for the exact candidate.

The baseline ledgers and supplied report are preserved original bytes.
Original study receipts, preregistrations and verdicts are immutable. Do not
rewrite historical evidence to support the new plan or cite another SHA's
checks as current. Report PASS / FAIL / NOT_RUN and NOT_OBSERVED honestly.

Flag **DRIFT DETECTED** when repeated local proofs, observers, framework work
or policy patches add complexity without resolving a specified scientific
question. Prefer the smallest falsifiable integrated prototype. No additional
mandatory external reviewer or activation gate is introduced by this scenario.
