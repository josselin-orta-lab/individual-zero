# Agent B Stage-10 private pass runner, incremental handoff

**Date:** 2026-10-11.
**Normative source:** `docs/architecture/reference/en/mvp-specification-v1.2.1.md` §15.4-15.6, §16.3, §20.3 Stage 10, P-42, INV-21/23/24/47.
**Agent B source commit:** `ce5f8657d9a3f708a3bb5baf4db35b4ec08acc60`.
**PR:** stacked Draft #29 targeting `i0/vnext-stages-10-12`, dependent on Agent A PR #25.

## Actual increment

Added `src/i0/modules/consolidation_pass_runner.py` and `tests/test_stage10_pass_runner_contract.py`. Also retained the already updated `consolidation_transaction.py` from a concurrent Agent B commit.

The runner admits an owner-supplied versioned work plan for the **current** consolidation pass. It charges `pass_prepare` before accepting the plan, charges each operation before calling the supplied handler, and charges `pass_validate` before adding a private validated checkpoint. Failed or exhausted budget keeps the pass private, and a waking interruption cancels the current pass, preserving already completed checkpoints but not refunding spent UC. Partial progress is snapshot-able. Runner restoration binds to the **entire** budget causal ledger, including used sleep-period references, and to the transaction and candidate digests.

The six named passes retain their normative order, but the actual semantic pass handlers and consolidation-produced Q, κ, precisions, rules, skills and h are **not yet implemented**. A test callback is not a production consolidation algorithm. The runner cannot admit `dormir`, perceive threats, execute physical commands, publish h or enforce atomic owner rebase. These remain required integration gates.

## Validation and provenance

The previous locally saved Stage-10 source bundle was reopened and checked against its archive. The exact pass-runner source file published in this commit was verified with Git blob `fcbfecc16ae5ec2fd786e8c48ef8edfbdd9cefa0`. The updated transaction source Git blob is `0be04efb21de32ab2add4b3b956bddbc0a7ae4a5`. The independently added three-test smoke contract file is Git blob `0da01f51ee754eaea7230fd369a0e3742a78936a`.

**Executed locally:** `PYTHONPATH=src:tests python -m unittest discover -s tests -p 'test_stage10_consolidation*.py' -q` on Python 3.13.5, **61 passed / 0 failed / 0 skipped** in an isolated filesystem reproducing the published dependency files. This existing 61-test suite includes the prior pass-runner and replay-agenda tests from the archive; it **does not include** the new three-test GitHub smoke file. The latter has been committed but not yet executed on the published SHA.

The standalone replay agenda and its tests are retained locally in the prior source archive, **not yet published in this Git commit**. Do not claim full interleaved replay is integrated in GitHub from the pass runner alone. Full Python 3.11/3.12, CI on the stacked PR and deterministic living-runtime integration remain unverified.

## Coordination and scientific boundary

While publishing, Agent B branch advanced concurrently from `7f4e0116518d` to `e68987450c72`. The concurrent transaction change was inspected and found to already match the required Git blob, so the subsequent commit was created using that newer parent, with an expected-HEAD fast-forward update only. No force-push or history rewrite. No Agent A Stage-11 files, shared journal/scheduler, main, workflow triggers or normative specifications were modified.

**Stage 10:** partial software implementation, not accepted. **Stage 12:** dependent, not integrated. **Stage 13:** no scientific campaign. **Stage 9:** scientific NO-GO unchanged.
