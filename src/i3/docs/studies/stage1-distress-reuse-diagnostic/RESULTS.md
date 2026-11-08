# Exact distress-evaluation reuse: insufficient to close the cost gap

Protocol: [STAGE1_DISTRESS_REUSE_DIAGNOSTIC.md](../../STAGE1_DISTRESS_REUSE_DIAGNOSTIC.md),
declared before execution at `d525a8a17faa7c13df3a616fea33dbb05fe68db8`.

Baseline: `98d2c650435ca19c5d2f1357b586c09a9e1a37a4` (#1153).
Characterized source: `96455f010a8ad150536db1bded0f01843b761860`.
GitHub Actions run `42473511648`: Python 3.11 PASS, Python 3.12 PASS.

Software only: no World, no life, no changed work accounting.

## Frozen verdict

`FEATURE_REUSE_INSUFFICIENT`

Candidate-F's prospective plausibility threshold was frozen at 470 simulated
steps/state.

Observed on the unchanged 80-state #1146 grid:

| Metric | Mean |
| --- | ---: |
| actual #1153 total simulated steps | 853.3 |
| non-projection steps | 13.0 |
| projection endpoints | 840.3 |
| actual distress evaluations | 835.3 |
| consecutive feature runs | 760.5 |
| unique feature tuples per decision | 639.9 |
| consecutive-only lower total | **778.5** |
| ideal decision-memo lower total | **657.9** |

The ideal memo lower estimate deliberately charges **zero** memory, read or
write work. It is therefore more favorable than any implementable cache, yet
it still exceeds 470 by 187.9 simulated-step equivalents/state.

The probe preserved the #1153 decision surface: 32 selected epistemic states,
including 8 water-deficit states.

## Reading

Exact duplicate distress results exist:

- consecutive-only reuse removes 74.8 distress evaluations/state on average;
- an ideal decision-wide exact memo removes 195.4/state;
- up to 984 distinct feature tuples are still required in one state.

But the redundancy is not large enough. The remaining cost is the need to
evaluate many genuinely different future bodily-distress states.

This closes:

- last-feature reward reuse as the route to Candidate-F cost parity;
- decision-local exact feature memoization as that route;
- another exact cache/refactoring campaign without a new source of compression.

## DRIFT DETECTED

Further cache engineering would add state, accounting and invalidation
machinery while the frozen optimistic lower bound already misses the target.
That would improve implementation sophistication without answering a new
scientific question.

Return Stage 1 to the projection architecture itself.

## Next question

#1149 already exposed the useful contrast:

- Candidate-F's event-local projection is much cheaper and makes information
  relevant in 24/80 states;
- exact per-step makes it relevant in 32/80, including **8 water-deficit**
  states where Candidate-F selects none.

Before inventing another projection, audit that residual. Determine whether the
lost water-deficit decisions are concentrated at generic events already visible
to the individual projection model, especially:

- predicted first vital death;
- distress-threshold crossings;
- restoration completion;
- option-induced shifts of those event times.

If the residual is localized, freeze a generic hybrid projection that uses the
cheap event representation on smooth intervals and exact unit steps only in a
small event neighborhood. No water-specific or action-specific correction is
allowed.

If it is not localized, report that the Candidate-F cost/accuracy frontier
cannot be repaired by local refinement and return to a different architecture
hypothesis.

No World/life panel is authorized by this diagnostic.
