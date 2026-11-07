# Stage 1 end-to-end numerical oracle: result

**Authorized for future newly frozen projection candidates.**

Classification:
`END_TO_END_HIGH_PRECISION_ORACLE_AUTHORIZED_FOR_FUTURE_CANDIDATES`.

Protocol: [STAGE1_END_TO_END_NUMERIC_ORACLE.md](../../STAGE1_END_TO_END_NUMERIC_ORACLE.md).

Software only. No World, life, Candidate E or omega rerun.

Exact checked head: `6e9f74d6aae91323399d6ce00d7008e58e4a206e`.
CI run: `42392414576`.

## Frozen gate

| Criterion | Result | Gate |
| --- | ---: | --- |
| End-to-end projection-equivalent invariant | **1.1102230246251565e-15** | <= 1e-10 |
| #1115 boundary final body | **[80, 0, 60, 90, 80]** | F=0, W=60, I=90 within 1e-10 |
| Direct bootstrap paid units | **255 / 255 / 255** | exactly 255 every case |
| Runtime projection mode added | **no** | must remain no |

All four prospective criteria pass.

## Meaning

The crucial change relative to rejected #1116 is continuity of state
representation.

The initial body and every learned transition coefficient are converted from
their **existing represented float** values with `Decimal.from_float`.
One Decimal body then flows continuously through:

1. explicit simulated plan transitions;
2. the 255-step bootstrap projection.

The body is converted to float only where existing I3 feature/distress/value
readouts require it. There is no float round-trip between plan and bootstrap.

This restores the projection-equivalent invariant to floating noise while also
recovering the exact vital boundary exposed by #1115.

## Descriptive comparisons

Historical repeated-float per-step remains extremely close in **decision
differences** to the new oracle:

- max decision bias: **3.311296478480941e-05**.

Its direct final body can nevertheless differ by 0.4 at a vital equality
boundary, as #1115 already established.

Existing event-exact remains farther from the end-to-end oracle:

- max decision bias: **0.01813728111589108**;
- max direct final-body difference: **0.4000000000000057**.

This does not invalidate Candidate C/D historically. Their gates were frozen
against the earlier truth.

The equal max prefix difference (0.0252723067) for both descriptive
comparators is not a gate. It reflects absolute value displacement under the
new continuous arithmetic; the scientific selection target remains decision
bias, while the projection-equivalent invariant guards representation
consistency.

## Authorization boundary

This result authorizes the end-to-end high-precision oracle only as laboratory
comparison truth for **projection candidates prospectively frozen after this
result**.

It does not:

- change P1.3 runtime cognition;
- add a projection mode;
- rewrite Candidate C/D;
- promote Candidate E;
- authorize an omega rerun;
- constitute an ADR-0015 architecture gate.

A future Candidate E may now be frozen against this oracle. It must still pass
the existing decision-bias target <=1e-3 and its own cost criterion before an
omega rerun is considered.

## Verification

Run `42392414576`:

- Python 3.11: PASS;
- Python 3.12: PASS;
- **647 I3 tests** PASS;
- **7 structural tests** PASS;
- navigation **532/532**, zero errors/warnings on Python 3.11.

No scientific or architecture promotion follows.
