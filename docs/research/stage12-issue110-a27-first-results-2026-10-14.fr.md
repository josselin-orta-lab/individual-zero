# Individual Zero #110, A2.7 : results of opt-in physical-capture partial-plan revalidation

**14 October 2026. Science checkpoint: PARTIAL.** Protocol frozen before code at `88c2b6a55391b901d8ae4f2e6ddfbefed16df82a`. Source of the first full completed Python 3.12 run: `a55f3b58a4768c679dde6c376d2e763590ebc99c`, [Actions #38592790611](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38592790611). This text reports the **completed Python 3.12 matrix** only; Python 3.11 is a separate pending confirmation at the time of this first checkpoint. Original red smoke #38592615643 is retained: it failed only because a test attempted to instantiate a mortal individual without the mandatory WAL, while its integrated actual-life revalidation test passed on both interpreters; the test was corrected to provide exclusive WAL, **not by relaxing the safety contract**.

## Design and observed output

16 separately born physical lives ×42 actual steps = **672 unique world steps**: `restored`/`sustained` × `free`/`A2` × instrumental P-48 `OFF/ON` × fresh capture revalidation `OFF/ON`. Control is the preexisting planner; treatment is opt-in `progressive_revalidate_on_new_capture=True`, default False. The condition, birth ID and hashes for every life are in the artifact `stage12-a27-py3.12`. All original WAL, causal chain, Goal Progress, First Person Agency, pair consumption, A2 and physical food/P-48 auditors passed with **0 exceptions and 0 audit failures**. None of the 16 lives can evaluate `attribution_bias` with the unmodified `2 success + 2 failure / window 12` policy.

| Profile | World | Instrumental | Fresh-capture invalidations OFF / ON | Sites physically visited OFF / ON | Real meals OFF / ON | Steps with net food increases OFF / ON |
| --- | --- | --- | --- | --- | --- | --- |
| restored | free | OFF | 0 / 0 | 31 / 31 | 1 / 1 | 1 / 1 |
| restored | free | ON | 0 / 0 | 31 / 31 | 1 / 1 | 1 / 1 |
| restored | A2 | OFF | 0 / 0 | 28 / 28 | 1 / 1 | 1 / 1 |
| restored | A2 | ON | 0 / 0 | 28 / 28 | 1 / 1 | 1 / 1 |
| sustained | free | OFF | 0 / 2 | 33 / 33 | **0 / 0** | **0 / 0** |
| sustained | free | ON | 0 / 2 | 33 / 33 | **0 / 0** | **0 / 0** |
| sustained | A2 | OFF | 0 / 0 | 32 / 32 | **0 / 0** | **0 / 0** |
| sustained | A2 | ON | 0 / 0 | 32 / 32 | **0 / 0** | **0 / 0** |

**T1 PASS (Python 3.12), T2 PASS locally, C4 FAIL on the incremental food-gain hypothesis.** Fresh revalidation fires twice in each of the two `sustained/free` treatment lives and never in any control. The first fresh plan from a new capture is explicitly searched instead of `reused_cached` in the actual 4-step short smoke. There are no fabricated progress receipts. However all physical outcomes and counts of sites/meals are unchanged: *fixing this cache is insufficient to make food-acquisition options win Competition.* The result is NOT a scientific proof of better agency, feeding, or useful exploration.

The A2 obstacle conditions do not exhibit this particular stale-cached partial segment, so the absence of invalidation there is not a failed intervention. A2 prior cause/agency audits remain independently valid.

## Mechanism isolated and remaining causal ambiguity

The fix lives in opt-in Stage6 Planning: a progressive `step_completed` option may be reused within one world step, but when an entirely new world step is perceived the old unexecuted segment is invalidated using the original `expires_at_step - option_ttl_steps` identity. The old candidate is cleared from Competition, Action Control and Planning before the already UC-charged new search. No separate cognitive belief, oracle data, proxy food score or new agency judgment was created. The non-opt-in historical path is not modified; completed goal plans retain their original engagement and revision rules.

**Remaining problem:** a fresh partial plan is still not rated sufficiently highly against novelty-linked autonomous exploration in the `sustained` case. The prior A2.6 600-step experiment independently established 0 meals/food=0 after 600 and no comparative physical P-48 change; A2.7's 42-step pilot does not resolve that. P-15 reduction to 0.35/0 was already disproven in earlier ablation and must not be repeated opportunistically. A next preregistration should isolate *actual prospective value of sequences leading to an edible resource* and opportunity cost versus novelty, with a test that permits failure and no forced actions.

## Verdicts, scope and next step

C1 subjective agency **PARTIAL**; C2 causal separation **PARTIAL**; C3 physical-diversity preservation **PASS for eight 42-step pairs only**, not exploration usefulness; C4 actual food completion **PARTIAL overall**, but **FAIL** of the new treatment's improvement hypothesis; C5 P-48 discrimination **PARTIAL**; C6 long-horizon stability for *this specific change* **INCONCLUSIVE**; C7 reproducibility **PARTIAL pending cross-Python repeat and true diverse seeds**; C8 technical conformity **PASS in the validated scope**. **Global PARTIAL**. No modification of MVP v1.3.1, Stage9, Oracle/Bench access boundaries, attribution thresholds, sleep or P-15. Do not declare Stage12 complete or close #110; operator acceptance remains outstanding.

**Follow-up:** confirm 3.11 on the same commit, inspect integration regression and negative test suite; if those pass, treat the isolated stale-plan revalidation as a software improvement (off by default), and open separately a scientifically preregistered competition-value intervention. Do **not** run long-life A2.7 as a success narrative when the initial effect is null; any 600-step extension must be justified by a distinct long-term concern.
