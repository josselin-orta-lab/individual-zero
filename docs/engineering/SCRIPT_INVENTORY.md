# Script ownership and legacy research inventory

This manifest is a conservative snapshot of the scripts present at commit `da72aca212f69bd47275a4592a781caef1896206`. It distinguishes scripts **explicitly referenced by the current natural I1 workflow** from scripts that require owner review. A path marked for review is *not* automatically obsolete, unused, safe to delete, or a scientific oracle.

The active natural-I1 CI scripts are listed in `config/tool-inventory.json`. Other scripts include historical A2/issue110 scientific explorations, I0 checks, M11 benchmarking and research-specific utilities. Keep their bytes and reproducibility intact until explicit dependency mapping and per-generation custody are established.

**Policy:** new active infrastructure belongs in versioned `tools/`, `src/i1/lab/` or its engine-specific test suite; historical scripts stay inspectable but never become natural I1 acceptance gates based on their filenames. Do not bulk-move imports or scripts by heuristic and do not reactivate old A2 workflows as required checks.

Use `python tools/check_tool_inventory.py` to verify that the inventory accurately covers tracked Python scripts under `scripts/` and that current CI essentials remain classified as active. Any new script requires an explicit inventory decision before the structural CI can pass.

## Dependency evidence without running old cohorts

Run `python tools/scan_script_dependencies.py --output reports/script-dependencies.json --markdown-output reports/script-dependencies.md`. The scanner parses all 153 script files via Python AST, records direct local imports, transitive dependencies between scripts, unresolved dynamic imports, and `i0` / `i1` / `lab` / `i1lab` namespace observations. **A namespace is evidence of an import, not proof of ownership or scientific relevance.** The five active infrastructure scripts are blocked from depending transitively on unreviewed historical scripts. Two historical I0 compatibility scripts have a direct import attested in `config/script-custody.json`; all others remain pending explicit review. The report is diagnostic, never an execution or scientific GO.

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
