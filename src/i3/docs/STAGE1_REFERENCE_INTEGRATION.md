# Stage 1 reference-repertoire integration: empirical branch-memory substrate

Issue #1061. Baseline before this slice:
`14b5f588ecfa54f15032e6462797a7bf9be73363` (PR #1075).

**SOFTWARE SUBSTRATE ONLY. NOT A DECISION POLICY. NO STUDY AUTHORIZATION.**

## Why this slice exists

The cost-reduced local prototype answered its engineering question but cannot be
used as the Stage-1 gate candidate. It changes local repertoire, memory
partition and ignorance assumptions as well as scoring. The fresh 46/47 result
shows many fully funded deaths and no positive contingent information value.

The next candidate must preserve P1.3's existing first-person spatial
repertoire, map/history, effect means, TD values, replay buffer, Competition and
Action Control.

A source audit found a narrower prerequisite. P1.3's `EffectsModel` retains an
effective count and running mean, not a distribution of lived effects. Its TD
replay buffer retains body-before/body-after/death but not the action key.
Therefore the scenario's two or three empirical outcome branches cannot be
honestly reconstructed from existing retained state.

Inventing hidden variance, importing World effects or creating a favorable
unknown prior would answer a different question.

## Bounded recent-effect ring

`modules/reference_branches.py::ReferenceBranchMemory` is an opt-in empty-at-
birth store built on the already tested personal-outcome custody rules.

Its total capacity is fixed:

```text
WINDOW = 3
primitive action classes = 6
global capacity = 18 records
```

A record contains only an internal action/token key and five personally lived
bodily deltas. Token proliferation cannot increase capacity. Oldest records
evict globally.

Exact-key latest <=3 support precedes latest <=3 same-action support. No global
cross-action fallback exists. Unsupported keys remain `NO_PERSONAL_SUPPORT`;
there is no stationary zero-delta prior in this reference-preserving path.

The ring is not inherited. It contains no position, hidden stock, world name,
future schedule, source gain or action preference.

## Paid storage and read

Storage reuses the existing `STORE_WORK` contract and the existing correction
for the individual's own already-paid decision debit.

A direct branch read over N retained records costs:

```text
cycles = 1
memory_items = 7*N + 2
```

Within one future decision, an ephemeral owner/version-bound support index may
reuse that already-paid scan; each later key lookup still costs one cycle plus
two memory items. Any new stored effect invalidates the index before new read
work is spent.

These are model-work units under the existing v2 tariff, not CPU instructions.

## What is deliberately unchanged

This slice does **not**:

- instantiate the ring inside P1.3;
- split, shrink or reinterpret `m_max`;
- change the TD replay buffer or EffectsModel;
- change options, BFS, source beliefs, explorer plans or perception;
- change beta_u/lambda_r scoring;
- add a runtime decision-policy name;
- run a World or expose a development/selection/validation/reserve condition.

Thus P1.3 remains byte-behaviorally on its existing path.

## Next bounded integration

The first of those controls is now implemented as the explicit opt-in
`reference_branch_memory_v1` policy. Its `decide` path delegates unchanged to
P1.3: same options, shuffle/RNG, simulations, curiosity/prudence score,
Competition and Action Control.

Its learning phase first computes the exact P1.3 base/replay purchase on a
detached allowance. The real allowance pays that identical reference work and
replay count. Only then, if an additional `STORE_WORK` block is physically
affordable, one lived effect is retained in the 18-record ring. Storage can
therefore change later physiology, as a real cost must, but it cannot steal a
reference replay or alter the decision that preceded its payment. If the extra
store is unaffordable, normal P1.3 learning still proceeds and no branch is
fabricated.

This storage-only arm is the cost control for the future information candidate.
The information arm must use the same storage rule and cost, while replacing
only the additive curiosity/relevance/prudence path with prepaid two/three-
branch information scoring.

That future comparison remains development-only until branch/replanning
semantics are frozen. It prevents attributing the physical cost of the new
empirical branch memory to information use itself.

The hard next design question is plan-level replanning, especially explorer
observations. Do not solve it by injecting unseen cells or a hidden resource
oracle. Any spatial observation branch must be generated from explicit personal
beliefs already available to the individual.

Stage 2 remains separate and blocked: it asks how much unique computation to
buy, not how to construct the Stage-1 subjective branches.
