# Engine generations: working map

This document reflects the live repository after #246 and the staged historical archive #251. It is an engineering map, **not** a declaration of scientific GO.

| Component | Authority | Location | Change policy |
| --- | --- | --- | --- |
| I0 | immutable reference | `src/i0/` | no changes in an I1 development PR |
| shared original Lab | historical reference runtime | `src/lab/` | no I1-specific behavior here |
| I1 | active artificial individual | `src/i1/`, `src/i1_overlays/` | versioned modifications with explicit real-life tests |
| I1 isolated Lab | generated from source and overlays | temporary `i1lab/` | never commit generated output |
| I1 birth | canonical natural identity | `i1lab.i1_birth.birth_i1` | no old experimental flags / hidden oracle |
| I1 test harness | real engine, SMOKE/FULL | `scripts/test_i1_ci.py` | assert mechanism and observed outcomes, not fixed choices |
| I0 history | non-authoritative for I1 | `archive/i0/` | byte immutable; manual restoration only |
| Registry | canonical generation locations | `config/engine-registry.json` | review when adding a generation |
| Archive inventory | original Git blob identities | `config/archives/i0-20261017.json` | never edit archived bytes to match a new engine |

## Development steps

1. Read `docs/engineering/START_HERE.md` and `config/engine-registry.json`. Verify the actual HEAD, open PRs and checks. Do not trust dated experimental outcomes as current-I1 truth.
2. Run `python scripts/check_engine_repository.py --json` to check preserved source boundaries and SHA-identified archives.
3. Run `python scripts/test_i1_ci.py --mode smoke --seed 246 --junit reports/i1-smoke.xml` and `--mode full`. Install the package with `python -m pip install -e .` first.
4. Change `src/i1/` and/or `src/i1_overlays/` intentionally. The canonical builder in `scripts/build_i1_fork.py` generates a private `i1lab` world. Treat its transformations and anchor failures as architecture contracts, not disposable nuisances.
5. Trace a real individual end to end: capture → bodily needs / temperament / lived history → candidate generation → Competition → Stage9 / Action Control → one WorldBody effect → memory and outcomes → paid consolidation → current-generation M11. Don't disable modules to make green tests.
6. Separate functional software proof from prospective scientific experiment; report seeds, birth identity, physical steps, UC, journal head, mortality and unknowns.
7. Keep irreversible death, first-person observability, genuine learning provenance and atomic publication. No rollback, resurrected life, hidden safety knowledge or artificial goals.

## Next engine generation: I2, I3, ...

**No new engine has been created yet.** For each proposed generation, keep `src/iN/` source separate from previous generations, define canonical constructor/identity, isolated shared runtime, typed contracts, a unique test harness, an explicit activation decision, and a separate CI workflow. Update the registry only after the generation is actually implemented. Do not rename I1 to I2 or inherit an experiment's measurements as normative requirements.

Use this promotion sequence: design proposal → architectural decision → isolated prototype → software invariants → new preregistered physical evidence → explicit activation. Record NO-GO and limitations. Keep older generations available for reproducible historical audits.

## Validation layers

- **Structural:** repository registry, immutable I0 / Lab tree, original archival SHA.
- **Software:** generated imports, authentic I1 birth, real physical action, starvation/thirst, irreversible death, owner custody, WAL/M11 recovery.
- **Behavioral:** real choices, learnable outcomes, temperament, cognitive publication and consolidation without forced scripts.
- **Scientific:** fresh independent mortal lives, controls and externally audited evidence. Never infer science from an all-green test badge alone.

Avoid creating generic names such as `latest_model` in runtime imports. Every life carries its generation/constructor/frozen config and authentic birth identity.
