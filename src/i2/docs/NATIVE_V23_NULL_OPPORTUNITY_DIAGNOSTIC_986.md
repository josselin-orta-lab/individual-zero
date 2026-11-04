# I2 P4 #986: interpreting a null v23 exploration mechanism without retuning it

**Preregistered** in [#986](https://github.com/josselin-orta-lab/individual-zero/issues/986) before this read-only observer was implemented. **Source base**: PR #985 `290fd468d7434cccf7bb255f514f2dc26e450b28`. Scientific source: the frozen six-born-life cohort and its independent cold audit in [#984](https://github.com/josselin-orta-lab/individual-zero/issues/984).

## Observed original cohort (not rerun)

At 96 paid steps, both learning-ON control and v23 factor-ON arms had **identical paid motor sequences** in each source-harm world; v23 evidence-tag count was zero in every life. All six agents physically entered source on tick 55 in the frozen graph, and some source food was consumed. The learning-OFF control differed from both learning-ON arms only later (tick 58), when the alternate was already known. That difference is attributable to the pre-existing learning ON/OFF contrast, not to v23. There were no deaths by tick 96, which is a right censor, not demonstrated long-term survival. A source meal can restore food while also damaging integrity; no single-channel improvement constitutes safety.

The frozen test and complete CI verdict remain separate. The original 20-minute Actions verification was cancelled before completing the entire 812-discovered-test-per-interpreter suite; this is **NOT** a technical PASS or a test failure. A subsequent 30-minute run was likewise insufficient. The later exact-head **45-minute** workflow [41901736290](https://github.com/josselin-orta-lab/individual-zero/actions/runs/41901736290) must complete both Python interpreters plus all safety gates before #985 can merge; check the live verdict rather than assuming PASS from a timeout change.

## Distinguishable reasons rather than an invented intelligence boost

The pure read-only `native_need_failure_opportunity_audit.py` operates on **cold-verified** first-person events and physical history. Only committed actions establish visited sites or personally failed consumption attempts. The observer records one first-blocking reason per tick plus independent gate counters, actual offers, paid scores and chosen movements.

- `NO_PAID_FRAME`: no signed paid choice frame; NO_ACTION is not exploration.
- `NO_FAILED_CURRENT_NEED`: no two personally consumed non-restoring resources for an active food/water need, or exploration trait zero.
- `URGENT_REFLEX`: actual body excludes regular exploration due to native reflex protection.
- `ORIGIN_NOVELTY_ALREADY_CREDITED`: avoid stacking independent innate novelty.
- `NO_UNSEEN_OFFERED_MOVE`: all locally offered destinations already visited, or no physical move offered.
- `MULTIPLE_UNSEEN_OFFERED_MOVES`: no unique experiment-defined adjustment candidate.
- `NONPOSITIVE_SCORE`, `SCORE_GAP_GT_FOUR`: proposed movement is not eligible to compete in the existing native score budget.
- `ELIGIBLE_BUT_NOT_CREDITED`: structural conditions observed but the actual recording shows no factor adjustment. In a factor-OFF birth this is expected; in an ON birth it is evidence to investigate, not a retrospective motor edit.
- `UNOBSERVABLE_PREBOOST_SCORE`: a tagged factor-ON frame has already overwritten its candidate value; **the actual preboost score gap cannot be inferred from the final signed frame**. The independent native cold audit, not this observer, must authenticate the recorded final frame and original genesis.

## Diagnostic interpretation of the frozen ticks 49-55

In each original world the native physical record shows a paid camp-to-passage movement at tick **49**, five personally committed non-restoring passage meals at ticks **50-54** (each food delta **-0.2** after metabolism), and a genuinely paid passage-to-source movement at tick **55**. This timeline is authentic physical evidence, but **does not prove** whether a bounded v23 bonus would have applied on tick 52/53/54/55: that requires the corresponding first-person claim, competing scores, and a signed birth factor. The new observer provides these gate-level counters and first-tick locations directly from the already verified existing owner journal. The reported null v23 credit remains unchanged.

**Measured versus unobservable score windows:** `positive_bounded_score_opportunity_ticks` counts only uncredited frames for which the observer can reconstruct an eligible positive candidate and an actual score gap within four units. `tagged_preboost_unobservable_ticks` separately counts genuine tagged activations where the *preboost* score is not in the signed final frame; these must **not** be added into a reconstructed-eligibility count or cited as a measured score-gap opportunity. `factor_tags` still counts actually observed provenance, independently of post-hoc gate classification. Constructed adversarial tests check both categories, but do not establish their prevalence in the original six lives.

The three distinct opportunity cases now have separate counters: `no_movement_offered_ticks` (physically absent movement affordances), `only_visited_moves_offered_ticks` (offered movements, but nowhere unseen), and `unique_unseen_and_double_failure_ticks` when exactly one never-reached local destination coexists with a personally established double-failure. Other reasons can still override such an overlap. The `first_double_failure_tick` and `first_unique_unseen_and_double_failure_tick` fields are retrospective research coordinates, **not new motor triggers**.

An `ELIGIBLE_BUT_NOT_CREDITED` tick under an ON birth is an integrity diagnostic warranting native replay scrutiny, **not automatically an instance of the expected behavior**. Under an OFF birth it may be a fully legitimate structural counterfactual, but not a claim that the alternate motor would have been chosen.

Counterfactuals remain explicitly limited: a historical final motor sequence cannot tell us what an unexecuted action would have found, and this classification cannot prove that boosting a move would improve survival. Neither visited source identity nor external food stock is input to the score categorization. If only one world or six lives yields a correlation, do not promote it to H3/G3 or independent M11.

## Software boundaries

The new module owns no SQLite memory, no motor, no Competition score or future food predictor. The test suite contains only constructed histories, not additional born lives and not a rerun of the original #984 panel. An operator who wishes to classify a real SQLite journal must FIRST call `NativePaidI2.inspect(path).audit()` on the same immutable completed journal, THEN extract the verified `events.event_json` and matching `native_physical_events` before applying `report_need_failure_opportunities`. Do not treat the pure observer as an independent cryptographic witness.

## Existing-life read-only entry point

After a native I2 research life has reached its authentic terminal or its born technical horizon, an operator may run:

```sh
python tools/i2_native_need_failure_diagnostic.py path/to/completed-native-life.sqlite
python tools/i2_native_need_failure_diagnostic.py path/to/completed-native-life.sqlite --ticks
```

The tool calls `NativePaidI2.inspect(path).audit()` **before** reading the old journal, opens the same existing SQLite file in `mode=ro`, and rejects an incomplete still-running life. It reads `native_genesis`, `events`, and `native_physical_events`, reporting eligibility classifications without choosing a motor or creating a life. A read transaction provides a coherent snapshot **during extraction**, but the earlier native audit and this later read are separate connections; their identity is not atomically guaranteed if a writer can change the file between them. Use a preserved, quiescent, completed SQLite source and independently check its immutability/provenance; do **not** promote this observer as a cryptographically source-pinned historical witness. No frozen birth is replayed as a *new* trial; observation is retrospective only. The local cold audit is not independent anti-rollback M11 certification.

**Retrospective-exposure limitation:** the frozen six-life #985 unittest creates its SQLite identities under `TemporaryDirectory()` and removes them when the test exits. The original test emits research JSON traces but does not preserve full journal databases. No SQLite artifacts were listed for the earlier 30-minute or newer 45-minute workflow when this note was reviewed. Consequently this CLI cannot currently produce an independently cold-verified per-tick classification **of those original six lives** unless authentic, complete, unchanged original journal files are separately available. Constructed tests of this observer, including food and water failures, are software checks only. Do not regenerate the six test lives and describe them as the original samples, or infer the original v23 eligibility gates from the partial JSON trace.

The PR is stacked on still-unmerged v23. Do not merge it before #985's complete exact-head Python 3.11+3.12 suite passes. No engine activation, I1 import, autonomous survival victory, or physiological change is included.
