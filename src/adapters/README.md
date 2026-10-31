# External adapters: integration without cognitive ownership

This directory translates external APIs or data into **generation-owned contracts**. It does not own an individual's mind, learning policy, physical WorldBody, living memory, Action Control, UC Scheduler or M11 persistence. Follow [strict generation autonomy](../../docs/decisions/ADR-0001-strict-generation-autonomy.md) and the [agent navigation guide](../../docs/engineering/AGENT_NAVIGATION.md).

**Generation status:** I1 is the active independently owned engine; I0 is frozen historical material; I2 is an unregistered, non-living proposal. Do not turn an I0 integration into a hidden dependency of I1 or I2.

## What belongs here

- External API and data-format translation, schema validation and explicit trust-boundary checks.
- Dependency-specific connection and lifecycle management without transferring cognitive authority.
- Read-only instrumentation that does not inject privileged Oracle/Bench/WorldBody data into a living individual.
- Licensing, provenance, error handling and versioned assumptions about an external dependency.

An adapter may serve a particular generation only when **that generation explicitly declares its interface and owner**. A shared import path is never permission to share mutable cognition, birth state, memory or persistence across generations.

## What belongs in an engine instead

Memory policy, action arbitration, motivation, learning and consolidation, embodied observation, cost accounting and admissibility remain in `src/iN/` for the specific generation. If an adapter would change any of these, review it as a cognitive/architectural change with targeted tests and, where needed, a preregistered experiment.

## Example: external memory package

```text
I1's observed memory contract and owner (verify real call sites)
    |
    v
src/adapters/<external-memory>/  # API translation only
    |
    v
Third-party package
```

The I1 engine still chooses **when, why and under which UC budget** to remember. I2 must prove its own contracts independently, not inherit I1's live adapter state. The equivalent old I0 diagram is historical, not the current placement rule.

See the [worked adapter example](../../examples/adapter-example.md) and [I1 mechanism handbook](../i1/docs/README.md). Document whether any live path actually uses the adapter before claiming a capability is integrated.
