# P4 #990 proposed manual one-shot study workflow: EXECUTION BLOCKED

This branch preserves the **inert review template** `src/i2/docs/templates/i2-p4-990-manual-study.yml.example`, outside GitHub Actions execution paths, as a candidate which could *eventually* connect the previously reviewed single-use-claim helper to the frozen six-life runner. It is **not an executable GitHub Actions workflow**, has never been dispatched and must remain a **draft** until every acceptance gate below has been independently verified. The prior candidate under `.github/workflows/` was rejected by the repository's structural policy and has been removed, not whitelisted. Installing this template later would require a separate explicitly reviewed architectural decision, source-locked CI and custody plan.

## Pre-birth ordering

The operator must manually dispatch from `main` with the exact 40-character reviewed HEAD and `RUN-I2-P4-990-ONCE`. Only run number 1 / attempt 1 is admitted. GitHub Actions uses a serial concurrency group, exact SHA checkout with no persisted credentials, Python 3.11 and `-B` to avoid incidental Python bytecode in the research checkout.

Before **any** call to `NativePaidI2.create`, the workflow verifies the clean source and invokes `tools/i2_p4_990_one_shot_claim.py`, with **only that step** carrying its `GITHUB_TOKEN`. This helper requires the exact active ruleset id **26611746**, validates source identity and creates the fixed protected tag `refs/tags/i2-p4-990-single-use-spent` using one atomic GitHub API POST. An ambiguous result, second dispatch, retry, policy mismatch or moved source refuses. The marker is never deleted or reset as a retry mechanism. The proposed procedure is not proof against privileged future administration changes.

After an accepted claim, one operator-approved invocation of `tools/i2_p4_origin_failure_study_990.py` would run the **unchanged** preregistered six cells (3 arms × 2 worlds, up to 128 committed steps or death, no scripted motors or optimizations) and write original SQLite journals, cold-audited archive copies, signed readouts and receipt hashes to a new output directory outside the repository.

## Forensic custody and remaining STOP conditions

The inert template proposes creating an external custody directory **before** consuming the marker, records the reviewed SHA and an execution phase, then attempts a forensic SHA-256 inventory and `actions/upload-artifact@v4` with `if: always()` so ordinary command failures still upload original and **ABORTED partial** SQLite files. Artifact creation is *attempted* on failure, not guaranteed on host loss, cancellation or hard timeout. The requested 90-day retention is subject to organization/repository policy and does not satisfy independent immutable M11 custody. The proposed manifest hashes **relative paths from inside the evidence directory**, rejects symlinks and verifies every recorded hash before upload; after download, an operator can independently run `cd extracted-evidence && sha256sum --check SHA256SUMS.txt` without needing the original runner path. A static no-birth contract test checks this behavior. This is still not a demonstrated upload/retrieval rehearsal, and a missing upload or host failure remains a blocking risk. Manifest SHA-256 checks prove local consistency, not externally witnessed origin or anti-rollback.

**Do not approve a real dispatch until the following are verified:**

- [ ] Full source-locked Python 3.11 and 3.12 I2 safety CI passes for parent #996 and this exact workflow PR. No engine activation or cognition/physiology change.
- [ ] Stage the actual workflow and tag ruleset in a **separate test repository** using a distinct test marker, verifying token permissions and refusal of a second dispatch, repeat attempt, tag update and deletion. Never create/delete the actual production marker merely to test it.
- [ ] Independently review minimal workflow credential permissions. `contents: write` is currently needed to create the tag; this workflow's job token scope is wider than a tag-only token and is a residual security limitation.
- [ ] Rehearse failed and aborted artifact handling using **mock fixture files with NO native births**. Verify uploaded files and SHA-256 checks can be retrieved and read.
- [ ] Establish a **durable independent storage and export plan**, ideally with a streamed/checkpointed copy of source evidence robust to abrupt runner loss. `if: always()` and a 90-day GitHub artifact are insufficient to guarantee complete forensic retention under hard host failure.
- [ ] Independent reviewer approves one reviewed `main` SHA and execution ceremony after all gates, including preserving unfavorable/null outcomes, with no automatic retries or favorable-only repetition.

If any gate remains unsatisfied, **do not merge or dispatch this workflow**. A passed workflow *technical* status alone does not establish general autonomous adaptive survival, H3/G3 or M11. Original #985 six-life journals cannot be recreated by the new cohort.

Research issue: https://github.com/josselin-orta-lab/individual-zero/issues/990
