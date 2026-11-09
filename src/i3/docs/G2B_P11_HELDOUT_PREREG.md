# I3 G2b: P1.1 versus P1 on held-out Worlds (preregistration)

**Filed on 5 November 2026 before running held-out Worlds H1-H3.** Protocol
`i3-g2b-p11-heldout-v1`; `src/i3/lab/heldout_p11.py` defines Worlds,
execution and verdict computation. Each version is executed once; outcomes
are published separately, irrespective of the verdict.

## Question

Does the P1.1 correction (known sleep restores energy and vigilance in
self-projection) perform at least as well as P1 on unseen Worlds, without
reintroducing the defect of returning to known water too late?

## Conditions

- **Versions:** P1 commit `1068935`; P1.1 is the preregistration commit.
- **Genomes:** `generation_zero(201)` through `(230)`; one life per genome
  per World, life seed 2000 + n, horizon 400. The versions use identical
  genomes and seeds for a paired comparison.
- **Held-out Worlds**, specified after P1.1 development ended:

| World | Situation |
| --- | --- |
| `g2b-h1-hidden-spring` | 16 x 16; water four cells north, out of sight; food nearby |
| `g2b-h2-round-trip` | Water at the starting point, food ten cells away; the individual must travel, eat and return to drink |
| `g2b-h3-dried-spring` | Finite adjacent spring A (four drinks); spring B 14 cells away and out of sight; food near both |

## All required criteria for adopting P1.1

1. **Non-inferiority per World:** P1.1 survivors at step 400 >= P1 survivors
   minus three (out of 30).
2. **Target defect (H2):** thirst deaths after at least one drink:
   P1.1 <= P1.
3. **G2 regression:** using the three original G2 Worlds for declared
   regression only, at least 8/10 lives drink in each.
4. **Engineering:** identical replay of every P1.1 life; mean <= 1 ms/step.

Verdict `ADOPT_P1_1` only if all hold; otherwise
`REJECT_P1_1_KEEP_P1` and revert to P1.

Descriptive, without a criterion: use of the distant spring in H3 (strategy
revision).

*English translation. The original preregistration is preserved byte-for-byte
under `archive/i3/original-language-records-2026-11-09/src/i3/docs/G2B_P11_HELDOUT_PREREG.md`.*