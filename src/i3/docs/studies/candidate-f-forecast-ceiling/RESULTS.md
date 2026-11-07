# Stage 1 Candidate F forecast ceiling: result

**Verdict: `CANDIDATE_F_FORECAST_CEILING_PASS`.**

Protocol: [STAGE1_CANDIDATE_F_FORECAST_CEILING.md](../../STAGE1_CANDIDATE_F_FORECAST_CEILING.md).

Exact checked head: `413cb727f4148a7f084628b0bba173f8897a22c5`.
CI run: `42394859198`.

## Frozen result

Reference projection quote remains exactly **8**.

Candidate F common projection quote is **256**:

`1 + sum(1,2,4,8,16,32,64,128)`.

This is a conservative forecast-body ceiling, not an actual work receipt.

Across the 486 already-frozen direct projection cases, Candidate F actual work
remains:

- min 16;
- mean 86.61111111111111;
- max 112.

All are below the structural quote.

## Omega-zero kernel proof

The complete 80-state #1101/#omega software grid was executed at omega=0 with
integrated Candidate F and the new common ceilings.

- evaluated: **80/80**;
- unfunded: **0**;
- every actual work vector <= its quoted common ceiling: **yes**;
- max actual simulated steps in one complete water-future calculation:
  **561**;
- max quoted common ceiling simulated steps:
  **1293**.

The difference is intentional. Forecast-body accounting is conservative while
physical/model work remains charged from the actual sparse execution.

## Reference and rejected modes

- `chunk_end` quote remains 8;
- `trapezoid` quote remains 8;
- rejected `event_quadratic` and `event_quartic` fail closed instead of
  silently borrowing the old 8-unit quote.

All active Stage-1 forecast formulas that formerly embedded
`len(model.proj_chunks)` now use the shared mode-aware quote.

## Decision

The already-frozen omega software falsifier may now be rerun with Candidate F.

Because Candidate F has state-dependent sparse work, the rerun must preserve a
common forecast ceiling across omega arms. Actual paid work may legitimately
vary with the predicted state trajectory and must be reported rather than
forced equal.

No reference adoption is authorized.

## Verification

Run `42394859198`:

- Python 3.11 PASS;
- Python 3.12 PASS;
- **676 I3 tests** PASS;
- **7 structural tests** PASS;
- navigation **532/532**, zero errors/warnings on Python 3.11.

No World, life or scientific allocation was opened.
