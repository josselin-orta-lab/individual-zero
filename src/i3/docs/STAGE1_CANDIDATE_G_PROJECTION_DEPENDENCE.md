# Stage 1 Candidate-G: does its decision-relevance depend on the projection?

Issue #1061. Baseline: `05a9b33` (#1146). **Declared before execution.
Descriptive software diagnostic only: no World, no life, no study index, no
adoption, no change to Candidate-G's #1146 verdict.**

## Why

#1146 passed Candidate-G's software gate with **one** strictly advantageous
epistemic trial out of 80 states, in an energy-deficit state, with trial
advantage 0.00034. Candidate-G deliberately keeps the P1.3 reference projection
(`chunk_end`).

The earlier projection-consistency work showed that this projection charges
each geometric chunk with end-of-chunk distress, which biases comparisons
between plans of different lengths. Declared diagnostic D1 found that, under
per-step projection, Stage-1 water information became decisive in 32 of 40
selected trials (0/80 under `chunk_end`). Candidate F's lab-gated projection
(`event_local_quadratic4`, decision bias ≤ 1e-3) is the accurate alternative
that exists on `main`. In the rejected omega gate it entered bundled with other
changes.

Question: is Candidate-G's thin decision-relevance a property of personal
recurrence, or of the reference projection it runs on?

## Arms (same frozen #1146 grid and fixtures, nothing else changed)

1. `reference`: `simulation_mode="reference"`, `chunk_end`. Must reproduce #1146
   exactly: 1 selected epistemic, 27 declined, max information
   0.002384135709742774, best trial advantage 0.10848337088618987.
2. `candidate_f_projection`: `simulation_mode="candidate_f"`,
   `projection_accounting="event_local_quadratic4"`, the lab-gated accurate
   projection with no omega and no Candidate-F policy.
3. `per_step`: reference simulation with 255 unit chunks, the diagnostic truth.

## Reported per arm

States with a strictly advantageous epistemic trial (#1146 definition), split
into water-deficit and other states; declined states; maximum information;
best trial advantage; mean and maximum paid work per state (cycles, simulated
steps, memory items) and its ratio to `reference`.

## Reading (no decision rule; nothing is adopted)

- `reference` must equal #1146; otherwise the diagnostic is invalid.
- If the accurate arms show many more epistemic selections than `reference`,
  the lever for Candidate-G is projection consistency. Its paid cost then becomes
  the architectural question.
- If not, projection is not the lever for Candidate-G and recurrence itself is
  thin on this grid.
