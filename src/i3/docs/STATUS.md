# I3: current research and engineering status

**PROPOSAL. UNREGISTERED. NO ACTIVE ENGINE ENTRYPOINT. NO GENERAL SCIENTIFIC GO.**
I1 remains the active engine. Authority: [engine contract](../engine.json),
[registry](../../../config/engine-registry.json),
[ADR-0014](../../../docs/decisions/ADR-0014-i3-lignee-enjeu-de-soi.md).

Updated 6 November 2026 for the owner-requested scenario integration
[#1059](https://github.com/josselin-orta-lab/individual-zero/issues/1059).
Evidence baseline: `e4eb3e80c9dc48e131e05383d952909bd86213b7` (PR #1058).
That integration changed documentation and priorities only. The subsequent
Stage-0 slices add laboratory metadata/arithmetic and read-only funding/revision
receipts, not cognition or physics; no validation/reserve world or scientific-study life.

## Latest software result: shared first-contact prior shows generic capacity

8 November 2026: the prospectively frozen
[shared first-contact prior gate](studies/stage1-shared-first-contact-prior/RESULTS.md)
passes D0-D7 and returns:

`SHARED_FIRST_CONTACT_PRIOR_CAPACITY_SHOWN`.

At omega=0 the imagined K80 path remains exactly Candidate-H:
**24 RELEVANT / 56 FALLBACK**, 40 declines, mean probe work 470.05 simulated
steps/state. P80, the directly perceived first-drink path, rises from
**48/80 RELEVANT at omega=0** to **56/80 at omega=0.25/0.5** and **72/80 at
omega=1**. All Stage-A states and fallbacks are funded; renaming and shared-prior
identity controls pass.

The positive result needs a strong boundary. The newly relevant P80 states are
**not water-deficit states**. At omega=0.25/0.5 they are energy=50 and
vigilance=50; at omega=1 they are energy=20/30/40/50 and vigilance=40/50.
The generic RMS prior is therefore demonstrating an inherited
action-opportunity expectation dominated by its energy/vigilance scale, not a
water-specific instinct.

F108 carried-food relevance also rises and saturates at 108/108 by omega=0.5,
while K80 imagined relevance is non-monotone (24 at omega=0, then 12/14/12 for
positive omega 0.25/0.5/1). D7 confirms that this divergence occurs **after**
the exact shared RMS prior; the imagined and perceived decision structures
respond differently to the same inherited expectation.

This is capacity evidence only. It does not authorize runtime adoption or a
new live panel.

Both prospectively frozen software prerequisites now PASS:

- [Candidate-I shared-prior integration](studies/stage1-candidate-i-shared-prior-integration/RESULTS.md):
  `CANDIDATE_I_SHARED_PRIOR_INTEGRATION_PASS`, I0-I9 all PASS, every
  first-contact fallback funded and exactly addend-free;
- [composite-funding reducer repair](studies/stage1-composite-funding-reducer-repair/RESULTS.md):
  `COMPOSITE_FUNDING_REDUCER_REPAIR_PASS`, R0-R6 all PASS.

The first prospectively frozen runnable multi-option protocol has now failed
its mandatory S1 identity rule:
[CANDIDATE_I_RUNTIME_INTEGRATION_DEFECT](studies/stage1-candidate-i-runtime-integration/RESULTS.md).

Its proposed "with-information top set differs from without-information top
set" rule disagrees with frozen #1170 on **700/1,128** one-trial P80/F108
states: 696 false negatives and 4 false positives. Both Python 3.11 and 3.12
reproduce the same fracture. The implementation was not merged and 60/61
remain unopened.

The failure clarifies that two semantics had been conflated. #1170 direct
first contact asks whether the unknown **trial itself is strictly worth taking**
versus its own no-trial comparator and every other offered option. #1163
post-contact asks whether extra information changes the decision top. Those
questions remain distinct.

The prospectively frozen successor
[Candidate-I runnable multi-option integration v2](STAGE1_CANDIDATE_I_RUNTIME_INTEGRATION_V2.md)
now passes S0-S11:
[CANDIDATE_I_RUNTIME_INTEGRATION_V2_PASS](studies/stage1-candidate-i-runtime-integration-v2/RESULTS.md).

Final tested source `9c5ef3e2657c1d2be1e0e8f0b592b6a957dcff6b`,
Actions `42500166929`, Python 3.11/3.12, 918 tests. The exhaustive one-trial
reduction is **0/1,128 mismatches**. Multi-trial permutation/renaming,
addend-free fallback custody, omega ablation, composite funding, post-contact
parity and already-exposed runtime smoke all pass.

Two review defects were corrected before the final verdict: the fallback
Stage-A receipt omitted already-paid base/recurrence work, and forced-failure
restoration omitted transient `_unknown`/`_presence` caches. Neither repair
changed scores, relevance, actions, omega, fixtures or V2-R1/R2.

The fresh
[Candidate-I 60/61 DEVELOPMENT protocol](studies/stage1-candidate-i-development-60-61/PROTOCOL.md)
is now prospectively frozen. It allocates 12 matched blocks / 48 lives across
stable, depletion and pulse, with four arms: P1.3, Candidate-H, Candidate-I
native omega and same-genome Candidate-I omega=0. Canonical plan digest:
`a8e8dc955a3324e3f78986b4e4de8d8894f8196e1ba7321b89f295016dc1c876`.

The frozen 60/61 panel was subsequently opened exactly once by #1182 after
the omega=0 arm and source-locked runner had merged. The software matrix passed,
then the panel stopped after **5 completed lives** while generating
`stable-60-g902:personal_relevance_candidate_h_v1` with
`CognitiveFundingError: cognitive work exceeds available energy/vigilance`
inside `learn_from_outcome -> branch_memory.observe`.

This is
[ENGINEERING_FAILURE_NOT_A_DEATH](studies/stage1-candidate-i-development-60-61/RESULTS.md),
not a J1-J7 result. Originals are archived on
`evidence/i3-stage1-candidate-i-60-61-46c52b2a5a81`, evidence commit
`ebb8d1f9`. **60/61 are exposed and permanently closed. Do not rerun.**

The prospectively frozen
[branch-decision settlement repair](studies/stage1-branch-decision-settlement-repair/RESULTS.md)
now returns **`BRANCH_DECISION_SETTLEMENT_REPAIR_PASS`**. B0-B9 all pass on
Actions `42505811626`, Python 3.11/3.12. The synthetic legacy mismatch is
reproduced, full Stage-A + Stage-B cognition remains charged, Candidate-H/I now
bind total decision work to the matching pre-Stage-A body, ordinary learning
semantics remain unchanged, and stale/missing settlement receipts fail closed.
Merged repair authority: `5ee25b3b0f39050321b0b5c6147bdae0e3e68ec5`.

60/61 remain exposed and permanently closed with no J1-J7 verdict. The next
fresh lived question is now prospectively frozen on
[Candidate-I 62/63](studies/stage1-candidate-i-development-62-63/PROTOCOL.md).
It uses new DEVELOPMENT indices 62/63, world seeds 2062/2063, G0 903/904 and
new life seeds, while preserving the four arms and J1-J7 exactly. Machine plan
digest:
`ba8e934c33fd060318721883e4f6e92034dd68ed743cf044ac97f9f4dc3a21e7`.

The source-locked 62/63 runner subsequently merged in #1186. The separate
one-shot transport #1187 passed the full Python 3.11/3.12 software matrix and
then opened 62/63 exactly once from execution source
`81f05a7fb79c9e1f264cab63a363dc181ff663b2`, Actions `42507594360`.
**18 lives completed** before
`depletion-62-g903:personal_shared_prior_candidate_i_v1` stopped with
`RuntimeError: missing branch decision settlement start body`.

The originals and failure receipt are archived on
`evidence/i3-stage1-candidate-i-62-63-81f05a7fb79c`, evidence commit
`1e975da3`. This is
[ENGINEERING_FAILURE_NOT_A_DEATH](studies/stage1-candidate-i-development-62-63/RESULTS.md),
not J1-J7 evidence. **62/63 are exposed and permanently closed. Do not retry.**
PR #1187 is closed and unmerged.

Source inspection identifies a narrower rollback-authority defect: Candidate-I
captured its probe snapshot before clearing the previous decision's `last`.
An unfunded Stage-A restore could revive that stale `last` after the matching
settlement receipt had been cleared. The branch-memory fail-closed guard then
correctly rejected learning.

The prospectively frozen software-only
[Candidate-I probe-restore authority repair](studies/stage1-candidate-i-probe-authority-repair/RESULTS.md)
now returns **`CANDIDATE_I_PROBE_AUTHORITY_REPAIR_PASS`** on repair-code
authority `5ca8f2dcb7f87c18880ea3c45b773eec0daab2d4`, Actions
`42517714784`, Python 3.11/3.12. U0-U9 all pass. Rollback snapshots no
longer own `last`, branch settlement or pending learning authority; unfunded
exits restore only reversible first-person state, while FALLBACK/RELEVANT create
fresh current-decision authority. The funded FALLBACK also recaptures the
current opportunity-presence receipt from its one real final perception, so
recurrence storage no longer loses that lived observation after rollback.

60/61 and 62/63 remain permanently exposed and closed with no J1-J7 verdict.

The prospectively frozen
[Candidate-I lifecycle-custody stress](studies/stage1-candidate-i-lifecycle-custody-stress/RESULTS.md)
now returns **`CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_PASS`**. Tested source
`1bdca27ae95509e9b54817bd25b2c0a21872c069`, Actions
`42518978398`, merged authority
`5e85106157afa6c600dd1983efde94fb80032977`. Python 3.11/3.12 pass the
975-test suite; navigation passes on 3.11. All L0-L11 are green and all nine
already-exposed DEVELOPMENT-0 smokes reduce with `smoke_failures=[]`.

This is engineering readiness only. It does not evaluate survival, uptake,
route frequency, omega direction or J1-J7.

The frozen
[Candidate-I 64/65](studies/stage1-candidate-i-development-64-65/RESULTS.md)
panel was subsequently opened exactly once from execution source
`427eedd374575e84d725ef3a6e287a69f1991518`, Actions
`42522541342`. The Python 3.11/3.12 software matrix passed before exposure.

The runner admitted **35 complete reductions**. The 36th original,
`pulse-64-g905:personal_shared_prior_candidate_i_omega0_ablation_v1`,
also completed as a 141-step natural `zero_food` death, but reduction stopped
afterward in `stage0_revision._resource_events` with
`ValueError: processing status contradicts paid base block`.

The original and all prior evidence are archived on
`evidence/i3-stage1-candidate-i-64-65-427eedd37457`, evidence commit
`f09806130d0ea0d9d9a66a12d6baa3afe5b66d15`.
This is **ENGINEERING_FAILURE_NOT_A_DEATH**, not J1-J7 evidence.
**64/65 are exposed and permanently closed. Do not retry.** #1195 is closed
and unmerged.

Read-only inspection of the archived 36th original localizes the reducer defect
at decision 134: Candidate-H Stage A was fully paid
(4 cycles / 18 simulated steps / 248 memory items), Stage B was exactly zero,
and the final public status was `NO_PROCESSING_BUDGET`. The Stage-0 reducer
incorrectly applied that Stage-B status to total Stage-A+Stage-B work.

The prospectively frozen software-only
[multi-phase processing reducer repair](studies/stage1-multiphase-processing-reducer-repair/RESULTS.md)
now returns **`MULTIPHASE_PROCESSING_REDUCER_REPAIR_PASS`** on tested source
`252419ff099fbb95990fb7a19426864c0a5a8346`, Actions
`42523805013`. Python 3.11/3.12 pass **999 tests**; M0-M9 are all green.

The reducer now authenticates total work separately from route-specific
processing ownership: Candidate-H finals, Candidate-I P1.3 fallback and
post-contact use Stage B; Candidate-I `INFORMATION_FINAL` uses its retained
Stage A. All cognition remains physically charged.

After this independent PASS, a read-only check of the archived 36th 64/65
original found zero processing/work contradictions across all 141 trace rows;
the former t=134 failure reduces as Stage-B `processing_paid=false`. This does
not admit the life to J1-J7.

The prospectively frozen
[Candidate-I lifecycle-custody stress v2](studies/stage1-candidate-i-lifecycle-custody-stress-v2/RESULTS.md)
now returns **`CANDIDATE_I_LIFECYCLE_CUSTODY_STRESS_V2_PASS`** on tested
source `f9544cf2e22f69a953fdd4141adc6991547c7e16`, Actions
`42524858889`, merged authority
`fbaecde68d6fbcb5a9ec8c6d5908b4b1880137bd`. Python 3.11/3.12 pass;
the 3.11 suite runs **1008 tests**. Historical L0-L11 remain unchanged and
V0-V8 all pass on the generic paid-Stage-A / zero-Stage-B
`NO_PROCESSING_BUDGET` boundary using actual H/I production decisions.

This is engineering readiness only. 60/61, 62/63 and 64/65 remain permanently
exposed/closed with no J1-J7 verdict.

The fresh
[Candidate-I 66/67](studies/stage1-candidate-i-development-66-67/RESULTS.md)
panel was subsequently opened once by one-shot transport #1205 after the exact
Python 3.11/3.12 software matrix passed. Execution source:
`9db49f8c3b522e73fd42ab5ca63fcc5d74662b99`; Actions
`42532125173`.

**Ten lives were admitted.** The eleventh original,
`stable-67-g907:personal_shared_prior_candidate_i_v1`, completed runtime and
was archived, then Stage-0 revision reduction stopped with
`ValueError: invalid Candidate-I post-contact processing receipt`.

Evidence is preserved on
`evidence/i3-stage1-candidate-i-66-67-9db49f8c3b52` at
`18a7e27bd79de81280e171fdf682f8a5f4195830`. #1205 is closed/unmerged.

**66/67 are permanently exposed and closed. There is no J1-J7 verdict.**
Do not rerun, resume, complete remaining cases, retroactively admit the
eleventh life after repair, or use partial lived metrics to tune Candidate-I.

Read-only localization shows a reducer-ownership gap: Candidate-I post-contact
correctly delegates to Candidate-H #1163, but the reducer accepts only nested
complete Candidate-H finals. A legitimate nested Candidate-H
`PROBE_UNFUNDED` therefore fails before Candidate-H's already-valid processing
semantics are applied.

The next intervention is prospectively frozen in
[STAGE1_POST_CONTACT_PROBE_REDUCER_REPAIR.md](STAGE1_POST_CONTACT_PROBE_REDUCER_REPAIR.md).
Q0-Q9 are software-only. The repair must support nested Candidate-H
`PROBE_UNFUNDED` under both incomplete funding classes, preserve complete
post-contact/direct-H semantics, fail closed on malformed phase receipts, and
must not use a 66/67 original as an acceptance fixture.

## Current handoff: 58/59 exposed, no Candidate-H continuation verdict

8 November 2026: the frozen Candidate-H DEVELOPMENT 58/59 transport opened
the panel once under execution source
`c2f63445ce8a3033ce8a2adfb9a0b1417b21c021`, Actions
`42484179997`. Software checks were green before exposure.

The execution archived originals on
`evidence/i3-stage1-candidate-h-58-59-c2f63445ce8a`, but stopped while
reducing the third arm with
`ValueError: resource processing status disagreement`. The failure receipt is
`ENGINEERING_FAILURE_NOT_A_DEATH`: two cases were reduced before the stop
(reference 400-step censored; Candidate-G 98-step zero-water death), while the
Candidate-H original was archived but not admitted to the aggregate.

Because worlds opened, the frozen `STOP_AND_ARCHIVE_NO_RETRY_NO_REPLACEMENT`
rule applies. **58/59 are exposed and closed.** Do not rerun, replace seeds or
infer H1-H6 from the partial panel. There is no Candidate-H engineering
continuation PASS/FAIL from 58/59.

## Read-only 56/57 audit: first contact is represented asymmetrically

The preserved
[first-contact audit](studies/stage1-candidate-g-development-56-57/POSTHOC_FIRST_CONTACT_AUDIT.md)
reduces the immutable 56/57 originals without replay or counterfactual scoring.

Its main new observation is structural: in all **28/28** Candidate-G
pre-contact on-water decisions, unsupported `boire` is forecast as the generic
average step (water -0.4, uncertainty 1, information value 0). The same unknown
first drink receives a paid unsupported-effect prior when it is *imagined* at
an unseen frontier. P1.3 can cross the flat first-contact decision through its
designer curiosity addend; Candidate-G usually cannot.

The audit also separates two descriptive failure modes: an unsupported mode
with little exploration/first-contact value, and a supported mode where
Candidate-F-like cognition cost and sleep/inactivity return. It does not alter
the 56/57 frozen verdict or authorize tuning on exposed evidence.

## Next Stage-1 software slice: shared first-contact prior

The owner-approved
[shared first-contact prior protocol](STAGE1_SHARED_FIRST_CONTACT_PRIOR.md)
is the next bounded Stage-1 intervention. It asks whether the same inherited
RMS/omega expectation can govern an unsupported action whether the trial is
imagined or the resource is already perceived.

This slice is **software laboratory only**. It must pass frozen defect stops
D0-D7 before interpreting capacity. The primary R1 question is whether some
declared `omega > 0` makes at least one perceived-water first drink relevant
where `omega = 0` does not. `NO_CAPACITY` is a valid result and must not be
rescued by widening omega, rescaling the prior or changing fixtures.

Do not modify Candidate-H runtime, do not consume 58/59 as a tuning set, and do
not open another World/life panel from this protocol. P1.3 remains reference;
Stage 2 remains blocked.

## Latest software integration: unified Candidate-H passes

8 November 2026: the prospectively frozen
[unified Candidate-H integration](studies/stage1-candidate-h-unified-integration/RESULTS.md)
passes U0-U9 on final tested source
`bf527c92dd445b4f4ffcab4c8a24cbe8ed0c959f`, Actions
`42482799511`, Python 3.11/3.12.

The integrated software preserves the two previously frozen relevance semantics
exactly: first contact remains 24 RELEVANT / 56 FALLBACK with zero mismatches;
post contact remains 68 / 12 with zero mismatches.

On the fixed 60-decision routing panel, Candidate-H produces 37 complete P1.3
final routes and 23 Candidate-F final routes. All five required route classes
are observed, all 37 P1.3 fallbacks match their independent same-body P1.3
controls, phase accounting passes, omega -1/+1 changes nothing, and projector
state always returns to `reference/chunk_end`.

Verdict:
**`CANDIDATE_H_UNIFIED_SOFTWARE_INTEGRATION_PASS`**.

Three engineering verifier defects were corrected before the final verdict:
an over-strict import assertion, exact floating settlement equality despite the
prospectively frozen 1e-12 tolerance, and an extra bit-exact body condition
incorrectly folded into U3. None changed the candidate, relevance predicates,
60-decision panel or U0-U9 rules.

This PASS authorizes only a **separately frozen fresh DEVELOPMENT protocol**.
Candidate-H is still absent from `runtime/life.py`; no fresh World/life,
selection, validation, reserve, adoption or Stage 2 is authorized yet.

## Latest software gate: Candidate-H post-contact relevance fallback passes

8 November 2026: the frozen
[post-contact Candidate-H gate](studies/stage1-candidate-h-post-contact-relevance/RESULTS.md)
passes P0-P6:
`CANDIDATE_H_POST_CONTACT_SOFTWARE_GATE_PASS`.

All 80 personally learned-water states fund the actionable-belief plus
commensurate Candidate-F Stage A. **68** states are genuinely decision-relevant;
**12** have positive information but do not change the top decision and
therefore fall back. All 12/12 fallback states fund a complete P1.3 decision,
match same-body P1.3 exactly (max score error 0), and preserve their pre-probe
P1.3 top set.

This confirms that positive information value alone is still too broad:
relevance must be defined by an actual decision-top effect under one score
geometry.

Together with the first-contact H0-H5 PASS, both relevance semantics now have
bounded software evidence. The next admissible slice is a **unified Candidate-H
runtime software-integration gate** only. It must combine the two already-frozen
rules without changing them, pay every probe/fallback, preserve P1.3 on
fallback, and reconcile runtime forecast ceilings. No fresh World/life panel is
authorized by this PASS.

## Latest software gate: Candidate-H first-contact relevance fallback passes

8 November 2026: the frozen
[Candidate-H first-contact gate](studies/stage1-candidate-h-relevance-fallback/RESULTS.md)
passes all H0-H5 rules:
`CANDIDATE_H_FIRST_CONTACT_SOFTWARE_GATE_PASS`.

Candidate-H pays the canonical Candidate-F relevance probe first. In the 24
strictly relevant states it executes no fallback. In all **56/56** non-relevant
states it can still fund a complete P1.3 four-plan fallback from the body after
the paid probe, with exact same-body P1.3 score identity (max error 0).

Crucially, all **20/20** support-only projector-drift states identified by #1161
return to their pre-probe P1.3 top set. Across all 56 fallback states there are
**0** top-set changes versus pre-probe P1.3. The fallback adds paid work rather
than hiding it: mean combined simulated work is 503.36 steps in fallback states
versus canonical probe mean 470.05.

The first implementation run reported H4 FAIL because the H4 verifier
reconstructed fixture bodies with a captured outer-loop level=50. That
bookkeeping defect was corrected to use each row's immutable level; candidate
computation and H0-H5 were unchanged. Final run `42478647427` passes on
Python 3.11/3.12.

This PASS is **first-contact software evidence only**. No runtime Candidate-H or
fresh live panel is authorized. Next freeze a separate software falsifier for
**post-contact relevance gating** under personally learned actionable belief.
P1.3 remains reference; 56/57 remain exposed and closed.

## Latest software diagnostic: support is not decision relevance

8 November 2026: the declared
[support-vs-relevance diagnostic](studies/stage1-candidate-g-support-vs-relevance/RESULTS.md)
classifies **`SUPPORT_TRIGGER_ORDINARY_POLICY_DRIFT_PRESENT`**.

On the frozen #1146 grid, personal recurrence support exists in all 80 states,
but only 24 states strictly select the epistemic trial. Among the remaining 56
support-only states, switching the whole decision to the canonical Candidate-F
projector changes the ordinary top option set in **20/56**, including **4 unique
winner changes**. Across all states the top set changes in 44/80.

The effect is not a small accounting detail: the four fixed ordinary plans cost
37 simulated steps under P1.3 versus 368.79 on average under Candidate-F in the
support-only states, with maximum pairwise ordinary score-gap shift 0.02643.

This identifies a structural defect in Candidate-G's activation rule:
**personal support is treated as if it already implied current decision
relevance**. The accurate projector can therefore alter ordinary policy even
when the information trial is not strictly advantageous.

Candidate-G live remains closed and 56/57 remain exposed. The next admissible
work is a prospectively frozen **software-only relevance-gated fallback**
falsifier: pay to establish relevance, use P1.3 for the final ordinary decision
when the epistemic trial is not strictly advantageous, and use one commensurate
Candidate-F decision only when it is. Any fallback must pay both computations;
no reimbursement, omega, action-specific rescue or fresh World/life panel.

## Current engineering handoff: Candidate-G 56/57 continuation FAIL

8 November 2026: the prospectively frozen no-omega Candidate-G DEVELOPMENT
pilot is complete
([result](studies/stage1-candidate-g-development-56-57/RESULTS.md)).

Execution source `6ce6fbc2025f9f6e6b34b779142f90c10c28a1e0`, Actions
`42477021573`, 36/36 original lives preserved on
`evidence/i3-stage1-candidate-g-56-57-6ce6fbc2025f`.

The frozen continuation rule is **FAIL**. Candidate-G genuinely alternates
between the canonical accurate projector and P1.3 reference (368
information-active decisions, 1213 reference-only), and cuts lived projection
cost sharply versus rejected Candidate-F: 0.9161 vs 2.1983 energy/step and
1.2723 vs 3.1118 vigilance/step. But R5 fails unchanged:
`NO_PROCESSING_BUDGET` is **2.8463% Candidate-G versus 2.0436% Candidate-F**.

Survival was not a criterion, but is an adverse descriptive result:
Candidate-G reaches the 400-step censoring horizon in **0/12** lives, P1.3 in
**3/12**. Water uptake is 16 Candidate-G versus 196 reference.

A posthoc funding-composition read shows Candidate-G nevertheless has fewer
total unfunded decisions (9.1082%) than Candidate-F (21.4578%), because
Candidate-F more often fails earlier at `NO_FUNDED_SCORE`. This does **not**
replace R5 or rescue the candidate.

**56/57 are exposed and closed. Do not retune on them.** Stop the Candidate-G
live path. The next admissible work is read-only analysis of preserved evidence
or a new software-only architecture falsifier on established fixtures. No fresh
live panel, selection, validation, reserve, reference adoption or Stage 2 is
authorized.

## Latest scientific gate: genomic omega Candidate-F rejected

7 November 2026: the full frozen
[Stage-1 omega ADR-0015 gate](studies/stage1-omega-adr0015/RESULTS.md)
completed under execution source
`ca506554e67eddde08e71ba6872df3b50f3ea4be`, Actions run
`42416437088`, with durable prerelease
`i3-stage1-omega-adr0015-ca506554e67e`.

All technical custody completed: 16/16 selection shards, 24/24 validation
shards, both aggregates, 47 workflow jobs with zero failures, and 85 durable
release assets. G6 custody passes. The scientific verdict is
**`FAIL_FROZEN_STAGE1_OMEGA_GATE`**.

Validation survival over 240 main lives per arm is stark:

- P1.3 reference: **82/240** survivors;
- selected Candidate-F with inherited omega: **0/240**;
- the same selected candidate genomes with omega forced to zero: **0/240**.

Candidate survival is zero in every F0 family and every population. Reference
survival is stable 25, depletion 41, pulse 16.

Revision also collapses: candidate complete-rank mean is 401.0 with zero
reacquisitions, versus reference 282.5875 with 35 reacquisitions. Candidate is
worse in all 8 populations.

Selection shifts omega upward in only 6/8 populations, below the frozen 7/8
G3 rule. Pooled omega does shift from 0.076728 in the candidate pools to
0.154818 among selected genomes, but this does not rescue G3.

Actual omega versus same-genome omega=0 has zero survival difference in all
8 populations and all three F0 families because both candidate arms die
universally. Therefore G4/G5 fail as well.

Frozen rule verdicts: **G1 FAIL, G2 FAIL, G3 FAIL, G4 FAIL, G5 FAIL, G6 PASS**.

Candidate cognition on realized validation trajectories costs about
2.23494 energy / 3.13911 vigilance per lived step, versus 0.58475 / 0.71725
for P1.3. Omega-zero has nearly the same cost as the candidate. This is
descriptive, not proof that cost alone causes the collapse.

**DRIFT DETECTED:** Candidate-F/omega is rejected on F0. Do not tune omega,
change G1-G6, select the six favorable populations, or add a Stage-2 compute
rule to rescue exposed validation 120..167.

The next bounded Stage-1 question is causal and narrower: preserve P1.3
decisions while physically paying an equivalent Candidate-F information
computation burden. That **cost-only reference-choice control** can distinguish
cost collapse from policy-choice collapse. It must be software-falsified first
and use fresh development conditions only if later executed.

P1.3 remains reference. I3 remains unregistered. Stage 2 remains blocked and
the P4 reserve remains sealed.

## Latest correction: canonical Candidate-G set is 24, not historical 32

8 November 2026: the frozen canonical numerical audit
([result](studies/stage1-candidate-g-canonical-numeric-audit/RESULTS.md))
completed at source `ce6c16bbae6bdf9d3f46cdb38bebbdcd0dc776ee`,
Actions `42474206334`, Python 3.11/3.12 PASS.

Historical float per-step and canonical high precision both pay exactly
18 cycles, 201 memory items and 1288 simulated steps/state. Yet canonical high
precision selects **24 states / 0 water**, while historical float selects
32 / 8 water. The only eight changed state identities are water 40 and 50 at
horizons 4/6/8/12.

Crucially, canonical high precision's selected set is **identical 24/24** to
Candidate-F's event-local projection set, with no extras or misses. Candidate-F
uses mean 470.05 simulated steps/state.

Classification:
**`HISTORICAL_WATER_SELECTIONS_NUMERIC_ARTIFACT`**.

This resolves the residual noted after #1149. Do not spend further Stage-1 work
trying to recover the historical eight water states. The projection question is
now sufficiently answered for this grid: Candidate-F is cheap and
decision-equivalent to the canonical oracle.

Next bounded question: separate Candidate-F's projection from the rejected
genomic-omega live architecture. Freeze a Candidate-G integration gate that
uses personal recurrence plus Candidate-F projection **without omega**, and
measures whether projection cognition itself is fundable before any new life
panel.

## Latest negative diagnostic: exact distress reuse remains too expensive

8 November 2026: the declared exact distress-reuse diagnostic
([result](studies/stage1-distress-reuse-diagnostic/RESULTS.md)) completed at
source `96455f010a8ad150536db1bded0f01843b761860`, Actions
`42473511648`, Python 3.11/3.12 PASS.

The frozen classification is **`FEATURE_REUSE_INSUFFICIENT`**. Starting from
#1153's 853.3 simulated steps/state, consecutive identical feature reuse gives
an optimistic 778.5. An ideal decision-local exact feature memo, with **no
memory/read/write charge at all**, still gives 657.9. Candidate-F's prospective
threshold was 470.

Therefore further exact memo/cache work cannot plausibly close this gap under
the exposed fixture. The 32/8/24/40 decision surface remains unchanged.

**DRIFT DETECTED:** close this engineering route. The next bounded Stage-1
question is architectural: audit why Candidate-F's cheap event-local projection
misses the 8 water-deficit decisions that exact per-step recovers. Test whether
the residual is localized around generic predicted-death, distress-threshold,
restoration or option-shifted event times. No water/action-specific patch is
authorized.

## Latest exact-cost reduction: predicted-death truncation passes

8 November 2026: the death-truncated per-step falsifier, frozen at
`5fe2edb52f73e133178fbd77c579b2f9b6149c04`, completed at source
`0c3dc70d1de64a3c62c5e60e7ac6e1392b0fd549`, Actions
`42472935275`, Python 3.11/3.12 PASS. See the
[durable result](studies/stage1-death-truncated-per-step/RESULTS.md).

The structural verdict is **`DEATH_TRUNCATED_PER_STEP_EXACT_PASS`**.
Projection/value/body errors are at numerical-noise scale. The frozen #1146
Candidate-G counts exactly match per-step truth: 32 selected, including 8
water-deficit states, and 40 declines.

All 400 projection calls reach predicted death before step 255. Paying only
endpoints actually reached reduces mean work from 1288 to **853.3 simulated
steps/state** and mean bill from 2.9762/3.476 to **2.1068 energy / 2.6066
vigilance**, with the common forecast still fixed at 1288.

Candidate-F cost parity is not reached, so **no runtime candidate is
authorized**. The remaining compute gap is now about 383 simulated steps/state.
Before another cache, measure exact common prefixes among the five projection
calls within each frozen Candidate-G state. Only a demonstrated reuse opportunity
may justify a new decision-local representation.

## Latest accounting result: exact cache funds 80/80 but memory dominates

8 November 2026: the frozen exact-cache accounting sensitivity
([result](studies/stage1-separable-cache-accounting/RESULTS.md)) completed under
source `fddf08637651f7e1b5f0cf5577e3415ca4edf2e5`, Actions
`42472340815`, Python 3.11/3.12 PASS.

Both predeclared accounting bounds fund all 80 #1146 states, so the primary
classification is **`CACHE_ACCOUNTING_ROBUSTLY_FUNDED`**. The exact cache also
retains decision relevance: 32 selected epistemic states under the optimistic
bound and 39 under the conservative bound.

The separately frozen runtime-advance rule nevertheless **fails**. Mean actual
bill is 7.7591 energy / 3.5322 vigilance for the lower bound and 17.1839 /
12.9570 for the upper bound, versus Candidate-F's frozen #1149 bill of 1.3402 /
1.840. No runtime candidate is authorized.

The bottleneck is no longer projection accuracy or yes/no funding ambiguity.
It is the stored representation: 1,848 fresh traces write 1,912,680 memory items
while only 152 later accesses hit a trace (7.6%). Paying four 255-element exact
arrays per trace is a bad exchange for that reuse rate.

Next Stage-1 architecture falsifier: **exact death-truncated per-step
projection**. Stop computation at the first predicted vital zero and sum the
absorbing maximal-distress tail analytically. The current per-step diagnostic
prepays all 255 unit chunks even though no new bodily distress is evaluated
after death. This candidate changes work only, never projected value. Open
sparse exact checkpoints only if this simpler optimization remains too costly.

## Latest structural result: exact separable projection cache passes

8 November 2026: the exact decision-local separable-cache falsifier, frozen at
`2887239575771c9ec3afe17d898a8d38135f68b6`, completed at source
`74725372f82ad490467f20cf0a69e815650bae7b`, Actions run
`42471715382` (Python 3.11/3.12 PASS). See the
[durable result](studies/stage1-separable-projection-cache/RESULTS.md).

The candidate reproduces the 255-step per-step truth at numerical-noise scale:
max pairwise decision bias **2.22e-15**, projection-equivalent invariant
**1.33e-15**, max final-body channel error **0**. All frozen structural rules
pass. Exact reuse is observed in both fixture families: 972 trace hits on the
486-case grid and 50 on the nonlinear #1150 option set.

This establishes **representational feasibility only**. The current I3
accounting prices full model-level simulated steps, not an isolated
channel-distress sample. The descriptive channel-sample lower bound is therefore
not a CognitiveWork bill and cannot support an energy/vigilance claim.

Next bounded question: freeze a physical accounting/capacity contract for cache
construction, reads, storage and rebuilds, then run the frozen #1146 Candidate-G
80-state kernel under real CognitiveBudget. If a defensible paid construction
is not fundable, report consistent foresight as unaffordable at current physical
prices. P1.3 remains reference; no World/life or runtime adoption is authorized.

## Latest exploration: cheap consistent-projection shortcuts fail

Two declared exploratory probes on the #1146 fixtures, measured against the
per-step projection ([results](studies/stage1-affordable-projection-probes/RESULTS.md)):

- **Local sensitivity.** Linear expansion errors: wait 0.0034, sleep 0.0055,
  eat 0.30, drink 1.91.
- **Decision-time anchored grid.** Decision bias 0.2153, against 0.2164 for the
  reference.

Neither approaches 1e-3. The next design, not implemented, is a separable
cached projection: exact per-channel discounted tables held as paid,
capacity-bounded memory, rebuilt on drift change, with death coupled through
the minimum time-to-death. The honest alternative outcome is a scientific
result: consistent foresight unaffordable at current physical prices.

## Latest diagnostic: Candidate-G depends on projection consistency, not recurrence

#1146 passed Candidate-G's software gate with 1/80 strictly advantageous
epistemic trials under the P1.3 `chunk_end` projection. A declared, descriptive
rerun of the same grid ([results](studies/stage1-candidate-g-projection-dependence/RESULTS.md))
changed only the projection:

| Arm | Epistemic trials | Paid simulated steps per state |
| --- | --- | --- |
| reference | 1 | ×1 |
| Candidate-F projection | 24 | ×8.9 |
| per-step | 32 | ×24.3 |

The accurate projections make information decision-relevant. Their cost is
the architectural obstacle, consistent with the processing-budget failures of
the funded Candidate-F gate. Candidate-F's projection selects 0 water-deficit
states where per-step selects 8, which is worth an audit.

Next proposal, frozen before any code: an affordable consistent projection,
namely one accurate projection plus paid local sensitivity per decision, reused
across options. No world or panel is authorized.

## Latest complete causal diagnostic: 54/55 cost-versus-policy remains unresolved

8 November 2026: the fresh 54/55 panel completed all 36 preregistered lives once
under execution source `a27e4c3ccebfcfec610b79f02f00fd2440d1b7dc`, Actions run
`42426687157`. All originals are preserved in evidence commit
`18bfda8bc680afc9df01d1d2ebb308b79efcbc70`.

See the
[complete result](studies/stage1-candidate-f-cost-vs-policy-development-54-55/RESULTS.md)
and
[read-only causal audit](studies/stage1-candidate-f-cost-vs-policy-development-54-55/POSTHOC_CAUSAL_AUDIT.md).

The frozen primary rule required at least one matched block where Candidate-F
dies while the deliberately **overcharged** P1.3-choice control survives.
Observed: **0/12**. Candidate-F and upper-cost both die in all 12 blocks;
ordinary P1.3 survives 4/12. Therefore the preregistered strict
cost-sufficiency counterexample is **not observed**.

This null does not prove cost sufficiency because the control pays Candidate-F
shadow cognition plus an additional P1.3 decision. It is intentionally not
cost matched.

The secondary paired behavior nevertheless implicates policy. Upper-cost lives
longer than Candidate-F in 7/12 blocks, shorter in 1 and ties in 4. In every
one of the four blocks where P1.3 survives, Candidate-F obtains zero water while
the upper-cost P1.3-choice arm obtains water and lives longer than Candidate-F,
although it still dies before horizon.

Aggregate positive water uptake is reference 232, Candidate-F 4, upper-cost 25.
Movement is 831 / 79 / 216 respectively. Across upper-cost lives the shadow
action differs from the actual P1.3 action on 510/2395 decisions.

Cost also remains severe. Upper-cost accumulates 868 P1.3
`NO_PROCESSING_BUDGET` steps and 36.24% physical inactivity. Realized paid
energy/vigilance per lived step is 0.60876/0.75158 reference,
2.06095/2.90923 Candidate-F and 1.66955/2.11048 upper-cost. Trajectories differ,
so these rates are descriptive, not mediation.

**Current interpretation: cost and policy are both implicated; exact mediation
remains unresolved.**

**DRIFT DETECTED:** Candidate-F/omega is already rejected by the frozen gate.
Do not tune it, rerun 54/55, or build another increasingly artificial causal
control merely to obtain a clean percentage. A tighter control is admissible
only if it can match physical cost without granting unpaid P1.3 cognition,
reimbursing the body, forcing actions or otherwise violating I3 contracts. If
no such paid construction is available, stop causal decomposition here and
return Stage 1 to architecture design.

P1.3 remains reference. I3 remains unregistered. Stage 2 remains blocked and
the reserve remains sealed.

## Latest causal diagnostic attempt: 52/53 closed on observer engineering failure

7 November 2026: the prospectively frozen 52/53 Candidate-F cost-vs-policy
diagnostic opened once under execution source
`e10365f605c6e919af1651a5c20f335ae6fd5f40`, Actions run
`42422888044`.

Py3.11/3.12 software preconditions passed. Twelve complete original lives were
archived before the runner stopped while reducing the twelfth life. Durable
evidence commit: `60c5ae22c0b381865ec81678015c41efc1b9d975`.
Artifact: `13593974371`.

The failure is **ENGINEERING_FAILURE_NOT_A_DEATH**. The physical upper-cost
life `stable-53-g902` completed 286 steps and died from zero water. At step
177 the Candidate-F shadow paid 3 cycles + 347 memory items, then P1.3 had
insufficient remaining budget for its own processing block and correctly
reported `NO_PROCESSING_BUDGET` with zero P1.3 work. The historical Stage-0
revision join incorrectly required total decision work to be zero whenever that
P1.3 status was present.

The upper-cost receipt itself is consistent: total work equals shadow +
reference work on all 286 decisions, P1.3 remains sole motor authority, and the
maximum sequential-vs-cumulative settlement gap is only
1.4210854715202004e-14.

Therefore 52/53 are **closed with no rerun** under their frozen stop-and-archive
rule. Only three complete matched stable blocks were reduced before failure;
depletion/pulse were never generated. No cost-vs-policy causal verdict is
evaluated from this incomplete prefix.

See
[52/53 result](studies/stage1-candidate-f-cost-vs-policy-development-52-53/RESULTS.md)
and
[observer failure audit](studies/stage1-candidate-f-cost-vs-policy-development-52-53/POSTHOC_OBSERVER_FAILURE_AUDIT.md).

Next intervention: correct Stage-0 revision's processing-work check **only for
the explicit upper-cost policy** so P1.3 funding status is checked against
`reference_choice_work`, while total physical decision work remains
independently authenticated. Ordinary policy semantics must remain unchanged.
Any renewed diagnostic requires a fresh prospective allocation.

**DRIFT DETECTED:** do not rerun 52/53, reinterpret the partial stable prefix as
a causal result, or weaken the physical-work receipts globally.

## Latest diagnostic: cost paralysis receded, local policy still fails

7 November 2026, [cost-reduced development result](studies/stage1-cost-reduced-development/RESULTS.md)
and [read-only zero-information audit](studies/stage1-cost-reduced-development/POSTHOC_INFORMATION_ZERO_AUDIT.md),
PR #1075. The prospectively frozen 46/47 panel completed once: 24 lives, no
retry or engineering crash, originals archived before reduction.

The candidate meets its **engineering-only** continuation rule: aggregate
physical inactivity is 403/1792 = 22.49% and there are 12 positive water
uptakes. Only 3/12 candidate lives enter terminal NO_PROCESSING lock, versus
the first diagnostic's pervasive early funding collapse. This does **not**
constitute a Stage-1 gate result.

The candidate nevertheless remains 0/12 alive at horizon, with 10 dehydration
and 2 starvation deaths. Reference is 4/12 alive. Candidate cognition costs
2.059937 energy and 3.166388 vigilance per lived step versus 0.476000 and
0.584084 for reference; trajectories differ, so this is descriptive rather
than cost-matched mediation.

The newly visible bottleneck is behavioral rather than merely computational:
candidate sleep occupies 1241/1792 steps (69.25%). None of 8666 paid option
scores has positive information value above 1e-12, despite 8224 (94.90%) having
complete empirical support. In stable/pulse, all eight candidate lives remain
fully funded until death, obtain zero water, and never score a local `boire`
option. Across 400 funded decisions with sensed water <=20 in those families,
drink is available 0 times while sleep is chosen 381 times.

The read-only audit does not reconstruct unarchived branch values. It therefore
does not claim whether zero information is dominated by signal aliasing or an
unchanged best continuation. It does show that 4255 fully supported zero-value
scores introduce at least two distinct new payoff-cell keys, so total payoff
collapse is not a sufficient explanation. Synthetic kernel tests separately
prove that the implementation can produce positive information value.

**DRIFT DETECTED:** stop optimizing duplicate work and do not add a Stage-2
budget heuristic to rescue this local prototype. Its deliberate local repertoire
cannot value discovery of unseen cells: hypothetical movement reveals no new
map cell, while repertoire/memory/prior also differ from P1.3. The next Stage-1
candidate should preserve P1.3's existing first-person spatial repertoire and
learned state, changing the information-value mechanism as narrowly as possible.
Do not rerun exposed 44-47, tune the stationary prior, force resources, or
rewrite Competition. P1.3 remains reference.

Stage 0, #1026, #1054 and the scientific Stage-1 survival/revision gate remain
open. No selection/validation/reserve exposure, activation or scientific GO.

## Current Stage-1 engineering handoff: reference-preserving path

The adverse local prototype has been replaced by a staged P1.3-preserving path:

- #1076: fixed paid 18-record empirical branch memory, empty at birth.
- #1077: `reference_branch_memory_v1`, storage-only P1.3 cost control with
  unchanged decisions and replay allocation before extra storage.
- #1078: paid exhaustive conditional replanning over existing P1.3 plans.
- #1080: conservative frontier belief using P1.3's existing Laplace resource
  rate; unsupported/newborn resource mass remains non-actionable.
- #1081: observable branch-specific continuation plans with a fail-closed
  anti-oracle rule.

The first live integration is now the opt-in
`reference_frontier_information_v1` **engineering probe**. It preserves
P1.3 perception, map/history, effects, TD values, option repertoire, concrete
first motor commands, Competition and Action Control, and inherits #1077's
branch-memory storage/replay rule. Its experimental score removes additive
curiosity/relevance/prudence.

Its information scope is deliberately narrow: each existing `explorer:*`
option is treated as one generic newly revealed-cell probe. If #1080 supplies
personally supported actionable-water belief, the informed forecast may reveal
the existing travel prefix plus one generic move and `boire`. Food probability
and all unsupported mass are non-actionable in this partial mechanism.
Multi-cell independence is not assumed and old `_unknown` counts do not
multiply the probability.

All scored options share one conservative decision-work forecast ceiling.
Actual work alone is physically billed. The default P1.3 reference is unchanged.

This is **not** the complete Stage-1 candidate: unknown-food integrity-effect
distributions, multi-cell joint outcomes, frozen-projection ablation,
zero-perceived-cost diagnostic and scientific source/genotype/case/margin/
multiplicity/stopping locks remain open. No new 48/49 development, selection,
validation or reserve world is authorized by this implementation.

Stage 2 stays blocked. Stage 0, #1026 and #1054 remain open.

## Latest fresh diagnostic: 48/49 stopped by observer engineering failure

The prospectively frozen [48/49 protocol](studies/stage1-frontier-water-development/PROTOCOL.md)
was opened once in run `42364436764`. It stopped in the first three-arm block
after two completed lives. See the immutable
[engineering-failure result](studies/stage1-frontier-water-development/RESULTS.md).

Completed `stable-48-g901` lives:

- P1.3 reference: 128 steps, dehydration death, no water uptake;
- storage-only control: 128 steps, dehydration death, no water uptake, first
  NO_PROCESSING at step 34 followed by 95 inactive steps.

The candidate case did **not** produce a complete life. The external P5e
Competition observer rejected the new frontier witness because its historical
score identity did not include the explicit `information_value` term.
Runner status is `ENGINEERING_FAILURE_NOT_A_DEATH`.

The artifact and six original files are archived under execution source
`a1e53daee016e801289a85c9cd7855798b048051` and evidence commit
`89a36a9186bb9ff89769598baba021f7c79af62a`.

**No scientific or candidate mechanistic verdict is available.** The
preregistered 48/49 panel is closed under its no-retry/no-replacement rule.
Do not resume its remaining cases.

Next: a narrow software-only Competition-observer compatibility fix. It must
preserve the anti-forgery checks and historical witness behavior. Only after
that fix may a new, separately allocated development panel be prospectively
defined. Stage 2 remains blocked.

## Latest complete diagnostic: 50/51 frontier-water mechanism is real but bootstraps too late

The separately preregistered [50/51 result](studies/stage1-frontier-water-development-50-51/RESULTS.md)
completed all 36 lives once in run `42365345012`, with all originals archived
before reduction. The [read-only bootstrap audit](studies/stage1-frontier-water-development-50-51/POSTHOC_BOOTSTRAP_AUDIT.md)
adds no new life.

The candidate's engineering continuation rule is **met**: 7/12 candidate lives
contain positive frontier information and 121 frontier options have positive
information value. This is the first live I3 evidence that the reference-
preserving value-of-information path becomes numerically positive in ordinary
paid lives.

The mechanism activates immediately after relevant personal experience. In all
seven positive-information lives, the first positive information score occurs
exactly one step after the first positive water uptake. Five other candidate
lives never experience water, never obtain positive information and all die.

Survival remains adverse and is not a Stage-1 gate result: reference survives
3/12, storage-only 6/12 and candidate 2/12. Candidate gains no survival block
relative to either control, loses one block relative to reference and four
relative to storage-only. These 12 matched blocks are not independent
populations and no significance claim is made.

The candidate is **not computationally paralyzed**: physical inactivity is only
1.11% and there are 30 NO_PROCESSING_BUDGET steps. Instead it executes 1021
waits and only 410 moves, versus 465 waits and 826 moves in storage-only.
Candidate cognitive cost is also higher on realized trajectories: 0.7612 energy
and 1.0457 vigilance per lived step versus 0.5851 / 0.7274 for storage-only.

The mechanistic interpretation is now sharper: the conservative #1080 belief
refuses to invent a bodily consequence for an unseen resource. That keeps the
model first-person and non-oracular, but creates a circular bootstrap. Before
the individual has personally learned that water can help its body, discovering
water has no actionable frontier-information value. Once the first useful water
experience occurs, the mechanism comes online on the very next step.

Candidate deaths are 7 dehydration and 3 starvation. Food information remains
explicitly unimplemented, so the three starvation deaths show a known scope
limit but do not explain the water-bootstrap failure.

**DRIFT DETECTED:** do not respond by restoring curiosity as a hidden bonus,
tuning 50/51, inventing favorable water behind a frontier, or jumping to Stage
2. The next Stage-1 work must address unknown-outcome bootstrap generically and
prospectively. Any new prior must be action/token/world-renaming invariant and
must not be selected from exposed 44-51 development results.

P1.3 remains reference; I3 remains unregistered. No selection, validation,
reserve exposure or scientific Stage-1 GO.

## Stage-1 bootstrap substrate after 50/51

The adverse 50/51 result is preserved and closed. No later slice reruns those
worlds. The current software-only bootstrap chain is:

- **#1088:** `paid_zero_mean_stake_prior`. Two opposite unsupported effect
  hypotheses along the current distress gradient, p=.5/.5, exact zero expected
  external bodily delta, no action/token/map/World input. Exact CI: 457 I3
  tests.
- **#1089:** exact observed-effect view for future reuse of one action inside
  one subjective branch. No mutation of real EffectsModel/TD/map/RNG and no
  cross-action propagation. Exact CI: 466 I3 tests.
- **#1090:** nested unsupported-action trial value. It separately reports
  no-trial value, frozen post-trial value, informed post-trial value,
  `information_value` and `trial_advantage`. A synthetic test demonstrates
  positive information value from the strictly zero-mean prior. Exact CI: 476
  I3 tests.
- **#1091:** first-person frontier modality prior. P1.3's existing Laplace
  resource-presence formula is retained; conditional water/token modality uses
  symmetric Laplace smoothing over personal incidences. Zero-incidence
  distribution is .5 no resource / .25 water / .25 token. No body utility or
  effect enters the prior. Exact CI: 486 I3 tests.

These pieces answer different uncertainties and must not be collapsed:

1. what modality an unseen frontier may reveal;
2. what an unsupported newly available action might do;
3. how behavior should change after that effect becomes observable.

The source scenario states **2-3 simulated branches** for Stage 1. A direct
3-way modality x 2-way effect product would exceed that declared envelope.

**DRIFT DETECTED:** do not build a generic recursive belief tree, add Stage-2
compute selection, or reopen development 44-51. The next bounded Stage-1 design
must express the existing water-frontier engineering question with at most
three outcome leaves, while keeping resource observation distinct from action
effect. Any such composition remains software/development-only until
prospectively frozen on a fresh allocation.

P1.3 remains reference. I3 remains unregistered. Stage 0, #1026 and #1054
remain open; no scientific Stage-1 GO.

## Latest Stage-1 decision-boundary result: information is real, winner unchanged

The 7 November software sequence now resolves the immediate local ambiguity.

- #1099: without a future matching action opportunity, information was zero in
  160/160 tested multi-deficit states.
- #1101: exact P1.3 water explorer-prefix semantics retained positive
  information but selected an epistemic trial in 0/80 states.
- #1102/#1104: carried unknown food gives genuine information from personal
  safe/toxic experience; in the rich competing-needs fixture it improved meal
  rank in 9/27 states.
- #1105: under **one shared complete cognition-depleted forecast body**, all
  27/27 rich states were fundable; information was positive in 9/27 and raised
  the meal score in 14/27, but the raw winner changed in **0/27**.

This removes the main cost-comparability ambiguity. The Stage-1 computation is
not numerically dead and its real v2 burden does not erase the signal. The
current bottleneck is that P1.3 contains too little representation of reusable
future opportunities for learning an effect to become decision-dominant.

**DRIFT DETECTED:** stop adding local water/food score patches, synthetic
competitor variants or Stage-2 budget rules. The next bounded intervention is a
single generic first-person future-opportunity representation used only to
unblock Stage 1. It is an operational prerequisite, not permission to launch
full Stage 3. It must not encode hidden stock, source persistence, schedules,
world-family identity or a favorable effect prior.

P1.3 remains the reference. I3 remains unregistered. No new scientific life,
selection, validation or reserve exposure follows from these software results.
Stage 2 remains blocked; Stage 0, #1026 and historical #1054 remain open.

## Stage-1 ω (owner decision A): capacity shown, projection bias found

The owner chose option A (7 November 2026): a heritable generic expectation
toward the unknown, ω ∈ [−1, 1], drawn symmetrically and set only by lineage
persistence. Recorded before code in
[STAGE1_OMEGA_SOFTWARE_FALSIFIER.md](STAGE1_OMEGA_SOFTWARE_FALSIFIER.md):

- **Uniform, need-agnostic shift.** The personal RMS prior becomes (ω ± 1)·s,
  so its mean is ω·s and its spread unchanged.
- **Not yet in the genome.** ω is an explicit kernel parameter for now; the
  genome change is deferred so archived v3 digests stay valid.
- **Reference semantics.** The #1101 exact-explorer source change is reused for
  reference-preserving semantics; #1101's rejection stands.

Falsifier 1, executed once on the #1101 grid, no world or life:
`CAPACITY_SHOWN`.

- **R0–R2 pass.** ω = 0 reproduces #1101 exactly, paid work is identical
  across ω, and the direction is monotone.
- **R3 passes.** ω = 0.5 and ω = 1 add 4 positive water-revelation states
  (52 → 56); ω = −1 removes 4.
  ([results](studies/stage1-omega-software-falsifier/RESULTS.md))

**Post-hoc finding, the next blocker.** The P1.3 simulator values longer plans
higher even when the extra steps are waits: food-stressed −1.4263, +1 wait
−1.4151, +3 waits −1.3938. The likely cause is end-of-chunk distress accounting
in the self-projection, an inconsistent bootstrap.

- **Unaffected:** ω's effect, because every arm compares the same plans.
- **Uninterpretable:** absolute signs of Stage-1 trial and revelation
  advantages, including #1101's.

Proposed next slice: a bootstrap-consistency invariant and a projection fix,
gated as a reference change. ω's genome slice and live integration wait for it.

## P1.3 projection consistency: confirmed defect, no cheap fix yet, D1 reframes Stage 1

The plan-length bias is confirmed as a bootstrap inconsistency of the P1.3
projection's end-of-chunk accounting. Per-step projection satisfies the
invariant to 8.9e-16. Measured on a frozen grid
([results](studies/projection-consistency/RESULTS.md)):

- **Opt-in `trapezoid` accounting** (same 8 paid units, exact when distress is
  linear) reduces the worst decision bias only from 0.169 to 0.133.
  Verdict `NO_CANDIDATE_PROMOTED`. The default stays `chunk_end`, bit-identical
  on 60 compared values.
- **Declared diagnostic D1.** The ω falsifier rerun with unbiased per-step
  projection gives:
    - ω's effect strong and monotone: 16 → 52 trial states;
    - at ω = 0, 32 of 40 selected trials epistemic, versus 0/80 under the
      biased projection.

  #1101's sub-decisive-information verdict was largely an artifact.
  Per-step costs 255 units instead of 8 and is not a live option.

Next: candidate C, event-aware accounting (split chunks at closed-form
threshold-crossing and death steps, pay any extra evaluation), under a new
frozen protocol, then the ω falsifier again. Reference adoption needs an
ADR-0015 gate.

## Current reference and observed limits

| Area | Implemented / observed status |
| --- | --- |
| Core | P1.3 adopted on the funded v2 substrate under ADR-0015; first-person cognition is actually paid. P1.2's original rejection remains unchanged. |
| P2 | Equal initial opportunities support lineage comparisons; 0/7729 exact static probe work-vector matches. Probes are descriptive, not cost-matched ceilings. |
| P3 / P4a | Original lineage and held-out pilots completed. P4a selected 47/144 versus random 42/144; population differences -2,+9,-1,-1. General lineage advantage not demonstrated. |
| P4b | Retained learning 84/288 survivors versus 0/288 paid-discard; 144/144 same-genome history pairs have distinct learned-model hashes. This does not demonstrate stable acquired behavioral individuality. |
| P5a / P5b | Learned effects and action-specific readout show strong bounded survival dependence. Removing TD values or replay did not show the same collapse. Actual work and activity differ. |
| P5c | Normal 110/288, curiosity discarded 4/288, risk discarded 105/288, both 7/288. Four genetic populations; no conventional confirmatory inference or information-only cost-equivalence claim. |
| P5d | Original development evidence includes 125 paid carried-food opportunities without a meal selected in the masked-curiosity arm. Full competing scores were not recorded; cause remains open. |
| P5e | Full paid Competition observer and 24 original development lives archived. Normal 7/12 censored, masked 6/12. Masked arm: no collections and no carried-food exposure, so its meal competition is NOT_OBSERVED. |

P5e had 342 normal-arm carried-food opportunities: 333 had another candidate
with a strictly higher raw score. Threshold effects included three raw-top meal
losses and three lower-score meal wins. **This does not establish a generally
broken Competition or resolve the P5d masked-arm case.** The supplied report's
additional hunger/competing-needs interpretation is post-hoc and attributed to
its author, not independently re-executed by this integration.

## Accepted direction; implementation slices and limits below

[ADR-0016](../../../docs/decisions/ADR-0016-i3-generalization-without-imposed-rules.md)
and the single [development plan](DEVELOPMENT_PLAN.md) integrate the
[unaltered supplied scenario](GENERALIZATION_SCENARIO_SOURCE_2026-11-06.md).

Next: **Stage 0** independent-population design, energetic mediation and
first-person diagnostic exposure ([#1060](https://github.com/josselin-orta-lab/individual-zero/issues/1060)).
Keep individuality under [#1026](https://github.com/josselin-orta-lab/individual-zero/issues/1026)
and P5d resource uncertainty under [#1054](https://github.com/josselin-orta-lab/individual-zero/issues/1054).
Then **Stage 1** information value in predicted bodily distress
([#1061](https://github.com/josselin-orta-lab/individual-zero/issues/1061)), followed
by **Stage 2** paid value of computation
([#1062](https://github.com/josselin-orta-lab/individual-zero/issues/1062)).

Change detection/latent causes/factorization, successor features, topological
maps and multi-family lineages remain deferred Stages 3-6. No such mechanism
is implemented or adopted by this update. Competition is a low-priority audit,
not the next survival-policy rewrite. No scripted drinking/eating or hidden
reward bonus may replace a failed experiment.

New validation requires separate preregistration, genuinely independent
populations and previously unopened allocations >=120. The original P4 reserve
1200000..1200199 remains sealed. Eight populations improve exact-test resolution
but do not guarantee power; the proposed 7/8 later lineage direction is not
itself a significance result. See the plan's explicit operational clarifications.

## Evidence and historical custody

Full pre-integration [status ledger](STATUS_BEFORE_GENERALIZATION_2026-11-06.md),
[plan ledger](DEVELOPMENT_PLAN_BEFORE_GENERALIZATION_2026-11-06.md) and
[documentation ledger](README_BEFORE_GENERALIZATION_2026-11-06.md) are retained
byte-for-byte at the same directory depth. Their old next-task instructions
are historical, not the current priority queue. Original artifacts are unchanged.

Direct current references: [P3](studies/p3-mutation-pilot/RESULTS.md),
[P4a](studies/p4a-g2-heldout/RESULTS.md),
[P4b](studies/p4b-paid-outcome-learning/RESULTS.md),
[P5a](studies/p5a-paid-component-screen/RESULTS.md),
[P5b](studies/p5b-paid-readout-heldout/RESULTS.md),
[P5c](studies/p5c-paid-score-addends/RESULTS.md),
[P5d analysis](P5D_POSTHOC_COLLECTION_CONSUMPTION.md),
[P5e protocol](P5E_DEVELOPMENT_PROTOCOL.md) and
[P5e results](P5E_DEVELOPMENT_RESULTS.md).

[TEST_PLAN.md](TEST_PLAN.md) describes software checks; historical test counts
and CI links certify their own SHAs only. Exact current checks belong to the
integration PR. A documentation merge does not create a new scientific result.

## Stage 0: first non-executing design slice

[Design contract](STAGE0_DESIGN.md), issue #1060: eight new G0 candidate pools
(K=40, m=5 per architecture/population), separate F0 selection/validation blocks,
strict complete-outcome ranking and exact sign-test arithmetic with explicit
ties/effective n. New validation identifiers are 120-167; the reserve stays
sealed. Identifiers are not generated genomes, selected winners or observed
lives. This is not a preregistration or a completed Stage 0.

Standalone scalar/metadata tests and full-repository integration checks are
separate; exact CI results belong to the implementation PR. Final family-R
protocol/source locks, practical margins, multiplicity, lineage controls and
#1026/#1054 remain open. No survival, individuality or generalization result is added.

## Stage 0: actual funded-life receipt connection

`lab/stage0_energy.py` verifies full runtime evidence chains and original
phase work/body debits, then summarizes complete declared reference/candidate
pairs in eight population blocks. Actual decision/learning energy and vigilance,
replay work, early deaths and total lived time remain explicit. Chosen waiting
is not physical inactivity. Zero-lived-step rates are undefined, not zero.
Pair opportunities must match; actual spending need not. Output is descriptive,
not causal energetic mediation, authenticated custody, or a scientific verdict.

Development-only integration tests check observer on/off equality of actual
receipts, body, actions, learned state and per-decision RNG. Exact results belong
to the implementation PR, not this status text. No Mind/runtime/physics/genome
change, default observer, new study life or validation/reserve exposure.
Study-specific case/genotype/intervention binding and prospective registration
remain required; the fixed design is not automatically executable.

## Stage 0: personally available revision endpoint

[Concrete R-depletion-v1 contract](STAGE0_REVISION.md) explicitly chooses the
existing depletion ecology as a first F0 revision stratum, not a new family.
`lab/stage0_revision.py` joins existing resource sidecars to paid life receipts:
positive uptake at a personally used source, first local absence, separately
paid processing, then positive uptake elsewhere. The clock never starts from
hidden stock. No exposure/failure/death and unknown latencies remain explicit;
reacquisition is neither survival nor proof of internal belief revision.

No new generator, observer hook, allocation or scientific cohort. Sidecar joins
are consistency checks, not original-chain authentication. Next: bind the
bounded Stage-1 candidate and these definitions to a prospective gate rather
than expand the observer framework. Stage 0 and #1026/#1054 remain open.

## Stage 1: paid information-value kernel, not a deployed cognitive candidate

[Kernel contract](STAGE1_INFORMATION_VALUE.md): a new computational primitive
compares one common continuation against observation-conditional re-planning
across two/three subjective forecasts in the existing distress-return units.
All branch scoring/projection and reduction work is funded before execution;
the total computation cost enters the predicted body. Indistinguishable
signals and body states cannot confer perfect hidden-outcome information.

No automatic prior, World input, action command, learned-state mutation or new
genome. The default reference does not call it; its curiosity/prudence remain
unchanged. The personal builder and opt-in local online prototype below are
implemented, not promoted. Budget consumption is not a physical settlement receipt;
the ordinary runtime must debit it. Zero perceived cost still requires payment.

Software tests include actual Mind projection/World debit and unchanged
reference-life behavior on a development fixture. Exact results belong to the
implementation PR. No new scientific study, held-out exposure, activation or
survival/generalization finding. #1060, #1061, #1026 and #1054 remain open.

## Stage 1: paid personal empirical hypotheses

`modules/personal_outcomes.py` records a bounded private history from applied
pre-decision/post-physics bodily outcomes, correcting only known own decision
cognition. Recording and constructing hypotheses consume real allowance; the
ordinary world owner must settle it. Exact-key recent experience precedes
same-action transfer to a new token. Unknown actions remain NO_PERSONAL_SUPPORT.
Two/three empirical hypotheses and their same-key persistence assumption feed
the unchanged kernel; body-only signals never expose sample identities.

These are fallible recent empirical hypotheses, not calibrated uncertainty,
true hidden effects or a new innate favorable prior. The default reference has
no extra store; the opt-in prototype below shares its episodic budget. The
original constructor software integration uses
fixed development fixtures with actual Mind decisions, World steps, new paid
recording and physical settlement. It is not a reference-cost-parity or survival
study. That constructor slice left existing executable source unchanged. The
subsequent local integration below changes runtime dispatch only by explicit
opt-in; genome, physics and historical evidence remain unchanged.

## Stage 1: local online information choice, not reference promotion

[Integrated local prototype](STAGE1_INFORMATION_VALUE.md): explicit run_life policy
`local_information_v1` connects personal outcome recording, fully funded
conditional forecasts and actually executed motor commands. Old additive
curiosity/relevance/prudence do not enter this score; original Competition and
motor control are reused. Default P1.3 behavior remains the reference.

An explicit stationary zero-delta ignorance prior replaces missing support
only in this prototype. It creates no positive resource gain but can be
optimistic about unknown decay. Episodic m_max is split between TD/replay and
personal effects, not enlarged. The complete batch has a common cost forecast;
unused Competition-cycle ceilings are predicted, never billed. Actual recording
is included once in the ordinary learning-phase debit. Policy identity enters
the manifest before birth; unsupported historical ablations fail before birth.

This changes the local planning repertoire and memory partition as well as
scoring. It is not the full spatial mechanism or a one-mechanism scientific gate.
Software checks include actual acquired-history use, a synthetic history-to-motor
contrast, observer/RNG parity, exact receipts and pinned previous-runner default
parity. Exact PASS/FAIL/NOT_RUN belongs to the implementation PR.

The first prospective development diagnostic remains adverse and immutable.
PR #1072 added phase receipts; #1073 removed per-key rescans; #1074 adds a
decision-local, owner/version-bound support index so later option constructions
pay explicit lookups without retraversing the same history. Forecast-only
compatibility work preserves the old common predicted body. The minimal
populated synthetic decision is now 1.3104 energy / 1.76 vigilance, with unique
rollouts the largest measured phase. **Stop exact-cost optimization here:** the
next informative step is a new source-locked development diagnostic, not another
observer or hidden budget heuristic. Full live ablations and the scientific
survival/revision gate remain open; Stage 0, #1026 and #1054 are not resolved.
No selection/validation/reserve exposure, activation or scientific GO.
