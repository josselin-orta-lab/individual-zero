# Agent B Stage-10 P-42 sleep consolidation work budget: technical result

**Date:** 2026-10-11.
**Code SHA:** `15fb85e37b49c3278744126d620cc131706af34b`.
**Normative source:** `docs/architecture/reference/en/mvp-specification-v1.2.1.md` §15.4-15.6, §16.3, §20.3 Stage 10, P-42, INV-21/23/24/47.
**Scientific status:** Stage 9 NO-GO unchanged; no scientific acceptance.

## Question and method (software investigation, retrospective report)

The previously isolated batch selector accepted an integer scan-UC quote but did not debit a real work ledger. That alone cannot establish a bounded consolidated-sleep computation path. Test the independent Stage-10 contract using logical counters, not wall-clock time, without modifying the Agent-A scheduler or its Stage-11 runtime.

Source: `src/i0/modules/consolidation_budget.py` (Git blob `fde24b6f66de771daea5a58f36fa682343264496`).
Test: `tests/test_stage10_consolidation_budget.py` (Git blob `866574663adb798cc51d8dfe6f0070ee46c3021b`).

Implemented `ConsolidationWorkBudget`, a separately owned causal ledger with injected versioned P-42 operation costs and bounded UC per sleeping world step and across one sleep period. A rejected charge cannot consume UC. Unused capacity from a prior step does not carry over as step quota, and the period-wide ceiling is never extended by passing time. Charges outside an active sleep step are refused. A later sleep period can restart its UC ledger while the **same suspended consolidation transaction** remains eligible for resumption. World advances and command admission remain external and controlled by their normative owners.

The `select_batch_with_charged_work` adapter verifies that selector and budget prices agree, then debits the actual sleeping-work ledger **before** accessing episode projections. On insufficient quota it raises a specific exception and does no episode scan. This is not an approximation or synthetic result. Full scans larger than a step slot are explicitly refused, not yet chunked across steps. Multi-step bounded scanning remains an open technical gap.

The ledger exports its causal state and validates the entire snapshot before owner mutation, including period identifiers, world-step chronology, cumulative work, per-step ceilings, and configuration version. Original operation-cost dictionaries are copied into an immutable mapping to prevent unversioned schedule edits.

## Actual validation

Environment: isolated local filesystem, Python **3.13.5**. Test command:

```sh
PYTHONPATH=src:tests python -m unittest discover -s tests -p 'test_stage10_consolidation*.py' -v
```

**35 tests, 35 PASS, 0 FAIL, 0 skipped**: 11 transaction tests, 13 batch-selection tests, and 11 budget tests. Each file's Git blob was checked before publication against the local tested file; the successful commit includes the exact new source and new tests. The isolated checkout uses a local copy of the relevant normative `lab.determinism` canonicalizer rather than a complete checkout of the GitHub repository. This is unit-only proof in the isolated environment, **not CI validation of all dependencies or an exact Python 3.11/3.12 full-suite result**. No GitHub Actions job was started.

The GitHub upload initially produced mismatched detached blobs due to transport encoding; these were not committed. Both subsequently committed blobs were checked against their exact expected Git SHA-1. No reserved Stage-11 source, no scientific historical protocol, no normative specification, no branch protection, and no workflow was changed.

## Open integration conditions

- Scheduler must initiate this ledger only after **actual** admitted `dormir` and subsequent entry into sleep, and journal all accepted/rejected charges. This standalone ledger cannot establish that itself.
- An episode population larger than one step's scan allowance needs an explicit cursor, per-slot work accounting and snapshot/restart; an uncharged scan is not permitted.
- The six semantic passes remain unimplemented and cannot be made green by synthetic callbacks.
- Consolidation must still rebase Q, κ, perceptual precisions, causal rules using all post-cut updates in original causal order and commit all owner states atomically.
- No actual reduced perception, admissible reflex in sleep, wake on authorized intention, maximum sleep duration, or long Golden replay has been validated by this change.
- Stage 12 integration and Stage 13 are not accepted. Stage 9 scientific NO-GO remains unchanged.

**Coordination:** stacked Draft PR #29 against Agent A's branch `i0/vnext-stages-10-12`; no merges, retargeting, history rewrite or force-push. The Agent-A branch continues independently and compatibility must be reviewed at integration.

## Subsequent verified software hardening: full P-42 digest (same date)

**Updated code commit**: `19f23c3ffd6f276e4a5e0b585ee5a094f358166a`.
**Final source Git blob**: `47badb42cf12e031dcc44a4880cfb4f538ce976b`.
**Final test Git blob**: `27b71e5a8fcd80809c4ca1f4ba08bbae771dce72`.

The original v1 budget snapshot validated its `config_version` string but could accept a different numeric P-42 cost schedule under the same version label. This new software fix hashes the complete canonical configuration, including both capacity bounds and every versioned operation cost, and stores `config_digest` in the causal snapshot. Restore now rejects changes of capacity/cost even when a version label was reused. The new test for same-label, different-capacity restoration and the corrupted-digest rejection both pass locally.

**Command actually rerun:** `PYTHONPATH=src:tests python -m unittest discover -s tests -p 'test_stage10_consolidation*.py' -q`, Python 3.13.5, **35 tests / 35 PASS / 0 FAIL / 0 excluded**. Isolated-local limitations described above remain fully applicable. The SHA 19f23 was pushed after the tested file bytes were independently matched to their Git blobs. No Python 3.11/3.12 full-suite or GitHub Actions result applies to this SHA.
