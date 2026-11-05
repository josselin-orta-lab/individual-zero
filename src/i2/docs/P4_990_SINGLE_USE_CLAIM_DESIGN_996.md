# I2 P4 #990: single-use remote claim design, NOT wired to a birth workflow

This branch is an isolated proposal for the *operational* blocker in preregistered research issue [#990](https://github.com/josselin-orta-lab/individual-zero/issues/990). It adds no I2 cognition, body, motor policy, birth flags or new scientific cohort. No experiment has been launched.

## Proposed claim protocol (offline/testable)

\`tools/i2_p4_990_one_shot_claim.py\` is **not called** from any workflow or research runner. It is a fail-closed prototype for a future independently reviewed manual-execution ceremony:

1. Require exact first \`workflow_dispatch\` on current \`main\`, reviewed full 40-character SHA, explicitly typed confirmation, the approved workflow ref, and GitHub run number/attempt **1**.
2. Check the live \`main\` ref matches the approved SHA, then issue an **atomic GitHub \`POST /git/refs\`** to reserve fixed ref \`refs/tags/i2-p4-990-single-use-spent\` *before any birth*.
3. Accept exactly HTTP 201 with matching ref/source as the only successful claim. A duplicate ref, retry attempt, moved main, timeout, unauthorized context, strange API response or ambiguous network failure must **refuse**, never automatically retry.
4. Return only a diagnostic receipt, explicitly marked \`NOT_EXECUTED_BY_THIS_GUARD\` and \`m11_authenticated=false\`. Never print GitHub tokens or call the native I2 runner.

\`tests/i2/test_i2_p4_990_one_shot_claim_996.py\` uses a synthetic in-memory REST responder; tests first claim, repeated claim, run-number/attempt rejection, incorrect workflow context, missing token, changed source, HTTP 422/503 and ambiguous POST. These tests do **not** birth any I2 identity or call the real GitHub API.

## Additional fail-closed tag protection checks (#997)

The claim helper now refuses **before POST** unless the operator supplies a reviewed numeric `I2_P4_990_TAG_RULESET_ID` and the live GitHub detail endpoint confirms an **active repository tag ruleset**, with exactly `refs/tags/i2-p4-990-single-use-spent` as its sole include, no exclusions, both `deletion` and `update` protections, and **zero bypass actors**. A second live check **after** successful marker creation refuses if protection disappears. These checks run before births and are fail-closed on unavailable/malformed rulesets, but are **not atomic with rule administration**. The ruleset can be changed after the check by an administrator; this tool does not establish external immutability or M11.

The repository currently only exposes an active **branch** ruleset for `main`, so the helper is expected to REFUSE. This child change is still design-only and is not wired to any runnable workflow. Never install a permissive tag ruleset just to force the check to PASS. Administrators must review whether a no-bypass tag ruleset is operationally enforceable and whether this token can create the initial tag under it. Validate with harmless mock markers and real repository policy inspection, without creating any I2 life.

## Critical open security and science gates

**The fixed Git tag is not unforgeable or immutable by itself.** A repository administrator or token with tag deletion privileges can delete the ref and allow a later claim. A GitHub repository **ruleset preventing delete/update of the spent tag**, with independently reviewed bypass permissions, must exist *before* enabling the birth workflow. The workflow also requires a dedicated minimal-permission token capable of creating exactly that marker, while restricting source and artifact access. This repo-credential/ruleset configuration is **not implemented by this PR**. An actual workflow must not be added/merged/dispatchable until reviewed protections are in place.

The marker provides an atomic mutex/once-only reservation, **not an exactly-once scientific result**. If the API POST succeeded but its acknowledgment was lost, the cohort must remain unexecuted or be treated as an aborted, consumed attempt. A failed or canceled study does not authorize retry. GitHub Actions artifacts are time-limited; independently retaining complete original SQLite files, hashes, signed readouts, outcomes and any partial/aborted data needs separate operator-verified storage. The study remains explicitly manual. Do not promote \`m11_authenticated\`, adaptation, or survival to established.

**Execution preconditions before any real birth:** existing full exact-head native CI must pass on the final reviewed source; test Git ruleset against harmless duplicate tag claims, retries and malicious deletion attempt (not native births); review artifact-collection on failure with mock fixtures; approve one source SHA, verify clean tree and single use, manually execute only once; record all adverse and null results.

This documentation does not grant approval for a run and does not change the previously frozen 3 arms × 2 worlds × 128-step #990 protocol. The currently isolated older candidate manual workflow remains **unsafe and unused**.
