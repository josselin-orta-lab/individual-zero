# ADR-EXAMPLE - Adopt a shared timestamped event contract

> Fictional example. Not an active project decision.

## Context

Several completed experiments used incompatible event formats. This made cross-experiment comparison and Lab instrumentation unnecessarily difficult.

EXP-0012 and EXP-0018 both found that a shared timestamp and source identifier were necessary to reproduce ordering-related observations.

## Options considered

1. Keep per-module event formats.
2. Standardize only Lab logs.
3. Adopt a shared I0 event contract for cross-subsystem events.

## Experimental evidence or constraints

- EXP-0012: ordering ambiguity affected replay analysis.
- EXP-0018: source identity was required to reproduce arbitration traces.
- Lab tooling already supports timestamped events.

## Decision

Adopt a shared timestamped event contract for events exchanged between the affected I0 subsystems.

## Consequences

Positive:

- easier trace comparison;
- simpler Lab instrumentation;
- clearer ordering assumptions.

Costs:

- affected modules must migrate;
- adapter compatibility must be checked.

## Individuals / axes concerned

- I0
- AXIS-ARCH
- AXIS-MEMORY
- AXIS-ACTION

## Date and status

Example only.
