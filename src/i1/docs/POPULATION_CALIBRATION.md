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
