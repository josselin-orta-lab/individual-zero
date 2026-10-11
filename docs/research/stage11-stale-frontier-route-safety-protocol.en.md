# Stage 11: previously observed route invalidated by external world change

**Prospective public development protocol, 11 October 2026.** Registration precedes the source changes and new executions below. **Not scientific held-out / Golden / Stage 9 evidence.** Normative source is `docs/architecture/reference/en/mvp-specification-v1.2.1.md`. The current [routed junction and UC results](stage11-observed-route-uc-results-2026-10-11.fr.md) are a historical control and must not be edited retroactively. No change to default-off route policy, physics, normative constraints, SafetyProtocol or cognitive thresholds.

## Question

If the individual already physically saw and traversed the corridor (2,2) → (3,2) → (4,2), can a later *external, journaled world input* block an otherwise valid observed return path? Does the individual re-check the next physical neighbor rather than relying on an old stored passability survey or the Lab's hidden state? If the obstruction disappears, what actual trajectory is then observed? A hidden danger at the same former return site must remain unknown until physically justified; we must not award it to the canonical safety source as advance knowledge.

## Prespecified variants

All variants start from the **same public 10-step open-junction layout**, initial state, Stage11 opt-in routing config and Planning envelope in `lab.stage11_routed_junction_probe`. No operator command scheduling and no goal injection. Use **InjectedScenario** only (owned by Stage2), which writes `external_input_received` and `external_input_applied` to the hash-chained journal before each world step. The user-visible local capture is the only source of adjacency passability or creature occupancy consumed by cognition.

1. `unchanged_control`: no scenario change; existing ten-step route back to the fork is the matched software baseline.
2. `creature_blocks_return`: at world step **3** place a creature at **(3,2)**, the immediate next return hop previously seen as clear. It remains present for the remaining steps.
3. `creature_removed`: same placement at step **3**, then removal at world step **5**; do not assume the agent returns or learns to wait.
4. `unknown_danger`: at step **3** activate a nonlethal danger zone at **(3,2)**, with no change to local Perception passability and no canonical safety promotion. Score any body damage *after* physical transitions. This is not a guarantee that the individual should predict the hazard.

All world changes are external and journaled. For any scenario with an occupied immediate hop, check that **no applied route-command** attempts to enter the visibly occupied neighbor; count reflex and ordinary commands separately. The ordinary Action Control final veto remains active. If observed behavior violates that property, retain the failure and inspect the safety path rather than changing a test condition.

## Additional isolated canonical safety contract, synthetic only

Independently from the physically instantiated scenario variants, at the end of two *actually executed* steps inject **two explicitly synthetic, test-only DC-05 safety records** into the **canonical CausalModel**, promoting (3,2) to `known_lethal`; do **not** claim these records are lived observations. Test that charged Phase-1 Action Control `verifier_admissibilite` rejects a routed return to (3,2), no route option is offered/executed, and journal output remains verifiable. Do not modify Action Control, duplicate a safety cache, create a hidden-world oracle, or misclassify the synthetic evidence as scientific. Use the existing Stage11 synthetic snapshot precedent.

## Fixed measures and outcomes

- World-step positions captured through actual `perceptual_capture` events, observed visits, commands applied (ordinary vs route vs reflex), journaled external scenario events, and every physical damage transition.
- Planning UC accepted and refused for `geographic_route_search`, `geographic_admissibility_preflight`, `planning_build`; raw found routes versus surviving proposals and final executed transits.
- If creature blocks return, preserve *non-success* (including persistent waiting). If removal occurs, record whether and when the individual returns, not a forced success.
- Initial WorldBody/Perception equivalence and identical pre-intervention actions at steps 1–2; no early leak of the future scenario.
- Independent exact reexecution of each registered variant, journal verification, SHA-256 hashes of input configuration, output and canonical journal; no invented visit of the last, unobserved command.
- Tests may assert custody, safety gating, deterministic replay and absence of world-oracle access. Long-horizon competence and hazard learning must be recorded as measured outcomes, not presumed.

Run only targeted Python 3.12/unit CI during implementation. Python 3.11 complete run and Goldens remain distinct. Stage 11 **IN PROGRESS**; Stage 9 **scientifically NO-GO**; PR remains draft, repo private.
