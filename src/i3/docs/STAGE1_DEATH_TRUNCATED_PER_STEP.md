# Stage 1 projection: exact per-step truncation at predicted death

Issue #1061. Baseline:
`f2a541b2783261a02e65511ddfbb8a9aab070c57` (#1152).

**FROZEN BEFORE IMPLEMENTATION. SOFTWARE ONLY.**

No World, no life, no study index, no runtime projection mode, no reference
adoption. P1.3 remains the reference.

## Motivation

#1149 showed that the 255-unit per-step projection makes Candidate-G
decision-relevant in 32/80 frozen states, but charges a mean 1288 simulated
steps per state.

#1151 showed exact separability. #1152 then showed that materializing complete
exact prefix traces is a bad physical trade: only 7.6% of trace accesses hit,
while the cache writes millions of paid memory items.

Before adding another representation, test the simplest exact optimization
already implied by irreversible mortality.

The current diagnostic per-step mode sets `proj_chunks = (1,) * 255` and
`Mind.project` prepays all 255 projection units before the loop. After the
first predicted vital zero, however, the body is frozen and reward is the
absorbing `-d_max`; no later bodily distress evaluation occurs.

Question: can we stop computation exactly there and sum the remaining absorbing
tail analytically?

## Candidate: `death_truncated_per_step_v1`

Laboratory-only subclass of the reference Mind.

It keeps:

- reference float state semantics;
- reference learned drift/restoration;
- unit chunks;
- the same 255-step finite prefix and infinite tail definition;
- identical clamping, vital-zero and restoration rules;
- `proj_chunks = (1,) * 255`, so existing forecast ceilings still quote the
  full worst-case 255 units.

For each projected unit step while alive:

1. prepay **one** `simulated_step`;
2. advance F/W/I by the exact reference unit drift;
3. apply the exact reference restoration rule;
4. clamp all five channels;
5. test vital zero;
6. assign `-d_max` on the death endpoint, otherwise evaluate ordinary
   distress;
7. add that one discounted reward.

If the endpoint is dead, do **not** simulate later endpoints. Add the remaining
infinite absorbing `-d_max` tail from the next discount power and return the
body frozen at the death endpoint.

If no death occurs by step 255, add the same final-reward infinite tail as the
existing per-step diagnostic.

No starting reward is added. No extra memory/cycle category is introduced.

The death endpoint itself is paid as one simulated step even though its reward
is the known `-d_max`; this is conservative and keeps one paid unit per
projected endpoint reached.

## Why the common forecast remains 255

The existing information kernels precompute a complete common work ceiling
before comparing branches. Candidate actual death time is value/state
dependent, so the forecast may **not** rely on early death.

Therefore `projection_simulated_steps_ceiling(candidate) == 255` must remain
true. Early death lowers actual settled work only; it never makes preflight
cheaper or changes the common forecast body.

This gives a strong parity expectation: if projection values are exact, the
#1146 Candidate-G decisions must match the existing per-step arm because the
forecast body and information semantics are unchanged.

## Frozen exactness characterization

### A. Existing 486-case projection grid

Reuse exactly the projection-consistency fixtures:

- midpoint + G0 seeds 6000..6004;
- 27 bodies;
- sleep-learned, sleep-unlearned, projection-equivalent;
- prefix / +1 wait / +3 waits;
- horizon 6.

Truth: existing `per_step` reference-float projection.

Report max option-value error, max pairwise decision bias and max final-body
channel error.

### B. #1150 nonlinear option set

Reuse its ten bodies and six plans. Report the same direct errors versus
existing per-step truth.

## Frozen Candidate-G grid

Reuse #1146 exactly: 80 states, same effect memory, recurrence 2/6/10,
explorer, ordinary continuation and horizons.

Because the common forecast ceiling remains per-step-identical, exact semantic
parity requires:

- selected epistemic = **32**;
- selected water-deficit = **8**;
- selected other-deficit = **24**;
- declined = **40**.

Also report:

- actual CognitiveWork mean/max;
- actual energy/vigilance mean/max;
- common forecast ceiling mean/max;
- projection calls;
- early-death projection calls;
- paid projection steps total and mean per projection;
- death-step min/mean/max;
- actual-work/common-ceiling violations.

Frozen baselines from #1149:

| projection | selected | mean simulated steps/state | mean energy | mean vigilance |
| --- | ---: | ---: | ---: | ---: |
| Candidate-F | 24 | 470 | 1.3402 | 1.840 |
| per-step | 32 | 1288 | 2.9762 | 3.476 |

Cycles=18 and memory_items=201 for both baseline projection arms.

## Frozen gate

Structural/software pass requires all:

1. max option-value error <= **1e-12** on both fixture families;
2. max pairwise decision bias <= **1e-12**;
3. max final-body channel error <= **1e-12**;
4. all 80 #1146 states complete;
5. Candidate-G counts are exactly 32 / 8 / 24 / 40 as above;
6. zero actual-work/common-ceiling violations;
7. mean actual simulated steps/state < **1288**.

Pass verdict:

`DEATH_TRUNCATED_PER_STEP_EXACT_PASS`

Fail verdict:

`DEATH_TRUNCATED_PER_STEP_EXACT_FAIL`

Separately report:

`candidate_f_cost_parity` iff mean actual energy <=1.3402 **and**
mean actual vigilance <=1.840.

A later runtime candidate is authorized by this slice only if the structural
gate passes **and** Candidate-F cost parity is reached. Otherwise preserve the
result as an exact cost reduction and return to architecture design.

Do not change the 255 common forecast ceiling after seeing death times.

## Boundaries

This slice does not:

- change BodyLaws, mortality or distress;
- add a cache or persistent memory;
- approximate any live endpoint;
- change Candidate-G recurrence/information semantics;
- use early death to underquote branch work;
- open World/life/development/selection/validation/reserve conditions;
- authorize Stage 2.
