# Experiments vs software tests

Both tests and experiments are essential, but they support different claims.

## Software test

A software test verifies behavior that is already specified.

Example:

> Does resetting the simulator restore the documented initial state?

Possible result:

- pass;
- fail.

A failure means the software no longer satisfies an expected contract.

## Scientific experiment

A scientific experiment evaluates a hypothesis or comparison.

Example:

> Does memory strategy B improve delayed recall relative to strategy A under the defined benchmark?

Possible result:

- better;
- worse;
- equivalent within uncertainty;
- inconclusive;
- hypothesis not supported.

The code may be perfectly correct while the scientific hypothesis still fails.

## Examples

### Add a log field

If the new field does not alter behavior:

**software tests only**.

### Fix a timestamp bug

If expected behavior is clear:

**regression test**.

### Replace a memory library

If the replacement can alter what is remembered or recalled:

**EXP + integration tests**.

### Optimize a loop

If behavior is demonstrably equivalent:

**performance measurement + non-regression tests**.

If timing itself influences cognition:

the assumption of equivalence may need an **EXP**.

### Change an action-selection threshold

If the threshold is part of reference cognition and behavior is expected to change:

**EXP**.

## Quick rule

Ask:

> Am I verifying that the software still does something already defined, or am I trying to learn what effect a mechanism has?

The first is usually a test.

The second is usually an experiment.
