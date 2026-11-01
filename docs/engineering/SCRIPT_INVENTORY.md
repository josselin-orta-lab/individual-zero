# Script ownership and legacy research inventory

This inventory was originally established at commit `da72aca212f69bd47275a4592a781caef1896206`; it is **not** a live executable-script census. Always consult the versioned JSON at current HEAD for membership and run the static checks before using counts. It distinguishes scripts **explicitly referenced by the current natural I1 workflow** from scripts that require owner review. A path marked for review is *not* automatically obsolete, unused, safe to delete, or a scientific oracle.

The active infrastructure script classification is listed in `config/tool-inventory.json`. Other scripts include historical A2/issue110 scientific explorations, I0 checks, M11 benchmarking and research-specific utilities. Keep their bytes and reproducibility intact until explicit dependency mapping and per-generation custody are established.

**Policy:** new active infrastructure belongs in versioned `tools/`, `src/i1/lab/` or its engine-specific test suite; historical scripts stay inspectable but never become natural I1 acceptance gates based on their filenames. Do not bulk-move imports or scripts by heuristic and do not reactivate old A2 workflows as required checks.

Use `python tools/check_tool_inventory.py` to verify that the inventory accurately covers tracked Python scripts under `scripts/` and that current CI essentials remain classified as active. Any new script requires an explicit inventory decision before the structural CI can pass.

## Dependency evidence without running old cohorts

Run `python tools/scan_script_dependencies.py --output reports/script-dependencies.json --markdown-output reports/script-dependencies.md`. The scanner parses the scripts listed at the current commit via Python AST and records direct local imports, transitive dependencies between scripts, unresolved dynamic imports, and `i0` / `i1` / `lab` / `i1lab` namespace observations. **A namespace is evidence of an import, not proof of ownership or scientific relevance.** The explicitly classified active infrastructure scripts are blocked from depending transitively on unreviewed historical scripts. A small, source-blob-pinned subset has direct imports attested in `config/script-custody.json`; all other historical files remain pending individual review. The report is diagnostic, never an execution or scientific GO.

## Generation-aware import evidence and manual script triage

Run the static scanner on the current commit. The JSON report now contains
`observed_import_root_counts`, `review_queue` and `review_queue_status`.
It distinguishes `i0`, `i1`, `i1lab` and the **unscoped legacy**
`lab` namespace. The old `lab` import does not establish I0 ownership,
since older I1 research also used it.

The review queue prioritizes scripts with ambiguous Lab dependencies,
cross-generation references, unresolved dynamic launches and inbound
dependencies from active infrastructure. The score is an **organizational**
heuristic and never a scientific confidence score. Every row includes
the Git blob SHA, observed roots, callers and reasons.

An actual owner assignment still requires separately reviewed source
provenance, tested dependency closure and an explicit manual decision.
Neither the report nor this inventory moves, activates or executes scripts.

## Decision protocol: preserve first, move only with proof

As of the inspected main at `6ebf53aa7235ff1d8598998d3de0bb7377e659ff`, the JSON inventory lists **6 active CI scripts and 148 research/legacy review scripts (154 total)**. These are dated counts, not assertions about future HEAD. Files are not automatically obsolete because of age, a historical study identifier, or a lack of an obvious current import.

1. **Find an existing owner.** Check `config/tool-inventory.json`, `config/script-custody.json`, current GitHub workflows, the original experiment, and the actual call sites. The inventory defines the initial triage queue, not a migration instruction.
2. **Inspect dependency closure without executing experiments.** Run the static scanner and inspect a single path in `reports/script-dependencies.json` under `scripts["scripts/<name>.py"]`. Check its `source_git_blob_sha1`, `script_dependencies`, `resolved_subprocess_script_dependencies`, `direct_import_evidence`, `literal_file_references` and `dynamic_or_relative_import_lines`. An absent static dependency is **not** proof of non-use.
3. **Make one explicit decision:** keep active in place; preserve as a historically reproducible script pending custody; move a proven independent script behind a path-compatible wrapper; or request a source-pinned archive relocation with documented reproduction impacts. Never silently delete, bulk-rename or import historical scripts as a new generation's runtime.
4. **Validate the smallest relevant contract first.** Check `python tools/check_tool_inventory.py` and the applicable generation's tests. Before moving anything, inspect workflow entrypoints, docs links, subprocess invocations, relative-path assumptions and exact-source citations. Preserve original SHA provenance in the review record.
5. **Record the outcome in the PR:** affected paths and generation; original Git blob; caller/dependency evidence; unresolved dynamic references; exact tests and SHA; compatibility or archival strategy; whether scientific behavior changed; explicit `NOT_EVALUATED` if no experiment ran.

A physical reorganization is worthwhile only when it improves agent navigation **without losing experimental reproducibility**. Continue classifying ambiguous sources rather than inventing more directories to store an unresolved question. See [agent navigation](AGENT_NAVIGATION.md), [test placement](../../tests/TEST_LAYOUT.md), and [research source custody](RESEARCH_DOSSIERS.md).
