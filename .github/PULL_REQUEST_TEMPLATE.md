## Summary

Explain the change, why it is needed, and the affected I0 modules or research artifacts.

## Contribution type

- [ ] Documentation / maintenance only
- [ ] Bug fix with expected equivalent cognitive behavior
- [ ] Cognitive behavior change (link an EXP or documented diagnostic)
- [ ] Architecture / contract change (link the normative section and decision)

## Verification performed

Record the **exact** local commands run, results, and complete Git commit SHA. If a check was not run, explain why.

## Scientific and security boundaries

- [ ] No credentials, private keys, secrets, personal data or confidential materials are included, including in fixtures or logs.
- [ ] No concealed held-out seeds, world files, or oracle information are published to developer-accessible code or CI.
- [ ] No scientific gate, INV-25 acceptance or Golden is claimed from unit tests or development fixtures.
- [ ] Changes respect `docs/architecture/reference/en/mvp-specification-v1.2.1.md` (do not edit this normative source).
- [ ] Source/protocol/environment versions and any behavior changes are traceable.
- [ ] PR does not introduce untrusted-code execution with elevated permissions or expose Actions secrets.

## Review

- Link the issue / EXP / ADR if applicable.
- Identify the reviewers needed for safety, architecture, science or compatibility.
- External PRs are proposals only: approval and merge privileges remain with authorized maintainers.
