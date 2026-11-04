# P4 #957: can target-specific food credit mask earlier chosen-outcome value?

**4 November 2026, research-only structural test, before execution.**
Source depends on [PR #956](https://github.com/josselin-orta-lab/individual-zero/pull/956), exact source head `37993c81b8b714e4d2978337ad8dd1fc051e675d`. This dependent working branch contains ONLY a new test and this note. The test is **NOT_RUN**. No PR/CI before both #956 Python checks succeed and it merges. Follow issue [#957](https://github.com/josselin-orta-lab/individual-zero/issues/957).

## Exact distinction

The currently selected generic G2 value can encode a previously observed net bodily consequence. The native `personally_nonrestoring_scores` stage subsequently assigns the **target-specific** food value `innate_adjustment(PRIORS, current_body, temperament)["manger"] + personally_observed_food_successes - personally_observed_food_failures` when a prior target-food result exists, replacing the input score for `manger`. Its target success/failure count checks food restoration only, not concurrent injury. An injured body can still shift the ranking of sleep and other actions through current pressure; this study therefore must not claim complete blindness to injury.

## Controlled pure probes

At an identical current body, temperament, canonical first-person capture and one read-only previously lived food-result projection:

1. Deliberately distinguish three incoming generic scores, including a negative value; show that one positive past target-food restoration yields the **same target-association output** despite differing generic inputs.
2. With no personally chosen food result, show the incoming generic scores are preserved.
3. With learning OFF, show identical preservation even if a physical food-result row exists.
4. With identical food gain but different before/after integrity loss, show the target-specific count and target-association stage remain identical.

These are synthetic *stage probes*, not independent paid lives, not simulated successful behavior and not a replay of #953. Do not infer hidden future harm or an unchosen action. No new resource valuation, action veto, score formula, time clock, state owner, motor or UC path. All physical decisions in #953 remain frozen. Actual choice-level interpretation must consult first-person paid scores, prior observed food outcomes and current body in [#955](https://github.com/josselin-orta-lab/individual-zero/issues/955).

## Interpretation and safety

If tests pass, they establish only a narrow **value-overwrite property of the native target stage**, not the causal source of later harmful feeding. A new composition rule would alter behavior and must be prospectively designed as a separate optional intervention with negative controls and source-locked continuing lives. No survival, P4 generalization, G3, H3 or M11 claim.

After #956 exact-head full dual-version CI PASS and merge, rebuild this two-file slice on the merged main and run one focused PR with Python 3.11 and Python 3.12. Keep CI costs bounded and do not duplicate running jobs.
