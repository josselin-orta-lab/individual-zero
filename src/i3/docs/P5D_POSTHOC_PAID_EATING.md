# P5d: paid eating proposals versus accepted decisions (original-only)

**Technical verification:** [GitHub Actions 42284056578](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42284056578) PASS, 195 focused I3 tests under Python 3.11 and 3.12, exact original SHA-256 analysis and generation ownership checks. Original-only; zero new lives. The ephemeral verification workflow was deleted from the integration branch after validation.

**Classification:** exploratory post-hoc analysis of the same **24 original P5d development lives**; no new life, no additional world exposure, no new genes, no behavioral patch and no scientific GO. Tracking [#1054](https://github.com/josselin-orta-lab/individual-zero/issues/1054). Original executable `00287fcc15892736eabc7bd98b47f83a5fc180f6`; full original data under [permanent custody](studies/p5d-resource-acquisition/) at raw SHA-256 `3d9eff0469157cd1c9f41978720ddc61eb8b40da1c86366b3f1ed50f9823d5ec`.

## New falsifier: is food ignored because it is not proposed or not affordable?

The read-only tool `python -m i3.lab.p5d_posthoc_eating src/i3/docs/studies/p5d-resource-acquisition/p5d-original.json.gz` first calls the independently established `p5d_custody.verify_original` to reject different raw bytes, missing or duplicated lives, forged cognitive payments or inventory discontinuities. It then uses **only** the original already-paid resource score and first-person carried inventory receipts; no mind/world simulator is executed.

| Existing observations when carrying food | Normal curiosity | Curiosity addend discarded |
| --- | ---: | ---: |
| Steps with nonempty carried inventory | 180 | 125 |
| Steps with a genuinely paid `manger:<token>` option | 180 | 125 |
| Steps with enough energy *after paid decision* for the meal motor | 179 | 125 |
| Steps with body integrity above the hard innate veto threshold | 180 | 125 |
| Steps where `manger` is highest among recorded **resource-only** options | 158 | 95 |
| Steps with positive computed curiosity on `manger` | 180 | 125 |
| Steps with positive curiosity **applied** on `manger` | 180 | 0 |
| Steps with negative risk addend applied to `manger` | 180 | 125 |
| Steps choosing direct `manger` / actually eating | 7 / 7 | 0 / 0 |

**Interpretation:** Under curiosity masking, eating was not omitted from the planner, and those 125 scored opportunities had enough motor energy and body integrity above the threshold that could trigger the narrow innate-integrity veto. Yet in the actual lived decisions the direct eating option was not chosen once. The risk penalty remains applied in the mask arm; these results cannot isolate its effect from the missing curiosity bonus or the changing history.

An important caveat: the original P5d observer persisted **only resource-family scores**, not the complete paid candidate set (especially `attendre`, `dormir`, movement and exploration). Therefore **95/125 top resource scores do not mean 95/125 best overall options**. Also missing are accumulator state, within-decision competition winner before motor admission and the complete per-option motor veto trace. The current receipts establish *non-selection* but cannot distinguish full-score competition, cross-step accumulator inertia and controller fallback. Do not call this an action veto or cognition deficit.

The conditions diverged in physical action by step 1 or 2. These are repeated dependent observations from two engineering genotypes and a 120-step developmental horizon, not independent populations. Scores for different histories cannot be interpreted as paired equal-body treatment effects.

## Next smallest engineering instrumentation

Expose, at the **observer boundary only**, exactly the **already computed and paid** score witnesses for *all* candidate families in a new development-only diagnostic; do not execute additional forecasts or RNG and do not supply a privileged source to Mind. Record in a read-only sidecar: option identifiers, retained full score components, finite-budget conditions, winning option before motor admission, any fallback to second-ranked option, final admitted motor command, and existing motor-cost and physiological receipts. If any item would require extra cognition, it cannot be silently added or charged for unexecuted work. Default trace/evidence hashes and learned state must be identical with/without observation.

Before opening new worlds, test synthetic chooser/receipt parity, correct rank semantics under signed score changes, collection-to-ingestion, and strict no-postmortem work. Then freeze a small **new development-only** cohort, independent of P5c published validation 96–119, with explicit stop rule and no genome tuning. Future scientific validation requires independent populations/ecologies and a separate prospective protocol with indices >=120; original P4 reserve stays sealed. Same-genome/different-lived-history individuality remains a separate question under #1026.

I1 remains the active engine, I3 is an unregistered proposal.
