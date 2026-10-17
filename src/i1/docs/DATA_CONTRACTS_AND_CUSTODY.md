# I1 data contracts, causal ownership and durable custody

**Audience:** an engineer or autonomous agent changing natural I1. **Basis:** executable source in `src/i1/`, the active generation contract `src/i1/engine.json`, and the current PR #254. This is a map of existing representations, not a new behavioral requirement.

## Keep six layers apart

| Layer | Authoritative owner and read/write interface | What it is not |
| --- | --- | --- |
| World reality | `src/i1/runtime/world.py::WorldBody.apply`, `capture_local`, `telemetry` | Not an individual's global knowledge: `ground_truth` and operator frames are never inputs to cognition |
| First-person capture | `src/i1/lab/stage3_runtime.py::Stage3Runtime.open_step` → `src/i1/modules/perception.py::SymbolicPerception.capture` / `PerceptualCapture` | Not the whole world, not an independently commanded second observation |
| Transient cognitive proposals | `src/i1/contracts.py::Contribution`, `GoalProposal`, `OptionProposal`, `Plan`; `src/i1/lab/bus.py::ProducerBuffer`, `InMemoryBus.pour` | Not an applied command or an authenticated durable generation |
| Published cognitive working view | `src/i1/contracts.py::STVersion`, `src/i1/modules/cognitive_space.py::CognitiveSpace.publish` | Not another autonomous owner or evidence that the individual selected the globally optimal option |
| Journal and first-person autobiography | `src/i1/runtime/journal.py::HashChainedJournal`; restricted `src/i1/runtime/journal_views.py::JournalViews.autobiographical` | An append-only technical record is not automatically a lived memory |
| Durable cognitive owners | `src/i1/runtime/stage4_runtime.py::Stage4Runtime.causal_owners` and cooperative overrides; Stage10 `SlowHistory`; optional M11 `M11TransactionalMortal` | Not an opportunistic rewind or a mechanism that revives dead individuals |

### Working-data schema and admission

`src/i1/contracts.py` defines data-only types: `GoalProposal` contains source, pressure, temporal coordinates and `justification_ref`; `Contribution` includes emitter, signal family, confidence, urgency, risk, value, production time/cycle, expiry, payload and provenance; `OptionProposal` pairs a proposed `Option` with a possible `Plan`; `STVersion` separates `fixed`, `competitive`, `requests` and `diff`. A proposal's presence does **not** show that its referenced event was authentic, that it passed the Gatekeeper or that the physical world changed.

`src/i1/lab/contracts.py::SchemaRegistry.validate_message` checks the declared major schema version, required fields and unknown causal fields, and strips explicitly ignorable noncausal fields. `src/i1/lab/bus.py::InMemoryBus.pour` is the message-admission boundary. `src/i1/modules/gatekeeper.py::Gatekeeper.select` selects contributions, after which `CognitiveSpace.publish` versions `S_t`; `src/i1/runtime/stage4_runtime.py::_phase_hooks` orchestrates these phases. Never bypass the bus/schema path by writing a hypothetical insight directly into `S_t`.

**Temporal warning:** an `STVersion` at cycle N is not a fresh perception for every downstream consumer. `Stage4Runtime.run_step` freezes `goal_for_planning` and `st_before_cycle` before the Scheduler runs that cycle. Check these barriers when a goal is proposed but not planned until a later cycle.

### Technical occurrence versus authorized experience

`HashChainedJournal` stores `JournalEntry(index, event_id, previous_hash, event_hash, causal_event)` as an append-only SHA-256 chain. `append` computes canonical causal bytes. `entries_since` and `get` are technical inspection paths and do not confer first-person knowledge. `HashChainedJournal.audit_durable_wal` audits an independent WAL file offline; it does **not** return a runnable individual.

`JournalViews.commit_autobiographical` verifies that each source `event_ref` exists, belongs to the same `attempt_ref` and `t_monde`, has an allowed kind and passes `AutobiographicalPolicy.project` (including nested field restrictions). It records `AutoSegmentCommit(event_id, t_monde, attempt_ref, event_refs, filter_version)`. `JournalViews.autobiographical` supplies the bounded approved projection to Memory. `src/i1/modules/memory.py::EpisodicMemory.ingest_autobiographical` deduplicates event identifiers, closes bounded episodes and retains their `event_refs`, goal and body context. Technical logging alone never makes hidden hazard coordinates or an operator canary learnable.

## Persistent slow history, active forms and owner identity

`src/i1/runtime/consolidation_publication.py::SlowHistory` owns one `stage10-history-v1` snapshot: `schema`, `current_version`, `current_state`, `lineage`. Lineage records source/new versions, consolidation identity, cut, batch/candidate digests and journal commit index. `committed_episode_refs` are deduplicated source references. A version increment by itself is not evidence of a useful cognitive effect.

`Stage10PublicationCoordinator.REQUIRED` uses **publication keys** `value_needs`, `causal_model`, `perception`, `metacognition_health`. In contrast, the canonical registered Value/Needs owner has **owner_id** `value_and_needs` in `src/i1/engine.json`. `src/i1/runtime/stage10_runtime.py::_Stage10ValueNeedsPublicationView` adapts that owner to the publication key; **do not create a second Value/Needs owner** or rename the published roster to resolve the difference.

Natural I1's `src/i1/runtime/i1_active_value_needs.py::I1ActiveValueNeeds` adds observed procedures without becoming an independent command or safety authority. Other owners have `src/i1/runtime/i1_cognitive_publication.py::ActiveConsolidatedOwner` wrappers containing `schema`, `owner_id`, `canonical_owner`, and `observed_consolidated`. The wrapper's normal `restore_causal_state` requires byte-equivalent canonical online state: a consolidation may add validated advisory observations, **not rewind prior online learning**. The M11-only `install_m11_cold_state` requires an authenticated one-time capability; it is not a live rewind interface.

The three non-Value/Needs advisory row families are explicitly validated in `src/i1/runtime/i1_cognitive_publication.py::validate_owner_rows`:
- `causal_model`: bounded `hypothese_causale` associations with source episode/event references and `validated_for_safety=false`;
- `perception`: authorized `world_transition_experienced` projection, status `observed_not_verified`;
- `metacognition_health`: authorized `agency_comparison` projection with the same unverified status.

For Value/Needs, `I1ActiveValueNeeds.prepare_stage10_advisory_rebase` checks the `compiled_private` procedural source and preserves current online TD. For the other three, `ActiveConsolidatedOwner.prepare_stage10_owner_rebase` recomputes candidates and validates approved post-cut update kinds. The publisher refuses new writes if the frozen journal slice or owner baselines changed. **Publication accepted**, **nonempty rows changed**, and **measured behavioral learning** require *three different pieces of evidence*.

## M11 image and recovery: a single current generation

`src/i1/lab/sqlite_current_envelope.py::registered_current_metadata` validates the versioned current image (`custody_schema`, `individual_id`, sorted `owner_ids`, `owners`, `owner_roster_hash`, `rng_owner_ids`, `journal`, `lifecycle`, `world`, `scheduler`). `src/i1/runtime/m11_transactional_mortal.py::_runtime_image` adds checked `runtime_local` metadata including a constructor-contract digest, journal sequence counters and the stored owner view. `_verify_i1_active_publication_custody` cross-checks committed private forms against the actual active owners before a generation can be accepted.

`M11TransactionalMortal.run_step` checks the audited current image, writes a **durable intent fence before computing the next step**, executes one isolated private runtime candidate, then commits new state and causal suffix via `src/i1/runtime/sqlite_life_store.py::SQLiteLifeLedger.commit_generation`. Only after an unambiguous committed generation does it publish the new canonical runtime. SQLite's `LifeReceipt.may_recover` is true **only** for `status == "active"` with **no pending intent**. `M11TransactionalMortal.cold_recover` reconstructs an exact fresh factory against that committed image, never an older snapshot. A terminal, mismatched, corrupt or uncertain state fails closed.

There are two independent durability modes: `src/i1/runtime/i1_birth.py::birth_i1` creates an exclusive, newly born append-only WAL identity; `birth_i1_m11` uses exclusively SQLite M11, **not both WALs**. Neither allows continuing a dead life.

## Diagnosis before changing a schema

1. Record exact HEAD, selected engine contract, birth configuration, owner roster, world/seed, custody mode, and real journal head and count.
2. Locate the earliest divergence: physical transition, first-person capture, contribution, bus admission, `S_t`, action admission, autobiographical projection, owner state or SQLite receipt.
3. Read only the **correct authority** at that boundary. An operator-only frame can explain a discrepancy externally but must never be fed back to individual cognition.
4. For a schema change, enumerate producer/consumer, version, export/restore methods, hash/canonicalization and negative examples (unknown fields, duplicate refs, mismatched owner, changed online state).
5. Test before/after and failure injection separately; never mask a mismatch with a restore to a historic living state.
6. Mark absence of instrumented owner deltas as **NOT_OBSERVED**, not as empty learning. Current preset JSON does not reveal full cognitive state.

**Test anchors:** `scripts/test_i1_ci.py`, `tests/i1/test_i1_generated_isolation.py`, `tests/i1/test_i1_stage10_canonical_publication.py`, `tests/i1/test_i1_m11_adversarial.py`, `tests/i1/test_i1_natural_m11_cold_recovery.py`. Check each test's actual assertions before attributing proof, and attach its exact passing SHA.

See [MEMORY_AND_LEARNING.md](MEMORY_AND_LEARNING.md), [CONSOLIDATION_AND_PUBLICATION.md](CONSOLIDATION_AND_PUBLICATION.md), [MORTALITY_AND_M11.md](MORTALITY_AND_M11.md), and [STAGES_AND_INTERFACES.md](STAGES_AND_INTERFACES.md).
