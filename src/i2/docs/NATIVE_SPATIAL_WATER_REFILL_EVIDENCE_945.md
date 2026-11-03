# P3 #945: first-person evidence cannot include unobserved spatial water refills

**3 November 2026, isolated scientific-validity repair.** Depends on physical-site food [#942](https://github.com/josselin-orta-lab/individual-zero/issues/942) / [PR #943](https://github.com/josselin-orta-lab/individual-zero/pull/943) and independent exogenous food renewal [#944](https://github.com/josselin-orta-lab/individual-zero/issues/944). Research-only native single-owner SQLite lives; not active engine, independent M11, H3 or G3 proof. Do not launch this as a competing CI while #943/#944 validation is pending.

## Verified source risk, not a prior behavioral conclusion

Older `bounded_native_evidence` accumulated `evidence:i2:native:water-offer-refilled:<tick>` based on globally known committed time, without checking whether the birth-local water source could be observed at the individual's physical site. It could therefore turn a hidden, exogenous refill of a distant source into first-person evidence. It is a **source-provenance defect** regardless of whether any particular motor decision was influenced. Frozen #943 64-step and #944 independent 96-step observations must not be retroactively rewritten.

## Minimal v18 native fix

For **new** v18 spatial research births, never emit a scheduled water-refill *event history* into first-person evidence. Merely standing at a water source now does not prove one witnessed a past refill. The physical refill law and born locality are unchanged; the current `boire` affordance remains directly observable only when at an actual reachable source with current stock. Admitted drinks continue to convey actual bodily consequences. Nonspatial/global-offer research births retain their existing global timing trace for independently audited observations (not spatial P3 scientific evidence).

This deliberately removes unsupported information, **not** a movement prior, hunger/thirst weight, resource score, spatial learning association or physical replenishment. `GENESIS_SCHEMA` advances from v17 to **v18**, so signed older research births cannot be silently interpreted under new subjective provenance rules. One native SQLite owner, paid Competition/Action Control, UC and cold replay remain unchanged.

## Prespecified negative and positive tests

[Target test](../../../tests/i2/test_native_spatial_water_refill_evidence_945.py) isolates pure physical route probes (not autonomous evidence): remote refill at tick 3 is physically present but absent from personal water offer and its subjective evidence; after physically reaching camp, the current water affordance is present, but retrospective hidden refill-event markers remain absent. Food source at the other site remains locally offered with its own independent clock; future food and water payoffs are not exposed. Standalone global and zero-refill controls distinguish existing legacy global-affordance research behavior.

Two additional independent internally paid 16-step learning ON/OFF native births with identical physical site/stock/refill laws verify that all actual personal claim events omit hidden spatial refill markers, all motor actions emerge from existing paid Competition, real UC and modeled body consequences remain replayable, and no engine or M11 is asserted. A 16-step trajectory is merely an engineering validity probe, not evidence of natural-learning improvement.

**Falsifier:** a remote timing marker appears in a spatial captured claim, a local physically stocked `boire` disappears, cold audit diverges, or the real physically born water/food stock laws change. Preserve any negative motor consequences. Full P3/P4 ecological and long-life scientific evidence remains not established.
