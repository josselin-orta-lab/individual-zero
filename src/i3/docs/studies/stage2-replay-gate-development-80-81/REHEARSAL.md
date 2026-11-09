# Stage 2.1 exact transport: sealed engineering rehearsal (ADR-0017 / ADR-0019)

**Status: `PASS`. Engineering only, never evidence. ADR-0017 remains active.
No development, selection, validation or reserve World was opened.**

| Item | Value |
| --- | --- |
| Transport commit | `e23a28e` |
| Transport fingerprint | `15136d132b5244bf511a576b44619a5f44ef945d6472324bc1102ce449d967f9` |
| Plan SHA-256 | `a28606678d13bb9af18f590c328a63eb9eb82f7130c90656e4f520260d294c92` |
| Sealed manifest SHA-256 | `e359cb0556b971efc1adec7a3793a9fc70c68b5ff37f9db5b6631a61ca8a8de4` |
| Phase G | `GENERATED`, 36/36 |
| Phase R | `COMPLETE`, 36/36 |
| Invariant failures | 0 on all 10 (paid and settled cognition, horizon, declared policy, gate summary iff gate, ticket bound to World, cohort and fingerprint) |
| Mean time per step | 0.86 ms |

Machine report: [REHEARSAL.json](REHEARSAL.json). As ADR-0017 requires, it
contains structural facts only, with no reduced rows.

## What was rehearsed

The exact transport the future pilot would use:

- the frozen plan [PLAN.json](PLAN.json);
- the admission guard `lab/stage2_admission.py`;
- runtime dispatch in `runtime/life.py`, behind World-bound tickets from
  `runtime/admission.py`;
- the parameterized runner `lab/stage2_panel.py`;
- the unchanged G/R pipeline `lab/two_phase_panel.py`.

Same arms (FIXED, GATE, ZERO-PERCEIVED-COST), horizon 400, 36-life shape. Only
the declared engineering namespace differs: worlds 2/3, genomes 90011/90012,
life base 9 010 000.

## What it certifies and what it does not

It certifies one exact transport fingerprint. Any change to cognition, runtime,
pipeline, runner, guard, generators or plan yields a new fingerprint and
requires another rehearsal (ADR-0019 decision 4).

It is **not** a lift, not a scientific verdict, and not a measurement of
replay, cost or survival.

## Owner decision required (not taken here)

The scientific pilot (development 80/81) stays closed until the owner records
the ADR-0017 lift in `src/i3/docs/STATUS.md`. The guard recognizes exactly one
line made of the prefix `ADR-0017 OWNER LIFT: Stage-2.1 transport ` followed by
the transport fingerprint above. That line is deliberately **not** written
anywhere in this repository; a test checks that the status ledger does not
contain it.
