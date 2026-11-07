# Stage 1 Candidate-F failure diagnosis: upper-cost reference-choice control

Issue #1061. Baseline:
`fd83f92cf35ae469a344d75e1a84a030b37d006d`.

**SOFTWARE FALSIFIER ONLY. NOT A RUNTIME POLICY. NO WORLD OR STUDY AUTHORIZATION.**

## Why this control exists

The complete frozen omega gate rejects the integrated Candidate-F architecture:

- P1.3 reference: 82/240 validation survivors;
- Candidate-F + inherited omega: 0/240;
- same selected candidate genomes with omega forced to zero: 0/240.

The omega-zero arm does not isolate physical cognition cost. It still executes
Candidate-F information scoring and lets that policy choose the motor action.

Candidate-F also consumes far more cognition on its realized trajectories:
about 2.23494 energy and 3.13911 vigilance per lived step versus 0.58475 and
0.71725 for P1.3. Those descriptive costs do not establish causal mediation
because behavior and bodily history differ.

The next question is therefore:

> Can P1.3 still choose coherently after paying a real Candidate-F decision
> computation first?

## First falsifier: deliberately conservative upper-cost control

The initial primitive is not advertised as exact cost matching.

For one aligned first-person state:

1. a distinct Candidate-F/omega mind executes a complete ordinary candidate
   decision computation;
2. its actually consumed work is immediately charged to the cumulative bodily
   allowance;
3. the same non-body first-person capture is presented to a plain P1.3 mind,
   but with body equal to the **post-candidate-cognition body**;
4. P1.3 executes and pays its ordinary decision computation;
5. only P1.3's action/parameter are returned.

The Candidate-F shadow action has zero motor authority.

Total work is therefore:

```text
candidate shadow decision work
+ P1.3 reference decision work
```

This is an **upper-cost** intervention. It pays more computation than the
Candidate-F policy alone because both calculations actually execute.

That asymmetry is useful as a first falsifier:

- if a future integrated upper-cost arm remains materially closer to P1.3
  survival than Candidate-F, physical cognition cost alone is insufficient and
  changed policy is strongly implicated;
- if the upper-cost arm also collapses, physical cost may be sufficient, but
  this control cannot quantify the contribution because it intentionally
  overcharges. A tighter shared-work control would then be required.

Do not call the latter result "cost mediation established".

## State alignment

Before either computation, the primitive fails closed unless reference and
candidate share the same:

- inherited common P1.3 parameters;
- effects statistics;
- personal map/history/visible cells/position;
- internal token mapping;
- TD values and replay buffer;
- previous action state;
- perception RNG state;
- budget-order RNG state;
- Competition accumulator and intention state.

Intentional architectural differences remain:

- P1.3 reference simulation is `reference/chunk_end`;
- Candidate-F uses `candidate_f/event_local_quadratic4`;
- Candidate-F owns its extra branch memory and omega machinery.

This slice is one-decision only. It does not yet solve how to maintain aligned
learned state over a full continuing life.

## Physical settlement

Each subcomputation runs on a CognitiveBudget starting from the actual body
available at that point.

Candidate work is settled before P1.3 begins. Therefore P1.3 receives the real
lower energy/vigilance state produced by the extra cognition.

The cumulative allowance then settles the reference work using the ordinary v2
CognitiveBudget rule: the complete phase bill is recomputed from the phase-start
body. A detached reference suballowance separately subtracts reference work from
the already debited post-shadow body.

Because cognition cost is linear in CognitiveWork, those bodies are
mathematically identical. Their floating-point evaluation order can differ by a
few machine ulps, so the primitive requires a maximum absolute channel gap
<=1e-12 rather than byte equality. The cumulative v2 allowance is authoritative
for the physical body and the sequential body/gap are retained as audit fields.

No unpaid evaluator or fabricated work vector is used.

## Explicit limits

This slice does not:

- add a runtime `decision_policy`;
- execute World;
- synchronize learning across multiple steps;
- claim exact cost matching;
- waive candidate cognition;
- reuse the Candidate-F action;
- alter P1.3 reference behavior when the primitive is not invoked;
- reopen exposed development 44..51 or selection/validation 72..167;
- touch P4 reserve;
- authorize Stage 2.

The next step, only if this primitive is software-valid, is to design the
smallest continuing-life controller with authentic learning/state custody.
No fresh development allocation should be opened before that controller has an
explicit falsifier and observer contract.


## Continuing-life state custody prerequisite

The one-decision upper-cost falsifier is not sufficient by itself for a life.
A Candidate-F shadow that keeps its own non-motor choices would accumulate a
fictional first-person history.

The next software-only custody layer therefore enforces this rule:

> **the shadow computes from the control individual's actual lived history, not
> from the actions the shadow wanted to execute.**

Before each future shadow decision,
`synchronize_candidate_shadow(reference, candidate)` deep-copies the common
P1.3 state retained by the actual reference controller:

- effects statistics;
- personal map/history/visible cells/position;
- token mapping;
- TD values and replay buffer;
- previous action state;
- Competition accumulators and intention;
- perception RNG and option-order RNG states.

The copy is experimental counterfactual apparatus, not cognition performed by
the individual, and is not billed. The **shadow decision itself remains fully
executed and paid** by the upper-cost primitive.

The alignment deliberately preserves Candidate-F-private state:

- inherited omega;
- paid personal branch memory and record count;
- experimental architecture/cost counters.

Mutable common structures are deep-copied. The shadow cannot mutate the real
P1.3 effects, map, values or replay buffer.

### Learning from the action that really happened

After P1.3's selected action is physically applied, the shadow may retain one
extra personal branch-memory sample only if:

1. ordinary P1.3 learning was funded;
2. an additional `STORE_WORK` block is physically affordable and prepaid;
3. the life is still alive.

The sample key comes from **P1.3's actual admitted action**, never the shadow
candidate action.

P1.3 sees the body after shadow cognition. Therefore its stored `last.before`
already excludes the earlier shadow debit. The branch sample removes only the
P1.3 decision work from the later post-physics delta. This recovers the
personally lived action consequence without double-correcting shadow cognition.

The common learned model is not recomputed a second time for the shadow. At the
next decision it is copied from the reference controller again. The shadow's
extra branch memory is the only separately retained learned component required
by Candidate-F information scoring.

This yields a conservative continuing-life cost shape:

```text
decision:
    paid Candidate-F shadow computation
  + paid P1.3 decision computation

learning:
    ordinary paid P1.3 learning
  + paid Candidate-F branch STORE_WORK when affordable
```

Candidate-F therefore receives no free private memory, while its non-motor
choice cannot create a fake action/outcome history.

This is still software custody, not a runtime policy and not a scientific life.
The next slice must compose this custody with the one-decision controller and
prove multi-step P1.3 action parity before any fresh allocation.
