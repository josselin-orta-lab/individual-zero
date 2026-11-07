# Stage 1 projection Candidate F: result

**Frozen verdict: `CANDIDATE_F_PASSES_LAB_SOFTWARE_GATE`.**

Protocol: [STAGE1_PROJECTION_CANDIDATE_F.md](../../STAGE1_PROJECTION_CANDIDATE_F.md).

Exact checked head: `240d88835b64a98647202ec726f7b246280fa6ae`.
CI run: `42393650198`.

Laboratory integration only. No World, life or omega rerun.

## Frozen 486-case result

| Metric | Candidate F | Gate |
| --- | ---: | ---: |
| Max decision bias vs #1117 oracle | **1.02736695e-05** | <=1e-3 |
| Projection-equivalent invariant | **3.77789498e-07** | <=1e-3 |
| Max direct final-body error | **0.0** | <=1e-10 |
| Direct paid units min / mean / max | **16 / 86.6111 / 112** | max <255 |
| Max prefix-value error vs oracle | 1.24868236e-05 | descriptive |

All frozen gates pass.

## Interpretation

Candidate F leaves Candidate E's sparse projector unchanged and changes only
the state continuity across explicit plan simulation and the bootstrap.

The result collapses Candidate E's ~1.5e-2 end-to-end error by roughly three
orders of magnitude:

- E max decision bias: ~0.01545;
- F max decision bias: ~0.00001027.

The projection-equivalent invariant similarly falls from ~0.01533 to
`3.78e-07`.

This confirms the causal diagnosis:

**the sparse local quadratic-4 approximation was already sufficient; the
failure was the float -> Decimal state seam.**

The remaining candidate error is comfortably below the preregistered 1e-3
software gate while retaining a maximum direct projection cost of 112 versus
255 for the oracle.

## Decision

Candidate F is authorized for a separate explicit opt-in Mind integration
slice.

That integration must reproduce this laboratory candidate without changing
the default reference path. It must verify:

- default/reference parity when the mode is off;
- candidate-value parity with this frozen laboratory implementation;
- identical Candidate-E direct projection cost;
- no hidden World/life coupling.

Only after that integration passes may Stage-1 forecast ceilings be frozen for
Candidate F and the existing omega falsifier be rerun.

No reference adoption is authorized.

## Verification

Run `42393650198`:

- Python 3.11 PASS;
- Python 3.12 PASS;
- **663 I3 tests** PASS;
- **7 structural tests** PASS;
- navigation **532/532**, zero errors/warnings on Python 3.11.

No scientific or architecture promotion follows.
