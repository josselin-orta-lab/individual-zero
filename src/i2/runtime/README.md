# Isolated I2 prototype (ADR-0008, issue #664)

This is an **internal executable research prototype**, not an active registered
generation, independently authenticated M11, external robot or claim of natural
learning. The existing I2 v5 cognition owner persists a local WorldBody,
inventory, selected internal effect, action admission reference and paid UC in
**one SQLite COMMIT**. Competition and Action Control remain the same I2
modules. The in-transaction hook is private to this bounded prototype.

Run: `PYTHONPATH=src python -m i2.runtime.isolated_prototype --scenario adverse --steps 6`.

The executable runner creates two new independently identified, disposable
SQLite files with equal initial UC and world laws: observed-chosen valuation
and a fixed-prior no-learning ablation. Six (maximum eight) captures are
bounded and every paid choice, no-offer, veto, abstention, energy change,
termination and prior observation is auditable. Fixed priors and the
observational +5 score are **researcher-assigned comparator semantics**, not
natural motivation. Run results are engineering smoke evidence only, not
confirmatory G4/G5 cohorts or the closed G1-LAB v1-r1 study.

Internal admission is explicitly persisted after a fresh non-vetoed paid
Action Control review and bound to the cognitive event head. External motor
authority is always NONE. Only the **next** subjective capture can refer to
the last committed chosen physical consequence. Local replay checks both
world and cognition state, energy, inventory, actual UC and event provenance.
A modeled terminal prevents further cognition. `before_commit` rolls back
both world and UC; `after_commit` ambiguity permanently halts this in-process
executor. Cold open is **inspection-only**, never recovery.

No independently authenticated, non-equivocating external M11 witness,
cross-domain anti-rollback guarantee or physical robot effect exists. This
mechanism is not qualified for live engine registration or external action.
Retain I1 as active; do not rerun or tune the closed v1-r1 16-arm study.

## Auditable first-person decision contrasts

`demo` also publishes `arms[*].decisions` and `behavioral_contrast`.
The readout is **researcher-only**, generated from an audited, already
committed local journal. It never becomes an additional sensory input.
Each decision includes the exact prechoice energy/inventory/resources,
offered actions, paid scores, personally observed older outcomes, outcomes
actually used by the valuation, UC and eventual selected physical effect.
No future impulse or unchosen-world outcome is available to cognition.

The first action divergence can be called a **matched programmed valuation
contrast** only if the prehistory, state, affordances, experience and UC
match, and the *existing researcher-written scores* explain the choice.
In the eight-capture toy world this commonly exposes adverse fourth-capture
avoidance versus a fixed prior, while the stable scenario shows no
action divergence over a short horizon. Neither is natural intelligence,
generalization, a survival benefit or a confirmatory scientific result.
After the first divergence, later rewards and mortality are **unmatched**
trajectories, not a causal contrast of equivalent worlds.

Use the single existing command to inspect without launching new cohorts:

```bash
PYTHONPATH=src python -m i2.runtime.isolated_prototype --scenario adverse --steps 6
```

A neutral payoff may induce an abstaining score tie. Preserve that null/negative
outcome rather than adjusting the scores or claiming it is adaptive.

## Owner-controlled physical time (prototype only)

The prototype now exposes `advance_physics()`: one **explicitly scheduled**
body-metabolism tick with energy -1, in the same SQLite world owner,
without cognition, an action or UC consumption. It keeps running if the
cognitive budget is zero. Every tick is transactionally journaled and
replayed alongside the existing cognitive events, and terminal energy=0
absorbs all subsequent cognition and physical ticks.

A future cognitive capture sees only the *committed post-tick body energy*.
It cannot see future tick sequences, world impulses, unchosen outcomes or
new researcher-only decision diagnostics. Before-COMMIT failures roll back;
after-COMMIT ambiguity halts further in-process operation. Cold-open remains
inspection only. Neither this manual clock nor SQLite is a real-time
Scheduler, independent M11 witness or authenticated irreversible life.

## Bounded world-owned cadence (internal research runner, #664)

The existing I2 SQLite owner now offers `run_world(ticks=...)` and a
reproducible paired smoke command:

```bash
PYTHONPATH=src python -m i2.runtime.isolated_prototype --world --scenario adverse --ticks 8
PYTHONPATH=src python -m i2.runtime.isolated_prototype --world --scenario stable --ticks 12 --initial-uc 0
```

Unlike calls to `step()` or individual `advance_physics()` invocations,
**one bounded runner invocation** advances physical time without asking the
experimenter what to do each tick. The *same* existing SQLite WorldBody ticks
once every world interval, losing 1 energy even if cognition cannot run.
Every **second** committed physical tick offers a normal I2 cognitive window
if a valid intention remains, the cognitive horizon is not exhausted, and
the existing I2 UC prices can cover the entire offered candidate batch plus
safety review. Cognition chooses (or abstains) inside the usual paid
Competition and admission path; no external action is prescribed.

The UC reservation is conservative: with too few available units the world
records `COGNITION_UNFUNDED` and continues its body clock without free
partial cognition. The runner reports physical ticks and skipped windows,
selected actions, actual UC and modeled death. Split, same-process calls
continue from committed tick counts rather than restarting their cadence.
The whole prototype is capped at **32 physical ticks**. If alive at that
boundary it reports `RESEARCH_HORIZON_CENSORED`, not survival, fitness or
immortality; postterminal action remains prohibited. The prototype's direct
tick/step methods are still present for fault-injection tests, so this is not
a cryptographically enforced scheduler or an independently timed process.

The two disposable arms in `world_demo` have matched initial UC, world laws
and built-in schedule but distinct fresh identities. The first behavioral
divergence is diagnostic only and later mismatched trajectories cannot
establish a causal survival benefit. All dynamics remain **synchronous,
in-process and researcher-triggered to start**, not a separate background
thread, autonomous wall-clock metabolism, authenticated M11 or living I2
engine. No settings or coefficients were tuned from this comparison; the
previous one-shot v1-r1 experiment remains closed.
