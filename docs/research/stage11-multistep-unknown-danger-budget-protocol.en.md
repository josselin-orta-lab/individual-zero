# Stage 11: public multi-step corridor, unknown danger, and Planning-UC contrast

**Pre-run development protocol, 2026-10-11.** This document is registered before the new diagnostic implementation and its execution. It is **not** a held-out scientific experiment, a Stage 9 acceptance, or a Golden. The sole normative reference is `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, particularly the local Perception boundary, Action Control safety authority, P-48, DC-07, DC-11, and physical evidence accounting.

## Question and fixed public environment

Can the current Stage 11 local-frontier mechanism show a reproducible, bounded multi-step trajectory into a geometric dead end without inventing visits or an escape plan? Do two otherwise identical individuals choose the same **first action** when a dangerous site is hidden in WorldBody but entirely absent from the accessible adjacent Perception and initial canonical safety facts? Does a zero Planning-UC envelope suspend all new geographic options without reclassifying the unknown hazard as safe or unsafe?

The public fixture starts at (2,2), with needs at the existing Stage 11 neutral `START_BODY`. The only open corridor consists of (2,2), (3,2), and (4,2). Obstacles are placed at (2,1), (2,3), (1,2), (3,1), (3,3), (4,1), (4,3), and (5,2). All other resource, creature, lethal-zone, and water-source layout features are empty. Standard WorldPhysics parameters and frozen E-v1 remain unchanged except for an explicitly versioned nonlethal danger-zone damage of 5 integrity points per affected world transition. No WorldBody truth is given to Exploration, Planning, Competition, or the canonical safety source; initial safety facts are intentionally empty and identical between conditions.

Run exactly **8 consecutive real world steps** per independent copy, no scripted individual action, no target injection, no forced goal, no oracle access or operator interventions. The three versioned variants are:

1. `corridor_clear`: this physical corridor has no danger zone, normal Planning envelope.
2. `corridor_unknown_danger`: the same physical corridor, but (3,2) is a *hidden* nonlethal WorldBody danger zone, still unknown to Action Control at initialization.
3. `corridor_unknown_danger_planning_0`: same hidden hazard, but Planning has zero logical UC using the existing Stage11 strict-budget configuration. No change to action safety policy, Exploration data or physics.

All differences in truth are scoring-only Lab inputs. The canonical safety source returns `unknown` for (3,2) at initialization in **all three** conditions.

## Prespecified measurements and negative checks

- A frozen input digest (including layout, world configuration, fact-source summary and effective development configuration), source commit, condition and journal SHA-256.
- The **first world-step decision signature** (execution status, primitive and option reference). Clear and unknown-danger runs must agree *before* either could physically experience the hidden danger; a mismatch is a failed epistemic noninterference check, not a scientific finding.
- Ordered, real `perceptual_capture` positions, confirmed Exploration visit ledger and applied geographic commands. A sent command's final unobserved arrival is **not** counted as a visit.
- Whether the two-advance corridor ends with no **novel** available frontier; if the individual stays there and cannot backtrack because revisits have no P-48 novelty, record the stagnation as a **limitation**, not a success at multi-step planning.
- Danger encounters scored externally from actual observed positions, and final simulated integrity read by Lab only. Do not claim the individual *recognized* harm without a corresponding owned physical/causal evidence chain.
- Actual Planning preflight and build UC charge entries, accepted/rejected counts, budget deferrals, offered targets, and total applied geographic commands. Rejected UC are not consumed UC; budget deferral means neither safe, unsafe nor absence of novelty.
- Canonical journal verification and exact reexecution for each variant. Keep any negative outcome (including no movement, no discovery, no adaptation) instead of tuning parameters to force a positive result.

**Pass/fail contract for the diagnostic infrastructure:** every path stays within the declared passable corridor; ledger sites equal real Perception captures; the first action does not depend on undisclosed danger truth; zero Planning UC produces no geographic action, no funded preflight and no retained offered targets; all journal chains verify and same-config reexecutions agree. Any other behavior (avoidance, exposure, long-horizon escape, learning, scientific generalization) is an **observed result or open question**, not an assumed pass condition.

The Python 3.11 full suite and Goldens remain **separate and not covered by this development fixture**. Stage 11 stays IN PROGRESS; Stage 9 scientific held-out stays NO-GO.
