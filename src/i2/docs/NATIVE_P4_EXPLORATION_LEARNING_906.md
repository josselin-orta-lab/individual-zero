# I2 P4 #906: separate innate exploration from experienced food consequences

**Prospectively frozen 4 November 2026 in [#906 comment](https://github.com/josselin-orta-lab/individual-zero/issues/906#issuecomment-6630029521) BEFORE writing/running the experiment.** Baseline main `6c9157371be0034b90f9fa617d061f721ba4a080` after merged #970, with source-pinned Python 3.11/3.12 PASS. This is a new discovery cohort; never reinterpret #947 or #968. No runtime change, tuning of the origin novelty score, physical policy, Action Control, UC or hidden-world knowledge.

## Frozen 2x2 physical and experience factors

All four native v20 SQLite research births: body `(85,35,35,100)`; temperament `(0,.5,.3,0,0)`; current 3-site world, born camp, water camp, food source; stock water 2 / food 1; renew both every 8 committed ticks; +40 per actual drink, +35 per actual meal; UC budget 950; 96 committed maximum, never restart; same native motor, physiology and replay contracts. Set `origin_novelty_tie=True` in **every** birth. No programmed motor tape.

Within each world, choose only `learning=False` versus `True`, all experimental P2 place-return, handoff, context-free credit, evidence-tie exploration and sleep-consolidation switches **OFF**; `target_food_credit_enabled=True` fixed. Learning itself gates the original G2 outcome history and food-target evidence, so call ON/OFF a **learning package** comparison, not an isolated synapse.

Two harm worlds differ only in *physically applied, previously hidden* food injury: `harmless` = 0; `harmful` = -12 integrity per admitted ordinary meal. No prospective injury oracle and no forced resource consumption.

## Outcomes and causal interpretation

For every independently born continuing life, record actual paid movements, `NO_ACTION`, site chronology, offered local foods and waters, true consumed meals and injury, bodily minima/last state, UC, terminal tick or 96-step right-censor and independent cold audit. Identify novelty provenance tags separately from food-learning evidence. At first learning ON/OFF motor divergence compare exact prior motors and bodily condition and **count personally experienced meals before that divergence**. If food was never encountered or the first difference preceded any actual food, the result cannot establish learned food strategy. Later physically divergent histories are not a second independent controlled contrast. For each learning flag, compare harmful vs harmless only up to first real meal: hidden injury must not change their prior physical histories or motor choices. No extra goals, values, forced rescue or environmental retuning if results are adverse.

**Strong negative outcomes:** pre-exposure divergence, no food exposure, same recurrent harmful consumption, useless abstention, real biological death, or no stable first post-experience contrast. A 96-step survival is censored. Four selected worlds are not random replicates or a generalizable held-out result. Native G3/H3, independent M11, natural learning or systematic survival advantage remain **NOT_ESTABLISHED** even on fully green software CI.

## Engineering and handoff

Only `tests/i2/test_native_p4_exploration_learning_906.py` and this documentation page are new; existing native v20 behavior/code remain unchanged. One normal complete two-version source-pinned CI after opening one PR, all six generation boundaries and inert proposal checks; no intermediate Actions reruns or scoring adjustments. After results, preserve real nulls and only then propose a *separately prospectively frozen* generalization cohort if a food-experienced divergence is interpretable.
