# Candidate-J software falsifier: results

**VERDICT: `CANDIDATE_J_DEFECT`. Under ADR-0018, Stage 1 closes NEGATIVE.**

- Protocol: [STAGE1_CANDIDATE_J.md](../../STAGE1_CANDIDATE_J.md), frozen by
  #1210.
- Implementation choices: [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md),
  committed with the code before execution (`15e8d3d`, 00:18 UTC).
- Single execution: 00:24–00:25 UTC on 9 November 2026, 74 s, from that
  commit. Machine output: [results.json](results.json).

No World, no life. The ADR-0017 moratorium is untouched.

## Custody note

A first background launch at 00:18 UTC was terminated by the sandbox after
about one minute. It produced no output, no file and no partial result, and
nothing from it was read. The execution above is the only one that produced
results.

## J0: projector validity, the defect stop

The canonical oracle is the #1155 per-step Decimal end-to-end simulation,
applied to the same Candidate-J valuation. The comparison covers 160 states
(K80 and P80) × 18 arms, that is 2,880 decisions and 12,960 option scores. In
2,088 of those decisions the oracle's top-two gap exceeds 1e-3.

| Projector | Max abs value error | Top mismatches (gap > 1e-3) | J0 |
| --- | ---: | ---: | --- |
| `event_quadratic` | 0.0555 | 48 | fail |
| `event_local_quadratic4` (declared fallback) | 0.0178 | 0 | fail (value error > 0.01) |

All 48 `event_quadratic` mismatches lie where inherited hope sits near the
decision boundary:

- **arms:** 16 at ω = 0.25, κ = 0.05; 28 at ω = 0.25, κ = 0.10; 4 at ω = 0.5,
  κ = 0.20;
- **fixtures:** P80 20, K80 28;
- **low channel:** food 24, water 24.

The fallback projector is **decision-equivalent** to the oracle in all 2,088
decisive states. It still exceeds the frozen value tolerance of 0.01.

Both projectors fail J0, so the frozen verdict table gives
`CANDIDATE_J_DEFECT`. As the protocol prescribes, J1–J4 were not evaluated.

## What this establishes

- **A sharp projection-precision dependence.** Candidate-J's first-contact
  decisions flip under the cheaper accurate projector exactly where hope is
  moderate. Where hope tips a decision, its margin is of the same order as the
  projection error.
- **The projector that reproduces the oracle's decisions is the expensive
  one.** In the pre-design sandbox, `event_local_quadratic4` costs 42 to 107
  simulated steps per plan evaluation, against 9 for P1.3's `chunk_end`. J4 was
  not run, but on those figures alone Candidate-J would very likely have
  exceeded the 2.5× cost wall even if J0 had passed. That expectation is not a
  measurement.
- **Not established:** first-contact capacity, need-sensitivity, cost, or any
  survival or lineage property. The capacity question (J3) remains unobserved.

## Consequence under ADR-0018

ADR-0018, decision 4, closes Stage 1 on the first software verdict other than
`CANDIDATE_J_CAPACITY_SHOWN`. Decision 5 fixes the negative closure:

- **P1.3 remains the reference.**
- Recorded result of Stage 1: under convex distress with absorbing death,
  stakes-only evaluation does not bootstrap first contact (symmetric ignorance
  is aversive). An inherited expectation can, but in the Candidate-J form its
  decisions depend on projection precision that current affordable projectors
  do not deliver.
- **P1.3's curiosity is recognized as an innate disposition**: its form is set
  by the designer and its weight (`beta_u`) is heritable. This is option B of
  the [first-contact decision note](../../STAGE1_FIRST_CONTACT_DECISION.md).
- No Stage-1 candidate follows. Candidate-K or any other Stage-1 architecture
  is excluded.
- **Stage 2 is unblocked on P1.3.** Its first question, when a precise and
  costly evaluation is worth its price, is precisely the one Candidate-J ran
  into.

Changing the J0 tolerance or the projector after this verdict would be a
post-hoc rescue, and ADR-0018 forbids it. The ADR-0017 moratorium still applies
to every lived panel.
