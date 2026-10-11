# Stage 11: public 600-world-step software stability and exact replay probe

**2026-10-11, registered BEFORE implementation or execution.** Public development-only software protocol, **NOT** held-out science, Golden acceptance, or a test in the operator's real conditions. Normative source for the currently implemented branch: `docs/architecture/reference/en/mvp-specification-v1.2.1.md` (Stage 11 §20.3, §14 Exploration, §16.4 modulation, §17 deterministic replay). Stage 9 remains scientific NO-GO; PR #25 stays Draft/open.

## Fixed fixture, no tuning after observation

- Source: exactly `build_stage11_reference_runtime(enable_geography=True)`, unchanged world/body physics, initial body, public map, Equipment, temperament, safety rules, P-43 costs and module budgets. Use the existing default Stage-11 version, without adding new behaviors or access to WorldBody hidden data.
- Horizon: exactly **600 completed physical world steps**, not 600 cognitive cycles or 600 journal events. Do not reset or externally refill energy, food, water or integrity; do not alter physiology, inject rewards, invent knowledge, or rewind a fatal outcome. This reference world has its own fixed physics and is **not** a realistic survival challenge.
- Create **two independent runtime instances** from the same immutable fixture. Run each instance from step 1 through 600, using `runner.run_step()` as the sole ordinary physical entry point. Do not share owners or journals.
- After world steps **1, 300, 600** (and **only** those points), take and verify a complete periodic snapshot of all `runner.causal_owners` through the existing `SnapshotManager`, with a fixed descriptive version manifest and the exact step in the receipt. Do not restore or insert additional snapshots. If the execution genuinely stops early (safety block, lethal/terminal or exception), record that first divergence and do **not** declare the 600-step gate passed.
- Collect per-run full technical journal head and canonical SHA-256, all-owner canonical SHA-256, snapshot IDs and SHA-256s, number of actual physical captures, executed commands, outcomes and modulation profile transitions, and total accepted/rejected UC charges. The individual must not receive these technical metrics as cognition.
- Compare the two independent executions **exactly**, including all metrics, final owner state, both canonical full journals (via cryptographic digest and head), and identical snapshot schedule/IDs. Verify each hash-chain; count only physically captured positions as visited. Do not require positive autonomous danger learning or successful hydration at a particular time.
- Separate a stress PASS (600 completed steps and matching replay) from any *behavioral* hypothesis about Exploration or Global Modulation: report observed actions/coverage, do not assert optimization, learning, or real-world survival.
- Generate a compact machine-readable JSON diagnostic with frozen `protocol_version`, `classification=public_software_diagnostic_not_heldout`, `steps`, per-run hashes, count metrics, `identical_independent_reexecution` and `scientific_verdict=null`. Print the complete evidence only if two independent runs agree; otherwise fail closed with first available counterexample.

## Validation and interpretation

- Perform one quick unit regression for source changes unrelated to this probe, then one separately requested Python 3.11/3.12 full CI on the exact probe SHA. Run the 600-step software diagnostic in the full CI (Python 3.12) with a bounded timeout and no permanent **new** workflow trigger. Report its real measured status separately from the unit test count; do not treat it as 600 extra unit tests.
- **No reparameterization post-result.** A failure or early terminal outcome remains negative; propose any alternate conditions as a **new** predeclared experiment, not a revision of this one.
- The 600-step diagnostic can at most support a preliminary **software hypothesis**. As requested by the revised MVP approach, final Stage 11 acceptance still requires **operator validation**. Do not convert this software PASS into project scientific validation or Stage 9 GO.
- Respect the newer project decision toward permanent death: this probe deliberately creates no rollback; any rollback retained by the currently implemented normative-v1.2.1 runtime must be identified as a separate pending architecture migration, not misrepresented as removed.

**Keep `main`, PR #25 merge state, GitHub permissions/protections, and the normative English file unchanged.**
