# Stage 1 projection candidate C: event-aware quadratic accounting

Issue #1061. Baseline before coding:
`f92a7cf016221fafdec70c7f6ccf5606ac0d7675`.

**FROZEN BEFORE CHARACTERIZATION. SOFTWARE ONLY. NO WORLD OR LIFE.**

## Motivation

The existing projection-consistency study established:

- reference `chunk_end`: max decision bias 0.169, 8 paid projection units;
- same-cost `trapezoid`: max decision bias 0.133, 8 units;
- per-step truth: zero measured bias, 255 units.

The same-cost candidate therefore failed. Diagnostic D1 showed that the
projection bias had hidden much of Stage-1 information value.

Candidate C asks whether most of the per-step accuracy can be recovered by
paying only at predicted bodily regime changes plus one midpoint per smooth
segment.

## Frozen algorithm

Keep the outer geometric projection horizon unchanged:
`1,2,4,8,16,32,64,128`.

Inside each outer chunk:

1. analytically find the next continuous-time event under the individual's
   current learned drift/restoration model;
2. considered events are:
   - crossing a bodily distress threshold;
   - vital zero/death;
   - channel clamp at 0 or 100;
   - completion of learned sleep restoration;
3. isolate an event that falls on an integer endpoint into its own one-step
   segment; bracket a fractional event by the adjacent integer endpoints;
4. on every non-dead segment evaluate distress at start, midpoint and end,
   deduplicating start values inherited from the previous segment;
5. fit the unique quadratic through those three values and sum that polynomial
   at the actual discrete step endpoints using exact gamma discount weights;
6. a one-step segment uses its exact endpoint value;
7. death is absorbing maximal distress after the first predicted dead endpoint.

Every distinct distress evaluation is charged as one simulated projection unit.
There is no adaptive tolerance and no result-dependent subdivision.

## Frozen grid and truth

Use exactly the existing projection-consistency grid:

- midpoint + generation_zero(6000..6004);
- sleep-learned, sleep-unlearned and projection-equivalent fixtures;
- 27 bodies;
- horizon 6;
- prefix / +1 wait / +3 waits;
- per-step 255-unit projection as truth.

Total: **486 cases per scheme** (3 fixtures x 6 genomes x 27 bodies).

## Prospective gate

Candidate C passes this software selection gate only if:

1. max decision bias versus per-step <= 1e-3;
2. projection-equivalent invariant max gap <= 1e-3;
3. every direct projection on the frozen grid uses fewer than 255 paid
   projection units.

Also report:

- max prefix value error versus per-step;
- max absolute +1/+3 wait gaps;
- min/mean/max paid projection units.

If any criterion fails: `NO_CANDIDATE_PROMOTED`. Do not tune Candidate C in
this PR.

If it passes: it becomes only an opt-in projection candidate. The next slice
must teach all forecast ceilings to quote its dynamic projection work and then
rerun the already-frozen omega falsifier. Reference adoption remains a separate
ADR-0015 decision.

The default remains `chunk_end` whatever the result.


## Amendment A1 — grid count metadata, before reading Candidate C metrics

The inherited projection-consistency prose described the grid as 270 cases per
scheme, but its executable frozen loops are 3 fixtures x 6 genomes x 27 bodies
= **486**. The first Candidate-C CI stopped on a test assertion checking the
incorrect 270 metadata before printing Candidate-C metrics.

Only this count is corrected. Fixtures, genomes, bodies, plans, algorithm,
thresholds and selection rule are unchanged.
