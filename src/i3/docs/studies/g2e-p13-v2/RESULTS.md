# I3 G2e: P1.3 versus P1.1 on funded v2 under selection (result)

**Preregistered decision: `ADOPT_P1_3`.** Protocol:
[G2E_P13_V2_PREREG.md](../../G2E_P13_V2_PREREG.md), commit `31c4429`;
method [ADR-0015](../../../../../docs/decisions/ADR-0015-i3-portes-sous-selection.md).
Both arms use the same v2 physics with cognition prepaid (#1004).
Data: `BASE.json`, `P1_3.json`, `g2-*.json`, `reference.json`,
[verdict.json](verdict.json).

**Execution note.** The P1.3 arm was interrupted at the end of a session
before writing any result, then restarted from the beginning with identical
source and seeds ([EXECUTION_NOTE.txt](EXECUTION_NOTE.txt)). This completed
the one preregistered run; it was not a second experimental attempt.

## Primary criterion: five selected genomes per arm, 100 new held-out Worlds per family

| | Reference (P1.1-v2) | P1.3-v2 | Worlds better / worse |
| --- | --- | --- | --- |
| Strategy revision (R), out of 500 | 163 | **270** | 62 / 9 |
| General (dev), out of 500 | 201 | 208 | 30 / 20 |
| **Total, out of 1,000** | 364 | **478** | 92 / 29, **p = 4 x 10^-9** |

Floors passed: identical G2 regression (10/10 drinkers in each of the
three Worlds, both arms), exact replay, **no unfunded step**, identical
Worlds and mean execution time 1.27/1.28 ms per step (limit 2 ms).

## Descriptive observations

| | Reference | P1.3-v2 |
| --- | --- | --- |
| Selected R lives that depleted the nearby source | 325 | 346 |
| Then drank at the distant source | 75 (23%) | **206 (60%)** |
| Revision latency median (quartiles), steps | 124 (96-140) | 134.5 (82-182) |
| Random genome per World, R/dev survivors out of 100 | 21 / 35 | 35 / 39 |
| Funding-related inactive-step fraction (selected) | 10.6% | 7.8% |
| Selection survival for the five best candidates out of 60 | 27, 27, 27, 26, 25 | 33, 32, 32, 31, 30 |

Laboratory probes were **neither validated nor cost-matched**. The reference
searcher survives 95/100 R Worlds and 70/100 dev Worlds. It pays around
0.07 energy per step versus about 0.55 for an I3 individual under v2;
these are not comparable ceilings.

## Interpretation

Revisable place beliefs greatly increase how often a strategy is revised
(60% versus 23% of lives that deplete the near source), but **not how
quickly**: median latency among revising lives remains comparable. The gain
on general conditions is small (+7/500). The improvement also appears among
random genomes.

Overall survival is markedly lower on funded v2 than v1, since thought
has a real cost and approximately one step in ten cannot fund cognition.
This is the stake-of-self property ADR-0014 intended. It also argues for
letting the lineage select cognitive spending (`n_base`, `h_max`,
`m_max`) instead of designer tuning.

Limits: generation-zero genomes selected among 40; no lineage;
two laboratory-generated families; no scientific learning claim.

## Consequences

- **P1.3-v2** becomes the reference (genome `i3-genome-v3`,
  `belief_rate` gene).
- Continue plan #1002 with P2 (validate generators and probes, match costs,
  separate development/selection/validation/reserve), then P3 (lineage pilot).

*English translation. Original preserved unchanged at
`archive/i3/original-language-records-2026-11-09/src/i3/docs/studies/g2e-p13-v2/RESULTS.md`.*