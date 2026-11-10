# I3 Stage 2.1: control semantics audit and next falsifier

**10 November 2026. Source-level methodological clarification, not a new scientific World or result.**

## What RANDOM actually randomizes

The closed 64-triplet developmental panel found 27/64 GATE survivors and 27/64 RANDOM-EQUAL-MEAN survivors, with four GATE-only and four RANDOM-only horizon survivors. This is a robust **finite-panel null risk-difference observation** and must not be rewritten or declared confirmatory equivalence.

A direct source review reveals a distinction which should accompany every interpretation of these data:

1. `modules/stage2_random_equal_mean.py::scheduled_replays` uses a life-seeded HMAC/SHA256 count schedule, choosing **6 or 7 nominal replay slots** at each reached/eligible sleep opportunity. This is a randomized *quota*, not randomized replay-content selection. The target mean `5532/867` was frozen from the old 80/81 developmental cohort.
2. `modules/p13_replay_gate_mind.py::P13ReplayGateMind._gate` computes the same paid GATE diagnostics, then in `random_equal_mean` mode replaces the GATE-chosen count `k` with `min(random_nominal, eligible)`. This mode does **not** choose randomly *which* replay memories or transitions will be updated.
3. `modules/mind.py::Mind.learn_from_outcome` unconditionally orders its TD replay buffer using `best = sorted(range(len(replay_mind.buffer)), key=lambda i: -replay_mind.buffer[i][0])` and updates `best[:replay_limit]`. Both paid GATE and RANDOM run this same prioritized buffer selection (subject to the actually funded count).
4. The physical work debit remains real. In the completed 64-unit panel RANDOM scheduled 32,146 nominal slots, 32,120 eligible, and actually paid 32,120; GATE paid 32,969 replays. Equalizing an *historical* mean count does not equate realized per-life or per-sleep counts, eligible memories, survival duration, fuel bills or learning trajectories.

**Terminology correction:** name the historic comparator **`RANDOM-COUNT-PRIORITIZED-REPLAY`** in explanatory prose, while leaving its immutable runtime policy ID `p13_replay_gate_random_equal_mean_v1` and all previously executed files untouched. Calling it a randomized *memory selection* control would be false. The completed outcome distinguishes **two full-policy replay-quantity decisions**, not a TD-prioritization versus random-content-selection effect.

The 64-triplet data are not evidence that TD prioritized experience selection lacks value, nor that a GATE count is biologically equivalent to a random quota. Likewise, they do not isolate the GATE count's own causal mechanism at constant replay work: real counts and life duration still differ, and the intervention acts within a closed feedback loop.

## Revised scientific hypothesis, prospective only

**H-content:** At a *given realized prepaid replay count* and shared agent state at a chosen sleep-learning opportunity, selecting the highest-|TD-error| memories for updating produces a distinguishable local learned-state change from uniformly sampling the same number of eligible buffer slots without replacement. This is a local, identifiable contrast under the same available memory, runtime work and external state. It does **not** itself establish that such selection improves future survival.

**H-quantity:** With the same TD-prioritized content policy, choosing replay quantity from the individual's estimated future stakes versus a count-control schedule may change physically paid work, resulting trajectories and survival. The closed 64-triplet panel addresses this second question only as a full-life descriptive contrast, without exact per-sleep count matching. Any causal *fixed count* intervention changes the estimand and needs a fresh prospective protocol.

### Minimum experimental decomposition before new birth

Design two orthogonal interventions, not a retroactive fourth arm of the consumed cohort:

| Question | Variable changed | Controlled/verified | Appropriate inference |
| --- | --- | --- | --- |
| **Content** | Priority by experience-derived absolute TD error versus a genuinely random *subset* of replay items | Same starting state, prepaid count, eligible buffer, world state and actual measured energy/vigilance | Immediate differential learning/replay update (first local falsifier) |
| **Quantity** | GATE value/cost `k` versus count schedule `k` | Priority selection remains the same; document actual eligible and funded count | Finite or generalizable behavioral/survival policy effect only after a new powered, witnessed cohort |
| **Interaction** | Crossed content and count policies | Same published physics and action control | Interaction identifiable only after crossed design, not from old GATE/RANDOM history |

The first controlled CONTENT comparison can be a **detached learning-state software/engineering probe** using a cloned pre-sleep state and a new opt-in replay-selection laboratory helper. Its only output should be differences in learned representations and exact work/cost receipts. Both arms must genuinely execute the same funded replay work; the random-subset choice requires a new life-seeded independent random stream and may not consume or alter the organism's ordinary RNG stream. The original TD-prioritized P1.3, `_gate` formula, motor admission and world physics must not be changed. Unit tests should include deterministic replay identity under copied snapshots, rejection of bogus paid work and no contamination of original source branches. Declare the local estimand, input population and stopping rule **before** inspecting outcomes. If a software probe uses synthetic fixed learning states, treat it as mechanistic technical evidence, not a biological cohort.

A subsequent full-life crossed policy study, if scientifically justified by that probe, would need its own new source lock, World/genome/life allocations, independent sampling review, prespecified outcome and a single irreversible claim. No previously consumed indices 80/81, 240000..240095 or 360000..360063 may be reborn or reused. No post-hoc NI loss margin, favorable ecology selection, unobserved survival rescue behavior, Stage 2.2 or active engine registration is authorized by this document.

## Original-only readout before any further design

New pure reader `lab/stage2_three_arm_original_audit.py` validates **every** original gzip compressed/uncompressed SHA-256 against the preexisting pinned original manifest, reconstructs all 192 original reduced rows and complete 64 triples directly from sealed life histories, recomputes the paired survival and paid-replay counts, and verifies all published aggregate report fields without importing or executing World, Mind, genome or scientific admission. It is run by a PR-only CI job against exact evidence commit `aaff20234b8a4f9d11595d6eb852371d0ce00f97`, outputting an aggregate-only receipt. No original is modified or regenerated. Its PASS, if established by CI, strengthens custodial consistency, **not** iid sampling or causal interpretation.

**Research decision:** retain the B1 finite outcome, relabel the existing control accurately, and study replay **content selection** locally before paying for another large survival cohort. A null or adverse local result is equally admissible; do not tune the individual to force it to survive.

## Verified post-archive execution witness

The source-pinned independent checker was executed successfully in [Actions run #42786008464](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42786008464), job **I3 read-only 192/192 source-pinned original audit**, from PR #1255. The checker read exact evidence commit `aaff20234b8a4f9d11595d6eb852371d0ce00f97` without running a World. It verified **192 compressed and 192 decompressed original SHA-256s**, source-bound manifest digest `f493a30598c3dd82f56ab84653537286487bea61414cfc2226785209c724a50f`, all 192 identity-preserving original-to-reduced rows, full funding and RANDOM nominal/eligible/paid receipts, 64 matched exact source/genome/World/life triplets and the aggregate report.

Independent original recount: FIXED **26/64**, GATE **27/64**, RANDOM **27/64** horizon survivors. Primary GATE−RANDOM: **23 both, 4 GATE-only, 4 RANDOM-only, 33 neither**, paired difference 0/64. Family GATE-only/RANDOM-only: stable **2/1**, depletion **1/3** (adverse), pulse **1/0**. Original RANDOM total: **32,146 nominal**, **32,120 eligible**, **32,120 paid** replay slots; **5,046** funded draw opportunities, **5,047** lived sleep ordinals. The full read-only aggregate-only witness is [artifact #13749616920](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42786008464/artifacts/13749616920). This audit demonstrates source custody and numerical reproduction, **not** externally independent sampling or causal mechanism identification.
