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

**OPEN software defect observed by source inspection at PR #254 original HEAD `84d7e0ef`:** `_publish_live_consolidation` constructs the `owners` mapping using `canonical` in three conditional values **before** the following assignment `canonical = type(self).__name__ == "I1Runtime"`. On reaching this function, Python's local-variable scoping therefore raises `UnboundLocalError` before publication preparation. The source inspection establishes an executable defect, **not** a measured frequency in living runs. Fix only with a focused negative/positive path test, and do not claim multi-owner publication after a simple syntax check. Until a tested correction exists: publication behavior remains **UNVERIFIED / OPEN**.
