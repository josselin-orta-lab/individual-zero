# Stage 10: frozen episodic batch selection, Agent B software-development receipt

**Date:** 2026-10-11. **Normative authority:** `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, §15.6, §16.3, §20.3 Stage 10, P-42, INV-21/23/24/47. No normative document was modified.

**Code commit:** `c36713dab0cf75f80db6585f707caa4a48dd8976` on `i0/mvp-parallel-completion`, stacked Draft PR #29 targeting `i0/vnext-stages-10-12` and dependent on PR #25.

## Scope and contract

New `src/i0/modules/consolidation_batch.py` implements a *detached deterministic batch-selection boundary*, using the existing autobiographical `EpisodicMemory.Episode.as_dict()` schema. The explicit slow-history pending-ID set gates eligibility; only episodes ending strictly before the causal cut may be selected. Source projections are copied, a frozen selection digest is computed using the existing canonical causal encoder, and selected payloads can be passed into `ConsolidationTransaction` without reference aliases.

A versioned *development* P-42 policy exposes batch capacity, normalization references, weighting for lived reward magnitude, recorded episode surprise, recency, exact active-goal contextual repetition, and a positive ageing term. Every weight is injected; no campaign value is chosen or frozen by this work. Contextual repetition is **not evidence of repeated procedural success**, causal certainty, or skill compilation. The ageing property is an analytical bound on fixed-signal scores with finite older backlog, **not an observed long-life result**.

Selection requires the caller to supply at least the logical UC quote for scanning **all supplied episodes**, including those already consolidated. It refuses insufficient reservation before accessing episode projections. **This method does not debit the actual compute-budget owner**; that integration, per-step bounded work and suspension remain missing. Providing an arbitrary integer without a real reservation is not a valid runtime integration. No additional cognitive reward or intrinsic motive is generated.

The batch is chosen at consolidation startup as specified by §15.6. This selection contract does **not** execute the complete normative pass 1 inside the six-pass worker, nor interleaved replay, extraction, procedural compilation, recalibration, reindexing, owner rebase or coordinated atomic publication.

## Reproducible local technical tests

Source blob: `7bf409894e5012e98293ea323cccf8607c1429fa`.
New test blob: `e342910e9799cbd5ac4e84632c7ae9cca1901b37`.
Existing transaction source blob: `d12c657fb17896d2b9e2d2c3014bcb1801688dda`.
Existing transaction test blob: `9de0cf075b77e0d305e95e66eb4aa2a90ea9adb5`.

An isolated container with **Python 3.13.5** ran:

```sh
PYTHONPATH=src python -m unittest discover -s tests -p 'test_stage10_consolidation*.py' -q
```

**24 tests / 24 PASS / 0 FAIL / 0 skipped**, consisting of 11 transaction tests and 13 new selection tests. The files were checked against the GitHub blob SHA-1 values; a locally copied implementation of the `lab.determinism` canonicalization functions supplied the dependency, rather than an exact full-repository checkout. The first run had **1 fixture failure** because the overflow example contained too few nonzero weighted terms; the fixture was corrected, and the 24/24 pass obtained without altering acceptance limits.

These are **isolated unit tests only**, not a full dependency-integrated suite, Python 3.11/3.12 CI, a Golden, a semantic six-pass verification, or scientific evidence. The stacked PR's base is absent from the current PR CI filters; no expensive or redundant GitHub Actions jobs were invoked.

## Dependencies and next gates

1. Real `Memory.episodes` and slow-history pending ledger must supply the authoritative projections and eligible IDs. Unit fixtures only reproduce the schema.
2. The Scheduler / budget owner must precharge exact UC for examining episodes. If work is too large for one sleep slot, suspend with an explicit cursor instead of silently performing uncharged work.
3. Implement six actual passes with source episode/event provenance and rule/skill deduplication (DC-16), then privately rebuild Q, κ, perception precisions and causal rules using post-cut journal updates.
4. Publish `h_new` and all active forms atomically via the coordinated scheduler boundary, with real rollback and deterministic replay.
5. Agent A owns the active Stage-11 runtime; no reserved file was changed. Agent A's branch advanced independently during this work. Do not merge without compatibility checks.

**Status:** Stage 10 partial, Stage 11 in progress (Agent A), Stage 12 not integrated, Stage 13 not launched. **Stage 9 scientific NO-GO unchanged.**
