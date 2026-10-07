# RAI example: episodic memory retrieval

> Fictional example. Not project evidence.

## Need

An experiment needs a component able to retrieve episodic traces using:

- content similarity;
- recency information;
- inspectable retrieval scores;
- deterministic configuration where possible.

## Scan

Three candidate paths are identified.

### Candidate A

A mature open-source retrieval library.

Pros:

- maintained;
- permissive license;
- stable API;
- deterministic mode.

Limits:

- does not expose one score needed by the experiment.

### Candidate B

A research implementation from a paper.

Pros:

- mechanism is scientifically close to the hypothesis.

Limits:

- difficult to instrument;
- unclear maintenance;
- dependency stack is heavy.

### Candidate C

Implement from scratch.

Pros:

- complete observability;
- exact fit.

Limits:

- highest development and validation cost.

## Decision

**ADAPT Candidate A**

Reason:

The library already satisfies most of the need. A thin adapter can expose the missing instrumentation without changing the underlying retrieval mechanism.

## Expected outputs

- external dependency version pinned;
- adapter in `src/adapters/`;
- integration tests;
- EXP comparing the adapted component to the current baseline;
- limitations documented.

## What would change the decision?

If the missing score cannot be exposed without changing retrieval semantics, the decision should be revisited. The project may then compare Candidate B or IMPLEMENT a minimal mechanism.
