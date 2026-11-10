# I3 Stage 2.1: first actual first-person distress shadow, engineering only

**Prospective intervention frozen before execution (10 November 2026)**. Baseline main: `16c510394f8aec9707818c24e0a0f5a8434ae7f4`. This is a direct successor to merged #1279 and issue #1276, not a revision of the 48 completed synthetic trials. Reference P1.3, I3 registry, closed cohorts, replay gate and action competition are unchanged.

## Question and falsifier

Can two identically counted (k=3) *detached*, personally trained prediction heads generate preoutcome predictions on the **same actually captured first-person Body**, then receive a genuine *later World.step outcome*, without influencing the individual's action, physical bill, survival or RNG? The minimal falsifier is a prospective registered prediction matched to an actual future step plus exact observer ON/OFF equality of full physical/decision evidence. If no eligible six-memory history occurs, report zero scored windows, not a positive outcome.

This does **not** ask whether replay priority improves prediction. No adaptive memory selection, reward shaping, future-resource hint or synthetic rescue policy is authorized. The historical `PersonalDistressHead` is action-agnostic. Any difference in proper squared loss is descriptive for one factual logged action, not a causal action-value or counterfactual World comparison.

## Frozen non-scientific engineering setup

- Exactly two predetermined temporary reference lives with `midpoint()`, `dev_open_field()`, life seeds `920041` and `920042`, each horizon 80, each executed ON and OFF with the same genome, WorldSpec and seed.
- The observer is an *external, scoped method spy* in `lab/stage2_lived_distress_shadow_engineering.py` wrapping `Mind.decide` AFTER it returns and `World.step` AFTER it returns, without altering either value. It is never used on scientific original lives, in the engine dispatch, in parallel threads or as an action selector.
- At the first decision with at least six actual personal memory tuples, after the individual's choice but before World.step: clone one real Mind into two heads, execute exactly three replay training updates with historic TD-priority versus the separately seeded HMAC random memory identity selector, and freeze both forecasts (SHA-256) at the current *actual* captured body. Do not substitute an imagined after-body or peek into the World.
- Score only the next factual step's returned observed Body and actual terminal flag, using the existing intrinsic distress target and squared loss. Keep the terminal penalty as an adverse observed target. A missing eligible history remains NO_ELIGIBLE, never zero loss.
- Compare `trace_head`, `evidence_head`, `steps_lived`, `terminal`, `death_causes`, `actions`, `final_body`, and full `cognitive_accounting` from ON and OFF executions; any mismatch aborts. No revisions, rerolls or selective omission.

## Interpretation and hard limits

This is the first direct prospective check of the head's *software integration with a real first-person outcome*, **not** a scientific birth cohort, proof of generalization or demonstration of cognitive cost-effectiveness. Existing reference Mind cognition is paid by World; the extra shadow-head CPU **is not physically paid**. Thus `scientific_lives=0`, `scientific_verdict=NOT_ISSUED`, no independently witnessed iid ecology, no causal survival inference, and no Stage 2.2 activation.

Scientific development decision after exact-head CI: independently re-express the direct-outcome candidate as a physically tariffed learning/readout operation within the existing energy and vigilance budget **before any use to choose actions**, then design a prospective new-source prequential assessment with full first-person action matching and right-censor custody. Preserve both the no-learning forecast and random-content comparator. If physical parity or data provenance fails, stop instead of silently subsidizing cognition.

## Verification

Target `python -m unittest discover -s tests/i3 -p 'test_stage2_lived_distress_shadow_engineering.py' -v` and full I3 Python 3.11/3.12 software suites on the *exact PR head*. The static method spies run only in isolated synchronous engineering tests and must be restored even on exceptions. Record the Actions run ID, statuses, all observed loss signs, the number of eligible/scored windows and any negative/null evidence before claiming PASS.
