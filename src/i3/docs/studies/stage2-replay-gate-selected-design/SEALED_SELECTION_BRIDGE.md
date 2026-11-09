# Stage 2.1 sealed selection-to-validation preflight (software only)

**9 November 2026. DRAFT ENGINEERING CONTRACT, NO SCIENTIFIC WORLD AUTHORIZED.**
Baseline `main` `411b3e495c24338780acbc6e14d6b8431e50dab9`.
Do not change historical [DEVELOPMENT 80/81](../stage2-replay-gate-development-80-81/RESULTS.md),
the original [selected design](PROTOCOL.md) or the subsequent [v2 inference proposal](PROTOCOL_REVISION_V2.md). The selected eight-population mean-noninferiority design is still **NO_GO** pending independent methodology and owner decision. I3 remains unregistered; P1.3 funded-v2 remains reference.

## Why this preflight exists

The [finite-panel receipt reader](FINITE_PANEL_RECEIPTS.md) checks a complete set of 1,200 reduced cells, but cannot prove which founders really won selection, whether worlds and newborn genomes match the same claimed originals, or whether paid costs were copied from an archived life instead of invented. The new `i3.lab.stage2_sealed_selection_bridge` connects the *existing* `two_phase_panel.load_sealed` archive verifier and `stage0_design.rank_candidates` persistence-only ranker to that finite-panel readout. It never generates a World, creates a life, dispatches a Mind, or issues a scientific verdict.

## Caller pins and exact records

The bridge requires explicit **external expected pins** for each archive:
`source_sha` (40 hex characters), `plan_sha256`, `transport_fingerprint` and `manifest_sha256` (64 hex characters each). They must be supplied by a separate, authenticated custody record. The in-archive `SOURCE_LOCK.json` must match `schema=i3-stage2-1-selected-sealed-preflight/v1`, its exact cohort, count, `no_retry=true` and all four pins. A self-issued lock with matching digests is **not** proof of owner approval or provenance.

The fixed two-phase `MANIFEST.json` must be fully generated, have no failure, and have exactly the expected `life-000.json.gz` through `life-3839.json.gz` (selection) or `life-000.json.gz` through `life-1199.json.gz` (validation) with no extras. The existing sealed loader compares packed and uncompressed SHA-256 and exact embedded identities. This bridge additionally checks source-plan bytes against the caller's `plan_sha256`, exact source-lock metadata, allocation identities, policy labels, per-life world and genome digests, admission-ticket world binding, physical cognitive energy/vigilance settlements and terminal/death/censoring conventions.

## Selection is reconstructed from all originals, never trusted from summaries

For each of the eight F0 populations and both architectures FIXED/GATE, the input **must** contain every candidate-founder/world result: `8 × 40 × 6 × 2 = 3,840` sealed original lives, including losses and deaths. Each source identity binds a cohort, population, ecological family, world index and seed, genome birth seed, life seed, and assigned policy. The ranks are reconstructed separately within each arm by the existing `stage0_design.rank_candidates`: 400-step survivors first, then total lived time, then ascending founder seed. Five distinct selected founders are derived per arm and population. There is no input parameter for overriding, omitting or swapping a favorable selected set. No learned state is inherited.

The code also compares each founder's original genome digest across worlds/arms and each exact world-slot's name and digest across individuals. This checks internal consistency, not identity against an external approved genome or WorldSpec digest list. It cannot independently establish the actual genetic or environmental source implementation. An independent source-locked external witness is still needed.

## Validation remains separate, read-only, and descriptive

Only after reconstructing selection, a separate `validation` archive can be checked for all **1,200** matched (condition, population, validation World, derived selected founder) cells. The exact five control conditions and same-genome pairing follow the frozen candidate identifiers. The source and genome hash checks are reapplied across selection and validation. RANDOM's funded draws, nominal/eligible/actually paid replay counters and frozen 5532/867 mean are checked against full-life receipts before the existing finite-panel reducer receives its 1,200 rows. No absent, duplicate, foreign or outcome-dependent omission is accepted.

The result explicitly reports `MATCHES_CALLER_SUPPLIED_DIGEST_PINS_ONLY`, not independent authentication. A finite panel summary and genetic selection provenance from sealed outcomes are made available, but an independent review of the full prospective study design, World independence, statistical power and margin is still required. All evidence, including adverse null results, must remain sealed.

## What cannot be concluded

- No new scientific World, selection, validation, reserve or historical DEVELOPMENT index is opened by this read-only library. There is no executable scientific runner here.
- Cryptographic agreement against **caller-supplied** expected SHA values is conditional and not an owner authorization, source-code attestation, registry of opened indices, or proof that those pins were registered *before* exposure.
- Even a perfect 3,840+1,200 archive pass is **not** a survival non-inferiority test, power justification, scientific adoption, I3 activation or independent ecological generalization. The original eight-population inferential NO_GO remains.
- The tests use synthetic reduced life dictionaries and miniature locally generated sealed archives; they do not construct scientific Worlds or re-execute the one-shot R0-R4 falsifier.

**Next blocker:** independent custody authority and externally committed source/plan/world/genome pins, together with an adjudicated, appropriately powered prospective design and separate scientific owner permissions, are required before this preflight could ever be used for scientific evidence.

## Runtime-contract correction (9 November 2026, follow-up to PR #1230)

The original first bridge was exercised against hand-written synthetic life records rather than the exact `run_life` schema. It incorrectly expected an `admission_receipt` field on every arm, including FIXED. The engine actually records `admission` on replay-gate arms only, duplicates that receipt in `manifest.experimental_policy.admission` and the top-level experimental policy, and emits no admission for the P1.3 `reference` policy. This defect could reject true sealed archives. The bridge now checks the policy-specific real shape and rejects an invented reference ticket. It also checks exact replay mode, ticket family/index/world seed, manifest ID, source manifest digest, clean Git source identity matched to caller's source pin, complete world snapshot digest, G0 birth-genome reconstruction, declared physical requested/paid/unpaid accounts, and death causes. Synthetic regression fixtures now model those exact schema relationships without opening a World.

**Limits remain:** an in-archive source-file hash manifest can be self-consistent but cannot independently attest the audited Git checkout or a pre-exposure owner authorization. A world snapshot may match its own SHA without independent verification against a fully frozen original world generator; ticket equality is structural, not cryptographic authorization. The bridge must not be called a tamper-proof scientific authenticator. No source-locked selection or validation experiment is authorized, and the 720-life mechanism-first v3 proposal remains an unapproved alternative to the 5,040-life selected design.
