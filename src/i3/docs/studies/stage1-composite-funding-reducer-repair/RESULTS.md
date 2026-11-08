# Composite decision-funding reducer repair: software PASS

Protocol:
[STAGE1_COMPOSITE_FUNDING_REDUCER_REPAIR.md](../../STAGE1_COMPOSITE_FUNDING_REDUCER_REPAIR.md).

**SYNTHETIC SOFTWARE/ENGINEERING ONLY. NO 58/59 REPLAY.**

Frozen verdict:

`COMPOSITE_FUNDING_REDUCER_REPAIR_PASS`

Confirmed by GitHub Actions run `42491280991` under Python 3.11 and 3.12.
The Python 3.11 job ran 895 I3 tests plus navigation checks successfully.

## What failed in 58/59

The historical revision reducer recognized only the four P1.3 public funding
statuses. Candidate-H can emit:

`NO_FUNDED_RELEVANCE_PROBE`

when its detached relevance probe cannot complete.

That public status is intentionally composite. The same decision receipt carries
the underlying `candidate_h_probe_funding`, which is either:

- `NO_PROCESSING_BUDGET`; or
- `NO_FUNDED_SCORE`.

The resource observer already records the decision outcome corresponding to
that underlying processing class. The old reducer instead rejected the public
composite string before it could interpret the nested receipt.

## Repair

The reducer now normalizes funding in one fail-closed helper.

Historical statuses normalize to themselves.

The only added public composite status is
`NO_FUNDED_RELEVANCE_PROBE`, and it is accepted only when the trace carries
one of the two declared incomplete Stage-A funding classes above.

The public sidecar and trace funding strings must still be byte-identical.
Both observer outcomes must still match the normalized historical processing
class.

No other composite string is accepted.

## Frozen rules

| Rule | Result |
| --- | --- |
| R0 historical behavior unchanged | PASS |
| R1 exact synthetic legacy reproduction | PASS |
| R2 narrow composite normalization | PASS |
| R3 processing-paid semantics | PASS |
| R4 fail closed on invalid composite receipts | PASS |
| R5 custody joins unchanged | PASS |
| R6 no World/life/evidence authority | PASS |

The synthetic gate proves that the legacy predicate rejects both declared
Candidate-H composite fixtures before normalization.

After repair:

- nested `NO_PROCESSING_BUDGET` is unprocessed and requires zero decision
  work;
- nested `NO_FUNDED_SCORE` counts as paid processing and must satisfy the
  existing paid base-block work check;
- neither composite probe failure may admit a motor action.

The gate rejects missing/illegal nested funding, unknown public status,
observer-outcome disagreement, sidecar/trace status disagreement, paid/unpaid
work contradictions, composite motor admission and ordinary custody
disagreement.

## Interpretation

This repairs the **generic reducer**, not Candidate-H cognition.

It does not:

- alter the archived Candidate-H life;
- make the partial 58/59 panel complete;
- authorize a retry;
- construct an H1-H6 verdict from the archived original;
- weaken action/body/work/uptake joins.

58/59 remain exposed and closed.

The independent Candidate-I integration gate still has to pass before a fresh
DEVELOPMENT protocol may be proposed.
