# I1 stages, cooperative runtime composition and module interfaces

**Authority:** executable source at the reviewed SHA, `src/i1/engine.json` and the real birth entrypoint. This is a change map, not a new normative Stage contract or a claim that a scientific capability has been demonstrated.

## Read the *actual* runtime, not the Stage numbers as a pipeline

The active entrypoint is `i1lab.i1_natural_runtime.I1Runtime`, created through `src/i1/runtime/i1_birth.py::birth_i1` or `birth_i1_m11`. The transitional builder `scripts/build_i1_fork.py` copies I1-owned Lab files and native overrides into the disposable `i1lab` namespace. Source-of-truth edits belong to `src/i1/`, never to generated output or frozen I0.

```text
I1Runtime
  <- I1WaterPrudentRuntime <- I1WaterLearningRuntime
  <- ExperimentalI1Stage12Runtime <- Stage12Runtime
  <- Stage11SleepRuntime(Stage11Runtime, Stage10Runtime)
  <- shared Stage9Runtime <- Stage8Runtime <- Stage7Runtime
  <- Stage6Runtime <- Stage4Runtime
                                  owns Stage3Runtime
                                       owns Stage2 substrate and WorldBody
```

The diagram shows the *cooperative inheritance and ownership graph*, not a sequence of physical actions. Verify it against `src/i1/runtime/i1_natural_runtime.py`, `src/i1/runtime/i1_d2_runtime.py`, `src/i1/runtime/i1_water_runtime.py`, `src/i1/runtime/i1_active_runtime.py`, `src/i1/lab/stage12_runtime.py` and `src/i1/lab/stage11_sleep_runtime.py`. Stage11 and Stage10 both inherit Stage9, but their cooperative method resolution shares a single lower Stage9 substrate, Scheduler and physical world. **Do not instantiate both and run two steps.**

**Not in this natural-I1 runtime inheritance chain:** `src/i1/lab/stage1_runtime.py::ScriptedStage1Runtime` and `src/i1/lab/stage5_runtime.py::Stage5Runtime` (a separate Stage4 branch). Natural temperament is installed independently by `src/i1/runtime/i1_birth_temperament.py` and `I1Runtime.__init__`; do not patch Stage5 and assume this changes active I1. The presence of an ancestor called `ExperimentalI1Stage12Runtime` does **not** authorize reviving historic H1/H2 actors. The canonical `I1Runtime` fixes its current configuration at birth.

## Stage ownership and the intervention map

| Layer | Executable owner / entrypoints | Inputs, effects and investigation boundary |
| --- | --- | --- |
| Stage 1: scripted research substrate | `src/i1/lab/stage1_runtime.py::ScriptedStage1Runtime` | Scripted scalar-world mechanics for historical component checks. **Not the natural I1 life-loop.** |
| Stage 2: physical dispatch and custody | `src/i1/lab/stage2_runtime.py::ScriptedStage2Runtime.open_step`, `send_admitted_command` | Owns Scheduler, physical `WorldBody`, terminal boundary, journal and command dispatch. Its `_send_mortal_command` has no lethal rewind; operator-only event injection must stay external. |
| Stage 3: first-person capture and admission interface | `src/i1/lab/stage3_runtime.py::Stage3Runtime.open_step`, `attempt_reflex`, `_dispatch` | `WorldBody.capture_local` plus own body telemetry becomes `PerceptualCapture`. `ActionControl` admits or refuses commands. One real capture per ordinary waking step, not an operator map. |
| Stage 4: cognition and scheduling | `src/i1/runtime/stage4_runtime.py::Stage4Runtime.run_step`, `_phase_hooks`, `_charge` | Needs, contributions, goals, `S_t`, bus, Gatekeeper, Competition, Action Control; cognitive UC charged by Scheduler cycle. A registered intention is not an executed command. |
| Stage 5: separate temperament branch | `src/i1/lab/stage5_runtime.py::Stage5Runtime` | Historical Stage4-plus-temperament composition, **not** active natural-I1 inheritance. Check `src/i1/runtime/i1_birth_temperament.py` instead for natural dispositions. |
| Stage 6: simulated planning | `src/i1/lab/stage6_runtime.py::Stage6Runtime._propose_for_cycle`, `src/i1/modules/stage6_planning.py::SimulatorPlanner.propose` | Builds a plan from the *current capture* and `S_t`, invalidates stale partial segments, then registers a candidate. A simulated consequence is not a physical result. |
| Stage 7: autobiographical Memory | `src/i1/lab/stage7_runtime.py::Stage7Runtime._autobiographical_events`, `_phase_hooks` | Uses `JournalViews.autobiographical` with allowed projection policies, closes episodes, checks intentions and may propose recall. Full technical journal is **not** imported as lived memory. |
| Stage 8: value/precision/calibration | `src/i1/lab/stage8_runtime.py::Stage8Runtime._evaluate_competition_cycle`, `_handle_agency_comparison` | Evaluates option evidence, handles comparator-derived verification and closure of kappa. A prediction or confidence score is not verified causal authorship. |
| Stage 9: lived causal modeling | `src/i1/lab/stage9_runtime.py::Stage9Runtime._phase_hooks`, `src/i1/modules/causal_model.py::CausalModel.ingest_closed_autobiographical_episode` | Connects follow-up **perceptible** body state and Memory-closed episodes to causal candidates under epistemic limits. No hidden hazard identity oracle. |
| Stage 10: sleep and paid consolidation | `src/i1/runtime/stage10_runtime.py::Stage10Runtime._run_live_consolidation`, `_publish_live_consolidation`, `src/i1/runtime/consolidation_publication.py::Stage10PublicationCoordinator` | Sleep gating, P-42 paid private candidate, post-cut protection and four-owner publication. Correction #255 prevents early `UnboundLocalError`; **nonempty publication in natural lives remains NOT_OBSERVED** without a live trace. |
| Stage 11: spatial exploration | `src/i1/runtime/stage11_runtime.py::Stage11Runtime._phase_hooks`, `_geographic_frontier_targets` | Spatial/frontier contributions and budget-aware navigation derived from accessible geography. It is combined with Stage10 through `Stage11SleepRuntime`. |
| Stage 12: metacognitive observation and agency | `src/i1/lab/stage12_runtime.py::Stage12Runtime._phase_hooks`, `_dispatch_decision` | Goal-progress, lived attribution diagnostics and occupancy/alerts; these must not rewrite observer truth into self-knowledge. Diagnostics are not an oracle. |
| Active I1 specializations | `src/i1/runtime/i1_natural_runtime.py::I1Runtime`, `src/i1/runtime/i1_water_runtime.py::I1WaterLearningRuntime`, `src/i1/runtime/i1_active_runtime.py::ExperimentalI1Stage12Runtime` | Current temperament, uncertainty-aware affordances, personally learned water/need signals and active consolidated owner views. Inspect the final method override before editing a parent. |

**Important nuance:** `src/i1/lab/stage11_sleep_runtime.py::Stage11SleepRuntime.run_step` guards the unified mortal loop. `src/i1/runtime/stage10_runtime.py::Stage10Runtime.run_step` governs awake-versus-sleep routing beneath that guard. Physical-world advancement is not one transition per cognitive Stage. Under M11, `src/i1/runtime/m11_transactional_mortal.py::M11TransactionalMortal.run_step` is the only authorized outer transaction entrypoint.

## Executable handoffs during a waking step

| Producer → consumer | Data / interface | Ownership or timing rule |
| --- | --- | --- |
| WorldBody → Perception | `WorldBody.capture_local`, `SymbolicPerception.capture`, `PerceptualCapture` | Only locally accessible sensory and own bodily information; global layout, lethal zones and canary remain Lab-only. |
| Perception/Needs/Memory/Exploration/Planning → bus | `Contribution`, `GoalProposal`, `OptionProposal`, `ProducerBuffer`, `InMemoryBus.pour` | Publishing a candidate is not admission; data must satisfy schemas, phase and provenance gates. |
| Bus → Gatekeeper → `S_t` | `Gatekeeper.select`, `CognitiveSpace.publish` | Retains a bounded competitive view and feedback; the currently published `S_t` is a phase boundary, not a fresh hidden-world capture. |
| `S_t`/planner → Competition | `Competition.register`, `evaluate`, `CompetitionCycleResult` | Accumulation and threshold may choose an option; fallback can occur only within the existing controls. |
| Competition → Action Control → WorldBody | `ActionControl.prepare_option_step`, `admit`, `dispatch_prechecked`, `WorldBody.apply` | Refusal or insufficient UC leaves an intention unexecuted; only physical dispatch yields `TransitionResult`. |
| Physical transition → journal → lived projection | `src/i1/runtime/journal_views.py::JournalViews.commit_autobiographical`, `autobiographical` | A technical occurrence may contain hidden fields; autobiographical allowlist is narrower and tied to event, attempt and world step. |
| Lived episode → causal owner | `EpisodicMemory.ingest_autobiographical`, `CausalModel.ingest_closed_autobiographical_episode` | Owner update needs eligible lived evidence, not physical truth from an external evaluator. |
| Sleep evidence → four owners | `Stage10PublicationCoordinator.prepare`, `publish` | Distinguish paid selection, private candidate, rebase, accepted commit and **actual nonempty owner changes**. |
| Full causal state → M11 | `M11TransactionalMortal.run_step`, `SQLiteLifeLedger.audit`, `cold_recover` | Exclusive custody of one current generation; pending intent, corrupted image, mismatch or death forbids opportunistic recovery. |

See [COGNITIVE_FLOW.md](COGNITIVE_FLOW.md) for temporal detail, [UC_AND_SCHEDULING.md](UC_AND_SCHEDULING.md) for P-43 versus P-42 charges and [MORTALITY_AND_M11.md](MORTALITY_AND_M11.md) for terminal custody.

## How to modify an interface safely

1. Confirm natural I1 actually resolves the target override. Compare `I1Runtime` with its parent chain; do **not** infer the active implementation from a historical Stage name.
2. Locate the producer, consumer and owner export/restore functions. List input schema, temporal phase, provenance and cognitive UC (when charged).
3. Preserve first-person filters at `WorldBody.capture_local` and `JournalViews`; do not read `ground_truth` to fill a missing subjective field.
4. Keep Action Control as the only admitted dispatch route, one physical world transition per command, and M11 as exclusive custody when enabled.
5. Add a negative test demonstrating what **cannot** cross the boundary. Positive output alone is insufficient.
6. Run structural, current-I1 smoke/full, M11 and generated-source suites as appropriate. Record exact SHA, observed fields and any `NOT_OBSERVED` gap.

## Scope of proof

Current tests validate specific software paths, not the whole theory. Useful executable anchors are `scripts/test_i1_ci.py` (natural birth, perception, physical physiology, M11-related invariants and adaptive mechanisms), `tests/i1/test_i1_generated_isolation.py` (actual generated ownership), `tests/i1/test_i1_stage10_canonical_publication.py` (the #255 entrypoint and invalid-form deferral), `tests/i1/test_i1_m11_adversarial.py` and `tests/i1/test_i1_natural_m11_cold_recovery.py`. The Stage1/5 sources are historical engineering artifacts, not acceptance oracles for natural I1.

**OPEN / NOT_OBSERVED:** general adaptation across new environments, robust self-maintenance, causally verified distal agency and nonempty retained publication across all owners. A green CI does not turn these into scientific results.
