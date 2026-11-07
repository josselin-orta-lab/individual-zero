# Stage 1 projection death-boundary arithmetic: result

**Classification: `FLOAT_ACCUMULATION_DELAYS_REFERENCE_DEATH_BOUNDARY`.**

Protocol: [STAGE1_PROJECTION_DEATH_BOUNDARY_AUDIT.md](../../STAGE1_PROJECTION_DEATH_BOUNDARY_AUDIT.md).

This is a post-hoc audit of the single already-exposed worst case from #1114.
No new grid, World, life or study index was opened.

Exact checked head: `ef382f75a4e42c6d59255eb13f0f36e4c791bff5`.
CI run: `42390015096`.

## Result

The learned direct projection drift in the exposed midpoint/sleep-learned case is:

```text
food      -0.2 / step
water     -0.4 / step
integrity +0.2 / step
```

Sleep restoration is present in memory but inactive at the initial
`energy=80, vigilance=80` state because both channels already exceed the
midpoint distress threshold.

At the critical food boundary:

| Step | repeated-unit food | algebraic food | Decimal food | repeated dead | algebraic dead |
| --- | ---: | ---: | ---: | --- | --- |
| 49 | 0.20000000000000207 | 0.1999999999999993 | 0.2 | no | no |
| 50 | **2.0539125955565396e-15** | **0.0** | **0.0** | **no** | **yes** |
| 51 | 0.0 | 0.0 after clamp | -0.2 before clamp | yes | already dead |

Thus the repeated IEEE-754 recurrence crosses the exact mathematical death
boundary one discrete step late.

Terminal bodies:

- algebraic death at step 50: `[80,0,60,90,80]`;
- repeated-unit death at step 51:
  `[80,0,59.599999999999795,90.20000000000014,80]`.

The extra step changes water by approximately `-0.4` and integrity by
approximately `+0.2`, exactly matching the #1114 final-body discrepancy.

The event-exact diagnostic terminates at the algebraic boundary to floating
noise (`water=59.99999999999999`), while the existing repeated-unit per-step
truth follows the delayed step-51 boundary.

## Scientific consequence

The 255-unit per-step diagnostic is therefore **path-dependent at an equality
boundary**. It remains the historical truth used by the frozen C/D protocols,
so their negative results are not rewritten.

However, it should no longer be treated as a numerically neutral oracle for a
future Candidate E until canonical discrete death-boundary semantics are frozen
prospectively.

This does not prove that algebraic/event semantics should replace repeated
recurrence. It proves only that the two differ for representational, not
biological, reasons in this exposed case.

## Decision

- historical Candidate C/D gates unchanged;
- no candidate promoted;
- no omega rerun;
- default remains `chunk_end`;
- next protocol must define canonical numerical semantics for exact threshold,
  clamp and death boundaries before any Candidate E characterization.

## Verification

Run `42390015096`:

- Python 3.11: PASS;
- Python 3.12: PASS;
- **637 I3 tests** PASS;
- **7 structural tests** PASS;
- navigation **532/532**, zero errors/warnings on Python 3.11.

No scientific or architecture promotion follows.
