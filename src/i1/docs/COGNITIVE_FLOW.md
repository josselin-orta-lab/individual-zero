# I1: causal and cognitive flow for one lived world step

This is an architectural reading map, not a claim that every optional producer emits evidence on every cycle.

| Order / responsibility | Implemented in | Subjective data / custody |
| --- | --- | --- |
| Physical world & Scheduler | `runtime/world.py`, `runtime/stage4_runtime.py` | Hidden world truth stays in Lab; Scheduler owns physical step |
| Local capture | `runtime/stage4_runtime.py`, `modules/perception.py` | Adjacent cells, local resources, current body, not complete hazard map |
| Modulation, needs, temperament | `runtime/stage11_runtime.py`, `modules/value_needs.py`, `runtime/i1_birth_temperament.py` | Internal state; pressure, not action instruction |
| Goals, exploration and options | `modules/goal_manager.py`, `modules/exploration.py`, `modules/stage6_planning.py` | Only perceived or genuinely learned affordances |
| Gatekeeper, competition and control | `modules/gatekeeper.py`, `modules/competition.py`, `modules/action_control.py`, `runtime/stage4_runtime.py` | UC-priced possibility, chosen candidate, admission, actual command |
| World effect and experienced outcome | `runtime/world.py`, `runtime/stage4_runtime.py` | Physical effect is ground truth; lived projection is narrower |
| Online learning, agency, memory | `modules/causal_model.py`, `modules/agency_comparator.py`, `modules/memory.py` | Hypotheses and personal observations, not simulator attribution |
| Sleep, consolidation, owner publication | `runtime/stage10_runtime.py`, `runtime/i1_cognitive_publication.py` | Paid private candidate and verified owner-specific form |
| Durable custody or death | `runtime/m11_transactional_mortal.py`, `runtime/sqlite_life_store.py` | Authenticated atomic current generation, no rewind |

## Physical and cognitive sequence

1. **Birth:** `runtime/i1_birth.py` builds the natural `I1Runtime` with bodily, equipment, Stage10/11 and detection contracts. The current build produces `i1lab` as an isolated compatibility namespace, sourced from `src/i1/lab` and `src/i1/runtime`; it is not permission to import I0's Lab.
2. **Capture:** Stage 3 sees local physical state. The operator may see a complete `WorldLayout` and journal; the individual may not. Exposing a global map or latent hazard information constitutes an epistemic defect.
3. **Cycles and phases:** `runtime/stage4_runtime.py::_phase_hooks` schedules modulation, perception, needs, goals, planning, bus, gatekeeper, competition, control and metacognition. Stage11 adds geography/frontier-specific hooks. Verify producers and temporal read barriers in the code for the exact change.
4. **UC:** `runtime/stage4_runtime.py::_charge`, the Scheduler and module budgets charge operations. A skipped/faulted budget event is not free work. No budget-exempt shortcuts for desired behavior.
5. **Action:** Action Control admits a primitive, then WorldBody applies its physical consequence. Planning, predictions and action receipts have different authority.
6. **Feedback:** the full technical journal records what physically occurred; autobiographical projections filter hidden fields. Online learning must use the restricted lived observation.
7. **Sleep and consolidation:** Stage10 processes validated candidates under budgets and publishes to registered causal owners with provenance. Publication counts and nonempty value require separate evidence.
8. **M11 option:** the transactional owner fences the intent, privately computes one step, commits SQLite, and publishes only the canonical generation. On uncertainty it stops; death cannot be undone.

## How to debug a failure to eat

Trace `WorldBody.inventory()` versus physical food `WorldBody.telemetry()`; current local percept and inventory representation; Value/Needs contributions; goal arbitration; Stage6 option generation; Gatekeeper selection; Competition result; Action Control admission; the `manger` transition and its personally observable consequences. Distinguish the absence of an option, rejection of an option, and a correctly chosen alternative. Do not insert a rule `collecter -> manger` to conceal the causal defect.

## Traceability constraint

For any changed component, record: owner, inputs and provenance, outputs, UC charges, timing/phase, effect of death or fault, code entrypoint and distinguishing negative test. If a relation is not instrumented, mark **NOT_OBSERVED**, not "the agent reasoned that...".
