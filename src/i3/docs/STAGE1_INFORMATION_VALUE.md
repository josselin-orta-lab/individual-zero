# Stage 1: paid information components and opt-in local choice

Issue #1061; baseline `942b973faec73f1020505bd53b841691eb01c590`.
This connects the paid kernel and personal history below to online local choice,
not a new roadmap, adopted reference or completed Stage 1.
The [development plan](DEVELOPMENT_PLAN.md) and ADR-0016 remain authoritative.

## Implemented question

Can a personally acquired bodily consequence affect a subsequent **executed**
choice through prepaid conditional distress forecasts, without the additive
curiosity, relevance and prudence score? This is an integrated software falsifier.
It is not a survival/non-inferiority or revision-latency experiment.

`run_life(..., decision_policy="local_information_v1")` explicitly constructs
`modules/information_mind.py::InformationMind`. The default remains `reference`
and constructs the unchanged P1.3 Mind. The experimental policy, unknown prior
and episodic partition are bound in the manifest before birth. Other historical
learning/readout/score-ablation combinations are rejected before World creation.
No registry, engine entrypoint, physical law, genome schema or tariff changes.

## Paid information kernel

`modules/information_value.py::paid_information_value` takes exactly two or
three positive-probability SubjectiveOutcome branches with total mass one,
explicit signal classes, five-channel probe deltas, and a common continuation
set. Deltas are subjective net motor/metabolic/resource effects, excluding
this calculation's cognitive debit. They are not true World transition laws.

For branch b, continuation a and bodily return G(b,a), it computes:

```text
V_common   = max_a sum_b p(b) G(b,a)
V_informed = sum_o max_a sum_{b compatible with o} p(b) G(b,a)
information_value = V_informed - V_common
```

Observation o consists only of the declared signal and predicted directly
sensed body after the probe. Hidden sample identity cannot choose a continuation;
saturated bodily observations remain aliased. G uses the existing normalized
three-discount-horizon negative-distress return, then the existing projection
and learned residual. Death is absorbing. Outcomes are averaged, not maximized.
The diagnostic difference is not an extra bonus or Stage-2 value of computation:
the actual experimental score is the complete V_informed.

For B branches, A continuations and C projection chunks, the uncached kernel
has B*A matrix cells. With the decision-local exact-cell reuse below, let U be
the number of unique predicted first/second-body cells actually computed:

```text
cycles          = 1 + U + 1
simulated_steps = U*(2 + C)
memory_items    = B*7 + B*A*5
replays         = 0
```

The matrix description is still fully prepared, so memory_items continues to
scale with B*A; only duplicate cell projection work is reused.

A preparation block precedes drift lookup and the remaining-cost quote. Each
score, actual geometric projection and final reduction is prepaid. Terminal
hypotheses still execute the charged absorbing projection. Work must match the
quote on success; failed quotes retain only executed preparation, while later
exceptions retain only blocks already consumed and produce no partial score.
These are declared model blocks, not CPU instructions or host-energy estimates.

The default API and `paid_personal_information` retain their existing cost
semantics. The standalone `perceive_cost=False` diagnostic ignores only the
kernel's incremental cost, never prior construction/spending or real payment.
It cannot unlock unaffordable work and is not yet a full live-policy ablation.
The common-batch extension is described below; it is not a waived-cost economy.

## Personal-outcome constructor

`modules/personal_outcomes.py` keeps the same no-support and hypothesis
semantics. It now accepts an optional observer-only work receipt that records
existing setup, history-scan and branch-build spends without changing the
allowance or returned outcomes. PersonalOutcomes starts empty with explicitly
bounded capacity 1..512. Its
items contain only an action/internal-token key and five bodily deltas, not
positions, hidden stocks, source gains or exogenous schedules. `observe` requires
living pre-decision and post-physics/pre-learning bodies, actual decision work,
and a fresh allowance. It prepays one cycle plus 16 memory items, then records
the bodily delta with only that known own decision energy/vigilance debit added
back. This cannot undo clipping or identify intrinsic causal resource effects.
Caller binding is required; the public interface is not authenticated evidence.
An invalid/unfunded observation neither stores nor evicts a sample.

Construction takes the latest at most three exact-key effects; only absent
exact-key support permits the same-action personal backoff. There is no global
or cross-action transfer. Unsupported probes/continuations raise NoPersonalSupport
in the original class, with consumed scans retained and no later work charged.
Two/three samples have equal mass. One sample is duplicated at half mass only
for the kernel API, not independent evidence or measured uncertainty. Recent
adverse samples are not filtered; forgotten history is not reconstructed.

Repeating the same action/token shares its probe hypothesis. Other keys use
their own personal mean; their full uncertainty is not propagated. This is a
fallible local-persistence approximation, not a posterior or change detector.
All constructed signals are body_only. It grants no inventory or spatial facts.
With N stored items, A continuations, Q unique queried keys, B branches and
S returned support vectors, construction prepays:

```text
cycles       = 1 + Q + 1
memory_items = (2 + 3*A) + Q*(7*N + 2) + 5*S + B*(7 + 5*A)
```

`paid_personal_information` distinguishes `construction_work`, kernel `work`
and combined `total_work`, all on the same real allowance. The original tests
and their historical PR records remain applicable to their pinned source;
current full-checkout checks must run again. The opt-in subclass below supplies
its unknown semantics and inherited episodic partition without modifying this
original constructor or retroactively adding cost to old life receipts.

## Deliberately local scope

Candidates are primitive local rest, drink, collect, eat and adjacent movement
commands, constructed from the **paid personal map and inventory**, never World.
There is one probe step and one hypothetical continuation, followed by the
existing self-projection and learned residual. The old remote BFS macro-plans
are not scored by this prototype. It predicts no information about unseen cells.
The existing Competition and motor admissibility code are reused unchanged.
All plans are one-step, so there is no multi-step intention to preserve.

Hypothetical movement exposes no new map cells. Eating decrements carried
quantity; collecting adds exactly one item. After drinking or collection the
prototype conservatively assumes no leftover environmental stock at that site,
rather than injecting hidden quantities. A later actual capture can show more.
Continuations have structural first-person feasibility, not a guarantee about
future energy, stock or motor admission. They are never commands to World:
the next real decision processes a new capture and ordinary control runs again.

This restricted repertoire and memory partition differ from the reference.
A future survival difference would therefore not isolate information value.
Do not submit this local prototype as the planned one-mechanism Stage-1 gate.

## Explicit ignorance, not invented experience

The underlying PersonalOutcomes component still raises NoPersonalSupport.
Only this experimental subclass supplies an explicit stationary ignorance prior:
one zero-delta hypothesis, represented as two identical half-mass branches for
the kernel API. This is the same assumption for every unsupported action, with
no positive food/water effect, action preference or forced exploration command.
It is not stored as experience and does not inherit across births.

Stationarity is **not objectively neutral**: ignoring unknown decay can be
optimistic and can prefer an unknown action to a personally costly known one.
This is an explicit falsifiable modelling assumption, not a calibrated prior
or the algorithm prescribed by the supplied scenario. Do not tune it to rescue
poor development lives. Existing random tie-breaking resolves equal forecasts.
Personal exact-key or same-action samples replace it when acquired. Recent
samples remain fallible; this is neither a change detector nor a full posterior.

## Costs, comparison point and failure

Perception/control preparation, hypothetical map/inventory construction,
personal-history scans, branch construction, kernel rollouts and reductions
consume existing CognitiveBudget allowance before execution. All option
forecasts use the **same** predicted starting body after the complete quoted
batch plus the inherited Competition cycle ceiling. This avoids artificially
cheaper earlier options due to sequential scoring.

The kernel's optional `forecast_work` is a prediction ceiling, not a spend. It
must cover that call's actual work and be affordable from the original body;
it cannot be combined with the zero-perceived-cost diagnostic. Its default
behavior is unchanged. The local caller reconciles the sum of actual kernel
work with the complete evaluation quote before allowing Competition to run.
Competition then consumes only the cycles it really executes. Unused cycles
are not billed, refunded or fabricated. Thus the forecast can conservatively
overestimate Competition cost; it is not claimed to equal every realized bill.

A failed complete comparison returns no authorized command. All consumed work
is still settled once by the ordinary runtime, and passive physiology advances.
A computational error propagates instead of becoming a physical death or a
partial score. Physical death prohibits further decision or learning. Sleep
never retroactively finances an unaffordable comparison.

### Exact decision-local cell reuse after the adverse diagnostic

The first complete development diagnostic showed that exhaustive local scoring
can exhaust vigilance before the individual can continue acting. The first
response is implementation-level reuse, not a new budget policy: within one
decision only, two payoff cells with exactly the same predicted first and
second body under the same decision-local model state may share the already
computed scalar projection result.

The common forecast body remains the **old exhaustive batch ceiling**, including
the Competition ceiling. Therefore reuse cannot improve a score merely by
predicting that its implementation is cheaper. Only work actually executed is
charged. No cache crosses a decision boundary, no hidden World fact or branch
label enters the key, and a failed partial calculation still returns no command
and no refund.

This is deliberately narrower than Stage 2. It does not decide whether another
cycle is worth buying, change inherited ceilings, alter tariffs, or skip a
unique forecast. A later budget-allocation policy would be a separate mechanism
and require its own prospective comparison.

### Synthetic phase-cost measurement after exact reuse

PR #1072 adds observer-side phase receipts and a reducer that must reconcile
exactly to the already-declared decision work before converting work through
the current BodyLaws. It runs no study life and provides no Mind input.

On the deterministic 1x1 synthetic fixture used by the software test, with the
midpoint genome and three local options, the empty-history decision used 0.7872
energy and 1.72 vigilance in total. Repeated personal-history scans were already
the largest phase: 0.1836 energy / 0.45 vigilance, versus 0.04 / 0.07 for the
single unique projected cell after exact reuse.

With the candidate's personal half-memory filled to its midpoint capacity
(136 synthetic samples), total decision cost was 2.9536 energy / 2.06 vigilance.
History scans consumed 1.8972 energy / 0.45 vigilance (9 scan cycles and 8586
memory items), while eight unique projected cells consumed 0.32 energy / 0.56
vigilance. Thus on this software fixture, repeated scans dominate **energy**
as memory fills, while unique rollouts dominate **vigilance**. This is an
engineering scaling observation, not a survival result and not evidence that
the same ranking holds on larger maps with more options.

The next cost-only correction may therefore remove exact repeated history scans,
but must preserve returned support sets, unknown-query semantics, paid work
truth and the common forecast body. Skipping a unique query or choosing a
smaller cognitive budget would instead be policy-changing and belongs to a
separate prospective mechanism.

The old bonus terms are absent from the experimental score, not computed and
then added or discarded. Compatibility witness fields are zero and marked
`score_kind=local_expected_distress`; `uncertainty=None` is not a calibrated
zero-uncertainty estimate. The full existing Competition/resource observers
remain opt-in and provide no additional Mind input.

## Episodic memory and learning

The existing inherited rounded m_max is explicitly divided: floor(m_max/2)
recent personal effects and the remainder for ordinary TD/replay transitions.
Their combined retained count cannot exceed m_max. This is **not** a cap on all
map cells, effect statistics or other state. No extra gene or silent migration;
unused beta_u/lambda_r stay in the existing birth schema but do not score this
candidate. The fixed two-step local lookahead is not Stage-2 budget selection.

Ordinary learning reserves and settles its normal bill. When additionally
affordable, STORE_WORK is reserved in that same learning phase. After settlement,
the original PersonalOutcomes.observe executes with a checked suballowance
for that already funded block and the original pre-learning physical body.
There is no second World debit. It removes only the known decision-phase
cognitive charge from the lived delta, as in the original constructor.
No paid storage means no new personal record. No record is made after death.
The new personal-history digest is separate from the original learned-state
signature, so old meanings are not silently broadened.

## Verification and next intervention

`tests/i3/test_information_mind.py` exercises inventory/known-map restrictions,
empty birth, prior replacement, memory partition, insufficient budget, terminal
bodies, common forecast-cost semantics, real online history use, a synthetic
history-to-issued-motor falsifier, exact two-phase receipts, existing observer
parity including RNG, and default-reference parity against the previous pinned
runner at the same current source snapshot. It uses synthetic software fixtures
and existing stable development indices 0 and 1 only. A synthetic history
contrast is not acquired individuality or a scientific survival benefit.

Record exact local and full-checkout CI checks in the PR. Do not borrow a
prior SHA's success or turn short software trajectories into new scientific
populations. The original report, studies, allocations and P4 reserve are unchanged.

The bounded development diagnostic is complete and adverse. Exact decision-local
cell reuse is the first cost correction because it removes only duplicate work
while preserving the exhaustive forecast body and score semantics. Synthetic
phase accounting now shows repeated personal-history scans dominating energy
once memory is populated, while unique rollouts dominate vigilance on the
minimal fixture. The next bounded intervention is exact scan reuse, not a
policy-changing budget allocator. Spatial information remains deferred until
the paid comparison itself is sustainable.
Do not tune a rescue prior, rewrite Competition, or expand observers instead.
Full live ablations and the source/genotype/case/margin/multiplicity/stopping/
compute-locked survival and revision gate remain open. Stage 0, #1026 and #1054
are not closed by this slice.
