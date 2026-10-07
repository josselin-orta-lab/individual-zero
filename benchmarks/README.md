# Benchmarks

Benchmarks provide reusable scenarios, reference data, metrics, and comparison rules.

A benchmark should allow several variants or EXPs to be compared under the same conditions.

## A benchmark should document

- purpose;
- scenario;
- input data or generation procedure;
- metrics;
- configuration;
- expected invariants;
- known limitations;
- versioning when interpretation changes.

## What does not belong here

Do not place conclusions specific to one experiment in a benchmark.

Example:

The benchmark may define a delayed-recall task.

EXP-0012 may conclude that memory strategy B performs better than A on that task.

That conclusion belongs in EXP-0012.

## When to create a benchmark

A scenario becomes a good benchmark candidate when:

- more than one mechanism needs the same comparison conditions;
- several EXPs need the same metrics;
- a stable task is needed to track reference changes;
- reuse will reduce protocol drift.

A one-off EXP scenario does not automatically need to become a benchmark.

## Changing a benchmark

Small additions can remain ordinary benchmark maintenance.

If changing a shared benchmark changes how existing results should be interpreted, treat the change as a significant shared decision and consider an ADR.

## Example benchmark skeleton

```text
benchmarks/
└── delayed-recall/
    ├── README.md
    ├── config/
    └── data/
```

The benchmark README should be enough to understand what is being measured without reading a specific EXP.
