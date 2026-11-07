# Stage 1 canonical event segmentation: result

**Event boundaries cleared for Candidate E.**

Classification:
`CANONICAL_EVENT_SEGMENTATION_MATCHES_ORACLE`.

Protocol: [STAGE1_CANONICAL_EVENT_SEGMENTATION.md](../../STAGE1_CANONICAL_EVENT_SEGMENTATION.md).

Exact checked head: `c98d148c80b5d4a4374718c7cf8703f9960f08f1`.
CI run: `42392801147`.

## Frozen 486-case result

- maximum projected-value error vs #1117 oracle:
  **3.410605131648481e-13**;
- maximum final-body error:
  **0.0**;
- event segments per direct projection:
  **6 / 12.928 mean / 22**;
- paid endpoint evaluations:
  **255 / 255 / 255**.

The 1e-10 gate passes by more than two orders of magnitude.

## Interpretation

With the same represented-float model values and one canonical Decimal state,
the structural event boundaries reproduce the authorized direct oracle.

Therefore the earlier event-aware failures were not evidence that threshold,
restoration or death events are intrinsically unsuitable. The remaining
compression problem is isolated to how distress is sampled/interpolated inside
the now-validated event segments.

This diagnostic deliberately evaluated every discrete endpoint, so it is not a
candidate accounting scheme and offers no cognitive-cost reduction by itself.

## Consequence for Candidate E

Candidate E may now preserve these exact event/state semantics and vary only
the sparse distress evaluation rule.

A structurally conservative next candidate is piecewise local quadratic
accounting with a fixed maximum block of four discrete steps:

- within each canonical event segment, split further into blocks of at most 4;
- reuse the block-start reward;
- for a 1-step block, pay only the endpoint;
- for a 2-step block, start/mid/end are the actual discrete endpoints;
- for 3- or 4-step blocks, pay fixed midpoint and endpoint rewards and use the
  unique quadratic through start/mid/end to reconstruct the remaining
  discrete endpoints;
- no adaptive tolerance or post-result subdivision.

That design keeps at most two unpaid discrete endpoints between paid rewards
and is a direct refinement of Candidate C rather than another high-order
global polynomial.

It still requires a prospectively frozen <=1e-3 decision-bias gate and a
strict <255 direct-cost gate before any omega rerun.

## Verification

Run `42392801147`:

- Python 3.11 PASS;
- Python 3.12 PASS;
- **652 I3 tests** PASS;
- **7 structural tests** PASS;
- navigation **532/532**, zero errors/warnings on Python 3.11.

No runtime, scientific or architecture promotion follows.
