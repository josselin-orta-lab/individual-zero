# I3 Stage-6-light: offline toy persistence-to-parent-to-genotype check (15 November 2026)

**Status: `TOY_PARENT_SELECTION_LINEAGE_MATCH_NOT_ADMITTED` only for fabricated 16-population inputs.** Engineering-only follow-up to merged PR #1399, the source-pinned genome-v4 reconstruction check, and open issue #1395. The manifest `STAGE6_LIGHT_PROTOCOL_METHOD_V1.json` remains deny-all. There are no new World indices, lives, cohort runs, parent selections on real individuals, owner decisions, or scientific observations.

## Falsifiable question

Given a *caller-supplied* mock persistence receipt for each of the six ecological opportunities of each G0/G1 genotype, an invented RNG seed for each child draw, and a separate claimed G0/G1/G2 genotype chain, can an offline checker reject any mismatch between (a) the exact selection ranking / uniform control, (b) the chosen parent, and (c) the claimed genome-v4 mutation and digest?

**Failure conditions:** a missing or duplicated G0/G1 life opportunity; censored life with less than 400 steps; unexpected fields or non-Boolean censor; a changed persistence score altering a weighted selected parent for a declared seed; a changed uniform-control seed altering its draw; an unsupported / repeated draw seed; a parent slot differing from the selected draw; or a parent/child digest or mutation inconsistent with the independent genome reproduction check. Do not evaluate G2 persistence for selecting G3: the method ends at G2.

## Exact tested mock wiring

- `src/i3/lab/stage6_light_selection_parent_preflight.py` invokes the existing deny-all Stage6 guard first, then calls the offline genome-lineage checker from merged PR #1399. It admits only `kind=TOY_NO_WORLD` receipts, strict exact fields, and 16 independent *logical* populations (or an explicitly marked partial test fixture). Each population must supply G0 144 persistence rows and G1 288 rows, hence **6,912** mock G0/G1 persistence rows across 16 populations. These are **not native archived biological lives**.
- Each generation selects exactly 24 parents per arm/population. For each of **1,536** mock G1/G2 child draws, the checker recomputes `selected` ranking by descending censored count, descending lived steps, ascending slot, then uses linear weights `24,23,...,1`; `random_parent` performs a uniform slot draw and **does not read fitness to choose the parent**. The test-only Python RNG seed is supplied by a caller and therefore can be fitted after seeing an outcome.
- Every declared draw is joined with the child's exact `parent_slot`, `parent_genome_sha256`, `genome_sha256` and full reference-v4 native mutation chain established by the genome preflight. The G0 prior is shared between arms; G2 parentage is arm-specific. No inherited learned mind state or World facts are permitted in that genotype chain.
- The public return contains only structural counts, a claim-content hash, and negative permission/provenance fields. No ranking, score, living result, or scientific sign is emitted.

## Critical nonclaims

A valid mock seed/draw pair is **not evidence that the true parent was drawn prospectively or under the intended distribution**. The seed might have been selected post hoc; comparing it to an invented receipt cannot prove independent randomization. This preflight does not read actual sealed gzip originals or independently validate the historical source/timestamp, real selection state, actual mutation RNG seed custody, biological costs or true execution order G0/S1/G1/S2/G2/R. Indeed, arbitrary synthetic fixtures can fully pass this checker. A SHA-256 of those claims establishes bytes only, not external signing or time of creation.

**Next critical task:** implement a source-exact authentic-original extractor and a verified G/S selection-receipt format, including before-selection sealed original hash roots and independently committed parent/mutation seed streams; then test mismatched state, rollback, conflicting or replayed receipts. No real World/seed or owner permission should be issued automatically. The G/S/R exception to ADR-0017 and separately scoped live rehearsal/science grants are still absent. I1 remains active; I3 remains unregistered development reference; P1.3 funded-v2 stays reference, Stage 2.1 `NOT_ISSUED/HOLD_NO_VERDICT`, and Stage6 `NOT_RUN_NO_AUTHORIZATION`.

Suggested narrow test: `PYTHONPATH=src python -m unittest discover -s tests/i3 -p 'test_stage6_light_selection_parent_preflight.py'`. The full I3 Python 3.11/3.12 CI must pass on the PR exact source before merger.
