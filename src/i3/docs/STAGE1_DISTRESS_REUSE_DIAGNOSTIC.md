# Stage 1 diagnostic: exact distress-evaluation reuse after death truncation

Issue #1061. Baseline:
`98d2c650435ca19c5d2f1357b586c09a9e1a37a4` (#1153).

**DECLARED BEFORE EXECUTION. DESCRIPTIVE SOFTWARE PROBE ONLY.**

No World, no life, no runtime mode, no adoption, no new work tariff.

## Question

#1153 reduced exact per-step Candidate-G work from 1288 to 853.3 simulated
steps/state by stopping at predicted death. Candidate-F's frozen mean is 470.

Existing projection-candidate accounting describes one distinct distress
evaluation as one simulated projection unit. The death-truncated projection can
therefore contain exact redundancy even when bodily states differ:

- two endpoints with exactly the same `Mind.feats(body)` require the same
  `Mind.distress` result;
- consecutive equal feature vectors need no lookup table at all: the previous
  reward can be reused;
- equal feature vectors across the five projection calls in one decision could
  be memoized exactly, but would require a later paid-memory contract.

Measure that opportunity before implementing either mechanism.

## Frozen fixture

Reuse the complete #1146 Candidate-G 80-state grid through the exact
death-truncated #1153 candidate unchanged.

For each state record the five projection calls and every actual call to
`Mind.distress(features)`.

The probe must not alter CognitiveBudget work or decision values.

## Metrics

Per state and aggregate report:

- actual total simulated steps and projection paid endpoints;
- non-projection simulated steps;
- number of actual distress evaluations;
- number of consecutive feature runs within each projection call;
- number of unique exact feature tuples across the whole decision;
- duplicates removable by consecutive-only reuse;
- duplicates removable by ideal decision-local exact memoization;
- maximum live unique feature count.

For orientation only, construct two **unbilled lower estimates**:

1. `last_feature_reuse_total` =
   existing non-projection simulated steps
   + consecutive feature runs
   + paid death endpoints.
2. `decision_memo_lower_total` =
   existing non-projection simulated steps
   + unique feature tuples per state
   + paid death endpoints.

The death endpoint remains paid in both estimates. No memory/read/write cost is
added to the second estimate, so it is deliberately optimistic and **not a
CognitiveWork receipt**.

## Frozen reading

Candidate-F frozen mean: **470 simulated steps/state**.

Classification:

1. if mean `last_feature_reuse_total <= 470`:
   `LAST_FEATURE_REUSE_PLAUSIBLE`;
2. else if mean `decision_memo_lower_total <= 470`:
   `DECISION_LOCAL_FEATURE_MEMO_PLAUSIBLE`;
3. else:
   `FEATURE_REUSE_INSUFFICIENT`.

If (1), the next slice may freeze exact consecutive-reward reuse with ordinary
CognitiveWork and no persistent cache.

If (2), the next slice may freeze a small paid decision-local feature memo,
including exact key/read/write cost. Do not assume memory is free.

If (3), close distress memoization as the route to Candidate-F cost parity and
return to architecture design.

No threshold or fixture may change after reading the probe.
