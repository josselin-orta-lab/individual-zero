# I1 natural goal arbitration: 0.04 / 0.35 birth calibration

**Decision (2026-10-18):** engineering adoption for canonical I1 test births, **not** a scientific survival or learning GO. Provenance: [issue #307](https://github.com/josselin-orta-lab/individual-zero/issues/307) and research [PR #308](https://github.com/josselin-orta-lab/individual-zero/pull/308), based on experimental [PR #303](https://github.com/josselin-orta-lab/individual-zero/pull/303). This dedicated PR is based on `main` and does not merge either research branch.

## Concrete owner and effective birth

`src/i1/runtime/i1_birth.py::birth_i1` instantiates `i1_natural_runtime.I1Runtime`. That canonical constructor calls `configure_birth_temperament`, then `_configure_birth_goal_policy(..., "natural-004")` **before** `super().__init__` creates the GoalManager and physical body. Frozen nested Stage11 Stage9→8→7→6→4 holds `goals.replacement_hysteresis=0.04` and `critical_pressure=0.35`; Stage10 receives that exact Stage9 subtree before birth. Both receive versioned policy identifiers. GoalManager receives those values directly through Stage4Runtime. The owner policy is immutable throughout life. `birth_i1_m11` goes through the same natural constructor, preserving the cold-recovery fingerprint.

Reference Stage4/10/11 fixtures are **not** edited: they are software compatibility inputs and remain historical `0.10 / 0.90`. An explicitly named private research constructor option `i1_goal_policy="historical-010"` is available only to controlled counterfactual callers of `I1Runtime`; public `birth_i1` cannot pass it. Never use the historical arm as the canonical default.

## Scope and limitations

This only changes the GoalManager thresholds and versions within canonical natural I1. ValueNeeds pressure, temperament, TD reward, Competition, Action Control, motor commands, physics, memory, consolidation semantics and I0 are unchanged. No emergency actions are scripted. The actor remains mortal; stale or impossible choices may still occur. Small pressure differences below 0.04 retain hysteresis, whereas sufficiently urgent lived need can bypass the refractory threshold at 0.35.

In #307, water/energy at zero had normalized pressures about 0.429922/0.358268 for one temperament, a gap 0.071654 too small for historical 0.10. The new policy permits a goal change in that condition, but this is **not** proof that Competition accepts a drinking option or that the TD learner improves hydration. [Issue #306](https://github.com/josselin-orta-lab/individual-zero/issues/306) independently documents misleading negative rewards for useful drinking under the unchanged absolute-setpoint TD signal. Do not broaden this PR to fix #306.

## Evidence and validation gates

`tests/i1/test_i1_natural_goal_calibration.py` checks real natural births (including Stage4/10/11 equality, lifetime configuration stability), explicit historical controls, physically attainable urgency, anti-chatter and refractory behavior, without postbirth reassignment. Dedicated CI additionally checks natural M11 cold recovery, engine boundaries and the I1 test suite.

**Science remains unconfirmed until fresh matched independent mortal births** in `oasis` (water/resources at birth) and `foraging` (additional decisions), or equivalent registered worlds. Use identical seeds/world physics/TD for both arms, only the birth goal policy differing. Archive complete verifiable WALs; report SHA, identity, seed, world, actual goal config, goal transition pressures, proposals and Competition outcomes, applied drink/eat, physical need trajectories, time at zero, learning Q changes, mortality and oscillation. `NOT_OBSERVED` is the honest value for any missing endpoint. A software PASS is not a scientific GO.
