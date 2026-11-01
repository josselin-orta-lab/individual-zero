# G0 operator handoff: export and check historical I1 evidence, without new lives

**Purpose:** perform a reproducible, *operator-controlled* retrieval of the existing A1-P and A1-C GitHub Actions artifacts. This is a practical continuation of [the dated G0 provider inventory](../research/audits/I1_G0_PROVIDER_ARTIFACT_CUSTODY_2026-11-01.md) and [issue #661](https://github.com/josselin-orta-lab/individual-zero/issues/661). It is NOT an independent custody audit, G0 GO, living I1 execution, or new I2 capability.

## Why this is urgent

As observed on 1 November 2026, A1-P [run 40938021102](https://github.com/josselin-orta-lab/individual-zero/actions/runs/40938021102) held **8 life artifacts and 1 aggregate**; A1-C [run 40944104333](https://github.com/josselin-orta-lab/individual-zero/actions/runs/40944104333) held **48 life artifacts and 1 aggregate**. GitHub displayed an expected **28 November 2026** expiry. The 8 individual A1-P jobs passed but the **A1-P aggregate job failed**. A1-C software jobs passed yet its **targeted scientific result remains NO_GO**. The source archive branch is still **unprotected** at the dated inspection. Recheck GitHub availability and retention immediately before the operator export.

The inventory's `provider_artifact_digest` is the GitHub package's reported SHA-256, **not** an attestation of any M11 archive, SQL event chain, causal benefit, or independent storage.

## Phase 1: plan and operator-reviewed download

Run in a **complete local checkout** with Python 3.11+. The only script introduced for this task is [`tools/research/g0_custody_receipt.py`](../../tools/research/g0_custody_receipt.py), reusing the existing G0 manifest validator. It performs **no network request** itself.

```bash
python tools/research/g0_custody_receipt.py plan > /tmp/iz-g0-export-plan.json
python tools/research/g0_custody_receipt.py plan --shell > /tmp/iz-g0-export-review.sh
```

The second command emits 58 commands referencing **exact immutable GitHub artifact IDs**. Inspect the script before executing it. It uses your existing authenticated `gh` session, creates new files with restrictive permissions and refuses to overwrite an existing artifact name. It never writes a GitHub token to the script. It requires an explicitly selected private destination:

```bash
export IZ_G0_EXPORT_ROOT=/secure/location/outside-this-repository/g0
mkdir -p "$IZ_G0_EXPORT_ROOT"
chmod 700 "$IZ_G0_EXPORT_ROOT"
# Inspect /tmp/iz-g0-export-review.sh before explicitly running:
bash /tmp/iz-g0-export-review.sh
```

**Do not put originals under the public repository**, attach private M11 data to an issue or PR, check it into Git, or use an unaudited bulk ZIP extractor. A downloaded artifact may itself be a provider ZIP wrapping the original M11 ZIP: keep those layers distinct. A 401/404/expired artifact must be reported as missing rather than replaced by a synthetic life. If the `gh api` transport returns an unexpected body, the next phase refuses its byte digest.

## Phase 2: offline package-byte receipt

When *all* packages of one campaign have been retrieved, verify them against the **dated original inventory**. Use separate receipt paths **outside the export directory**; the tool will not overwrite an earlier receipt.

```bash
python tools/research/g0_custody_receipt.py verify \
  --root "$IZ_G0_EXPORT_ROOT" --campaign A1P \
  --receipt /secure/location/a1p-provider-receipt.json

python tools/research/g0_custody_receipt.py verify \
  --root "$IZ_G0_EXPORT_ROOT" --campaign A1C \
  --receipt /secure/location/a1c-provider-receipt.json
```

Or use `--campaign ALL` if all 58 are present. A failure on missing, extra, altered, linked or size-mismatched files returns nonzero and writes **no receipt**. SHA-256 is streamed from opened regular file descriptors; the verifier is offline and never extracts M11, launches I1, executes research, or mutates the original ZIPs. A receipt includes the original inventory SHA-256, provider IDs, observed byte digests, a **local clock** timestamp (not trusted time), and explicit fields:

- `original_inner_m11_zip_sha256_verified: false`
- `original_m11_chain_audited: false`
- `independent_durable_custody_attested: false`
- `G0_scientific_gate: PARTIAL` and `scientific_verdict: NOT_EVALUATED`

**Provider package byte match is only stage one.** It never means that the original scientific contents match.

## Phase 3: verify original M11 ZIP identities against frozen source pins

Preserve each provider package unchanged, then stage the **original** inner ZIPs in separate private, empty A1-P and A1-C directories outside the repository. Inspect provider ZIP members and extract only through an isolated, bounded ZIP reader with checks for duplicate names, path traversal, link entries and ZIP bombs. The G0 tool deliberately **does not unpack or execute** downloaded packages, so an untrusted package cannot trick the research agent into overwriting evidence. Do not silently treat the GitHub wrapper as an original M11 ZIP.

Run the **new offline originals-byte stage** once the operator has staged all original ZIPs. It reads the historical A1-P eight-hash matrix from the *exact Git blob* of the existing A1-P reproducibility tool; A1-C uses the separately SHA-256-pinned original 48-life manifest and the exact Git blob of its existing cold audit. Any changed frozen reader, missing ZIP, unexpected extra file, mismatched hash/size or duplicate A1-C entry is a hard failure:

```bash
python tools/research/g0_custody_receipt.py verify-originals \
  --campaign A1P --originals-dir /private/g0/originals-a1p \
  --receipt /private/g0/receipts/a1p-original-byte-receipt.json

python tools/research/g0_custody_receipt.py verify-originals \
  --campaign A1C --originals-dir /private/g0/originals-a1c \
  --manifest /private/g0/sealed/I1_ECO_A1C_EVIDENCE_MANIFEST.json \
  --receipt /private/g0/receipts/a1c-original-byte-receipt.json
```

A1-P original filename tokens use `td-read-masked`, whereas some GitHub *artifact names* use `td_read_masked`. Preserve the exact filenames required by the frozen scientific SHA list when staging the original ZIPs; do not reinterpret role/seed/arm.

The output `ORIGINAL_M11_ZIP_BYTES_MATCH_HISTORICAL_PINS` asserts **byte identity only** relative to these dated project pins. It does not authenticate the source independently, validate native M11 causal journals, rerun a birth, attest external storage, or approve G0. Receipts include exact historical run/source identifiers and the reader Git blob. A green receipt must be followed by the existing scientifically scoped cold audit.

For A1-P, the existing [A1-P H48 reproducibility tool](../../tools/research/i1_a1p_h48_reproduce.py) separately verifies its sealed **research capsule** and original ZIPs. A capsule is required for this deeper tool; it is **not** created or certified by the new byte-receipt command:

```bash
python tools/research/i1_a1p_h48_reproduce.py \
  --verify-only --capsule /private/locked-a1p-capsule.zip \
  --originals /private/8-original-a1p-zips
```

For A1-C, the [existing cold audit](../../tools/research/i1_a1c_reward_shadow_audit.py) additionally checks the native M11 chain and historically scoped measures. Its original manifest digest is `01ac08f8a084dff682256fca721cb6ff0e02b9d085207f088151b76a5e44bfca`. Successful original ZIP checks are a prerequisite, not a substitute for independent scientific reproduction. They do **not** rerun births or transform A1-C NO_GO into GO.

Finally, commission **independent retrieval and hashing** from at least two separately governed durable custody domains, record an external attestation (signed/independently verifiable as applicable), and enable or independently anchor deletion/force-push protection for `archive/i1-reference-2026-10-31`. Merely creating local receipts cannot close G0.

## Focused development tests

```bash
python -m unittest discover -s tests -p test_g0_custody_receipt.py -v
python tools/research/g0_custody_receipt.py plan > /tmp/iz-g0-plan.json
python tools/research/g0_custody_receipt.py verify-originals --help
python tools/research_dossiers.py g0-provider-inventory
```

These checks use synthetic bytes and metadata only. No CI job should authenticate with GitHub to bulk-export historical M11 artifacts or run any mortal cohort. Report PASS/FAIL/NOT_RUN and exact source SHAs separately. After authorized external retrieval and independent review, update issue #661 with **redacted** evidence metadata, never secret custody paths or personal archive contents.
