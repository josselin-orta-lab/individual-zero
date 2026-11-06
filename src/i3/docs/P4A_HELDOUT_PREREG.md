# I3 P4a: prospectively registered held-out validation of frozen P3 G2

**Study:** `i3-p4a-g2-heldout-v1`. **Status: REGISTERED BEFORE FIRST
VALIDATION LIFE**, not a scientific GO. P4b is a different future experiment.

### Immutable preregistration custody

- **Exact P4a implementation commit:** `01132efef08edb23143c4618d1a2491b23026eb4`.
- **Prospective validation schedule SHA-256:** `7d5785eca2f65b1562c2dca22bc4bd65f930250e8a0b032df18a030b22b38289`.
- Frozen G2 file SHA-256: `6cfb0ac7c0dd603f67c2a08863e6e8ef2183b51db19bb2ede05ba4e371610419`.
- Frozen G2 canonical payload SHA-256: `4663421628f726dde75a3c2f48494e506ceec0fba593dab3441cab8d0da88d2b`.
- Original P3 selection JSON SHA-256: `e45df7a494b01b02846128f5c93b30987a383edd65bd5884d6690740da11103e`.
- Prospectively verified code [run #42185090272](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42185090272): 120 I3 tests on Python 3.11 and 3.12, isolation guards and 48 frozen genotypes preflight. **No validation world opened during these checks.**

## Primary question and null

Do the G2 genetic dispositions produced by selection for persistence generalize
to **unopened** ecologies, compared with equally reproduced and mutated G2
genomes descended from randomly chosen parents? Primary null: no advantage
of selected-parent over random-parent G2 lines on fresh environments. Negative
or mixed signs support neither generalization nor a scientific GO.
P3's G1 decline and G2 difference +5/144 inside selection are contextual
evidence, **not** a reason to adjust this protocol.

This is **not** a learning-effect experiment or an individuality test.
No changed cognition, no evolution/mutation during P4a, and no selection of a
best genome before, during or after the validation cohort.

## Population design (locked before looking)

- Independent experimental units: **4 populations** (IDs 0..3).
- Arms: `selected` vs `random_parent`, each population containing exactly
  six previously frozen G2 genomes per arm, for 48 fixed genotypes in all.
- Ecologies: `stable`, `depletion`, `pulse`, two untouched fresh validation
  worlds per population and family; **24 unique world keys**, each shared across
  both arms and all six fixed genotypes in the same population.
- P2 reserved validation seeds: **30000 to 30023** (indices 0..23).
  Validation world index:
  `6*population + 2*family_index + repeat`, family index in
  (stable=0, depletion=1, pulse=2), repeat 0/1.
- Validation life seed = **160000 + world index** and is identical for all
  compared genotypes in both arms on that world.
- Horizon = **400 physical steps**. Total = 4 × 2 × 6 × 3 × 2 =
  **288 complete life histories**, at most **115,200 physical ticks**.
- Strict v2 body law, source, initial body and environment opportunities
  are equal across the arms. Actual realized cognitive energy, vigilance and
  inactivity can differ by genotype and life, and **must be reported**;
  do not force equal realized computation.
- No repeated life after an adverse outcome, no rescue or replacement, no
  tuning based on any P4a validation result. The P4 reserve seeds
  1200000–1200199 are **not** opened. P3 selection worlds are not reopened.

## Analysis specified before exposure

Primary endpoint: **fraction of censored survivors at physical step 400** for
each arm and independent population, each population/arm having 36 lives
(6 genotypes × 3 ecology families × 2 repeats). For each population:
`(selected survivors - random-parent survivors) / 36`.
Report all four differences, their mean, observed range, and an exploratory
two-sided 95% Student-t interval (df=3, t-critical 3.182) for the mean
population-level difference, with the tiny n=4 and non-normality limitations.
Never treat the 288 individual lives as statistically independent.

Secondary descriptive outcomes: ecology-specific deaths/censoring, total lived
steps, cognitive energy/vigilance paid, physical inactivity steps, learning
updates and replays, with full provenance; group these by population, arm and
ecology. No secondary endpoint licenses cherry-picking or a scientific GO.

A zero/negative overall mean or inconsistent signs must be explicitly
described, not hidden. A positive mean whose interval includes zero remains
inconclusive; even a positive interval alone would support only a narrow
held-out G2 survival contrast on this ecology mix, not causal learning or
human-like individuality. Any life-ending zero-vital-channel event is real
death; reaching 400 steps alive is **censored**, not dead.

## Program and validity gates

The only authorized execution is:
`I3_P4A_SOURCE_SHA=01132efef08edb23143c4618d1a2491b23026eb4`
`I3_P4A_SCHEDULE_SHA=7d5785eca2f65b1562c2dca22bc4bd65f930250e8a0b032df18a030b22b38289`
`I3_P4A_APPROVED_PROTOCOL=i3-p4a-g2-heldout-v1`
with `PYTHONPATH=src python -m i3.lab.p4a_validation --run OUTPUT.json`.

The code must verify exact Git HEAD, schedule, both frozen-G2 digests, 48
unmodified genotypes and all 24 allocations before the **first** validation
world is created. The prospective preregistration Git commit must be merged
into `main` **before** this separate one-shot workflow runs, while the workflow
checks out the *older pinned executable commit*. GitHub Actions must retain
the complete original life receipts, summary and SHA256 receipts as immutable
artifacts. If a physics/funding/provenance error occurs, mark
`ENGINEERING_INVALID`, preserve all failed logs and *do not* relabel it as
mortality, amend the cost model or quietly rerun the study.

P4b learning and individuality work is **NOT_RUN**; it requires a separate
prospective registration and untouched cohorts. P4a's result cannot be used
to redesign or select G2 genotypes. I1 remains active, I3 unregistered.
