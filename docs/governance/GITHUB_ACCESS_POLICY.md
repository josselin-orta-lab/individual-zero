# Individual Zero: proposed GitHub access and merge policy

**State: PREPARED, NOT YET ENFORCED.** The canonical repository is currently private and user-owned. No organization, team permissions, transfer, public visibility change or branch rules have been applied by this document. The implementation specification remains `docs/architecture/reference/en/mvp-specification-v1.2.1.md`.

## Governance goal

Anyone may **read, clone, fork, open issues and submit pull requests** after a public release. A public GitHub repository cannot limit who may *propose* a PR from a fork. Access to push into the **canonical upstream repository** is granted only to named GitHub collaborators or members of explicitly authorized organization teams. Merging into protected `main` is reserved for the maintainer team, and must follow required review and validation.

Permissions on the canonical repository **do not control independent forks**. The Apache-2.0 software and CC-BY-4.0 research documentation licenses permit reuse subject to their terms. Protecting `main` protects the official project history; it does not prevent lawful forks or redistribution.

## Intended organization roles (create only after choosing the organization)

| Group | Suggested GitHub role | Allowed | Not allowed |
| --- | --- | --- | --- |
| Organization owners | Organization Owner | Account policy, security, recovery, assignment of roles | Routine bypass of protected-branch review |
| `i0-maintainers` | Write to repo, selected as the **only allowed pusher/merger to `main`** | Final merge after all checks; release management | Direct push without PR when PR is required |
| `i0-developers` | Write to repo | Push named feature branches; open and update PRs | Push or merge into protected `main` |
| `i0-reviewers` | Write to repo, **not** in the allow-to-push-`main` group | Independently review and approve changes; become additional CODEOWNERS if trusted | Merge or direct push to `main` |
| Public contributors | No upstream repository permission | Read, fork, open issues, propose PRs | Push to upstream; merge PRs |
| Observers | Public read; optional Triage | Follow science, report issues, handle triage if granted | Push code or merge |

Base organization repository permissions should be the least privilege needed. Audit existing direct collaborators and installed GitHub Apps after transfer, because team policy does not erase pre-existing write/admin grants. Require two-factor authentication and secure owners' recovery methods.

The current preliminary [CODEOWNERS](../../.github/CODEOWNERS) assigns all files to `@josselin-orta-lab`, including the CODEOWNERS file and sensitive areas. **Verify that the account remains a valid code owner with write access after transfer.** Once the real organization exists, consider additionally adding a trusted, write-enabled `@ORGANIZATION/i0-reviewers` team and ensure the team is visible. This is important: **a PR author cannot approve their own PR**. A sole code owner would otherwise block maintainer-authored PRs if code owner review becomes mandatory. The second reviewer may approve but must not receive permission to merge into `main`.

## Proposed branch protection: `main`

After the organization and appropriate plan/visibility exist, apply and **verify** a branch protection rule or ruleset to `main`:

1. Require a PR for every update to `main`; **one independent approval** minimum.
2. Require code owner review **only after at least two trustworthy eligible reviewers exist** so maintainer-authored PRs cannot deadlock.
3. Dismiss stale approvals when new code is pushed; require all conversations resolved.
4. Restrict who may push/merge to the matching branch to `i0-maintainers` (authorized person(s) only). The developer team should **not** be on that branch push allowlist.
5. Prohibit force pushes and branch deletion.
6. Apply restrictions to administrators and remove broad bypasses where available. If emergency bypass is unavoidable, record the person, reason and action.
7. Test both a developer account and a maintainer account: developer feature-branch push succeeds; developer direct push/`main` merge fails; maintainer direct push fails; a reviewed and approved maintainer merge succeeds; an owner-authored PR can obtain an independent approval.
8. Protect any long-lived integration branch (e.g. `i0/vnext-stages-10-12`) where appropriate, without preventing work on isolated feature branches.

**Workflow caveat:** today's `.github/workflows/ci.yml` uses `pull_request.paths` filters and conditional jobs. Do **not** make a job required until every PR in its scope always receives an appropriate terminal result; a docs-only change otherwise can be stuck waiting for an absent check. The current default workflow token has `contents: read`; keep the least privilege, do not run untrusted PR code under `pull_request_target` with secrets, and configure first-time external contributor workflow approvals.

**Capabilities caveat:** GitHub Free provides branch protections/rulesets on **public** repositories, but not on this current **private personal Free-plan** repository (GitHub API returned a feature/plan 403 for rulesets). A genuinely protected **private-to-public** transition without an unprotected public interval requires checking an appropriate paid plan and configuring enforcement *before* the visibility flip. With GitHub Free, keep this repository **private until the complete audit and organization preparation**; then schedule the visibility change and immediate protections as an explicit owner-controlled operation. Never claim that a committed CODEOWNERS file enforces the rules by itself.

## Research isolation and publication

- Historical Stage-9 scientific gate remains **NO-GO**. Reproducible development diagnostics are not independent held-out evaluations.
- Independent world/seed custody, plaintext preregistration secrets and bench-only oracle belong outside the developer-readable or future-public repository, including its Git history, PRs, Issues, Actions logs and forks.
- No secret, private metadata, historical Actions log or unsupported dependency may be declared safe merely because the current working tree does not expose it.

## Steps requiring owner action

1. Complete [pre-publication readiness review](PUBLICATION_READINESS.fr.md), including full reachable-history and CI-log scanning and any remediation.
2. Create a GitHub organization under the chosen name; keep I0 **private**. Confirm account/organization 2FA and repository default role settings.
3. Review transfer consequences, including the possible permanent retirement of the original owner/repo name after heavy recent Actions usage: [GitHub transfer rules](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository). Existing GitHub links/DOIs should be inventoried.
4. Transfer only after the owner intentionally confirms the target organization and repository; audit transferred direct collaborators and GitHub Apps.
5. Create the actual teams, add only the named people, validate their permissions, then update CODEOWNERS to eligible users/teams.
6. Enforce and test protection on the target branch using GitHub UI or an admin-authorized tool. This GitHub integration **does not expose administrative ruleset/permission writes**, so configuration requires an organization owner.
7. **Only after a separate explicit human GO**, consider public visibility. Confirm post-publication security and permission audits.

This policy defines the intended model. It does **not** change current repository visibility or security settings.
