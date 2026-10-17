# I1 evidence matrix

**Status taxonomy**

- **DESIGN:** motivating theoretical hypothesis, not observed evidence.
- **IMPLEMENTED:** code exists in the current I1 engine, with specified tests.
- **SOFTWARE_TESTED:** a described invariant was checked by tests on an exact SHA.
- **BEHAVIOR_OBSERVED:** measured in a specific fresh mortal life, with trace/seed.
- **SCIENTIFICALLY_ESTABLISHED:** preregistered independent replication and challenge completed. None asserted here.
- **OPEN / NOT_OBSERVED:** evidence is missing or inconclusive, never assumed success.

| Capability or constraint | Current assessment | Traceable code / test | Boundary of conclusion |
| --- | --- | --- | --- |
| Physical food/water decay and mortality | IMPLEMENTED; covered by software tests | `runtime/world.py`, `runtime/i1_natural_sleep.py`, `scripts/test_i1_ci.py` | Does not prove learning to feed or survival |
| Needs, temperament and autonomous option selection | IMPLEMENTED | `modules/value_needs.py`, `runtime/i1_birth_temperament.py`, `modules/competition.py` | No forced optimal survival behavior |
| First-person locality and oracle isolation | IMPLEMENTED; source/CI gates | `runtime/world.py`, `runtime/journal_views.py`, `tests/i1/test_i1_generated_isolation.py` | Does not prove no leak from every future integration |
| Goal progress and subjective agency | IMPLEMENTED with epistemic limits | `modules/stage12_goal_agency.py`, `runtime/i1_natural_runtime.py` | Distal causal responsibility remains unproven |
| UC accounting and genuine cognition | IMPLEMENTED; smoke/full software suite | `runtime/stage4_runtime.py`, `modules/competition.py` | Budget green is not learning quality |
| Episodic learning and lived outcome | IMPLEMENTED; prospective strength OPEN | `modules/memory.py`, `modules/causal_model.py`, `modules/td_values.py` | Correct prediction != verified causal attribution |
| Nonempty four-owner Stage10 publication | OPEN / NOT_OBSERVED as scientific result | `runtime/stage10_runtime.py`, `runtime/i1_cognitive_publication.py` | Needs real private candidates, provenance, replay and cold checks |
| Authenticated M11 custody and terminal refusal | IMPLEMENTED; SOFTWARE_TESTED on recorded CI SHAs | `runtime/m11_transactional_mortal.py`, `tests/i1/test_i1_m11_adversarial.py`, `tests/i1/test_i1_natural_m11_cold_recovery.py` | Cannot recover uncertain or dead living states |
| Six preregistered preset environments | IMPLEMENTED; two brief software births tested | `lab/world_presets/`, `tools/run_i1_world_preset.py` | Not behavioral calibration or scientific GO |
| Generalized adaptive self-maintenance | OPEN / NOT_OBSERVED | Needs future runs over independent worlds | Cannot claim from short preset smokes |
| Consciousness | NOT_ESTABLISHED | No qualifying criterion/evidence provided | No assertion permitted |

## Evidence submission contract

For each meaningful claim record the exact Git HEAD, contract and world digest, birth identity, physics step sequence, UC and journal evidence, relevant observer fields, code path, counter-example and alternative explanations. Label the distinction between **software correctness**, **observed behavior**, **causal interpretation** and **scientific acceptance**.

Do not elevate former A2.38/A2.39/H1/H2 studies or experiments built on broken model versions to natural I1 normative evidence. Those files remain historical only. The authoritative *current* status is [STATUS.md](STATUS.md) plus real CI and reproducible new observations, never a copied assertion.

## Detailed mechanism guides

Consult [NEEDS_AND_ACTION.md](NEEDS_AND_ACTION.md), [MEMORY_AND_LEARNING.md](MEMORY_AND_LEARNING.md), [CONSOLIDATION_AND_PUBLICATION.md](CONSOLIDATION_AND_PUBLICATION.md), [MORTALITY_AND_M11.md](MORTALITY_AND_M11.md) and [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md). These explain what to measure and what remains unproven; none changes the scientific gate.

## Executable traceability for agent interventions (source-inspected)

The rows below map a theory or rule to the **current implemented interface**, a distinguishing software test and the still-missing scientific evidence. Paths in `runtime/` and `modules/` refer to `src/i1/`; all tests are repository-root paths. Test references are entrypoints, **not** claims that each row has been independently demonstrated in a prospective living-world experiment.

| Mechanism / theory | Executable function or interface | Invariant and matching test | Current evidence limit |
| --- | --- | --- | --- |
| Situated perception, incomplete world information | `runtime/world.py::WorldBody.capture_local`, `modules/perception.py::SymbolicPerception.capture`, `lab/stage3_runtime.py::Stage3Runtime.open_step` | No global hazard/Oracle fields in local capture; `scripts/test_i1_ci.py::CurrentI1.test_local_perception_excludes_hidden_truth` | IMPLEMENTED / SOFTWARE_TESTED on a recorded CI SHA; total future integration leak freedom OPEN |
| Physical metabolic cost, mortal existence | `runtime/world.py::WorldBody._body_after_continuous_dynamics`, `WorldBody.apply` | Food and water decline per transition; fatal integrity cannot authorize another living step; `scripts/test_i1_ci.py::CurrentI1.test_deprivation_has_real_physical_cost` and `test_terminal_death_cannot_resume_or_rewind` | Physical software mechanisms tested; adaptive survival NOT_OBSERVED |
| Needs generate motive, not obligation | `modules/value_needs.py::ValueAndNeeds.assess`, `produce`; `modules/goal_manager.py::GoalManager.arbitrate` | Pressure depends on accessible own body telemetry and explicit thresholds; `scripts/test_i1_ci.py::CurrentI1.test_complete_natural_architecture_is_enabled` checks installed modules, **not** every need-to-goal transition | IMPLEMENTED; cross-world causal motivation OPEN |
| Candidate planning, selection and act | `modules/stage6_planning.py::SimulatorPlanner.propose`, `modules/competition.py::Competition.evaluate`, `modules/action_control.py::ActionControl.admit` | A simulated plan cannot bypass admission; `scripts/test_i1_ci.py::CurrentI1.test_real_steps_and_wal` covers the end-to-end natural step, not exhaustive option rejection | IMPLEMENTED / partial software coverage; intention attribution NOT_OBSERVED |
| First-person autobiography and causal uncertainty | `runtime/journal_views.py::JournalViews.commit_autobiographical`, `modules/memory.py::EpisodicMemory.ingest_autobiographical`, `modules/causal_model.py::CausalModel.ingest_closed_autobiographical_episode` | Only authorized projections are eligible, not operator truth; `scripts/test_i1_ci.py::CurrentI1.test_uncertainty_is_not_hidden_safety_knowledge` provides a narrow negative guard | Mechanisms implemented; durable knowledge acquisition under new worlds OPEN |
| UC is finite and auditable | `lab/compute_budget.py::CycleComputeBudget.charge`, `runtime/stage4_runtime.py::Stage4Runtime._charge`, `modules/consolidation_budget.py::ConsolidationWorkBudget.charge` | P-43 waking budget and P-42 sleep work separate; `scripts/test_i1_ci.py::CurrentI1.test_active_modules_participate_in_real_step` covers active modules, not full quantitative UC calibration | Budget mechanisms IMPLEMENTED; cognition-quality inference not licensed |
| Stage10's safe four-owner software boundary | `runtime/stage10_runtime.py::Stage10Runtime._publish_live_consolidation`, `runtime/consolidation_publication.py::Stage10PublicationCoordinator.prepare`, `publish` | Canonical owner selection before use, invalid forms deferred; `tests/i1/test_i1_stage10_canonical_publication.py` is a targeted regression for issue #255 | Software entrypoint corrected and CI-tested at the exact recorded commit; genuine nonempty multi-owner lifelong publication OPEN / NOT_OBSERVED |
| Authenticated M11 persistence without resurrection | `runtime/m11_transactional_mortal.py::M11TransactionalMortal.cold_recover`, `runtime/sqlite_life_store.py::SQLiteLifeLedger.audit` | Identity, chain, owner roster, pending intent and terminal refusal; `tests/i1/test_i1_m11_adversarial.py` and `tests/i1/test_i1_natural_m11_cold_recovery.py` | SOFTWARE_TESTED for exercised fixtures; arbitrary unseen corruption remains beyond test scope |

When documenting a new mechanism, supply **the precise function + the exact test assertion + current SHA + observed data**. A test that only checks constructor wiring cannot be relabelled as proof that an individual learned or made a sound decision. If a required intermediate trace is absent, tag **NOT_OBSERVED**, not `PASS`.

See [STAGES_AND_INTERFACES.md](STAGES_AND_INTERFACES.md) for the runtime method-resolution graph and [DEVELOPMENT_PLAYBOOK.md](DEVELOPMENT_PLAYBOOK.md) for investigation recipes.
