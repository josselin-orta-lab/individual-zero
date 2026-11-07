# Stage 1 Candidate-F cost versus policy: fresh 54/55 development falsifier after observer fix

Issue #1061. Source baseline before protocol:
`954ea5f312024fb902dd43a6845341adc3f88f0f` (merged PR #1140).

**PROSPECTIVE DEVELOPMENT DIAGNOSTIC ONLY. NOT A STAGE-1 SCIENTIFIC GATE.**

This protocol is frozen before any I3 development world at indices 54/55 is
opened. This PR contains no execution hook.

## Why this diagnostic exists

The frozen ADR-0015 omega gate is complete and rejected.

Validation survival:

- P1.3 reference: **82/240**;
- selected Candidate-F with inherited omega: **0/240**;
- same selected Candidate-F genomes with omega forced to zero: **0/240**.

Candidate cognition on realized trajectories was much more expensive than
P1.3, but omega=0 retained Candidate-F policy and also died universally.
Therefore that gate does not distinguish:

1. a physically unaffordable cognitive architecture;
2. harmful changed decisions;
3. both.

PRs #1137-#1140 implement a conservative causal falsifier. The new upper-cost
arm actually computes Candidate-F/omega cognition, physically pays it, then
lets plain P1.3 compute from the resulting lower body and grants motor authority
only to P1.3. Its total decision bill is therefore **larger**, not artificially
cost matched.

If that arm can survive a matched opportunity where ordinary Candidate-F dies,
then Candidate-F-style cognition cost is not universally sufficient to make
survival impossible. This still does not prove that policy is the sole or
dominant mediator.

## Fresh allocation frozen before exposure

P2's frozen development cohort spans indices 0..99, corresponding to world
seeds 2000..2099.

Known Stage-1 development history before this freeze:

- 44/45: local-information diagnostic;
- 46/47: cost-reduced local-information diagnostic;
- 48/49: opened once, then closed after observer engineering failure;
- 50/51: complete frontier-water diagnostic;
- 52/53: opened once, then closed after Stage-0 revision observer engineering failure; no causal verdict.

Repository collision searches before this freeze found no I3 study allocation
for development indices **54/55** or P2 world seeds **2054/2055**.

Use exactly:

- F0 ecologies: `stable`, `depletion`, `pulse`;
- development indices: **52, 53**;
- P2 world seeds: **2052, 2053**;
- current v4 G0 genome seeds: **901, 902**;
- horizon: **400**;
- three policy arms in exact order:
  1. `reference`;
  2. `genomic_omega_frontier_information_v1`;
  3. `candidate_f_shadow_upper_cost_reference_controller_v1`.

For zero-based family ordinal f, index ordinal w and genome ordinal g:

`life_seed = 7440000 + 1000*f + 10*w + g`.

All three arms in a block share family, world, genome, life seed and horizon.

Total if later executed: **12 matched opportunity blocks / 36 lives**, maximum
**14,400 physical steps**.

The two G0 genotypes and repeated F0 blocks are not independent evolutionary
populations. No inferential population claim is allowed.

No selection, validation or reserve condition is opened. The P4 reserve
1200000..1200199 remains sealed.

Machine-readable runner:

`python -m i3.lab.stage1_candidate_f_cost_vs_policy_diagnostic --plan`

Canonical plan SHA-256:

`e1c8bd89e9e6cfa921fb0332bf9376e44181f649d19c896e7f736e888c1845c4`.

## Arms

### Reference

Ordinary P1.3 policy and ordinary paid cognition.

### Candidate-F

`genomic_omega_frontier_information_v1`, the architecture rejected by the
frozen omega gate. This arm controls that the adverse mechanism remains adverse
on the new development opportunities; it is not retuned.

### Upper-cost P1.3-choice control

`candidate_f_shadow_upper_cost_reference_controller_v1`.

At every decision:

1. common shadow state is aligned to P1.3's actual lived history;
2. Candidate-F/omega shadow cognition is really executed;
3. that shadow work is physically included in the decision bill;
4. P1.3 then computes from the lower post-shadow body;
5. only P1.3 controls the motor action.

At learning:

1. ordinary P1.3 learning/replay purchase occurs;
2. Candidate-F-private branch storage is appended only if one extra
   `STORE_WORK` is physically affordable;
3. that private sample comes from the action P1.3 actually executed.

This is deliberately an **upper-cost** arm. It is not exact cost matching.
Candidate-F and the upper-cost arm can diverge in trajectories and therefore in
realized shadow work.

## Primary causal falsifier

For each matched block classify Candidate-F versus upper-cost as exactly one of:

- `UPPER_SURVIVES_CANDIDATE_DIES`;
- `CANDIDATE_SURVIVES_UPPER_DIES`;
- `BOTH_SURVIVE`;
- `BOTH_DIE`.

Frozen engineering continuation rule:

`at least one UPPER_SURVIVES_CANDIDATE_DIES block`.

Such a block is a strict **counterexample to universal cost sufficiency** on the
tested opportunities: a body can reach horizon while really paying Candidate-F
shadow cognition plus the extra P1.3 decision, provided P1.3 retains motor
authority.

It does **not** establish:

- exact energetic mediation;
- equal realized Candidate-F work across arms;
- policy as the sole cause;
- policy as the dominant population-level mediator;
- survival non-inferiority;
- Stage-1 acceptance;
- generalization.

If no strict counterexample appears, the result is inconclusive about cost
sufficiency because the control is deliberately overcharged.

## Required upper-cost custody at every decision

Every completed upper-cost life must authenticate every trace step:

- `total_work == candidate_shadow_work + reference_choice_work`;
- `total_work == funding_phases.decision.work`;
- motor authority exactly `P1.3_REFERENCE_ONLY`;
- `candidate_motor_authority == false`;
- settlement authority exactly
  `CUMULATIVE_V2_PHASE_START_BODY`;
- sequential settlement max absolute gap <= 1e-12;
- phase-start and final decision-debit bodies match the runtime receipt;
- shadow-private branch commit/retained totals match branch-memory custody.

Any mismatch is `ENGINEERING_FAILURE_NOT_A_DEATH`.

## Descriptive secondary observations

Retain for all arms:

- death/censoring and lived steps;
- physical death causes;
- actual paid energy/vigilance and per-lived-step descriptive rates;
- funding outcomes and first funding failure;
- physical inactivity separately from chosen wait and sleep;
- move/drink/eat/collect counts;
- positive water/food uptake;
- resource acquisition witnesses;
- branch-memory receipts where present;
- Candidate-F frontier/omega counters where present;
- Stage-0 revision receipt.

For upper-cost also retain:

- aggregate shadow decision work;
- aggregate reference decision work;
- total decision work;
- maximum sequential-settlement audit gap;
- number of decisions where the shadow motor preference differs from the actual
  P1.3 action;
- candidate-private branch commits.

Paired lived-step ordering upper vs Candidate-F and upper vs reference is
descriptive only.

## Source lock and original custody

The execution source must preserve the merged #1143 runtime/cognition/observer baseline exactly. #1143 changes only Stage-0 revision authentication for the explicit upper-cost policy: P1.3 processing status is checked against reference-choice work while total shadow+reference work remains fully authenticated and physically billed.

Before any world-generation import the runner rejects:

- wrong exact Git SHA;
- wrong protocol digest;
- dirty I3 source;
- any diff from baseline in `src/i3/modules`, `src/i3/runtime`,
  P2 ecology/world generation, Stage-0 energy/revision receipts or engine
  registry.

Protocol/runner/test/document changes are allowed before execution. Cognition,
runtime, physics and observers are not.

Every complete original life must be written as gzip before reduction.
A crash or custody mismatch is an engineering failure, never a death.

A later execution PR, if authorized after this protocol merges and exact-head
Python 3.11/3.12 checks pass, must:

1. add a temporary one-shot workflow only;
2. run on initial PR `opened`, first attempt, exact branch/base/repository;
3. run the full software matrix first;
4. archive every available original even on partial failure;
5. create an immutable evidence branch parented by exact execution source;
6. remove the write-capable hook before final integration.

No retry, replacement seed, favorable stopping, horizon extension, forced
resource, body/memory reset, clone or resurrection.

## Interpretation boundary

This diagnostic is intentionally narrower than another architecture search.
Candidate-F/omega remains rejected by the scientific gate regardless of this
development outcome.

A positive strict counterexample justifies the next causal analysis around
**which changed choices** create the collapse.

A null result leaves cost and policy unresolved and does not authorize tuning
omega, Stage-2 compute budgeting or reuse of exposed worlds.

P1.3 remains reference. I3 remains unregistered. Stage 2 remains blocked.
