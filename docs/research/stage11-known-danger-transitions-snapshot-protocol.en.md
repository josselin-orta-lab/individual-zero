# Stage 11: canonical known-danger transitions across full-owner snapshots

**Software-test contract recorded on 2026-10-11 before implementation of these tests.** Not a scientific preregistration, held-out trial, safety certification or Golden. The sole normative source is `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, notably DC-05, DC-08, INV-01/08/25/33 and immediate Action Control final veto.

## Question and boundaries

Current unit tests separately show: (a) a synthetic DC-05 promotion blocks a geographic frontier/return, (b) a full-owner snapshot taken *before* promotion restores unknown safety facts, and (c) physical world scenario danger injection is not a knowledge oracle. They do not jointly test a **live known-danger promotion followed by revocation and two full-owner snapshots** in a runtime that has already executed physical steps.

The learned safety status belongs **exclusively** to the canonical Causal Model. `CanonicalSafetyFacts` reads it; Exploration and Planning must never maintain independent forbidden maps. Physical WorldBody lethal/danger zones remain separate from the individual's learned model, and synthetic unit evidence must never enter a scientific record. This test intentionally invokes the causal owner outside normal phase scheduling to probe its service boundary; it **does not** demonstrate that live physical evidence produced these transitions.

## Frozen inputs and expected behavior

1. Build the existing public `junction_open` Stage11 observed-route fixture (survey refresh on, route enabled, no hazards in WorldBody). Execute step 1 normally: a physical capture at (2,2) and potential move into the known public east corridor. The canonical status of (4,2) begins `unknown`.
2. Inject two distinct, explicitly labeled **synthetic unit-only** DC-05 harm records for `lethal-zone:4,2`, with unique episode and observation references, `source="monde"`, and the existing `n_sec=2`. A single record is insufficient; two published records yield `known_lethal`. These fabricated test fixtures carry no actual physical provenance or scientific weight and must not be recorded as lived observations.
3. Execute the next full real-world step under this synthetic known-lethal state. Verify the charged canonical geographic preflight excludes the physical destination (4,2), no autonomously dispatched movement enters it, and the real Perception visits remain correct. The final Action Control veto is not bypassed.
4. Take a **full-owner periodic snapshot** at that coherent step boundary; include WorldBody, Exploration, Causal Model, Memory (including the spontaneous-recall threshold), scheduler and other canonical owners. Capture exact exported states and verify the snapshot fingerprint.
5. Introduce two unique, synthetic unit-only DC-05 *harmless* records, maintaining the existing `m_sec=2`: the first alone cannot lift prohibition, the second publishes status `aucun`/unknown. Do not modify WorldBody ground truth or preserve a private unsafe map. On the next real step, the now-revoked hazard is no longer excluded by the canonical safety prefilter; the choice remains subject to ordinary cognitive evaluation, budget and final veto. The test must not force movement or invent reward.
6. Take a second full-owner snapshot after a real step. Restore the known-lethal checkpoint and the unknown checkpoint independently; every causal owner must equal its corresponding frozen state. The live SafetyFacts view must immediately agree with its restored canonical model. Append-only journal integrity is checked, without claiming that snapshot restore rewinds technical history.
7. Unit validation only: compare two independently constructed runs of the same scripted synthetic inputs and public WorldBody trajectory for deterministic normalized journals and owner states **within this test**, while explicitly noting the synthetic safety inputs are not journaled lived evidence and cannot be used as scientific replay proof.

Any failed invariant remains a failure; do not weaken to one-sided comparison. Do not run Python3.11 full, long Goldens, held-out, or merge from this contract.

**Before test execution: UNVERIFIED. Stage 11 IN PROGRESS, Stage 9 scientific NO-GO; PR #25 remains draft/unmerged.**
