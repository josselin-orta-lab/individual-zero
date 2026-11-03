# ADR-0010: Stable-world prior and evidence-based associative memory for low-abstraction I2

**Status: ACCEPTED as a scientific/architectural principle by the project owner,
3 November 2026.** Applies to future I2 development and interpretation,
not retrospective rewriting or automatic living-engine activation.
Complements [ADR-0006](ADR-0006-evidence-grounded-aversion-reappraisal.md)
and [ADR-0009](ADR-0009-i2-physiology-temperament-parity.md).
Research tracker: [#906](https://github.com/josselin-orta-lab/individual-zero/issues/906).

## Context and verified motivation

The owner's observation is fundamental: a low-abstraction individual cannot
infer an **invisible reversal** in a resource's effects by the mere passage
of time. Typical physical resource properties are comparatively persistent;
they can also change, sometimes abruptly, but this must not be assumed
without new evidence. This is a **modeling prior** for the target ecology,
not an assertion that nature never changes unpredictably.

Frozen native #912 offered concrete evidence: after hidden degradation,
both learning-on and innate-only individuals drank the now-useless water
42 times in 96 ticks, and neither returned to critical thirst after the
first restoration. This is not evidence of failure to *anticipate* the
unobservable reversal; it exposes a mismatch between the intended need
and the old global-relief +5 valuation. The initial draft #914 then
proposed instant clearing of all accumulated failures on one success,
which would create excessive volatility in the association.

ADR-0006 had already found that a fixed stale-option +9 reward worsened
survival under persistent adversity and was not endogenous curiosity.
Do not repeat that mistake under a new implementation name.

## Decision

1. **Local stability by default.** Never add score merely because a choice
   has been untried for N ticks; elapsed time alone is not evidence that a
   previously harmful source improved. Do not identify hidden reversals
   that are observationally indistinguishable.
2. **Need-specific personal learning.** The efficacy of an actual resource
   is evaluated against the *need it was selected to satisfy*, not a
   rounded sum of unrelated physiological signals. Only committed,
   first-person before/after evidence enters the association.
3. **Cumulative and fallible associations.** Each confirming or
   contradicting *real* exposure updates evidence gradually. One
   unexpected success must not erase dozens of failures, nor should one
   failure erase a strongly repeated pattern of success. Inactivity
   without new exposure does not rewrite that history.
4. **Different motives are not an oracle.** New sensory/context evidence
   may justify considering a hypothesis. A strong present physiological
   need or innate survival reflex may justify a known risk. Neither
   implies a prediction that the external world's hidden quality
   changed. A new chosen action, if admitted, can subsequently reveal
   a changed effect.
5. **Competition remains the decision-maker.** Evidence updates
   preferences; they do not force, forbid, revive, or silently execute an
   action. Current body pressure, innate mechanisms, resource availability,
   paid UC and fresh Action Control retain their independent roles.
6. **Ecologically relevant falsifiers first.** Prioritize matched long
   lives in stable resource regimes, noise/isolated anomalous outcomes,
   physical exhaustion and recurrent needs. Test gradual externally
   observable changes separately. Sudden uncued regime switches are
   robustness tests and cannot demand foreknowledge.

## Implementation and non-claims

The scoped native experimental implementation in [PR #914](https://github.com/josselin-orta-lab/individual-zero/pull/914)
uses a simple cumulative, **researcher-declared** signed unit evidence
(`+1` after a real target-need restoration, `-1` after a real
nonrestoration), reconstructed from the one born owner's journal
(maximum 128 physical ticks). This is neither a fitted biological
plasticity model nor proof of natural learning. The G2 generic chosen
memory remains separately bounded (64); no new owner or M11 certificate.

Any positive finding must survive controls for innate drives, action
availability, prior personal trajectories, UC and simple noisy-outcome
counterexamples. A decrease in paid score alone does not demonstrate
a changed action, a safety improvement or survival advantage.
Frozen #912 reports and prior ADRs are preserved as historical
source-pinned evidence. Sleep/dream recombination remains deferred
in #902; engine registration and independent M11 remain forbidden.

## Rejected alternatives and future review

- Periodic automatic resource retry or a time-based freshness bonus:
  **rejected**, because it fabricates suspicion of a hidden change.
- Immediate wiping of long adverse history upon a single positive event:
  **rejected**, because it overreacts to noise.
- Permanently banning a resource after one negative sample:
  **rejected**, because the action may remain physically viable and
  competing needs can justify risk.
- Assuming a clock-stable world is an absolute law: **rejected**.
  Genuine cues, sustained contradictory evidence and urgent needs
  can rationally change behavior without predicting invisible events.

The count-based score may need replacement if ecological longevity,
noise or scale falsifiers fail. Any such replacement requires its own
source-locked test; do not retune the historical experiments to pass.
