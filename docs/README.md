# Documentation

This directory contains versioned project documentation.

## Where to start

If you are discovering the project, begin with `presentation/`:

1. [Project overview](presentation/01-project-overview.md)
2. [Repository tour](presentation/02-repository-tour.md)
3. [Research workflow](presentation/03-research-workflow.md)
4. [First-hour contributor guide](presentation/04-contributor-first-hour.md)

These files are intentionally short and should remain understandable without reading the entire technical specification.

## Documentation areas

### `presentation/`

Human-oriented entry points explaining the project, repository, workflow, and contribution model.

Use this area for documents that answer: **"What do I need to understand first?"**

### `architecture/`

Architecture-level descriptions of Individual Zero and its reference generations.

Use this area for:

- I0/I1/I2 generation manifests;
- structural interfaces;
- execution-cycle descriptions;
- relationships between major subsystems;
- architecture diagrams.

Do not store experiment-specific evidence here.

### `research/`

Research methods and explanatory documentation broader than a single experiment.

Use this area for:

- RAI methodology;
- experiment lifecycle;
- tests vs experiments;
- terminology;
- interpretation rules shared by several EXPs.

### `decisions/`

Architecture Decision Records (ADRs) supported by experimental evidence or explicit constraints.

An ADR records a shared decision after the evidence exists. It does not replace the evidence.

## Evidence location

The documentation directory explains the project. Scientific evidence belongs in `../experiments/`.

Reusable comparison protocols belong in `../benchmarks/`.

The live map of questions and experiments belongs in `../RESEARCH_MAP.md`.

## Licensing

Original non-code documentation is licensed under CC BY 4.0 unless a file states otherwise. See `../LICENSE-DOCUMENTATION`.
