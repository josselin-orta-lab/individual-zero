# I1 Lab: environment, execution and observation

This directory is **owned by generation I1**, not shared with I0 or I2. The active natural-I1 engine composes its own Lab and runtime; see [I1's engine contract](../engine.json), [runtime map](../docs/STAGES_AND_INTERFACES.md) and [agent instructions](../AGENTS.md).

## What belongs here

I1-specific world and body interfaces, Stage runtime substrate, physical observations, UC accounting, technical journals, reproducible fixtures and read-only research instrumentation. These are **not** permission to feed operator-only or hidden-world information into a born individual. A mechanism under lab/ can participate in an active I1 runtime; do not assume that all files are inert merely because the directory is called Lab.

## Locate the actual execution

- Active birth and natural runtime: source under [../runtime/](../runtime/) and the entrypoints declared in [../engine.json](../engine.json).
- Physical boundaries and Stage ownership: [STAGES_AND_INTERFACES.md](../docs/STAGES_AND_INTERFACES.md).
- Observability and reproducibility: [OBSERVABILITY.md](../docs/OBSERVABILITY.md) and [WORLD_PRESETS.md](../docs/WORLD_PRESETS.md).
- Tests: [tests/i1](../../../tests/i1/README.md) and the registered validation suites.

## Historical bootstrap files

Some copied files, including cli.py and early neutral execution examples, still describe the **I0 bootstrap** and may import I0 in those noncanonical paths. The command individual-zero is the historical I0 demonstration, **not** I1's active natural birth. Do not use those examples as I1 runtime instructions or silently activate them. Their future code-level disposition requires a separate inspected change with tests.

For current placement guidance see [repository placement](../../../examples/repository-placement.md). For the historical CLI see [running the I0 bootstrap](../../../docs/presentation/06-running-the-bootstrap.md).

**Rule:** I1 owns its actual WorldBody, cognition, UC, state and authenticated M11 contract. No shared active src/lab, no obsolete-engine fallback, no borrowed living state. Software tests alone do not demonstrate autonomous learning.
