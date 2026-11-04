# I2 P4 #988: custody of completed native research journals

**Scope:** source-pinned engineering observability improvement for P4 / [#988](https://github.com/josselin-orta-lab/individual-zero/issues/988), stacked on draft [#987](https://github.com/josselin-orta-lab/individual-zero/pull/987), **not** an additional cognitive hypothesis, experiment cohort or engine authority. The original frozen #985 six-life test used disposable `TemporaryDirectory()` SQLite databases. Its historical summary persists, but original signed complete journals were not retained as research evidence. This change does **not** reconstruct, change, or claim to recover those missing originals.

## Optional operator command (future completed lives only)

```sh
python tools/i2_native_completed_life_archive.py path/to/completed-life.sqlite path/to/unused-archive.sqlite
```

The new CLI copies **one already completed** (authentic terminal or born technical-horizon-censored) native I2 SQLite life into a **new** destination under an existing directory. It does not birth, resume, step, edit physiology, change score, mutate source journal or schedule actions. It runs `NativePaidI2.inspect(...).audit()` on the source, uses SQLite's consistent online backup to a private temporary file, cold-audits the copied identity, checks exact identity/genesis and full native audit endpoint equality, audits source once more to detect ordinary changes and publishes using atomic, non-overwriting hard-link creation. On failure the temporary copy is removed and no destination path is created. Existing paths and symlinks are rejected. It returns a JSON receipt including SHA-256 of the published archive bytes, completed revision, biological death versus right-censor, remaining UC, final site/body and local cold-audit PASS.

These are **custody checks**, not external authenticated M11, adversarial storage immutability or proof of atomic identity with the original across every operation. A malicious rewrite with the same audited endpoint or concurrent write races not captured by separate audits may escape detection; the operator must work with a quiescent completed source. The receipt reports `original_unchanged=AUDIT_ENDPOINT_MATCH`, **not** byte-for-byte immutable original file attestation. The archived copy is for retrospective research only; never invoke `step()` or a runnable `reopen()` on it. Store receipt and archive in a controlled external custodian if independent provenance is required. GitHub Actions does not automatically retain these binaries.

## Test scope and scientific limits

`tests/i2/test_native_completed_life_archive_988.py` uses small ordinary SQLite stand-in files and mock native audits to test complete/censored and genuinely terminal status, preserved source bytes, archived data/byte digest, existing destination refusal, symlink rejection, post-backup audit mismatch, endpoint-source mutation and cleanup. **These are not born I2 lives and cannot establish the real engine cold replay integration.** The real-native audit API remains the runtime authority and mandatory CI provides source-level regression coverage. Before claiming verified native custody, additionally apply the command to an independently cold-audited, completed *new* permitted life (without relabeling it as any #985 original) and inspect a matching SHA-256 receipt.

The CI run should wait until parent #987 has its complete exact-head Python 3.11 and 3.12 safety results; this branch is deliberately stacked/draft to avoid overlapping expensive native suites. No new score rules, food quality oracle, external motor, I1 import, M11 promotion or scientific adaptive-survival claim. The frozen six-life null v23 activation and no-motor-divergence observations remain unchanged.
