# Stage 2.1 replay gate: package audit and canonical status

**CANONICAL STATUS: `CORRECTED_FALSIFIER_PENDING`.**

The supplied package reports a single software execution at 08:20:33 UTC on
9 November 2026 with verdict `REPLAY_GATE_CAPACITY_SHOWN`. That execution is
preserved in [SUPPLIED_RESULTS.md](SUPPLIED_RESULTS.md), but it is **not a valid
verdict under the frozen #1212 protocol**.

## Why the supplied verdict is non-conforming

The frozen protocol defines:

`r_hat = (n_relevant + 1) / (n_decisions + 2)`.

The supplied implementation used:

`r_hat = (relevant_decisions + 1) / (audited_decisions + 2)`.

That changes the gate whenever an otherwise valid decision cannot fund its
post-decision audit. The implementation notes explicitly described the altered
denominator, so this is not a hidden numerical accident. It is a protocol
divergence.

The integrated code corrects the denominator to all scored decisions and adds
a regression test for the frozen formula. No result from the supplied
execution is promoted to the corrected implementation.

## What remains useful from the supplied run

The supplied run is still informative engineering evidence:

- R0 reported choice/score identity with P1.3 on 40 decision states;
- R1 reported forced-open replay identity;
- R2 reported discrimination between histories where learned residuals had or
  had not mattered;
- R4 reported bounded paid overhead;
- R3 passed 84/84 monotonic pairs, but vacuously because all S1 bodies replayed
  the full batch.

These observations motivate, but do not replace, the required corrected
falsifier execution.

## Next scientific action

Execute the corrected R0-R4 software falsifier **once**. No World or life is
needed and ADR-0017 remains in force. The resulting verdict is the first
canonical Stage-2.1 software verdict.

A non-capacity result moves Stage 2 to slice 2.2. There is no post-hoc rescue.
