# I3 G2e: P1.3 versus P1.1 on funded v2 under selection (preregistration)

**Filed before any execution.** Method:
[ADR-0015](../../../docs/decisions/ADR-0015-i3-portes-sous-selection.md).
Plan: [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md), item 1 (P1.3).
Frozen code: `src/i3/lab/selection_gate_v2.py`. One execution per arm.

## Question

On the **same** v2 physical substrate (cognition paid in advance, #1004)
in both arms, does revisable place belief (P1.3 with one `belief_rate` gene)
improve survival among selected genomes, particularly when a source runs dry?

## Arms

| Arm | Commit | Cognition |
| --- | --- | --- |
| Reference (P1.1-v2) | This preregistration commit (cognition identical to `eb12a0f` on `main`) | Cumulative place-presence beliefs |
| P1.3-v2 | `474259d` (branch `i3/p1.3-v2`) | Beliefs revised at inherited `belief_rate` (genome `i3-genome-v3`, 30 genes) |

Common genes retain equal values between arms (checked on one reference
genome). G2d results on the v1 substrate remain archived and are not used.

## Protocol

- **Candidates:** `generation_zero(6000)` through `(6039)`; **select**
  five highest-persistence genomes on `dev` development Worlds 100-129
  (horizon 300) and `R` development Worlds 100-129 (horizon 400).
- **Evaluation:** completely new, never executed reserved seeds
  **1,000,200-1,000,299** for families `dev` (horizon 300) and `R`
  (horizon 400), under neither substrate previously. Life seed 80000 + k.
  Statistic: survivors among five selected genomes per World.
- **Revision latency (R):** from the step when the individual takes the final
  drink at the nearby spring (first personal evidence of depletion) to its
  first drink at the distant spring. No revision if the latter never occurs.

## Frozen decision rule (`decide`)

Adopt P1.3-v2 if:

1. selected total (out of 1,000) exceeds reference under a one-sided exact
   World-level sign test with p <= 0.05;
2. within either family, the loss is no more than 15 survivors out of 500;
3. floors: in every G2 World (generation-zero genomes), no more than one
   fewer drinker than reference; exact replay of the best genome; no unfunded
   step; identical World digests; mean <= 2 ms/step as an engineering guard
   for this machine (v2 was about 1 ms/step in development).

Otherwise retain the reference. Failure retains P1.1 but does not bar
construction of the selection pilot (plan item 1).

## Descriptive, not a decision criterion

Survival of one random genome per World; revision latency distribution and
revision share among lives that depleted the nearby spring; fraction of
funding-related inactive steps; ranking of all 40 candidates; lab probes
(**neither validated nor cost-matched**, P2) on selection/evaluation Worlds.

*English translation. The original preregistration is preserved byte-for-byte
under `archive/i3/original-language-records-2026-11-09/src/i3/docs/G2E_P13_V2_PREREG.md`.*