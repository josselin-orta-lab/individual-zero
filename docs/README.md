# Documentation

This directory contains versioned project documentation.

## Where to start

If you are discovering the project, begin with `presentation/`:

1. [Project overview](presentation/01-project-overview.md)
2. [Repository tour](presentation/02-repository-tour.md)
3. [Research workflow](presentation/03-research-workflow.md)
4. [First-hour contributor guide](presentation/04-contributor-first-hour.md)

These files are intentionally short and should remain understandable without reading the entire technical specification.

## Agent route and generation ownership

For task-oriented agents start at [agent navigation](engineering/AGENT_NAVIGATION.md), then use the [Architecture Atlas](architecture/ATLAS.md) to trace generation ownership, real I1 causal flow and proposal boundaries; [I1's handbook](../src/i1/docs/README.md) documents the active engine, and [I2's handbook](../src/i2/docs/README.md) documents non-living proposal fixtures. Their own `docs/STATUS.md` files hold short current summaries; `STATUS_HISTORY.md` preserves earlier updates. Global documentation does not override generation-owned source or contracts.

## Physical location and custody

Generation-owned [I1](../src/i1/docs/README.md) and [I2](../src/i2/docs/README.md) handbooks live alongside their source. Dated studies remain under [research](research/README.md) or generation-owned scientific sources. [The archive index](../archive/README.md) distinguishes frozen I0 from historical references, and [the test index](../tests/TEST_LAYOUT.md) routes software checks. Preserve original evidence citations and source blob identity before relocating files.

To locate paths without loading entire directories, run `python tools/repository_layout.py inventory --kind docs --match stage12 --limit 15` (or use `--kind tests` / `--kind archives`). This is read-only navigation, not a scientific verdict.

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

The documentation directory explains the project. Scientific evidence may be recorded in generation-owned studies and under `research/` as well as formal `../experiments/` records. Locate it via the active [evidence matrix](../src/i1/docs/EVIDENCE_MATRIX.md) and original provenance, not by assuming an empty `experiments/` index means no studies.

Reusable comparison protocols belong in `../benchmarks/`.

The [research map](../RESEARCH_MAP.md) defines cross-cutting axes and points to the [global research coordinator](engineering/RESEARCH_COORDINATOR.md), [incremental corpus index](engineering/RESEARCH_CORPUS.md) and [source-pinned dossiers](engineering/RESEARCH_DOSSIERS.md). They support agent navigation and evidence-gap review; they are **not** a live census or an independent scientific verdict. Always inspect the [original dated studies](research/README.md), [active I1 evidence matrix](../src/i1/docs/EVIDENCE_MATRIX.md) and [current GitHub issues](https://github.com/josselin-orta-lab/individual-zero/issues).

## Licensing

Original non-code documentation is licensed under CC BY 4.0 unless a file states otherwise. See `../LICENSE-DOCUMENTATION`.
