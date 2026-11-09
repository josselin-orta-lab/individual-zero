# Stage 2.1 finite-panel receipt contract (software proposal only)

**9 November 2026. NOT preregistered. NO scientific World, no selection, no validation, no reserve, no new owner lift, no scientific verdict.**
Baseline main `cf9b0c05a4ee6bce5d3dd10afce1aa90b0edc309`.
The original Stage-2.1 [PROTOCOL.md](PROTOCOL.md), [inference audit](INFERENCE_POWER_AUDIT.md), and [v2 statistical revision](PROTOCOL_REVISION_V2.md) retain their histories. I3 remains unregistered and P1.3 funded-v2 remains the reference.

## Precise next implementable question

Before arguing about confidence intervals again, can the observer account for **every assigned validation life**, its genetically selected provenance, its paired world, death/censoring status and actually paid cognitive costs, without turning an aggregate into evidence it does not support?

A read-only software module `i3.lab.stage2_finite_panel` specifies the complete **candidate** finite panel: 8 population IDs × 6 existing F0 validation worlds × 5 selected founders × 5 arms = 1,200 expected reduced rows. Selection remains a separate, never executed operation requiring the complete original selection receipts (40 founders × 6 worlds × 2 policies per population). The reducer's `selected_founders` validates only five **distinct G0 birth seed IDs** from the correct population pool; it cannot prove these five were *actually selected*, or whether the source-locked genome digest matches an original. A future scientific adapter MUST verify those original selection receipts and immutable provenance **before** calling it.

The proposed validation conditions are FIXED on FIXED-selected, GATE on GATE-selected, FIXED on GATE-selected, RANDOM on GATE-selected and ZERO-PERCEIVED-COST on GATE-selected. All four GATE-selected comparisons reuse exactly the same five genome seed IDs and each population's six world slots. Those repeated lives are correlated, **not** 1,200 independent replicates. `expected_cells` constructs identifiers only; it never constructs a World or Mind.

## Fail-closed reduced receipt contract

Every row must carry exactly:
`condition, population, family, world_index, world_seed, genome_seed, life_seed, terminal, steps_lived, cognitive_energy_paid, cognitive_vigilance_paid, inactive_steps, sleep_steps, replays_paid, random_draws, random_nominal_replays, random_eligible_replays`.

The software verifies the declared identity against the closed prospective F0 mapping, exact 1,200 distinct cells, strictly valid 1..400 lived steps, nonnegative finite actual energy/vigilance paid, bounded activity/sleep/replay counts, and terminal `dead` or `censored`. `censored` is valid only at 400; death on step 400 must **remain death**. A missing/duplicate/replaced life, invalid field, boolean masquerading as an integer, alien founder, changed world or mismatched seed fails closed. Crashed or absent lives are **not assigned deaths**, and never silently dropped from the denominator. Missing originals make the panel `NO_VERDICT`, not an estimate based on survivors alone.

RANDOM records separately funded draws, scheduled nominal count, eligible replay opportunities and physically paid replays. Each funded draw nominally schedules 6 or 7 replays, with realized paid <= eligible <= nominal. Unfunded/ineligible sleep may reduce actual average replays; the frozen 5532/867 is a nominal expectation and must not be presented as a matched realized replay count. The validator checks internal arithmetic, **not** the life-seeded cryptographic draw sequence against a sealed original; that requires a separate source-locked custody adapter.

The readout reports, **for each population and each F0 family**, survival counts, assigned lives, deaths, horizon censoring, lived time, total actual energy/vigilance, costs per *assigned life* and per *lived step*, inactivity and replay totals. It reports the following descriptive **finite-panel** survival contrasts:

- GATE-selected vs FIXED-selected: architecture-plus-selection difference;
- GATE vs FIXED on identical GATE-selected genomes: same-genome mechanism comparison;
- GATE vs RANDOM and GATE vs ZERO-PERCEIVED-COST on identical GATE-selected genomes: control contrasts.

The eight population-specific survival fractions are also returned, along with their equally weighted finite-panel mean. A favorable family cannot hide an adverse family by being omitted. The reader must not infer equal ecology mechanism weights outside F0, transportability or population-level statistical independence.

## Honest boundaries

This module is *not* a scientific reducer for sealed original life records. Its input is an explicit already-reduced list with unverified labels; it cannot audit the source SHA, exact WorldSpec, genome hash, full two-phase G/R archive, source-frozen random schedule, actual original energy tariff, physical death cause, or independent sampling design. All such attestations are required upstream and remain absent. Calling it on fabricated 1,200 synthetic rows is **unit testing only**, never an experiment or observed result.

Most importantly, the finite mean for this **specified finite panel** is a descriptive quantity, not the expected mean effect in unseen populations or new ecological families. No confidence bound is silently applied; `scientific_verdict = NOT_ISSUED`, `source_and_original_custody = NOT_AUTHENTICATED`, `population_independence = NOT_ESTABLISHED` and `world_opening_authorized = false` remain hard-coded.

## Next falsifiable step and decision boundary

An independent methodological review should choose either a *finite-panel descriptive* question (with limited inference and no claim of mean non-inferiority beyond the panel) or a genuinely generalizable non-inferiority design with justified population sampling, effect margin and power. The current v2 Hoeffding sensitivity is intentionally conservative and is not evidence that generalizable non-inferiority is theoretically impossible. Selection or validation cannot begin until a newly frozen scientific protocol, source lock, index-scoped one-shot consumption, complete engineering rehearsal and distinct owner decisions exist. The preexisting development 80/81 authority remains exhausted.

**Technical acceptance:** 1,200 synthetic receipt test cells validated; corrupted/missing/duplicate/foreign cells rejected; deaths and paid costs preserved; no World import or scientific gate opened.
