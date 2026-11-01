# Agent navigation: find the right authority quickly

This is a **navigation index**, not a second architectural specification. It should require minutes rather than an archaeological dig through PR history. All paths below are repository-root-relative.

## Two-minute routing

| If your task is... | Start here | Then verify |
| --- | --- | --- |
| Determine what is currently active | `config/engine-registry.json` | current HEAD and generation `engine.json` |
| Decide the next scientific intervention | `docs/engineering/RESEARCH_COORDINATOR.md` and `config/research-program.json` | dated evidence, source-pinned dossiers, current issues and unreviewed gaps |
| See the architecture, causal path and intervention owners | `docs/architecture/ATLAS.md` | `docs/architecture/ENGINE_GENERATIONS.md`, generation-owned Stage maps and real call sites |
| Inspect I2 G1 proposals versus G2 tests | `docs/architecture/proposals/README.md` | dated proposal headers and `src/i2/docs/STATUS.md` |
| Modify the living I1 engine | `src/i1/AGENTS.md`, `src/i1/docs/README.md` | `src/i1/docs/STATUS.md`, code, targeted tests |
| Understand I1 causal flow | `src/i1/docs/COGNITIVE_FLOW.md` | `src/i1/docs/STAGES_AND_INTERFACES.md` |
| Change memory, needs, sleep or M11 | `src/i1/docs/README.md` | mechanism guide, observed source paths and invariants |
| Evaluate an I1 scientific claim | `src/i1/docs/EVIDENCE_MATRIX.md` | original preregistration, exact SHA and evidence |
| Work on I2 research fixtures | `src/i2/AGENTS.md`, `src/i2/docs/README.md` | `src/i2/docs/STATUS.md`, `tests/i2/` |
| Propose/promote an engine | `docs/engineering/ENGINE_PROMOTION.md` | `docs/decisions/ADR-0001-strict-generation-autonomy.md` |
| Inspect archived I0 | `docs/architecture/ENGINE_GENERATIONS.md` | `config/archives/i0-20261017.json` without modifying history |
| Contribute or file an issue | `CONTRIBUTING.md` | issue/PR templates and code owner policy |
| Run engineering scripts | `docs/engineering/START_HERE.md` | `src/iN/engine.json` and `docs/engineering/SCRIPT_INVENTORY.md` |
| Find tests by generation and tooling | `tests/TEST_LAYOUT.md` | `python tools/repository_layout.py inventory --kind tests --match <topic>` |
| Find frozen or historical archives | `archive/README.md` | I0 custody manifest and `python tools/repository_layout.py inventory --kind archives` |
| Find research reports and audits | `docs/research/README.md` | original evidence and `python tools/repository_layout.py inventory --kind docs --match <study>` |

For research priorities use `python tools/research_coordinator.py recommend` and inspect `python tools/research_dossiers.py gaps` before choosing a code route. For broad historical lookup use `python tools/research_corpus.py report --top 8`; its lexical matches are unreviewed. Only then open the [Architecture Atlas](../architecture/ATLAS.md) for ownership and implementation paths.

## Source of truth

**Registry** says *which generation is active*. **Engine contract + real code** say *what is installed and executable*. **ADRs** say *what is allowed*. **CI on an exact SHA** says *what software was checked*. **Experimental evidence** says *what was measured*, and only a reviewed scientific gate can say *what was established*. An older issue, PR, historical status ledger, theoretical proposal or test fixture never overrides these.

## Lightweight documentation checks

Use `python tools/check_repo_navigation.py --scope current` for current guides. `--scope all` inspects historical Markdown as well and reports its broken references as warnings, without rewriting archived research. Add `--strict-historical` when an exhaustive failure report is explicitly required. This check never instantiates an individual or proves cognition.

## Working boundaries

- I0 is immutable research history. I1 has its own cognition, runtime, Lab, tests and existing born identities. I2 has independent, non-living synthetic prototypes only. No historical runtime imports, carried-over life state or compatibility modes for successor engines.
- `src/i1/docs/STATUS.md` and `src/i2/docs/STATUS.md` are **short current reading surfaces**, with earlier campaign ledgers preserved alongside as `STATUS_HISTORY.md`.
- `docs/research/` includes many historical experiment records. Read the current evidence index and the original, dated protocol **before** drawing a conclusion. `experiments/` contains experiment conventions and formal records; its sparse index is not evidence that no research has occurred.
- For a narrow fix, read the specific owner contract and its direct tests. Don't load every historical file into agent context.

## Minimum reproducible handoff

`generation | main/branch SHA | objective | modified paths | invariants | tests and status | observed data | scientific status | remaining risks | issue/PR`

Keep `NOT_RUN` and `NOT_OBSERVED` explicit. Never claim CI for a different SHA or infer scientific success from tests.
