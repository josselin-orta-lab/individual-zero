# MVP v1.3.2 — GA-SPATIAL-01, normative amendment candidate

**Operator direction:** Option A, 14 October 2026. **Status:** proposed normative amendment for protected review, **NOT** merged or demonstrated in the runtime.

This is an explicit additive contract to the GA-01 to GA-07 target in `docs/architecture/reference/en/mvp-specification-v1.3.2.md` (PR #148). The authoritative historical v1.3.1 text and the separate DC-05 food-safety proposal remain unchanged.

## GA-SPATIAL-01: two independent sources

Metacognition's **existing** `Stage12GoalProgressLedger` may additionally commit `spatial_progress_v1` for an admitted, goal-motivated movement. Record life identity, intent and action refs, selected movement direction, observed start coordinate, *perceptually identified* resource target coordinate/reference, initial Manhattan distance, strict criterion `distance_after < distance_before`, deadline `t+1`, and version **before execution**. Spatial `failure` means this local progress criterion was not met; it neither establishes overall goal failure nor the reason for an obstruction. No retroactive intent or forced move. An unavailable or delayed lived capture produces `unknown`.

Action Control's **existing** `GoalAgencyService` may independently commit `spatial_mechanism_v1` with the *same* intention and physical action, but its own perceptual cue references and decision rule. It MUST NOT read `goal_criterion_outcome`, the calculated distance comparator, a P-47 label, hidden WorldBody causes, Oracle or Bench. It may access prior efference, the perceived pre-action adjacent cell in the precise commanded direction, and the new genuine perception after the transition.

- `self`: admitted/executed directional movement and witnessed displacement matching the efference, relevant to the preidentified goal-related target. Actual contribution is only I0's subjective judgement.
- `world`: admitted/executed command toward a legitimately preidentified goal-related target; **exactly the commanded adjacent cell** was directly perceived as nonpassable at action commitment; the later authorized perception confirms no movement. I0 *subjectively* credits that perceptible local external constraint. No other direction, unknown passability, unrelated target, or mere failure is admissible. The producer must be independently auditable from the original recorded pre/post perceptual cues, including cell identity.
- `unknown`: every incompatible/uncertain case, including missing or contradictory cue, hidden obstruction, misaligned target, unavailable capture, unadmitted command, and inaccessible goal target.
- `unavailable`: cognitive work refused or no authorized next-step perception; distinct from a computed `unknown`.

This contract does **not** relax Action Control or safety admission. If known blocked movement is never admissible, genuine `world` may be structurally unobservable. The operator must receive that negative finding rather than an artificial episode.

## Versioning, custody and charges

Use the existing Action Control and Metacognition owner snapshots, no duplicate mutable ledger. Declare positive deterministic UC at birth for any extra perceptual classification and pair jointure; reject absent debits. Keep one pair per genuinely experienced physical step and current-generation atomic M-11 recovery. Strict mortality, sleep, journal and Phase 1 publication apply unchanged. No retroactive diagnostic.

## Independent evidence and acceptance

The external auditor must reconstruct pre-action target visibility, goal/action binding, command admission and transition, exact pre/post adjacent cell evidence, strictly later result, producer judgement, charges, unique life and references, and diagnosis consumed in its permitted subsequent step. Technical hash validity alone never proves semantics or physical causation.

Refuse tampered-and-rehashed obstacle, target, direction, command, cue, identity, timing and UC receipts. Pre-register physically contrasted worlds and trials **before** collecting new evidence. Do not reduce `bias_min_outcomes_each=2`, `window=12` or `attribution_bias_threshold=0.75`. Positive software fixtures alone do not meet scientific reception. The issue stays open and Stage 12 unaccepted until genuine independent results and operator validation.
