# Stage 11: public-known lethal frontier prefilter, development protocol v3

**Recorded before editing code and before the new CI execution (2026-10-11).** This protocol is an incremental **software-development** comparison only. It does not amend the normative English `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, register a scientific held-out experiment, or authorize any scientific GO.

## Existing reproducible defect

[Public v2 evidence](stage11-local-modulation-geography-results-2026-10-11.fr.md) at commit `904b4ec389998b554429a65f642e81677252d878` / [CI #38112051388](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38112051388) had **21** repeated `stage11_geographic_planning_unavailable` journal records in the six-step `known_lethal_north` fixture. Action Control correctly vetoed the known-lethal cell and zero physically observed visits entered it, but a limited Planning UC budget was wasted. The old result stays unchanged.

## Normative boundary and proposed solution

EN normative §9.4 expressly allows Planning to query `verifier_admissibilite(option, contexte)` before finalizing an option. For local single-step geographical frontiers, Stage11 pre-phase-1 freezes a read-only admissibility decision **from Action Control** for each *currently physically perceived* adjacent passable and creature-free direction. The only excluded directions are those for which the existing safety service explicitly returns `inadmissible`. `indeterminate` **must remain eligible** and is never equated with inadmissible or danger. Neither Exploration nor Planning may read private safety facts, Lab WorldBody, hidden danger/lethal zones, or an oracle.

The exclusions are applied **before** the bounded geographic target capacity limit and before any numeric Simulation rollout or `planning_build` UC charge. Thus a denied north cell does not hide a valid east/west/south alternative when target capacity is one. Do not persist exclusions as local causal or semantic facts; recompute them from the canonical safety service at each new cycle, so a later lawful demotion can re-enable the target. Do not change the final Action Control veto or any prohibition category or threshold. All currently retained candidate options must be invalidated if they are no longer a current admissible offered target, and a degradation step cannot designate a new one.

One `stage11_geographic_admissibility_prefiltered` event per physical step (when the cycle exists and at least one known-inadmissible direction was excluded) logs the directions, destinations, and provenance `action_control.verifier_admissibilite`. This is an *optimization trace*, not a causal discovery, a new safety rule, a preempted risk alert, or a physical visit.

## Prespecified public software gates

Re-run `python -m lab.stage11_geographic_robustness_probe` on the four prior fixed layouts, 6 steps each, plus `python -m lab.stage11_geographic_probe` on the eight-step baseline. Add focused tests to require:

1. In `known_lethal_north`, **zero** `stage11_geographic_planning_unavailable` records resulting from known lethal target planning; at least one prefilter record; **zero** physically perceived known-lethal visits; the reference initial north direction is not offered. At least one other adjacent target must still be eligible in a separate one-target-capacity unit test.
2. For `north_obstacle`, `east_corridor`, and `visible_creature_north`, no prohibited cell visits. Public coverage need not equal historical numbers because elimination of invalid candidates changes competition, but report all changed counts without retrospective target tuning.
3. Unknown (`indeterminate`) safety status remains eligible, and a change in the Action Control safety source is reflected on re-query; no immutable private "blocked cells" cache, no leaked oracle. Two identical runs must produce equal journal hashes and diagnostic results. Snapshot/rollback contracts should remain exact.
4. No extra movement is credited without a fresh physical Perception capture. The geographic mode remains OFF in baseline hydration and Stage9 references. No Stage9 held-out, external experimental seeds, full Golden or independent science review runs are authorized.

**Outcomes will be recorded as they occur, including failures.** Versioned public diagnostic: `stage11-public-frontier-layout-robustness-dev-v3`. Stage11 remains IN_PROGRESS and Stage9 scientific held-out remains NO-GO.
