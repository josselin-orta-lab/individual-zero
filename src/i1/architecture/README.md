# I0 architecture

This directory contains implementation of I0's structural coordination.

## Typical responsibilities

This area may eventually contain:

- global execution-cycle control;
- sequencing and timing assumptions;
- coordination between cognitive subsystems;
- shared state-routing mechanisms;
- architectural arbitration that is not local to one module.

## What belongs elsewhere

A self-contained cognitive mechanism generally belongs in `../modules/`.

A neutral scheduler used only to run experiments may belong in `../../lab/`.

External API glue belongs in `../../adapters/`.

## Change discipline

Changes that alter the global cycle or structural relationships between several subsystems are scientific and architectural changes.

They should be evaluated before integration.

If results justify a shared reference decision, record that decision in `../../../docs/decisions/`.

## Example

Changing the internal algorithm of one memory implementation may remain a module-level experiment.

Changing the order in which memory, regulation, and action selection are coordinated is an architecture-level change.
