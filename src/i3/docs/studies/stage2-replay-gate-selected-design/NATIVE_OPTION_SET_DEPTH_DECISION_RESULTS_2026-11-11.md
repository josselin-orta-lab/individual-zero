# Stage 2 E1: native decision-depth discrimination on a frozen synthetic grid

**Result date:** 11 November 2026. **Technical status:** PASS, negative native action-discrimination result on the declared finite grid. **Scientific status:** NOT_ISSUED. **Operational decision:** STOP this particular horizon-cap candidate; retain P1.3 funded-v2, I3 unregistered Stage 2.1. **Scientific births: 0.**

## Exact evidence chronology

1. Owner-approved completion roadmap, [Stage 2 audit](../../STAGE2_COMPLETION_AUDIT_AND_ROADMAP_2026-11-11.md), merged in PR #1310; evidence-locked E0/E1 review [source-triage report](STAGE2_E0_E1_CAMPAIGN_LAUNCH_2026-11-11.md) in #1311; [previous 3/3 forecast vs 0/3 top-rank software result](PAID_COMPETITION_VS_HORIZON_SOFTWARE_RESULTS_2026-11-11.md) in #1313.
2. [Frozen native option-set protocol](NATIVE_OPTION_SET_DEPTH_DECISION_PREFLIGHT_2026-11-11.md) committed first at **72b996bae2fcdf2e654e529d987a8b80e39fe057** against main **0c68cc4b37137bd2f1cb7b684719828894044001**, *before* the new runnable test/helper.
3. Lab-only [source](../../../lab/stage2_native_option_depth_choice.py) and [five tests](../../../../../tests/i3/test_stage2_native_option_depth_choice.py) built on the fixed grid; submitted in [PR #1314](https://github.com/josselin-orta-lab/individual-zero/pull/1314). **Exact test source HEAD:** c9cecd77ef76f9bcb9c200e3df6fbf46e1bdca7c. Merged into main as **4f8f8fc854c833dfc5f33ca7e77f1baaccef6a29** without touching actual P1.3 runtime, physiology, genome, learned reference, control, registry or old cohorts.
4. [GitHub Actions #43043257219](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43043257219) **SUCCESS** on exact source c9cecd77ef76f9bcb9c200e3df6fbf46e1bdca7c. Python 3.11 job #130600359369 **1,126 tests PASS in 119.299 seconds**; Python 3.12 job #130600358874 **1,126 tests PASS in 187.414 seconds**. Each ran all five new E1 focused tests. All historical scientific-generation/action jobs on that PR were SKIPPED, not relaunched. CI runtime figures describe the whole software suite, **not** measured native cognitive biological costs.
5. Both interpreter versions returned exactly the same digest: **9a08f583a99a15fcf0cafc1146e3c83a83af1a8d1adbd225ab3045c1e9fdf179**. This is SHA-256 of a bounded, deterministically reconstructed software payload from *synthetic unpaid* model states, **not** a living original or independent World proof. The entire 48-row case table and 24 comparison records are returned by the pure source audit(), available for reproduction; the original CI logs preserved the aggregate/result digest, **not** an independently sealed full-row original ZIP.

## Complete declared finite sample and observed outcome

Exactly 3 precommitted artificial bodies x 4 artificial perception contexts (water_here, food_here, frontier, carried_food) x (depth cap1, cap4, full native horizon, plain reference Mind) = **48 executed native Mind.decide calls**, with the same genotype midpoint and life seed 211. Two comparisons per 12 scenarios = **24 short-versus-full contrasts**. The four context fixtures are not genuine first-person captures from lived Worlds; six action-effect means inserted in native EffectsModel were **unpaid fixtures**. The lab subclass modifies ONLY the simulated depth of each offered plan. Original native options, scoring and paid native Competition/ActionControl remain the authority.

| Preregistered readout | Exact source observation | Meaning |
| --- | ---: | --- |
| Real native Mind.decide software calls | **48** | Not manually selected alternate motors |
| Short/full comparisons with the same fully scored offered-option order | **24/24** | No option-set or funding-dropout ambiguity in these comparisons |
| Score-vector differences | **3/24** | Some deeper plan simulations alter the evaluation |
| Selected native option differences | **0/24** | Updated scores did not change selected option |
| Actual native admitted action/parameter differences | **0/24** | No software decision-level mediation shown |
| Funding-dropout or offered-option confounded action differences | **0/24** | No false positive from an unaffordable option |
| Full cap versus plain P1.3 Mind mismatch | **0/12** | Existing complete decision implementation retained |
| Extra cognition charged through native model budget | **PASS** | Simulated plan, bootstrap projection, option service and Competition cumulative model work were prepaid in energy/vigilance and independently reconciled |
| Zero-budget / invalid-depth / unsupported-context safeguards | **PASS** | No unfunded computation converted into a motor |
| Native World calls / new study lives | **0 / 0** | No actual physiological result or independent population |

The sampled differences in scores do **not** imply an improved objective value: the final native option and motor remained unchanged. It remains possible that doing less of the same calculation would save model resources in a future life, but a new cost-aware controller would itself consume cognition and might change later learning, sleep and food. Nothing here estimates that net downstream D advantage. Nor can this small artificial grid refute useful deep simulation in other personal histories, environments or longer plans.

**Software mechanism verdict: NO_DECISION_DISCRIMINATION_ON_FROZEN_GRID.** This is a valid *negative for this predeclared test*, not a universal invalidation of horizon computation. Per the frozen stop rule, do not retune bodies, seed, effects, maps, token names or option types until a positive case appears. Do not open a new lived cohort to rescue this source without a distinct, independently motivated causal hypothesis.

## Critical-path consequence and next gate

The code now supports two bounded facts: on one frozen two-plan software grid, longer horizons changed 3/3 forecasts but 0/3 top-ranked plans; on a more native, 12-context option set, cap1/cap4/full changed scores in 3/24 paid software contrasts but final selected option and physical action in **0/24**. This is evidence *against claiming a newly discovered cost-effective reflection benefit*, not against the general feasibility of self-determining computation.

**Decision:** No adaptive-depth or second replay-head policy implementation is justified from this evidence. Reference remains P1.3 funded-v2. Stage 2.1 is not scientifically closed, Stage 2.2/2.3 not authorized, and I3 not registered. What remains is an **identifiable prospectively testable action-relevant information channel** from real paid first-person experience, a true equal-compute paid-discard native delivery, and independent scientific sampling and cost inference if that channel survives software tests. The [separate proposed PR #1309](https://github.com/josselin-orta-lab/individual-zero/pull/1309) stays a design draft, not a World admission. Do not add generic predictor scaffolding, memories or new survival heuristics to fake a positive case.

**Stop rule for engineering proliferation:** After two consecutive bounded non-decisive source-locked E1 software checks, treat repeated synthetic-state hunting as drift unless new **real original evidence** or a concrete source-verified bug changes the mechanism question. The cheapest next legitimate scientific step is a methods/source-index review to identify a truly delivered, first-person, paid decision signal, not a larger synthetic grid. If no source-justified candidate is identifiable, publish a scoped candidate negative and leave the broader Stage-2 hypothesis open rather than claiming scientific closure by administrative tick-box.

## Reproduction, without claiming local execution

Software reproduction: PYTHONPATH=src python -m i3.lab.stage2_native_option_depth_choice. Focused suite: PYTHONPATH=src python -m unittest discover -s tests/i3 -p test_stage2_native_option_depth_choice.py. The source outputs complete case records with the digest. **This agent did not execute a local clone** (github.com DNS unavailable to its container); the two executions cited above were verified via completed exact-source GitHub Actions logs. No unseen science or new World was run.
