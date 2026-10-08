# Architecture documentation

This directory contains architecture-level descriptions of Individual Zero and its reference generations.

## What belongs here

Use this directory for documents that describe:

- the global execution cycle;
- structural relationships between cognitive subsystems;
- shared cognitive interfaces;
- architectural invariants;
- reference-generation manifests;
- architecture diagrams that are meant to describe the current reference.

## What does not belong here

Do not place here:

- the evidence for one specific experiment;
- local prototype notes;
- implementation details that belong next to code;
- speculative mechanisms that have not become part of a reference or architectural candidate.

Those belong in `../../experiments/`, `../../src/`, or research discussion respectively.

## I0, I1, I2

I0, I1, I2, and later names represent **architectural generations**, not ordinary software versions.

Software can evolve inside I0 while the fundamental architecture remains compatible.

A new generation should be considered only when all three conditions are supported:

1. there is an architectural incompatibility with the current generation;
2. the change affects global behavior or several functions;
3. enough experimental evidence exists to establish a new baseline.

## Reference hierarchy

Long-form reference documents are organized by language under [`reference/`](reference/README.md).

For the current French documentation:

1. [Normative MVP specification v1.2](reference/fr/mvp-specification-v1.2.md) is the **implementation authority for the MVP**.
2. [Conceptual architecture v2](reference/fr/architecture-v2.md) is the broader conceptual and scientific architecture.
3. Repository-specific notes such as the I0 overview and bootstrap runtime document the current codebase and must remain consistent with the normative MVP specification.

When a conceptual statement and an implementation rule differ, implementation work follows the normative MVP specification for the scope of the MVP.

English equivalents use the same filenames under `reference/en/`. The language lives in the directory, while the basename and document version remain stable across translations.

## Repository architecture documents

- [I0 overview](I0_OVERVIEW.md): concise description of the current I0 reference boundary.
- [Bootstrap runtime boundary](BOOTSTRAP_RUNTIME.md): executable bootstrap architecture and its deliberately non-cognitive boundary.
- [Individual template](INDIVIDUAL_TEMPLATE.md): structure for future generation manifests.

## Example

Replacing one memory implementation behind a stable interface may remain inside I0 if the architecture does not change.

Changing the role of memory in the global cycle, the contract shared with action selection, and the timing assumptions across several modules may become a candidate I1 if experiments justify it.

## Decision trail

If an architectural choice becomes shared reference behavior:

1. evidence remains in the relevant EXP;
2. the shared decision is recorded in an ADR;
3. this documentation is updated to describe the resulting architecture.
