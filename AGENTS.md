# Individual Zero: instructions for development agents

These instructions govern work on this repository, not the cognitive rules
of a living individual. Before acting, read:
1. `config/engine-registry.json` and the active `src/iN/engine.json`.
2. `docs/engines/iN/STATUS.md` and `docs/engines/iN/ARCHITECTURE.md`.
3. `docs/engineering/START_HERE.md` and relevant ADRs.
4. The real GitHub branch HEAD, open PR dependencies and latest CI; never
   assume status from a previous conversation or a dated report.

## Isolation and source of truth

- I0 is a frozen reference: `src/i0/` and `archive/i0/lab/` may NOT be
  rewritten as part of an I1 campaign. The original archive is SHA-pinned.
- Every generation owns its Lab. I1 uses `src/i1/lab/`, runtime
  `src/i1/runtime/` and cognitive modules `src/i1/modules/`.
  Never recreate a shared production `src/lab/`. Restore it in an
  isolated test checkout only for legacy I0 compatibility.
- I1 is active. I2 is not registered or activated. Never create a living
  generation from a skeleton alone or carry over individual memory, safety
  labels, weights, or historical experimental results as normative truth.
- `engine.json` specifies declared interfaces and obligations; the runtime
  and real evidence establish actual behavior. The global registry indexes
  registered generations. Update both together and run the structural guard.
- I1 currently builds the isolated import namespace `i1lab` using
  `scripts/build_i1_fork.py`. Do not rename persistence modules or rewrite
  born identities without explicit compatibility, M11 cold-recovery, and
  generated-artifact parity evidence.

## Invariants that must never be bypassed

- The individual learns only from its own observable experience, bodily
  needs, temperament and lived history. No oracle, hidden hazards, unearned
  prebirth knowledge or forced action choices.
- Death is irreversible. No restoration of a living individual's previous
  cognitive or physical state, no resurrection and no postmortem stepping.
- M11 must refuse uncertain or noncanonical generations, unregistered
  owners, contradictory publications and unfinished durable intent.
- Account for UC expenditure honestly. Do not disable cognition, protection
  layers, owners, learning or testing to obtain green CI.
- H1/H2 and older experimental cohorts are not scientific oracles for the
  current natural I1. Old evidence is historical, never acceptance criteria
  for emergent I1 behavior.

## Workflow for each implementation

1. Verify scope: engine, files, contract, baseline SHA and PR dependencies.
2. Open one focused PR or commit series. State expected causal and durability
   impacts, including what must stay unchanged.
3. Add tests for the changed invariants (normal, negative and failure cases),
   and update `docs/engines/iN/STATUS.md` with outstanding risks.
4. For I1 run:
   `python scripts/check_engine_repository.py --json`
   `python scripts/check_engine_contracts.py --json`
   `python -m unittest discover -s tests/i1 -p 'test_*.py' -v`
   `python scripts/test_i1_ci.py --mode smoke --seed 246`
   `python scripts/test_i1_ci.py --mode full --seed 247`
   and the M11 / generated-output regression tests on GitHub.
5. Check Python 3.11 AND 3.12 Actions for the exact new commit, preserve
   provenance and report blockers. Do not claim a merge or success on an
   untested SHA. Integrate stacked PRs strictly in dependency order.
6. Separate software, behavioral and scientific results. Green tests prove
   their tested properties only, not consciousness or scientific GO.

## Future engines

Use `python tools/new_engine.py --generation I2 --parent I1 --output <dir>`
for a no-write preview. Explicit `--apply` only creates a *proposal* scaffold;
it does NOT register, activate, import or instantiate I2. Each generation needs
an independent Lab, source, contracts, tests, CI and new scientific evidence.
