# Repository placement examples (generation-aware)

These are **fictional** examples, not evidence or current implementation claims. First inspect `config/engine-registry.json` and the intended generation's `engine.json`. [Agent navigation](../docs/engineering/AGENT_NAVIGATION.md) explains the authority hierarchy.

## 1. Measure an active I1 cycle

Place generation-specific read-only instrumentation under `src/i1/lab/` or its owning runtime as appropriate; tests under `tests/i1/`. Do not introduce a shared active `src/lab/`. An EXP is needed only if the measurement is part of a scientific claim or expected to alter studied behavior.

## 2. Change how I1 recalls memories

Inspect `src/i1/docs/MEMORY_AND_LEARNING.md` and the specific source owner. Change the minimal I1 module, add targeted `tests/i1/` regressions and preregister a scientific comparison when a behavioral claim is made. The historical I0 source is frozen.

## 3. Study a possible successor mechanism

Keep non-living research code in `src/i2/` and tests in `tests/i2/`, with a clear hypothesis, negative cases and no I1 runtime import. A passing synthetic fixture does not authorize a born I2 or M11 recovery.

## 4. Integrate an external memory package

Put API translation in `src/adapters/`, but keep cognitive policy and first-person memory ownership inside the target generation. Document license, trust boundary, provenance and an EXP if behavior or interpretation changes.

## 5. Fix a logging defect

Edit the specific generation-owned logging component or external observer and add a local regression. Do not change cognition, identity or M11 custody merely to simplify a log.

## 6. Change a generation-wide interface

Record the question and evidence, review an ADR when applicable, then change only the authorized generation's contracts and tests. New generations are autonomous by [ADR-0001](../docs/decisions/ADR-0001-strict-generation-autonomy.md); never retain obsolete runtime fallback modes.
