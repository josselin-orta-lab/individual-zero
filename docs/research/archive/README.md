# Historical research source archives

This directory contains **historical research source material**. Its location does not confer current architectural authority, reproducibility, or scientific acceptance.

## Contents

- [Issue 110 GA08 legacy source snapshot](issue110-ga08-legacy/): preserved experiment-specific source layout with `.github/workflows/`, `scripts/`, `src/i0/`, `src/lab/` and `tests/`. It is **not** the active engine, and these copies must not be imported into I1 or I2.

## Three different custody boundaries

1. [Frozen I0 archive](../../../archive/i0/README.md): workflows, Lab and tests covered by the immutable [source manifest](../../../config/archives/i0-20261017.json). These are exact historical Git blobs and not living-I1 acceptance criteria.
2. **This directory**: research-specific legacy source snapshots kept for tracing old experiments. Do not assume that the frozen I0 manifest covers these files; investigate the original Git SHA and associated study before claiming exact reproduction.
3. [Original dated research records](../README.md) and [study indexes](../studies/README.md): protocols, reported outcomes and cross-references may remain at original paths because other records cite them.

## Before using or reorganizing an archival source

Identify the study, exact source commit, input artifacts, referenced workflow and test fixtures. Keep the original bytes and paths until the complete dependency and citation closure is verified. Never run a historical workflow from this directory as if it were an active GitHub Action, resurrect the old shared Lab in a current engine, or transfer a historical individual state into a new generation.

Use `python tools/repository_layout.py inventory --kind archives --match issue110` for navigation. The inventory is read-only and its `NOT_EVALUATED` result is **not** a scientific verdict.

If the archive source, protocol or original evidence cannot be authenticated, record `SOURCE_REVIEW_REQUIRED` instead of silently replacing it or calling the study reproduced.
