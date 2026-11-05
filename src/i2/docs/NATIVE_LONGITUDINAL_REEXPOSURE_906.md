# I2 native longitudinal re-exposure: preregistered 32-cycle cohort

Research issue #906. Built on PR #909 (physical outcome reversal),
and native lifetime + recurring affordance PRs #907 and #908.

**Purpose:** observe whether the same individual's experiences
affect choices when encountering a repeatedly available resource with
physically different qualities. The default innate competition remains
active in BOTH learning ON and learning OFF arms. This is not a
pre-judged performance competition and not a survival proof.

## Fixed before first CI execution

Eight independently born native SQLite lives cross:
- Cognitive arm: personal chosen-result learning OFF/ON, same innate
  needs, temperament, and physical action affordances.
- External water-effect world:
  1. `always_empty`: effect 0 for all ticks.
  2. `becomes_useful`: effect 0 until 12 completed ticks, then 20.
  3. `becomes_empty`: effect 20 until tick 12, then 0.
  4. `always_useful`: effect 20 for all ticks.

All use body (85 energy, 90 food, 35 water, 100 integrity);
five temperament coordinates (0, 0.5, 0.3, 0, 0);
32 physical/cognitive cycles, UC 1000 at birth, original water
stock 1 and one new physical offer every two **committed** ticks;
no food stock, no discovered secondary source, sleep consolidation OFF.
The external quality changes do not alter physical action access,
do not appear as forecasts in subjective claims, and do not grant
hydration unless a real paid water action is admitted and executed.

## Recorded observables

Emit one structured `I2_NATIVE_LONGITUDINAL_906` report for all eight
lives: every admitted action, actual pre/post quality-linked drink,
actual water gain, final hydration, terminal, UC spent, cold replay.
Never force the agent to drink, explore, or follow a preferred script.
Check after/before physics independently for each physical action.
Verify identical initial affordances across all eight births and
identical first-person timing of exogenous water-offer renewal.

Comparisons to analyze *after* the run:
- Number of repeated drinking choices before/after the hidden change.
- Latency from first personally observed failed/recovered drink
  until a changed choice or a useful resource is revisited.
- Whether the learning arm outperforms its innate-only counterpart
  **after matching exposure** rather than merely being born with a
  different world or a more restricted action set.
- Negative findings: no choices change, untested quality shifts
  remain invisible, or an innate response performs equally well.

## Strict limits

One native birth and a 32-tick deterministic laboratory world are
still not evidence of robust general natural learning. The external
world repeats a known small set of offers with a single change in
quality; cognition remains a bounded G2 heuristic, long-memory
readout retains only its 64 most recent choices, and cross-world
distributional survival/long-term learning remains **NOT ESTABLISHED**.
No independent M11 attestation, I1 runtime parity or living I2 engine
is claimed. Dream-like replay stays deferred in #902.

This cohort is independent of the previous **8-tick terminal**
sanity check. The result is not required to be positive, and criteria
must not be rewritten after inspecting first CI logs.

## Retrospective result and identifiability (3 November 2026)

**Status: exploratory analysis of the original, unchanged #910 protocol, not
a new preregistration or a learning-performance GO.** Original source:
[PR #910](https://github.com/josselin-orta-lab/individual-zero/pull/910),
test head `6b29cff5be58e1c6b1eb2dd5cf2e2cd57a0f5c8a`,
[Python 3.11/3.12 PASS run 41609889806](https://github.com/josselin-orta-lab/individual-zero/actions/runs/41609889806).
Both versions replayed the same deterministic laboratory test; they are not
independent biological or scientific replications.

| World | ON/OFF water choices before tick 13 | ON/OFF water choices from tick 13 | First ON/OFF action divergence | Post-change outcome observable? |
| --- | ---: | ---: | ---: | --- |
| Always empty | 6 / 6 | 10 / 10 | None in 32 ticks | No change |
| Becomes useful | 6 / 6 | 3 / 2 | Tick 17 | Yes, both drank after the change |
| Becomes empty | 3 / 2 | 0 / 0 | Tick 5 (before the change) | **NO, censored** |
| Always useful | 3 / 2 | 0 / 0 | Tick 5 | No change |

All eight laboratory lives were nonterminal at the technical 32-tick bound.
In the *becomes useful* world, both arms had the **same admitted action and
physical outcome through tick 16**, including actual successful hydration
at ticks 13 and 15; tick 17 is the first action divergence (learned:
`boire`, innate-only: `dormir`). Its causal attribution should examine
both arms' paid action-specific opinions and identical first-person facts at
the divergence. This establishes a **candidate experience-dependent choice
difference in a bounded engineered policy**, not a general adaptive gain or
an independently verified cognition claim.

In the *becomes empty* world, the quality flip at 12 was never followed by
a chosen drink in either arm. The two lives behaved identically to their
respective *always useful* controls. The experiment **cannot test response
to newly ineffective water** in that cell. Final reserves (82.2 ON vs 62.2
OFF) reflect an extra *pre-change* successful drink in the ON arm, not
recognition of the deterioration. In the always-empty world ON and OFF
make identical decisions across all 32 ticks, underscoring the continued
strength of innate behavior.

The updated software readout distinguishes `UNOBSERVED_CENSORED` from
`PHYSICALLY_OBSERVED`, counts no-motor ticks and checks that any first
choice divergence is preceded by identical committed physical states and
available personal evidence. These are **post-hoc diagnostics**, not
predicted successful results, new world events, new motor authority or
confirmation of longitudinal natural learning.

**Next falsifier:** give the same born individual a genuinely revisitable
physical need and changing resource over enough real, paid time to observe
both success and later failure, with identical innate-only controls. Declare
the environmental change and the opportunity/observation criterion *before*
the new run. If no individual revisits, report non-identifiability again;
never force a `boire` motor action or feed the world schedule to cognition.
