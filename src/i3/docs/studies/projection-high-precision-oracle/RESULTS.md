# Stage 1 high-precision projection state oracle: result

**Verdict: oracle not authorized.**

Classification:
`EVENT_SEGMENTATION_DIFFERS_FROM_HIGH_PRECISION_ORACLE`.

Protocol: [STAGE1_PROJECTION_HIGH_PRECISION_ORACLE.md](../../STAGE1_PROJECTION_HIGH_PRECISION_ORACLE.md).

Software only. No World, life, study index, Candidate E or omega rerun.

Exact checked head: `87d6ad65f7d2180bc9b6ac9e4107509d44d43c60`.
CI run: `42390463269`.

## Frozen 486-case result

| Comparison | Max prefix error vs oracle | Max decision bias vs oracle | Projection-equivalent invariant gap | Max final-body error |
| --- | ---: | ---: | ---: | ---: |
| event-exact | 0.0181372811 | **0.0181372811** | 0.0181372811 | 0.4000000000 |
| historical repeated-float per-step | 0.0154528426 | **0.0154528426** | **8.88e-16** | 0.4000000000 |

The high-precision oracle's own projection-equivalent invariant gap is
**0.0153340562**, far above the frozen numerical-equivalence tolerance
`1e-10`.

All high-precision projections cost exactly 255 simulated units.

## Interpretation

#1115 correctly identified a real floating accumulation artifact at one vital
zero boundary. But replacing **projection state arithmetic only** with
high-precision arithmetic is not a coherent global numerical semantics.

The projection-equivalent fixture is the decisive clue. Its explicit wait
transition is still executed by ordinary P1.3 `Mind.simulate` float
arithmetic, while the subsequent bootstrap projection uses high-precision
state arithmetic. The two halves of what should be one equivalent transition
therefore no longer share one numerical representation.

The historical repeated-float per-step path preserves this particular
projection-equivalent invariant almost exactly because both the explicit wait
and the projection recurrence use the same ordinary float arithmetic. That does
not erase #1115's death-boundary artifact; it shows that numerical semantics
cannot be changed in `project()` alone.

Likewise, event-exact remains materially different from the high-precision
projection-only oracle. The result does not justify treating either one as the
new truth.

## Decision

- do not authorize this projection-only high-precision oracle;
- historical Candidate C/D gates remain unchanged;
- default remains `chunk_end`;
- do not freeze Candidate E yet;
- do not rerun omega;
- the next numerical protocol, if pursued, must cover the **entire simulated
  state transition chain** used for comparison, including explicit plan
  transitions and bootstrap projection, under one arithmetic semantics.

That next protocol should remain laboratory-only. It must first recover the
projection-equivalent invariant before it can define truth for a new candidate.

## Verification

Run `42390463269`:

- Python 3.11: PASS;
- Python 3.12: PASS;
- **641 I3 tests** PASS;
- **7 structural tests** PASS;
- navigation checks PASS on Python 3.11.

No scientific or architecture promotion follows.
