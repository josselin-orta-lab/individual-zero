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

## Paid plan-level replanning kernel

`modules/plan_information.py` now supplies the next software-only prerequisite.

It accepts exactly two or three caller-supplied subjective probe outcomes and an
explicit set of existing P1.3 continuation plans. Every branch/continuation cell
is executed through `Mind.simulate`; no branch is selected by its hidden
identity. Conditional replanning can use only the declared observable signal
plus the predicted directly sensed body after the probe.

The kernel quotes a conservative complete-matrix work ceiling before scoring.
Its common forecast body includes that full ceiling. Every cell is then actually
executed unless the subjective probe already predicts physical death, which is
absorbing. Favorable early death/short plans may reduce actual work but cannot
make the forecast body cheaper. There is no early stopping or Stage-2 compute
choice.

This closes the **replanning arithmetic** gap without closing the **outcome
generation** gap. In particular the kernel does not generate an exploration
branch, edit a map, reveal an unseen cell or read World.

## Unsupported frontier outcomes: conservative personal belief

`modules/unknown_outcomes.py` now freezes the unknown-outcome rule before any
live Stage-1 policy.

It reuses the **existing P1.3 frontier resource base rate exactly**:

```text
p_resource = (personally seen resource-bearing cells + 1)
             / (personally seen passable cells + 2)
```

This is the same Laplace/Beta(1,1) structural prior already used by P1.3
curiosity. No new genome field, source density, world family constant or
development-fitted probability is introduced.

The new rule deliberately separates **resource presence** from **actionable
consequence**.

Conditional water-versus-token modality weights come only from the
individual's personally perceived map. A previously seen cell containing both
modalities contributes one incidence to each. The split is frequency-based,
not weighted by current thirst, hunger, utility or survival outcome.

Resource mass becomes actionable only if the individual has both:

1. personally learned a positive bodily effect for that generic modality
   (`boire -> water`, or at least one `manger:<internal token> -> food`);
2. retained paid recent empirical branches for that action class in the fixed
   18-record branch memory.

The resulting frontier belief has at most three observation classes:

- `NO_ACTIONABLE_PERSONAL_MODEL`;
- `ACTIONABLE_WATER`, if personally supported;
- `ACTIONABLE_FOOD_TOKEN`, if personally supported.

Any resource probability assigned to a modality without personal positive
effect evidence or paid branch support is folded into
`NO_ACTIONABLE_PERSONAL_MODEL`. It is **not** represented as zero bodily
effect, an average hidden resource gain, a favorable synthetic branch or an
oracle observation.

### Newborn semantics

At birth, before personal resource-effect experience, the structural resource
base rate is still 0.5 when no cell has been seen. But there is no actionable
resource-effect branch. The frontier model therefore reports
`NO_ACTIONABLE_PERSONAL_MODEL`.

This is intentionally conservative. It may fail to bootstrap exploration. Such
a failure is an admissible Stage-1 result and must not be repaired by choosing
a favorable prior from the already exposed 44-47 development worlds.

### Paid work and invariance

The personal map/effect scan is explicitly paid. Empirical branch retrieval is
also paid through the existing decision-local support index; missing support is
a paid negative result. No World object, hidden stock, future schedule or token
truth is read.

Food support uses same-action empirical fallback rather than any particular
external token identity, so renaming internal token labels changes no
probability or bodily-effect arithmetic. Token proliferation cannot increase
the 18-record branch-memory capacity.

This closes the **unsupported-outcome semantics** gap without yet creating a
live `reference_information_v1` policy.

## Observable revealed continuations

The next arithmetic gap is now implemented in
`modules/plan_information.py::paid_revealed_plan_information_value`.

The uninformed comparator receives only **common continuations**, meaning plans
that exist before the probe observation. Each subjective branch may additionally
declare plans that become available only after its observable result.

For example, an `ACTIONABLE_WATER` branch may expose a generic P1.3 simulation
plan consisting of one movement step followed by `boire`. The simulation plan
does not encode which adjacent direction contains the source; P1.3 action-effect
simulation already treats movement through its generic learned movement effect.
No hidden coordinate is therefore needed for value arithmetic.

Likewise an `ACTIONABLE_FOOD_TOKEN` branch may expose movement, collection and
eating using an **observed-token placeholder only inside that observable
branch**. The token cannot exist in the common pre-observation plan set.

The kernel enforces the anti-oracle condition directly: if two subjective
outcomes collapse to the same observable pair of signal and predicted body,
they must expose identical continuation names **and identical plan bodies**.
Different hidden outcomes may not silently grant different action sets.

The informed value can choose among common plus revealed plans for each
observable group. The uninformed value can choose only among common plans.
Every available branch/plan cell is actually prepaid and executed under one
conservative complete-matrix forecast ceiling. There is no favorable early
stop, no branch-max shortcut and no Stage-2 compute-selection rule.

This closes branch-specific **plan availability arithmetic**, but still does
not bind the frontier prior to a live P1.3 decision loop. The remaining bounded
integration is now mechanical but scientifically important:

1. convert a particular existing `explorer:*` option into its travel/probe
   consequence without changing its first motor command;
2. obtain the paid #1080 frontier belief from the same personal state;
3. construct only signal-permitted revealed continuations;
4. score information in place of additive curiosity/relevance/prudence while
   preserving the rest of P1.3's option repertoire, Competition and control;
5. use the #1077 storage-only arm as the physical memory-cost control.

That live candidate must still be development-only until its full cost ceiling,
no-support path, frozen-projection ablation and source/case locks are frozen.

Stage 2 remains separate and blocked: it asks how much unique computation to
buy, not how to invent outcomes the individual has never represented.
