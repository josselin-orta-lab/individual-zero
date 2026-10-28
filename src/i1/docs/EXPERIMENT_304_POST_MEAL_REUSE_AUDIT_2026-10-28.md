# I1 #304/#305 - Post-meal natural reuse, bounded M11 audit (2026-10-28)

**Base SHA**: `1747fa7988afaaa2e67a7dccc3610cdfeda84472`. **Research type**: operator-only retrospective trace analysis of the already preregistered, fixed 18-step Oasis B natural pair. No extended birth, no changed motor command, no altered TD, reward, Competition, P-40, UC, physics, I0, or I1 engine. This is **not** a new independent experiment.

## Falsifiable question

At Oasis B step 11, canonical I1 applied `manger berry_a` while its Stage8 `i1:affordance:manger:target=berry_a` value was `unlearned`; the action won because a personally learned negative `primitive:dormir` value reduced sleep's Competition evidence (PR #596). Does the subsequent genuine eating consequence become an **owned TD update**, and is a later physically offered, paid food-related signature **read and reused** within the original life horizon?

## Locked source and endpoints

Use exact unchanged `tests/i1/test_i1_natural_q_stage8_holdout_304.py` birth and physical path: preset Oasis, identity b, 18 steps, two independent M11 SQLite ledgers (canonical vs research Stage8-only-Q-masked). Audit only the existing **canonical** branch from immediately after the first `manger` command to the original last committed step. Preserve all negative, censored and dead outcomes.

Capture in chronological order, using real committed causal journal rows:
1. Actual `command_experienced` eating step and subsequent physical food, water, energy and integrity changes, without assuming the gain was known before action.
2. Genuine later `td_update_published` rows with `previous_signature`, `next_signature`, `return_g`, `delta`, `updated_signatures`. Distinguish TD publication time from the step to which a reward is attributed.
3. Actual subsequent `stage8_option_evaluation` for `manger`, `collecter` and other available contenders with learned status, signature, Q and evidence; corresponding `competition_cycle` ratios and admission/actual commands when applicable.
4. First later independently paid **new** local `collecter` or `manger` proposal/offer, if any. Do not assume that inventory or world physics made a second opportunity available. Distinguish `NOT_EXPOSED` from `LEARNED_BUT_NOT_READ`, `READ_BUT_NOT_ADMITTED`, `APPLIED_NO_BENEFIT`, `IMMEDIATE_REUSE_OBSERVED`.
5. Verify M11 generation, no postmortem continuation, identity, physics digest, source integrity and owner charges already required by #595/#596.

The report must explicitly include actual later applied command sequence and candidate evidence; it must not claim semantic utility from learned Q alone or from a counterfactual after bodies diverge.

## Predefined verdicts

- `NOT_EXPOSED`: no later food-related opportunity becomes naturally available.
- `TD_PUBLICATION_NOT_OBSERVED`: the necessary personal TD consequence is absent in the fixed window.
- `LEARNED_BUT_NOT_READ`: relevant TD weight exists but no later paid read.
- `READ_BUT_NOT_ADMITTED`: actual learned read reaches Competition but cannot be linked to a later physical act.
- `APPLIED_NO_BENEFIT`: a later food-related action physically applies without an observed relevant nutritional improvement.
- `IMMEDIATE_REUSE_OBSERVED`: later learned read, real freely applied food-related action and real physiological benefit; **still not automatically a causal isolated, durable or robust adaptive GO**.
- `SCIENTIFICALLY_INCONCLUSIVE` for competing signatures, already diverged bodies or ambiguous ownership.

Record the first missing transition, do not alter any thresholds to obtain a positive. The original fixed 18 steps, two environments and identity cohorts stay unchanged. A prospective selective read ablation may be planned in a separate issue/PR only if this diagnostic reveals a genuine later exposure.

## Integration

Documentation + read-only observer instrumentation only, no cognitive engine changes. Enforce 4/4 exact-head CI Python 3.11/3.12 and inspect the emitted canonical M11 report before merge, respecting #348. This report does not increase the global gate of `engine.json`.
