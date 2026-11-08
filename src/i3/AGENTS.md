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

#1156 now completes that separation: the bounded software gate for Candidate-G
personal recurrence + Candidate-F projection **without genomic omega** passes
(`PERSONAL_RECURRENCE_CANDIDATE_G_INTEGRATION_PASS`). Persistent mode remains
P1.3 `reference/chunk_end`; the canonical projector is decision-local and only
enters when a paid personal information path exists.

**Next work is already frozen, not yet executed:** follow
[the 56/57 DEVELOPMENT protocol](docs/studies/stage1-candidate-g-development-56-57/PROTOCOL.md).
Do not alter its arms, seeds, horizon or continuation rules after exposure. Do
not open 56/57 from an ordinary development PR: they require a separately
reviewed one-shot transport after exact-head Python 3.11/3.12 checks. The pilot
tests activation plus physical affordability against P1.3 and rejected
Candidate-F; survival is descriptive only. No selection, validation, reserve,
reference adoption or Stage 2.

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
