# Architecture Decision Records

An ADR records a **shared architectural decision** after sufficient evidence or explicit constraints exist.

It is a memory of why the reference architecture changed.

## Use an ADR when

Examples include:

- changing a shared cognitive interface;
- changing the global execution cycle;
- changing a structural relationship between several modules;
- adopting a dependency that becomes part of the reference baseline;
- changing a shared benchmark definition in a way that alters result interpretation;
- promoting a candidate I(n+1) to a new reference generation.

## Do not use an ADR for

- a local choice inside one EXP;
- a compatible refactor;
- a minor dependency update;
- an ordinary bug fix;
- a prototype choice that has not become shared reference behavior.

## Evidence first

An ADR should point to the EXPs, benchmarks, measurements, or explicit constraints that motivated the decision.

An ADR never replaces an experiment.

## Lifecycle

A typical architectural change looks like:

**Question -> EXP -> Results -> Shared decision needed? -> ADR -> Reference update**

If the result remains local to the experiment, no ADR is needed.

## Naming

Use sequential files:

```text
ADR-0001-short-title.md
ADR-0002-another-decision.md
```

The number records order, not importance.

## Template

Start from [ADR_TEMPLATE.md](ADR_TEMPLATE.md).

A filled illustrative example is available in [../../examples/adr-example.md](../../examples/adr-example.md).
