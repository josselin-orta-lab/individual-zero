# I2 native terminal-boundary cohort: frozen eight-cycle experiment

Protocol fixed **before execution**, 3 November 2026. Follows issue #888,
the four-step 2x2 comparison in PR #904, and ADR-0009. Do not adjust criteria
to the outcomes after inspecting a CI log.

## Hypothesis, not a claimed result

In the bounded native single-SQLite G2 world, eight consecutive actions with
an initial water reserve of 3 and natural water decay 0.4 per action reach
zero water unless a *physically restored water source* is actually used.
Compare two independently born cognitive arms (learning enabled/disabled,
both with the innate reflex intact) across two externally locked worlds
(one hidden source with water gain 30, and an empty search with gain 0).
The learned arm may abandon ineffective old water after personal experience,
explore, and consume the new source if it physically exists. Neither cognition
nor exploration should create a resource in an empty world.

## Fixed factors

- 4 independent native lives, identical initial 4-channel body
  `(energy=80, food=60, water=3, integrity=100)` and five born traits
  `(0, 0.5, 0.3, 0, 0)`.
- Old water: 4 drinks, each ineffective (gain 0). No food source.
- One physically available exploration site **from birth in all arms**;
  the actual hidden world source is absent/present (gain 0/30).
- Native sleep-consolidation ablation OFF to isolate the learning factor.
- Both worlds run 8 physical/cognitive ticks; 1000 synthetic UC (identical
  in all arms), to avoid mistaking UC exhaustion for metabolic mortality.
- Normal paid cognition, safety, motor admission, metabolism and actual
  physical effects remain in force. No forced action tape or outcome oracle.

## Predeclared tests

Each life must commit and cold-audit exactly 8 physical events, with no
post-terminal mutation; terminal lives must reject another step. Check
matched births and available physical choices within each world. Discovery
can occur only after an admitted exploratory action; a newly discovered
water source can first enter the following first-person capture and be used
at most once. An empty world cannot produce a discovered-water drink.

Expected bounded result: positive-world learner actually explores and drinks,
so its water reserve remains positive and it is nonterminal at the 8-tick
boundary. Both no-learning controls and the empty-world learner remain
dehydrated and terminal by eight ticks. Both controls remain physically and
behaviorally indistinguishable across hidden-source worlds they did not
explore. The positive and empty learned worlds have the same actions until
the exploration result is actually observed.

If any expectation fails, report it and investigate the mechanism rather
than reframe failure as success.

## Limitations and follow-on

An 8-tick difference in **terminal status in one deterministic toy world**
does not demonstrate population survival improvement, generalized natural
learning, robustness to varied birth traits, physical parity with I1,
independent M11, or registered executable I2. The horizon itself prevents
measuring time-to-death beyond tick 8. No weather, travel, resource renewal,
fatigue accumulation, multi-stage sleep, or asynchronous world clock exists
in this prototype. Later replicate across independently sampled world
conditions and birth temperaments, with outcome criteria frozen in advance.

Dream-like reorganization remains deferred in #902.
