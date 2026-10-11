# Agent B Stage-10 transaction custody v2: software-only development report

Date: 2026-10-11. Normative authority: English MVP specification v1.2.1, 15.6, 17.6, 20.3, INV-23/24/47. Scientific Stage-9 verdict: **NO-GO**, unchanged.

## Branch and coordination

Agent B branch: `i0/mvp-parallel-completion`. Original base: `3f32fd9afa6373d1536c0baf186d280942a79bdd`. Draft stacked PR: #29 targeting `i0/vnext-stages-10-12`. Agent A moved to `69a9037e90e0c3e7280331d695b51342c6e4d8a7` during the preceding increment. No rebase, merge, force-push or edits of reserved runtime, scheduler or journal files.

## Verifiable change

Previously the private transaction recorded a cut marker but not the journal index or hash, stored episode references without a complete frozen episode payload, and restored checkpoints without a cryptographic consistency chain.

V2 stores a full cut tuple (world step, append-only journal index, event ID, journal head hash, source history version), validates complete episode payload ownership before the cut, hashes the frozen input batch, hashes checkpoint contents in normative pass order using the existing causal canonical encoder, rejects malformed snapshots, and supports complete transaction-slot export and atomic validation-before-restore. A scheduler commit *receipt contract* validates identity, version and candidate digest before the slot is released. It does not itself publish h, rebase owners or prove the existence of a real journal event. Schema upgraded intentionally to v2; old v1 snapshots are incompatible and require an explicitly coordinated migration if any v1 transaction was persisted.

## Tests and limits

A locally isolated stand-in for `lab.determinism.canonical_causal_bytes`, copied from the repository, was used because the container has no network connectivity for git clone. The evolving candidate implementation was exercised using Python 3.13.5 and `PYTHONPATH=src python -m unittest discover -s tests -p 'test_stage10_consolidation_transaction.py' -v`. **14 of 14 isolated local tests passed**, after correcting one test fixture that incorrectly tried to register an already completed transaction. This is not a validation of the complete repository or its two required CI environments.

Two source and test files were subsequently uploaded to GitHub through the connector in separate commits. The final uploaded test suite was independently reformulated into 11 focused tests, **not yet executed against the pushed SHA**. The 14/14 local outcome must NOT be attributed to the GitHub HEAD. Python 3.11/3.12 full-suite validation of the pushed SHA, Stage-11 integration, long Goldens and scientific acceptance remain **unverified**. The CI pull-request branch filter does not include this stacked PR target.

## Remaining work

1. Audit the v2 snapshot and receipt interface under Python 3.11/3.12 on the exact branch commit before claiming validation.
2. Implement the six *real* cognitive passes, P-42 work envelopes and episode-priority/aging on their canonical owners; synthetic test callbacks are not substitutes.
3. Implement technical validation of privately staged owner rebases from h_new and chronological post-cutpoint journal updates, with coordinated atomic scheduler installation and recovery after failure.
4. Integrate ordinary `dormir`, reduced perception, reflex-safe wake and world step advancement without touching Agent A files before interface coordination.
5. Extend the full normative matrix, Stage 12 detectors and Stage 13 preflight independently.

Classification: Stage 10 in progress, not accepted; Stage 12 dependent and pending; Stage 13 campaign not started; Stage 9 scientific NO-GO.
