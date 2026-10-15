# Stage 12 / issue #110 : B, contrat cognitif d'agence proximale et de responsabilité distale

**15 October 2026. Operator choice: B. This file is an implementation plan and proposed versioned contract, not a silent modification of the normative MVP v1.3.1.**

## Invariants and deliberately limited first version

B extends the existing Action Control owner, rather than adding an agent, an Oracle reader, a new memory owner or another WAL. The existing `stage12_goal_agency_judgement` is the **proximal action-agency judgement**: an inherently fallible judgement based on authorized efference and first-person sensory change, not a physical cause. A separate, versioned `stage12_outcome_responsibility_judgement` expresses what happened to the *perceived goal criterion*, and what I0 can responsibly claim about causing it.

The first version must be **conservative**: `observed_outcome` may be `improved / not_improved / unknown / unavailable` from current/prior first-person captures, whereas `subjective_responsibility` is **`unknown`** whenever the observation is available, even alongside `self` for the proximal action. This is a substantive first-person abstention, not an automatic denial of any causal effect. On UC refusal or missed observation, the judgement is `unavailable`. **No production `self` or `world` distal attribution is supported by existing evidence.** If a later sensory contract warrants a more specific judgement, it must undergo a separate science gate and policy-version change.

- **Birth only**: `dual_scope_agency=True` must require `subjective_goal_agency=True`; legacy identities do not change their journal/event schema. The new facet is subordinate to Action Control.
- **Provenance**: the twin scope uses the *same* precommitted goal, life, intent, command and first-person capture from the voluntary command. No lab truth, WorldBody causal labels, prediction compliance, observed physical effects, Oracle, Bench or unknown post-hoc source.
- **UC**: a new explicitly priced Action Control operation `goal_outcome_responsibility_assessment` is charged once for each due judgement, in addition to the existing action-agency assessment. Refusal must create `unavailable`, never a fabricated self-cause.
- **Journal**: the new precommit and assessment each have canonical references to the corresponding action-assessment and action-judgement, with their own immutable `policy_version`; original first-person journal rows remain unmodified. M-11 seals all owner state and new events in the **existing atomic generation** and cannot restore a different birth contract.
- **Attribution bias**: the legacy GA-06 pairing maps a physical outcome to the old `self/world` label; in B that label is explicitly *proximal*, not distal. Until there is a separate, independently validated dual-scope detector contract, reject `dual_scope_agency=True` together with `attribution_join=True` at birth instead of crediting misleading pairs. The 2+2/12 rule is not weakened.
- **Terminal/sleep**: no new cognition during sleeping reduced capture, UC refusal, step with no precommit or after death. No historical restore or replay of a physical command. Legacy state serialization byte-for-byte unchanged when B is disabled.

## Required tests, independent of a passing CI badge

1. One direct ingestion with inventory decrement but **no body food increase** yields proximal `self`, distal `not_improved/unknown`.
2. A **body food improvement with no action cue** yields proximal `unknown`, distal `improved/unknown`.
3. Subjectively identical spatial displacement from different physical causes never becomes a certified distal `self`; B cannot access source-hidden intervention labels.
4. UC refusal and missed step yield `unavailable`, with no false pair; duplicate refs/steps and rehashed mismatched action references fail validation.
5. The existing service's opt-out behavior remains unchanged. New charges are recorded as genuine accepted/refused `compute_charge` events under the **same owner**.
6. M-11 birth/cold recovery with B enabled must preserve pending commitment, two distinct judgements and current-step identity without creating a second owner or WAL, or restoring a mismatched legacy image.
7. Short real lives with B enabled show authorized first-person observations but do not claim GA-06 calibration or 600-step validation.
8. Full relevant regression and independent canonical-journal audits, CI 3.11/3.12, and review of normative consequences before any spec migration or Stage12 operator sign-off.

## Status gate

This design is authorized as the operator's **architectural B choice**. Its scientific sufficiency, the production merge, normative migration and operator reception remain separate gates. Stage12 **PARTIAL**, issue #110 **OPEN**. Preserve the previous A2.18–A2.27 scientific negative results; notably proximal collection does not prove distal food responsibility and even a physically truthful sensor plus cryptographic seal cannot reveal hidden causal interventions.
