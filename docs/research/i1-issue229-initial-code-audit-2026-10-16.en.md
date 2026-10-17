# Issue #229: initial causal code audit (development, not confirmatory science)

Date: 2026-10-16. Baseline `main`: `bf59eceaf97805f04a18b0b28f1396f2e98bfa89`. Inspected frozen A2.39 implementation: `af5006612b45b46d5ee2b2ed9e97b9cf6e104167` (PR #228). This branch starts from the latter because the A2.39 live I1 integrations are not yet merged into main. I0, WorldBody, v1.3.3 and A2.38/A2.39 artifacts remain unchanged.

## Verified code-level mechanism, not yet a complete born-life causal proof

1. `src/i1/modules/stage6_planning.py:206-230` does enumerate `manger` from perceived berry inventory, independently of a successful transition forecast. This establishes the affordance, **not** production of an actionable OptionProposal.
2. `stage6_planning.py:283-327` can only traverse edges for which the exact equipment simulator returns complete predicted transitions; `search` skips unavailable edges. The current full-state exact table has no general ingestion fallback. Every initial candidate must therefore be checked against exact model coverage before assuming planning can return it.
3. `src/i1_overlays/i1_active_runtime.py:236-264` handles an unsolved eat goal with a two-branch fallback: B collection when local, otherwise movement east to a visible B site. When the body already carries B berries but none is locally collectable and none is east, this fallback returns `None`. When local berries remain, it proposes `collecter` again, never `manger`.
4. `i1_active_runtime.py:275-303` applies the external factorized model, whose only action families are MOVE_E and COLLECT_B. This is an instrumental proposal, not personally learned food knowledge; unseen eating cannot be represented by that external forecast.
5. `src/lab/world.py:891-908, 972-995, 1056-1064`: continuous food/water decay each physical step, real berry ingestion decrements inventory and updates food/integrity; lethal reasons are lethal_zone and zero_integrity, not zero_food or zero_water. Physiology is unchanged.

Thus the earliest **demonstrated code-level bottleneck** lies between enumerated affordance and an executable prediction-backed/fallback proposal. Stage9 has not been shown to reject a genuinely generated `manger` proposal. This is a qualified mechanistic diagnosis, **not** yet complete per-life proof or exclusive attribution.

## Independent diagnostic awaiting execution

`scripts/diagnose_i1_issue229.py` runs a newly born autonomous I1 baseline, records each decision step (candidate commands, inferred proposal traces, selected/executed command, UC and physical receipts), and separately runs technician-only WorldBody physical controls (empty inventory, B consumption, A toxicity). The direct primitive tests are **not** autonomous behavior. Neither the script's existence nor code review is an executed experiment.

## Correction direction (not yet validated)

A prospective I1-only model may separate action availability from outcome prediction, allowing a bounded, paid, uncertainty-marked one-step **candidate** for an inventory-grounded `manger` without pretending to know its food or toxic effect, and pass it through Competition, Stage9 and Action Control. No forced action, effect prior, free UC or safety override. Such change needs a new versioned birth contract, tests, a preregistered matched cohort and independent audit; draft PR #239 should be reviewed first.

Historical A2.38/A2.39 GO/NO-GO statuses are unchanged. Issue #229 remains NO-GO until actual physical first-person evidence and nonregression exist.
