# Stage 11: matched total-UC geographic safety preflight ablation

**Registration:** 2026-10-11. **Class:** public software development only, no held-out or scientific acceptance. Normative English `docs/architecture/reference/en/mvp-specification-v1.2.1.md` (§§9.3–9.4, 14 and 16.3) remains the sole implementation authority.

## Unresolved question

In the known-lethal public six-step map, [v2](stage11-local-modulation-geography-results-2026-10-11.fr.md) had 21 repeated failed geographic plans. The [v3 prefilter](stage11-known-lethal-frontier-prefilter-results-2026-10-11.fr.md) had zero rejected plans but consumed 22 accepted UC for read-only Action Control preflight. That does **not** establish an improvement in total UC because safe substitute plans are then constructed, evaluated and registered.

This protocol measures **all** accepted and rejected module UC charges over complete runs, not CPU wall-time or only the geographic slice.

## Controlled compatibility ablation

Use the already-public four `stage11_geographic_robustness_probe` layouts:
`north_obstacle`, `east_corridor`, `visible_creature_north`, `known_lethal_north`, each for exactly **six consecutive world steps**, fixed reference initial body (energy 50, food 60, water 60, integrity 100), with geographic mode on, `max_targets_per_cycle=4`, identical simulation equipment, physics, pre-existing innate safety facts and full Action Control veto.

Compare separately instantiated I0-vNext Stage-11 copies with **one** changed experimental condition:

- **Legacy-compatible geometric target construction:** `geographic_preflight=False`. This reproduces the earlier no-prefilter Stage-11 code path in the *current* software, with mandatory final Action Control admissibility unchanged; it is not a claim that the executable is bitwise identical to an older git commit.
- **Current preflight:** `geographic_preflight=True` (default when geographic exploration is opt-in); only `INADMISSIBLE` directions from `ActionControl.verifier_admissibilite` are excluded, before capacity and `planning_build`. `INDETERMINATE` remains a candidate. The preflight consumes a versioned **1 Planning UC per eligible cycle**, and the full Action Control veto remains in force.

Stamp both configurations with distinct explicit experimental version suffixes and record their hashes; never change a safety threshold, κ, simulator, Equipment, or the normative specification. Geography-disabled reference remains unchanged.

## Prespecified endpoints

For each run report (separately by condition):

1. **Total accepted UC** summed from all accepted `compute_charge` journal entries, in every module. Also report **total requested-but-rejected UC**, which is not consumed, and the number of rejected charge attempts. Do not conflate these.
2. Accepted UC by module, including Planning, Exploration, Competition and Gatekeeper. Accepted Planning charge categories include `planning_build` and the optional `geographic_admissibility_preflight`; report separately.
3. Total number of cognitive cycles from cycle boundary journals if reliably available (otherwise report absent, not invented).
4. Actual geographic `planning_unavailable` counts, `prefiltered` counts, geographically proposed options, physically **applied** exploration commands, distinct sites in real Perception captures, zero known-lethal or occupied-creature visits, and recorded journal/integrity SHA-256.
5. Pure *within-condition* exact replay from fresh copies. Do not compare journal hashes across different configurations for equality.
6. The primary directional question is whether `optimized.total_accepted_uc < legacy.total_accepted_uc` on the known-lethal map; **record the result even when false**. Other maps are negative controls expected to incur a new preflight cost, not necessarily a benefit.

## Hard gates

- Both variants use the actual ordinary safety veto. The legacy condition is a **development ablation** only; never interpret it as permission to bypass a forbidden command.
- No hidden WorldBody cells may enter the individual. The Lab may use layout truth solely to score post-hoc visits, not to supply targets, safety facts or predictions to Exploration.
- `requested_uc` is a logical versioned quantity, not CPU time and never part of an option's value or reward.
- Report a lower total UC as a narrow property of this six-step known public fixture, not a generalized efficiency improvement.
- Do not run private seed lists, Stage9 held-out, full Golden or broaden thresholds to force a favorable result.

**Stage11 IN_PROGRESS. Stage9 scientific validation remains NO-GO, PR draft/unmerged.**
