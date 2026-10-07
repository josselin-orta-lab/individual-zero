# I0 overview

## Status

I0 is the first integrated reference architecture planned for Individual Zero.

At the current bootstrap stage, the repository contains an **executable technical scaffold** for I0, but not a completed cognitive implementation.

The scaffold proves the execution contract, observability path, deterministic run setup, and action boundary. It deliberately returns a no-op action and tracks only technical state.

It should not be read as a claim that memory, motivation, action selection, perception, self-modeling, or any other final cognitive mechanism has already been selected.

See [Bootstrap runtime boundary](BOOTSTRAP_RUNTIME.md).

## Purpose

I0 exists to provide a common executable baseline against which research questions can be measured.

Without a shared reference, each experiment risks silently testing a different system.

I0 should therefore be:

- executable;
- inspectable;
- instrumentable;
- reproducible;
- modular;
- small enough to reason about;
- stable enough to serve as a baseline while still being evolvable.

## Structural boundaries

I0 owns the project's reference cognitive behavior.

This includes, as they are progressively implemented:

- execution-cycle behavior;
- cognitive interfaces;
- project-developed cognitive modules;
- reference configuration;
- assembly and relationships between cognitive components.

I0 does not own:

- generic experiment orchestration;
- neutral logging;
- general metric collection;
- external API translation;
- experiment conclusions.

Those belong to the Lab, adapters, or experiment records.

## Research domains

The research map currently distinguishes six domains:

- architecture and global dynamics;
- perception, body, and world model;
- memory, learning, and consolidation;
- internal regulation, affect, and motivation;
- action selection, agency, and control;
- self, metacognition, and continuity.

These domains organize scientific questions.

They do **not** require I0 source code to have six matching top-level modules.

## Interfaces before implementations

Where useful, I0 should separate the **role expected from a cognitive function** from the particular implementation satisfying that role.

This allows:

- comparing multiple implementations under a shared contract;
- adapting external projects;
- replacing a mechanism without rewriting unrelated subsystems;
- making architectural assumptions explicit.

An interface should not be created merely for abstraction's sake. It should help experimentation, substitution, observability, or structural clarity.

## Minimal I0

The first I0 implementation should be smaller than the long-term architecture.

The minimum useful I0 is the smallest integrated cycle that allows the project to:

1. run deterministically enough to reproduce;
2. expose state to the Lab;
3. exercise at least one meaningful cognitive pathway;
4. compare a controlled variant with a baseline;
5. preserve enough trace to understand the result.

The repository now contains the chassis needed for items 1, 2, and 5, but it does not yet satisfy item 3: no meaningful cognitive pathway has been selected.

The exact cognitive components of the first scientific baseline remain a research and implementation decision to be established through the first real EXP.

## Evolution inside I0

Not every behavioral change creates I1.

Changes may remain in I0 when the fundamental architecture remains compatible.

Examples:

- bug fixes;
- instrumentation;
- performance improvements;
- replacing an implementation behind a stable role;
- parameter changes validated by EXP;
- local cognitive improvements that do not create an architectural incompatibility.

## Candidate I1

A candidate I1 becomes meaningful when evidence supports a structural rupture.

The project expects three conditions before promoting a new reference generation:

1. incompatibility with the current architecture;
2. impact on global behavior or several functions;
3. sufficient evidence to establish a new baseline.

Until then, "candidate I1" is a research state, not a marketing version number.
