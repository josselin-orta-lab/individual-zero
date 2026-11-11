# I3 Stage 2 cross-slice software preflight: fixed Competition evidence versus additional horizon

**Freeze before executable implementation, 11 November 2026.** Baseline main f72127f7b365c20a177f1291a9ae9d71809b18f7. **Status:** software-only mechanistic audit, not a new scientific stage GO, no World, no lived individual, no new native behavior.

**Why now:** [E0/E1 source gate](STAGE2_E0_E1_CAMPAIGN_LAUNCH_2026-11-11.md) ruled out interpreting the existing action-agnostic TD replay head or unchanged native EffectsModel one-step forecasts as new action-conditional information. Do not add another replay predictor. The cheapest alternative is to characterize computations **already inside P1.3**, not import Stage-3 cognition. Scientific Stage 2.1 remains NOT_ISSUED and P1.3 funded-v2 remains the reference.

## Fixed mechanistic questions and falsifiers

- **CYCLE hypothesis:** With a fixed scored-option vector, successive native Competition cycles repeat the same normalized evidence, not a new forecast or sensory datum. Extra cycles can change accumulation/intentional persistence, but cannot exceed the raw best score of the unchanged alternatives on that static vector. If an implementation secretly updates scores during the inner loop, or spends an unreported cycle, fail the preflight.
- **HORIZON hypothesis:** Repeated native Mind.simulate calls on the **same** frozen internal-effects model, body and candidate plan, with horizons 1, 4 and 8, can produce distinguishable predicted cumulative intrinsic returns because more plan steps are modeled. Actual simulated steps and all self-projection work must be prepaid by CognitiveBudget. If horizons yield no changed predicted returns in the fixed grid, report a negative local capacity result and do not choose different fixtures after exposure.
- **Limits:** Different forecasts or ranks in synthetic source cases are **not** an observed decision under World, and do not identify a positive net value of computation or survival benefit. Cycle effects on intention may have delayed, unrepresented bodily consequences; do not call them useless from a static-score bound alone.

## Frozen finite grid, no World

- Genome: reference i3-genome-v4 midpoint; life seed 211; no inherited information, unchanged P1.3 Mind, BodyLaws v2.
- Three synthetic first-person-consistent bodies (E,F,W,I,V): (80,60,60,80,80), (45,40,40,75,70), (30,25,25,70,50). These are invented software starting states, **not born or source-authenticated outcomes**.
- Fixed synthetic action-effect observations, unpaid fixture construction only: wait (-0.35,-0.2,-0.4,+0.2,0), sleep (+3,-0.35,-0.4,0,+4). The source is labelled SYNTHETIC_UNPAID_FIXTURE. No hidden ecology or World mutation is consulted.
- Two non-motor-executed model plans, each exactly eight same-action steps: 8 waits or 8 sleeps. They are generic demonstration plans, not claims of a current real action candidate set. Evaluate each under explicit maximum simulated horizons 1, 4, 8 on a **fresh native CognitiveBudget from the same body**. Report scores, actual simulated steps, work categories, model energy and vigilance paid, and whether the between-plan rank changes with horizon. These are not source-realized expenses.
- For the Competition check, use the frozen two-option score vector returned at horizon 8 and the identical body. Repeat raw native _compete separately from identical fresh Mind states for ceiling cycles 0, 1, 4. Report the chosen option, actual paid cycles and its score relative to raw maximum. No motor command is executed and no decision policy is integrated.
- No adaptation to output, selective seed search, actual exposure, external memory, new reward, artificial action preference, or fitted parameter. One frozen fixture grid, negative and null results published.

## Software assertions and exact scientific status

1. **Source isolation:** refuse World instantiation; the helper uses only existing I3 native Mind, BodyLaws, CognitiveBudget and the declared synthetic fixtures. No run_life, no birth.
2. **Native funding:** every executed simulation/Competition work count is an actual successful CognitiveBudget purchase in both model currencies; 0 <= actual modeled-plan steps <= horizon; total prepaid simulated-work units are **at least** plan steps and also include the native self-projection blocks. No fake negative/unpaid units or motor after-cost assumption.
3. **Determinism:** identical seed/body/plan/horizon produces identical work and forecast; no World name, future information or external target. Extra cycles never alter the frozen scored vector; selected winner must be one of its original alternatives and its score cannot exceed maximum.
4. **Primary descriptive mechanism result:** counts of bodies where one or both plan forecasts change from depth 1 to 8; counts of bodies with cross-plan raw-rank differences; complete cycle no-information result and cost table. Do not require a favorable option ranking; zero is a result.
5. **Primary scientific result:** always NOT_ISSUED. No inference on independent organisms, calibration of CPU energy, action utility, survival non-inferiority, or Stage 2.2/2.3 promotion.

**Execution admission:** software helper and tests only, under I3 lab/tests paths; no physics, genome, existing Mind/Competition, runtime, active surface or registered engine modification. Tests are to be executed on the exact source SHA under I3 Python 3.11 and Python 3.12. Software PASS is not World authorization. Results should be consigned with exact SHA and no new-born count.
