# Repository tour

This page explains where things live without requiring you to understand all of I0.

## Top-level view

```text
individual-zero/
├── docs/
├── examples/
├── src/
├── experiments/
├── benchmarks/
├── tests/
├── RESEARCH_MAP.md
└── CONTRIBUTING.md
```

## `docs/`

This is versioned project documentation.

- `presentation/`: short onboarding documents.
- `architecture/`: reference architecture and generation-level descriptions.
- `research/`: shared research method.
- `decisions/`: ADRs recording shared architectural decisions.

Documentation explains the system. It is not the primary storage location for scientific evidence.

## `src/lab/`

The Lab contains neutral infrastructure for running and observing research.

Examples:

- run orchestration;
- logging;
- seeds;
- metrics;
- artifact collection;
- reproducibility helpers.

A useful question is:

> Would this still be useful if I0 were replaced by a different architecture?

If yes, it probably belongs in the Lab.

## `src/adapters/`

Adapters connect external projects to I0 interfaces.

Examples:

- converting a third-party memory API into the format expected by I0;
- translating external model outputs;
- dependency lifecycle and error handling.

Adapters should translate. They should not quietly become the place where cognition is redesigned.

## `src/i0/`

This is where the reference Individual Zero behavior lives.

- `interfaces/`: cognitive contracts;
- `architecture/`: global coordination and structural implementation;
- `modules/`: cognitive mechanisms;
- `config/`: reference configuration.

If a piece of code directly determines how I0 thinks or acts, this is usually where it belongs.

## `experiments/`

An experiment keeps the evidence for a scientific question.

Typical contents:

```text
EXP-0047/
├── README.md
├── config/
├── run/
└── results/
```

The experiment README should tell a future contributor:

- what was asked;
- what was tested;
- what baseline was used;
- how to reproduce it;
- what was observed;
- what decision followed.

Reference code should not be permanently copied into an experiment folder.

## `benchmarks/`

Benchmarks define reusable comparison conditions.

A benchmark can be shared by several EXPs.

Examples include:

- a memory retention scenario;
- a delayed decision task;
- a robustness scenario;
- a common metric definition.

A benchmark should not contain conclusions that belong to one experiment.

## `tests/`

Tests verify software behavior against a known expectation.

Examples:

- a parser returns the documented structure;
- a reset restores the expected state;
- an adapter preserves required fields;
- a refactor keeps outputs unchanged.

Tests are necessary, but they do not establish that a cognitive mechanism is scientifically better.

## `RESEARCH_MAP.md`

This file maps active scientific work.

It lists:

- research axes;
- active questions;
- EXPs;
- architectural candidates;
- major external dependencies.

The Research Map is not a backlog of every possible idea.

## `examples/`

Examples are intentionally illustrative.

They show how the project workflow should look without pretending that the example result is real project evidence.

Each example should be clearly marked as non-authoritative.

## A quick placement exercise

Where should these go?

**"Measure the duration of each cognitive cycle."**

Usually: `src/lab/`.

**"Choose which memory item is recalled."**

Usually: `src/i0/`.

**"Translate I0's memory query into Library X's API."**

Usually: `src/adapters/`.

**"Compare Library X with the current memory mechanism."**

Usually: an EXP, possibly with an adapter.

**"Verify that the adapter preserves timestamps."**

Usually: `tests/`.

That distinction is the backbone of the repository.
