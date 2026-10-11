# Stage 11: first divergent decision after transient hidden physical harm

**Additional public development diagnostic registered 2026-10-11 AFTER the result of prior experiment, BEFORE this trace implementation.** This is expressly a *post-result diagnostic*, NOT a preregistered scientific hypothesis, hidden-seed result, Golden or causal intervention. Original ten-step protocol and all eight SHA-pinned outcomes remain unchanged in `stage11-transient-hidden-route-uc-snapshots-results-2026-10-11.fr.md`.

## Known negative observation to investigate, not retune

On source/test `00619fecae037269b60b47cff0141a4e7019adc1`, [CI #38134913304](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38134913304), both 4/4 UC cases have the same first four physical commands, including two charged route transit hops through visited positions. The control moves south to the previously observed frontier at world step 5 and captures a southern branch. The hazard case, which physically lost 10 integrity points after a hidden zone was set at step 3 and removed before step 5, chooses the permanent `attendre` instead. Canonical danger status remains `unknown`. This behavioral divergence is an observed **negative** result. Do not equate it with knowledge of hazard absence, safety gating, causal learning or correct rest.

## Fixed trace, extraction and exact-replay checks

Only investigate the two already named `control` / `hidden_transient` conditions, with **(Planning, Exploration)=(4,4)** and **exactly ten** public real world steps on the existing `junction_open`, `survey_refresh=True` runtime. External events are unchanged: `set_danger_zone(active=True/False)` at step 3, then `set_danger_zone(active=False)` at step 5, each logged with sequence 0. Capture full periodic snapshots after steps 4 and 5 in the same order/version as the original fixture; do not restore or execute a second instance on a different schedule before comparing ten-step journal bytes. The next run is independent with exactly the same inputs and snapshots.

At the **first divergent world step, step 5**, read the **technical journal as Lab only after the action**, and extract per-cycle, in logged causal order, the already emitted:
- `stage11_geographic_option_proposed` (option ref, source, target, destination);
- `stage11_intrinsic_evaluation` (option ref, status and numeric intrinsic term);
- `stage8_option_evaluation` (option ref, learned/simulated status);
- `competition_cycle` (actual accumulator before/after, threshold and whether the option crossed);
- `stage11_geographic_preflight_consulted`, `stage11_geographic_budget_deferred`, `stage11_geographic_planning_unavailable`, and `s_t_published` for provenance and budget;
- `stage11_modulation_transition` in steps **3–5** (profile changes only when actually published), plus read-only profile name immediately after world steps 3, 4 and 5;
- `command_admitted` / `command_vetoed` at step 5, if present.

Also report true body integrity *only as a Lab measurement* after steps 3, 4, 5 and the actual step-5 command/source. Extract **no future truth into Planning or Exploration** and generate no new reward or explanation in the running system. Do not alter Stage-11 runtime, thresholds, UC envelopes, safety policy, frozen Equipment, world physics or intrinsic-motivation coefficients.

Build a versioned, JSON/hashable retrospective trace from only these preselected public fields and log it. Compare two independent executions of each variant including snapshot IDs/hashes, normalized technical journal bytes and the filtered trace. Compare the unmodified ten-step journal digests with the SHA-256 values already recorded in the earlier result for budget 4/4; a difference is a failed reproducer, not an invitation to rebase the old evidence. Do not assert a **causal explanation** from correlation alone. The software gate checks technical trace availability/format, provenance, initial noninterference and exact replay, not a particular level of exploration.

## Boundaries

Keep the result under a separately versioned probe and test. The original matrix remains permanently attributable to its previous source SHA, unmodified. Record the first factual difference in published proposals or accumulators, if observable, and state any ambiguity. If no admissible explanation is recoverable from the technical trace, retain **INCONCLUSIVE**, never tune for a PASS. Goldens and independent held-out remain separate. No PR merge, normative specification edit, `main` write, GitHub settings changes or new permanent CI triggers.

**Stage 11 IN PROGRESS; Stage 9 scientifically NO-GO; PR #25 Draft/unmerged.**
