# I2 P4 #990: synthetic artifact retrieval rehearsal (no native birth)

This is an isolated **synthetic-only** two-job test of artifact retention for the intended six-life study. It does NOT invoke `NativePaidI2`, invoke the one-shot claim helper, or create `refs/tags/i2-p4-990-single-use-spent`. It does not reproduce the original #985 cohort or start any #990 life.

## Experimental fixture

`tools/i2_p4_990_synthetic_artifact_custody.py` creates two tiny SQLite databases labeled exclusively `SYNTHETIC_NO_I2_BIRTH`: one completed fixture and one deliberately aborted fixture with only one record. Both have explicit, separate JSON states and a SHA-256 manifest with **relative file paths**.

The local unit tests enforce that both SQLite journals remain readable and that relocating evidence to a new directory does not invalidate verification. They reject changed bytes, missing aborted files, extra unreceipted files, path traversal, absolute paths, symlinks and relabeling an aborted state as completed.

The dedicated GitHub workflow `.github/workflows/i2-p4-990-synthetic-artifact-rehearsal.yml` is allowed on the PR touching these fixtures, and only has `contents: read`. The producer job creates fixtures, intentionally runs a failing *fake command* (`exit 23` with `continue-on-error`), asserts the failure was observed, then uses `if: always()` to upload the directory. An **independent second job** downloads the archive in a fresh runner and verifies all hashes, both SQLite contents and the fact that no real research result is present. The fixture artifact retention is seven days.

**Interpretation:** A successful rehearsal would prove ordinary artifact upload/download/reverification after a controlled command failure on GitHub Actions; it would **not** establish that upload succeeds following VM termination, cancellation, timeout, network outage, or after the artifact retention window. It is **not** an independent M11 witness, external anti-rollback attestation or durable multi-year custody. An additional external destination / streamed evidence and independent operator verification are required before the real experiment.

## Security and merge restrictions

This rehearsal must not be confused with or replace the real #990 workflow. It has no `contents: write` permission, no tag claim, and no I2 birth or scoring. Its PR remains DRAFT until source-locked Python 3.11/3.12 safety and the new standalone two-job workflow actually pass.

Do not merge the separate manual workflow candidate [#997](https://github.com/josselin-orta-lab/individual-zero/pull/997), nor dispatch #990, on the strength of these synthetic tests alone. The claim gate #996 and durable original SQLite custody require independent acceptance. Scientific H3/G3/M11 remain NOT_ESTABLISHED.
