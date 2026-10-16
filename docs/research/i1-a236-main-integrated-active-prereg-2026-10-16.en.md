# A2.36 preregistration: all I1 experimental models active after integration into main

**Date:** 2026-10-16. **Registration precedes the A2.36 heldout runner and physical cohort.**
**Source baseline:** `main` at `bf59eceaf97805f04a18b0b28f1396f2e98bfa89`, integrated by PR #226 on 2026-10-16. This is **not** the former #219/#222 development branch. PR #226 staged I1, D0/D1/D2, the A2.35 recalled-collection mechanism and their old negative findings into the same main tree. The main integration is technical and default OFF, not scientific GO. **Only new I1 mortal births explicitly enable all experimental models; I0 never does.**

## Question

When I1's external partial visible-delta model (Stage 6), **first-person water learning** (D1), **UC-priced risk-of-new-movement review** (D2), and **episodic source-backed berry collection review** (A2.35) are all activated together on the current main code, do (a) their evidence origins remain properly separated, (b) their interventions continue to behave when water/food goals switch, (c) no unearned safety or terminal claims emerge, (d) no death/UC/journal/M11 regression occur? Do **not** treat technical successes, movement abstention, or observations after death as learned hazard classification.

## Frozen cohort before seeing A2.36 outcomes

**Six strata, eight scenario indices each, three new independent I1 mortal births per scenario: 48 triplets / 144 births.** All are actual `I1WaterPrudentRuntime` + Stage12 + WorldBody lives with a unique `i1:a236:<stratum>:<index>:<arm>` identity, independent physical/Memory/causal owners and immutable per-life WAL. At most **12 physical commands per birth**, truncate at death, exception or nonapplied step. Arms in alternating order by index; no same-life reset, shared episodes, injected memories, UI shortcuts or Oracle read in cognition.

**All three arms have these explicitly birth-enabled flags:** `i1_model_enabled=True` with a physically trained frozen 16-example external-laboratory prior, `i1_water_probe_enabled=True`, `i1_water_learning_enabled=True`, forecast charge 2 UC, D1 consider/acquire each 2 UC and mortal+I1 identity. The three arms are:
- `FULL`: `i1_lived_recall_enabled=True`, recall review 1 UC; `i1_d2_prudence=True`, D2 review 1 UC. Thus all four models enabled.
- `NO_RECALL`: same but `i1_lived_recall_enabled=False`, `i1_d2_prudence=True`. This is a targeted memory-consumer ablation with I1's other active models intact.
- `NO_D2`: same but `i1_lived_recall_enabled=True`, `i1_d2_prudence=False`. This isolates conservative movement commitment while retaining learned water and the food/recall models.

**Strata and physics:**
- `BERRY_LOCAL`: B at the *current* initial cell (quantity `16 + i%3`); food `10+i`, water `95`. Real berries, not fed by operator to memory. No lethal zone. Tests whether the active Stage 6 and episodic recall still contribute in the joint D1/D2 runtime.
- `WATER_NEW_E_SAFE`: newborn starts at a known local-water source north of the original origin, then external scenario at world-step 4 changes position to an unvisited position `(12+i,12)` with adjacent east source and no hazard. Food `80`, water `1+i%3`; no B. This measures valuable but unvisited exploration cost.
- `WATER_NEW_E_LETHAL`: like WATER_NEW_E_SAFE but east source also has **invisible lethal hazard**. Physically same preaction view as safe arm, but independently scored.
- `WATER_VISIT_N_SAFE`: external relocation at step 4 to original origin with a previously visited north water source, no hazard.
- `WATER_VISIT_N_CHANGED_LETHAL`: identical to WATER_VISIT_N_SAFE except a logged external `set_lethal_zone` at physical step 4 makes the previously safe/visited north target lethal without an observable precursor.
- `BERRY_EAST_HIDDEN_LETHAL`: B east and an invisible lethal zone east, no water source, food `10+i`, water `95`; first action can be a genuinely sensory-indistinguishable lethal attempt, scored as an information limit.

For water strata use already-merged D2's otherwise unchanged Stage11 geographic development flag, Stage9 and Stage12 configuration and water-needs/water-plan setpoints = 95, standard immutable WorldBody. For berry strata the same config and Stage11 geography **disabled** to retain comparable food opportunity. World initial energy `65+i%2`, integrity 100. Use unchanged D2 zero-consolidation-weight *scientific fixture* in all arms, not a product recommendation. These are fixture settings, not calibration or production defaults.

**Frozen prior:** before constructing any heldout lives, execute 8 real WorldBody east-move and 8 real local-B collect transitions in separate physical laboratory worlds, construct `EquipmentCorpus`, fit `fit_external_lab_shadow`, verify source `corpus_sha256` and counts (8,8). The prior must remain `source_scope=external_lab`, and is never counted as I1's own lived memory. Prohibit any fitting/reward update based on A2.31–A2.35 or A2.36 test lives.

## Pre-registered outcomes and decision criteria

Every stratum has **8 triplets as the fixed denominator**, even when no act is executed or an individual dies. Report physically applied commands, source IDs, capture timing, water improvement, previously learned return, model proposals, recall-credited evidence, D2 abstentions, UC and terminality separately. Archive external score facts apart from journal/first-person data.

**Integrity hard gate (ALL 144 lives):** 0 invalid in-memory/hash-chained WALs, 0 malformed independent audit, 0 actor after death, 0 double physical action, 0 non-first-person lived evidence admitted, 0 hidden hazard/certified-safety/unearned distal-agent claim. Any occurrence is **HARD NO-GO** with raw evidence. Confirm distinct birth IDs and model/owner provenance on every life. All 144 records must remain, including truncated lives.

**Mechanism checks (distinct from science GO):**
1. `BERRY_LOCAL`: among the 8 FULL and 8 NO_D2 lives, at least 6 each must have an actual `collecter` success followed by earlier closed episode, admitted recall in subsequent `S_t` and source-backed score `0.45`. NO_RECALL may collect but must have **0** A2.35 review charge and **0** score 0.45. Anything else means joint-model recall integration NOT DEMONSTRATED.
2. Water strata: >=6/8 NO_D2 new-safe worlds must actually use the lived-water-origin movement and physically succeed in later drinking, and >=6/8 FULL previously visited safe-world returns must do so, or classify `NOT DEMONSTRATED`; do not assume exact historical D2 baseline reproduced in the stacked model.
3. `WATER_NEW_E_LETHAL`: if NO_D2 acts and dies in an unobservable hidden hazard, that is a cost of exploration, **not a prediction-error tally**. FULL movement abstention is an opportunity/survival tradeoff, not proof danger was detected. `WATER_VISIT_N_CHANGED_LETHAL` is a stale-visit epistemic counterexample; any revisit death in FULL is reported as safety NO-GO, not excused by earlier visits.
4. `BERRY_EAST_HIDDEN_LETHAL`: deaths from identical first-person views are not blamed as perceptual ignorance; compare first-authorized captures and model-output certainty across arms. Do not infer transfer from one dead life to another.
5. Costs: sum admitted/refused actual UC per operation, compare FULL, NO_RECALL and NO_D2 per stratum and number of actual steps; never compare aggregate cost without disclosing survival/step differences. Baseline no-recall has 0 positive A2.35 review charges; baseline no-D2 0 positive D2 review charges.
6. M11: demonstrate same-life birth contract separation and no silent activation; PR #222's earlier cold M11 after five recalled collections had a byte-identical sixth journal step. A2.36's combined FULL class must have an independent fresh cold-recovery check with the water owner and D2 toggle; otherwise mark integrated M11 recovery **PENDING**.

**Verdicts:** `INTEGRATION_TECHNICAL_PASS/FAIL`, `BERRY_RECALL_SUPPORTED/NOT_DEMONSTRATED`, `WATER_TRANSFER_SUPPORTED/NOT_DEMONSTRATED`, `EPISTEMIC_RISK_NO_GO`, `M11_PENDING/PASS/FAIL`. Never upgrade to scientific deployment GO from these matched deterministic cohorts. Future scientifically confirmatory work requires independent operator archive audit, a new prospective natural-option competition cohort (A2.35-B reported 0/32 genuine contests), full UC/survival and uncertainty tests, and a solution to nonperceptible changing danger that does **not** grant omniscience.

## Reproducibility

Run under Python 3.11 and 3.12 on the identical frozen physical cohort. These are **software repeats**, not independent scientific replications. Save each life journal/WAL/canonical export, exact Git HEAD, sealed external training digest and individual records JSONL. Predeclare deviations explicitly if fixtures/runner need repairs; never retune thresholds after observing heldout outcomes. The scientific release gate stays **NO-GO**.
