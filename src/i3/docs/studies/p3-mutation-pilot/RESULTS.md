# I3 P3: original preregistered mutation-only lineage pilot, selection results

**Status: SOFTWARE/PROVENANCE PASS; NO SCIENTIFIC GO.**
This is the first and only P3 selection run under the prospective
[P3 preregistration](../../P3_PILOT_PREREG.md) merged **before** execution.
Source pinned at `52476fec3f39a7fd70bf611877b01d9c13d26009`,
opportunity schedule `230cd653f0a8e580682b351fa3474b9f4dbd9f3e98e7eec1fa61361c0e7289db`.
The complete original selection is [Actions run 42181938835](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42181938835);
one subsequent **verification-only** run [42182975466](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42182975466)
reconstructed all G2 genomes without executing a new life. The earlier
failed verification job [42182858104](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42182858104)
was a syntax error in the post-run custody checker, not in P3 execution,
and remains visible. No negative outcome was discarded.

## Technical custody

| Evidence | Verified |
| --- | --- |
| Independently initialized populations | 4 |
| Parent-selection arms | Selected by lifetime persistence; random-parent control |
| Generations | G0, G1, G2 |
| Complete, observed lives | **864 / 864** |
| Unique selection world keys | **72 / 72** |
| Deaths / censored survivors (all generations/arms) | **614 / 250** |
| Missing life evidence hashes | **0** |
| G0 paired arms identical (genomes and observed results) | Yes |
| Reconstructed, genome-digest-verified G2 genotypes | **48 / 48** |
| Validation/P4 reserve worlds opened | **0** |

The full original JSON evidence (unmodified, gzip-compressed) is
[`selection-full.json.gz`](selection-full.json.gz); the
[summary](selection-summary.json) and [48 full frozen G2 genomes](G2_GENOMES.json)
are in this same directory. All original and derivative SHA-256 receipts are
preserved. The original artifact stays available in GitHub Actions through
its documented retention window, but this repository archive provides
lasting custody independently of the artifact expiry.

Original uncompressed selection JSON SHA-256:
`e45df7a494b01b02846128f5c93b30987a383edd65bd5884d6690740da11103e`.
Internal canonical source-data digest:
`76bed12cce89b051b59542a425d29e53725475146504bced97660523fcf73040`.
Frozen G2 JSON file SHA-256:
`6cfb0ac7c0dd603f67c2a08863e6e8ef2183b51db19bb2ede05ba4e371610419`.
Frozen G2 canonical internal digest:
`4663421628f726dde75a3c2f48494e506ceec0fba593dab3441cab8d0da88d2b`.
The frozen gene values were reconstructed from G0 seeds, recorded parent
slots and mutation seeds under the **same unchanged genome algorithm**,
then compared to all original genotype digests. It is not a second experiment.

## Selection-environment outcome: censored survivors / 144 lives per arm and generation

| Generation | Selected-parent | Random-parent | Difference |
| --- | ---: | ---: | ---: |
| G0 (paired identical genomes) | 34 / 144 | 34 / 144 | 0 |
| G1 | 37 / 144 | 50 / 144 | **-13** |
| G2 | 50 / 144 | 45 / 144 | **+5** |

There is **no monotonic evidence** of a consistently beneficial selected
lineage. The G1 selected arm does worse. At G2 the difference is
+5/144 = **+3.47 percentage points**, but it is a selection-cohort
outcome, not a prospective held-out gain.

### Four independent population-level contrasts at G2

| Population | Selected / 36 | Random / 36 | Paired difference |
| --- | ---: | ---: | ---: |
| 0 | 14 | 11 | +3 |
| 1 | 16 | 13 | +3 |
| 2 | 12 | 13 | -1 |
| 3 | 8 | 8 | 0 |

Only two populations favor selection, one favors random parenting, and
one ties. The mean paired difference is **+1.25 survived lives per
population of 36**. The sample SD of these four differences is
approximately **2.06 lives**. An exploratory 95% Student-t interval is
roughly **[-2.03, +4.53] lives per population** (n=4; strong small-sample
assumptions). It spans harm and benefit; it is not a confirmatory claim.

### Cognitive economics (G2 only)

| Metric | Selected | Random-parent |
| --- | ---: | ---: |
| Cognitive energy paid, all 144 lives | 24,816.658 | 20,856.462 |
| Cognitive vigilance paid, all 144 lives | 30,344.266 | 25,372.476 |
| Physical inactivity steps | 5,143 | 8,060 |
| Deaths | 94 | 99 |

These are **actual realized** costs, not normalized computational budgets.
The selected arm uses more cognition and experiences fewer inactive ticks
while also achieving five additional censored survivors in selection.
Do **not** attribute the survival difference to selection efficiency or
to learning: genes change cognitive demand, each life has its own history,
and there is no learning ablation in P3. Both arms received the same
initial world/body/life-seed opportunities and per-unit payment laws.

## Scientific interpretation and next steps

P3 supports the *technical feasibility* of carrying an exclusively genetic
lineage over three generations without transmitting experiential state.
It does **not** establish sustained natural selection, generalized
fitness advantage, individuality from lived history, or a causal
contribution of learning. The four population outcomes and G1 decline
are explicit adverse/null evidence.

All G2 genotypes are now frozen under `G2_GENOMES.json`. P4 must first
preregister a genuinely prospective validation study on unopened
`validation` worlds, including matched random-parent controls, independent
population-level uncertainty, and targeted within-life learning ablations
that preserve orientation. It must never choose genotypes based on the
validation outcomes or reopen the P4 reserve without a separate protocol.
Historical P1/P2 results and active I1 are untouched. I3 remains an
unregistered proposal, and **no scientific GO is granted**.
