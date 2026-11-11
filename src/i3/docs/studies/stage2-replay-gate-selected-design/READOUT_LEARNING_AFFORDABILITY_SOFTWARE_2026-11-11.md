# I3 Stage 2.1: self-computation can consume the reserve for subsequent learning

**Frozen engineering-only protocol, 11 November 2026, before code/tests or any
fixture result.** Exact `main` baseline
`a6abe6475d393a71b620efc8ece458ac4fac690c`, after closed
[#1296](https://github.com/josselin-orta-lab/individual-zero/pull/1296)
and documentation #1297. Related hypotheses [#1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276)
and cognitive-cost [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283).

The canonical `src/i3/ACTIVE_SURFACE.json` currently declares
`fresh_lived_worlds_allowed=false`,
`all_new_worlds_currently_authorized=false`. **Run no World, run_life,
engineering/DEVELOPMENT cohort, scientific original, generator or selected
population.** This protocol only probes *pure* existing
`BodyLaws`, `CognitiveBudget`, `transition` and the reference
`Mind.prepare_learning` advance-allocation method on clearly
constructed software fixtures. No prior evidence may be rescored.

## Falsifiable question and distinction

The preceding #1296 pass only established that after the original
already-chosen and prepaid action, a proposed passive action/global/persistence
readout can reserve its **own** `CognitiveWork(cycles=6,memory_items=48+n)`
without stealing the motor command's energy. The next native phase is
`Mind.prepare_learning` on the body returned by that action, and it
**requires another advance two-currency payment**. Motor-preserving
authorization does **not** reserve or guarantee the *future outcome
learning* block. It must not be silently presented as energetically
neutral cognition or a value-of-computation improvement.

**Primary technical falsifier:** with the same frozen valid before-body,
same chosen original action, original decision work, unchanged genome, laws
and memory/effects state, run two *pure* native transitions:
(A) without optional passive-readout work and (B) with the **additional
native budget-authorized** proposed readout work, both paying original
decision work and executing exactly the same commanded action.
Without opening a World, use the actual reference `Mind.prepare_learning`
to assess whether the next **base** learning block can be authorized
on each post-transition body. Predeclare at least one energy-limited
and one vigilance-limited (A affordable, B not affordable) fixture,
plus funded-both and rejected optional-readout controls. If the
reference learning's funding state never differs in the declared
near-boundary cells, report a negative technical result; do not retune
the cells after exposure.

## Frozen software fixtures and physiology

Use only `midpoint()` native genome,
unchanged v2 `BodyLaws()`, action `attendre`,
`Mind.last=(before_body,('attendre',),'attendre',None)`,
empty `Mind.buffer` and `EffectsModel`, no hidden World.
The prior original decision is a deliberately **synthetic**
`CognitiveWork(cycles=3,memory_items=12)` allocation on a
`CognitiveBudget(before_body,BodyLaws())`. The proposed optional
readout is the frozen `proposed_readout_work(n=0)` already declared
in #1296, with `cycles=6,memory_items=48`.
The unmodified `transition` performs the same passive food/water
decay and native chosen wait motor in both branches. No invented
food/health/water gain is provided; the only branch intervention is
the native modeled readout energy/vigilance cost. Match actual
motor-command admissibility and charge both currencies. Then run
`Mind.prepare_learning` with a new actual-body-derived
`CognitiveBudget` on the resulting nonterminal body and original
`Mind.last`, retaining the base-update allocation and its actual
`CognitiveWork`. Do **not** execute `Mind.learn`, TD updates,
or `World.pay_cognition`; this is a pure-model affordability
check, **not a paid lived outcome**, biological survival or
first-person forecast calibration.

Fixed before-bodies (energy, food, water, integrity, vigilance),
explicitly including an energy-limited and vigilance-limited learning
window, a fully funded comparison and an optional-readout rejection
window:

- `energy_boundary=(0.56, 60, 60, 90, 80)`
- `vigilance_boundary=(5, 60, 60, 90, 0.55)`
- `both_funded=(5, 60, 60, 90, 5)`
- `optional_denied=(0.49, 60, 60, 90, 80)`

For `optional_denied`, the zero-extra-work branch remains a valid
reference but the extra optional ticket is rejected by the
motor-energy reserve. Mark B as `NO_FUNDED_READOUT`, *not* a
counterfactual World transition or an imputed success. For each
authorized A/B fixture, report original decision work, requested
optional work, exact native decision energy and vigilance debit,
post-action body, whether the native base learning could be allocated,
base learning work, and residual energy/vigilance (if funded).
Learning isn't an all-or-nothing replay promise; the reference
`prepare_learning` may pay base work and conditionally reserve a
positive number of sleep replays on another selected action. Here
`attendre` has zero sleep replays. Keep post-outcome terminal
status explicit, not a fitness score.

## Hard invariants and controls

- No optional `passive_readouts`, observer hashing, future prediction
  or data scan before its `CognitiveBudget.try_spend` authorization.
  To prevent conflating this pure affordability probe with a forecast
  experiment, no passive readout needs executing at all.
- Both A and admitted B share exactly the original chosen physical
  action, parameter and same original decision work. The only
  different physical work is B's known optional ticket; no modifying
  `Mind.decide`, body laws, genetics, native action selection, reward,
  resource stock, or motor-command fallback.
- `Mind.prepare_learning` is called on independent new, genuine
  `CognitiveBudget` objects with the respective produced body.
  Verify source Mind learned state, RNG, effects and memories unchanged
  before and after the probes.
- All charged decision and optional units must satisfy original native
  `CognitiveBudget` and `transition` algebra, with no unpaid/
  clipped deficit or borrowed sleep. An energy/vigilance-low negative
  control must be rejected without budget mutation, phantom work
  or accidental free cognition.
- Recheck the *same* exact source and fixtures on Python 3.11 and
  3.12, plus full I3 regression suites/ownership/navigation.
  Do not interpret deterministic synthetic fixture rows as
  independent biological observations or a statistical effect.

## Scientific and development decision

If the full invariant and branch divergence gate pass, **technical
model only**: optional already-chosen readout work can consume current
reserves otherwise available for the individual's own immediate
outcome learning, even when the original chosen motor remains
admissible. This identifies an operational cost/phase interaction
that future value-of-computation studies must price. It does not
show the individual *should* decline to think, nor justify
hard-coded survival/learning rules or a forced motor change.
A valid real-world predictive-utility experiment still requires a
new prospective source/owner authorization, phase-aligned future
body target, calibrated operation costs, independent ecological
sampling and proper no-learning/action-blind controls.

`worlds_opened=0`; `scientific_lives=0`;
`scientific_verdict=NOT_ISSUED`; no fresh World,
no selection/validation/reserve, no Stage 2.2 GO or I3 activation.
