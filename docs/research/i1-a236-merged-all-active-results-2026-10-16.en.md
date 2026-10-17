# A2.36 — all I1 models ON after the latest merges into main: results and scientific disposition

**Date:** 2026-10-16. **Baseline:** `main` `bf59eceaf97805f04a18b0b28f1396f2e98bfa89`, integrated through PR #226. **Experiment PR:** #227 (Draft), I1-only. **Frozen preregistration:** `docs/research/i1-a236-main-integrated-active-prereg-2026-10-16.en.md`, committed as `324b04b6dd51395fd6ebdbcd1a23f843cf929621` before the physical runner was created. **Exact passing code:** `048e4cb5568eac6c69de22adb2a4b437bce264e6`. [Latest Python 3.11 + 3.12 CI](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38879286978), both SUCCESS.

## Experimental arms and independence

48 externally configured world triplets, 144 distinct mortal I1 births, 6 strata × 8 distinct world indices × 3 arms. All arms explicitly turned **on** the external-lab factorized predictor, first-person water learning, and water perception/proposal pipeline. `FULL` additionally enables remembered positive berry collection and D2 prudence; `NO_RECALL` disables only remembered berry collection evaluation; `NO_D2` disables only D2. Each individual owns WorldBody, Stage12, first-person causal journal, WAL, Memory and irreversible mortality. No inter-individual memory transfer.

**Physical external laboratory prior**: 16 real independent WorldBody actions (8 MOVE_E, 8 COLLECT_B) with sealed SHA-256 `b82b6e0931053923c8417a8053405b4e17f5953e5f32fe88b8757613351efcc1`. This is not I1 lived knowledge. Heldout lives were not used to fit the model.

**Measured:** 144 lives, 48 triplets, **1,208 applied/dead physical transitions**, **0 hard violations detected** by the preregistered checks, zero recorded exceptions/invalid journal attestations. Both Python jobs report identical external training SHA, complete per-stratum summary, and number of lives/transitions, with independent WAL/artifact archives per job. The two Python versions repeat **one deterministic cohort**; do not call them independent scientific replications.

## Six-stratum science ledger (all figures per eight independent mortal lives per arm)

| Stratum | FULL | NO_RECALL | NO_D2 | Narrow interpretation |
|---|---|---|---|---|
| Local berry | 8/8 source-backed recalled boosts, 8/8 actual collection lives, 0 deaths | 0/8 boosts, 8/8 actual collection lives, 0 deaths | 8/8 boosts, 8/8 collection lives, 0 deaths | Recalled outcomes change score, **not demonstrated to change physical action** |
| New east water, safe | 0/8 achieved learned transfer, 0 deaths | 0/8 transfer, 0 deaths | 8/8 transfers, 0 deaths | D2 blocks useful **new** movement too |
| New east water, invisible lethal | 0/8 deaths, 0 transfers | 0/8 deaths, 0 transfers | **8/8 deaths** | D2 abstention prevents exposure without identifying lethality |
| Revisited north water, safe | 8/8 transfers, 0 deaths | 8/8 transfers, 0 deaths | 8/8 transfers, 0 deaths | First-person history supports revisiting in the tested stable environment |
| Revisited north water, invisibly changed lethal | **8/8 deaths** | **8/8 deaths** | **8/8 deaths** | **Stale, once-correct first-person evidence cannot certify future safety** |
| East berry, invisible lethal | **8/8 deaths** | **8/8 deaths** | **8/8 deaths** | Same preaction evidence does not disclose a hidden terminal hazard |

**Total physical deaths:** 56/144 = 24/48 per hidden east-berry stratum + 24/24 in changed visited-water stratum + 8/8 NO_D2 in new lethal east water, distributed across arms. Numerically 56 is an **outcome count**, not 56 demonstrably mistaken first-person hazard predictions. An informationally indistinguishable first exposure is not inferential incompetence. No survivor or postmortem data are smuggled into the next birth.

## Cost and exploration trade-off

The 8 `WATER_NEW_E_SAFE` FULL lives required **8,432 accepted UC**, including **728 D2 review UC**, to execute 96 steps collectively, with **0/8 useful transfers**. The corresponding `NO_D2` lives required **2,152 UC**, no D2 review cost, 96 steps, and **8/8 successful transfers**. The `WATER_NEW_E_LETHAL` FULL group used the same 8,432 UC and avoided eight deaths by abstaining, whereas `NO_D2` died after just 32 collective physical steps (848 UC): these different horizons are **not** fair equal-time efficiency comparisons.

In `WATER_VISIT_N_SAFE`, FULL consumed 5,744 UC (312 D2 review UC) for eight transfer successes versus 2,152 UC without D2 for the same eight transfer successes and same 96 steps. Thus the tested policy incurs a substantial **evaluation/abstention tax** that must be justified against physiological opportunity costs. It is incorrect to claim D2 detects a danger from an invisible label.

In local berries, FULL consumes 96 extra recall UC across eight lives. All three arms collect; no incremental collection or survival benefit is demonstrated from remembered score 0.45 versus baseline score 0.35.

## Combined-model limitation

All four models are **enabled at birth**, but active proposals are task-conditional: the factorized forecast and berry recall fire in food worlds; water learning and D2 fire in water worlds. These six dedicated physical strata **do not prove simultaneous multi-goal Competition** in one life. The earlier A2.35-B natural-alternatives experiment found 0/32 eligible genuine simultaneous competitions; this missing decision-opportunity evidence remains open.

Initial source and environment transitions in water transfer were externally scheduled and logged. They demonstrate **first-person learned response after relocation**, not self-chosen long-distance searching. Future genuinely autonomous mixed-need studies must not credit operator relocation as initiative.

## M11 and epistemic boundary

Two **distinct** integrated birth-enabled cold-restart software tests, both PASS in Python 3.11 and 3.12 on exact HEAD `048e4cb`:
- `tests/test_i1_a236_combined_m11_cold.py`: a genuinely closed berry-success episode and recalled source, five committed steps, then a cold restart; sixth journal head hash is identical to uninterrupted control. Changed predictor, recall, water and D2 flags/cost birth contracts refuse recovery.
- `tests/test_i1_a236_combined_m11_water.py`: actually admitted first-person water experience and D2 review, including a cold restart; sixth journal head hash matches uninterrupted life. Again this is narrow deterministic continuity, not a randomized crash-consistency certification for all fault boundaries.

The A2.36 `summary.json` field `m11_all_active_cold_recovery: PENDING` remains the honest *in-cohort* assessment, because M11 was tested by separate regression lives, not as a cold restart applied to each of the 144 test individuals. The **external integrated M11 regression gate** is PASS. These are distinct facts; do not post-hoc overwrite cohort outcome fields.

## Final scientific determination

- **Technical integrated I1 experiment:** PASS for the audited cohort and narrow M11 regression gates.
- **Positive collection-memory source → experimental option evidence:** SUPPORTED in eight full-model local-berry lives, with no proof of changed physical choice.
- **First-person water transfer in stable visited environment:** SUPPORTED in the tested visited-water worlds; novel-water transfer is blocked by D2.
- **Adaptive epistemic risk management under lethal changed or unseen worlds:** **SAFETY / GENERALIZATION NO-GO**.
- **General cognitive deployment and scientific Stage12 promotion:** **NO-GO**.
- **I0 canonical architecture and mortal physical laws:** unchanged. PR #227 stays Draft, **not merged**.

**Next preregistered experiment:** mixed water and berry needs within the *same* independent mortal I1 life, with natural goal competition, UC, first-person provenance and physiological cost. Then study personally learned nonlethal harm with discriminating cues, without installing an omniscient hidden-zone classifier.
