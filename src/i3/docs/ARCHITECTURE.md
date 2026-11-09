# I3: Architecture (historical v1 baseline and current handoff)

There are no imports from I0, I1 or I2 (ADR-0001). The bodily transition was
adapted from I2 with recorded provenance (RAI: ADAPT).

| File | Responsibility |
| --- | --- |
| `modules/body.py` | Body laws (physical model v4), vigilance channel, vital currency, vulnerable capacities |
| `modules/world.py` | Separate World: locations, stocks, hidden effects, scheduled changes and local capture |
| `modules/genome.py` | Closed genome, generation zero, bounded mutation and admissibility |
| `modules/mind.py` | Perception, learned effects, map and source-presence beliefs, self-projection, TD values, self-model, Competition, Action Control, learning and sleep replay |
| `runtime/life.py` | Deterministic life with hash-chained original traces |
| `lab/dev_worlds.py` | Development Worlds, not preregistered test Worlds |
| `lab/first_falsifier.py` | Historical preregistered G2 gate |

One step follows: `World.capture()` -> `Mind.decide(capture, allowance)`
-> `World.step(action, cognitive work)` -> `Mind.observe_outcome()`
-> `Mind.prepare_learning()` -> `World.pay_cognition()` ->
`Mind.learn_from_outcome()`. Under body laws v2, the decision is paid before
the motor action, and affordable learning and replay are prepaid in the same
step. No replay is deferred beyond death or the observation horizon. Refer to
[COGNITIVE_FUNDING.md](COGNITIVE_FUNDING.md) for causal order and limitations.

**Current architecture boundary:** P1.3 remains the reference. The Stage-2.1
replay-gate implementation is unadopted and unregistered. ADR-0017 still bars
fresh scientific Worlds; accepted ADR-0019 allows only engineering-cohort
pre-lift transport and rehearsal. See [ACTIVE_SURFACE.md](ACTIVE_SURFACE.md).

Closed Stage-1 candidate implementations moved to
[`archive/stage1/`](../archive/stage1/README.md). Historical opt-in runtime
paths and retained regression tests import that internal compatibility archive.
