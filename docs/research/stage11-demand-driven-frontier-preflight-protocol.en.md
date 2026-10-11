# Stage 11: demand-driven local admissibility consultation, public protocol v4

**Recorded before code or benchmark changes, 2026-10-11.** Public software development only. The sole normative source remains `docs/architecture/reference/en/mvp-specification-v1.2.1.md` (§§9.4, 14, 16.3 and 17). This is not a Stage9 held-out registration or scientific acceptance.

## Prior evidence and motivation

[Matched v3 all-module total-UC report](stage11-geographic-total-uc-ablation-2026-10-11.fr.md) found preflight gained 20 UC on the public known-lethal 6-step fixture (235→215 UC), but cost +22, +6, +8 UC on maps where no direction was inadmissible. Crucially the preflight can be charged repeatedly when Exploration has **no novel, physically perceived, traversable adjacent cell to propose at all**. This extension addresses only that situation; it must not fabricate a safety decision or optimize using the hidden map. Because eligibility can change next step, absence is checked anew from accessible Perception and the versioned Exploration visit ledger, not cached.

## Fixed implementation rule

Create a separately versioned, opt-in Stage-11 `geographic_preflight_requires_frontier` (new public development default ON for geographic mode; legacy v3-eager compatibility value OFF). The Stage9 and geography-disabled paths retain their exact original behavior.

At phase-0 freeze, before any Planning proposal, obtain the **unfiltered** `Exploration.geographic_cibles(capture)` from the actual Perception capture and previously recorded physical visits. When this tuple is empty, the v4 mode shall:

- **Not** invoke Action Control's early `verifier_admissibilite` service, and **not** charge `geographic_admissibility_preflight` Planning UC for that cycle.
- Produce no geographic option, no fictitious visit, no phantom `inadmissible` exclusion event. This absence of *novelty* is not a verdict that any cell is safe, lethal or permanently inaccessible.
- Continue ordinary cognitive work, underlying physical safety checks, reflexes, and Action Control's **final** veto unchanged.

When at least one raw frontier exists, the complete existing canonical preflight still runs, charges 1 versioned Planning UC, and removes ONLY `INADMISSIBLE` directions **before** applying `max_targets_per_cycle`. If a sole raw candidate is known lethal, even though filtering yields no target, the preflight MUST still execute and be billed. `INDETERMINATE` stays eligible. Any later physically observed novel frontier requires recomputing Action Control, with no saved safety facts or cross-cycle "no-frontier" latch. The cheap presence test is the same bounded Exploration read already used to produce the frontier, not a second owner, simulator rollout or world oracle.

Preserve the original matched v3 UC comparison by **explicitly pinning the eager-v3 behavior** in its versioned protocol. No rewriting historical v3 hash claims.

## Predeclared software fixtures and measurements

Execute three current-code conditions, each with separate versioned configuration and a fresh I0-vNext runtime, for exactly 6 world steps:

1. Stage-11 geographic preflight **disabled** (compatibility reference, final veto still ON).
2. Stage-11 geographic preflight **enabled eagerly** (v3-compatible, consult on each eligible geographic Planning cycle regardless of frontier).
3. Stage-11 geographic preflight **demand driven** (v4, new behavior).

Use all four original declared public map variants without change: north obstacle, east corridor, visible north creature, and known-lethal north. Add exactly two NEW public fixture shapes, declared now: `all_adjacent_obstacles` (all four neighbors at birth blocked) and `sole_north_known_lethal` (three neighbors blocked, the north adjacent passable but known lethal by the same externally declared innate Action Control fact). Initial body equals public reference setpoints. These two variants are Lab-only fixture construction; the individual sees only its Perception neighborhood and existing canonical safety facts, never the hidden layout.

For each condition report exact source/code/config identifiers, journal verification/hash, physical perceived site count, applied geographic moves, offered frontiers, preflight UC accepted and rejected, total accepted and requested-but-rejected logical UC, Planning UC and rejected geographic plans. Contrast v4 versus eager-v3 primarily on the all-obstacles fixture; report negative or null outcomes honestly on all maps. Verify twice-run exact replay, no ghost movement, no known-lethal or creature-site visits and no change to stage9 scientific status.

Unit checks: no early call when raw frontier absent (blocked neighbors, already-visited cells, no information interest, capacity reached); no Planning preflight charge; correctly recheck when a visible unvisited frontier later appears; known-lethal-only candidate still checked and rejected; no reclassification of `INDETERMINATE`; degraded mode makes no new target and final Action Control veto remains always active.

**Interpretation:** reduced UC is a narrow property of these tiny public fixtures, not general safety/efficiency or convergence. Full Golden, Python reference-environment matrix, Stage9 independent held-out, Stage10 and Stage12 stay out of scope. Stage11 IN PROGRESS; Stage9 SCIENTIFIC NO-GO; PR must stay draft and unmerged.
