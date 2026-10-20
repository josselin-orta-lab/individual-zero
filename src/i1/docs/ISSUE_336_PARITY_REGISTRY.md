# #336: exact per-issue attestations for dormant I1 experiments

The old inline `_approved_experimental_326/327/328/329` functions in
`scripts/test_i1_artifact_parity.py` are replaced with exact source-pin
manifests in `config/i1-isolated-source-pins/issue-<number>.json`.

One manifest corresponds to **one reviewed native Python module** and names
a single generated counterpart. `schema`, issue number, path pair and
40-character lower-case Git blob SHA-1 are validated before any exemption.
Source bytes must match the pinned Git blob digest; the built artifact must
exist. The ordinary I1 builder additionally verifies each generated SHA-256.

To add a *new, independently reviewed inactive module*, open a separate
issue and PR containing its native source and a new issue-specific manifest.
Never use a wildcard, directory prefix exception or reused digest.
Existing I0 isolation, migrations, M11 and Competition approvals are unchanged.

This removes collisions in the central parity script for future isolated
PRs. No cognitive feature is activated and no scientific/behavioural
conclusion is drawn. Regression: `tests/i1/test_i1_issue_336_parity_pins.py`.
