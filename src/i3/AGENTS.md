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

**Current intervention:** isolate the architecture-level failure before inventing
another cognition mechanism. The smallest useful control is:

> P1.3 chooses with its ordinary reference policy while the Candidate-F
> information computation is still actually performed and physically paid.

This is a **cost-only reference-choice control**. It must not waive charges,
reuse the candidate score, secretly choose the candidate action, or bill
unperformed fictional work. The candidate computation must be real and its
receipts authentic; only motor choice remains P1.3.

The existing `omega=0` arm is not a cost-only control. It retains Candidate-F
information scoring and changed decisions, so its universal mortality cannot
separate cognition cost from policy effect.

Before any life:

1. define the exact point at which both reference choice and candidate work are
   computed from the same first-person pre-decision state;
2. define how physically paid candidate work changes the body before the
   reference command is admitted, without recomputing a hidden cheaper choice;
3. prove observer/RNG/map/learning custody and no duplicate motor authority;
4. demonstrate the default reference remains exact when the control is off;
5. freeze a small **fresh development-only** allocation if software falsifiers
   pass.

Do not reopen selection/validation 72..167, tune omega, change G1-G6, or launch
Stage 2. Do not rewrite Competition or force survival actions to repair the
negative gate.

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
