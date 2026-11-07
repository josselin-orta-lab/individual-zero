# Stage 1 — carried food: does the one-reuse bound make information decision-neutral?

**Frozen before coding.** Baseline: PR #1103 head `0fe6b0e` plus test-boundary
repair `ca8ec1d`. Software characterization only: no World, no life, no
development/selection/validation/reserve index is opened or rerun.

## Observed limit (from the #1103 raw-rank audit)

On #1103's synthetic 27-state grid (mixed safe/toxic personal `manger` history,
two carried units), the #1102 carried-food score has **positive information in
18/27 states** but **improves the meal's raw rank in 0/27** (base or total), is
raw-top by base return in 15/27, and P1.3 already selects the meal in 24/27.
The water path showed the same pattern (#1101: 0/80 epistemic trial selections
with exact explorer semantics). Information value exists but does not move a
decision.

## Question

Is that decision-neutrality caused by the kernel's **one future use** bound
(#1102 models at most one repeat regardless of inventory), or does it persist
when each carried unit is represented as a possible future use?

This distinguishes a representational limit (what future the individual can
represent) from a scaling problem of the prior or a dominance of trial risk.

## Mechanism under test (opt-in; default unchanged)

`paid_carried_unknown_food_information_value(..., max_future_repeats=1)`.
With `r = min(max_future_repeats, inventory_count - 1)` represented repeats,
each personal effect branch `i` (unchanged: two or three rows from paid branch
memory, exact-token then same-action support, no new prior) gets plans
`P_ij` = eat `j + 1` carried units, `j = 0..r`:

```text
informed = sum_i q_i * max_j P_ij
frozen   = max_j sum_i q_i * P_ij
information_value = informed - frozen  (>= 0)
```

Every cell is simulated and paid before comparison; no early stop. Outcome
branches stay at two or three (plans are not outcome branches). The default
`max_future_repeats=1` must reproduce #1102 exactly (values and work).

Why this is not a behavioral rule: no bonus, no prior, no threshold, no command.
The future uses are units the individual itself carries (first-person). The
score would still have to compete with every other P1.3 option; this slice does
not integrate it.

## Characterization (frozen)

Same 27-state grid and fixtures as #1103 (energy 35/60/85 × food 5/20/40 ×
integrity 20/50/80; water and vigilance 80; same seed, same history). Carried
units `n ∈ {2, 3, 5, 9}`, with `max_future_repeats = n - 1` (1, 2, 4, 8).
Controls: uniformly harmful history at every `n`; one carried unit.

Reported per `n`: states with positive information; median and maximum
information value; candidate raw-top by base and by total; candidate improves
the reference meal's base / total rank; candidate above the reference meal base
score; reference chose the meal; mean paid kernel work (cycles, simulated
steps, memory items) and its ratio to `n = 2`.

## Decision rule (prospective)

- **Defect stop:** harmful history yields positive information at any `n`, or
  one unit yields positive information, or default `k = 1` differs from #1102 →
  implementation defect; stop and report.
- **Bound not causal:** meal base-rank improvement stays 0 for every `n` and the
  raw-top-by-base count does not increase from `n = 2` to `n = 9` → the one-reuse
  bound does not explain decision-neutrality; close this direction for carried
  food and record it.
- **Bound causal:** base-rank improvement > 0 for some `n > 2`, or raw-top-by-base
  increases → software evidence that the number of represented future uses gates
  the decisional weight of information. Next question (not implemented here):
  how an individual could estimate future uses from its own history when they
  are not carried.

Either way: no runtime integration, no Competition change, no world, no tuning
of grid, seeds or fixtures after the first run. Results are recorded as they
come, labeled `DESCRIPTIVE_NOT_COST_MATCHED` like #1103.
