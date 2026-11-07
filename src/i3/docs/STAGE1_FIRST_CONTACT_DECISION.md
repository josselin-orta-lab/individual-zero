# Stage 1 — first contact: decision required before any implementation

**Status: DECIDED, 7 November 2026: the owner chose option A.** The
implementation starts with a frozen software falsifier,
[STAGE1_OMEGA_SOFTWARE_FALSIFIER.md](STAGE1_OMEGA_SOFTWARE_FALSIFIER.md). That
document amends the shift direction (uniform, not along the distress gradient)
and defers the genome schema change to its own slice.

## Blocker

Before any personal experience of a resource or action effect, information
value is structurally too small to justify a risky unsupported trial. Evidence,
all on the reference-preserving path:

| Evidence | Result |
| --- | --- |
| 50/51 development lives (frontier water, information only) | 5/12 never experience water, never activate information, all die |
| Zero-mean radius-100 prior, 80 synthetic states | 0/80 trials selected |
| #1101, exact explorer semantics | 0/80 epistemic trial selections; max information 0.0006 |
| #1103 + reuse characterization (carried food) | 0/27 meal promotions at 1–8 represented future uses; information saturates |
| P5c (registered, n=4 populations) | without the curiosity term: 4/288 survivors vs 110/288 |

Mechanism: with a zero-mean ignorance prior and a convex predicted-distress
stake, an unknown trial has a negative expected immediate value (Jensen). Its
only credit is the value of information, which is bounded by how much the best
plan differs between imagined effects and barely grows with represented reuse.
First contact therefore never pays for itself. The P1.3 curiosity term pays for
it instead, as a designer-shaped addend.

## Options

**A. Heritable ignorance-prior disposition (recommended to test).** One generic
gene `ω ∈ [−1, 1]` shifts the mean of the existing zero-mean unsupported-effect
prior along the individual's own current distress gradient. The scale is the
personal recent RMS (#1097), so the shift is `ω × RMS`.

- `ω = 0` is exactly today's prior, `ω < 0` is innate pessimism and `ω > 0` is
  innate hope that untried actions relieve what currently hurts.
- No action name, resource identity, map or World input. The individual still
  decides through predicted distress, which now includes the trial's risk.
- Generation 0 draws `ω` symmetrically, so only lifetime persistence can move
  it, as in ADR-0014. A designer-set positive `ω` would be curiosity in disguise
  and is excluded.
- This is a genome change: owner decision required.

**B. Keep P1.3 curiosity for first contact.** Declare the Stage-1 replacement
falsified for first contact, keep information value where it acts (post-contact
prudence), and leave the curiosity addend as an acknowledged designer term. No
new mechanism, and an honest negative.

**Rejected.**

- Independent per-channel signs break the 2–3 branch cap.
- Patching recurrence is not causal, as measured above.
- A smaller designer-chosen prior radius is calibration.
- Forced trials, resource injection and Competition rewrites are policy rules.

## Falsifiers if A is approved

1. **Software, no world.** On the #1101 water grid and the carried-food grid:
    - `ω = 0` reproduces current results exactly;
    - some `ω > 0` selects pre-contact trials;
    - a realized harmful personal history still allows rejection after contact;
    - every computation is paid.
2. **Selection, under ADR-0015, on prospectively frozen fresh worlds.** `ω`
   evolves freely from a symmetric generation 0.
    - The first-contact hypothesis fails if selected genomes do not shift `ω`
      upward, or do not beat the `ω := 0` ablation at equal genomes.
    - It also fails if survival depends on `ω` only in water-poor families, which
      would signal ecology-specific calibration.

Option B is not pursued. A's falsifier 1 passed (`CAPACITY_SHOWN`), but it exposed a P1.3 projection plan-length bias that must be fixed first: [results](studies/stage1-omega-software-falsifier/RESULTS.md). The genome and the live path stay unchanged until then.
