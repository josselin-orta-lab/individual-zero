# Agent B Stage 10: multi-step charged replay agenda construction (local development evidence)

Date: 2026-10-11. Normative source: English MVP v1.2.1 §15.6, §16.3, P-42 and INV-21/23/24/47. Status: **development/validation locally, NOT integrated or scientifically accepted**.

## Problem and approach

The already published `build_charged_replay_agenda` debits an entire frozen batch in one sleeping step, so it cannot finish when that preparation requires more UC than a single slot. An independent, **locally implemented** `IncrementalReplayAgendaBuilder` decomposes agenda construction into individually charged operations: reading a frozen episode, checking each lived event reference, comparing and inserting in a stable recency/oldness order, and emitting each replay unit. No operation is performed on a failed budget charge, no borrowing of UC across steps occurs, and the final unit ordering and plan exactly match the existing deterministic `InterleavedReplayAgenda` contract.

The builder includes snapshot verification of the full budget state and a chronological log of operation identity, UC price, sleep-period reference and sleeping world-step. Technical restoration reconstructs the private progress without spending UC again or invoking any cognitive owner handler. A waking cancellation clears unvalidated agenda progress and retains already spent UC; malformed autobiographical evidence enters a non-retryable private invalid state. No journal, oracle or WorldBody read is introduced.

## Exact local evidence and reproducible handoff

Two **unpublished** files under a local development directory:

| Path | Git blob SHA-1 |
| --- | --- |
| `src/i0/modules/consolidation_replay_builder.py` | `08c1f79dd859df300f07f2606ac3a464275d0177` |
| `tests/test_stage10_consolidation_replay_builder.py` | `93f7470feb50d1430560f9df294a32180a43147e` |

Local archive: `agent-b-stage10-incremental-replay-builder-2026-10-11.tar.gz`. Its SHA-256 is `6d9b02c9f360e47d305b9993391e54e15150c8919671594f79f6205c2154d3dd`. This archive is a **local handoff artifact**, not a GitHub repository file or proof of an integrated implementation.

Python: **3.13.5** (Python 3.11 and 3.12 are not available locally). The validation uses locally staged Stage-10 modules and a copied minimal `lab.determinism` canonicalizer. No full current-GitHub repository checkout is available in the container.

Executed twice:

```sh
PYTHONPATH=src:tests PYTHONHASHSEED=0 python -m unittest discover -s tests -p 'test_stage10*.py' -q
PYTHONPATH=src:tests PYTHONHASHSEED=314159 python -m unittest discover -s tests -p 'test_stage10*.py' -q
python -m compileall -q src/i0/modules tests
```

**81/81 PASS, 0 FAIL, 0 skipped in each test run** (including the existing three pass-runner contract smoke tests). No CI, Golden, integrated runtime test, Python 3.11/3.12 verification, or scientific campaign has been executed for this new source.

## Publication blocker and next safe integration step

The GitHub connector accepts content but not an already-mounted local filesystem path. A lossless source transfer has not yet been completed for the larger builder file. **Neither new source file has been committed to the Agent B branch.** GitHub's new pass-builder behavior must remain **unverified** and **absent** in the normative matrix until exact Git blobs are published, checked and tested. The smaller tests blob can already be reconstructed and independently checked; do not publish tests alone without their source.

Before publishing: transfer both full files, compare returned Git blobs against the two SHA-1 values, check branch HEAD lease, atomically commit source/tests only on `i0/mvp-parallel-completion`, and rerun validation against its exact GitHub sources. The dependency on the real Stage-11 runtime remains open. No reserved Agent-A file, normative specification, main, workflow or protection was edited.

**Stage 10 partial. Stage 12 dependent. Stage 13 campaign not started. Stage 9 scientific NO-GO unchanged.**
