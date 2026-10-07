# I0

This directory contains the reference cognitive architecture and behavior of Individual Zero.

## Role

I0 is the first integrated research baseline.

It should remain small enough to understand and instrument, but complete enough to support meaningful experiments.

I0 owns:

- the reference execution cycle;
- cognitive interfaces;
- project-developed cognitive modules;
- reference configuration;
- assembly and structural relationships between components.

I0 does not own:

- neutral research runtime;
- generic logging and metrics;
- external API translation;
- experiment evidence.

Those belong in the Lab, adapters, or experiment records.

## Structure

```text
src/i0/
├── interfaces/
├── architecture/
├── modules/
└── config/
```

### `interfaces/`

Contracts between cognitive roles and implementations.

Use interfaces when they help substitution, comparison, observability, or structural clarity.

### `architecture/`

Global execution-cycle logic, coordination, and structural relationships between subsystems.

### `modules/`

Cognitive mechanisms developed in the project.

Do not mirror research axes mechanically. Source organization should follow implementation boundaries.

### `config/`

Reference configuration for the current I0 baseline.

## Example

A rule deciding which memory item wins recall belongs in I0.

A logger recording the selected memory item belongs in the Lab.

A translation layer to an external retrieval package belongs in adapters.

The experiment comparing two recall mechanisms belongs in `experiments/`.

## Behavioral changes

A change that can alter reference cognition should be connected to an EXP before integration.

A shared architectural change may later require an ADR.

See [I0 overview](../../docs/architecture/I0_OVERVIEW.md) and [repository placement examples](../../examples/repository-placement.md).
