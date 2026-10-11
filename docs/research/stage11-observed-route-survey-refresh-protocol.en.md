# Stage 11: opt-in refresh of physically observed geographic adjacency

**Prospectively registered 11 October 2026, before the new mechanism or tests.** Public software-development-only investigation; neither scientific validation nor a held-out/Golden campaign. Normative source: `docs/architecture/reference/en/mvp-specification-v1.2.1.md` (§14, DC-07, DC-11, INV-08, physical observation ownership, snapshot integrity). Stage 9 scientific NO-GO remains intact.

## Fixed negative baseline

[Prior predeclared physical safety experiment](stage11-stale-frontier-route-safety-protocol.en.md) and [separate normative reflex repair](stage11-creature-reflex-normative-remediation-protocol.en.md) produced [826 passing Python 3.12 tests](stage11-creature-reflex-remediation-results-2026-10-11.fr.md) on commit `8210af69`. With the reflex corrected, the open fork is recovered in the unchanged control. With a visible creature placed at (3,2) on world step 3, the individual never takes an applied geographic transit into it. **When this creature is removed at world step 5, the individual still does not return during ten steps.** The physical path reopened, but an Exploration-owned local topology survey captured while the creature occupied the edge is not revised by a later paid physical capture. Do not erase this negative control.

## Isolated, versioned hypothesis

An **opt-in** owner-level `refresh_surveys` flag permits an ordinary newly captured local Perception observation to update the *current* adjacency set of a previously physically visited site after the Phase-1 Exploration `exploration_observe` UC is accepted. The gate for reading the changed route must remain in a subsequent Phase-1 Planning read from the **frozen before-Phase-1** Exploration state. A newly free neighbor is **not a newly visited location**; no invented physical visit or intrinsic reward is permitted until an actual step-opening capture there. The old stored free-neighbor set must not be promoted to permanent 'safe' truth or retained as a hidden oracle. This is a route-graph maintenance rule, not acquired causal knowledge.

- Default existing Stage 11 configuration and existing `geographic-exploration-v1` and `geographic-exploration-v2-survey` owner snapshots remain exactly as before. Distinct opt-in config `refresh_surveys=True` requires `observe_routes=True`, and exports/restores a new `geographic-exploration-v3-survey-refresh` snapshot schema. Reject cross-version restores.
- For an already observed physical position, if **the current paid Perception** differs from its prior recorded free-neighbor set on a **new world step**, atomically replace only that position's survey, carry the new `world_step`, and record old and new neighbor sets plus observation provenance in the canonical journal. Reject a conflicting second survey from the **same world step**; no 'refresh' from Planning, map truth, an uncharged cycle, or a future-timestamp record.
- Reobserving unchanged neighbors must be idempotent and cost no additional artificial update (the ordinary `exploration_observe` cycle charge still exists).
- Strictly reuse the existing bounded visited-site router, UC charges for route search + preflight + plan build, Competition and final Action Control safety veto. No threshold change or safety-policy update.

## Frozen software comparisons and checks

Same fixed 10-step public junction and body as the earlier recorded experiment. `creature_blocks_return` (creature at 3,2 throughout after step 3), `creature_removed` (placed at step 3, removed at step 5), `unchanged_control`, and `unknown_danger` (nonlethal hazard at step 3, no visible creature). Compare **old opt-in routing owner** against the **new survey-refresh opt-in owner** with otherwise matched physical inputs and the *corrected* Stage-3 reflex. Report all trajectories and physical captures; specifically report **whether** the reopened edge is traversed after step 5, not a presupposed successful return. No injected destinations, commands, information leaks or fabricated visits.

Check versioned snapshot roundtrip, atomic rejection of future/unvisited/duplicate surveys, current-step physical adjacency, no additional owner surveys in no-UC Exploration cycles, journal validation, exact independent reexecution with SHA-256 input/owner/journal provenance, and no route into an active creature-occupied neighbor. Unknown hazard must remain unknown without physical/canonical evidence; report damage as externally scored. Negative outcomes must remain in final report.

The entire change is **opt-in**, distinct from Stage 9 held-out and the separate Python3.11 and Golden validation campaigns. Keep the repository private and PR #25 draft.
