# Contributing to Individual Zero

Thank you for contributing.

## Contribution paths

### Technical
For bugs, documentation, tooling, Lab work, tests, behavior-preserving optimizations, and compatible adapter maintenance.

Typical flow: **Issue if useful -> short branch -> change -> tests -> pull request -> merge**.

### Scientific
For a hypothesis, comparison, or behavior change that must be measured.

Typical flow: **Question -> EXP -> RAI -> minimal prototype -> test -> results -> integration decision**.

### Architectural
For changes to a shared cognitive contract, the global cycle, or several subsystems.

Typical flow: **Question -> EXP -> results -> ADR -> integrate in I(n) or open candidate I(n+1)**.

An ADR records a decision. It never replaces an experiment.

## Placement

- If code describes how I0 thinks or acts, put it in `src/i0/`.
- If it only runs or observes, put it in `src/lab/`.
- If it connects I0 to an external dependency, put it in `src/adapters/`.
- Put scientific evidence in `experiments/`.
- Put reusable comparison scenarios in `benchmarks/`.
- Put software verification in `tests/`.

## When an EXP is required

Create or join an EXP when work tests a scientific hypothesis, compares mechanisms, changes I0 reference cognitive behavior, replaces a reference cognitive component, or alters the global cognitive cycle or structural relationships.

An EXP is normally not required for documentation, CI, packaging, logging without behavior change, behavior-preserving refactors, clear bug fixes, equivalent performance work, compatible adapter maintenance, or ordinary software tests.

If unsure, open an Issue describing expected impact. Create an EXP only after identifying a measurable scientific question.

## RAI

Before significant implementation, perform a time-bounded **Reuse, Adapt, Implement** scan.

Ask whether a credible solution already exists, whether it matches the hypothesis, whether its license is compatible, whether it is observable and reproducible, and what its integration/maintenance costs are.

Choose:
- **REUSE** when a solution fits;
- **ADAPT** when a useful mechanism needs a limited interface or modification;
- **IMPLEMENT** when no satisfactory solution exists or the mechanism itself is under study.

## Branches

Branches are temporary and describe a change, not a long-lived research axis.

Examples:

```text
fix/logger-timestamp
feat/simulation-reset
exp/0047-memory-replay
docs/contribution-guide
chore/repository-maintenance
```

## Pull requests

Explain:
- what changed;
- why;
- how it was tested;
- whether I0 cognitive behavior can change;
- related EXP, Issue, ADR, or benchmark.

A PR changing reference cognitive behavior must point to the EXP that justifies it.

## Tests vs experiments

Software tests verify known expected behavior. Scientific experiments test hypotheses under defined conditions. One does not replace the other.

## Negative results

Keep negative and inconclusive results when they provide reproducible information.

## Licensing

Contributed source code is provided under Apache-2.0. Original documentation, research text, diagrams, and written experimental reports are provided under CC BY 4.0 unless stated otherwise. Preserve third-party licenses and attribution.

## Conduct

Critique ideas, mechanisms, methods, and evidence freely. Treat contributors respectfully. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
