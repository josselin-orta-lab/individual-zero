# Adapters

Adapters connect external components to the interfaces expected by Individual Zero.

Their job is **translation and integration**, not to hide new cognitive architecture.

## Responsibilities

An adapter may contain:

- API conversion;
- data-format conversion;
- configuration mapping;
- compatibility handling;
- dependency-specific error handling;
- instrumentation required to observe the external component;
- lifecycle glue needed to initialize or stop the dependency.

## What does not belong here

An adapter should not silently become:

- a new memory policy;
- a new action-selection mechanism;
- a new motivation system;
- an architectural coordinator;
- a place where project cognition is implemented simply because the external API was inconvenient.

If the adapter itself becomes the mechanism being studied, treat that work as I0 code or as an experimental prototype.

## Example: external memory library

A clean integration might look like:

```text
I0 memory role
    |
    v
src/i0/interfaces/
    |
    v
src/adapters/<external-memory>/
    |
    v
third-party project
```

I0 remains responsible for **what role memory plays**.

The adapter is responsible for translating that role into the external library's API.

If choosing the external library can alter behavior, evaluate the choice in an EXP before it becomes reference behavior.

See [adapter example](../../examples/adapter-example.md).
