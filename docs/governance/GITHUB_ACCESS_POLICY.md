# Individual Zero: GitHub access and merge policy

**Observed 2026-10-11: PUBLIC repository, protected `main`.** Canonical repository: [josselin-orta-lab/individual-zero](https://github.com/josselin-orta-lab/individual-zero), owned by a personal GitHub account. This document describes **current enforcement**, then future options. The implementation source of truth remains `docs/architecture/reference/en/mvp-specification-v1.2.1.md`.

## Current enforced settings (GitHub API inspection)

- [Ruleset 24874656: Protect main](https://github.com/josselin-orta-lab/individual-zero/rules/24874656): `enforcement=active`, target `refs/heads/main`.
- Rules: prevent deletion and non-fast-forward pushes; require a pull request before merging for actors without bypass.
- PR configuration: **0 required approvals**, no required code owner review, no required resolution of review threads, allowed PR merge method **squash** only.
- Bypass: `RepositoryRole` actor 5 (repository administrators), `always`. **All repository administrators**, not just the repository owner, can bypass.
- `main` reports `protected=true`. Other existing branches, including `i0/vnext-stages-10-12`, are **not protected by this ruleset**.
- Repository merge settings permit squash; merge commits and rebase merge are disabled.
- `CODEOWNERS` names `@josselin-orta-lab`, but **does not itself enforce approvals**.

These settings protect `main` against ordinary direct pushes and destructive updates. They **do not** ensure that only the owner can merge a PR: someone with repository write/merge permission can generally merge without an approving review, provided the configured rules are met. An administrator can bypass the ruleset. **Audit collaborator and app permissions in GitHub Settings; this connector cannot enumerate them.**

## Public contribution model

Anyone can read, clone, fork, open issues and submit PRs from a fork. Forks and PRs do **not** grant upstream write access. Only accounts explicitly given `Write`, `Maintain` or `Admin` permissions (or an authorized app) can modify eligible upstream branches. Users with `Write` can ordinarily push to **unprotected** branches even if they were created by someone else. Protect long-lived working branches separately if that is undesirable.

Canonical code is Apache-2.0 and documentation/research material is CC-BY-4.0 unless otherwise identified. These licenses permit reuse subject to their terms, including public forks; protecting the canonical branch cannot prohibit independent forks.

## Pending permission checks (owner action)

1. [Settings → Collaborators](https://github.com/josselin-orta-lab/individual-zero/settings/access): review every named person, pending invitation, role and external GitHub App with repository access. Remove unintended write/admin access. Confirm whether the owner is the sole administrator.
2. [Rulesets](https://github.com/josselin-orta-lab/individual-zero/settings/rules): confirm current ruleset enforcement after future changes. The Admin bypass is intentionally allowed by the owner but must not be described as a user-specific exception.
3. [Actions settings](https://github.com/josselin-orta-lab/individual-zero/settings/actions): confirm default workflow-token permissions are restrictive, fork PR approval policy is suitable, and untrusted PRs cannot obtain repository secrets.
4. Confirm repository owner 2FA/recovery and review third-party GitHub Apps.
5. If independent review becomes required, appoint eligible reviewers before increasing the approval count; an author cannot approve their own PR.

## Future organization model (not configured)

If the repository is transferred to an organization, assign narrowly scoped access to named maintainer, developer and reviewer teams. Ensure only intended maintainers can merge to `main` by testing actual permissions and branch rules. A `Write` role alone may be too broad for a developer intended to push feature branches but never merge to `main`. Do not claim organization teams or branch push restrictions exist until GitHub confirms their enforcement.

## Scientific and security boundaries

- Stage 9 historical scientific assessment remains **NO-GO**, independently of repository access status.
- Held-out worlds/seeds, bench-only oracle data, private datasets, credentials and preregistration secrets must not enter public source, commit history, PRs, issues, Actions logs or artifacts.
- Current public visibility is **not** proof that these historical surfaces have passed a complete audit. See [post-publication security follow-up](PUBLICATION_READINESS.fr.md).
