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
- generic causal snapshot manager with the four normative life snapshot types, owner-scoped export/restore, hash verification, RNG restoration, and append-only-journal preservation;
- integrated scripted Stage-1 runtime wiring Scheduler, Bus, Journal, RNG streams, scalar technical world, producer buffers and Snapshots;
- exact causal continuation after snapshot restore, including RNG and producer-local sequence state;
- independent full re-execution comparison through a reusable replay verifier;
- autobiographical projection through explicit AutoSegmentCommit references and a versioned allowlist policy;
- separate evaluation trace storage;
- explicit machine-delay non-causality test.

Stage 1 gate status:

- INV-21: green through explicit per-cycle UC accounting, module envelopes, protected capacity, non-carryover, deterministic refusal before overrun, and over-consuming-stub tests;
- INV-22: green through explicit exclusion of machine time from causal state and a delayed-vs-undelayed byte-identical journal test;
- INV-33: green for the Stage-1 scripted substrate through independent re-execution plus snapshot restoration and exact causal continuation;
- INV-35: green through closed ontology admission and deterministic logged rejection of unknown semantic terms;
- reference journal: generated and retained by CI on Python 3.11.

Deferred without blocking the Stage 1 gate:

- full nested payload validation for schemas whose owning cognitive/world components are not implemented yet;
- periodic snapshot scheduling from P-55 until a preregistered campaign value is supplied;
- production campaign RunManifest instantiation, which now has a validated builder but requires real campaign values and equipment reference.

## Stage 2 progress on this branch

Implemented:

- deterministic 32 x 32 grid world with impassable borders and a 300-step day including 100 night steps;
- body state with energy, food, water and integrity, all bounded to [0,100];
- primitive commands for movement, collection, eating, drinking, stone placement, tool crafting, sleep and wait;
- P-52/P-53-driven action costs, body decay/gains, damage, resource quantities and tool recipe;
- water, two berry species, wood, stone, hostile-creature positions, damaging danger zones and explicitly lethal zones;
- shelter formation from exactly four stones;
- deterministic seeded world generation with explicit counts and seeded toxic/nutritious berry identity;
- isolated oracle capability accessible only through the evaluation bench;
- oracle canary isolation checks and a source-level dependency check forbidding oracle/bench dependencies under `src/i0`;
- separate evaluation trace and external death/rollback/block/alert counters;
- deterministic external scenario injection logged before application;
- typed protocols for all five MVP battery situations, with trait scoring deferred to Stage 5;
- lethal checkpoint immediately before every scripted command send;
- lethal-transition detection, rollback, protocol mask and renewed `attempt_ref`;
- campaign/diagnostic safety-block distinction and operator alert after `R_letal_max`;
- autobiographical projection only for non-lethal attempts;
- exact replay of injected scenarios and a full 300-step scripted-agent day;
- Stage 2 reference journal generated and retained by CI on Python 3.11.

Stage 2 gate status:

- INV-02: green for current code boundary through capability denial, `src/i0` dependency scan, and oracle-canary non-leak checks;
- INV-27: green for the current no-learning Stage-2 system; lethal transition, detection, rollback and mask are absent from the autobiographical projection;
- INV-28: green for protocol-mask scope in Stage 2; the mask is cleared after a non-lethal step and exists only in technical Scheduler state;
- INV-29: green through repeated distinct lethal commands, safety block, bench counter and operator alert;
- INV-33: extended through deterministic scenario state and full scripted-day replay;
- INV-39/INV-44/INV-49: exercised by the Stage-2 scripted send/rollback path.

Prepared but not activated as cognition:

- the five battery scenario mechanisms are typed and versioned, but profile scoring and disposable-copy administration remain Stage 5;
- the scripted agent is intentionally not Action Control; Stage 3 will become the sole normative command sender for the individual.

Still requiring preregistration before a scientific campaign:

- concrete P-29, P-37, P-38, P-49 and P-52 to P-54 values;
- campaign world counts, costs, damages and scenario bounds;
- materiality thresholds and battery termination values.

## Stage 3 progress on this branch

Implemented:

- `PrimitiveCommand` promoted to a shared I0/world interface so cognitive code does not depend on Lab internals;
- minimal local symbolic world capture containing only authorized local state, with hidden danger/lethality and oracle canaries excluded;
- deterministic `SymbolicPerception` without noise or learned state;
- immutable Stage-3 safety-fact source, designed to be replaced later by the canonical Causal Model source;
- `ActionControl.verifier_admissibilite` with admissible / inadmissible / indeterminate outcomes;
- the three exact MVP veto categories with policy-version trace;
- protected-integrity check driven by explicit P-37 input;
- protocol-mask check after semantic veto/protected-invariant checks;
- innate adjacent-creature avoidance reflex using one step capture;
- deterministic avoidance geometry documented as reversible TD-S3-01;
- Action Control admission trace emitted before send;
- Action Control as the only Stage-3 dispatcher into the admitted-command execution port;
- vetoed reflex falls through to the permanent `attendre` Stage-3 stub; the veto does not select the replacement;
- lethal reflex rollback resumes in the same world step without replaying the reflex;
- exactly one local perceptual capture per Stage-3 step;
- deterministic Stage-3 replay and CI-retained reference journal.

Stage 3 invariant status:

- INV-12: direct/reflex branch green. Every reflex command links to its trigger and capture. The cognitive option → S_t provenance branch is structurally deferred to Stage 4 because S_t does not yet exist at Stage 3;
- INV-13: green. Reflexes and vetoes never enter competition, and veto never chooses a replacement action;
- INV-45: green for Stage 3 through exactly one local capture per waking step;
- INV-52: green for implemented Stage-3 send paths: admission is journaled before checkpoint/send and vetoed commands are never sent;
- exact replay remains green over the stacked Stage 1/2/3 substrate.

Deliberately not implemented yet:

- S_t, gatekeeper, competition, goals, planner, values, F_cog or learning;
- full cognitive branch of INV-12, which becomes testable at Stage 4;
- Stage-3 safety facts learned from experience: only the immutable initial source exists here, as required before the Causal Model arrives.

## Stage 4 progress on this branch

Implemented:

- frozen causal contracts for GoalProposal, Goal, Contribution, Option, Plan, EvaluationOption and S_t;
- Value and Needs with explicit setpoints, weighted homeostatic deviation D_t, reward r_t, need alerts and goal proposals;
- Goal Manager as sole owner/writer of the active goal, with one-cycle proposal visibility, hysteretic replacement, satisfaction, abandonment counter and refractory state;
- Gatekeeper with the five normative dimensions, fixed Stage-4 weights, f = 1, exact-subject grouping, exact-symbolic novelty stub, safety preemption, hysteresis, bounded queue, emission quota and soft slot-diversity quota;
- immutable S_t publication by its sole owner, including body, active goal, current plan step, normal profile, synthetic budget state and last-action comparison;
- Perception last-known symbolic map and observation contributions, still with zero noise;
- greedy E-0 planner reading only active goal, founding S_t and Perception's map, never world/oracle;
- explicit grounding of planned options in contributions actually retained by the founding S_t;
- bounded live-option registry, permanent `attendre`, accumulators, urgency, leak, thresholds, inertia, residuals, relative-margin tie-break and C_max fallback;
- substitution evidence by primitive action type only; learned value, simulation and intrinsic motivation remain unavailable/non-applicable exactly as Stage 4 requires;
- Action Control ownership of the current cognitive plan step, advancing only after a non-lethal applied command;
- minimal position result comparator using E-0 predicted movement and the next perceptual capture; non-conformance invalidates the current plan and candidate;
- P-43 logical per-cycle budget using the Stage-1 `CycleComputeBudget`, including envelopes and protected capacity;
- minimal F_cog representation as cumulative actually-consumed UC plus last-cycle UC and synthetic budget state, with normalized DC-13 dynamics explicitly deferred to Stage 10/P-39;
- complete cognitive causal state included in lethal checkpoints and restored on rollback while the technical journal remains append-only;
- C_max fallback performed inside phase 4, therefore inside the same budget/F_cog accounting as ordinary decisions;
- direct reflex remains prior to cognition and opens no deliberation;
- deterministic one-day Stage-4 compatibility fixture and retained CI journal.

Stage 4 reference fixture:

- duration: 300 world steps;
- causal journal bytes: 31,021,402;
- golden journal head: `87e2de3c49f07bafa8026ef785e5e50abf38c98314e780b3e2c5107bf26bdac8`;
- minimal F_cog UC counter at day end: 9,551;
- fixture values are software-compatibility values only and are not campaign calibration or preregistration.

Stage 4 invariant status:

- INV-01: green for implemented Stage-4 causal owners through unique owner identifiers and encapsulated single-writer state;
- INV-04: green; published S_t structures are recursively immutable and snapshot through a plain causal representation;
- INV-08: green for implemented producers; goal proposals become visible one cycle later and Planning consumes the active goal/S_t only from the previous cycle;
- INV-09: green for the minimal runtime; deliberation is bounded by C_max and no world transition occurs before decision/fallback send;
- INV-10: green for implemented options; motif_ref is mandatory and stale goal_ref proposals are rejected/pruned;
- INV-11: green for the minimal system; only Goal Manager writes the active goal;
- INV-12: green for both implemented paths: reflex commands trace to trigger/capture; cognitive commands trace to option, founding S_t and explicit grounding contributions retained by that S_t;
- INV-13: remains green from Stage 3; reflexes/veto never enter Competition;
- INV-17: green; engaged option restarts at A = 0 and non-winning alternatives retain rho times their accumulator;
- INV-18: green for Gatekeeper age/expiry because age changes only with t_monde, not with extra cognitive cycles;
- INV-19: green; queue capacity and eviction are deterministic;
- INV-21: green for Stage 4 through per-cycle UC accounting, module envelopes, protected capacity, explicit degradation and a forced planning-overrun test;
- INV-27/INV-28: extended through cognitive rollback: lethal cognitive branches restore complete causal cognition, remain absent from autobiographical projection and resume under protocol mask;
- INV-33: extended through deterministic Stage-4 re-execution and the full-day golden journal;
- INV-41/INV-52: preserved; the exact admitted command object is the one dispatched, after veto/mask and before lethal checkpoint/send.

Minimal stubs that remain intentionally incomplete:

- kappa remains f = 1; verification and reliability learning begin at Stage 8;
- learned Q is `unlearned`, simulator evidence is `unavailable`, m_a is `not_applicable`; richer EvaluationOption production begins in Stages 6, 8, 10 and 11;
- risk/protection remain minimal hand-written safety inputs; causal safety facts arrive at Stage 9;
- Global Modulation remains the fixed `normal` profile until Stage 11;
- F_cog has no normalized fatigue/sleep-pressure dynamics until Stage 10;
- E-0 is deliberately not obstacle-aware; a blocked movement is detected by the comparator and triggers replanning, while the richer model arrives later;
- no memory, learning, simulator, causal model, exploration or consolidation is introduced.

## Stage 6 progress on this branch

Implemented independently from Stage 5, as allowed by Diagram J:

- explicit accessible `SimulationState` containing only perceived/local state, authorized body variables, inventory and observable context;
- inventory propagated through the Perception boundary rather than read directly from `WorldBody` by equipment;
- typed one-step equipment predictions with horizon, confidence and equipment version;
- versioned/hashable offline `EquipmentCorpus` and immutable `EquipmentArtifact`;
- deterministic exact-transition-table baseline trainer with no fallback extrapolation;
- conflicting outcomes for an identical accessible input are rejected explicitly;
- real controlled reference corpus covering movement, blocked movement, resources, tools, shelter, creatures by day/night, sleep and wait;
- budgeted `Simulator` with R_max/H_max bounds, deterministic rollout de-duplication and explicit unavailable/partial outcomes;
- P-46 conjunctive benchmark over overall error, unavailable rate, per-family error, per-horizon error, calibration and systematic bias;
- E-v1, E-v2 and E-v3 are distinct immutable artifacts and each passes the equivalence gate;
- Stage-6 simulated option evaluator computes predicted homeostatic rewards, discounted E_a^sim and bounded tanh evidence;
- Competition consumes typed simulation evidence while preserving the exact Stage-4 substitution path when simulation is unavailable;
- `not_evaluated` freezes accumulator and threshold state and contributes no artificial zero evidence;
- integrated `Stage6Runtime` supplies common-budget E_a^sim inside the six-phase live loop;
- simulator-based multi-step planning replaces greedy E-0 on the Stage-6 path;
- lived prediction errors are emitted as typed causal contributions;
- shelter planning is covered by an acceptance test;
- full 300-step deterministic Stage-6 reference trajectory is retained by CI.

Stage 6 reference fixture:

- duration: 300 world steps;
- causal journal bytes: 32,171,169;
- golden journal head: `1f7a61df76a84a5f3c00b66ee636ec99ca787793775b0a6ef15449db69286e1b`;
- CI green on Python 3.11 and 3.12;
- 203 tests green;
- Stage 1-4 golden references remain byte-identical.

Stage 6 gate status:

- equipment does not import temperament, memory, learned Q, causal model or oracle internals;
- only accessible symbolic state and authorized inventory/body variables enter equipment;
- unseen inputs remain unavailable rather than extrapolated;
- incomplete rollouts never become completed simulated evidence;
- E-v1 -> E-v3 equivalence is explicitly benchmarked;
- live Competition receives simulator evidence only through the typed evaluator;
- deterministic replay remains green over the full Stage-6 reference day.

## Current repository gap

The normative implementation now includes the deterministic substrate, world/body/bench, reflex/control, complete Stage-4 cognition, Stage-5 temperament/copy instrumentation, and Stage-6 equipment/simulator integration. Stage 6 is software-complete. The next implementation dependency is the next stage defined by section 20 of the normative specification; no later cognitive mechanism should be pulled forward merely because the simulator now exists.

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

