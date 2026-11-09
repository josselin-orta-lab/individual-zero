# Survival B1: prospective F0 WorldSpec compatibility and collision preflight

**9 November 2026 · NON-EVIDENTIARY SOURCE ADAPTER PROTOTYPE · NO SCIENTIFIC LIFE**

Continuation of the [1,500-pair metadata-only allocation](B1_PROSPECTIVE_SAMPLING_PREFLIGHT.md), the [B1 scientific study design](SURVIVAL_B1_LAUNCH.md), and [decision gate #1239](https://github.com/josselin-orta-lab/individual-zero/issues/1239). This slice bridges metadata to **temporary, fully specified ecologies** for engineering validation. It does **not** create an individual, step a World, collect biological survival, preregister B1, open a validation or reserve cohort, or authorize any new science index.

## Mechanism-preserving candidate adapter

New module: \`src/i3/lab/stage2_survival_b1_worldspec_audit.py\`.

The unchanged P2 ecology source \`p2_ecologies.py\` defines three mechanisms: \`stable\` (persistent water), \`depletion\` (near finite and far persistent source), and \`pulse\` (finite water with periodic external dry/recovery events). The B1 **private structural builder** separately reproduces the same transformations and calls the same \`p2_ecologies.validate_ecology\` checks. The only generation parameter difference is the *explicit*, bounded-by-preview \`worldgen.generate(..., development=False)\`, which permits proposed high seed values. The legacy P2 \`world_for\` cohort bounds, default-development guard, historical indices, physics, resource tariffs and active experiment registry remain untouched.

To catch an unintended F0 change, dedicated tests compare the **entire canonical WorldSpec snapshot fingerprint**, not just a family name or sample geometry, between the new builder and historical P2 generation on non-reserve development, selection and validation seeds for all three ecologies. No historical life is rerun. This is compatibility against the current frozen P2 implementation; **future source fingerprinting must still explicitly record the entire byte-level generation chain** before any science.

## Synthetic audit of the full proposed 1,500-pair preview

The auditor accepts only the [fixed PUBLIC, synthetic preview witness](B1_PROSPECTIVE_SAMPLING_PREFLIGHT.md), recomputes the entire 1,500-pair manifest, rejects altered or missing identities, and generates the **1,500 proposed WorldSpecs exactly once each** under the preview. A call to P2 structural validation transiently instantiates a World solely to verify its internal consistency; it does not take an action, capture observations, create a Mind or spawn a biological life. Therefore "no scientific Worlds opened" does **not** mean zero WorldSpec objects or zero temporary constructor checks. The status counter distinguishes these facts.

Two SHA-256 fingerprints per spec are checked across the 1,500 inputs, without convenient reseeding:
1. The **full canonical initial snapshot** including its unique seed-based display name, for provenance.
2. The **name-independent canonical initial snapshot**, removing \`name\` before hashing. This rules out a false uniqueness claim based solely on different names when the material initial ecology is identical.

If any pair shares either fingerprint, the entire synthetic audit **fails closed**, reports the collision as an engineering fault, and does not drop or replace that pair. The audit computes one digest of the ordered \`(pair_id, family, full_digest, name_free_digest)\` rows for cross-version comparison. CI publishes *only* this aggregate fingerprint, per-family counts, structural PASS/FAIL, number of specs validated and explicit negative admission/independence flags. No individual world layouts, genomes, survival outcomes or original-life records are exported.

The dedicated job runs under the existing allowlisted I3 proposal workflow on Python 3.11 and Python 3.12. It is **not a 3,000-life rehearsal** of FIXED/GATE, and it does not provide a future scientific runner or admission token.

## Statistical and custody limitations

An observed 1,500/1,500 no-collision result would support only *distinct generated synthetic WorldSpec snapshots for one public-key schedule*. It would **not prove** independence or identical distribution of survival outcomes across proposed pairs, an unbiased ecological superpopulation outside the three F0 generators, an approved loss margin, full B1 inference power, or external research authority. Deterministic HMAC-derived seeds are a reproducibility contract, not independently witnessed entropy. The 1,500 proposed pairs remain **a resource capacity scenario**, never an arbitrarily selected confirmatory n.

Prospective B1 scientific execution still requires:
- Independent methodological review of actual **iid-pair target/sampling** and ecological family weights, acceptable survival-loss margin, fixed sample size, and calibrated one-sided paired non-inferiority analysis. Include adverse-family, missing-data and multiplicity interpretations.
- A **new** independent committed and externally witnessed source/World/seed plan (not the public preview root), explicit source-file pins, actual WorldSpec digest collision audit, and verified non-overlap with all consumed and P2 reserved indices.
- A **separate fail-closed scientific admission mechanism**, complete exact-path full-scale engineering G/R rehearsal with source-stable provenance, and fresh, narrow owner-scoped authorization issued **before** exposure.
- No reruns of closed DEVELOPMENT 80/81, no use of P2 reserve, no retrospective post-outcome seed replacement, no promotion of I3 or invented scientific GO.

## Reproduce the non-evidentiary checks

\`\`\`bash
PYTHONPATH=src python -m unittest discover -s tests/i3 -p 'test_stage2_survival_b1_worldspec_audit.py'
PYTHONPATH=src python -m i3.lab.stage2_survival_b1_worldspec_audit
\`\`\`

This **does instantiate 1,500 temporary WorldSpecs and structural validators**, but does not execute a living individual. All outcomes and inferred scientific statuses remain \`NOT_ISSUED\`; only engineering/custody diagnostics may be published.

**Disposition: SYNTHETIC_F0_WORLDSPEC_PREFLIGHT / NO BIOLOGICAL SURVIVAL RESULT / SCIENTIFIC ADMISSION STILL LOCKED.**
