# Issue #317: certified completed multi-hop returns after sleep

**Read-only verifier added in commit `2d4a6378`; falsification test `0df2e7d3`.** No change to cognition, physics, I0, the main control, or witness PR #316.

## Why previous reports falsely said 0

The existing `physically_arrived_from_outside_current_perception` metric tests whether the destination was *outside the latest capture at the instant of arrival*. A genuine route becomes visible on its last hop. Therefore this is an inappropriate test of initial unseen long-distance arrival; it is not evidence that physical multi-step returns never happened.

The new metric `completed_remote_multihop_returns` starts with an independently physically certified memory hop aimed at a destination outside the **starting** Perception, then requires a same-entity, same-target final memory hop. Each world-step from the first hop to arrival must have exactly one Action Control command, actual World & Body transition, matching admission hash and scheduler closure. Every intervening stationary action must preserve position; a contradictory sighting, any unexplained movement, a different entity, missing continued option link, uncommitted transition, ambiguous attempt, or bad position cancels certification. The previous motor ref must have an actual Stage11 `i1_place_memory_intention_continued` to the next option at the immediate following world step, with independently observed current position. A reselected motor option still requires its own Competition passage and Action Control physical application. The verifier cannot influence I1.

## Physical witness in existing authenticated WAL

`memory-corridor / 1142`, SHA `eef98704569e44e0c026aebbeeb2eae2396911d8`, GitHub Actions [run #39170762411](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39170762411), original archive `i1-317-corridor-1142` (not rewritten).

- World step 71: from (11,8), select a remembered wood at (9,8) **outside current Perception**; applied memory move to (10,8) with proper Action Control admission and committed WAL. Step 72 publishes the one-hop continuation toward (9,8), but legitimate sleep wins, executing 72–77 while position remains (10,8). At step 78, the same wood's remembered new one-hop option is selected after Stage8 (learned TD available), applied, and physically reaches (9,8). This constitutes **one completed remote multi-hop return with sleep** under the new metric.
- World step 79: from (9,8), remembered stone at (11,8) is invisible; I1 moves to (10,8), sleeps at step 80 and subsequent sleeping steps, then reaches (11,8) with another selected memory action at step 86.
- World step 87: from (11,8), another first-person return toward wood at (9,8), the first hop reaches (10,8), and the next step 88 selects a new memory option and physically reaches (9,8).

These examples demonstrate the *capability* in one individual on one intentionally simple world. They do not demonstrate that wood or stone is useful, population survival benefit, efficient non-oscillatory travel, or a generalized distant navigation policy. TD reuse is an observed input to subsequent deliberation, not an externally validated reward for resources.

## Required scientific gate

Run the new verifier in CI against original, sealed WAL. Test strict false-positive rejection and compare the corridor and paired held-out worlds. Track sleep, vital urgency, UC, oscillations, M11 cold replay. Do not automatically merge draft PR #318 or close issue #317 until software CI and independent physical comparisons pass. Scientific verdict remains **NO-GO globally**, even if the first three physically verified examples qualify as a bounded cognitive success.
