# I3 Stage 2.1: precommitted native World learning-settlement bridge (12 November 2026)

**Preimplementation research record.** Branch research/i3-stage2-actual-learning-settlement-20261112, main base `baed9350f9e6aa234df08af9df66e66cc1f112d3`. This is an **engineering-only, one-action** verification of a pre-existing synthetic **opportunity-cost** result, not a scientific birth or an action/autonomous decision experiment. It is not the causal information-to-action mechanism required by #1276/#1062. The scientific result remains `NOT_ISSUED`, Stage 2.1, P1.3 funded-v2 unchanged.

## Frozen question and boundary

The [existing four-case pure-body model](../../../lab/stage2_readout_learning_affordability.py) suggests that an extra model-funded action-phase readout can make the **next reference outcome-learning block** unaffordable even when the selected physical motor remains affordable. Is that effect actually realized by **World.step -> native Mind.prepare_learning -> World.pay_cognition -> Mind.learn_from_outcome**, with the existing five-channel body and both charged currencies, rather than merely predicted by `transition` and `debit_cognition`?

The four cases are immutable and inherited, **not selected on new outcomes**:
1. energy_boundary body (0.56,60,60,90,80)
2. vigilance_boundary (5,60,60,90,0.55)
3. both_funded (5,60,60,90,5)
4. optional_denied (0.49,60,60,90,80)

Two arms per case: baseline `DECISION=CognitiveWork(cycles=3,memory_items=12)`, and optional-readout-requested with `proposed_readout_work(0)=CognitiveWork(cycles=6,memory_items=48)` admitted by the existing `_authorize_optional` with original motor reserve. Fixed demonstration command `attendre`, no parameter. **The command is an engineering fixture supplied by the laboratory, NOT selected by a native Mind, and must never be described as an autonomous action.** The mind's `last` is explicitly fixture-bound for the native outcome-learning test. Exactly 4 x 2 = 8 isolated one-step **engineering World** transactions are planned; 0 scientific lives, no life runner, no held-out/selection/reserve World. Minimum valid `WorldSpec` (1x1, body from fixture, no accessible resource, no change schedule, unchanged BodyLaws) prevents any World-state oracle or resource-policy test. No shadow history or alternate cognition is injected.

In the optional branch, if a new readout ticket is authorized, execute the existing `passive_readouts(mind, body, action)` **after funding and before World.step**, discard its information, and only then submit cumulative work to the real native World step. If denied, no optional readout or charge. Baseline must run no optional readout. Both modes are an **explicit cost intervention**, not the earlier E3 equal-compute VISIBLE/DISCARD causal information contrast.

## Registered audit and falsifiers

- Count exact requested/admitted `CognitiveWork`, `World.step` actual `cognitive_accounting` energy/vigilance `requested=paid`, `unpaid=0` and compare against `cognitive_cost`.
- Following the factual native step, call `Mind.observe_outcome` and `Mind.prepare_learning` with fresh `CognitiveBudget` matching actual result body. If no base learning can be funded, do **not** call `Mind.learn_from_outcome` or `World.pay_cognition`; preserve a counted `NO_FUNDED_LEARNING` result. If granted, pay using real `World.pay_cognition(learning.work)` **before** executing actual `Mind.learn_from_outcome`, ensuring equality with the allowed replay count and post-payment body.
- Preserve and separately report `IMMEDIATE_POST_WORLD` and `POST_PAID_LEARNING` body, including all 5 channels. Compare real World settlement with existing `examine(body,extra_requested)` pure projections: same funding verdict, step body, learning fundability and post-learning body where available. Verify **two** actual next-learning opportunities are lost (energy_boundary and vigilance_boundary) by extra readout, one case funds both and one denies optional work with no phantom bill. A lost opportunity is not a survival effect and is **not** a measured value-of-information outcome.
- Mandatory no-source-update-before-funding, correct original source body and action, native cost parity, no future World observation given to `passive_readouts`, no extra postterminal calculation. The reader's output is deliberately ignored.
- Explicit negative controls: forged work/account receipt rejected, low E/V optional readout not invoked, invalid body rejected; no `run_life`, no permanent policy or BodyLaws/World/genome changes, no original cohort source/indices reused. Only tests may instantiate the predeclared 1x1 engineering World.
- If the real native sequence diverges from the pure existing reference fixture or an unfunded operation executes, **FAIL** and report the negative/fault rather than tune the four cases. Software integrity `ACTUAL_WORLD_LEARNING_SETTLEMENT_PASS` is not a scientific GO.

## Cost and scientific boundary

The optional tariff is the existing **provisional operator-category** ticket from the prior software model; the new [host operation profiler](STAGE2_HOST_OPERATION_STAGE_PROFILE_RESULTS_2026-11-12.md) does **not** justify converting host nanoseconds/allocations to native energy/vigilance. Laboratory hashing/fixture construction is never billed as cognition. These 8 one-step engineering Worlds are not individual life or ecological samples. They do not establish a naturally chosen decision, generalized cognition, predictive utility, survival noninferiority or an independent target distribution.

**Stop after these 8 predeclared World transactions** in the single main audit, and never open a scientific World. Any CI reruns are software verification of the same frozen engineering fixture, not new biological units.
