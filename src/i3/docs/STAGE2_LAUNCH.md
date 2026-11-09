# Stage 2 launch: decide how much to think

Issue #1062. Baseline: `350ee52` (#1211). Reference: P1.3, retained by the
ADR-0018 negative closure of Stage 1. The ADR-0017 moratorium is active.

**OWNER-APPROVED LAUNCH.** It opens no World and adds no life or runtime
change. It records pre-design measurements, fixes the order of work and freezes
the first slice by this merge.

## Stage-2 rule (DEVELOPMENT_PLAN)

Another computation runs only when its expected viability gain exceeds its cost,
both expressed through the same distress function D and subject to physical
funding. `n_base` and `h_max` become ceilings. Replay is a priced computation.
Metareasoning is itself paid and bounded.

The comparison is against a fixed budget, with a zero-cost control and an
equal-mean random-budget control. Any matching mean comes from development,
never from validation. There is no free evaluator.

## Pre-design measurements (disclosed, not results)

**1. Where P1.3's cognition is spent.** These are read-only reductions of the
12 already-archived P1.3 lives of 56/57: 2,806 lived steps, 0.531 energy and
0.660 vigilance per step.

| Component | Energy / step | Vigilance / step | Share (E / V) |
| --- | ---: | ---: | --- |
| Decision: simulated steps (79.6 per decision) | 0.159 | 0.159 | 30% / 24% |
| Decision: cycles (4.3 per decision) | 0.087 | 0.217 | 16% / 33% |
| Decision: memory service (254 items) | 0.051 | 0 | 10% / 0% |
| Sleep replay (4.3 replays per lived step) | ≈ 0.16 | ≈ 0.18 | ≈ 30% / 27% |
| Base learning update (0.78 per step) | ≈ 0.07 | ≈ 0.10 | ≈ 14% / 15% |

The replay and learning rows are derived from the paid totals and the replay
tariff, so they are approximate.

**2. Replay is expensive and has shown no measured benefit.** In P5a (1,152
lives), discarding replay's persistent effect left survival at 119/288, against
112/288 for normal P1.3. That replay was still computed and paid. No study has
tested not paying for it.

**3. Projection precision does not change P1.3's choices on the probed
states.** In a sandbox, P1.3's `chunk_end` scores were compared with the #1155
per-step Decimal oracle on the same P1.3 scoring:

- 126 states: food, water or integrity at 5, 10, 15, 20, 30, 40 or 50 (others
  at 80), water perceived here or a frontier, `h_max` 4, 8 or 12, drinking
  personally known;
- result: **0/126 different top options.**

Candidate-J was precision-sensitive because inherited hope set its margins near
the decision boundary. P1.3's margins are not. The question "when is precise
projection worth its cost" is therefore expected to be degenerate for the
current reference and is deferred. This amends the first-question wording of
the plan.

## Two tracks

**Science track, software now and lived after the lift.**

| Slice | One targeted change | Why this order |
| --- | --- | --- |
| **2.1 Replay gate** | Each sleep replay runs only if its expected gain in D exceeds its D-cost | Largest cost with no measured benefit |
| 2.2 Deliberation ceiling | Competition cycles stop when another cycle is not worth its D-cost | Cycles take a third of vigilance |
| 2.3 Simulation depth | Horizon below `h_max` when deeper simulation is not worth it | Simulation takes 30% of energy |
| deferred | Precision on demand | Degenerate for P1.3 on probed states |

The first slice's frozen protocol is
[STAGE2_REPLAY_GATE.md](STAGE2_REPLAY_GATE.md).

**Engineering track, required before any Stage-2 lived panel (ADR-0017
lift).**

1. A two-phase G/R executor, with all-lives-first generation, a sealed
   manifest, `REDUCTION_DEFECT_PENDING_REPAIR` and blind repair, plus tests.
2. The `engineering` cohort, disjoint from the four existing ones, with guards
   so that it is never admissible as evidence.
3. One parameterized runner instead of copied pilot runners.
4. A sealed rehearsal workflow that publishes only pipeline status, digests,
   invariants and time per step.
5. The owner's lift entry in `STATUS.md`.

Without this track, Stage 2 can produce only software evidence.

## Appendix: projection-precision probe (sandbox)

```python
from i3.modules.mind import Mind
from i3.modules.genome import midpoint, SCHEMA
from i3.modules.body import CognitiveBudget, BodyLaws
from i3.lab import projection_end_to_end_numeric_oracle as O

PRIME = ((("se_deplacer",), (-2., -.2, -.4, 0., 0.)), (("attendre",), (-.35, -.2, -.4, .2, 0.)),
         (("dormir",), (3., -.35, -.4, 0., 4.)), (("boire",), (-.5, -.2, 35., 0., 0.)))

class Oracle(Mind):
    def simulate(self, body, plan, horizon, budget):
        self._observer_first_forecast = None
        return O.simulate_end_to_end(self, body, plan, horizon, budget)

def mk(cls, h):
    m = cls({"schema": SCHEMA, "genes": dict(midpoint()["genes"], h_max=h)}, 211,
            observer_decision_diagnostics=True)
    m.map = {}
    for k, d in PRIME:
        m.effects.observe(k, d)
    m._drift = m.drift()
    return m

def top(m, cap):
    info = m.decide(cap, CognitiveBudget(cap["body"], BodyLaws()))[3]
    sc = sorted(((w["total_score"], w["option"]) for w in info["observer"]["score_witness"]),
                reverse=True)
    return sc[0][1] if len(sc) == 1 or sc[0][0] - sc[1][0] > 1e-12 else None

# For here in {(True, ()), (False, ())}, channel in {food, water, integrity},
# level in {5, 10, 15, 20, 30, 40, 50}, h in {4, 8, 12}:
#   compare top(mk(Mind, h), cap) with top(mk(Oracle, h), cap)  ->  0 / 126 differ
```
