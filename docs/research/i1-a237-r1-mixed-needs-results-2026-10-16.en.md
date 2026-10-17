# A2.37-R1 scientific outcome after D2 null-geography repair

**Date: 2026-10-16.** **Not independent confirmatory replication.** The preregistered A2.37-v1 initial cohort had technical FAIL (16 invalid lives) and is permanently archived at `docs/research/i1-a237-first-attempt-failure-2026-10-16.en.md`. [Amendment 1](i1-a237-fault-amendment-1-2026-10-16.en.md) transparently authorized only a software repair in the I1 D2 overlay; never changed worlds, thresholds, model priors or actor memories. This R1 reruns the **same** 32 deterministic triplets after the D2 fix.

**Exact validated R1 HEAD:** `d35039dbd66e82b404ac591e0a55520444ca57fa`. [GitHub Actions R1 run 38886469863](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38886469863): two SUCCESSFUL scientific jobs Python 3.11 and 3.12, including the new five-step actual mortal `test_i1_a237_d2_no_geography.py`. Summary hashes, all stratum metrics, source SHA and external training checksum match. Both jobs archive **all 96 lives and individual WALs**.

## R1 unfiltered science results

**96 distinct mortal births, 32 matched triplets, 1,536 applied physical transitions, 0 detected hard technical violations and 0 deaths.** All four experimental models explicitly enabled in FULL, with independent `NO_RECALL` and `NO_D2` birth ablations. Frozen physically executed external lab training SHA-256: `38beae290dfda31d5b2a1176d12b21cc344f13bd7e2c5c060fc47413bb5b3af6`. This is **not** first-person lived information.

| Mixed-food/water stratum | FULL both physically collected and drank | NO_RECALL | NO_D2 | Interpretation |
|---|---:|---:|---:|---|
| BOTH_LOCAL | 8/8 | 8/8 | 8/8 | Actual same-life mixed needs can be satisfied when both resources are immediately accessible |
| BERRY_LOCAL_WATER_E | **0/8** | 0/8 | 0/8 | All arms repeatedly wait: a water goal persists without learned access to east-water and suppresses local-food opportunity |
| WATER_LOCAL_BERRY_E | **0/8** | 0/8 | **8/8** | FULL/NO_RECALL first drink, then Stage6 proposes east movement for a real eat goal; D2 rejects all unvisited east moves |
| BOTH_LOCAL_WATER_E_HIDDEN_LETHAL | 8/8 | 8/8 | 8/8 | Locally available berries and water are used; no arm steps into the hidden lethal east cell. This is **not** evidence of detecting its hidden hazard |

**Pre-registered primary success criterion** required >=6/8 FULL lives jointly drink and collect in BOTH_LOCAL **and** BERRY_LOCAL_WATER_E. Measured 8/8 and 0/8: `MIXED_GOAL_NOT_DEMONSTRATED`, notwithstanding technical PASS. Do not reinterpret the alternate WATER_LOCAL_BERRY_E 8/8 NO_D2 as satisfying the primary criterion.

**First attempt remained FAIL:** The 16 original `AttributeError: 'NoneType' object has no attribute 'export_causal_state'` plus unclosed WALs are preserved, not erased or recoded. Post-repair null geography is an empty *authenticated* visited set and D2 charges and rejects, preserving validated WALs. The direct five-step I1 regression and whole R1 both pass on Python 3.11/3.12.

## Independent source-lineage diagnosis from complete first-person raw artifacts

The raw canonical journals resolve the former ambiguous outcome:
1. In `BERRY_LOCAL_WATER_E`, the active goal at step 1 is `drink`, and there is **no active change to `eat`**, no Stage6 model-origin proposal, no water option, and every command over 16 steps is `attendre`. Both needs are unmet at birth but the architecture prioritizes thirst and fails to use the immediately present berries while novel water is not yet learned. This is a **goal/opportunity and fallback issue**, not a failure to perceive berries.
2. In `WATER_LOCAL_BERRY_E`, physical `boire` occurs in steps 1 and 2; at step 3 the active goal genuinely changes to `eat`. Stage6 factorized model proposes `se_deplacer east` specifically for `goal:eat:food:3:1`. D2 emits a paid `i1_d2_movement_commitment_review` with `prior_physical_visit=False`, `current_safety_known=False`, `decision=defer_unknown_or_unfunded` referencing that **food-origin option ID**. The agent thereafter waits despite visible berries east. In the matched NO_D2 life, the same model-origin east movement is physically executed at step 3 and berries are collected from step 4. **D2's global movement veto spans goals**, it is not confined to water choices.
3. This broad D2 veto is a **research-policy tradeoff**, not a hidden-world classifier and not necessarily a software bug. Disabling it would expose lives to genuinely unobserved lethal hazards, as A2.36 proved. Do not silently exempt food movements or infer east-cell safety merely because berry B is visible.
4. `BERRY_LOCAL_WATER_E` uses 8,800 accepted UC over 128 steps across 8 FULL lives, delivering neither gain. `WATER_LOCAL_BERRY_E` uses 10,040 accepted UC over 128 steps in FULL versus 4,885 UC over 128 steps in NO_D2; only NO_D2 achieves mixed needs. Those aggregate UC differences include architecture-wide cycle costs and repeated option reviews; **they are not all D2's marginal review price**. No claims about longer-term nutritional/water death are possible in a 16-step zero-consolidation-weight fixture.

## What is and is not proven

**Proven within this repaired deterministic software cohort:** hash/journal validity, source-backed first-person water/berry evidence under real physics, independent ablation flags, bounded score upgrade after real berry history, authentic mixed-need behavior for locally accessible resources and a cross-goal movement veto with actual action trace.

**Not proven:** real global-goal deliberation, safe/adaptive exploration, learned unknown hazard classification, a behaviorally useful effect of 0.35→0.45 recalled collection scoring (all arms succeed in BOTH_LOCAL), improved mortality, longer-horizon metabolic policy, independent replication, safety under changed previously visited zones. The hidden-lethal auxiliary source in R1 was not physically contacted; zero mortality is **not** proof of a hazard detector.

## Next hypothesis without unwarranted omniscience

A2.38 should separately preregister and test:
- **Goal starvation under inaccessible dominant thirst**: an epistemically valid way to surface the currently available local-food opportunity alongside a blocked hydration goal, with typed per-option source/evidence, actual UC and no fabricated knowledge.
- **Cross-goal physical exploration**: a *bounded, priced and mortal* policy for committing to unvisited cells based on genuine need pressure and first-person evidence **without knowing whether invisible lethal hazards are present**. Match safe/lethal perceptually identical worlds and quantify both opportunity and death; distinguish choice policy from predictive accuracy.
- **Longer horizon and cold M11**: actual persistent learning under both needs, UC exhaustion, irreversibility, and source/agency attribution. A higher exploration success rate in safe cells without admitting mortal loss in matched hidden-lethal worlds would be a misleading, unbalanced endpoint.

**Release disposition:** technical R1 **PASS**; scientific mixed-goal criterion **NOT DEMONSTRATED**, general I1 cognitive deployment **NO-GO**. Draft PR #227 remains unmerged, I0 and WorldBody unchanged.
