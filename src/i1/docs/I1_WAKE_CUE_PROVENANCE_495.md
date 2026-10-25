# #495: First-person waking cue, provenance boundary

Status: **design not activated**. See #490 and merged #491–#494.

## Current natural facts

- A reduced-perception Stage10 step can produce technical `stage10_reduced_capture` and `stage10_sleep_woke` receipts.
- After an alert wake (without the reflex branch), Stage10 produces a fresh `perceptual_capture` through the canonical Stage3 serializer. This *perceptual content* is first-person, but the technical wake reason, hidden mode and Stage10 control labels are not.
- A voluntary re-admission can follow that capture only through ordinary Competition and Action Control.
- Current DC-09 autobiographical allowlists accept neither the raw technical wake label nor `perceptual_capture`; `world_transition_experienced.body_before` becomes accessible only under the proven I1 same-attempt sensory concordance policy.
- Therefore **a personally available post-wake body perception is not yet an autobiographical memory of waking** and consecutive sleep commands are not one remembered sleep session.

## Invariants for any implementation

1. The same attempt must contain, in journal order, reduced capture, technical wake, full first-person waking capture, and actually sent command. All sources must have one `attempt_ref`; the waking capture must be before the command and its visible body must not be inferred from technical WorldBody state.
2. A future versioned waking-cue event must contain only fields genuinely present to the awakened individual, and only become visible through the existing DC-09 commit and paid Memory reader. An authorizing technical wake receipt must **not** itself be projected.
3. No retroactive promotion of prior histories, post-admission mutation, duplicate source ownership, additional command, gratis UC, motor privilege, or reward. M11 replay must preserve one source owner.
4. Reflex waking, reduced continuation, missing/duplicate capture, no physical command, after-admission perturbation, terminal death and cold replay all remain negative or explicitly unknown as appropriate.
5. An individual waking cue does not establish a closed, continuous subjective sleep session, its duration, or the causal learning effect on future sleep preferences.

## Distinct evidence targets

- **L1**: deterministic, negative and exact-source contract validation of the versioned projection.
- **L2**: natural birth, real sensor → DC-09 → Memory ingestion, closed-episode read and cold M11 replay with the same authentic references.
- **L3**: prospective counterfactual or paired-action observation that the remembered cue actually changes permitted deliberation and a physically admitted decision. **NOT_ESTABLISHED**.

No versioned cue is enabled by this design note; this tranche only strengthens operator-side attempt matching.
