# I2 P3 #925: independent ordinary food opportunities in the existing three-site world

**Research-only physical extension, 4 November 2026.** Architectural hypothesis, negative controls and boundaries preregistered in [#925 comment 6631979093](https://github.com/josselin-orta-lab/individual-zero/issues/925#issuecomment-6631979093) **before** code and experiment; exact source baseline merged `main` `93429d93eac247fdfd0dc23693a92871307d3e18` after frozen [#974](https://github.com/josselin-orta-lab/individual-zero/pull/974). Old #972/#973/#974 research identities, traces and outcomes remain **unchanged**, not migrated or reinterpreted.

## Why this is a physical substrate rather than another decision heuristic

[#974](https://github.com/josselin-orta-lab/individual-zero/pull/974) demonstrated a paid, **post-experience** movement-vs-food divergence only when food physically harmed integrity. G2's generic *whole-body* result favored leaving a damaging single source over eating a needless, damaging third meal, unlike the target-only food success score. In harmless food worlds the same-world actions coincided. All four 96-step lives were right-censored and source-local nutrition had **no second physical alternative**. Leaving the harmful site was not demonstrated *switching to safer food*. We must not add a reward for unseen source quality or interpret inability to find a nonexistent alternative as cognitive failure.

## Native v21, minimal single-owner implementation

`src/i2/runtime/native_paid_cycle.py` now defines `i2-native-paid-local-life-v21-dual-local-food`. Existing `ordinary_food_site`, primary stock, replenishment, food gain and integrity injury remain exactly the same in a no-secondary birth. New birth-only fields:

- `second_food_site=None` by default; when set, it must be a **different** location in the existing `camp/passage/source` graph, with `spatial_world=True` and a real primary site.
- `second_food_stock=0`, `second_food_restock_every=0`, `second_berry_food_gain=0.`, `second_berry_integrity_delta=0.` when no secondary site exists. When enabled, all stock/rate/effects are separately frozen at birth, included in genesis digest and immutable. No overlapping food sites, no new owner, memory, map, candidate action or motor semantics.
- At a current location, only food belonging to that location can be offered. Stock counts previously **admitted** meals at that location reconstructed from actually committed adjacent moves. Time-based restock follows each site's **own** exogenous law. This does **not** disclose a remote site's stock, hidden food efficacy or future replenishment to current first-person evidence.
- A legitimately admitted `manger` applies exclusively the *current site's* birth-locked food gain and integrity delta through the existing body/action journal in the existing SQLite transaction. No free energy, no special safety override, and no credit to unchosen food. Exact same physical law is reconstructed from prior committed rows during cold audit. The one `manger` semantic still supports G2 chosen-result scores across sites, a scientifically distinct limitation for later testing, **not** a place-specific source memory invented here.

The preexisting cognition and physiology/UC owner, birth temperament, current needs, paid Competition, fresh Action Control, irreversibility, first-person boundary, origin novelty and all optional learned/innate score mechanisms remain unchanged; I2 remains **NOT_REGISTERED_NOT_EXECUTABLE**, G3/M11 **NOT_ESTABLISHED**. v20 signed SQLite lives have no compatibility migration and are preserved only as immutable prior research artifacts.

## Technical negative and physical tests

`tests/i2/test_native_dual_local_food_925.py` covers the following:

1. At camp, **neither** remote passage nor remote source food is offered. At passage a selected safe/unsafe food offer uses passage stock/effects only. When depleted, passage does not borrow source stock. Visiting source exposes independent source stock/effects; its meals do not deplete passage. Returning to passage does not restore it magically.
2. Separate exogenous per-site replenishment clocks, no future effect or offsite offer; a helper-only physical fixture is **not counted** as an autonomous chosen life.
3. Single-primary source projection remains available to older pure fixture dictionaries; no-secondary births preserve legacy physical rule semantics under new *unmigrated* genesis.
4. Invalid site overlap/nonspatial/bad stock, bad timing and invalid food gain rejected; one genuine unscripted 30-or-terminal tick native life receives paid decisions and an independent cold replay; mutation of the immutable secondary injury in genesis is rejected.

A future biological trial must never use pure fixture motion rows as observed paid decisions.

## Prospective scientific successor, not executed by these unit tests

Freeze a separate new P4 cohort **only after** the physical CI completes: same identity birth law and competing needs across learning ON/OFF, with a food opportunity at passage and another at source whose unknown injuries are **counterbalanced**; include both harmless, both harmful, depleted/inaccessible alternative and genuinely never-observed choices. Hold innate exploration equal, source exposure and current bodily state observable in traces. Only a first *real post-harm* decision that voluntarily approaches and consumes the genuinely separate safer alternative can count as a candidate history-dependent change. If the individual never meets the source, report NO_EXPOSURE. If neither physical option is feasible, report NO_FEASIBLE_ALTERNATIVE. Wrong choices, hesitation, wasting UC, injury, zero-food death and right censor all remain publishable. No default activation, learning-score formula revision or scripted rescue.

**Scope and CI:** single focused source/test/document PR, exactly one normal full Python 3.11+3.12 I2 proposal CI, six boundary checks plus inert-engine assessment. No PR merge without full exact-head PASS; no scientific adaptation or H3 claim from green tests. Research next-step is an explicit P3/P4 decision based on this real substrate, not a new heuristic.
