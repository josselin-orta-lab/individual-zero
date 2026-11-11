# I3 Stage 2.1: phase-aligned action forecast and readout-model budget, software results

**Date:** 11 November 2026. **Evidence category:** source-locked software-only engineering falsifier, NOT lived or independent scientific evidence. **Decision:** technical PASS, `scientific_verdict=NOT_ISSUED`.

## Reproducible immutable source

- Baseline main prior to protocol: `97cb83b386ef73883f949d357fcbe514b4f40260`.
- [Frozen protocol](ACTION_CONDITIONAL_PHASE_AND_READOUT_BUDGET_2026-11-11.md) committed **first** at `15461ff84fb8b64619440019a9eaab4231bd898b`.
- Implementation and tests: source head `ed67a0c76d91ba2d4d80150d796210cadbd92ebc` in [PR #1296](https://github.com/josselin-orta-lab/individual-zero/pull/1296), merged as `4ac74d0aee8e6c52b5cbe74ecc424b5b0b894ad2`.
- Exact [GitHub Actions #42929649585](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42929649585): **PASS 1081/1081 full I3 tests each on Python 3.11 and 3.12**, with 7/7 engine/generation-ownership checks in both. Navigation/ownership PASS on Python 3.11; Python 3.12 navigation intentionally skipped.
- All new software fixtures execute with `World.__init__` and `run_life` guarded against invocation. **Worlds opened: 0. Scientific lives: 0.** No old study or engineering source was rerun.

## F1: outcome-phase target definition

Reference v2 `run_life` executes the following **within one tick**, in this order:

`Mind.decide` -> `World.step` (pays decision computation plus action, provides `IMMEDIATE_POST_WORLD` body) -> if living and affordable, `Mind.prepare_learning` -> `world.pay_cognition(learning.work)` -> `result["body"] = world.body` -> `Mind.learn_from_outcome(result)` updates `EffectsModel` using `POST_PAID_LEARNING` body.

Thus **PRIMARY** `POST_PAID_LEARNING` is aligned to the body-delta actually learned by native `EffectsModel`; **SECONDARY** `IMMEDIATE_POST_WORLD` is explicitly retained as an alternative target, not silently substituted. In no-learning or terminal cases the two bodies/targets coincide. Terminal both phases use original innate `-d_max`. The future is never available before forecast/action SHA freeze.

Synthetic, deliberately constructed `attendre` fixture, scalar **squared losses** (`action / global / persistence`; not out-of-sample):

| Fixed synthetic phase | Action | Global | Persistence |
| --- | ---: | ---: | ---: |
| Immediate after World step | 0 | 0.021287620563271718 | 0.012920111111111193 |
| After synthetic v2 learning debit | 0.00001571025823412813 | 0.0224599362274056 | 0.01383688359132377 |
| No affordable learning | identical to immediate | identical to immediate | identical to immediate |

The nonzero learning fee changes the energy/vigilance and hence the distress target even without any additional World tick. For the chosen constructed fixture, the earlier zero action loss is a **deliberately aligned test**, not a robust predictor or scientific improvement. Terminal fixtures preserve the full adverse `-d_max` penalty; explicit future right-censor returns null target/loss. Impossible phase transitions, tampered SHA/choice, invalid receipts, terminal learning, and post-learning changes to food/water/integrity are rejected.

The historic #1286/#1288/#1292 snapshots scored the `World.step` body before this learning phase, and must **NOT** be retroactively claimed to have measured the new primary phase. Their original observations and negative findings remain untouched.

## F2: modeled optional readout tariff, authorization before computation

Proposed category ticket for the passive already-action-chosen three-forecast readout and O(n) native memory-arity scan:

`CognitiveWork(cycles=6, simulated_steps=0, memory_items=48+n, replays=0)`, n in `[0,512]` and `n<=mind.m_max` as actually inherited.

Under unchanged v2 BodyLaws at `n=0`: modeled fee **energy 0.1296; vigilance 0.30**. Extra memory contributes `0.0002 * n` energy under existing model law; there is no extra memory-item vigilance rate. This is a **proposal for allocation categories**, not a meter of actual CPU cycles, hash bytes, memory allocations or machine joules.

The original `Mind.decide` must already have selected and paid for its action. The same first-person `CognitiveBudget` verifies actual body and `Mind.last`, actual genetic memory capacity, two remaining currencies, and the chosen motor-energy reserve. Only after `try_spend` permits the additional ticket may the external observer inspect the previously learned EffectsModel, scan the native unlabeled memory tuples, calculate passive forecasts and compute the laboratory SHA. Denials on energy/vigilance/motor reserve have **zero readout**, zero extra ticket, unchanged original allowance and unchanged Mind. A null choice stays `NO_SELECTED_ACTION`, never forced rest/wait. Forged action/capture, invalid memory arity and extra budget failures fail closed.

**Crucial distinction:** `CognitiveBudget` here only authorizes the ticket in synthetic software; `debit_cognition` only validates pure arithmetic for hypothetical synthetic receipts. No `World.step` actually debited this readout ticket in a living reference I3. The observer's SHA-256 provenance is external laboratory CPU and **not charged as a born individual's computation**. Neither the synthetic prior native EffectModel observations nor this new passive readout are proof of born-individual payment.

## Scientific interpretation and next actions

The two-phase target is now explicit and software-checked. The mechanical feasibility of a motor-reserving **model-level** allocation is demonstrated, not physical consumption, predictive efficacy, comparative utility or ecological transport. Only one constructed synthetic action history, not an independent sampled World. Even a subsequent equal-price action/global/persistence trial must account for the extra chosen-decision readout fee in both arms; else the extra cognitive payment itself changes the observed next body and confounds inference.

Keep [#1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276) open to design genuinely prospective action-conditioned proper-loss comparison with both phase labels and terminal/missing custody, and [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283) open to calibrate the full endogenous CPU/memory/lookup/readout tariff. `ACTIVE_SURFACE.json` still has `fresh_lived_worlds_allowed=false`: any real new-World test needs a separately precommitted index-scoped source/authorization, plus independent ecology. No policy, World law, innate behavior, genome or Stage 2.2 is changed. I3 remains unregistered Stage 2.1; no scientific GO.
