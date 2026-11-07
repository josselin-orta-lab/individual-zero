# Stage 1 Candidate F: common forecast-cost ceiling

Issue #1111. Baseline:
`bd60a0c32c4735d479b0f1426458afe1f7fddd52`.

**FROZEN BEFORE IMPLEMENTATION. SOFTWARE ACCOUNTING ONLY.**

## Purpose

Candidate F is now an explicit opt-in Mind simulation mode, but existing Stage-1
information kernels quote projection work as `len(model.proj_chunks)`. That is
correct for reference `chunk_end` and same-cost `trapezoid`, but it can
underquote sparse event accounting because its number of paid reward
evaluations depends on the predicted state trajectory.

This contract prevents underfunded common forecast bodies before the frozen
omega falsifier is rerun.

## Projection-work ceiling

### Reference modes

For:

- `chunk_end`;
- `trapezoid`;

the complete projection quote remains:

`len(model.proj_chunks)`.

For the current geometric horizon this is 8.

Reference receipts must remain unchanged.

### Candidate E/F local quadratic-4

For:

`event_local_quadratic4`

the complete conservative quote is:

`1 + sum(model.proj_chunks)`.

For the current 255-step horizon this is 256.

Proof:

- the initial projected reward is evaluated once;
- every later local block covers L discrete steps;
- L=1 pays 1 new reward evaluation;
- L=2 pays 2;
- L=3 pays 2;
- L=4 pays 2;
- therefore every block pays at most L new evaluations;
- the blocks partition at most `sum(proj_chunks)` projected discrete steps.

Thus actual projection reward evaluations are <=
`1 + sum(proj_chunks)` for every body/event trajectory, including event splits
and absorbing death.

This quote is a **common forecast-body ceiling**, not an actual work receipt.
Executed Candidate F cognition continues to pay exactly the sparse work it
performs.

### Rejected C/D modes

`event_quadratic` and `event_quartic` have no active Stage-1 common forecast
contract because their candidate protocols failed. A common forecast helper
must fail closed if asked to quote them rather than silently reuse
`len(proj_chunks)`.

## Active formulas to migrate

Every active I3 formula that uses `len(model.proj_chunks)` as a projection
work quote must read the shared projection ceiling instead.

This includes:

- information-value cells;
- plan/revealed-plan information;
- unknown-action trial;
- carried-food information;
- water-frontier optional trial;
- water one-future-opportunity value;
- active reference-frontier/common-ceiling laboratory helpers.

The default reference values must remain byte-for-byte numerically unchanged.

## Gate

1. reference `chunk_end` and `trapezoid` quotes remain unchanged;
2. Candidate F local-quadratic actual direct work is <= its 256 ceiling on all
   already-frozen projection cases;
3. the water-one-future-opportunity kernel used by the omega falsifier can run
   with integrated Candidate F without exceeding its common ceiling;
4. rejected Candidate C/D modes fail closed when a common forecast quote is
   requested;
5. no World/life/study allocation is opened.

A pass authorizes a separate rerun of the already-frozen omega software
falsifier with Candidate F.

It does not authorize reference adoption or an ADR-0015 architecture gate.
