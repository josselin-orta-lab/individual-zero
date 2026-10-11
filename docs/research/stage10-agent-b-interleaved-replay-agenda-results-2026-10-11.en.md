# Agent B Stage 10: interleaved replay agenda, frozen autobiography and work accounting

**Date:** 2026-10-11. **Normative source:** English `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, §§15.4-15.6, 16.3, 17.6, 20.3; P-42, INV-21/23/24/47 and DC-16. **Classification:** retrospective software engineering unit verification, **not** a preregistered scientific experiment.

## Purpose and implementation

The Agent-B pass runner and the private transaction contracts have already been independently published on `i0/mvp-parallel-completion` prior to this increment. Their current Git blobs are `fcbfecc16ae5ec2fd786e8c48ef8edfbdd9cefa0` and `0be04efb21de32ab2add4b3b956bddbc0a7ae4a5`. This increment does **not** overwrite either owner.

The new `src/i0/modules/consolidation_replay_agenda.py`, blob `8b40b926e40075340e604913c75cd67ffcc041cc`, builds a deterministic recent/old interleaved *agenda* from already frozen autobiographical episode payloads. It requires the transaction to have completed pass 1 before constructing a pass-2 agenda. Duplicate physical event IDs across frozen episodes and invalid episode boundaries are rejected. Entries are work units referencing a frozen episode and one lived autobiographical event ID, not externally manufactured observations. Preparation through `build_charged_replay_agenda` charges a versioned P-42 logical scan operation before reading the episode batch; applying each work unit through the existing pass runner also debits UC before calling an owner-supplied handler.

New test files:
- `tests/test_stage10_consolidation_replay_agenda.py` Git blob `968401797a8040abf42b78763f6b465da2ee0c3c`.
- `tests/test_stage10_consolidation_pass_runner.py` Git blob `8afbec7e3624674472e5cfb2063bacf8af857776`.

The second test file expands the previously published three-test `test_stage10_pass_runner_contract.py` (Git blob `0da01f51ee754eaea7230fd369a0e3742a78936a`) with interruption, budget refusal, complete six-pass checkpoint scheduling **using only synthetic callbacks**, snapshots and restoration. These fixtures do not implement any semantic pass or compile knowledge.

## Tests actually executed before publishing

**Local isolation:** Python 3.13.5; staged copies of five relevant existing Stage-10 modules, the above new files and all applicable Stage-10 unit tests. The canonical `lab.determinism` functions were copied from earlier development, **not checked as the complete current GitHub dependency blob**.

```sh
PYTHONPATH=src:tests PYTHONHASHSEED=0 python -m unittest discover -s tests -p 'test_stage10*.py' -v
PYTHONPATH=src:tests PYTHONHASHSEED=314159 python -m unittest discover -s tests -p 'test_stage10*.py' -q
python -m compileall -q src/i0/modules tests
```

Both fixed-hash-seed runs: **64/64 PASS, 0 FAIL, 0 skipped**, including the newly published smoke tests from concurrent Agent-B work. Relevant Git blobs were separately verified by `git hash-object`. Unit evidence only; **no Python 3.11/3.12 integration CI**, no whole-repository verification, no living sleep replay, historical Golden comparison, scientific preregistration or held-out campaign.

## Known boundaries and remaining work

1. Work-plan construction itself must be charged by its producing owner. The agenda has a charged public factory but its raw deterministic constructor is not a substitute for Scheduler budget authority. An agenda too large for a single preparation slot currently fails explicitly, pending resumable/charged agenda construction.
2. `episode_replay` units are **scheduling and provenance references only**, not a claimed cognitive replay or causal-rule inference. Actual passes 1-6 must each have versioned, verified semantic owners. Test callbacks demonstrate private checkpoints, not learned behaviors.
3. The scheduler must enforce ordinary Competition and Action Control admission of `dormir`, next-step sleep entry, reduced perception, reflexes, dated-intention waking, capped duration, suspended consolidation resumption, and world/body advancement.
4. The scheduler must journal work charges and atomically publish `h_new` with rebased Q, κ, perceptual precisions, procedural skills and Causal Model states after replaying all post-cutpoint updates in causal order.
5. The existing Stage-11 Agent-A runtime, shared Scheduler, Journal, Snapshots, WorldBody and CI files are explicitly unchanged. Integration needs SHA-based coordination; do not merge Draft stacked PR #29 automatically.

**Stage 10: partial software readiness only. Stage 11: Agent A. Stage 12: integration incomplete. Stage 13: scientific campaign not launched. Stage 9: scientific NO-GO unchanged.**
