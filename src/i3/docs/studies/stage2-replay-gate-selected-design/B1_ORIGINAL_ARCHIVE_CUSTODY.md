# B1 original evidence custody: one-shot permanent archive

**Scope:** preservation of already generated original bytes, not scientific exposure or a new inference. The historical B1 `execute` entrypoint is permanently shut.

## Exact experimental provenance

- Frozen source/executed PR head: `713d4621d28ed668bf5f5a37f2d105a38d19fb57`.
- Executed GitHub Actions: [run #42735037051](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42735037051).
- Original run artifact: [#13725454291](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42735037051/artifacts/13725454291).
- Original GitHub artifact ZIP SHA-256: `2aff70fff077be04042379355cda8c798ed9ec81745413563bc88e4320615361`.
- Complete original MANIFEST SHA-256: `5a173d1ad2a7ea3980cb27f79fada44d4e9f7855af63d08a21d118acce21da9a`.
- Original source fingerprint: `3a533ebcf8657716bcd759aaa0c0ec1c694aed82862abeb1eb175b593cd8ede3`.
- Original frozen PLAN SHA-256: `37bee5deeb75e7e4ab481f3019b63c54b9d6f8bdabba6f7bb1de135e62f021dc`.
- GitHub ephemeral artifact expires 2027-02-08. A separate Git-hosted evidence branch is the intended persistent original custody.

## Exact one-shot archive workflow

The existing `.github/workflows/i3-proposal-checks.yml` contains a narrowly gated job named `b1-original-custody`, enabled ONLY on a `main` push that changes the frozen marker `B1_ARCHIVE_ONCE.json`. Other I3 PR jobs remain PR-only. The job uses minimal `actions: read` and `contents: write` permissions on trusted `main`, does not run untrusted PR scripts, never calls a Lab/World or generates a life, and refuses Actions reruns. It downloads only the exact original artifact ID. The job demands full original ZIP and manifest digests and validates all 192 gzip originals (packed/unpacked SHA, World/source/plan identity, paid cognition, matched pairs and outcomes) before publishing.

The target preservation ref is `evidence/i3-b1-96pair-development-20261110-originals`; the job creates it only if absent and never force-pushes. Original ZIP bytes remain unchanged, with `VERIFICATION.json` and `SHA256SUMS` under `archive/i3/stage2-b1-development-2026-11-10/`. An existing branch causes a hard failure rather than overwriting. This is Git-hosted immutable-by-procedure custody, **not** cryptographic write protection against a repository administrator deleting/changing refs.

## Verify the retained archive after publication

On the evidence branch:

```bash
cd archive/i3/stage2-b1-development-2026-11-10
sha256sum -c SHA256SUMS
```

The receipt should say 192 complete original lives, 96 exact matched pairs, 25 both alive, 5 FIXED-only, 13 GATE-only, 53 neither. The scientific interpretation is fully documented by [B1 exploratory results](B1_EXPLORATORY_DEVELOPMENT_RESULTS_2026-11-10.md). The archival job's successful execution and existence of the evidence branch **must be verified** before claiming permanent custody. Until then, issue #1248 remains open.

This archive does not certify iid sampling, the external witness, a clinical/statistical non-inferiority margin, independent scientific review, or active-engine status. No new indices or World exposures are authorized.
