# I0 interfaces

This directory defines cognitive contracts between I0 components.

## Purpose

An interface separates **what role the architecture expects** from **how a particular implementation provides it**.

This can make it possible to:

- compare multiple implementations;
- integrate external projects through adapters;
- replace a mechanism without rewriting unrelated modules;
- instrument shared boundaries;
- make architectural assumptions explicit.

## When to create an interface

Create one when the boundary is useful for research or architecture, not simply because abstraction is fashionable.

Good reasons include:

- two implementations need to be compared under one contract;
- an external project may be substituted;
- several modules rely on the same structural assumption;
- observability at the boundary matters.

## Example

A memory interface may define:

- query input;
- returned items;
- metadata required by I0;
- error semantics.

It should not necessarily dictate the internal storage algorithm.

An external library can then be connected through `src/adapters/`.

## Architectural impact

A change to a shared cognitive interface can affect several subsystems.

If behavior or scientific interpretation may change:

1. start from an EXP;
2. collect evidence;
3. record a shared architectural decision in an ADR if needed;
4. update reference architecture documentation.

See [adapter example](../../../examples/adapter-example.md).
