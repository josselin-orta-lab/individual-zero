# Stage 4 technical decisions

Status: non-normative implementation notes.

Normative authority remains `docs/architecture/reference/en/mvp-specification-v1.2.1.md`.

## TD-S4-01 · Symbolic accessible field

The MVP specifies symbolic perception without noise in the minimal system and uses examples where a resource may be observed several cells away, but does not set a numerical visual radius for Stage 4.

The reference Stage-4 implementation therefore treats the entire 32 x 32 grid as the accessible **symbolic** field for entity type and position only.

This does not expose:
- danger-zone or lethal-zone classifications;
- toxic/nutritious hidden berry identity;
- oracle annotations;
- evaluation metadata.

The choice is a temporary observation-geometry stub. A future version may introduce an explicit P-52 sensor field without changing Perception's interface.

## TD-S4-02 · Minimal novelty before Stage 11

The Gatekeeper must use the normative five dimensions at Stage 4, while the full novelty, learning-progress, habituation and boredom mechanism belongs to Stage 11.

Until Stage 11, `n(m)` is exact-symbolic:
- 1 when the contribution's exact subject is absent from the current retained/queued pool and the recent W-step subject history;
- 0 otherwise.

No semantic embedding, learned novelty or exploration bonus is introduced.

## TD-S4-03 · E-0 route geometry

The minimal E-0 planner uses deterministic Manhattan routing with horizontal moves before vertical moves. It reads only Perception's last-known symbolic map and the active goal. It never reads the world or oracle.

Obstacle-aware search is not introduced at Stage 4. A blocked predicted step causes replanning from the next perceptual state, as required by the later comparator/replanning path.
