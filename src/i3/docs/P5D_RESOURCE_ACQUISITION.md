# P5d: resource acquisition and need-weighted curiosity (engineering only)

Tracking: [#1054](https://github.com/josselin-orta-lab/individual-zero/issues/1054). Baseline main: `2d029edc3bc45e8dc14d606dcec5ef984144c32c`, after original-only P5c mortality analysis. No new selected genome, innate rule, world physics, cost tariff, action or rescue policy.

## Question and falsifier

Does curiosity masking primarily change which resource opportunities the individual *actually evaluates*, which motor commands it emits, whether acquired resources produce useful bodily gains, or only its later physical/budget trajectory? The first P5c result is exploratory: normal scored curiosity survived 110/288 vs 4/288 masked; original early command counts 392 vs 132. Command counts **do not** establish acquisition. The P5d observer should falsify a simple "more resource commands = more useful uptake" interpretation by permitting an admitted `boire` with zero positive water uptake or a `manger` with nonpositive food gain and harmed integrity. It must also preserve every original behavioral and paid-work witness when enabled.

## Observer boundary

Optional `run_life(..., observer_resource_acquisition=True)` attaches `src/i3/runtime/resource_observer.py`. Only `run_life` reads the external sidecar. There is **no change to `Mind.decide`, its first-person inputs, internal memory, action rules, selection, or motor/physics authority**.

Each step captures the original pre-decision five-channel body, capture-local water/tokens/inventory and neighboring opportunity count, first-person mapped-position count, the existing personally computed urgency (when funded), the **already funded** resource option-score witnesses, chosen plan, admitted physical action, post-transaction inventory difference, actual water/food change above ordinary metabolic decay, post-physics and post-paid-learning body and actual decision/learning charges. Exogenous stock and hidden token-effects are never passed to Mind or read as pre-action evidence. After-physics body truth is **observer-only**.

Six distinct states must not be collapsed:

1. Resource option *offered* by the personal planner.
2. Option *simulated/scored with real prepaid cognition*.
3. Motor *admitted* with sufficient resources and control checks.
4. Resource action *physically executed*, i.e. stock/inventory transaction accepted.
5. Resource *actually obtained*, distinguished from a zero- or negative-uptake contact; inventory collection and ingestion are separate.
6. Later survival or death, potentially mediated by many subsequent costs and choices.

World currently rejects invalid/empty resource commands transactionally: there are no "failed admitted contacts" in a completed life; rejected proposals are summarized in existing control diagnostics, **not falsely recorded as attempted contacts**. Positive uptake above passive decay is not a counterfactual treatment effect and may be zero because of saturation. `new_personally_mapped_cells` means newly stored spatial observations, **not** new physical visits. First-person captured nearby resources are the interface input, **not** proof that perceptual noise permitted recognition.

## Fixed development-only diagnostic

`PYTHONPATH=src python -m i3.lab.p5d_development --manifest` is pure metadata. `--run-development` would execute **24 new DEVELOPMENT-only lives**: three existing P2 families, indices **32..37**, engineering G0 seeds 901/902, full vs `discard_curiosity_bonus` score masks, life seeds 860032..860037, horizon 120. The same world/genome/seed and v2 prepaid work rules apply to paired modes, but their **realized** cognition and bodily states can diverge. The output retains all per-step observer receipts, population-free aggregate counts and first paired score/choice/contact/uptake/body/funding divergence. It is **not prospective validation or a claim of causal mediation**. Do not tune genes or fitness on published P5c validation indices 96..119.

Tests: `python -m unittest discover -s tests/i3 -p 'test_*.py'` and `python scripts/check_engine_repository.py --json`. `tests/i3/test_p5d_resource_observer.py` tests opt-in parity on a development world, no unpaid work, allowed indices, real zero-uptake contact and rollback of unavailable resources. CI/source SHA and scientific outcomes must be reported separately; constructing this source or passing tests does **not** imply that the 24 development lives were executed.

## Next decision

If development measurements discriminate offered/scored/issued/absorbed resource pathways, write an independent **prospective** P5d study protocol before ever touching new validation worlds >=120. Larger genetically independent lineages and genuinely new ecology mechanisms are required for broader generalization, rather than repeating P3's four population units. The separate same-genome/different-history/common-novel-challenge question remains open under #1026. I1 remains active, I3 is unregistered and the P4 reserve is sealed.
