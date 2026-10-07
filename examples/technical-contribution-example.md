# Technical contribution example: improve run metadata

> Fictional example.

## Goal

Add the current Git commit hash and seed to every Lab run summary.

## Why this is technical

The change improves reproducibility metadata but is not expected to alter I0 cognitive behavior.

## Placement

- implementation: `src/lab/`;
- tests: `tests/`;
- documentation: Lab README if public behavior changes.

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
