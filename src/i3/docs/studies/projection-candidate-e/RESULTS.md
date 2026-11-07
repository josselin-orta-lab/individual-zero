# Stage 1 projection Candidate E: result

**Frozen verdict: `NO_CANDIDATE_PROMOTED`.**

Protocol: [STAGE1_PROJECTION_CANDIDATE_E.md](../../STAGE1_PROJECTION_CANDIDATE_E.md).

Exact checked head: `9c02e94d71859ea574af2810b0847e775103ab34`.
CI run: `42393249318`.

Software only. No World, life, study index or omega rerun.

## Frozen 486-case result

| Metric | Candidate E | Gate |
| --- | ---: | ---: |
| Max decision bias vs #1117 oracle | **0.0154526985** | <= 0.001 |
| Projection-equivalent invariant | **0.0153340598** | <= 0.001 |
| Max direct final-body error | **0.0** | <= 1e-10 |
| Direct paid units min / mean / max | **16 / 86.6111 / 112** | max <255 |
| Max direct projection-value error | **7.5442452e-05** | descriptive |

Candidate E passes the state and cost criteria but fails the two end-to-end
decision criteria.

## Interpretation

The sparse local projector itself is not the problem.

Directly, Candidate E:

- reproduces the authorized oracle's final body exactly;
- stays within `7.55e-05` in projected value;
- reduces direct reward evaluations from 255 to at most 112.

That direct projection error is already below the scientific decision-bias
target of `1e-3`.

The failure appears only after Candidate E is invoked from the ordinary
`Mind.simulate` plan chain:

- explicit plan transitions still evolve body state in ordinary float;
- Candidate E then switches the bootstrap to the canonical Decimal event state.

This recreates the same representation boundary diagnosed in #1116. The
projection-equivalent invariant rises to `0.015334`, almost exactly the
projection-only high-precision signature.

Therefore reducing the local block below 4, adding nodes, or changing the
quadratic would target the wrong mechanism.

## Decision

- Candidate E is rejected unchanged.
- Do **not** tune the block size in this PR.
- Do **not** rerun omega.
- Retain the opt-in E projector and its direct accuracy/cost evidence.
- The next candidate must carry one canonical state representation through
  both explicit simulated plan transitions and Candidate E's sparse bootstrap.

This is an integration-semantics failure, not evidence against local
quadratic-4 compression.

A new candidate must be frozen separately before it is evaluated.

## Verification

Run `42393249318`:

- Python 3.11 PASS;
- Python 3.12 PASS;
- **658 I3 tests** PASS;
- **7 structural tests** PASS;
- navigation **532/532**, zero errors/warnings on Python 3.11.

No scientific or architecture promotion follows.
