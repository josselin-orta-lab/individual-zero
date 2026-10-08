# MVP v1.2.1 implementation map

Status: working implementation document. This file is non-normative.

Normative authority: `docs/architecture/reference/en/mvp-specification-v1.2.1.md`.

If this map conflicts with the normative specification, the specification wins.

## Implementation progress on this branch

Completed in the current branch:

- deterministic causal encoding, SHA-256, deterministic identifiers;
- independent causal RNG streams with complete state snapshot/restore;
- causal run-manifest primitives;
- append-only hash-chained causal journal;
- concrete I0 structural registries for ontology, similarity contract, κ signal families, safety policy, schema compatibility and P-01 to P-58 identifiers;
- explicit construction of a campaign parameter registry only when all 58 values are supplied;
- validated in-memory bus with local producer buffers, canonical phase-1 pouring, deterministic admission/rejection, ontology/schema checks, and journaled rejection reasons;
- deterministic simulated-time scheduler with world-step opening, rollback attempts, exact phases 0 through 5, canonical component order, and step-close count guards;
- generic causal snapshot manager with the four normative life snapshot types, owner-scoped export/restore, hash verification, RNG restoration, and append-only-journal preservation.

Still missing from normative Stage 1:

- full nested payload validation for every schema in 5.2;
- integration of bus + scheduler + snapshots into one scripted Stage-1 runtime;
- autobiographical/evaluation journal views;
- complete replay runner and retained reference journal;
- periodic snapshot frequency wiring (P-55) once a preregistered value is supplied.

## Current repository gap

The existing bootstrap provides a neutral Lab loop, structured events, a deterministic smoke scenario, and a deliberately non-cognitive I0 no-op boundary. It does not yet implement the normative Stage 1 execution substrate: canonical causal serialization, normative deterministic identifiers, independent causal RNG streams with restorable state, a causal run manifest, a hash-chained append-only journal, the six-phase scheduler, the normative bus/contract validator, or complete causal snapshots and replay.

## Functional groups

| Category | Functional group | Normative sections | States owned | Inputs | Outputs | Dependencies | Main tests | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Infrastructure | Deterministic execution foundation | 5.1; 17.1-17.4; 20.3 Stage 1; INV-22, INV-33 | RNG stream registry; causal manifest; journal chain | campaign seed; structural-contract refs; causal events | canonical bytes; deterministic IDs; RNG draws/state; chained journal entries | none | canonical fixtures; stream independence; RNG restore; chain verification/tamper detection; byte-identical journal | 1 |
| Infrastructure | Structural contracts and validation | 4.1-4.4; 5.2; 17.2; INV-35, INV-51 | schema/version registries; loaded structural artifacts | ontology, similarity, signal-family, safety, parameter and schema artifacts | validated immutable contract versions; rejection events | deterministic foundation | unknown term/version/causal-field rejection; artifact hash verification | 2 |
| Infrastructure | In-memory contribution bus | 2.2; 4.3-4.5; DC-11; Stage 1 | subscriptions; request registry; schema versions as assigned in 5.3 | validated contributions and requests | canonical phase buffers; deliveries | structural validation | canonical pour order; deadline/depth rules; invalid admission logged | 3 |
| Infrastructure | Scheduler and six-phase runtime | 3.1-3.7; DC-11; Stage 1; INV-08, INV-09, INV-21, INV-22, INV-45, INV-53 | clock; step/cycle counters; attempt_ref; cycle budgets | world-step control; component phase hooks | ordered phase execution; step/cycle events | deterministic foundation; bus | phase ordering; C_max; frozen world during deliberation; one capture per waking step | 4 |
| Infrastructure | Snapshots, restoration and replay | 17.1-17.8; DC-08, DC-09; Stage 1; INV-33, INV-44, INV-49 | snapshots and version registry | complete causal owner states; RNG states | complete snapshot; restoration; interval replay | deterministic foundation; scheduler | snapshot/restore continuation; journal not rolled back; attempt_ref uniqueness | 5 |
| Infrastructure | World, body and evaluation boundary | 7.1; 18; 19; Stage 2; INV-02, INV-03, INV-27-29 | world/body state; bench metrics/evaluation trace | admitted commands; scenario inputs | transitions; telemetry; oracle-to-bench data only | Stage 1 substrate | physics; oracle isolation; induced death rollback; scenario replay | 6 |
| Minimal cognitive loop | Action-control and reflex loop | 9; DC-12; Stage 3; INV-12, INV-13, INV-39, INV-52 | commands in progress; veto policy application | step capture; option command | admission/refusal; admitted command | world/body; safety contract | reflex priority; veto trace; no command without admission | 7 |
| Minimal cognitive loop | Perception, contributions, gatekeeper and S_t | 6; 4.3; DC-04, DC-11; Stage 4; INV-04, INV-08, INV-18, INV-19 | perception precisions where applicable later; gatekeeper queues/quotas; published S_t versions | one step capture; bus contributions; frozen kappa/profile | observations; selected candidate state; immutable S_t | bus; scheduler | S_t immutability; retention/age; bounded queues; visibility cuts | 8 |
| Minimal cognitive loop | Needs, goals, planning and option competition | 7; 8; DC-01-03, DC-10, DC-15; Stage 4; INV-10, INV-11, INV-14-17, INV-41, INV-42 | active goal; plans; candidate registry; accumulators; engaged option; Q_active later | S_t; body state; service evaluations | proposals; plans; DecisionAdmise | S_t; action control | accumulator lifecycle; tie-break; goal ownership; decision trace | 9 |
| Progressive cognition | Temperament projection | 7.3; Stage 5; INV-30, INV-40 | tau and immutable ParametresTemperament are owned by snapshots/parameters | birth temperament | immutable derived coefficients | structural contracts; minimal loop | no direct tau reads; neutral mapping; hash stability | 10 |
| Progressive cognition | Equipment and simulator | 12; Stage 6 | immutable E models; no mutable module state | accessible simulation state; options | typed predictions | world corpus; minimal loop | budget equivalence; no oracle/temperament input; H4 version separation | 11 |
| Progressive cognition | Memory | 10; Stage 7 | episodes; intentions; indexes | autobiographical view; S_t | recalls; prospective proposals | minimal loop; snapshots | segmentation; recall determinism; access isolation | 12 |
| Progressive cognition | Online learning and calibration | 11; DC-06, DC-15; Stage 8 | Q_active; kappa_active; precision active forms | lived transitions and admissible verifications | next-step Q; next-cycle kappa | equipment; memory | no same-cycle learning effect; independent verification only | 13 |
| Progressive cognition | Causal model and agency | 9.6; 13; DC-05; Stage 9 | contingencies; hypotheses; causal/safety status | command results; comparator evidence | canonical contingencies; safety facts | memory; learning | attribution windows; safety promotion; no simulator correction from safety-only status | 14 |
| Progressive cognition | Sleep and consolidation | 15; DC-13, DC-16; Stage 10 | h candidate/private transaction; consolidated h | frozen batch; active forms after cut | atomic h/rebase commit | causal model; learning | interruption/resume; atomic visibility; no lost post-cut updates | 15 |
| Progressive cognition | Exploration and modulation | 14; 16.4; Stage 11 | exploration counters/progress; modulation profile | S_t; accessible novelty/progress | intrinsic motivations; frozen cycle profile | temperament; reliable alerts | profile freeze; deterministic novelty; exploration coefficient only | 16 |
| Progressive cognition | Metacognition and guardrails | 16; DC-07, DC-14; Stage 12 | F_cog; sleep pressure; health detectors; compute-state publication | UC consumption; verifications; system states | kappa publication; sleep motivation; degraded states | sleep; exploration/modulation | budget ceiling; degraded-mode invariants; campaign vs diagnostic block | 17 |
| Progressive cognition | MVP campaign | 19.5; Stage 13 | bench campaign records only | frozen complete registry; scenarios | metrics; retained journals; analyses | all prior groups | preregistration hash; battery; H1-H6 protocols | 18 |

## Dependency graph

```text
Deterministic execution foundation
  -> Structural contracts and validation
  -> In-memory contribution bus
  -> Scheduler and six-phase runtime
  -> Snapshots, restoration and replay
  -> World, body and evaluation boundary
       -> Action-control and reflex loop
            -> Perception + Gatekeeper + S_t
                 -> Needs + Goals + Planning + Competition
                      -> Temperament projection
                      -> Equipment and simulator
                      -> Memory
                           -> Online learning and calibration
                                -> Causal model and agency
                                     -> Sleep and consolidation
                      -> Exploration and modulation
                           -> Metacognition and guardrails
                                -> MVP campaign
```

Cross-stage prerequisites from section 20 remain authoritative. The graph above only groups implementation work and does not replace Diagram J.

## First autonomous group

The first implementation group is **Deterministic execution foundation**.

Reasons:

1. it is inside normative Stage 1 and has no prerequisite;
2. every later acceptance test depends on stable causal bytes, hashes, identifiers and random streams;
3. it can be unit-tested without a world or cognitive component;
4. it adds no cognitive behavior;
5. it can coexist with the current bootstrap until the normative scheduler replaces that scaffold.

### First-pass scope

Implemented in this pass:

- canonical causal encoding from 17.2;
- SHA-256 helper and deterministic IDs from 5.1/17.2;
- independent `random.Random` streams with normative seed derivation;
- complete RNG state snapshot/restore;
- immutable causal run manifest with required structural-contract references;
- append-only hash-chained causal journal and chain verification.

Deferred to following Stage 1 groups:

- ontology/schema semantic validation;
- contribution bus;
- six-phase scheduler;
- complete causal snapshots;
- technical/autobiographical/evaluation view projection;
- full replay runner.

## Requirement-to-code matrix for the first pass

| Normative requirement | Existing implementation | Missing implementation before this pass | Functional group | Test required |
| --- | --- | --- | --- | --- |
| Canonical causal bytes (17.2) | `json.dumps(sort_keys=True)` in `JsonlSink`, not normative | NFC, binary64 tagging, forbidden unordered sets/non-finite floats, UTF-8 canonical bytes | Deterministic foundation | equivalent mappings encode identically; float fixture; invalid values rejected |
| SHA-256 hash chain (17.4) | none | chain state, genesis hash, append-only entries, verification | Deterministic foundation | chain verifies; mutation is detected |
| Deterministic IDs (5.1, 17.2) | run_id supplied externally | SHA-256 namespace/context ID rule | Deterministic foundation | same context same ID; changed context changes ID |
| Independent RNG streams (17.2) | seed passed to BootstrapI0 but no RNG registry | normative seed derivation and per-source generators | Deterministic foundation | extra draw in A does not shift B |
| RNG state in snapshots (17.2) | none | getstate/setstate registry snapshot | Deterministic foundation | restored continuation exactly matches reference |
| Causal run manifest (17.2) | RunConfig has run_id/seed/cycles only | versions/hashes of required structural contracts and runtime | Deterministic foundation | missing/duplicate contract rejected; manifest hash stable |
| Byte-identical normalized journals (Stage 1) | event dictionaries compare equal in memory | canonical journal byte representation | Deterministic foundation | repeated journal bytes identical |
| Machine time excluded from causality (INV-22) | no machine-time field currently used | explicit separation in new causal journal API | Deterministic foundation | causal bytes contain no implicit wall-clock data |

