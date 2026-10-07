# Lab

The Lab is **neutral research infrastructure**.

It runs, observes, measures, and reproduces executions without deciding how I0 should think.

## Responsibilities

Typical Lab responsibilities include:

- starting and stopping an execution;
- simulation or environment orchestration;
- logging and structured event capture;
- telemetry;
- metrics collection;
- seed management;
- run identifiers;
- artifact collection;
- configuration loading;
- reproduction tooling;
- timing and performance instrumentation.

## What does not belong here

The Lab should not contain I0-specific:

- memory policy;
- affect or motivation;
- action-selection logic;
- self-model logic;
- learning rules;
- cognitive arbitration;
- domain-specific decision policy.

If moving a piece of code from I0 into the Lab would silently change cognition, it probably does not belong in the Lab.

## Placement test

Ask:

> **Would this code still be useful if we replaced I0 with I1 or a competing architecture?**

If yes, it is a good Lab candidate.

## Example

A logger that records which memory item was recalled belongs in the Lab.

The rule that decides **which** memory item should be recalled belongs in I0.

A timing tool that measures action-selection latency belongs in the Lab.

The action-selection mechanism belongs in I0.

## Scientific impact

Improving Lab observability does not normally require an EXP when behavior is unchanged.

If instrumentation changes timing, state, available information, or another property that can alter the studied behavior, treat the impact explicitly and create an EXP when necessary.

See [the placement examples](../../examples/repository-placement.md).
