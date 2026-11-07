# Stage 1 omega: durable evidence custody before execution

Issue #1061. Custody baseline:
`39a03c0841e38948479c11d8262924f8520ab816` (#1131).

**CUSTODY SOFTWARE ONLY. NO SELECTION OR VALIDATION EXECUTION.**

## Problem

The frozen ADR-0015 campaign contains 4,704 full I3 executions. Every main life
must retain its complete original trace.

Committing thousands of compressed traces directly into Git would permanently
inflate the repository. Relying only on GitHub Actions artifacts would instead
make the scientific record depend on artifact retention.

The campaign therefore needs a durable binary custody layer before world 72 is
opened.

## Two-layer custody

A future execution workflow will retain each completed shard in two places:

1. a normal GitHub Actions artifact, used as the workflow's redundant working
   copy and for downstream aggregation;
2. a deterministic ZIP uploaded as an asset of a campaign-specific GitHub
   **prerelease** targeted at the exact execution source commit.

The prerelease is the durable binary evidence store. It is separate from the
Git repository history and therefore does not turn thousands of life traces
into permanent Git blobs.

Selection/final aggregate JSON and their hashes remain small enough to publish
as normal textual evidence as well.

## Deterministic bundle

`stage1_omega_evidence_custody.bundle_directory` takes one completed shard
directory.

The source directory contains:

- the shard receipt JSON;
- every original deterministic `.json.gz` life written before reduction;
- any small shard-local custody files introduced by the execution workflow.

The bundle:

- walks files in lexical path order;
- rejects symlinks;
- rejects output inside the evidence tree;
- reserves `BUNDLE_MANIFEST.json`;
- stores every file as regular mode 0644;
- fixes every ZIP timestamp to 1980-01-01 00:00:00;
- uses one fixed compression setting;
- writes an internal sorted inventory with path, byte count and SHA-256.

The manifest also contains:

- file count;
- total uncompressed bytes;
- SHA-256 of the canonical inventory.

The returned receipt records both the evidence-tree digest and the final ZIP
SHA-256.

The same byte tree and label must therefore create the same ZIP bytes regardless
of host file mtimes or directory-creation order.

## Verification

`verify_bundle` does not trust the ZIP directory listing.

It rejects:

- malformed ZIP;
- duplicate member paths;
- absolute or parent-traversal paths;
- missing/duplicate manifest;
- undeclared extra members;
- duplicate manifest inventory names;
- invalid inventory rows;
- byte-length mismatch;
- member SHA-256 mismatch;
- aggregate file-count/byte-count/tree-hash mismatch.

Its success receipt includes the actual ZIP SHA-256.

## Campaign prerelease

The future workflow should create exactly one prerelease before the first
selection shard runs, after full software CI and source/protocol preflight.

Suggested immutable tag identity:

`i3-stage1-omega-adr0015-<execution-sha-prefix>`.

Each shard asset name must be unique and phase/population/arm explicit, for
example:

- `selection-p0-reference.zip`;
- `selection-p0-candidate.zip`;
- `validation-p7-omega_zero.zip`.

Small aggregate assets should include:

- `selection-aggregate.json`;
- `validation-aggregate.json`;
- campaign asset inventory/digests.

If the campaign fails technically, already completed assets are **not deleted**.
The prerelease should be published/retained with an engineering-failure status.
A technical failure remains distinguishable from mortality.

## Actions artifacts

Actions artifacts remain useful for job-to-job transport and redundant custody,
but their retention period is not the scientific durability contract.

An execution workflow should upload a shard artifact even when a later upload
to the prerelease fails, then stop the campaign.

It must never rerun a shard merely because release publication failed.

## Relationship to the gate

Evidence bundling is observer/custody infrastructure only.

It cannot:

- modify a life;
- change a selected genome;
- change G1-G6;
- rank a candidate;
- open a world;
- add or remove a death;
- repair a missing shard.

The gate continues to consume only authenticated shard receipts after all
predeclared barriers pass.

## Execution still blocked

This custody PR does not add or modify the GitHub Actions execution workflow.

After this software passes and merges, a separate one-shot execution PR must
freeze:

- exact merged source SHA;
- exact runner protocol digest;
- exact campaign prerelease tag convention;
- workflow matrix and timeouts;
- asset names;
- failure publication behavior.

Only that later PR may authorize the first construction of selection world 72.
