# I1: ready-to-launch world presets

The natural I1 world laboratory has six checked-in immutable-input JSON scenarios at `src/i1/lab/world_presets/`. They define external physical initial conditions, not subjective knowledge, commands, rewards, trained priors, H1/H2 policies or scientific results.

| Preset | Environment |
| --- | --- |
| oasis | Food, water and material at birth |
| foraging | Resource collection requiring local exploration |
| dry-valley | Scarce water and distant supplies |
| empty-land | No replenishment, genuine physical deprivation |
| hazard-edge | Creatures, resource, danger and lethal terrain |
| blocked-route | Obstacles between the individual and replenishment |

After merging the stacked PRs into the default branch, launch via GitHub **Actions → I1 manual preset world laboratory → Run workflow**. Before merge, inspect the draft workflow and run the Python CLI in a checkout of the PR branch; GitHub may not expose newly added manually dispatched workflows until they exist on the default branch. Choose a world, seed, steps (1–300), independent lives (1–3), and `wal` or `m11` custody. Or locally:

```bash
python tools/run_i1_world_preset.py --list
python tools/run_i1_world_preset.py --preset foraging --validate-only
python tools/run_i1_world_preset.py --preset foraging --seed 246 --steps 24 --lives 1 --custody wal --output-dir reports/foraging-246
```

A new output directory is mandatory. The runner uses canonical `birth_i1` or `birth_i1_m11`, advances via unforced `run_step`, and **never retries, replays, or resurrects a dead individual**. The world geometry, local perception, physics digest, birth identity and journal receipts are preserved in JSON for independent review. M11 reports include SQLite audit and terminal-recovery refusal. The report separates operator-only world truth from perceptible birth conditions.

These runs are on-demand and are not scientific GO or acceptance tests against earlier broken experimental cohorts. GitHub artifacts are retained for 14 days. Do not share private operator-only truth with the individual's decision modules.

The preset map is intentionally fixed per file: changing `--seed` changes the reproducible **individual birth identity**, not the layout or resources. To change environmental conditions, choose a different registered preset or introduce a reviewed additional JSON preset. The `--steps` argument caps simulation steps and never dictates actions; survival, feeding, exploring and death are observations, not success guarantees.
