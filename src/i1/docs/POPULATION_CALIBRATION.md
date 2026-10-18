# I1 natural population calibration: baseline-first optimization

Started 2026-10-18 on main `75762dc`; **restarted entirely from updated main `c82552c88c3b72384be7c14ce17b7dd6442dc30e`** after the explicit model integration of merged #309 and #312. No experimental research branch was copied. The native GoalManager control is now `0.04 / 0.35`; natural berry_b integrity damage is `-10`, frozen before birth in the native runtime. All pre-rebase cohorts and results are invalidated for this calibration. Use only new post-rebase cohorts and their SHA as evidence.

## Research question

Does a *population-level* choice of frozen, prebirth numerical owner parameters improve mean and worst-case bodily survival across independent natural I1 lives, while retaining subjective choice, native ValueNeeds, TD, Competition, body physics, sleep and death? **Parameter optimization is not in-life learning.**

## Isolation

No changes to `src/i1`, `src/i0`, body physics, sleep, motor selection or TD learning. The evaluator calls `birth_i1` exactly once per life. Candidate zero forwards unchanged current-main reference configurations. Calibrated GoalManager is native, not searched. Every other candidate uses `dataclasses.replace` exclusively before birth on **frozen GoalManager and Competition numeric configuration**, threaded through matching Stage11/Stage10 Stage9 owner trees. Natural birth still projects individual temperament and sleep rules. Same `life_id` for matched world+seed in separate independent processes retains temperament; unique separate WAL paths prevent shared history.

Initial search dimensions: Competition base threshold [0.30,0.65] and gain [0.75,1.25]. GoalManager remains exactly `0.04/0.35`, with no override or experimental selector. Other variables, especially ValueNeeds weights (later transformed by temperament), TD, sleep, reward and physics, are **fixed**. Search candidates are reproducibly drawn by external seed 20261018, not chosen using previous scientific results. This first batch is a bounded random-search matrix, NOT CMA-ES or a trained model.

## Stage 1: prospective screen

6 configurations, including native baseline, 2 worlds `oasis` and `foraging`, paired seeds 901/902, 120 maximum physical steps per life: 24 independent mortal lives. No forced actions or cheat information. Outputs: full WAL audited by canonical HashChainedJournal auditor; effective born config, SHA, world digest, actions, bodily trace, zero-needs time, deaths, TD version and learning coefficient. Score is external only: 0.8 survival fraction + 0.2 fraction of needs above zero; no TD reward is influenced. Rank primarily by worst-case candidate score, then mean; report deaths separately. The ranking does not declare a scientific GO.

## Gates

- Any changed source outside tools/tests/CI/docs is a NO-GO.
- Refuse mismatched physical config or TD owner, changing configs during a life, dishonest WAL, mixed SHA, mismatched candidate/world/seed cohorts or missing lives.
- A 120-step pass is screening only. Later rounds must allocate longer horizons with fresh independent seeds and held-out worlds, compare against the untouched native baseline, and measure robust vital dynamics, learning, consolidation, premature death and full lifespan before promoting a single parameter set.
- No automatic promotion or merge. I0 remains unchanged, all mortal deaths final.

Scientific status: `NOT_EVALUATED` until full paired cohort and held-out replication.


## Follow-up after first completed screen (2026-10-18)

The post-berry, post-hysteresis natural cohort [Actions #39140561923](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39140561923), SHA `1f96e78b`, completed 24/24 trials successfully. Every candidate scored exactly 1.0 in oasis and 0.991666667 in foraging at 120 steps; all 24 survived to censoring. The score was saturated, so it **cannot rank the six parameter sets**. No finalist was selected from these data.

PR #313 (read-only birth capability audit and strict toxic-berry parity) has since been merged to main at `2161b834`; this research branch is rebuilt on that main. A new prospective batch uses independent paired seeds 911/912, both worlds, 6 candidates, 300-step maximum. Each real I1 birth is independently validated with the same passive Stage4–12 audit as merged main. Every candidate retains natural GoalManager `0.04/0.35`, toxic berry `-10`, TD reward, fatigue, consolidation and all normal active cognitive capacities.

The external training score is now `0.7 * observed_steps/horizon + 0.3 * (1 - average normalized physical deficit)`, where each channel `water`, `food`, `energy`, `integrity` contributes the bounded shortage `(100 - clamp(body,0,100))/100`. This rewards lower shortage even when no channel reaches zero, but **does not modify the internal TD reward**. Report minimum integrity, death, drinks, food actions and physical history independently. This is still screening: no scientific GO or parameter promotion without held-out worlds/seeds and long survival.

Software risk: the previous score saturating is an **experimental evaluation deficiency**, not evidence of a broken I1 engine. Previous full-I1 CI failure was caused by the historical toxic-berry parity approval and is repaired by #313 with all general CI checks passing. Any newly identified genuine causal bug must be isolated rather than silently compensated by optimized parameters.
