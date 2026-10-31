# Contributing to Individual Zero

Thank you for contributing.

The project is designed so that a new contributor can start useful work without first learning the entire cognitive architecture.

## Before you start

For a quick orientation, read:

- [Project overview](docs/presentation/01-project-overview.md)
- [Repository tour](docs/presentation/02-repository-tour.md)
- [Research workflow](docs/presentation/03-research-workflow.md)
- [First-hour contributor guide](docs/presentation/04-contributor-first-hour.md)
- [Examples](examples/README.md)

Then read [the agent navigation map](docs/engineering/AGENT_NAVIGATION.md) and [strict generation autonomy](docs/decisions/ADR-0001-strict-generation-autonomy.md), and identify the generation and nature of your proposed change.

Before submitting or merging a PR, read the [access and merge policy](docs/governance/GITHUB_ACCESS_POLICY.md). Public forks may propose changes, but only explicitly authorized maintainers may merge into the canonical protected `main`. A PR template and CODEOWNERS file are not substitutes for enforced GitHub protection rules.

## Contribution paths

### Technical contribution

Use this path for:

- bugs;
- documentation;
- tooling and CI;
- Lab improvements;
- software tests;
- performance work with equivalent behavior;
- compatible adapter maintenance;
- refactoring without expected scientific behavior change.

Typical flow:

**Issue if useful -> short branch -> change -> tests -> pull request -> merge**

A scientific EXP is not required when no scientific behavior change is expected.

### Scientific contribution

Use this path when a hypothesis, comparison, or behavior change must be measured.

Typical flow:

**Question -> EXP -> RAI -> minimal prototype -> test -> results -> pull request / integration decision**

Experimental code remains isolated until reviewed evidence justifies integrating it into the appropriate active generation.

### Architectural contribution

Use this path when experimental results support a change to a shared cognitive interface, the global execution cycle, or several subsystems.

Typical flow:

**Question -> EXP -> results -> ADR -> integrate in I(n) or open candidate I(n+1)**

An ADR records a shared decision. It does not replace an experiment.

## Put work in the right place

| Location | Put here | Do not put here |
| --- | --- | --- |
| `src/iN/lab/` | generation-owned world, simulation and observations | shared living-world state across generations |
| `src/adapters/` | external API conversion, integration, configuration, compatibility handling | new cognitive logic disguised as integration |
| `src/i0/`, `archive/i0/` | frozen, separately reproducible historical reference | active I1 or I2 changes |
| `src/i1/` | active I1 cognition, runtime, Lab and handbook | obsolete-generation runtime imports |
| `src/i2/` | inoperative I2 research fixtures and proposal contracts | living engines, born states or motor authority |
| `experiments/` | question, RAI, protocol, reproduction commands, results, decision | permanent copies of reference code |
| `benchmarks/` | reusable scenarios, metrics, reference data, comparison rules | conclusions specific to one EXP |
| `tests/` | unit, integration, compatibility, regression tests | scientific interpretation |

A practical placement rule:

- if the change affects active I1 cognition or its living Lab, use `src/i1/` and its generation-owned tests;
- if it concerns non-living I2 research, use `src/i2/` without activating an engine;
- if it preserves historical I0 research, document it without mutating frozen sources;
- if it connects an external dependency without owning cognition, use `src/adapters/`.

See [repository placement examples](examples/repository-placement.md).

## Decide whether an EXP is required

Create or join an EXP when the work is intended to:

- test a scientific hypothesis;
- compare mechanisms or implementations;
- change the active generation's reference cognitive behavior;
- justify replacing a reference cognitive component;
- alter the global cognitive cycle or structural relationships.

An EXP is normally not required for:

- editorial documentation changes;
- packaging and development scripts;
- logging or metrics that do not change behavior;
- refactoring with equivalent expected behavior;
- clearly identified bug fixes;
- equivalent performance optimizations;
- compatible adapter maintenance;
- ordinary software tests.

If unsure, open an Issue describing the expected impact. Create an EXP only when a measurable scientific question has been identified.

## Use RAI before significant implementation

Before a meaningful prototype or expensive implementation, perform a time-bounded **Reuse, Adapt, Implement** scan.

Ask:

1. Does a credible implementation or research project already exist?
2. Does it actually match the hypothesis?
3. Is its license compatible with intended use and redistribution?
4. Can its behavior be observed, instrumented, and reproduced?
5. What are the integration, maintenance, security, and replacement costs?

Choose:

- **REUSE** when a solution already fits the need;
- **ADAPT** when a useful mechanism needs an interface or limited modification;
- **IMPLEMENT** when no satisfactory solution exists or the mechanism itself is under study.

See [RAI method](docs/research/rai.md) and the [RAI example](examples/rai-example.md).

## Branches

Branches are temporary and describe a change. They do not represent long-lived research axes.

Examples:

```text
fix/logger-timestamp
feat/simulation-reset
exp/0047-memory-replay
docs/contribution-guide
chore/repository-maintenance
```

Research axes live in `RESEARCH_MAP.md`. Experimental evidence lives in `experiments/`.

## Pull requests

A pull request should explain:

- the affected generation and its exact base SHA;

- what changed;
- why;
- how it was tested;
- which generation's cognitive behavior can change;
- the related EXP, if any;
- the related Issue, ADR, or benchmark, if any.

When a pull request changes reference cognitive behavior, it must point to the EXP that justifies the change.

Keep pull requests focused enough to review and reproduce.

## Software tests and scientific experiments are different

A software test verifies a known specification.

A scientific experiment tests a hypothesis or compares variants under defined conditions.

Both matter, but one does not replace the other.

See [Experiments vs tests](docs/research/experiments-vs-tests.md).

## Negative results

Negative and inconclusive results should be preserved when they contribute reproducible information.

A failed hypothesis can still prevent the next contributor from repeating the same dead end.

## Licensing and attribution

By contributing, you agree that:

- contributed source code is provided under Apache License 2.0;
- original documentation, research text, diagrams, and written experimental reports are provided under CC BY 4.0 unless stated otherwise;
- third-party material must retain its original license and attribution.

Do not commit material that cannot legally be redistributed by the project.

## Conduct

Critique mechanisms, assumptions, methods, and results freely. Treat contributors respectfully.

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
