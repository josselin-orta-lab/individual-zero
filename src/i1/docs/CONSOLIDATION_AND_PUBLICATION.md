# I1: Stage10 consolidation, owner custody and publication

This document describes the intended/current implementation boundary, not proof that scientifically useful consolidation routinely occurs.

## Owner separation

The registered four-owner roster in `engine.json` is `value_and_needs`, `causal_model`, `perception`, and `metacognition_health`. The owners are actual cognitive state holders, not aliases for arbitrary observer data. Consult `runtime/stage10_runtime.py::causal_owners`, `runtime/i1_cognitive_publication.py`, and `runtime/consolidation_publication.py`.

**Three operations must never be conflated:** online owner updates during wake; paid sleep/consolidation over a bounded and validated autobiographical candidate; atomic publication into the current owners. Counting a consolidation attempt or reporting a publication checkpoint does not establish a nonempty useful form.

## Expected safe path

1. An actual mortal life generates a first-person autobiographical history.
2. Stage10 admits sleep/reduced cognition and charges the relevant work using its existing UC contracts.
3. Validated private history is scanned/replayed with bounded cost and strictly controlled event provenance.
4. Consolidated owner-specific forms are produced and validated. A hypothesis remains *unverified* unless the lived evidence supports a stronger contract.
5. Publication occurs at a guarded boundary. Post-cut online updates must not be duplicated or overwritten by older replay output.
6. M11, where enabled, retains only an authenticated committed current-generation image. Reopening from a dead or uncertain state is prohibited.

## Evidence gate still OPEN

For any claim of generalized active publication, capture an actual life and prove **nonempty content for each claimed owner**, with source event/episode references, provenance restrictions, owner state before/after, UC debits, publication admission, stable durable audit and permitted cold recovery. State clearly if one owner publishes nothing. Do not infer positive evidence solely from smoke/full CI, the existence of classes, or historical broken experiments.

## Failure policy

Corrupt content, bad owner roster, ambiguous publication or uncertain storage commit must stop the path. No compensating rollback of living owner state. A failed publication cannot be made successful by replaying the life from an earlier checkpoint. Consult `tests/i1/test_i1_m11_adversarial.py` and `tests/i1/test_i1_natural_m11_cold_recovery.py`.

## Current executable gates and an identified defect (OPEN)

- `src/i1/runtime/stage10_runtime.py::_run_live_consolidation` requires enabled selection/semantic policies, sufficient frozen consolidation pressure, a valid scheduler journal cut and a paid episode scan. Its `ConsolidationWorkBudget` is a distinct P-42 ledger; see [UC_AND_SCHEDULING.md](UC_AND_SCHEDULING.md).
- `Stage10PublicationCoordinator.REQUIRED` is precisely the four registered owners. `prepare` freezes the post-cut online update slice, validates private rebases and snapshots canonical owner states. `publish` rechecks journal and owner identity at a scheduler synchronization point, rejecting intervening changes.
- The natural runtime chooses `I1Runtime`-specific owner adapters in `_publish_live_consolidation`; inspect each before claiming a *nonempty* change. A history version increment is not sufficient evidence of altered retained cognition.

**Software defect #255, corrected in source (pending SHA-specific CI validation):** `_publish_live_consolidation` previously referenced the local variable `canonical` before assignment, raising `UnboundLocalError` when that path ran. The minimal patch moves the same assignment before constructing the owner mapping, without changing the owner decisions. The regression at `tests/i1/test_i1_stage10_canonical_publication.py` reaches the actual publication method for natural and generic Stage10, verifies chosen owner mapping and safe deferral of invalid forms. `scripts/test_i1_artifact_parity.py` permits only the exact assignment relocation while requiring all other built module bytes to remain identical. **This is a software correction, not proof of nonempty, useful four-owner publication**. Independent living evidence, UC debits, state deltas and M11 cold recovery are still OPEN / NOT_OBSERVED.

## Operational Stage10 state machine and nonempty-publication proof

| Boundary | Executable checkpoint | Reject/defer conditions | What evidence is *not* yet established |
| --- | --- | --- | --- |
| Sleep admitted | `src/i1/runtime/stage10_runtime.py::Stage10Runtime._sleep_step` | Wake/reflex, critical-body or a missing frozen sleep context | `stage10_sleep_entered` is not evidence of memory replay |
| Batch eligibility | `Stage10Runtime._run_live_consolidation` and `src/i1/modules/consolidation_pending_index.py::ChargedPendingEpisodeIndex.advance` | Missing semantic policy, too little frozen pressure, no closed pending episode, uncompleted paid scan | Empty batch is not a failed publication |
| Frozen source | `src/i1/modules/consolidation_transaction.py::ConsolidationCut`, `ConsolidationTransaction` | No authenticated scheduler `step_opened` anchor or conflicting history version | `stage10_consolidation_batch_frozen` proves a selected batch, not trusted causal inference |
| Private six-pass work | `src/i1/modules/consolidation_semantics.py::LivedSixPassAlgorithm`; `src/i1/modules/consolidation_pass_runner.py::ConsolidationPassRunner` | Not enough P-42 charge for whole pass, suspended sleep, invalid lived event projection | `stage10_consolidation_pass_checkpointed` does not modify active owners |
| Candidate and owner rebase | `src/i1/runtime/stage10_runtime.py::Stage10Runtime._publish_live_consolidation`; `src/i1/runtime/consolidation_publication.py::Stage10PublicationCoordinator.prepare` | Wrong four-key `forms`, invalid source provenance, unreplayable post-cut online update, changed history/owner snapshot | Prepared owner states are *private*, not installed |
| Coordinated publication | `Stage10PublicationCoordinator.publish` and `src/i1/runtime/consolidation_publication.py::SlowHistory` | Unauthorized synchronization, modified journal or active owner, invalid prepared digest; exception triggers mortal fail-stop, **not rollback** | `stage10_consolidation_committed` or new `h` version does not by itself prove nonempty retained cognition |
| M11 authentication | `src/i1/runtime/m11_transactional_mortal.py::_verify_i1_active_publication_custody` and `M11TransactionalMortal.cold_recover` | Divergent published/history/advisory rows, pending durable intent, invalid contract or terminal identity | Authenticated recovery proves custody for the exercised current generation, not adaptation quality |

The six pass names in `src/i1/modules/consolidation_transaction.py::PASSES` are `episode_selection`, `interleaved_replay`, `hypothesis_extraction`, `procedural_compilation`, `kappa_recalibration`, `index_maintenance`. In natural I1, the index-maintenance semantic handler builds owner forms from permitted lived evidence. The final publication key set is `value_needs`, `causal_model`, `perception`, `metacognition_health`. **The canonical state owner `value_and_needs` has a different ID than the Stage10 adapter `value_needs`.** See [DATA_CONTRACTS_AND_CUSTODY.md](DATA_CONTRACTS_AND_CUSTODY.md).

To claim a **nonempty** owner-specific publication, collect a source-verified before/after owner snapshot or canonical hash comparison at an authorized boundary, the `consolidation_id` and journal cut, witnessed episode/event refs, the accepted P-42 charges and a corresponding current-generation M11 image where used. Enumerate all four owners separately; distinguish empty proposed rows, unchanged active rows and rows actually installed. A successful history receipt establishes only an atomic technical publication. Do not treat a note with `verification_status=observed_not_verified` as a certified safety rule.

The regression `tests/i1/test_i1_stage10_canonical_publication.py` only proves the corrected owner-selection entrypoint and **safe rejection** of an invalid candidate; it does not exercise full private six-pass nonempty owner publication. On the earlier exact SHA `f895ad3bc62a3096de071284ce85294b35275fc3`, the general CI passed; this scientific claim remains **OPEN / NOT_OBSERVED** until independently instrumented, reproduced and reviewed. Any uncertain mortal publication exception halts rather than restoring an earlier living snapshot.
