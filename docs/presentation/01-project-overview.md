# Project overview

## Why Individual Zero exists

Individual Zero explores a practical research question:

> Can we build an artificial individual capable of learning, adapting, and mobilizing what it has learned in genuinely new situations?

The project does not begin from the assumption that a particular theory of cognition is correct. Human cognition is an inspiration source, not a blueprint to copy mechanically.

The research goal is to build a system whose important mechanisms can be inspected, measured, challenged, replaced, and reproduced.

## What the project is building

The first target is **I0**, the initial integrated reference architecture.

I0 is useful because research questions become much easier to interpret when experiments share a common reference system.

I0 should be:

- executable;
- observable;
- small enough to understand;
- modular enough to replace mechanisms;
- reproducible enough to compare results;
- explicit enough that architectural changes leave a trace.

## The core separation

The repository is intentionally split into several roles:

- **Lab** runs, observes, measures, and reproduces.
- **Adapters** connect external projects.
- **I0** contains the reference cognitive behavior.
- **Experiments** preserve scientific evidence.
- **Benchmarks** provide reusable comparison scenarios.
- **Tests** verify expected software behavior.

The short version is:

> **Lab observes. Adapters connect. I0 operates. Experiments provide evidence. Tests verify the code.**

## How progress happens

A scientific contribution typically follows:

**Question -> RAI -> minimal plan -> prototype -> test -> results -> decision**

The point is not to maximize implementation volume.

The point is to make each meaningful change answer a question.

## What counts as progress

Useful outcomes include:

- a mechanism works better under defined conditions;
- a mechanism works worse;
- two variants are equivalent;
- a hypothesis is not supported;
- the experiment is inconclusive but exposes a measurement problem;
- an external component is good enough to reuse;
- an architectural assumption should be revised.

Negative results are part of the project memory when they are reproducible.

## What the project deliberately avoids

Individual Zero tries to avoid:

- building cognitive mechanisms without a question;
- copying external tools without checking whether they fit;
- hiding scientific behavior inside infrastructure;
- treating software tests as scientific evidence;
- using architecture documents as substitutes for experiments;
- creating long-lived Git branches for research axes;
- creating speculative EXP records merely to make the roadmap look populated.

## Current stage

The project is currently building its research foundations:

1. repository and collaboration workflow;
2. minimal Lab;
3. minimal executable I0;
4. first active research questions;
5. first reproducible experiments;
6. shared benchmarks;
7. iterative architectural evolution from evidence.

## Where to go next

- [Repository tour](02-repository-tour.md)
- [Research workflow](03-research-workflow.md)
- [First-hour contributor guide](04-contributor-first-hour.md)
- [Research Map](../../RESEARCH_MAP.md)
