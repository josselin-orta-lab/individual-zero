# Engine generations: working map

This document reflects the live repository after #246 and the staged historical archive #251. It is an engineering map, **not** a declaration of scientific GO.

| Component | Authority | Location | Change policy |
| --- | --- | --- | --- |
| I0 | immutable reference | `src/i0/` | no changes in an I1 development PR |
| I0 Lab | frozen historical reference | `archive/i0/lab/` | byte-identical to former common Lab |
| I1 | active artificial individual and version-owned Lab | `src/i1/`, `src/i1/lab/`, `src/i1/runtime/` | versioned modifications with explicit real-life tests |
| I1 isolated Lab | generated from `src/i1/lab/` and `src/i1/runtime/` | temporary `i1lab/` | never commit generated output |
| I1 birth | canonical natural identity | `i1lab.i1_birth.birth_i1` | no old experimental flags / hidden oracle |
| I1 test harness | real engine, SMOKE/FULL | `scripts/test_i1_ci.py` | assert mechanism and observed outcomes, not fixed choices |
| I0 history | non-authoritative for I1 | `archive/i0/` | byte immutable; manual restoration only |
| Registry | canonical generation locations | `config/engine-registry.json` | review when adding a generation |
| Archive inventory | original Git blob identities | `config/archives/i0-20261017.json` | never edit archived bytes to match a new engine |

## Development steps

1. Read `docs/engineering/START_HERE.md` and `config/engine-registry.json`. Verify the actual HEAD, open PRs and checks. Do not trust dated experimental outcomes as current-I1 truth.
2. Run `python scripts/check_engine_repository.py --json` to check preserved source boundaries and SHA-identified archives.
3. Run `python scripts/test_i1_ci.py --mode smoke --seed 246 --junit reports/i1-smoke.xml` and `--mode full`. Install the package with `python -m pip install -e .` first.
4. Change `src/i1/` and/or `src/i1/runtime/` intentionally. The canonical builder in `scripts/build_i1_fork.py` generates a private `i1lab` world. Treat its transformations and anchor failures as architecture contracts, not disposable nuisances.
5. Trace a real individual end to end: capture → bodily needs / temperament / lived history → candidate generation → Competition → Stage9 / Action Control → one WorldBody effect → memory and outcomes → paid consolidation → current-generation M11. Don't disable modules to make green tests.
6. Separate functional software proof from prospective scientific experiment; report seeds, birth identity, physical steps, UC, journal head, mortality and unknowns.
7. Keep irreversible death, first-person observability, genuine learning provenance and atomic publication. No rollback, resurrected life, hidden safety knowledge or artificial goals.

## Next engine generation: I2, I3, ...

**No new engine has been created yet.** For each proposed generation, keep `src/iN/` source separate from previous generations, define canonical constructor/identity, isolated generation-owned Lab, typed contracts, a unique test harness, an explicit activation decision, and a separate CI workflow. Update the registry only after the generation is actually implemented. Do not rename I1 to I2 or inherit an experiment's measurements as normative requirements.

Use this promotion sequence: design proposal → architectural decision → isolated prototype → software invariants → new preregistered physical evidence → explicit activation. Record NO-GO and limitations. Keep older generations available for reproducible historical audits.

## Validation layers

- **Structural:** repository registry, immutable I0 source and archived I0 Lab trees, original archival SHA.
- **Software:** generated imports, authentic I1 birth, real physical action, starvation/thirst, irreversible death, owner custody, WAL/M11 recovery.
- **Behavioral:** real choices, learnable outcomes, temperament, cognitive publication and consolidation without forced scripts.
- **Scientific:** fresh independent mortal lives, controls and externally audited evidence. Never infer science from an all-green test badge alone.

Avoid creating generic names such as `latest_model` in runtime imports. Every life carries its generation/constructor/frozen config and authentic birth identity.

## Lab ownership per generation

Each motor version owns its own laboratory: the current I1 Lab is `src/i1/lab/`, and the frozen I0 Lab is `archive/i0/lab/` (original Git tree SHA `18f5aabdd49a5cc2f7cae3b0996bf958a0843028`). The unversioned `src/lab/` path is removed. The only exception is a temporary restoration of I0's original Lab in a disposable CI checkout to run archived I0 tests against their original imports. This is not an active shared Lab. Future I2 needs `src/i2/lab/` and its own tested custody; no engine should silently use another generation's Lab. The canonical I1 runner retains the generated `i1lab` import namespace for persisted birth compatibility, but its sources now come exclusively from I1.

`individual-zero` remains a legacy I0 bootstrap demonstration, not a natural I1 CLI or scientific gate. Natural I1 must use its versioned birth entrypoint.
