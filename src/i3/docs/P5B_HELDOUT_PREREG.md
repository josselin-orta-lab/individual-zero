# I3 P5b prospective held-out action-effect readout experiment

**Registration status: prospective, written and merged BEFORE opening the first P5b validation world.**
**Scientific protocol:** `i3-p5b-paid-readout-heldout-v1`.
**EXACT executable scientific source SHA:** `11bd249d269116a720e503bc56e9b1244e91aea9`.
**EXACT prospective P5b schedule SHA-256:** `663e258b3c35e5b8d2f60d437e7ecc3079484dfe07f956d9d50bf775f69a66d1`.
**Frozen G2 raw artifact SHA-256:** `6cfb0ac7c0dd603f67c2a08863e6e8ef2183b51db19bb2ede05ba4e371610419`.
**Frozen G2 canonical SHA-256:** `4663421628f726dde75a3c2f48494e506ceec0fba593dab3441cab8d0da88d2b`.
[Source preflight 42220146405](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42220146405) passed **157 I3 tests under both Python 3.11 and 3.12**, source generation guards, G2 artifact verification, P4a/P4b/P5a original evidence hashes, and sealed allocation preflight **without opening any P5b validation world**.

## Scientific question and boundary

Does the retention and **action-specific reading** of personally learned effect statistics lead to different physical survival, choices and prepaid cognition, compared with masking this information but preserving the actual first-person learning machinery? The earlier P5a effect-storage ablation produced 0/288 survivors against 112/288 under normal learning, yet altered activity and costs. P5b preserves all genuinely executed and paid effect-model updates, controls separate **readouts**, and tests the behavioral consequences. This is **NOT** a pure cost-matched intervention; differences in work done, memories, energy, vigilance, inaction, body states and time at risk are post-treatment outcomes.

Four *paired* conditions, exact same initial world, genotype, life seed, body and physical v2 laws:
1. `full` (baseline): action-specific learned effect predictions, learned source signs, learned sleep prediction, all other mind pathways enabled.
2. `blind_action_predictions`: only simulated action delta readouts masked to zero unknown delta and maximum uncertainty; first-person effect learning and retention, sleep/rest forecast, source-sign recognition, veto, mapping, innate planning and funding still work.
3. `action_agnostic_prior`: every planned action uses the same global effect mean observed by this individual across its actual actions; no action-token-specific association, no world oracle, no manually forged benefits; sleep and source signs remain active.
4. `blind_sleep_forecast`: only personally learned sleep-restoration forecast is masked; learned action-specific effects and physical perception stay active.

All four computations use original budgeted cognitive cycles and work tariffs, not charges for hypothetical tasks. The observer copies only values already computed/paid, never adds an extra prediction or modifies living choices. No mind, learned spatial map, body history or observational trace passes across births.

## Frozen allocation and disjoint custody

The prospective 24 new validation world indices are **72..95**, ecological generator seeds **30072..30095**, life seeds **560072..560095**. Each world index = 72 + 6*population + 2*ecology_index + repeat, with original ecology order `stable,depletion,pulse`. All earlier P4a (0..23), P4b (24..47), P5a (48..71) validation worlds, all selection worlds and reserve seeds 1200000..1200199 are forbidden. Do not reuse even after a failed scientific run.

Study structure: **4 original P3 independent genetic populations** × **2 frozen G2 parenting arms** × **6 genotypes per parenting arm** × **3 ecologies** × **2 world replicates** × **4 readout conditions** = **1152 original lives**, horizon **400 steps** (up to 460800 physical ticks). All **48 frozen G2 genotypes**, no selection, mutation, tuning, favorites or discarded unfavorable worlds. Each world/genome pair is exposed to all four readouts with identical life seed. The study reports *within-population* contrasts and treats **n=4 independent genetic populations** as the unit, **not** 1152 independent population replicates.

## Predeclared primary endpoint, uncertainty, multiplicity

The **primary endpoint** is alive and censored at physical step 400, rather than time lived, reputation, learned memory uniqueness, activity or final resource abundance. Within each population and mode: 72 observed lives, pooling all originally frozen G2 parenting arms and ecological repeats in preregistered proportions. Three comparisons are `full-minus-blind_action_predictions`, `full-minus-action_agnostic_prior`, and `full-minus-blind_sleep_forecast`, each measured as censored survivor-count difference per population of 72. Report all four differences, the mean, an exploratory two-sided 95% Student-t interval (df=3, critical 3.182446305), exact two-sided independent-population paired sign-flip p, and Holm exploratory adjustment across all three comparisons. The minimum two-sided sign-flip p attainable with n=4 is **0.125**, so there is **NO CONVENTIONAL CONFIRMATORY TEST** for this small screening study, regardless of signs or aggregate life counts. Do not claim p<0.05 or use individual lives as independent units. No favorable result triggers I3 activation.

**Secondary outcome and mechanisms**: death cause and physical lifetime, actual billed decision/learning energy/vigilance by phase, work counters, physical inactivity and `no_processing_budget`, `no_funded_score`, `control_rejected`, `action_admitted` counts. These are post-treatment mediators and must be reported alongside survival. Energy and vigilance totals differ when realized work/life length differ; no same-realized-work attribution or post-hoc equalization is allowed.

Only the first **12 prepaid-decision steps** of each life are retained as compact option-score witnesses. Descriptive predeclared mechanistic contrasts on each paired `full` vs intervention life: the first different physical action within 12 steps, the first difference in the same named *actually scored* candidate's final score at exactly equal pre-decision five-channel body **before the first physical-action difference**, and the corresponding difference in its projected base return (separate from curiosity/risk bonus). Count how many of 288 pairs per intervention qualify; report first-difference distribution and censoring. A matched body and option **do not guarantee matched hidden memory, RNG or all relevant perceptions**. Thus this is a descriptive mediator diagnostic, not a randomized isolated within-state information-only estimate. A pair with no matching scored option or no divergence in 12 steps must be retained as a valid null/absence of evidence, never imputed.

## Stop conditions, original data and interpretation

All 1152 original outcomes, adverse signs, deaths/censoring, source/genome/world/life seeds and exact physical evidence hashes are retained. The execution audits every decision and learning phase for genuine positive paid work, no unpaid requested work, no fabricated decision scores, no postmortem learning, complete chronology, correct actual replay accounting, and correctly paired initial opportunity. If a condition fails, label the attempt **ENGINEERING_INVALID** and preserve all available logs. Do not silently change source, discard adverse lives, reuse the same study worlds or retry scientific allocation without a separate explicitly registered amendment. An archive verifier may be corrected independently and rerun without generating any new life, provided the original data bytes remain identical.

Launch requires **all three** environment locks and source HEAD:
- `I3_P5B_SOURCE_SHA=11bd249d269116a720e503bc56e9b1244e91aea9`
- `I3_P5B_SCHEDULE_SHA=663e258b3c35e5b8d2f60d437e7ecc3079484dfe07f956d9d50bf775f69a66d1`
- `I3_P5B_APPROVED_PROTOCOL=i3-p5b-paid-readout-heldout-v1`

The one-shot workflow must first establish that **this preregistration commit was already merged into `main`** before checkout of the *older exact scientific executable source* and any world exposure. Then run `PYTHONPATH=src python -m i3.lab.p5b_heldout --run OUT.json`, retain unmodified original full JSON and SHA-256 checksums, and publish a separate custody report and interpretation only after complete verification.

P5b does not test subjective experience, autonomous selfhood or whether identical genomes acquire stable personalities under an identical new challenge. Those are separately open. I1 remains active, I3 unregistered, and P4 reserve untouched. **No scientific GO.**
