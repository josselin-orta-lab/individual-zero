# Repository governance and public security follow-up

**Status (2026-10-11):** `josselin-orta-lab/individual-zero` is **public**.
The GitHub repository ruleset [Protect main](https://github.com/josselin-orta-lab/individual-zero/rules/24874656) is active for `main`. Publication does **not** establish that the complete Git history, GitHub Actions logs, artifacts, or collaborator grants are free of risks.

- [Current access and merge policy](GITHUB_ACCESS_POLICY.md): verified settings, administrative bypass, current permission model and proposed future organization controls.
- [Post-publication security follow-up (français)](PUBLICATION_READINESS.fr.md): dated audit evidence, unresolved checks and commands for a private local secret scan.
- [Security reporting](../../SECURITY.md): how to report a vulnerability without opening a public issue.
- [Contributing](../../CONTRIBUTING.md): how visitors can propose changes without write access.

Visitors can read, fork and propose pull requests. Fork access does not grant upstream write or merge permission. Only explicitly granted repository roles can push upstream. The current `main` rule requires a PR for non-bypass actors, with **zero required approvals**; it is not a guarantee that only one specific person can merge if other users have `Write` access.

Do not describe the historical pre-publication checklist as completed. Do not post raw secret-scan reports, credentials, or sensitive historical logs into public issues, PRs, or CI artifacts.
