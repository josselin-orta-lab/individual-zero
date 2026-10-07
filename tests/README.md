# Tests

Software tests verify behavior against a known specification.

They are different from scientific experiments.

## Types of tests

This directory may contain:

- unit tests;
- integration tests;
- compatibility tests;
- regression tests;
- non-regression checks for behavior-preserving refactors.

## Examples

### Unit test

> Given a valid event, does the timestamp parser return the expected value?

### Integration test

> Does the external-memory adapter preserve the fields required by the I0 interface?

### Regression test

> Does the simulator reset bug remain fixed?

### Non-regression test

> Does a refactor preserve the documented outputs?

## What a test cannot establish by itself

A passing software test does not show that:

- a memory mechanism learns better;
- a motivation model produces more adaptive behavior;
- one action-selection policy is scientifically preferable;
- a cognitive architecture is more general.

Those are experiment questions.

## Quick rule

Ask:

> Are we checking that software follows an already defined expectation, or are we trying to discover what effect a mechanism has?

The first is normally a test.

The second is normally an EXP.

See [Experiments vs tests](../docs/research/experiments-vs-tests.md).
