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

## Reference hierarchy and scope

The [versioned reference index](reference/README.md) distinguishes conceptual theory from historical MVP contracts through v1.3.3. English is normative **within each MVP version's declared scope**; French companion translations are informative unless stated otherwise. The superseded v1.3.0 journal-removal proposal must not be revived.

For **current I1**, read its [handbook](../../src/i1/docs/README.md), [engine contract](../../src/i1/engine.json), executable code and [evidence matrix](../../src/i1/docs/EVIDENCE_MATRIX.md). For **I2**, read the independent [proposal handbook](../../src/i2/docs/README.md), which cannot activate an engine. A historical specification, successful old CI or plausible experimental outcome never supersedes the registry, active code or a scientific gate.

The [MVP v1.2.1 implementation map](IMPLEMENTATION_MAP_V1.2.1.md) and Stage-3/4 technical notes are **historical implementation ledgers**, not current I1 instructions; statements such as "current branch" inside them refer to their original development snapshot. Preserve their scientific provenance rather than rewriting them to claim present behavior.

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
