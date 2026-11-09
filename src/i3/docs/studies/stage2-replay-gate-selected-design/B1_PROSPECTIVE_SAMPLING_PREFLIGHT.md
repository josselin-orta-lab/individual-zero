# I3 Survival B1: prospective iid-pair sampling preflight

**9 November 2026 · SOFTWARE-ONLY ALLOCATION CANDIDATE · NO SCIENTIFIC WORLD EVER GENERATED**

This is the next concrete step after the [24/24 engineering witness](B1_ENGINEERING_WITNESS_2026-11-09.md) and the [B1 scientific objective](SURVIVAL_B1_LAUNCH.md). New code: `i3.lab.stage2_survival_b1_sampling`. It does **not** alter the historical DEVELOPMENT 80/81 originals, any policy/brain/World physics, the P2 generator, the consumed owner lift or P1.3.

## 1. Chosen sampling frame, not a proof of independence

The proposed target is the expected GATE−FIXED difference in 400-step horizon survival for a **fresh newborn-G0/world pair** from an *equal-probability three-family F0 mixture*. A pair draws one of `stable`, `depletion`, `pulse` with probability 1/3 and is proposed to draw a fresh World seed, a fresh G0 genome seed and a fresh life seed. The two policy arms *within that pair* use precisely the same frozen WorldSpec, newborn genome and life seed. Neither policy modifies the organism's survival priorities, and the outcome comparison is across **complete policies**, not a causal isolation of the replay-selection mechanism.

The independent observational unit is the **whole matched pair**, not either arm individually, a replay event, a sleep step, or a world containing many founders. The analysis will not claim transfer to a fourth unknown ecological family.

The pure metadata scheduler uses HMAC-SHA256 domain-separated by `family`, `world`, `genome` and `life`, keyed by a **prospectively witnessed, 256-bit random seed**. It avoids modulo-three family bias through byte rejection (discard 255, then modulo 3); it does not force precisely equal observed family counts. World, genome and life seed domains occupy disjoint 2^60-wide integer ranges. It forbids duplicates or collisions with known historical, P2 and engineering ranges, and it refuses any manifest differing from a recomputation using the same committed witness.

**Crucial limitation:** uniqueness and cryptographic-looking pseudorandom seeds do **NOT** establish statistically iid World outcomes. The HMAC generator is a reproducibility mechanism, not an external entropy witness, a proof of ecological independence or an authorization for selection. `WorldSpec` structural equality and family-specific correlations have not been examined in this preview. The final scientific protocol must justify the model, entropy source, distinct generated WorldSpecs, Python/World generator determinism, ecological clustering assumptions and out-of-family limitations. The witness must be selected/committed independently before outcomes, not picked from several previews after seeing favorable behavior.

## 2. Why the ordinary P2 generator cannot simply be repurposed

Existing `p2_ecologies.world_for` accepts only its fixed DEVELOPMENT, SELECTION and VALIDATION ranges and explicitly refuses P2 reserve. Its internal `_generate_ecology` calls `worldgen.generate` in **development mode**, whose default guard refuses seeds at or above `1_000_000`. The novel B1 2^60+ proposal seed domains therefore cannot be opened by pointing the existing legacy runner at new index numbers; pretending otherwise would silently bypass declared boundaries.

A **separately reviewed prospective WorldSpec adapter** will be needed. It must preserve the three F0 ecological mechanisms and deterministic WorldSpec provenance, call the appropriate base worldgen with explicit `development=False` only for a newly authorized and unconsumed B1 science namespace, and remain fail-closed for engineering/archive/selection/validation/reserve reuse. Do not implement such an executable admission path in this *metadata* slice. The prospective review must compare any adapted WorldSpec against the frozen P2 semantics and full source/world digest witnesses. In particular, no change of physics or world-generation distribution may be hidden behind a different seed range.

## Follow-up: synthetic WorldSpec generation/parity audit (9 November 2026)

A separate [non-evidentiary F0 WorldSpec adapter and structural
collision audit](B1_PROSPECTIVE_WORLDSPEC_PREFLIGHT.md) now uses the
public preview identifiers to instantiate **temporary** initial
WorldSpecs, reproduces frozen P2 mechanisms and verifies canonical
provenance fingerprints *with and without display names*. This is
a subsequent engineering slice, not a revision of this original
metadata-only source; the sampling module itself still
instantiates zero Worlds. It neither executes an individual nor makes
unique seeds into proven independent ecological sampling, and its
structural validator can transiently instantiate a World to check
physical consistency. No biological or admission conclusions follow.

## 3. Capacity preview and research decision, not a preregistration

The preview produces **1,500 paired metadata units** and **3,000 proposed full-policy lives** (maximum **1,200,000 world steps** at horizon 400). These are simply an engineering resource scenario, **NOT** the approved n or independent observations already collected. The deterministic public root `PREVIEW_WITNESS` is labeled **synthetic and NOT a scientific seed**. It must never be moved into a genuine scientific plan. The preview CLI outputs only a structural summary with per-family counts, HMAC witness digest and whole-manifest SHA; it never serializes life outcomes or instantiates a World.

For the currently illustrated 5-percentage-point non-inferiority margin, two existing alternatives remain distinct:

- A conservative bounded Hoeffding guarantee at assumed true effect zero requires **7,198 truly independent units**, far beyond the 1,500-row preview.
- The [one-sided exact conservative paired bound](../../../lab/stage2_exact_paired_survival.py) has finite-sample coverage under iid **pairs** but no agreed minimum powered n. Prior paired-discordance scenarios may make 1,500 plausible under some assumed rates and inadequate under others. The historical 12 correlated DEVELOPMENT 80/81 paired blocks cannot certify those assumptions.

Do not select the loss margin post hoc to fit a feasible compute budget. Before exposure, record independent design review, family sampling frame/weights, acceptable margin, alternative-effect sensitivity, exact confidence analysis, allocated fixed sample size, a budget ceiling, a locked external witness/source index-claim, and an exact-transport full-size engineering rehearsal. The first genuine scientific life requires explicit new scoped permission. The old pilot permission is consumed; P2 reserve remains sealed.

## 4. Reproducible preflight and checks

```bash
PYTHONPATH=src python -m i3.lab.stage2_survival_b1_sampling
PYTHONPATH=src python -m unittest discover -s tests/i3 -p 'test_stage2_survival_b1_sampling.py'
```

The output contains **no** WorldSpecs, genome objects, living individuals or survival results. Tests establish deterministic metadata, one pair identity per ordinal, disjoint seed domains, known allocation non-overlap, no forced ecological balancing, and rejection of duplicate, altered or fabricated approval receipts. The GitHub B1 CI additionally recomputes the full synthetic preview and uploads its **structural-only summary**, never a scientific archive.

**Current disposition:** `SOURCE_SAMPLING_DESIGN_PREVIEWED / IID_NOT_ATTESTED / SCIENTIFIC_WORLD_OPENING_BLOCKED`. This is a falsifiable and auditable next step, not an inference or survival outcome.
