# Technical contribution example: improve run metadata

> Fictional example.

## Goal

Add the current Git commit hash and seed to every Lab run summary.

## Why this is technical

The change improves reproducibility metadata but is not expected to alter the active generation's cognitive behavior.

## Placement

- implementation: generation-owned Lab (for active I1, `src/i1/lab/`) or a strictly external read-only observer;
- tests: `tests/i1/` for I1-specific changes or appropriate tooling tests;
- documentation: owning generation's Lab README if public behavior changes.

## EXP required?

No, assuming metadata capture does not affect execution behavior.

## Expected PR evidence

- unit or integration test showing fields are written;
- example output;
- confirmation that run behavior is otherwise unchanged.

## Example branch

```text
feat/run-metadata
```

## If something unexpected happens

If collecting the metadata changes timing enough to affect a studied mechanism, the assumption of technical neutrality becomes false.

At that point, document the impact and consider an EXP.
