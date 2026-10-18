# Issue #317 architecture experiment: decouple factual place recall from active need

## Diagnosed mismatch (authenticated paired WALs)

In the frozen corrected cohort, the memory option `option:place-memory:...` is produced with `goal_ref=goal_for_planning.id`, even if I1 has never experienced a beneficial consequence of that entity. The Stage11 intrinsic bonus is only confidence in the **location** and generic informational interest, not a physiological affordance. GoalManager can change active needs within a step. Stage11 phase-1 Planning often uses the prior-cycle frozen goal while Competition registers against the newer actual GoalManager goal, causing failed registration. Later switches invalidate the registered candidate and its accumulated confidence. This conflates "I know where it was" with "it must fulfill my current need."

Competing legitimate actions additionally apply Competition's existing residual to losers, including memories: on the observed `oasis/1141` control, the same memory option falls from about `0.2276` to `0.1138` after a genuine collect action, despite stable position and goal. That residual is a **separate** intended Competition mechanism, and this experiment deliberately leaves it unchanged. Never simply remove its penalty to inflate crossings.

## Surgical architectural change

The place-memory proposal now carries **no goal reference** (as with generic frontier exploration). Its informational intrinsic valuation remains confidence- and temperament-based, with exactly the same cap and weights. Learned Stage8 Q-values are still context-dependent (current EvaluationState), so an actual experience can change later evidence without an innate class-to-need correspondence. Need pressure still governs goal-oriented options and provides the context of TD evaluation; no fake relation `water_source -> drink` or `berry -> eat` is added.

The proposal continues to be generated only from the owner's first-person observed and validated route and still requires at least one active goal at the existing Stage11 scheduling gate: **no new unconditional memory search/UC**. Action Control's final motor veto and the one-hop plan preflight are unchanged. Changing the goal while standing at the same personally observed site no longer invalidates the *information* option. Goal-bound alternatives still expire on goal change and plan semantics change resets evidence. The current destination/hop option ID remains local and cannot transfer evidence to an arbitrary new route after movement.

## Falsification and gates

- A generated I1 unit/integration test compares world-step identity, goal changes, negative/zero evidence, material plan changes and unchanged Competition residual for true winners.
- Run the pre-existing paired 8-life worlds and **then held-out seeds**. Track survival, thirst and hunger, sleep, physical movement, memory Competition crossings, actual *out-of-sight* first hops, multi-hop arrival, prior TD reuse, and UC. Any gains from a remembered site that is still visible are local only.
- If goal-neutral familiarity causes unlearned, non-useful returns that degrade survival or UC, this is a scientific NO-GO; revert or redesign rather than lowering thresholds.
- The original `main` control PR #316, I0 source, mortal physics, and archived WALs are never changed. This is an experimental patch, **not yet an accepted general navigation or learned-utility proof**.
