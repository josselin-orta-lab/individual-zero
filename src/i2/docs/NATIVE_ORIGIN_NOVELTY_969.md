# I2 P3/P4 #969: origin-visited novelty is an experimental tie discriminator

**Preregistered before source edits:** [issue #969](https://github.com/josselin-orta-lab/individual-zero/issues/969), parent [#949](https://github.com/josselin-orta-lab/individual-zero/issues/949), baseline main `c6d6f8ec10546d3055d13db19754c20a20dc4812`. This is a **new research-only native v20 birth contract**, not a correction to historical v19 lives. No runtime migration, I1 imports, external actuation, active registration or independently witnessed M11.

## Source-locked motivation and limits

Read-only actual paid #947 96-step trials, head `c167e3a9cb8779a82b7a4fe62096405844a146bc` and [CI run #41734213024](https://github.com/josselin-orta-lab/individual-zero/actions/runs/41734213024), showed 82 OFF and 75 consecutive ON positive ties at passage for `se_deplacer_vers_camp` versus `se_deplacer_vers_source`, both with score 4. Both lives declined to explore source and never encountered food. This is confirmed decision ambiguity, not evidence that the hidden source was known or must be visited. The later six-life #968 panel stayed at camp until zero-food death at tick 61, and its immediate nonaction may have different paid causes; do not attribute it to the passage tie.

## Mechanism and physical boundary

Opt-in `origin_novelty_tie=False` by default, exact bool in the same SQLite genesis digest and cold replay. The native v20 score stage receives only currently offered actions, their **already computed paid candidate values**, current innate exploration and reflex, and the list of places already physically reached by admitted movement (starting with the birth camp). It never receives food/water placement, stock, gains, future outcomes or source names as rewards.

Only when **at least two adjacent movements and no nonmovement candidate are positively tied for the maximum**, and exactly one tied motion destination has not been visited while some other tied destination has been visited, and `exploration > 0` with `NativeCaptureReflex.state == NO_PREEMPTION`, add one unit to that single unvisited movement. No correction for sleep-vs-movement ties; no reweighting of hunger, last resort, learning, or known-place benefit. Both unseen and both seen remain ambiguous. An urgent native reflex, zero exploration, negative/zero tie, higher-ranked action or nonmovement tie gives no adjustment. A site's experimental name is irrelevant to the pure discriminator.

Competition still issues and prices the advice, Action Control still reviews freshness/safety, physical movement still requires an adjacent offered edge, energy and real UC, and a terminal individual's death stays irreversible. Cold audit recomputes the same adjustment only from committed prior evidence; no new memory owner or second motor path.

## Distinct new test and falsifier

`tests/i2/test_native_origin_novelty_969.py` checks exact-bool flag / birth safety, cold replay, genesis tamper detection, symmetry under renaming, genuinely indistinguishable destinations, competition with a nonmovement candidate, known/unknown destination evidence, zero exploration and danger. It also runs a **new and separate** 64-tick pair of independently born, paid, unforced P3-style lives, learning OFF in both, sharing frozen food-source/water-camp replenishing physics from the earlier #944 geometry and differing *only* in the new birth flag. Record actual admission, site chronology, observed novelty tags, food contact, terminal/body, UC and independent cold audit. No motor script or expected winning outcome.

**Primary narrow result:** a first legitimate paid tie actually gains distinction if personally visited-vs-unvisited evidence exists. Secondary: voluntary movement, any actual first food consumption and bodily condition. A technical PASS on a pure score function is NOT evidence of new adaptive autonomy. If neither individual reaches source, interpret as NO_FOOD_EXPOSURE and inspect the **actual new paid scores** rather than tuning this cohort. If the new factor changes no motor actions, record a null. A 64-step surviving life is right-censored. This is not a generalization claim, neither natural learning nor G3/H3/M11.

## CI and handoff

Only one normal full I2 Python 3.11+3.12 source-locked CI after a focused PR is ready; no reruns for documentation or intermediate changes. An engine proposal must remain inert. Code/module hygiene and physical/UC/cold tamper checks are mandatory. Historical experiment sources and their results remain untouched. Final verdict pending exact-head checks and the raw tagged readout.
