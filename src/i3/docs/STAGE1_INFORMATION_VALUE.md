# Stage 1: paid information-value kernel, not yet a live policy

Issue [#1061](https://github.com/josselin-orta-lab/individual-zero/issues/1061),
following the Stage-0 [design](STAGE0_DESIGN.md) and [revision endpoint](STAGE0_REVISION.md).
Baseline: `82128766d5a7fdb377f1efa3b59f4bac1b2f48a5`.
The [single development plan](DEVELOPMENT_PLAN.md) remains authoritative.

Implemented: `modules/information_value.py::paid_information_value`, a bounded
computational primitive using the existing I3 distress, self-projection and
learned residual. It is **not called by Mind.decide or run_life**. P1.3 remains
the reference, including its existing curiosity/prudence terms. No new genome,
world, tariff, observer, selection runner or default behavior is introduced.
This is not a completed Stage 1, experiment registration or scientific GO.

## Source requirement versus this implementation choice

The owner's scenario asks for two or three paid subjective outcome branches,
re-planning, and information value in predicted cumulative bodily distress,
replacing rather than adding to curiosity and prudence. It does not specify a
prior, observation model, numerical quadrature or an online integration API.
The finite-outcome, one-probe/one-continuation kernel below is an explicit
implementation choice, not a definition attributed to the supplied report.

Each `SubjectiveOutcome` has a positive probability, a declared signal class,
a predicted five-channel change from the probe, and predicted changes for the
same set of continuation identifiers. There must be exactly two or three
branches, with probabilities summing to one. No hidden renormalization, omitted
probability mass, zero-probability branch or automatic optimistic prior.
Deltas are predicted net physical/motor/metabolic changes over each of the two
steps, excluding this kernel's separately accounted cognitive debit. They are
not commands or true World laws. Their provenance is the caller's obligation.

**Unknown-outcome boundary:** the current EffectsModel stores means and an
uncertainty proxy, not a calibrated multi-outcome predictive distribution.
This kernel does not pretend that those means already provide branch priors.
An absent distribution fails explicitly. The paid personal constructor below
now supplies a bounded empirical approximation with explicit unknown semantics.
It is not a calibrated posterior or a complete newborn policy. Synthetic
forecast vectors in tests are not acquired experiences or scientific results.

## Conditional re-planning without a hidden-outcome oracle

For branch b, probability p(b), continuation a, and predicted return G(b,a):

```text
V_common   = max_a sum_b p(b) G(b,a)
V_informed = sum_o max_a sum_{b compatible with o} p(b) G(b,a)
information_value = V_informed - V_common
```

An observation class o combines the declared signal with the predicted body
immediately after the probe, which current I3 senses directly. The hidden
branch index itself never selects a continuation. Indistinguishable signals
and equal sensed bodies share a conditional expectation. They cannot receive
perfect-information value by selecting separately for each hidden outcome.
Identical best continuations also give no information advantage.

G uses the existing normalized three-horizon negative-distress return: the
probe step, the continuation step, then Mind.project and its learned residual.
All channels matter through the individual's existing distress function. Risk
is averaged over bodily outcomes, not encoded as a separate prudence penalty.
A predicted vital-channel death is absorbing even if a subsequent forecast
would restore that channel. No maximization over the outcome distribution.
The returned ties are not resolved by a behavioral rule or a random draw.

`informed_value` already includes physical consequences and the calculation
cost. `information_value` is the within-matrix diagnostic increment, NOT an
extra score bonus and NOT net value versus skipping computation. Both sides
share the same computation and paid matrix. A future candidate must replace
its old score path with a complete compatible expected return, never add this
increment to beta_u/relevance/prudence. This is not Stage-2 metareasoning.

## Actual advance funding and failure semantics

Use the existing CognitiveBudget and unchanged v2 rates. With B branches,
A continuations and C existing projection chunks, the added declared work is:

```text
cycles          = 1 preparation + B*A score blocks + 1 expectation/replan block
simulated_steps = B*A*(2 explicit predicted steps + C projection chunks)
memory_items    = B*7 + B*A*5  (forecast vectors and signal/probability entries)
replays         = 0
```

These are explicit model blocks, not a measurement of CPU instructions or host
energy. The preparation block also reads the current personal drift. After it
is paid and executed, the complete remaining bill is quoted without withdrawing
it. All forecasts start from the body after that quoted full debit, avoiding
cheaper earlier branches. Every score block, projection and final reduction
then consumes its actual allowance **before** execution. On success, actual
work and remaining body must equal the quote. Terminal hypothetical branches
still execute the charged absorbing projection; no fake skipped rollout bill.

If preparation cannot be funded, no model read/projection executes. If the
full quote is unaffordable, only executed preparation remains charged; no
partial branch score is returned. An exception midway propagates, preserves
already consumed work and does not charge later computations. Callers must
retain and settle this work, not catch the error and discard the bill.
Actual physical death rejects computation before any allowance is spent.

The allowance is **not** proof that World settled a bill. The runtime remains
responsible for its ordinary strict debit; integration tests explicitly settle
it with World.pay_cognition. No hidden motor authority is granted by the result.

`perceive_cost=False` is an explicit zero-perceived-INCREMENTAL-cost diagnostic:
the prediction ignores this call's debit, but all actual work remains charged,
and earlier cognitive spending is still included. It cannot unlock an
unaffordable call. This is not waived physical charges, not the funded default,
and not yet the report's full live ablation. No frozen-projection survival
experiment is implemented or claimed here.

## Verification and immediate handoff

`tests/i3/test_information_value.py` covers informative/uninformative signals,
observable body changes, shared best continuations, averaging three outcomes,
prepaid work, cost-blind diagnostics, prior spending, renaming/order invariance,
invalid priors, absorbing death, failed budgets, interrupted projections and
rejection of a projection that does not consume its declared allowance.

Two full-checkout tests connect to actual Mind projection and World debit,
check unchanged learned/RNG state, and compare the ordinary reference life
before/after an independent kernel call on existing development fixture 0.
These are software tests, not a new scientific cohort or survival comparison.
Exact PASS/FAIL/NOT_RUN records belong to the PR and its checked SHA.

The personal constructor below completes the next computational connection.
Next: connect it to a separately selected experimental score path, removing
curiosity/relevance/prudence there. Keep the reference unchanged until the
prospective survival/revision gate. Before exposure, freeze sources, priors,
genotype/case binding, margins, multiplicity, stopping and compute rules.
Stage 0, #1026 and #1054 remain open. I1 active; I3 unregistered; P4 reserve
sealed; no selection/validation worlds opened by this implementation.

## Personal-outcome constructor

Added after #1067, baseline `a700015d3fe81ad01a102a06390539c034f9025d`.
`modules/personal_outcomes.py` adds `PersonalOutcomes` and
`paid_personal_information`. This is an explicit modelling choice, not a prior
or algorithm specified by the owner's report. Existing executable sources,
including EffectsModel, Mind, run_life and the information kernel, are unchanged.
The new path is executable through its API but is not called by ordinary lives.

### Personal evidence and cognitive debits

A new history starts empty, with an explicitly supplied capacity of 1..512.
The future candidate must bind it to inherited memory capacity and account for
its storage jointly with existing memory; this slice does not silently allocate
another free lifetime memory. Each stored item has only an action/internal-token
key and five bodily deltas. No location, stock, source gain, scheduled event or
hidden token effect is accepted. Non-token actions use a None token identifier.

`observe(key, before, decision_work, budget)` requires a living pre-decision
body and a fresh post-physics/pre-learning CognitiveBudget. The caller must
supply its actually applied key and actually settled decision work. The new
learning block costs one cycle and 16 memory items before it executes. The
recorded delta is post-physics minus pre-decision body, adding back only the
known energy/vigilance debit of that decision. Motor/metabolic/resource changes
remain in the observed delta. The new history update's own debit occurs after
this snapshot, so is not subtracted and re-added as a fictional old effect.

This adjustment does not undo saturation, recover true unclipped gains, remove
context dependence, or identify intrinsic causal effects. A fatal outcome is
not learned after death. The inputs are a first-person interface, not an
authenticated receipt: actual runtime binding is required. An invalid or
unfunded storage operation changes no memory and evicts no old sample.

### Explicit finite empirical approximation

A query scans the bounded chronological history after paying for that scan.
Use the latest at most three exact-key samples; only when there are none, use
the latest at most three same-action samples from other personally experienced
tokens. There is no cross-action/global fallback. Having collected a token does
not create knowledge of its ingestion consequences. An unsupported probe or
continuation raises `NoPersonalSupport` after the scans actually executed, with
no partial score, fabricated positive effect, or silent zero-valued estimate.
This deliberately does not solve initial action choice for an ignorant newborn.

Two or three samples have equal mass. Adverse samples in that recent window
are retained without need/sign-based filtering. This is an explicit short
empirical window, not a claim to preserve the entire lifetime distribution.
One sample is represented by two identical half-mass branches to satisfy the
existing kernel API; these are not independent observations or evidence of
measured uncertainty. Forgotten experiences cannot be recovered by the query.

For the probe's same action/token continuation, the branch effect is assumed
locally persistent across the two steps. Different keys use their own personal
empirical mean, including when both unknown tokens use the same backoff pool.
This is an uncalibrated, fallible correlation assumption, not change detection,
a posterior update, or a guarantee of stationarity. Context and body clipping
can invalidate it. Other continuations' mean predictions do not propagate their
full outcome uncertainty; the target probe alone supplies this small ensemble.

All branches use signal `body_only`, never a donor token or sample index. The
unchanged kernel can condition only on the predicted directly sensed body.
Clipping two distinct effects into the same bodily observation cannot reveal
which sample was used. The caller still must prove the proposed continuations
are first-person admissible: a repeated meal needs remaining inventory; a route
needs reachable known geometry. No action is commanded by the constructor.
This does not yet model the value of discovering unseen spatial resources.

### Complete paid connection

Construction pays a preparation block, then one complete bounded scan per
unique queried key, then means/matrix construction. Each block is charged before
execution. Missing support charges no later scan or unexecuted matrix. With
N stored items, A continuation identifiers, Q unique keys, B outcome branches,
and S returned support vectors across keys, successful construction costs:

```text
cycles       = 1 + Q + 1
memory_items = (2 + 3*A) + Q*(7*N + 2) + 5*S + B*(7 + 5*A)
```

`paid_personal_information` passes the constructed hypotheses to the unchanged
kernel with the same allowance. Its existing `work` remains kernel work;
`construction_work` and `total_work` expose the additional and combined work.
Both enter ordinary forecasts. `perceive_cost=False` still ignores only the
kernel's incremental cost; construction remains prior spending and is included.
This is not a zero-perceived-total-cost live ablation. All actual charges remain
payable, including consumed work when construction or the kernel fails.

`tests/i3/test_personal_outcomes.py` checks unknowns, exact/same-action fallback,
negative outcomes, bounded forgetting, birth separation, known-debit correction,
failed budgets, body aliases, renaming, and combined costs. Two real integration
tests exercise fixed existing stable development indices 0 and 1: actual Mind
decisions, World steps, paid personal recording, normal paid outcome learning,
then kernel computation and physical settlement. The additional memory work is
actually executed and charged, not post-hoc attached to an old receipt. This
software harness is not a reference-cost-parity study or a new scientific cohort.
An unchanged run_life test forbids implicit calls into this new component.

Next is integrated experimental choice, not another constructor or observer:
explicit newborn ignorance/bootstrapping, shared memory and paid accounting,
admissible continuations, and replacement rather than stacking of the old
score. Full live ablations and the prospectively locked survival/revision gate
remain unimplemented. Stage 0 and #1061/#1026/#1054 remain open; no activation,
held-out exposure or scientific benefit is inferred from software tests.
