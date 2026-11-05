# ADR-0009: Make I2 physically and temperamentally comparable before I1/I2 adaptation studies

**Status: ACCEPTED by project owner, 2 November 2026.** Scope: subsequent I2 development and scientific comparison. This is not engine activation or a retrospective change to an existing scientific result.

## Decision

The previously proposed direct I1/I2 comparative-adaptation campaign was **premature**: the active I1 natural-v4 world uses four physiological reserves (energy, food, water, integrity), coupled metabolic recovery and rest, dehydration/starvation terminal outcomes, and a born five-coordinate temperament; the current I2 research owner uses an energy-only toy body and no integrated born temperament. Differences in outcomes could thus come from the body and temperament rather than cognitive architecture.

**Before attributing superior adaptiveness to I2**, implement and independently verify parity in initial body conditions, physical transitions, food/water effects, action affordances, metabolism, fatigue/sleep constraints, world-clock semantics and raw birth-temperament coordinates. Do not import I1's executable runtime/state into I2. Keep the cognitive mechanisms independent and do not suppress I2's **innate** survival reflex merely to make it look learned.

## Incremental engineering

1. Inspect the actual I1 natural-v4 implementation, not historical Stage2 defaults; record actual physical constants and per-world overrides.
2. Build I2-native **pure**, exact-boundary reference body and temperament types with explicit tests and no second WorldBody/SQLite owner. First tranche in [native body contract](../../src/i2/modules/native_body_contract.py), [native temperament contract](../../src/i2/modules/native_birth_temperament.py), [focused tests](../../tests/i2/test_native_body_temperament_contract_888.py).
3. Next, integrate equivalent effects into the single existing I2 SQLite owner with first-person body observations and costs, consumed birth temperament, clear storage and replay. **The first tranche DOES NOT meet this integration milestone.**
4. Establish same-tape deterministic physical parity with I1 for the same effective world inputs and immutable temperament coordinates. Such external action tapes are **physics-only verifications**, not forced autonomous experiments. Report any mismatch; never tune toy behavior to hide it.
5. Only after physical/temperament parity, conduct prospectively matched, independently born I1/I2 autonomous trajectories with no forced choices, no hidden oracle, equal environment and explicit cognition-cost accounting. A higher energy endpoint in I2's current toy body is not an I1/I2 superiority result.

## Scientific and operational limits

I1 remains the active engine. I2 is an unregistered isolated prototype, M11 independently witnessed continuity NOT_ESTABLISHED and comparative cognitive superiority NOT_TESTED. Preserve all historic null/adverse results and frozen I1/I0 source. Keep CI bounded; documentation alone does not require heavy engine validation. The earlier research closeout remains a true historical administrative decision and this ADR authorizes a **new** engineering campaign, not reopening old cohorts.

Baseline `main 8ccc37aec87cba3cf3bce55f1ef795cb62cfdd6a`. Owner development issue [#888](https://github.com/josselin-orta-lab/individual-zero/issues/888).
