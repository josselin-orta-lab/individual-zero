# I1: needs, options and physical actions

**Authority:** explanatory mapping of current source, not a command to the individual. All results below must be verified with current software tests or new living evidence.

## Separate the variables

- **Physical state:** `runtime/world.py` owns energy, food, water, integrity, inventory and the effects of each physical command. Food carried in inventory and the bodily food reserve are different quantities.
- **Internal motivation:** `modules/value_needs.py::ValueAndNeeds.assess` processes bodily telemetry into a NeedState; `produce` contributes within the cognitive cycle. The contribution is information, not a compulsory command.
- **Temperament:** `runtime/i1_birth_temperament.py` configures the newborn's dispositions. These parameters should influence subjective arbitration without encoding privileged world facts.
- **Goal and options:** `modules/goal_manager.py`, `modules/stage6_planning.py`, `modules/exploration.py` generate and arbitrate hypotheses about possible goals and acts.
- **Decision and execution:** `modules/gatekeeper.py`, `modules/competition.py`, `modules/action_control.py` and `runtime/stage4_runtime.py` establish admission and dispatch; the world determines actual effects.

## Diagnostic cases

| External symptom | What to measure | What it does NOT establish |
| --- | --- | --- |
| Inventory increased but hunger persists | Physical inventory before/after, body food before/after | A failure of collection or an obligation to eat immediately |
| Water declines continuously | WorldBody dynamics, observable body telemetry, thirst pressure | That drinking is visible/available, or selected |
| An option to eat is absent | Local affordance, current knowledge and goal contributions | That the actor already knows food is edible |
| An option is offered but rejected | Gatekeeper, competing proposals, UC admission and temperament | That the organism is broken or must be forced |
| An action executes but has no intended effect | Admitted primitive, physical event and autobiographical projection | A guarantee of subjective causal understanding |
| Death follows inadequate self-maintenance | True terminal state, last journal and exposure history | A software fault unless an invariant was violated |

## Experiment design

Use `oasis`, `foraging`, `dry-valley` and `empty-land` from [WORLD_PRESETS.md](WORLD_PRESETS.md). Hold model SHA and birth conditions fixed when varying only the physical layout. Record separate trajectories for needs, inventory, candidate options, admitted commands, actual outcomes and UC. The existing preset report may **not** contain all cognitive fields; label them NOT_OBSERVED rather than inferring them from a movement or resource counter.

**Do not** append `collecter → manger` or `soif → boire` rules, or inject an edible-resource oracle. A plausible death under ignorance is an outcome, not justification for removing mortality.
