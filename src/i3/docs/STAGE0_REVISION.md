# Stage 0: R-depletion-v1 and a personally available revision clock

Continues [#1060](https://github.com/josselin-orta-lab/individual-zero/issues/1060)
and the [single plan](DEVELOPMENT_PLAN.md); depends on the
[funded-life adapter](STAGE0_DESIGN.md). Source baseline:
`43b262a2701d330b6725de66ff3e44a99ba0e693` (#1065).

**A concrete design definition and implemented observer-side endpoint, not a
preregistered study, adopted cognition, completed Stage 0 or scientific GO.**
No new world generator, observer hook, life runner or allocation is added.

## What comes from the source, and what is specified here

The [owner's scenario](GENERALIZATION_SCENARIO_SOURCE_2026-11-06.md) requires
survival non-inferiority and revision-latency superiority in a family R, but
does not define that family's generator or the latency clock. The following
is an explicit operational choice for a first bounded gate, NOT wording or a
result silently attributed to that report. Its F0 scope must stay visible.

**R-depletion-v1** reuses the existing P2 `depletion` mechanism as a revision
stratum within F0: a nearby finite non-replenishing water source, a distant
persistent source, and food near both. No new ecological-family transfer is
claimed. This is not F2 seasonality, hidden periodic change, or an added policy.
The historical G2e family R and its original endpoint/results remain untouched.

The executable generator is `p2_ecologies.world_for("depletion", cohort, index)`.
At the baseline, P2 Git blob is `f7e277da48309aef698b327f328e1f786e313ae2`;
its `worldgen.py` dependency is `7d6548662664afbab28627ea432977a9d658af79`.
That generator fixes geometry, source gains/stocks, food and initial bodies;
this definition changes none of them. Structural validity is not evidence that
every individual can survive. Do not search seeds until source loss occurs.

Use only the depletion rows already described in the Stage-0 design candidate:
selection indices `72 + 6*p + 2 + r`, validation `120 + 6*p + 2 + r`,
for populations p=0..7 and repeats r=0..1. These identifiers remain **unopened**.
No old G2e condition, enlarged P2 range or P4 reserve is used. Freeze source,
keys and collision checks in the eventual protocol before constructing them.
The other F0 strata remain necessary for a general survival comparison.

## Minimal observed sequence

`lab/stage0_revision.py::revision_receipt` consumes an already recorded
`run_life(..., keep_trace=True, observer_resource_acquisition=True)` result.
Prospective diagnostic studies also keep the existing full Competition witness;
this helper does not enable an observer, call a runner or send data to Mind.

1. Record a **positive bodily water uptake** at personal position q. A command
   alone or a visible but unused source is insufficient.
2. Start exposure at the first later local capture with no water at q. Unknown
   dry cells and hidden stock depletion do not start the clock.
3. Record separately the first such absence actually processed under the paid
   perception block. `NO_PROCESSING_BUDGET` means availability without processing.
   `NO_FUNDED_SCORE` and `NO_FUNDED_MOTOR` occur AFTER paid local perception in
   the current source; failed planning is not equivalent to absent perception.
4. End at the first positive water uptake at a different personal position.
   An old source refilling, a proposed drink, or a zero-uptake command is not
   alternative acquisition. Retain the first episode, not the fastest one.

The `here` channel is not subjected to the neighbor miss mechanism in the
current Mind. In this particular depletion ecology, only the individual's
own drinks reduce stock: the first dry local capture follows the last drink
at that source. There is no earlier hidden schedule or other consumer to infer.
The endpoint does NOT measure earliest evidence in arbitrary seasonal, neighbor-
only or multi-individual worlds. Those would need a separately specified measure.

The last successful drink still has a water-present pre-action capture. Do
not pretend the individual knew the source was empty during that same action.
A death on that action gives no subsequent exposure. No postmortem capture or
forced processing is manufactured.

## Time convention and outcomes

A trace row t records the action ending at t. A dry capture at decision e
therefore begins at boundary e-1. Uptake finishing at s has latency
` s - e + 1 ` physical action steps. Example: last drink at 1, first dry
capture at decision 2, alternative drink finishing at 4 gives **3 steps**.
The auxiliary paid-processing clock uses its own first decision in the same
formula. The availability clock retains the cost of delayed processing.

Return `NO_EXPOSURE` with reason `NO_PRIOR_POSITIVE_UPTAKE` or `NO_LOCAL_ABSENCE`,
`EXPOSED_NO_REACQUISITION`, or `REACQUIRED`. Separately retain terminal death or
horizon censoring, follow-up length and death causes. Zero-step deaths remain
records. Reacquisition on a fatal action does not imply survival. Missing or
inconsistent traces are errors, never a no-exposure outcome.

No exposure or no reacquisition has latency **None**, not zero, the full horizon,
or an invented success. Death before reacquisition is a competing terminal
outcome, not assumed independent censoring. A censored non-reacquisition only
reports the actually observed follow-up. A positive latency measures behavioral
resource reacquisition, NOT proof of revised internal beliefs or general agency.

## Upper-cost control processing semantics

The 52/53 cost-vs-policy diagnostic exposed one observer-boundary assumption
that was valid for all earlier one-mind policies but not for the explicit
upper-cost causal control.

In ordinary policies, public decision funding and total decision-phase work have
one cognitive owner. Therefore the historical consistency rule remains:

- `NO_PROCESSING_BUDGET` => total decision work is zero;
- any later funding status => the paid decision work contains at least the
  three-cycle P1.3 processing base.

The explicit
`candidate_f_shadow_upper_cost_reference_controller_v1` policy has two paid
computations in one physical decision phase:

1. Candidate-F shadow cognition;
2. the P1.3 motor-controller decision.

The public `funding` status is the status returned by the P1.3 motor
controller. A valid trace can therefore contain paid shadow work followed by
P1.3 `NO_PROCESSING_BUDGET`.

For this policy only, the revision join first authenticates the upper-cost
receipt:

- P1.3 is sole motor authority;
- Candidate-F has no motor authority;
- cumulative v2 settlement is authoritative;
- settlement audit gap <=1e-12;
- total decision work equals shadow work + reference-choice work and equals
  the physical phase work.

It then applies the historical processing-base rule to
`reference_choice_work`, not to total decision work.

This does **not** waive or hide shadow cognition. Shadow work remains in the
physical decision bill and Stage-0 energy receipt. It only prevents a paid
non-motor causal burden from being misclassified as P1.3 local processing.

The R-depletion endpoint remains unchanged: if P1.3 has
`NO_PROCESSING_BUDGET`, the event records `processing_paid=false`, even when
the shadow was paid earlier.

This distinction was frozen after the archived 52/53 failure. Those worlds are
closed and are not rerun to validate the repair. Regression coverage reproduces
the exact logical shape synthetically.

## Multi-phase Candidate-H / Candidate-I processing semantics

The 64/65 Candidate-I DEVELOPMENT stop exposed the same ownership issue inside
the native multi-phase candidates rather than in an external shadow controller.

A complete Candidate-H or Candidate-I decision can contain multiple physically
paid blocks. The public `funding` status is therefore not automatically the
status of **all** decision-phase cognition. The revision join now authenticates
the candidate's declared Stage-A / Stage-B / total receipt and applies the
processing predicate to the block that actually owns local processing for that
route.

The full physical bill is always preserved.

Frozen ownership:

- Candidate-H `P1.3_FINAL` / `CANDIDATE_F_FINAL`: Stage A is a detached
  relevance probe; Stage B is the one real final perception/decision, so Stage B
  owns R-depletion processing.
- Candidate-I `P1.3_BASE_FINAL`: Stage A is detached/rolled back; Stage B is
  the one real addend-free P1.3 decision, so Stage B owns processing.
- Candidate-I `INFORMATION_FINAL`: the real Stage-A perception/common score
  matrix is retained and Stage B only finalizes Competition/action control.
  Stage A therefore owns processing. A short Stage-B finalizer is not evidence
  of missing perception.
- Candidate-I `POST_CONTACT_CANDIDATE_H`: Candidate-H semantics apply and
  Stage B owns processing.

A valid sequential row may consequently contain nonzero total paid work followed
by a Stage-B `NO_PROCESSING_BUDGET`. In that case
`processing_paid=false` while earlier Stage-A cognition remains fully charged
in Stage-0 energy.

The repair is frozen and verified in
[the multi-phase reducer result](studies/stage1-multiphase-processing-reducer-repair/RESULTS.md).
64/65 remain closed and were not rerun to validate it.

## Consistency and limitations

First reuse `stage0_energy.energy_receipt` for the complete paid life and original
manifest/behavior/evidence chains. Then join resource sidecar rows to each
original action, option, personal/pre-action position, body, death and phase
work/payment. Recompute positive water uptake above passive decay from the
recorded physical body. No hidden source stock or location is used to start
or end exposure. Processing semantics are source-specific and must be rechecked
when a future cognitive candidate changes that boundary.

**The resource sidecar is not part of the original evidence hash.** These joins
catch inconsistent edits; they cannot authenticate an internally consistent
rewriting of capture values. Prospectively archive the whole original result,
including sidecars, and freeze its byte hash. Source/seed/genome/intervention
membership still needs study-specific binding. No authenticity or complete
physical-world replay is claimed by this helper.

## Gate design remains prospective

Keep fixed-horizon survival on ALL declared lives primary, with actual energy,
vigilance and lived time. Report exposure and reacquisition counts per arm and
population alongside latency distributions. Conditional successful-revision
latencies can select different survivors and exposures in each architecture;
a lower median among successes is not itself a causal or superiority result.
No exposure in either arm cannot pass a latency gate.

Before any selection/validation exposure, fix candidate/reference sources,
case/genome/intervention binding, survival margin, latency estimand including
no-exposure/death handling, independent units, multiplicity, sample-size
rationale and stopping/compute bounds. No p-value, non-inferiority verdict or
new study is produced here. The fixed Stage-0 design manifest is unchanged.

Tests cover synthetic positive/null/adverse event sequences, malformed joins,
and short existing **development** runtime fixtures (depletion indices 0,1,
24 steps), including actual paid-perception and observer on/off parity. Those
fixtures are not a new cohort or a generalization result.

Next: use these concrete definitions in the bounded Stage-1 candidate design
and prospective gate, not another general observer framework. Stage 0 remains
open for #1026 individuality, #1054 carried-food uncertainty, lineage controls
and the final study design. I1 active; I3 unregistered; P4 reserve sealed.
