# I3 Stage 2.1: local TD-prioritized versus random memory-identity falsifier

**Frozen before any local software test, 10 November 2026. Synthetic local mechanics only.**

## Why the new intervention is necessary

The closed and preserved 64-unit FIXED/GATE/RANDOM developmental cohort showed 27/64 horizon survivors for GATE and RANDOM, respectively. Source review in [RANDOM control semantics](RANDOM_CONTROL_SEMANTICS_AND_NEXT_FALSIFIER_2026-11-10.md) proves that `p13_replay_gate_random_equal_mean_v1` randomizes the **replay count**, while both policies still select which replay memories to update in descending TD-error priority order. The current question has therefore changed: what does **experience-based replay-content prioritization**, by itself, change in the immediate learned-value state when actual replay work is held fixed?

## Frozen design

[Machine-readable plan](CONTENT_SELECTION_LOCAL_FALSIFIER_PLAN.json) establishes exactly **48 synthetic starting Mind states**, numbered 0–47, generated with newborn genome seeds `9200000 + i` and local Mind seeds `9900000 + i`. Each contains **12 synthetic memory records** (valid internal before/after body states, no World origin), fixed before inspecting results. The baseline reference P1.3 learning formula `Mind._td` executes on **two deep copies** of each starting state.

- **TD PRIORITY:** first three memories sorted in descending absolute TD-error priority, exactly as `Mind.learn_from_outcome` currently does.
- **RANDOM CONTENT:** three distinct memory slots ranked by an independent, life-seeded HMAC stream using domain `i3-stage2.1/random-replay-content-local/v1`, without replacement or touching the Mind's own RNG stream.
- **Both:** exactly three genuinely executed `Mind._td` updates on their selected memories; a fresh `CognitiveBudget` pre-authorizes the same one-cycle selection overhead and same per-replay `CognitiveWork(simulated_steps=2*len(proj_chunks),replays=1)` for both copies. Use current `BodyLaws` and the same initial body `(80,65,65,90,80)`.
- **No World:** the report contains the exact **would-be World debit tariff**, not a claim that a real life has paid it. No motor action, World, survival result, genome evolution, policy upgrade or stage promotion occurs.

**Primary finite local response:** number of 48 snapshots with different final learned-value vectors (L1 distance nonzero) after the two equal-count interventions. Secondary: memory-subset overlap, mean absolute value-update magnitude, L1 between-arm difference, per-arm identical advance `CognitiveWork` and calculated energy/vigilance bills. The plan is descriptive, with **no artificial minimum advantage threshold** and no claim that magnitude of TD update equals expected fitness or survival. Return every null or adverse trial. No synthetic case replacement or after-outcome hyperparameter tuning.

If the identical work/physical tariff invariant fails, or the original Mind state or either RNG stream changes, the entire test fails before any result can be accepted. If selection differs but learned values do not, that is a valid negative local finding. If learned states differ, the result proves only the **software mechanism** can alter learning at fixed model work; it does not establish a beneficial change in survival or robustness.

## Practical consequence

This is a necessary structural/mechanistic experiment, *not* the next biological cohort. Only after all source/physical invariants and before any later World opening should a separate full-life design decide whether to cross replay **count** policies with replay **content** policies, how to witness independent ecological draws and how to quantify biologically meaningful viability effects. Preserve all closed original cohorts; do not change P1.3 or the frozen GATE formula to improve outcomes.

Run (software only):

```bash
PYTHONPATH=src python -m unittest discover -s tests/i3 -p 'test_stage2_replay_content_local.py' -v
PYTHONPATH=src python -m i3.lab.stage2_replay_content_local
```
