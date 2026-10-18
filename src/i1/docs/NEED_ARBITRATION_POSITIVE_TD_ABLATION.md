# I1 : prospective ablation of positive TD attenuation in need-linked affordances

## Causal hypothesis (pre-registered, 2026-10-18)

Evidence: genuine post-birth mortal WAL at commit `5a8045baa7ee95ac597585a7a8c6b1b933cc41ae` ([Actions #39115850839](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39115850839)), garden variant 32, geo novelty 0.30, sleep weight 0.0. At world step 301 the individual already **experienced** eating, perceives 2 berry_a in personal inventory and needs food (current eat-goal pressure 0.30873). Its I1 unknown affordance `manger berry_a` is physically considered with `prior_evidence=0.2083275`, TD learned evidence about 0.00662 and resulting Stage8/Competition evidence **0.0570492** from 25% prior plus 75% TD. Geographic frontier has evidence **0.0969125**. No option was forced. During steps 301–400 no eating despite two perceived berries and continuing hunger, 98 moves and 2 waits, ending in death at step 400. The candidate `manger` was proposed 234 times and never crossed Competition, despite 99 frontier crossings.

This is evidence of a **candidate-specific evidence attenuation**, not proof the learned reward should be regarded as intrinsically wrong. Do **not** change general TD update rules, feeding action priority, GoalManager, action dispatch or World physics. Investigate the learned scale/context separately under #301.

## Isolated research intervention

New `tools/i1_research_lived_evidence_floor.py` is **not imported** by canonical I1. Only an opt-in `--research-positive-lived-floor` in the external, fresh-birth investigation runner installs the versioned `i1-research-positive-lived-floor-v1` evaluator wrapper *in that process before any new birth*. Control processes use the current original evaluator. Only for an honestly generated, UC-paid, current-first-person grounded `i1_unknown_affordance` candidate whose TD state is already learned:
- No learned signal: unchanged.
- Positive learned signal **below its independently justified perceived need-based prior**: replace its input to the existing 25%/75% mixer by the prior, so positive TD does not inadvertently decrease available curiosity. This is a bounded *evaluation* floor, not a guarantee of crossing Competition.
- Positive learned signal above prior: unchanged.
- Zero or negative learned signal: **unchanged**; learned aversion is not suppressed.
- All action eligibility, Action Control, physical side effects, UC charge, option expiration, goal selection, opponent exploration, death and no rollback are retained.

This is a scientific **ablation**, not a parameter promoted to `main`; a versioned birth-policy contract separates it from canonical I1, and the runner records the effective installed policy and refuses a mismatch. The helper unit test tests positive, neutral, negative and malformed signals. Full source/CI evidence must be exact-SHA checked before treating any effect as valid.

## Pre-registered cohorts

[Actions #39117516313](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39117516313), physical initial SHA `d287f63fd4b3ca79f5c78ea71841ccbfe3fdfcc3`. Two worlds (`longlife-garden`, `oasis`) × control/positive-floor × two matched, independently perturbed resource layouts (variants **51/52**, seeds 991051/991052), one new mortal identity per cell, maximum **800** steps per life. Geo novelty 0.3 and sleep weight 0.0 are held constant. The initial source code addition `tests/i1/test_i1_positive_lived_floor.py` occurs at a later commit and must not be misattributed to this first physical cohort if hashes differ.

## Acceptance and rejection

Measure actual applied meals when the individual personally perceives edible inventory and has active food goal, action fraction per need-critical observed step, number of eating-option threshold crossings and goal continuity, real changes in food/water and integrity, mortality and right-censoring, percent exploratory movement, sleep, Stage10 receipts, retained semantic evidence if available.

An apparent gain cannot be declared unless the control and research arms have **matched world layouts, same code SHA, independently born WALs**, observed physical actions and a plausible competition effect. Reject or keep CONDITIONAL if increased eating is accompanied by pathologic exploration suppression, increased mortality, or no life beyond 800. Two layouts per world give **very weak statistical power**; no population-level GO nor causal learning proof. Explicitly include all deaths; never revive or re-run an identity.

This line of research must not introduce water/food or survival outcome information before it was actually experienced, nor treat neutral unlearned berries as guaranteed nutritious.
