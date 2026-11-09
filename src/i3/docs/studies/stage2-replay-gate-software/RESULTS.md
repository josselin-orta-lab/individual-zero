# Stage 2.1 replay gate: corrected canonical software result

**VERDICT: `REPLAY_GATE_CAPACITY_SHOWN`.**

The corrected frozen-protocol falsifier was executed exactly once on
9 November 2026 from source
`e5d10aefea16cf4a5445b40848c2fff48b903e97`, Python 3.11, GitHub Actions
run `42599443436`, job `129099996292`.

No World and no life were opened. ADR-0017 is unchanged.

Machine custody:

- full result: [`canonical-result.json.gz`](canonical-result.json.gz);
- compact summary: [`canonical-summary.json`](canonical-summary.json);
- uncompressed result SHA-256:
  `96e4ab5215e1f1eed4c5ef6d43b1d9e716c4629c4ef1dfcaecafd7642097ca61`;
- deterministic gzip SHA-256:
  `dadeb866a33469bc6acff03bba306b703d642e6237220fe30da804c022132c02`;
- workflow artifact id `13665446102`, artifact digest
  `sha256:16daf2273a9af58da324d8894a64dac0fc2afb2c0f96b3acbd4fa0e0036a10c8`.

## Frozen rules

| Rule | Canonical observation | Verdict |
| --- | --- | --- |
| R0 integrity | 0 decision mismatches, 0 unexpected extra-work rows, 0 renaming mismatches, no banned import | PASS |
| R1 identity | 0 mismatches against FIXED when forced open | PASS |
| R2 discrimination | S0: 0/16 replay batches; S1 high-E/V: 16 replays in all 4 required states | PASS |
| R3 cost sensitivity | 84/84 ordered pairs satisfy non-increase as E/V fall | PASS |
| R4 bounded metareasoning | 0 gate-overhead violations, 0 audit-overhead violations | PASS |

The frozen verdict table therefore gives
**`REPLAY_GATE_CAPACITY_SHOWN`**.

## Important boundary on R3

R3 passes **formally**, but the fixture is not discriminating about replay
cost. In S1, GATE replays the complete 16-memory batch in **all 16 tested
energy/vigilance bodies**, exactly as ZERO-PERCEIVED-COST and FIXED do.
Therefore the 84/84 monotonic result is true because the replay count is flat,
not because the software fixture demonstrates graded cost sensitivity.

This limitation was already visible in the supplied non-conforming run and is
not a reason to alter R3, S1, the cost formula or the frozen verdict after the
canonical execution. Doing so would be post-hoc tuning.

What the software result establishes is narrower:

- the corrected gate can remain fully shut when learned residuals have never
  mattered (S0);
- it can open when residuals have mattered (S1);
- the audit and gate are paid, bounded and decision-preserving;
- forced-open identity with P1.3 replay holds.

It does **not** establish that the gate will reduce replay in lived experience,
that cost-awareness is behaviorally active, or that survival is non-inferior.

## Relation to the supplied package

The earlier uploaded package reported the same nominal software verdict, but
used `audited_decisions` instead of the frozen all-decisions denominator in
`r_hat`. That supplied result remains preserved in
[SUPPLIED_RESULTS.md](SUPPLIED_RESULTS.md) and is not the authority for this
verdict.

Likewise, supplied DEVELOPMENT 68/69 remains descriptive evidence only. It used
the non-conforming implementation and does not become prospective Stage-2.1
evidence retroactively because the corrected software gate now passes.

## Consequence

Stage 2.1 remains the active scientific slice. Under its frozen protocol,
software capacity leads to the **lived path only after a valid ADR-0017 lift**.

Therefore:

- do not move to Stage 2.2 merely because the software gate passed;
- do not open a fresh World while ADR-0017 remains active;
- do not reuse 68/69 as the prospective development pilot;
- do not modify the frozen replay-gate mechanism from this result.

The next work is engineering/governance: prepare a fresh, source-locked Stage
2.1 development transport, pass the required full-scale sealed rehearsal on its
exact SHA using the non-evidentiary engineering cohort, and satisfy the
remaining ADR-0017 lift conditions before any lived execution.
