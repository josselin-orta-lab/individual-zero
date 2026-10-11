# Stage 11: hidden physical hazard under constrained UC and interval snapshot

**Development-only test contract recorded 2026-10-11, before implementation.** Sole normative authority: `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, §§4.6, 9.2, 17.1, 17.6, DC-05, DC-07, DC-08 and INV-08/21/25/33. This is NOT a preregistered scientific held-out trial, Golden or Stage 9 acceptance.

## Motivating gap

Existing public software fixtures exercise (a) a hidden `set_danger_zone` at world step 3 with the default cognition budget, (b) planning 0/1/3 UC and Exploration 0 UC in other worlds, and (c) snapshots with synthetic promoted known lethal facts. The combination **hidden danger + logged external change + strict UC + complete snapshot restore** has not been tested together. The hazard must remain world-only until legitimately perceptible consequences are experienced, never be read from WorldBody's hidden ground-truth zone membership by the individual.

## Frozen inputs

- Use `build_public_route_runtime(layout_variant="junction_open", survey_refresh=True, ...)`, existing public action equipment, and the real Stage11Runtime. No mock of Action Control, equipment, perception or canonical safety.
- Register two external scenario programs with the *same* id, version and event position/time but different effect: `ScenarioEvent(t_monde=3,sequence=0,operation="set_danger_zone",payload={"position":{"x":3,"y":2},"active":False})` for control, and identical with `active=True` for the hidden-hazard branch. No extra hazard information may enter cognitive input.
- Test the versioned UC profiles `(planning_uc,exploration_uc)=(0,0),(1,4),(4,4)`; no ad-hoc unversioned budget monkeypatches. For every profile, run physical world steps 1–3 on both branches. Compare actual logged `perceptual_capture` positions and `adjacent_creature_count`, and the actions/sources selected through the end of step 3. Before the change, actions/captures must agree; at the step-3 perception boundary the danger change is hidden and cannot affect an already selected command. Later bodily damage may legitimately alter future decisions.
- Check `external_input_received` and `external_input_applied` at exactly step 3, with matching operation and position but intentionally distinct `active` value. No `external_input_rejected`. Both technical journals hash-verify.
- The Lab-only `world.export_causal_state()` may establish that the two physical worlds differ at step 3; it must never be passed to the individual. Canonical `zone_status(x=3,y=2)` is `unknown` before the change and must **not** become known merely from the external input. New information must come from actual physical experience and satisfy DC-05. Do not assert that unknown means safe or that all future damage is avoided.
- Budget checks: for `planning_uc=0`, no Planning budget charge with `accepted=True` is allowed. With `exploration_uc=0`, no paid Exploration `exploration_observe` charge can be accepted. Deferrals must not claim a safety verdict or novel information. The physically captured site register remains independent of UC if a real capture exists.
- For the `(0,0)` and `(4,4)` hazard branches, take a complete periodic snapshot after step 3, run step 4, restore, compare every exported causal-owner state exactly, including WorldBody hazards, scenario cursor, canonical safety, scheduler and Memory. Technical journal remains append-only.
- Reconstruct each budget+hazard program independently and compare normalized journals and complete owner states after the first 3 steps, without re-running a rewound step on the same journal.

## World-only hazard input type fidelity addendum (2026-10-11, before implementation)

WorldBody's current scenario interface silently coerces `payload.active` using `bool(...)`; nonempty text such as `"false"` consequently activates a hazard. It also coerces grid coordinates through `int(...)` for danger/lethal-zone and creature inputs. These conversions change physical truth without matching the logged input's declared type and value. The external scenario interface MUST require `active` to be a literal Boolean for `set_danger_zone` and `set_lethal_zone` (default `True` when absent); any explicit non-Boolean is rejected. All world-only `position` inputs MUST contain exactly `x` and `y` as true integers (not bool, float or text), validated before mutation. This constraint is on **external world input interpretation**, not the individual's Action Control admissibility or spatial movement.

Fixed unit cases: `set_danger_zone` and `set_lethal_zone` reject `"false"`, `0`, `1`, `None` and array-typed activation; reject fractional, Boolean, string and extra-key grid positions. Preserve `world.export_causal_state()` exactly after each rejected call. Verify that a valid Boolean deactivation removes an actually active zone and that successful scenario programs still record receipt/application before Perception. No hidden world hazard is leaked to cognition.

## Limits

These are public deterministic software tests, not a measurement of independent scientific learning or unknown-hazard generalization. No oracle-derived safety fact, synthetic DC-05 evidence or safety guarantee is introduced. The test must never require a particular *action* when budget exhaustion legitimately changes selection. A failed test is preserved and diagnosed, not weakened into a misleading success.

**Status before execution: UNVALIDATED.** Python 3.11 full, Goldens and Stage 9 held-out remain separate; Stage 11 IN PROGRESS; Stage 9 scientific NO-GO; PR #25 remains draft and unmerged.
