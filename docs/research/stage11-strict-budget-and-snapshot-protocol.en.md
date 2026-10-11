# Stage 11: strict UC degradation, frontier suspension and canonical snapshot restoration

**Predeclared software-development protocol, 11 October 2026.** This is NOT an independent scientific/held-out campaign. The normative source remains `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, especially §9.4, §14, §16.3 (DC-07) and §17 (snapshots and replay). Stage 9 scientific held-out remains NO-GO.

## Problem and separation of claims

The existing Stage11 tests show v4 demand-driven early Action Control checks save logical UC when there is no local frontier. They have not yet demonstrated failure-closed behavior when **Planning's versioned per-module UC envelope is exhausted**. The Phase-1 Exploration owner may freeze an offered target before the Planning preflight or plan-construction charge is rejected. In a genuinely constrained/degraded cognitive cycle an unfunded proposal must not survive as an *active offered target* to collect intrinsic credit.

This protocol adds an explicit **suspension of geographical offers only after real budget refusal**, recorded distinctly from an absence of novelty or a safety prohibition. It does not modify the true physical visit ledger, the final Action Control veto, the immutable safety policy, the α/κ calibration, or historical Stage9 files.

## Four declared public logical-budget settings

Same public reference world, Equipment, Perception and needs-satisfied body (energy 50, food 60, water 60, integrity 100), geographic exploration ON and v4 demand-preflight ON. Run **3 physical world steps** for each independently instantiated runtime, with fixed, versioned P-43 configurations:

- `planning_0`: Planning envelope 0 UC. Its 1-UC preflight must be **rejected**, no geographic option may be registered or applied, and no denied budget charge is treated as an actual consumed UC.
- `planning_1`: Planning envelope 1 UC. First preflight can succeed but a `planning_build` (2 UC) must be **rejected** when a real frontier is present. Again no geographic option may be applied, and offered targets must be suspended once the shortage is reported.
- `planning_3`: Planning envelope 3 UC. Both charges are affordable for one candidate in the public reference; do not require a move to occur unless its usual Competition and Action Control paths actually accept it.
- `exploration_0`: Exploration owner envelope 0 UC and the normal Planning envelope. The `exploration_observe` charge must be rejected without pretending that Exploration registered new targets; physically captured locations nevertheless remain real visits because Perception/World integrity does not degrade.

All these world/cognition settings are public development fixtures, not hidden worlds or scientific parameter calibration. Charge logs must record accepted and rejected UC separately, and each incomplete-target report must name the precise **budget** operation, never “unsafe”, “no novelty”, or a fabricated model prediction.

## Canonical source and snapshot checks

A separate isolated **unit-test-only** reversible DC-05 safety-state exercise uses a Causal Model's published `lethal_zone` safety fact and its read-only `CanonicalSafetyFacts` adapter. The synthetic objects used to drive that test are **unit test inputs**, NOT lived evidence, scientific results, or an assertion that the public WorldPhysics actually inflicted harm. The same `ActionControl.verifier_admissibilite` consulted by Stage11 must reflect a fact promoted into the *canonical model* and then reflect the **restored snapshot state** without a cached “forbidden cells” table in Exploration. Restore through the actual SnapshotManager over all causal owners where supported; verify hash and owner-state equality and do not imply that the append-only journal is rewound.

## Regression gates

- No budget-related missing result becomes zero danger, confirmed absence of novelty, “safe”, or an intrinsic reward.
- Already-visited and fully blocked frontiers continue to be distinguished from budget-deferred ones.
- Final Action Control veto remains live and all performed actions are ordinary legitimate dispatches.
- No unobserved arrival is credited to geographical novelty; complete physical captures remain accounted even in degraded cycles.
- Two identical runs must be exactly deterministic, including journal and owner state.
- **Known limitation to record honestly:** the read-only pre-phase early safety lookup currently runs before the Planning budget charge. This protocol does not prove exact per-operation timing compliance and does not permit the absence of budget to authorize an action. A later architectural gate may have to move the consultation while preserving Phase-1 owner boundaries.

Status pending run: **NOT VALIDATED**. No full Golden, multi-Python, Stage9 held-out or scientific GO from these fixtures.
