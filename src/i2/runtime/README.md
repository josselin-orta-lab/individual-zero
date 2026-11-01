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

## Resource scarcity and bounded endpoint interpretation (issue #664)

A zero-resource genesis must **not** open a scripted collect intention absent
from the individual's first-person affordances. The initial intention now
uses COLLECT only when personally offered; otherwise it uses the available
DRINK option. This is a deterministic *researcher-specified initialization*,
not discovered exploration or a new motivational system. Competition, actual
UC debit, veto and action admission remain unchanged. A resource-empty
world is a negative control for food acquisition.

The existing `world_demo` reports a descriptive `endpoint` for each arm
alongside `world_endpoint_contrast`. Preselected endpoints are actual
physical ticks observed, modeled death tick, right-censoring, end energy,
actual UC spent, paid decisions, admitted actions and unfunded windows.
The paired energy delta is only reported when **both** arms have the same
nonterminal tick endpoint. Different death times and unequal exposure
remain separate observed events; no generalized survival advantage or
natural-learning GO can be inferred. Stable/neutral/adverse/reversal retain
their original scripted laws and unchanged policy. No favorable scenario
selection, estimator tuning or repeat of the closed v1-r1 factorial.

For a no-food control or zero-UC terminal demonstration, use the existing
bounded world command with the optional initial resource parameter:

```bash
PYTHONPATH=src python -m i2.runtime.isolated_prototype --world --scenario adverse --ticks 8 --resources 0
PYTHONPATH=src python -m i2.runtime.isolated_prototype --world --scenario neutral --ticks 12 --initial-uc 0 --initial-energy 4
```

This remains an explicitly started, internal synchronous toy world. Local
SQLite replay is not authenticated M11, and nondeath at a bounded horizon
is censored observation, not proof of longevity.

## Exogenous reversal clock, not cognitive attempt count

**Scientific-validity correction (#664):** the food payoff for a physical EAT
action is now indexed by the **committed physical world tick**, not by the
number of cognition events. The previous step-indexed payoff made a subject
which skipped an unaffordable cognitive window encounter a *different world*
at the same physical time. That confounded policy and environment.

Each existing scripted payoff phase covers two physical world ticks (the
existing cognitive-window cadence), with phase 0 through tick 2, phase 1
through tick 4, phase 2 through tick 6 and phase 3 from tick 7 onward.
After the eight-element exogenous script is exhausted, the last defined
payoff persists until the bounded world horizon. This is a **researcher-
specified hidden environment regime**, not a learned rule or a biologically
calibrated duration. Both independent arms receive the identical exogenous
payoff at the same physical tick regardless of whether they have acted or
how many cognitive windows they missed.

The one-owner commit applies the current physical-tick payoff. Its local
replay audit recomputes the same payoff from journaled physical ticks,
rejecting history changes. Diagnostic `exogenous_food_phase` in
`decision_evidence()` and `researcher_only_food_phase` in the world trace
are researcher-facing **after-commit readouts**, never published in the
subject's perception, score or chosen-outcome memory. The unchanged
past-only mechanism can adapt only after a consequence was actually
experienced. The world `reversal` control may now be inspected with:

```bash
PYTHONPATH=src python -m i2.runtime.isolated_prototype --world --scenario reversal --ticks 12
```

The direct, no-physical-tick `demo("reversal")` is refused because it
cannot expose a time-dependent reversal and would yield misleading science.
Existing constant stable/adverse/neutral single-step smokes are unchanged.
Different post-divergence trajectories are still not matched causal
survival evidence, and a programmed avoidance response is not proof of
natural or generalized learning. No frozen G1-LAB data or protocol changes.

## Blind hidden-recovery falsifier (ADR-0008, issue #664)

The frozen seven-case viability study stays untouched. A **separate bounded
negative-to-positive hidden world scenario** is now available in the same
single-owner runtime: food EAT yields -8 at physical phases 0-2 and +6
starting at physical tick 7. Neither the phase, prospective benefit,
researcher output nor the world script is published to cognition. The
individual only sees its own committed body state, affordances, paid scores,
and **previously chosen** consequences. No novelty/revisit bonus or
forced exposure is added.

Run the small source-locked two-world/two-policy diagnostic:

```bash
PYTHONPATH=src python -m i2.runtime.blind_restoration_probe --json
```

It compares hidden restoration to a persistently harmful control with the
same initial food harms, 16-tick world clock, 60 UC, 40 energy, eight
resources, and unchanged observational/fixed policies. Researcher-only
`_subjective_history` compares what the observational subject actually
could experience in both worlds, excluding world-phase/oracle fields.
A postchange EAT counts as **contact** only if selected and committed;
a positive food result becomes *personally available* only in a later
capture. If no EAT contact occurs, hidden recovery is not identifiable,
even when the counterfactual opportunity would have improved survival.

This is intended to preserve an informative **failure to rediscover** as
a negative finding. Do not alter priors, +5 offset, physical laws or UC,
or grant free curiosity to force a successful result. These four tiny
deterministic runs are an engineering/scientific falsifier, not
independent statistical replication, open-ended G2 tuning, living I2 or
authenticated M11. As with the reversal, the direct no-clock
`demo("restoration")` is refused. The original one-shot G1-LAB remains
closed and unchanged.


## Optional survival last-resort experiment (separate policy, #832)

For the new emergency survival priority, explicitly pass `--last-resort`
in an isolated `--world` run. The current SQLite owner stores the
selection at genesis and its replay recomputes which paid candidate
valuations were overridden. The original source-locked blind-restoration
and seven-case probes keep this switch off so their historical claims
do not change through retroactive policy substitution.

```bash
PYTHONPATH=src python -m i2.runtime.isolated_prototype --world --scenario restoration --ticks 16 --last-resort
PYTHONPATH=src python -m i2.runtime.isolated_prototype --world --scenario adverse --ticks 16 --last-resort
```

No second WorldBody, external motor, real M11 attestation, source-oracle,
free UC, or scientific promotion is implied. If a safer known plan is
added in future, the current fixed toy affordance classifier must be
replaced by an explicit source-bound viability comparison before claiming
the berry is genuinely the last resort.
