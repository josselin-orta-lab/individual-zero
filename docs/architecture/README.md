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

I0 is frozen; **I1 is the active generation** and I2 is a separate unregistered proposal. Software may evolve inside an active generation without forcing a successor, but no generation may depend on an obsolete runtime.

A new generation should be considered only when all three conditions are supported:

1. there is an architectural incompatibility with the current generation;
2. the change affects global behavior or several functions;
3. enough experimental evidence exists to establish a new baseline.

## Reference hierarchy

Long-form reference documents are organized by language under [`reference/`](reference/README.md).

For the current French documentation:

0. [MVP v1.3.1 migration target](reference/fr/mvp-specification-v1.3.1.md) **retains the full causal journal**, independently audits its complete export and makes Oracle/Bench optional observers.
1. [Normative MVP v1.2.1](reference/fr/mvp-specification-v1.2.1.md) is the historical Stage 10/11 development baseline; [v1.3.0](reference/fr/mvp-specification-v1.3.0.md) is a superseded proposal.
2. [Conceptual architecture v2](reference/fr/architecture-v2.md) is the broader conceptual and scientific architecture.
3. I0 overview and bootstrap documents describe **historical I0 scope**. For active I1 use its [generation handbook](../../src/i1/docs/README.md), [engine contract](../../src/i1/engine.json) and executable code; for I2 use its [proposal handbook](../../src/i2/docs/README.md). Historical MVP specifications do not automatically govern later generations.

When concepts, generation contracts and code disagree, determine their generation and version before acting. Historical MVP specifications govern their documented historical scope only, never silently override current I1 or activate I2.

English equivalents use the same filenames under `reference/en/`. The language lives in the directory, while the basename and document version remain stable across translations.

## Repository architecture documents

- [I0 overview](I0_OVERVIEW.md): historical description of I0, not the active I1 boundary.
- [Bootstrap runtime boundary](BOOTSTRAP_RUNTIME.md): executable bootstrap architecture and its deliberately non-cognitive boundary.
- [Individual template](INDIVIDUAL_TEMPLATE.md): structure for future generation manifests.

## Example

Replacing a memory implementation behind a stable interface may remain inside active I1 if the architecture does not change and scientific impacts are handled. I0 remains frozen.

Changing the role of memory in the global cycle, the contract shared with action selection, and the timing assumptions across several modules may become a candidate I2 if evidence and explicit architectural review justify it; this does not make I2 executable.

## Decision trail

If an architectural choice becomes shared reference behavior:

1. evidence remains in the relevant EXP;
2. the shared decision is recorded in an ADR;
3. this documentation is updated to describe the resulting architecture.
