# Stage 1 Candidate-G: canonical numerical semantics audit

Issue #1061. Baseline:
`819182ee7a749c8667f114fcf14bf38439091708` (#1154).

**DECLARED BEFORE EXECUTION. DESCRIPTIVE SOFTWARE AUDIT ONLY.**

No World, no life, no runtime mode, no adoption, no changed work tariff.

## Why

#1149 compared three projection arms on the frozen #1146 Candidate-G grid:

- reference chunk_end: 1 selected;
- Candidate-F event-local: 24 selected, 0 water-deficit;
- historical float per-step: 32 selected, including 8 water-deficit.

Later projection methodology already established that repeated IEEE-754 unit
addition can delay a vital-zero boundary by one step, while the authorized
end-to-end high-precision oracle follows canonical Decimal state continuity.

The eight historical water selections have very small information values
(about 1e-9..1e-6). Before designing a projection to preserve them, determine
whether they survive canonical numerical semantics.

## Frozen arms

### 1. `historical_float_per_step`

The existing #1149 per-step arm, unchanged:

- reference explicit simulation;
- 255 repeated float unit chunks;
- full 255 projection cost/forecast.

Expected frozen count: 32 selected, 8 water.

### 2. `canonical_high_precision_per_step`

Use the already-authorized end-to-end high-precision oracle semantics:

- one Decimal body continuously through explicit plan and bootstrap;
- 100 Decimal digits;
- 255 exact unit endpoints;
- same represented-float learned effects/drift/genes;
- same reward/readout functions;
- full 255 projection work and forecast quote.

This arm must use the same #1146 information kernel and CognitiveBudget.
Because its paid work/forecast is the same as historical per-step, any decision
difference between arms 1 and 2 is numerical semantics, not cognition cost.

### 3. `candidate_f_projection`

Read the existing #1149 Candidate-F result unchanged as a comparison baseline.
Do not rerun or reinterpret its scientific gate.

## Frozen fixture

Exactly the #1146 80 states:

- 5 body channels;
- levels 20/30/40/50;
- horizons 4/6/8/12;
- same recurrence 2/6/10;
- same personal effect memory;
- same explorer and ordinary continuation;
- same information kernel and strict selection definition.

## Report

Per arm:

- selected state identities by channel, level and horizon;
- selected count, water count, non-water count, declines;
- information value and trial advantage for every state;
- mean/max CognitiveWork;
- actual/common-ceiling violations.

For historical versus high precision:

- selected-state symmetric difference;
- water-selected symmetric difference;
- maximum information-value difference;
- maximum trial-advantage difference.

For high precision versus Candidate-F baseline:

- selected-state overlap/extras/missing;
- water-selected overlap/extras/missing.

## Frozen interpretation

Let the eight historical float water-selected state identities be frozen from
#1149.

Classification:

1. If canonical high precision selects **none** of those eight and selects no
   other water state:
   `HISTORICAL_WATER_SELECTIONS_NUMERIC_ARTIFACT`.
2. If canonical high precision selects exactly the same eight water states:
   `WATER_SELECTIONS_SURVIVE_CANONICAL_NUMERICS`.
3. Otherwise:
   `MIXED_WATER_NUMERIC_SEMANTICS`.

This classification does not promote Candidate-F.

If (1), do not design a hybrid merely to recover historical float water
selections. The next projection target should be canonical high-precision
decision behavior, not repeated-float parity.

If (2), then Candidate-F genuinely loses canonical water relevance and a
prospective generic event-local refinement may target that residual.

If (3), isolate the remaining states before any new candidate.

## Boundaries

This audit does not:

- change historical #1149 evidence;
- change the P1.3 default;
- authorize Candidate-F or Candidate-G runtime integration;
- alter BodyLaws or work prices;
- open World/life/development/selection/validation/reserve conditions;
- authorize Stage 2.
