# I3 development-agent instructions

These instructions govern repository work, never the individual's mind.
Read the root instructions, then [current status](docs/STATUS.md) and the
[single development plan](docs/DEVELOPMENT_PLAN.md). Inspect live HEAD, relevant
open issues/PRs and checks on the exact SHA before editing. The current
reference is **P1.3 on funded v2**; older descriptions of P1.1 as current or
P3 as not executed are historical, not the present source/evidence state.

## Approved direction and next work

[ADR-0016](../../docs/decisions/ADR-0016-i3-generalization-without-imposed-rules.md)
integrates the owner's 6 November 2026 scenario, whose
[original text](docs/GENERALIZATION_SCENARIO_SOURCE_2026-11-06.md) is preserved.
Stage 0 #1060 remains open, but the immediate bounded implementation is Stage 1
#1061 on the **reference-preserving path**. The local_information_v1 prototype
is retired as a gate candidate after the frozen 44-47 development diagnostics.
PRs #1076-#1081 provide the reference-preserving branch memory,
storage-only cost control, paid replanning, conservative frontier belief and
anti-oracle branch-specific continuation substrate. The first integrated
`reference_frontier_information_v1` water probe completed fresh 50/51:
information becomes positive in 7/12 lives, always exactly one step after first
positive water uptake, but survival is 2/12 versus 6/12 storage-only. Five lives
never bootstrap water information and all die. Do not tune or rerun 44-51.

PRs #1088-#1091 now isolate the generic bootstrap ingredients without opening a
world: zero-mean stake-projected unsupported effects; exact branch-local reuse
after an observed effect; nested one-trial value separating epistemic value
from overall trial advantage; and an action-neutral first-person frontier
modality prior. A synthetic test proves that a strictly zero-mean unsupported
effect can have positive information value when the observed body changes the
best continuation.

Subsequent software results now narrow the blocker further. #1099 shows zero
information when no future matching opportunity is represented. #1101 restores
exact P1.3 explorer semantics and selects an epistemic water trial in 0/80
states. #1102 proves carried-food information can exist; #1104 improves meal
rank in 9/27 rich competing-need states; #1105 then places every alternative
under one common cognition-depleted forecast body: 27/27 are funded, information
is positive in 9/27 and raises the meal score in 14/27, but the raw winner
changes in **0/27**.

**DRIFT DETECTED:** stop local water/food score patches and do not jump to Stage
2. The next code slice may test only one minimal generic first-person
future-opportunity representation needed by Stage 1. It must be empty at birth,
paid, renaming invariant, bounded to 2-3 outcome branches and unable to read
hidden stock, source persistence, schedules or world identity. This is not
authorization to implement full Stage 3 change detection/latent causes/
factorization.

Reuse #1026 for individuality and #1054 for the historical P5d uncertainty.
Stages 3-6 otherwise remain deferred and gated.

Do not prioritize a Competition rewrite: P5e did not establish generally
broken Competition, and its masked arm never carried food. Missing exposure
is NOT_OBSERVED. Do not force collection/eating, cherry-pick seeds or substitute
a normal-arm result for the missing masked-arm observation.

Every proposed cognitive mechanism must be evaluated through predicted
cumulative bodily distress, including real energy/vigilance costs. No rescue
bonus, world-specific policy, scripted behavior or reward shaping. Information
value and value of computation are hypotheses to test, not already adopted
code or outcomes to guarantee. One mechanism per gate; retain null/adverse
results and the prior reference after a failed gate.

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
