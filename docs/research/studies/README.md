# Research studies: navigation without relocating evidence

This is a **current navigation index**, not a new scientific evidence store or a replacement for an original protocol. Historical source files remain at their original Git paths because software, citations, Git blob pins and replay procedures may depend on those paths.

## Where to start

| Research family | Original records to inspect | Authority and limitations |
| --- | --- | --- |
| I1 A1-C targeted learning | [Original preregistration](../I1_ECO_A1C_PREREGISTRATION_2026-10-29.md) and [I1 evidence matrix](../../../src/i1/docs/EVIDENCE_MATRIX.md) | Read original outcomes and independent reviews; reported targeted NO_GO is not a verdict on all forms of learning |
| I1 A2-R reward / native-Q | [Original preregistration](../I1_ECO_A2R_REWARD_PREREGISTRATION_2026-10-30.md) and [generation status](../../../src/i1/docs/STATUS.md) | A preregistration and software contracts do not prove a cohort executed |
| I1 S1 | [Original preregistration](../i1-s1-main-72-life-prereg.md) and [dated report](../i1-s1-main-72-life-final-report-2026-10-18.fr.md) | Report claims require exact-source and trace verification |
| Historical Stage 9 | [Held-out evaluation manual](../stage9-independent-heldout-evaluation-manual.en.md) and [prelaunch decision](../stage9-heldout-prelaunch-decision-record.md) | Historical evaluation procedures are not an active I1 or I2 promotion gate |
| I2 G1-LAB aversion interpretation | [Source-pinned reappraisal and hidden-recovery study](i2-g1lab-aversion-reappraisal-2026-11-01/README.md) | Corrects the H2 interpretation, without a new experiment or scientific GO |
| Source and archive custody | [G0 provider-artifact audit](../audits/I1_G0_PROVIDER_ARTIFACT_CUSTODY_2026-11-01.md) and [research-source reconciliation](../audits/RESEARCH_SOURCE_RECONCILIATION_2026-11-01.md) | Custody uncertainty and source-SHA disagreements must remain visible |

The [global research coordinator](../../engineering/RESEARCH_COORDINATOR.md) provides candidate priorities and exact source references. It cannot authorize experiments or turn a test PASS into a scientific GO. For a broad historical catalog, use the [research corpus](../../engineering/RESEARCH_CORPUS.md).

## Historical Stage directories

- [Stage 11 research routing](stage-11/README.md): original report locations, grouped with the filename catalog.
- [Stage 12 research routing](stage-12/README.md): original report locations, preserving all existing links and Git blob identities.

These are navigation-only indexes: they never change the scientific status of a record.

## Other historical families

- [I1 records](i1/README.md)
- [M11 records](m11/README.md)
- [Stage 9 records](stage-9/README.md)
- [Stage 10 records](stage-10/README.md)
- [Cross-cutting records](cross-cutting/README.md)

The remaining Stage 4, Stage 5 and A-series records are accessible through the global catalogue; their small counts do not justify extra duplicate directory layers.

## New study layout (English directory and file names)

Create new records within `docs/research/studies/<study-id>/` only when a **new** study has a clearly identified owner. Link its protocol, measurements/results, negative evidence, limitations and independent review from a local `README.md`. Do not duplicate an existing document to create an appearance of independent evidence.

```text
docs/research/studies/
  README.md                 # current routing index (this file)
  <study-id>/
    README.md               # owner, question, source SHA, evidence status, links
    protocol.md             # proposed or preregistered method
    results.md              # observations and limits, when actually measured
    review.md               # independent verdict, only if actually reviewed
```

These filenames are a **suggested future convention**, not required empty placeholders. Keep large raw traces and authenticated M11 materials in their appropriate secure custody, not directly in Git. Recorded file paths and Git blob identities remain part of provenance.

**Before any historical move:** audit all original links, source-pinned manifests, CI/workflow references, tests and reproducibility commands. Preserve frozen I0 bytes. Perform reviewed, narrowly scoped migrations only; never use a pathname or an inferred date to determine scientific authority.

## Read-only discovery

```bash
python tools/repository_layout.py inventory --kind docs --match a1c --limit 20
python tools/repository_layout.py inventory --kind docs --match stage9 --limit 20
python tools/research_corpus.py report --top 8
python tools/research_dossiers.py gaps
```

The inventory is an address book, not a scientific conclusion. Historical records must not be bulk moved: preserve source paths until each original link, experiment manifest, SHA and CI reference is audited.

## Stable location index for the historical root

The 419 root-level Markdown records remain at their original paths. Use the read-only, Git-blob-preserving catalog to filter by filename-based family and topic:

```bash
python tools/research_location_index.py --family stage-12 --match result --limit 20
python tools/research_location_index.py --family stage-11 --limit 15
python tools/research_location_index.py --family i1 --limit 20 --json
```

The catalog classifies **names**, not verified generation ownership, protocol validity or conclusions. Do not move a report merely because its filename contains a stage or a result keyword.

## Read-only local-link review

Find broken or ambiguous relative Markdown links in the historical root, without editing original evidence:

```bash
python tools/research_link_audit.py --limit 30
python tools/research_link_audit.py --json --limit 100
```

Missing links are **review leads**, not automatic corrections: links may refer to older commits, external archives, intentionally retired paths or files outside this checkout. Review original source SHAs and Git history before modifying a dated report. The scanner does not validate scientific claims.
