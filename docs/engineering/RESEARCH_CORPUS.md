# Incremental research corpus indexing

This is the discovery and triage layer between [the global research coordinator](RESEARCH_COORDINATOR.md) and the hundreds of dated reports, experiment notes and proposals in Individual Zero. It is **not** a scientific evaluator, a search index of hidden research archives, or a new source of truth.

The script `tools/research_corpus.py` runs locally on a complete repository checkout. It reads the curated `catalog_roots` from `config/research-program.json`, currently `docs/research/`, `src/i1/docs/`, `src/i2/docs/`, `docs/architecture/proposals/` and `experiments/`. It uses only the Python standard library and does not contact GitHub, run a cognitive engine, execute tests or experiments, or update a scientific gate.

## Three useful outputs

**1. Reproducible document inventory:** files are ordered by repository path, indexed by their real Git blob hash, filename-derived kind hint, title, direct Markdown links, explicit issue/EXP/ADR/study identifiers and limited status mentions with original line numbers. All extracted status mentions carry `TEXT_MENTION_NOT_SCIENTIFIC_VERDICT`.

```bash
python tools/research_corpus.py index --output /tmp/iz-corpus-index.json
python tools/research_corpus.py report --top 10
```

**2. Incremental changes:** compare the current checkout with a previous inventory to identify added, deleted or changed files, including research identifiers that need fresh review. **Both prior and current topic references** count when selecting affected topics. The old snapshot is user-supplied, not authenticated evidence.

```bash
python tools/research_corpus.py delta --baseline /tmp/iz-corpus-index.json
```

**3. Candidate linkages:** review documents that share explicit identifiers such as `study:A1-C`, `study:A2-R`, `issue:304`, `exp:EXP-0001` or `adr:ADR-0001`.

```bash
python tools/research_corpus.py review --topic study:A1-C --limit 20
python tools/research_corpus.py review --topic issue:304
```

Shared identifiers only establish **possible topical relationships**. Two reports may cite the same issue while measuring different endpoints, reference different motor versions or describe historical versus current work. Filename tags like `possible_preregistration` and `possible_results` are review hints, not verified document types.

## Before adding anything to the knowledge graph

For each candidate protocol/results/decision chain, the reviewing agent must inspect its source content and establish: original preregistration; scope and date; version and exact source SHA; cohort, independent units and seeds; true controls; observed measurements; failed or null outcomes; alternative explanations; and the actual independent disposition. If any of these is absent, use `UNVERIFIED` or `NOT_OBSERVED`. Do **not** manufacture a scientific graph edge based on a filename or a software CI PASS.

The indexer surfaces co-occurrences of `NO_GO` and `PASS` as `POSSIBLE_STATUS_SCOPE_DISAGREEMENT_REVIEW`. This typically means the words may refer to **different things**, not that the research is contradictory. A contradictory claim requires comparing the same scientific question, protocol, population, endpoint, time and evidence lineage.

After human/agent review with appropriate authorization, update the original evidence owner first, then the curated `config/research-program.json` with explicit source marker and exact Git blob. Run the research coordinator audit. Negative findings and historical decisions must be preserved rather than silently overwritten.

## Boundaries and security

- A complete local checkout is required. Symlinks to other files or directories are skipped; path escapes and overlapping roots are rejected. Text extraction skips large/non-UTF8 documents with an explicit status.
- Markdown code fences are excluded from direct ID and status extraction. References are limited to explicit text patterns and local Markdown links; the index is not complete semantic understanding.
- The index is deterministic for a given checkout. An output file is created **only** with explicit `--output`. Do not commit generated snapshots as normative evidence, and do not consume unverified snapshots as approval.
- I0 remains frozen; I1 remains active; I2 is proposal-only and not born. No corpus-derived lead grants birth, rollback, motor control, recovery, experimental execution or promotion.
- For source interpretation and research prioritization, return to [the research coordinator](RESEARCH_COORDINATOR.md), [document authority classes](DOCUMENT_AUTHORITY.md) and the generation-owned evidence matrix.

## Lightweight validation

```bash
python -m unittest discover -s tests -p test_research_corpus.py -v
python tools/research_corpus.py report --top 3
python tools/research_coordinator.py audit
```

This task is deliberately a read-only corpus-navigation improvement. Broader semantic summaries, operator attestations and automated linkage to the *verified* research graph require a separately reviewed extraction-and-claim schema; do not promote scraped text to science.
