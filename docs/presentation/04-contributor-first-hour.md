# Your first hour as a contributor

You do not need to understand every cognitive mechanism before contributing.

This guide is designed to get you from "I just opened the repository" to "I know where my work belongs."

## Minute 0-10: understand the project shape

Read:

1. [Project overview](01-project-overview.md)
2. [Repository tour](02-repository-tour.md)

Remember one sentence:

> **Each generation owns its Lab and cognition. I1 is active, I0 is frozen, I2 is a proposal. Tests verify software; experiments supply scientific evidence.**

## Minute 10-20: identify your contribution

Ask which category fits best.

### Technical

Examples:

- fix a logging bug;
- improve installation;
- add a metric without changing behavior;
- update documentation;
- add a regression test.

You probably do **not** need an EXP.

### Scientific

Examples:

- compare two memory strategies;
- alter motivation dynamics;
- replace a cognitive mechanism;
- change a reference parameter expected to alter behavior.

You need a measurable question and probably an EXP.

### Architectural

Examples:

- change a shared cognitive interface;
- restructure the global cycle;
- promote a new architectural generation.

Start with evidence. An ADR comes later if a shared decision is needed.

## Minute 20-30: find the right location

Use this shortcut:

- "Active I1 behavior or its environment" -> `src/i1/` (including `lab/`, `runtime/`, `modules/`)
- "Independent inert I2 research" -> `src/i2/`
- "Frozen historical engine" -> inspect `src/i0/` and `archive/i0/` without edits
- "External integration without cognitive ownership" -> `src/adapters/`
- "What we measured and concluded" -> `experiments/`
- "What several variants should be compared on" -> `benchmarks/`
- "Whether software still follows a specification" -> `tests/`

If unsure, read [agent navigation](../engineering/AGENT_NAVIGATION.md) and [repository placement examples](../../examples/repository-placement.md).

## Minute 30-40: check whether the idea already exists

For significant work, do a small RAI scan.

Look for:

- existing packages;
- open-source research code;
- papers with usable implementations;
- compatible licenses;
- observable and reproducible solutions.

Do not spend days proving that every possible project on Earth is unsuitable.

The goal is enough search to avoid unnecessary reinvention.

## Minute 40-50: create the smallest useful record

Technical task?

Open an Issue if useful and create a short branch.

Scientific question?

Use the research Issue template or Discussion first if the question is still fuzzy.

Create an EXP only when the question is testable enough to document a baseline, metric, and minimally useful prototype.

## Minute 50-60: make your change reviewable

Before opening a PR, be able to answer:

- What changed?
- Why?
- How was it tested?
- Can the affected generation's cognitive behavior change?
- Which EXP justifies it, if needed?
- Are third-party licenses preserved?

That is enough to begin.

## You are allowed not to know

It is acceptable to write:

- "I don't understand this interface yet."
- "This metric may be wrong."
- "I found a conflicting paper."
- "The experiment produced no clear result."

The repository should make uncertainty visible rather than forcing fake certainty.
