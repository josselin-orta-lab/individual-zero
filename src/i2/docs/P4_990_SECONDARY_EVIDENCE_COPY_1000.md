# P4 #990: offline secondary evidence copy, no birth and no M11 claim

This proposal provides a separately invokable, **offline and opt-in** copy-verification utility, `tools/i2_p4_990_secondary_evidence_copy.py`. It neither creates a NativePaidI2 life nor contacts GitHub, consumes the production one-shot marker, changes a workflow or alters the preregistered six-life #990 physical and cognitive conditions. The helper cannot itself provision a storage device.

## What is verified

The source must be an existing research-evidence directory containing `SHA256SUMS.txt` with portable relative file names. Every regular file must be listed exactly once and match its SHA-256, with no symlinks, traversals, missing/unlisted paths or embedded control characters. A completed or aborted study status is retained as observed, never promoted or inferred from an archive transfer. An explicitly confirmed operation copies every original byte to a **previously nonexistent** destination directory in a separate filesystem; the destination is staged, hashed and checked, the source is rechecked, and a separate secondary-copy receipt is created. That receipt is checked again by `verify`, after the copy is published. No existing destination is overwritten, and a failed partial staging directory is retained for forensics, not falsely marked complete.

Ordinary operator commands, **after the evidence is downloaded** and an independent mounted filesystem is available:

```sh
python -B tools/i2_p4_990_secondary_evidence_copy.py copy /path/to/downloaded-evidence /mnt/independent-storage/i2-p4-990-first-and-only --confirm COPY-P4-990-TO-SECONDARY-STORAGE
python -B tools/i2_p4_990_secondary_evidence_copy.py verify /mnt/independent-storage/i2-p4-990-first-and-only
```

The `--synthetic-allow-same-device` flag exists only for no-birth fixtures; a report generated with it clearly states `SYNTHETIC_SAME_DEVICE_ONLY` and must NEVER be accepted as real independent custody.

## Rehearsal evidence (5 November 2026)

The exact-head GitHub Actions [synthetic run #42032315379](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42032315379) **COMPLETED SUCCESS** for both `synthetic-producer` and `independent-downloader`. The former executed the secondary-copy unit tests and uploaded both the initial completed/aborted synthetic evidence and a separate secondary-copy bundle. The fresh downstream job downloaded both bundles and verified the secondary receipt plus all SQLite and SHA-256 contents. The separate artifacts are `i2-p4-990-synthetic-evidence-42032315379` and `i2-p4-990-synthetic-secondary-42032315379`, both expiring 12 November 2026. The test uses the explicit `SYNTHETIC_SAME_DEVICE_ONLY` exception, so this is **not** an independent offsite storage or long-term retention demonstration.

Ten synthetic no-birth unit tests exercise successful independent-path readback, wrong confirmation, same-device refusal, overwrites, changed source bytes, missing aborted journal, injected/unlisted files, symlinks/path traversal, copied file tampering, receipt forgery, destination nesting and relocated verification. These tests initially have **NOT_RUN** status until source-locked CI completes. The tool does not require i2 engine imports or a network call.

## Limitations and STOP conditions

**A separate filesystem/device is not proof of a separate host, offsite durability, immutable cloud storage, periodic backup or independent M11 authentication.** The verification is an *operator-side local consistency check*, with potential races and a non-adversarial rename/no-overwrite assumption. A privileged actor could still substitute both files and receipt, remove the filesystem or roll it back. Neither the test fixture nor a passing hash check is evidence that the six #990 real lives have been executed or their causal behavior established.

A cloud or external archive location must be selected, mounted, retention-configured and independently audited by an authorized operator. Before scientific dispatch, rehearse download, copy, readback and retention with **synthetic evidence only**, plus explicit fault tests for upload/network failure and runner loss. GitHub Action artifacts are temporary; they are not permanent evidence. The real single-shot study workflow [#997](https://github.com/josselin-orta-lab/individual-zero/pull/997) remains unmerged and MUST NOT be dispatched on the basis of this tool. The producer/retrieval-only rehearsal [#998](https://github.com/josselin-orta-lab/individual-zero/pull/998) is independent and has passed a targeted Actions run.

Do not delete or reset the real protected production marker, alter the frozen #990 parameters, recreate original #985 journals or repeat a cohort to produce favorable outcomes. H3/G3/M11 and generalized survival learning remain NOT_ESTABLISHED.
