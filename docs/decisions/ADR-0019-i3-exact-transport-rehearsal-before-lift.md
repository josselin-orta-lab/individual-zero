# ADR-0019 - I3: exact transport rehearsal before the ADR-0017 lift

## Status

**ACCEPTED BY OWNER, 9 NOVEMBER 2026.** Narrow pre-lift engineering-transport clarification only. ADR-0017 is still active; this does not lift the world-opening moratorium.

## Context

Stage 2.1 now has a canonical software verdict:
`REPLAY_GATE_CAPACITY_SHOWN`. Its frozen protocol requires a lived development
path only after ADR-0017 is lifted.

ADR-0017, however, requires **before** the lift:

1. the two-phase G/R pipeline;
2. a disjoint non-evidentiary engineering cohort;
3. a full-scale sealed rehearsal on the **exact SHA of the next intended
   transport**;
4. then an explicit owner lift in `src/i3/docs/STATUS.md`.

The Stage-2.1 frozen protocol also says:

> Runtime support for lived arms comes only after software capacity and the
> ADR-0017 lift.

Software capacity is now shown, but the remaining ordering is circular. The
exact intended transport needs the replay-gate runtime path in order to rehearse
that path. The protocol forbids that runtime support until after the lift, while
ADR-0017 forbids the lift until the exact path has been rehearsed.

This is **DRIFT DETECTED in governance composition**, not a scientific failure.

The supplied 68/69 run does not resolve the circle. It used a non-conforming
`r_hat` denominator and its asserted owner lift is not authenticated by the
repository ledger. It remains descriptive development evidence only.

## Options considered

| Option | Verdict | Reason |
| --- | --- | --- |
| Lift ADR-0017 before the exact rehearsal | Rejected | Directly violates ADR-0017 |
| Rehearse a separate engineering-only imitation of the candidate | Rejected | The rehearsal would no longer certify the exact intended transport |
| Add the runtime path only after lift, then rehearse it | Rejected | Circular and reverses ADR-0017 ordering |
| **Permit the exact transport code pre-lift, but admit only the engineering cohort** | **Accepted** | Preserves exact-path rehearsal while keeping every scientific World closed |

## Accepted decision

ADR-0017 remains active and its four lift conditions remain
unchanged. The following narrow clarification applies:

1. **Pre-lift code is not pre-lift scientific authorization.** The exact
   Stage-2.1 transport may contain the replay-gate runtime dispatch and the
   parameterized panel runner before the lift, solely so the exact code path can
   be rehearsed.
2. **Engineering-only admission before lift.** Before an owner lift, the
   transport must fail closed for development, selection, validation and reserve
   cohorts. Only the declared `engineering` cohort may pass its admission
   guard.
3. **One path, not a rehearsal clone.** Engineering rehearsal and later lived
   execution use the same runtime dispatch, same policy implementation, same G/R
   pipeline, same reducer, same arms, same horizon and same panel shape. The
   rehearsal substitutes only the declared engineering namespace for worlds,
   genomes and life seeds.
4. **Exact-SHA custody.** A rehearsal PASS certifies one exact transport source
   SHA. Any source-code change to the transport, runtime policy, G/R pipeline,
   reducer, admission guard or plan invalidates that PASS and requires another
   rehearsal.
5. **No automatic lift.** A rehearsal PASS does not lift ADR-0017. The owner
   must still explicitly record the lift in `STATUS.md`.
6. **No live workflow before lift.** No workflow or command path that opens a
   scientific cohort is executed before the owner lift. The scientific
   transport may later check out the already-rehearsed source SHA.
7. **68/69 stays closed/descriptive.** It is never reused as the prospective
   Stage-2.1 development pilot.
8. **Stage-2.1 protocol clarification.** Its sentence about runtime support is
   read as: *scientific lived-arm authorization comes only after software
   capacity and the ADR-0017 lift; exact engineering-cohort transport support
   may exist before lift solely for ADR-0017 rehearsal.*

## Why this is narrow

This proposal does not change:

- the replay-gate mechanism, R0-R4 or canonical software verdict;
- P1.3;
- any World, physics, genome, tariff or scientific arm;
- the ADR-0017 owner-lift requirement;
- the prohibition on new scientific World exposure;
- the Stage-2.1 lived criteria or controls.

It only makes ADR-0017's exact-transport rehearsal executable without creating
a second, non-identical rehearsal implementation.

## Implementation consequences

The next engineering sequence becomes:

1. replace the copied 68/69 runner with one parameterized Stage-2 panel runner;
2. freeze a **fresh** Stage-2.1 development plan on unexposed indices;
3. add replay-gate dispatch to the exact transport with a pre-lift
   engineering-only admission guard;
4. run the full-scale sealed rehearsal on the exact transport SHA;
5. record PASS/FAIL using only ADR-0017-allowed structural outputs;
6. stop for the explicit owner lift decision;
7. only after the lift may a lived development workflow open the fresh panel.

## Previously considered consequence of rejection (not selected)

Stage 2.1 remains software-capacity-only. No lived replay-gate transport can be
rehearsed and therefore ADR-0017 cannot be lifted for this slice without a
different owner-approved ordering.

## Individuals / axes concerned

I3 research execution custody only. No cognitive or behavioral rule is changed.

## Date

9 November 2026. **ACCEPTED by the owner on 9 November 2026.** No automatic lift and no scientific cohort exposure.
