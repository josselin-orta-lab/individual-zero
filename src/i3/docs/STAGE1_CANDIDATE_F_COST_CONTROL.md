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

The cumulative allowance then settles the reference work. The primitive checks
that its final body exactly matches sequential suballowance settlement.

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
