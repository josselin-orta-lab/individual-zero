# Security Policy

Individual Zero is a research project. Security and capability concerns should be treated as part of the research process.

## Reporting

Do not open a public Issue for leaked credentials, vulnerabilities that could compromise contributors or infrastructure, or findings whose immediate publication could create avoidable concrete risk.

Use GitHub private vulnerability reporting when available. Otherwise contact the repository maintainer privately through GitHub before publishing technical details.

A cognitive-behavior finding is not automatically a software vulnerability, but may still deserve restricted discussion if it reveals a concrete safety risk.

## Secrets

Never commit API keys, passwords, private tokens, credentials, or private datasets.

If a secret is committed, treat it as compromised even if later removed from visible history. Revoke or rotate it immediately.
