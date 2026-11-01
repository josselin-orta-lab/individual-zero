# Document authority classes: current, research, historical

These categories are **reading guidance**, not a bulk migration or a change in scientific status. Keep existing citations, evidence SHA pins, experiments and archived bytes intact. A file's location or date alone does not establish its current correctness.

## 1. Current operational reference

The live registry at `config/engine-registry.json`, the generation's `engine.json`, accepted ADRs and current generation-owned `AGENTS.md` and handbooks state the intended rules. **Executable source** establishes what is actually installed and runnable. If source and documents disagree, report the discrepancy instead of inventing behavior.

Examples: `src/i1/docs/COGNITIVE_FLOW.md`, `src/i1/docs/STATUS.md`, `src/i2/docs/STATUS.md`, `docs/engineering/START_HERE.md`. Status pages are short routing surfaces, not proof that a development issue or scientific campaign succeeded.

## 2. Research and reproducible evidence

Research contracts, preregistrations, raw traces, negative results, analyses and independent verdicts answer *what was tested and observed*, conditional on protocol, data and exact source SHA. Evidence belongs in `docs/research/`, `experiments/`, benchmarks or generation-owned evidence indexes according to custody. The owning generation's current evidence index is the first stop for interpreting any claimed result.

A negative verdict is scientific information. An exploratory fixture does not become a confirmatory trial when reused in a PR. No held-out or hidden-world information may be routed into a living individual's first-person input.

## 3. Historical implementation and superseded decisions

Dated investigations, old issue reports, historical status ledgers, unapproved proposals and I0 archive records document the lineage. They remain discoverable for reproducibility but do **not** override active contracts or reenable old execution paths.

Examples: `src/i1/docs/STATUS_HISTORY.md`, `src/i2/docs/STATUS_HISTORY.md`, `archive/i0/`, dated `docs/research/` reports and unreconciled proposal files.

## Authority conflict and navigation procedure

1. **Current selection:** use `config/engine-registry.json`, current branch SHA and the generation's `engine.json`. A dated status report cannot override live state.
2. **Implementation claims:** check generation-owned source and its relevant contracts and tests. If they disagree with docs, report a discrepancy, not a silent compatibility fallback.
3. **Scientific claims:** navigate using the [original-path study indexes](../research/studies/README.md), then inspect the actual preregistration, original records, custody, controls and independent review. Filename hints and Git blob hashes provide routing/provenance, not scientific validation.
4. **Historical custody:** preserve `archive/i0/` and the [419-file historical root baseline](../research/studies/HISTORICAL_ROOT_FILES.md). A broken-looking historical link is a review lead, not permission to rewrite evidence.
5. **Choosing work:** use the [research coordinator](RESEARCH_COORDINATOR.md) plus current GitHub blockers to select a minimal intervention and explicitly state what remains `NOT_EVALUATED`.

## Practical rule for agents

For a targeted engineering change: consult the registry and contracts, task-scoped routing, real code paths and targeted tests. For a scientific assertion: independently inspect evidence, protocol and verdict. Treat all dated PRs, screenshots and status reports as snapshots, not live HEAD. Never delete or relocate historical sources by name-pattern alone; check provenance, imports, links and reproducibility first.
