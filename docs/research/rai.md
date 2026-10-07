# RAI: Reuse, Adapt, Implement

RAI is a lightweight decision method used before significant implementation.

Its purpose is to avoid rebuilding a component that already exists without turning external research into a blocking ceremony.

## REUSE

Choose **REUSE** when an existing solution satisfies the need closely enough.

Check:

- scientific fit;
- license;
- observability;
- reproducibility;
- maintenance state;
- security;
- replacement cost.

Typical output:

- pinned dependency or version;
- known configuration;
- integration tests;
- provenance documented.

## ADAPT

Choose **ADAPT** when an existing mechanism is useful but needs a thin layer around it.

Typical adaptation includes:

- interface conversion;
- instrumentation;
- configuration mapping;
- format conversion;
- limited behavior needed for compatibility.

If adaptation changes the cognitive mechanism itself, document that explicitly. It may become part of the scientific comparison rather than mere integration.

## IMPLEMENT

Choose **IMPLEMENT** when:

- no credible solution exists;
- existing candidates fail important constraints;
- the mechanism itself is the research object;
- reimplementation is necessary for observability or reproducibility.

Implementation should still begin with the smallest useful prototype.

## RAI Scan

Use a short scan before a meaningful prototype.

Look for:

- research projects;
- packages;
- papers;
- reference implementations;
- licenses;
- two or three credible candidates.

A scan can conclude quickly when the space is obvious.

## RAI Review

Use a deeper review before:

- adopting a major dependency;
- making an external component part of the reference baseline;
- investing in an expensive in-house implementation.

A review should include:

- scientific adequacy;
- maintenance;
- license;
- observability;
- reproducibility;
- cost;
- security;
- replaceability.

## Time-boxing

RAI should reduce wasted implementation time.

A useful rule is:

> Search enough to avoid reinventing an available solution, but not so long that a testable prototype is indefinitely delayed.

## Example

Suppose an EXP needs episodic memory retrieval.

Three outcomes are possible:

- an existing library exposes the needed semantics and instrumentation -> **REUSE**;
- a library is suitable but needs an I0 interface and extra logging -> **ADAPT**;
- available projects implement a fundamentally different mechanism from the hypothesis -> **IMPLEMENT**.

See [RAI example](../../examples/rai-example.md).
