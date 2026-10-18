# I1 – Prospective movement/needs investigation: 24-life physical evidence

**Date:** 2026-10-18  
**Scientific disposition:** `NO-GO` for a universal novelty-weight promotion; `CONDITIONAL` evidence for unblocking local movement in the garden, and `NOT_ESTABLISHED` for long-horizon survival, learning and cognitive sleep balance. No changes to `main` or I0.

## Exact reproducible provenance

- GitHub Actions run: [#39115068415](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39115068415), **12/12 jobs PASS**, 2 independently born mortal I1 individuals per job.
- Physical-run SHA: `545e8185886a34e662d9cf9c3555f972d7837d20`; branch PR [#300](https://github.com/josselin-orta-lab/individual-zero/pull/300). Later branch commit `22bc36220501262b278afed860ebc60c40b375d0` changes **only campaign documentation** relative to the physical SHA (verified by GitHub compare).
- CI of the current branch: [#39115100516](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39115100516), **4/4 green**, including Python 3.11/3.12.
- Worlds: `longlife-garden`, `oasis`, `foraging`; independently generated resource-layout variants **1 and 2**, same layout SHA and seed `773001/773002` across each world's four arms.
- Exactly one isolated experimental intervention: `GeographicExplorationConfig.novelty_weight` at birth, **0.15** (reference), **0.30**, **0.60**, **0.90**. Sleep-cognitive fatigue coefficient fixed at `w_F=0.0` **in these scientific processes only**. No arbitrary action order, knowledge of hidden map, forced drink, rollback or resurrection.
- All 12 artifact ZIPs expose full WAL + `report.json` + `investigation.json` per variant. External audit verified 24 expected combinations, identical paired-world hashes and seed labels, one physical applied/dead outcome per simulated step, actual-parameter receipt, same physical SHA and all reported action tallies.
- **24 newborn lives, 6,308 observed steps, 14 terminal deaths, 10 right-censored lives at the 300-step horizon**. The latter are not proven to survive beyond 300. Two variants per world do **not** support statistically persuasive confidence bounds.

## Outcomes (two individuals per cell; all deaths included)

Here `move`, `drink`, `eat`, `collect` and `sleep` count **physically executed command steps**, not intention, opportunity, inner episodes or memory usefulness. `alive` is merely active on stopping at 300 world steps.

| World | Novelty | Alive/2 at 300 | Observed steps | Move | Drink | Eat | Collect | Sleep % of observed steps | Water-zero steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| foraging | 0.15 | 0 | 456 | 0 | 0 | 0 | 0 | 9.0% | 246 |
| foraging | 0.30 | 0 | 456 | 0 | 0 | 0 | 0 | 9.0% | 246 |
| foraging | 0.60 | 0 | 427 | 159 | 0 | 0 | 0 | 13.8% | 217 |
| foraging | 0.90 | 0 | 423 | 174 | 0 | 0 | 0 | 9.5% | 213 |
| longlife-garden | 0.15 | 0 | 469 | 1 | 0 | 2 | 2 | 14.9% | 245 |
| longlife-garden | **0.30** | **2** | **600** | **252** | **6** | **10** | **10** | **30.5%** | **0** |
| longlife-garden | 0.60 | 2 | 600 | 280 | 6 | 7 | 7 | 34.5% | 14 |
| longlife-garden | 0.90 | 2 | 600 | 476 | 6 | 0 | 0 | 15.7% | 30 |
| oasis | 0.15 | 1 | 595 | 159 | 5 | 8 | 8 | 40.3% | 108 |
| oasis | 0.30 | 1 | 595 | 170 | 5 | 8 | 8 | 39.0% | 108 |
| oasis | 0.60 | 1 | 544 | 217 | 5 | 5 | 5 | 31.2% | 57 |
| oasis | 0.90 | 1 | 543 | 220 | 5 | 5 | 5 | 30.9% | 56 |

## Mechanism and interpretation

**M1 — deficient exploratory ignition is demonstrated locally:** in garden at 0.15, the same independently generated variants exhibit no geographic Competition threshold crossings, 1 physical move in 469 observed steps, no drinks and two deaths. At 0.30, there are 251 geographic threshold-crossed steps, 252 applied moves, six drinks and ten meals, and no death by step 300. The main observable change is in the *individual's competition for a perceived, physically available frontier*, not a forced survival script.

**M2 — maximum curiosity is not optimal even within garden:** at 0.90, 476 physical moves and six drinks but **zero meals**, 152 observed food-zero steps, mean final bodily integrity approximately 48.8 (versus 100 at 0.30), and **zero Stage10 technical consolidation receipts**, despite both lives reaching 300. At 0.60, some hunger crises persist and there are 31 technical commits, while at 0.30 there are 37. Technical memory receipts do not prove durable useful learning.

**M3 — mere movement is not enough:** in foraging at 0.15 and 0.30 both individuals die at step 228 without ever moving or drinking. At 0.60/0.90, movement (159/174 pooled physical moves) is real, yet both individuals still die in each arm without a single drink or meal. This calls for studying experienced outcome knowledge and return-to-resource behavior, not indiscriminately raising novelty.

**M4 — high novelty can displace need satisfaction:** oasis variant 1 moves off its spawn resources and dies at step 295 under 0.15/0.30 but earlier at step 244/243 under 0.60/0.90. Oasis variant 2 stays at its spawn resource, drinks/collects/eats and reaches 300 under all four values. **The two source-world variants must not be pooled into a claim of universal benefit.**

## Next preregistered questions

1. With new, independently generated maps and fixed temperaments, test whether 0.30 still permits movement and real drinking/eating beyond the 300-step horizon, with and without moderate cognitive sleep pressure.
2. Instrument **first-person visible/current resource**, goal pressure, budget, physically applied action, post-action physiological delta and remembered earlier resource encounters. Avoid reading operator map inside I1.
3. Isolate whether absent *return to previously discovered resource* is primarily a memory-retrieval/route-planning gap, not a lack of motivation. The current I1 geographic default has `observe_routes=False` and only promotes novel adjacent frontiers; this does not establish that a learned resource location can be revisited.
4. Evaluate subjective option arbitration under simultaneous thirst/hunger/fatigue before making any model correction. No fixed eat-first/drink-first priority is introduced.
5. No GO for a production coefficient or for causal learning without delayed-task advantage, published retained semantic content and survival noninferiority across sufficient independent layouts, always including deaths.

**Conclusion:** the hypothesis in [#299](https://github.com/josselin-orta-lab/individual-zero/issues/299) is partially validated: an inadequate exploration drive can be a movement bottleneck. A simple globally increased novelty setting is **not** an adequate general repair of the need/survival system.
