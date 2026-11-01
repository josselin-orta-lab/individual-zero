# G0 I1: source, A1-P/A1-C artifact custody inventory (1 November 2026)

**Classification: read-only GitHub provider metadata / research provenance audit.** This is NOT an external custody attestation, independent reproduction, scientific GO, restored M11 evidence, or approval of transition G0.

## Verified Git references (not immutable)

Repository: `josselin-orta-lab/individual-zero`. The reference branch `archive/i1-reference-2026-10-31` pointed, on 1 November 2026, to commit `1e19f02db14b64a35f8bb014d69cc061f311002c`. Its exact `src/i1` tree was `cf7968d3ee94a5792d37d76241a55d4c8406a3fb`, matching the [31 October transition decision](../../architecture/proposals/i2-transition-and-scientific-gates-2026-10-31.md) and issue [#661](https://github.com/josselin-orta-lab/individual-zero/issues/661). GitHub's branch API reports **`protected=false`**. A matching ref *today* does not attest that tomorrow's ref cannot be deleted or rewritten.

## GitHub Actions evidence inventory

The frozen, machine-readable [metadata inventory](../../../config/research-g0-artifacts.json) contains **all 58 provider artifact records**: artifact IDs, names, provider-upload SHA-256 digests, byte sizes, creation and expiry timestamps. Each entry was returned by GitHub Actions REST, but **no artifact bytes were downloaded or inspected in this review**. Metadata digests identify the Actions artifact ZIP wrapper and **are not the authenticated SHA-256 of the original M11 ZIP inside**.

| Campaign | Workflow and originating code SHA | Jobs / provider artifacts observed | First scheduled expiry |
| --- | --- | --- | --- |
| A1-P pilot H48 | [run 40938021102](https://github.com/josselin-orta-lab/individual-zero/actions/runs/40938021102), source `012ece9eb0b4531f714bd69af439eeb38d7bf701` | Eight individual M11 jobs succeeded; aggregate/cold reader job failed; workflow `failure`. **8 individual + 1 aggregate artifacts** currently non-expired | **28 Nov 2026 at 19:13 UTC** |
| A1-C confirmatory H48 | [run 40944104333](https://github.com/josselin-orta-lab/individual-zero/actions/runs/40944104333), source `26f7929b6db43f68e78b0cc0d9c67e7444f924c6` | 48 individual M11 jobs succeeded; independent cold audit job succeeded; workflow `success`. **48 individual + 1 aggregate artifacts** currently non-expired | **28 Nov 2026 at 19:53 UTC** |

These expiry times are **provider-scheduled**, not proof of an automatic deletion at an exact instant. The artifacts are ephemeral; do not rely on them as durable independent M11 custody. The A1-P *run* is not an overall CI success even though the pilot's eight individual jobs and later documented offline historical replay are positive technical observations. The A1-C run success does not turn the targeted scientific **NO_GO** into GO.

## Original-data witnesses already described in the repository

- [A1-P offline reproduction audit](I1_A1P_H48_OFFLINE_REPRODUCTION_2026-10-31.md) and read-only launcher `tools/research/i1_a1p_h48_reproduce.py`: enumerates **eight original ZIP SHA-256** and the separate historical replay capsule SHA-256 `cbe306707c724b0a4c43b628076980d96f4d088092d1bb35e282c0bbf5bada2d`. A dated local check is reported, but this session has **not** acquired or reverified those bytes; GitHub metadata is not a substitute.
- [A1-C preregistration](../I1_ECO_A1C_PREREGISTRATION_2026-10-29.md) and [fixed-action retrospective audit](I1_ECO_A1C_FIXED_TAPE_REWARD_SENSITIVITY_2026-10-30.md): state the frozen 48-life cohort and the original `I1_ECO_A1C_EVIDENCE_MANIFEST.json` SHA-256 `01ac08f8a084dff682256fca721cb6ff0e02b9d085207f088151b76a5e44bfca`. The manifest and original ZIP bytes are **not committed** as scientific evidence into this repository, so their hash and full independent custody were **not verified anew** here.
- [I1 transition plan](../../architecture/proposals/i2-transition-and-scientific-gates-2026-10-31.md): historical results remain A1-C targeted **NO_GO**, A2-R **NOT_EXECUTED 0/96** and general L3 **NOT_ESTABLISHED**. This audit **does not** re-estimate a scientific effect.

## Practical G0 blocker checklist for issue #661

1. **Before 28 November 2026:** have an authorized custodian export the existing **8 + 48 original-life artifacts and both aggregates**, without rerunning or regenerating any mortal lives. Record the GitHub artifact ID, exact download timestamp, package digest, original inner ZIP identity and the original cohort/role/seed/arm.
2. Validate the **downloaded bytes** independently: compare outer GitHub wrapper digests with the provider's metadata, then extract only through a bounded and safe reader and compare *inner original ZIPs* against the eight SHA-256 literals in `i1_a1p_h48_reproduce.py` and the locked 48-entry `I1_ECO_A1C_EVIDENCE_MANIFEST.json`. A run's CI PASS or an API-reported digest does not prove these original M11 contents match.
3. Store copies and sealed manifests in **two genuinely separate durable trust/retention domains**, with documented access, non-rewrite policy, timestamps and independent reviewer retrieval procedure. Do not commit private M11 archives to this public repository by default. A local disk or private library claim alone is not external custody.
4. Ensure the archival Git baseline cannot be **deleted or force-pushed** via an appropriate GitHub ruleset/branch policy or independently retained signed provenance. Verify policy enforcement externally; the current API reports no protection. The baseline tree hash alone is insufficient.
5. Ask an **independent reviewer** to retrieve and attest the original 8/48 life sets, original preregistrations, manifests, aggregate/replay outputs and exact generation SHAs. Record successes, failures, missing files and scientific limitations in a separate dated report. Do not silently drop A1-P aggregate job failure.
6. Close G0 **only** after archive access, independent integrity/reproducibility assessment and branch/source-protection evidence are recorded. Even a completed G0 would not approve G1/G3, I2 activation or L3 generalization.

**Live GitHub source observations on 1 November 2026:** branch and tree identity checked; 9 + 49 provider artifacts reported available and scheduled to expire on 28 November; no download, external custody proof, external reviewer decision or immutable-branch policy performed here. This document and its [metadata inventory](../../../config/research-g0-artifacts.json) are *navigation evidence about what must be independently secured*, not a scientific endorsement.
