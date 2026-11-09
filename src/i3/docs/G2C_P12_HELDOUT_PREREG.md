# I3 G2c: P1.2 versus P1.1 on generated held-out Worlds (preregistration)

**Filed on 5 November 2026 before using the reserved seeds.** Protocol
`i3-g2c-p12-heldout-v1`, executable `src/i3/lab/heldout_p12.py`. One
execution per version.

## What P1.2 changes

1. **Place beliefs revised at a heritable rate** (`belief_rate`): an
   observation moving average replaces accumulation, so an exhausted source
   ceases to be believed available.
2. **Heritable exploration** (`reach`): zero means nearest frontier (P1.1);
   >= 1 means heading-consistent rays extending into the unknown. Their value
   is the number of cells they would reveal, with stable heading identity
   introducing persistence.

Genome `i3-genome-v2`: both new genes are sampled last, so v1 and v2
genomes with the same seed share all v1 genes (paired comparison).

## Declared development (development Worlds only)

| Measurement | P1.1 | P1.2 |
| --- | --- | --- |
| Generated `dev` family, seeds 0-99, random genomes | 59/100 | 59/100 |
| Capacity: best of 40 genomes on 30 `dev` Worlds (100-129) | 23/30 | 25/30 |
| Systematic reference searcher on the same 30 Worlds | 22/30 | Not evaluated |
| `dev-failing-well`: survivors / distant source used | 6 / 5 out of 30 | 20 / 18 out of 30 |
| `dev-wide-field`: survivors | 0/30 | 9/30 |
| `dev-far-home`: survivors | 26/30 | 15/30 |

The loss in the `dev-far-home` corridor comes from rays pointing toward
unknown cells beyond unreachable outer boundaries. Exploration was therefore
made heritable rather than prescribing one universal choice.

## Conditions

- **Versions:** P1.1 commit `2657f3b`; P1.2 is this preregistration commit.
  Both use an identical generator (digest checked).
- **Held-out Worlds:** seeds 1,000,000-1,000,099 in family `R` (strategy
  revision: nearby finite source, distant hidden source, horizon 400) and
  family `dev` (horizon 300). Family R was written after development ended;
  only construction on one development seed was checked, without a life.
- **Genomes:** on World k, `generation_zero(70000 + k)`; life seed
  80000 + k.

## All required criteria for adopting P1.2

- **A. Strategy revision (superiority):** in R, more P1.2 survivors than
  P1.1 and a one-sided exact sign test over discordant pairs with p <= 0.05.
- **B. Generality (non-inferiority):** on `dev`, P1.2 survivors >= P1.1
  survivors minus five.
- **C. G2 regression:** at least 8/10 drinkers on each of the three G2 Worlds.
- **D. Engineering:** identical replays and mean <= 1 ms/step.

Verdict `ADOPT_P1_2` or `REJECT_P1_2_KEEP_P1_1`.

**Descriptive, not a criterion:** reference searcher survival; survival of the
best genome per version selected from development Worlds 100-129 (P1.1: 6003,
P1.2: 6002), evaluated on held-out Worlds.

*English translation. The original preregistration is preserved byte-for-byte
under `archive/i3/original-language-records-2026-11-09/src/i3/docs/G2C_P12_HELDOUT_PREREG.md`.*