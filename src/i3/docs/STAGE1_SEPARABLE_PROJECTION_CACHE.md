# Stage 1 affordable projection: exact separable decision-local cache

Issue #1061. Baseline: `50a1651b9d8e9b4dd7d24ceff7d385438f867e85`
(after #1150).

**FROZEN BEFORE IMPLEMENTATION. SOFTWARE ONLY.**

No World, no life, no study index, no runtime policy, no reference adoption.
P1.3 `chunk_end` remains the default.

## Question

#1149 established that Candidate-G becomes decision-relevant under a consistent
projection, but the accurate projections are expensive. #1150 rejected two
cheap approximations. The remaining structural opportunity is exact reuse:
P1.3 distress is a sum of five channel contributions, while many options in one
decision share unchanged channel end states.

Can the **per-step projection itself** be represented exactly enough by cached
channel-local traces and reused across options before adding persistent cache
state or another runtime mechanism?

This slice tests only that smaller question.

## Candidate: `separable_exact_cache_v1`

The candidate is laboratory-only and decision-local. One cache is created for
one option batch and discarded afterwards. It therefore cannot become stale
across learned-drift changes and introduces no persistent memory semantics.

For a fixed mind and its personally learned projection drift:

1. Project the same 255 discrete future endpoints as the existing per-step
   diagnostic truth.
2. Compute the sleep-restoration schedule from the projected energy/vigilance
   start state exactly as the current projection does. This schedule is shared
   by energy, vigilance and food; water and integrity remain independent.
3. Cache a channel trace by the exact represented float inputs that determine
   it. There is **no interpolation, rounding or body grid**.
4. A trace stores the channel endpoint and its weighted distress contribution
   at each of the 255 steps, plus the three gamma-discounted prefix sums needed
   to stop at an earlier vital death.
5. For a queried projected body, the first zero among food/water/integrity is
   the absorbing-death step. Before that step, the five cached channel
   contributions are summed; from death onward, reward is exactly
   `-d_max`. If no death occurs inside 255 steps, the existing final-reward
   tail convention is retained.
6. The final projected body is the cached endpoint at death, or at step 255 if
   no death occurs.

The candidate may reuse a trace only when its exact key matches. It may never
substitute a nearby level or a nearby restoration schedule.

## Why decision-local first

A persistent cache would add invalidation, retained-capacity and rebuild
semantics before we know whether separability yields meaningful reuse at all.
That would be engineering ahead of evidence. A decision-local exact cache is
the smallest falsifier of the structural idea.

A pass here authorizes only a later paid-memory/accounting slice. It does not
authorize runtime integration.

## Frozen fixtures

### A. Existing 486-case projection grid

Reuse exactly the existing `projection_consistency_characterization` fixtures:

- midpoint plus G0 seeds 6000..6004;
- 27 bodies;
- learned sleep, unlearned sleep and projection-equivalent fixtures;
- prefix, +1 wait and +3 waits;
- horizon 6.

Truth is the existing per-step `chunk_end` projection.

### B. Nonlinear option set from #1150

On the ten bodies already used by
`stage1_affordable_projection_probes.py`, evaluate the same plans:

- prefix;
- prefix + wait;
- prefix + 3 waits;
- drink;
- eat;
- sleep.

Truth is again per-step `chunk_end`.

No fixture may be changed after reading candidate output.

## Reported accuracy

Across both fixture sets report:

- max absolute option value error versus per-step;
- max pairwise decision bias versus per-step;
- max final-body channel error;
- projection-equivalent invariant max gap;
- worst-case metadata.

## Reported reuse / raw work

Because current I3 accounting has no separately frozen price for a single
channel-distress evaluation, this slice **does not invent one**.

Report raw candidate work instead:

- number of project calls;
- channel-trace builds and cache hits;
- channel endpoint/distress samples computed;
- scalar cache writes and reads;
- maximum live cache entries;
- uncached per-step endpoint samples for the same project calls;
- the purely descriptive lower-bound equivalent
  `ceil(channel_samples / 5)`, clearly labelled **not a CognitiveWork bill**.

No energy/vigilance affordability claim may be made from that lower bound.

## Frozen software gate

The structural candidate passes only if all are true:

1. max pairwise decision bias versus per-step <= **1e-3**;
2. projection-equivalent invariant max gap <= **1e-3**;
3. max final-body channel error <= **1e-10**;
4. at least one cache hit occurs on each fixture family;
5. total channel samples are strictly below five times the uncached per-step
   endpoint samples, i.e. separability actually reuses work rather than merely
   re-expressing it.

Pass verdict:

`SEPARABLE_EXACT_CACHE_STRUCTURAL_GATE_PASS`

Fail verdict:

`SEPARABLE_EXACT_CACHE_STRUCTURAL_GATE_FAIL`

A pass authorizes only the next slice: freeze a physical accounting and
capacity model for temporary/persistent cache memory, then test the #1146
Candidate-G kernel under real `CognitiveBudget`.

A fail closes this exact decision-local cache. Do not add interpolation,
fixture-specific grids or special water/drink rules to rescue it.

## Boundaries

This slice does not:

- add a projection mode to `Mind`;
- change `PROJECTION_ACCOUNTING`;
- change genome/body/world laws;
- change P1.3, Candidate-G or Candidate-F policy;
- open development/selection/validation/reserve worlds;
- claim that consistent foresight is affordable;
- authorize Stage 2.
