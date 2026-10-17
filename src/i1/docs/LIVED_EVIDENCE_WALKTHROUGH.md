# Trace one lived event through I1, without an oracle

This is an operator procedure, **not** a scripted action sequence for the individual. Use it on a newly born *current natural I1* under a registered world preset; do not replay dead lives or reactivate historic A2/H1/H2 cohorts.

## Reproducible capture

```bash
python tools/run_i1_world_preset.py --preset foraging --validate-only
python tools/run_i1_world_preset.py --preset foraging --seed 246 --steps 24 --lives 1 --custody wal --output-dir reports/foraging-246
python tools/inspect_i1_world_report.py --report reports/foraging-246/report.json
```

The **third command is illustrative only**: verify the report filename emitted by the runner before executing the inspector, since it requires `--report` and must receive the actual JSON path. The output directory must be new. The runner selects external initial conditions; `seed` governs the reproducible birth identity, not the individual's decisions or the world's hidden information. `--custody m11` selects mutually exclusive transactional persistence.

The external world report currently exposes physical observations and terminal/storage receipts; it explicitly marks `needs_arbitration`, `goal_selection`, `option_competition`, `uc_expenditure`, `first_person_learning`, `stage10_nonempty_publication`, and `subjective_agency` as **NOT_OBSERVED**. Never fill these fields from operator truth or assumptions about the selected action.

## Causal checkpoints and their actual sources

| Checkpoint | Inspect code and allowed evidence | What it can prove |
| --- | --- | --- |
| 1. Physical world before action | `src/i1/runtime/world.py::WorldBody.telemetry`, `capture_local`; the operator report separately records layout/danger | Actual bodily reserve/inventory and limited local opportunity are not identical |
| 2. One perceptual opening | `src/i1/lab/stage3_runtime.py::Stage3Runtime.open_step`, `src/i1/modules/perception.py::SymbolicPerception.capture` | The individual's accessible observation, **not** an omniscient map |
| 3. Need and deferred goal | `src/i1/modules/value_needs.py::ValueAndNeeds.assess`, `produce`; `src/i1/modules/goal_manager.py::GoalManager.defer_proposals`, `arbitrate` | A need pressure or goal proposal, **not** compulsory eating/drinking |
| 4. Proposed option | `src/i1/modules/stage6_planning.py::SimulatorPlanner.propose`, `src/i1/lab/stage6_runtime.py::Stage6Runtime._propose_for_cycle` | One hypothesis about reachable progress, **not** action success |
| 5. Competitive selection | `src/i1/lab/bus.py::InMemoryBus.pour`; `src/i1/modules/gatekeeper.py::Gatekeeper.select`; `src/i1/modules/competition.py::Competition.evaluate` | Separate bus admission, attention selection and choice accumulator |
| 6. Physical command | `src/i1/modules/action_control.py::ActionControl.admit`, `src/i1/runtime/stage4_runtime.py::_dispatch_decision`, `src/i1/runtime/world.py::WorldBody.apply` | Only an applied command changes physical state; failure still consumes a real step |
| 7. Journal and lived projection | `src/i1/runtime/journal.py::HashChainedJournal.append`; `src/i1/runtime/journal_views.py::JournalViews.commit_autobiographical`, `autobiographical` | Technical provenance and *narrower* authorized first-person events |
| 8. Episode and online knowledge | `src/i1/modules/memory.py::EpisodicMemory.ingest_autobiographical`, `src/i1/modules/causal_model.py::CausalModel.ingest_closed_autobiographical_episode` | A potentially closed episode and admitted or withheld hypothesis |
| 9. Sleep/consolidation/publication | `src/i1/runtime/stage10_runtime.py::Stage10Runtime._run_live_consolidation`, `_publish_live_consolidation`; `src/i1/runtime/consolidation_publication.py::Stage10PublicationCoordinator.publish` | Distinguish charge, private candidate, coordinated receipt and **nonempty** owner changes |
| 10. Durability and terminal status | `src/i1/runtime/m11_transactional_mortal.py::M11TransactionalMortal.run_step`, `src/i1/runtime/sqlite_life_store.py::SQLiteLifeLedger.audit` | Only latest committed active generation is cold-recoverable; dead or uncertain is terminal |

Use [DATA_CONTRACTS_AND_CUSTODY.md](DATA_CONTRACTS_AND_CUSTODY.md) to distinguish source representations, [UC_AND_SCHEDULING.md](UC_AND_SCHEDULING.md) for charge refusals and [EVIDENCE_MATRIX.md](EVIDENCE_MATRIX.md) for software-versus-science boundaries.

## One example question: I1 picked berries but did not eat

Start with two **physical** facts: did `collecter` increase berry inventory, and did `manger` ever appear as an **applied** action? If the first occurred and the second did not, investigate whether food deficit reached a Value/Needs proposal, whether a goal became active, whether the candidate was simulated, and whether Competition or Action Control refused it. A plan may remain pending across a fresh capture. No result allows inserting a hard-coded `collecter -> manger` reflex in order to achieve an expected ending.

If `manger` was applied and food did not increase, check the WorldBody primitive (available berry, `BerryEffect.food_gain`, decay, configured limits), not subjective goal formation. If consumption physically succeeded but personal beliefs did not change, cross `JournalViews`, Memory episode closure and owner update gates, respecting missing evidence. **Do not infer a memory update from inventory alone**.

## Designing a new read-only cognitive observer

**OPEN engineering work**, not existing report functionality: obtain the real causal boundary with a read-only snapshot/receipt captured *after* the corresponding authorized phase. Record source/attempt/step, `S_t` version, candidate/admission references, requested and charged UC, lived event refs and owner state hashes before/after. Never pass its measurements into the actor. For M11, the observer must only audit a fully committed current generation or a separately authenticated post-commit receipt; it may not acquire command authority or mutate a private candidate.

Log each missing checkpoint as `NOT_OBSERVED`; `UNVERIFIED` for a present but unvalidated claim; `OPEN` for a missing investigation or test. A passing simulator run is **not** evidence of correct subjective causation.
