# Stage 12: historical research location index

This index routes readers to the original Stage 12 research records. It does not reproduce or move source-pinned reports, authenticate scientific findings, or supersede the [current I1 evidence matrix](../../../../src/i1/docs/EVIDENCE_MATRIX.md).

At the 2026-11-01 repository organization baseline, **226** Markdown records matching `stage12-*` are located directly in `docs/research/`. This number is descriptive and may change.

## Find the original records

```bash
python tools/research_location_index.py --family stage-12 --limit 25
python tools/research_location_index.py --family stage-12 --match prereg --limit 25
python tools/research_location_index.py --family stage-12 --match result --limit 25
python tools/research_link_audit.py --limit 20
```

Each location-index entry reports the original Git path, Git blob SHA and a filename-based document-type hint. `protocol`, `result`, `audit` and `test` are search terms, **not scientific verdicts**. The [global study routing guide](../README.md) and [research corpus](../../../engineering/RESEARCH_CORPUS.md) cover related study IDs and possible cross-document connections.

Do not copy these 226 records into this directory or rename them en masse. Source-pinned manifests, old workflows, citations and historical exact-SHA reproduction can rely on their original paths. New studies may receive their own English-named directory; old study records require an explicit provenance audit before any migration.
