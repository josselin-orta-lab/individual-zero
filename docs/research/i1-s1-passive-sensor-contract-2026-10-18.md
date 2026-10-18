# I1 S1 passive scientific sensor contract (2026-10-18)

**Engine under observation:** I1 (active), after fix #283 at `9256ba74458f382d72379af4844d3a1ee62d5a5b`. This instrumentation changes **only the external preset-world operator report**. It does not modify I1 cognition, decision costs, environment, physics, owner publication, M11 or the permanent first-person journal.

## Operator-only fields
On WAL runs, the existing `Stage4StepResult` already contains `command_primitive`, `source`, `reflex_triggered`, `fallback_used` and `cycles_used`. The preset-world report now records them beside each actual step's execution outcome and world/body snapshot as `action_primitive`, `action_source`, `reflex_triggered`, `fallback_used`, `cycles_used`. The data are only read **after** I1 computes its choice and carries out the step; nothing is injected back.

The report distinguishes `applied`, `dead` and `safety_block`. A primitive appearing on a rejected or blocked execution is **not** an applied physical action. Count `applied` and `dead` physical commands in the applied numerator, but retain separate refusal and no-applied-command denominators. Independently check each non-dead physical transition in the authenticated WAL before treating a run as valid.

The observer must never interpret a sensor value alone as a proof of a changed cognitive representation or learning. A Stage10 technical receipt requires separately documented published-owner before/after states to support a semantic consolidation claim.

## Planned metrics
Per individual and preset, publish action count/closed world steps, proportions of primitives among applied actions, percentage of lived steps containing each primitive, means by age-bin and the percentage of steps with no applied command. Use observed-life steps rather than requested maximum steps. Preserve terminal steps, and mark administrative censoring separately from natural death. Body snapshots provide post-step energy, hydration, hunger and integrity **only to the extent exposed by the current telemetry schema**. No operator world truth is supplied to the individual.

This is an instrumentation amendment, not a rewrite of the frozen S1 failure cohort; that prior pilot remains TECHNICAL_FAILURE. A new SHA and prospective births are required for future trials. No scientific GO is inferred from sensor availability.
