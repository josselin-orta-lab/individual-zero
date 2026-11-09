# Stage 2.1 replay gate: implementation notes after package audit

Protocol: [STAGE2_REPLAY_GATE.md](../../STAGE2_REPLAY_GATE.md), frozen by #1212.
Governance: ADR-0017. This implementation remains software-only and unregistered.

The supplied development package contained a pre-execution implementation at
`0442ea9`. Audit found one material divergence from the frozen protocol:
`r_hat` was divided by audited decisions instead of all scored decisions.

The integrated implementation corrects that denominator before any canonical
software verdict is accepted:

`r_hat = (relevant_decisions + 1) / (decisions_total + 2)`.

Unaudited decisions therefore dilute the estimate exactly as #1212 requires.

Everything else follows the supplied implementation choices:

- `P13ReplayGateMind` is an opt-in P1.3 subclass, not a runtime policy.
- Modes are `gate`, `zero_perceived_cost`, and laboratory-only
  `forced_open`.
- Residual bookkeeping does not alter P1.3's chosen action.
- The audit runs after Competition/Action Control and costs one paid cycle.
- The gate pays one cycle plus two simulations of the one-step sleep plan.
- If any gate computation cannot be funded, no replay runs.
- ZERO-PERCEIVED-COST sets only perceived replay cost to zero; computation
  remains physically paid.
- Forced-open is an identity control against fixed P1.3 replay.

The supplied software run and 68/69 development pilot are preserved separately
as supplied evidence. They are not treated as a canonical execution of this
corrected implementation.
