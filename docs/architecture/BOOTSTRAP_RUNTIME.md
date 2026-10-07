# Bootstrap runtime boundary

## Status

Implemented as technical infrastructure.

This document describes the first executable scaffold of Individual Zero. It is not a scientific cognitive architecture claim.

## Why it exists

Before testing memory, motivation, action selection, perception, or self-modeling, the project needs a trustworthy way to:

- start an Individual;
- reset it with a known seed;
- present observations;
- collect actions;
- expose state;
- record structured events;
- reproduce a small run;
- test the execution boundary automatically.

The bootstrap runtime establishes those mechanics without selecting cognitive theories prematurely.

## Current execution path

```text
SmokeScenario
     |
     | Observation
     v
Lab runtime
     |
     v
BootstrapI0
     |
     +----> observable state
     |
     +----> noop Action
     |
     v
Lab event sink
     |
     v
JSONL artifact
```

## Why the action is `noop`

Any nontrivial action policy would already encode a behavioral assumption.

At this stage, that would create "cognition by convenience" before a research question exists.

The no-op action therefore means:

> the action boundary is executable, but no reference action-selection mechanism has yet been scientifically chosen.

## Current I0 bootstrap state

The scaffold exposes only technical state:

- seed;
- number of completed cycles;
- number of observations seen;
- last observation kind.

These fields make execution inspectable. They are not intended as a model of human or artificial cognition.

## Interfaces introduced

### Observation

A cycle-indexed input with:

- kind;
- data.

### Action

An externally visible requested action with:

- kind;
- data.

### StepResult

One execution result containing:

- action;
- observable state.

### Individual

The minimal protocol expected by the Lab:

- `reset(seed=...)`
- `step(observation)`

These interfaces should remain small until research requires stronger semantics.

## Lab responsibilities implemented

The first Lab now supports:

- deterministic run configuration;
- run identifiers;
- seed propagation;
- scenario-provided observations;
- structured run events;
- in-memory event collection;
- JSONL artifacts;
- compact run summary;
- command-line execution.

## Deliberate omissions

The bootstrap does not yet define:

- memory;
- learning;
- motivation;
- affect;
- perception processing;
- planning;
- action arbitration;
- self-model;
- world model;
- values;
- cognitive timing semantics beyond ordered cycles.

Those omissions are intentional.

## Promotion from scaffold to research baseline

The bootstrap becomes a meaningful cognitive I0 only when the first scientific mechanisms are added through explicit questions and EXPs.

Until then, it should be understood as:

**an executable research chassis, not an implemented theory of mind.**
