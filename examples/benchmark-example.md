# Benchmark example: delayed recall

> Fictional example. Not an active benchmark.

## Purpose

Provide a reusable scenario for comparing memory mechanisms on delayed recall.

## Scenario

1. Present a sequence of synthetic episodes.
2. Remove direct access to the original observations.
3. Run a fixed offline interval.
4. Ask the system to recover requested details.

## Inputs

Synthetic episodes generated from a fixed seed family.

## Metrics

- exact-detail recall accuracy;
- partial-match score;
- latency;
- number of retrieved traces;
- run failures.

## Comparison rules

All compared variants should share:

- episode sequence;
- offline duration;
- query set;
- seed set;
- evaluation metric implementation.

Only the mechanism under study should differ unless the EXP explicitly studies interactions.

## Known limitations

This benchmark does not measure:

- long-term semantic abstraction;
- interference across months of experience;
- value-dependent memory;
- real-world perception noise.

## Why this is a benchmark

Several different memory EXPs could reuse the same task and metrics.

A one-off experiment-specific scenario would not necessarily deserve a shared benchmark folder.
