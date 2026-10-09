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

## Stage 7 progress on this branch

Implemented:

- `EpisodicMemory` as sole owner of episodes, intentions, recall state and prospective indexes;
- Memory reads only the DC-09 autobiographical projection and has no dependency on the technical journal, oracle or evaluation trace;
- every autobiographical read is logged technically, while access events themselves remain excluded from autobiography;
- extended Stage-7 autobiographical allowlist for perceptible goal, S_t, comparator, episode and intention events without changing the Stage-1 to Stage-6 default policy;
- episode segmentation on active-goal change, lived comparator surprise above P-34, observable zone change and `L_episode`;
- automatic linking of episodes separated by less than `Delta_episode`;
- exact-search Stage-7 recall using recency, importance and symbolic S_t relevance;
- spontaneous recall only on threshold crossing, emitted as an ordinary Memory contribution through the bus and Gatekeeper;
- prospective intentions with time/event/context triggers, one active candidacy per occurrence, immutable base pressure and P-26 deadline-pressure projection owned by Goal Manager;
- read-only wake-deadline index for wake-authorized dated intentions;
- triggered intentions create both an ordinary Memory contribution and a next-cycle `GoalProposal`; Memory never writes the active goal;
- `Request` / `Response` causal contracts and a Bus-owned request registry;
- request depth <= 1, parent budget/deadline inheritance, two-node cycle rejection and repeated-question refusal inside W;
- direct Memory responses for exact `recall_recent` and `episode:<id>` requests;
- pending/closed request statuses published read-only in S_t;
- past-dependent acceptance task: exact episode query is empty before history and delivered after the episode exists;
- lethal cancelled branches remain absent from autobiographical memory;
- non-causal O(1) journal lookup and indexed autobiographical commits remove the quadratic journal scan without changing canonical bytes.

Stage 7 reference fixture:

- duration: 300 world steps;
- causal journal bytes: 34,636,835;
- closed episodes: 298 under the software-reference P-34 values;
- F_cog counter: 9,593 UC;
- golden journal head: `c356fe386c2480e78e485f85815ac93fc90f3b679e5806dcb61b374daee9da77`;
- 238 tests green on Python 3.11 and 3.12;
- Stage 1-6 historical golden behavior remains compatible.

Stage 7 gate status:

- INV-02: extended to Memory, including source-level absence of technical-journal/oracle dependencies;
- INV-20: request depth, cycles, budgets and deadlines covered;
- INV-27: lethal transition/detection/rollback/mask remain outside autobiographical Memory;
- prospective intentions pass through the ordinary attention and Goal Manager paths rather than directly changing goals;
- deterministic replay remains green over the Stage-7 reference trajectory.

## Current repository gap

The normative implementation is closed through **Stage 8 Online Learning**, as verified on `i0/stage8-online-learning-v1.2.1` (PR #17, draft, deliberately not merged). Stage 9 Causal Model remains the next normative development stage; Stage 10 consolidated forms remain outside Stage 8. Stage 8 may consume accessible S_t, experienced transitions and Stage-7 memory interfaces, but must not pull forward Stage-9 causal-model behavior or Stage-10 sleep/consolidation.

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


## Stage 8: Online Learning and active calibration — software-complete

**Normative authority:** `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, especially §§5.3, 8.1, 8.5, 11.1–11.4, 20.3 Stage 8, 21, DC-01, DC-06, DC-15. The EN specification is unchanged.

**Parameters:** P-13 (learned/simulated mixture), P-30 (individual discount), P-31 (TD learning rate and eligibility decay), P-32 (versioned feature projection), P-33 (reliability map confidence classes and finite priors). Perceptual-source precision estimation uses a separately versioned, explicit configuration under §11.2 rather than an undeclared constant.

### Causal state owners and update frontiers

| Owner | Active states exclusively owned | Temporal and snapshot behavior |
| --- | --- | --- |
| Value and Needs | `Q_active`: per-learning-signature linear parameters, update counts, eligibility traces, pending experienced-decision segments | Experience-driven TD is published only after an applied nonlethal transition; no oracle, lethal rollback or premature same-step evaluation. Unknown Q reads do not create state; unlearned is not zero evidence. Complete snapshot/restore. |
| Metacognition and Health | `κ_active`: DC-06 map, confidence buckets, finite prior, counted confirmations/contradictions, pending verification batch, verification IDs and credited independent physical observations | Each deliberation uses the previously frozen published version; canonical integration and atomic phase-5 publication; causal snapshot/restore, no self-verification or oracle. |
| Perception | Active precision per registered source, pending independent verification batch, finite prior-weighted error statistics and credited physical observations | Only Perception mutates its active precision; publish after a nonlethal world-step; causal snapshot/restore and versioned initial assumptions. |

No Stage 8 module mutates consolidated `Q`, consolidated `κ`, consolidated perceptual precision or the future Stage-10 Consolidation transaction.

The **closed, structural DC-06 family registry** is used unchanged. Calibration keys include the equipment/module version, emitting module, contribution type and signal family; confidence is bucketed into the P-33 classes. A strong verification must refer to a later, independent, `monde`-anchored physical consequence/modality; same-channel repetitions, repeated identifiers, duplicate physical observation credits, derived/self-confirmation, oracle, counterfactuals, and rolled-back experiences cannot inflate counters. Each physically independent credit is used at most once per key.

**Decision path:** experienced nonlethal reward → TD update to signature-indexed `Q_active` → typed learned option evaluation combined with available simulator evidence using `n/(n+n0)` → Competition accumulator and normal option selection. Metacognition's `κ_active` is separately consumed read-only through the Gatekeeper reliability factor, including `f × risk` security ordering. Learned, simulated, substitution, unavailable and unlearned evidence remain distinguishable. Legacy Stages 4–7 use their original Gatekeeper behavior when the Stage-8 reliability resolver is not attached. Learned experience is shown in `tests/test_stage8_evidence.py` to change a subsequent Competition winner.

### Verification and gate

- **263 unit tests green on Python 3.11 and 3.12**. Stage-8 tests: `tests/test_stage8_td_values.py`, `tests/test_stage8_kappa.py`, `tests/test_stage8_evidence.py` and `tests/test_stage8_precision.py`, plus all inherited Stage 1–7 suites. Behavioral, provenance, physical-observation deduplication, frozen-cycle, deterministic segment, source-owner and exact snapshot round-trip tests are included.
- Normative invariants tested and/or integrated: **INV-01, INV-03, INV-05, INV-07, INV-16, INV-26, INV-27, INV-33, INV-43 and INV-50**; DC-01, DC-06, DC-15.
- **Reference duration: 300 world steps**. Canonical journal size **35,061,323 bytes**; final SHA-256 chain head **`0a2dc62d4ba51722a96f307fdf6c7427d1aa3b0a8a3c0e21da81bc490eb23cf8`**.
- `Q_active`: **2 populated signatures, 597 updates**. `κ_active`: **1 updated calibration key, final publication version 1498**. `F_cog`: **9,593 UC**.
- **Two complete 300-step runs agree byte-for-byte** in journal bytes and hash, and exactly in `Q_active` and `κ_active` causal state. These checks and a frozen hash/size/state gate are part of CI.
- **Stage 7 historical hash unchanged:** `c356fe386c2480e78e485f85815ac93fc90f3b679e5806dcb61b374daee9da77`.
- Stage 6 reference is the corrected, already Stage-7-validated Stage-6 baseline `1bbd9071a4a7e9385f537a6f43362f34cc4e7f0a6ca301204abf9100ba2012d5`, incorporated through an explicit non-destructive merge of Stage-6 fixes. The older Stage-6 head `1f7a61df76a84a5f3c00b66ee636ec99ca787793775b0a6ef15449db69286e1b` predates those validated Stage-6 fixes; it was not silently substituted by Stage-8 changes.

### Stage-8 measured learning acceptance (post-golden, Lab-only)

The versioned `src/lab/stage8_learning_benchmark.py` now records two **separate, non-cognitive evaluation traces**; `tests/test_stage8_learning_benchmark.py` checks reproducibility and noninterference. This does not alter the individual or historical journals.

- **TD physical learning curve:** 160 nonlethal, observed water-cycle transitions with actual `WorldBody.apply()`, reward computed through Value and Needs, and DC-15 two-decision TD segments. Fixed benchmark configuration `stage8-online-learning-benchmark-v1` uses an inspectable bias-only feature to isolate the TD mechanism. Bench-only RMSE against the return inferred from observed rewards declines from **5.5555555556** at the birth checkpoint to **0.0493605471** at 160 transitions; intermediate measurements at steps 20, 40, 60, 80, 100, 120 and 140 appear in the CI artifact. This demonstrates controlled TD convergence, not a general learning claim.
- **Prequential κ Brier audit:** `Stage8PhysicalCalibrationRecorder` reads reliability *before* each physical verification, uses only observations actually credited in κ, and writes metrics to the separate Lab artifact. In the existing 300-world-step reference there are only **4 credited calibration samples**; first-half Brier **0.25**, second-half Brier **0.25**, neutral-baseline Brier **0.25**. **No decrease is demonstrated.** Four sparse observations with unchanged calibration are insufficient to validate the Stage-8 declining-Brier acceptance criterion.
- **CI:** new `stage8-learning-benchmark` JSON artifact and visibly reported `stage8_brier_gate=not_yet_demonstrated`; 268 tests passed on both Python versions in run 37822162804. Prior Stage 8 golden `0a2dc62d4ba51722a96f307fdf6c7427d1aa3b0a8a3c0e21da81bc490eb23cf8` remains frozen; historical Stage 7 golden remains unchanged.

**Open normative acceptance:** a preregistered independent physical calibration scenario with sufficiently varied correct/incorrect outcomes is still required for an observed decline in Brier. Do not declare Stage 8 empirically gated merely because its deterministic software and learning-curve tests pass. No oracle labels may enter the individual.

### Stage-8 independent physical calibration stress test (accepted)

A separately versioned, preregistered, *Lab-only* stress scenario now exercises the same DC-06 comparator-verification adapter used by the living Stage-8 runtime (no bench/oracle input to cognition). Each of 80 unique physical world-step observations follows the path: predeclared simulator prediction → ActionControl record → nonlethal WorldBody transition → later Perception capture → ActionControl comparison → Metacognition-owned κ_active update. Preverification reliability is recorded exclusively by the Lab. An independent physical observation reference is credited once; the 80 outcomes are not constructed from κ state or tuned to its feedback.

The fixed controlled predictor produces **64 conforming and 16 nonconforming outcomes**. Prequential Brier decreases from **0.17688754800727752** (first 40) to **0.16273764165848797** (last 40), both below the neutral **0.25** reference. The entire protocol is replayed twice exactly and has explicit invariants in `tests/test_stage8_calibration_stress.py`. All **270 tests** passed on Python **3.11** and **3.12**; GitHub Actions run **37823629279**, with the machine-readable `stage8-physical-kappa-calibration` artifact. The original 300-step scenario's inconclusive Brier 0.25 → 0.25 remains documented above, deliberately unmodified.

The calibration probe only confirms the normatively required **declining-Brier software acceptance in this preregistered stress scenario**. It does not establish general calibration across seeds, families, horizons, or the later Stage-13 scientific campaign. Existing Stage-8 reference golden `0a2dc62d4ba51722a96f307fdf6c7427d1aa3b0a8a3c0e21da81bc490eb23cf8` and historical Stage-7 `c356fe386c2480e78e485f85815ac93fc90f3b679e5806dcb61b374daee9da77` are preserved.

**Stage 8 implementation and its controlled acceptance gate are complete.** PR #17 remains draft for human review; no merge and no Stage-9 implementation have occurred.

### Deliberate boundaries

The noiseless reference trajectory produces no independent sensor-precision calibration samples; active precision update, provenance rejection and publication are separately exercised by deterministic tests. Stage 8 does not add Stage-9 Causal Model knowledge/contingencies or Stage-10 sleep/consolidation. P-33 and active-precision coefficients are versioned software-reference parameters, not empirical performance calibration. The normative Stage-13 campaign and inter-version equivalence evidence are not implied by a green software gate.

**Status:** **Stage 8 closed for the normative MVP implementation gate.** Next normative stage: **Stage 9 — Causal Model and agency**, only after review of the Stage-8 PR; no merge to `main` was performed.


## Stage 9 implementation checkpoint — DC-05 safety-state foundation (IN PROGRESS)

Development branch: `i0/stage9-causal-model-agency-v1.2.1`, PR #18 (draft), based on the verified Stage 8 branch. Source of truth: the unchanged English normative v1.2.1 specification.

- The new `CausalModel` is the **sole writer** of canonical contingency/safety-status records; `CanonicalSafetyFacts` is a read-only bridge from published safety status to existing Action Control veto/admissibility. The existing three-category versioned prohibition policy is unchanged.
- Explicit preregistered configuration `P-35: n1, n2` and `P-36: n_sec, m_sec` is required. Initial DC-05 promotion counts **distinct, independently experienced** harmful episodes, rejects repeated physical-observation references, contradictory intervening evidence, oracle, counterfactual, rollback, alternative causes and deliberately induced harm. Incidental distinct no-harm episodes can demote learned safety status; the adapter never demotes innate safety policy facts.
- Statuses are kept **separate on one canonical object**: a fact may become `etabli_pour_securite` without becoming causally `etablie`. Thus it cannot silently correct the Simulator (INV-25). A batch publishes at cycle closure; before closure the read-only adapter sees the old version. Causal snapshot/restore includes pending evidence, deduplication and published state.
- Normative tests in `tests/test_stage9_causal_model.py` cover promotion threshold, no double credit, rejection, contradiction, incidental demotion, veto source and exact snapshot round trip.
- **No Stage-9 full integration/golden yet.** Future work remains: true Causal Model observation and intervention lifecycle (§13.2), comparator attribution and P-47 (§9.6), context-aware safety admissibility and DC-05 episode equivalence, conditional learned simulator corrections only for `etablie` (§12.3), controlled test proposals, full runtime phase-5 publication and replay, INV-25 and behavioral gate. None of these are represented as complete by this checkpoint.

Stage 8 golden and all historical goldens remain frozen. Stage 9 is **not closed**. No merge to `main`.


### Stage 9 checkpoint 2 — runtime integration (IN PROGRESS)

- `src/lab/stage9_runtime.py`: Stage 8 preserved by inheritance, new `CausalModel` included as an additional unique causal snapshot/checkpoint owner. Its published safety-status view is supplied to the existing Action Control through `CanonicalSafetyFacts`. The fixed veto policy itself remains owned by Action Control and unchanged.
- DC-05 pending status updates become visible only at phase-5 publication by the normative scheduler. Each status change has a structured journal event containing fact ID, previous/new status, evidence and episode references, and model version.
- `src/lab/stage9_reference_fixture.py`: versioned Stage-9 reference setup, P-35/P-36 configured explicitly without changing Stage-8 reference configuration.
- `tests/test_stage9_runtime.py`: verifies a single causal owner, exact model snapshot round-trip, and that pending test evidence cannot affect the veto before phase 5 but published `etabli_pour_securite` changes Action Control refusal while the causal status remains `aucun`.
- **Important scope boundary:** this integration test injects *synthetic, typed evidence* directly into a controlled instance to verify the temporal contract. Runtime derivation of independently corroborated safety facts from real world captures, autobiographical episodes and comparator evidence is **NOT** yet implemented. Nor are §13.2 hypothesis lifecycle, §9.6 full agency attribution, §12.3 established-only simulator corrections or the Stage-9 golden.

Stage 9 must not be declared closed until those paths and their behavioral, invariant, replay and CI gates pass.


### Stage 9 checkpoint 3 — P-47 agency comparator (IN PROGRESS)

- New independently testable `AgencyComparator` under Action Control, enabled by `Stage9Runtime` only. `AgencyComparatorConfig` declares a version, per-variable tolerances for all six observable coordinates/body variables, and a bounded observation window (P-47).
- Action Control retains the sole pending command prediction owner, the frozen predicted consequences and the causal snapshot. The Stage-9 comparator consumes only accessible Perception captures, never `WorldBody`, oracle or a simulator ground truth.
- Compatibility with a predicted consequence is `self_compatible`, **not** causal proof. On nonconformity, attribution to an outside factor is allowed only for an independently accessible movement obstacle; all ambiguous mismatches remain `uncertain`. A missing effect after its declared window cannot be attributed retroactively.
- `tests/test_stage9_agency_comparator.py` covers window freshness/closure, conservative attribution, P-47 configuration and compatible candidate retention. Action Control's legacy snapshot serialization remains identical when the Stage-9 comparator is unattached, preserving the golden references for Stages 3–8.
- Remaining: full multi-command attribution and external-cause alternative accounting; lived episode and comparator-to-Causal-Model evidence adapter; complete §13.2 hypothesis/intervention lifecycle and conditional simulator correction. This checkpoint is **not** Stage-9 closure.


### Stage 9 checkpoint 4 — lived autobiographical evidence admission (IN PROGRESS)

- `CausalModel` now retains a causal snapshot of **actually applied, independently goal-motivated food exposure references**. Only an `applied` Action Control execution may create an exposure; a vetoed, rolled-back, lethal or otherwise unexecuted command cannot enter the candidate path.
- At the next world-step boundary, accessible **Perception telemetry** corroborates the integrity observation. At a subsequent **Memory episode closure**, the Causal Model consumes only matching command and successful world-transition event references from the DC-09 autobiographical projection. It has no direct raw-technical-journal or oracle access.
- Candidates for the existing DC-05 `SafetyEvidence` type require an actual `ate` outcome, matching action and effect, the same observed physical integrity, no separately visible creature/zone harm, and distinct closed episode references. The normal phase-5 Causal Model owner publishes any promotion to Action Control after the normative threshold, without changing causal `etablie` status or simulator predictions.
- `tests/test_stage9_lived_evidence.py` tests real-source matching, unavailable ingestion, independently observable alternative harm rejection, distinct closed episodes, and exact unfinished-exposure snapshot/restore.
- **Limited scope:** this is the food/toxicity DC-05 path; zone, nonfood invariant violation, contextual causal alternatives, hypothesis lifecycle, actively generated intervention proposals, and simulator corrections remain unimplemented. The controlled test exposes source-contract correctness, not a full autonomous two-ingestion behavior demonstration. Stage 9 remains OPEN.


### Stage 9 checkpoint 5 — explicit causal inference lifecycle (§13.2, IN PROGRESS)

- `src/i0/modules/causal_lifecycle.py`: typed, provenance-checked observational association, matched hypothesis alternatives, and experienced intervention records. Oracle, rollback and counterfactual inputs are rejected *before* causal admission.
- `CausalModel` remains the single canonical owner of causal and safety statuses. Causal predicates outside the existing **closed veto policy** must be explicitly registered in versioned `CausalModelConfig.causal_predicates`; this does not add a veto category.
- A correlation requires at least P-35 `n1` exposed observations plus an observed, **matched-context** unexposed base rate which is strictly lower. Review requires separately published correlation and independently sourced matched contrasting observations. Independent interventions require a previously published hypothesis and P-35 `n2` successful **distinct contexts** before `etablie`. A failed observed effect demotes `etablie` to `hypothese_causale` and invalidates previous success credit for a later re-establishment.
- Pending inference remains invisible until phase-5 publication, emits typed `causal_inference_status_published` journal events, and belongs to Causal Model snapshot/replay; deterministic sorting and local prepared state avoid partially committed inference on invalid input. Safety status `etabli_pour_securite` remains independent.
- `tests/test_stage9_causal_lifecycle.py` checks phase staging, mismatched base rates, distinct intervention contexts, revocation/re-establishment, causal snapshots and forbidden-origin canaries.
- **Still open:** automatic lived observation/intervention producer through authorized Memory and AgencyComparator interfaces; observational confounder review beyond explicit matched checks; eligible causal test options routed through Exploration/Competition; read-only established-only simulator correction; Stage-9 300-step gate and golden. Typed evidence tests do not themselves prove autonomous causal inference.



### Stage 9 checkpoint 6 — automatic lived observation intake (IN PROGRESS)

Closed, real DC-09 autobiographical food-consumption episodes that have matching applied commands, lived transition effects and next-step Perception telemetry now create both a DC-05 safety evidence record and a **separately typed causal observation** owned by `CausalModel`. Both records share the actual Memory episode and world-transition reference. Preflight validation prevents partial evidence admission when a record is already duplicated or rejected.

The observation is explicitly `cause_present=True`, never an invented control group or an intervention. Without independently lived `cause_present=False` baseline episodes, it **cannot** progress beyond `aucun` under §13.2. An alternative observed creature/zone harm prevents both safety and causal admission. New tests in `tests/test_stage9_lived_evidence.py` enforce these distinctions.

**Still missing:** autonomous independent baseline producer, comparator-to-intervention source with action/episode linkage, explicit alternative-hypothesis review, Exploration/Competition causal test options, established-only simulator corrections and Stage-9 golden. This checkpoint alone is not Stage-9 completion.


### Stage 9 checkpoint 6b — P-35 co-occurrence correctness

Audit revealed that the initial correlation gate counted cause-present exposures as `n1`, including exposures without the effect. The implementation now counts only `cause_present AND effect_present` co-occurrences **in observably matched contexts**, then separately requires a strictly lower matched unexposed base rate. New `tests/test_stage9_cooccurrence_threshold.py` locks down absent effects, unmatched reference contexts and deterministic pending-observation snapshot replay.

This is a normative correction to Stage-9 typed inference; it does not alter Stage-8 code or historic golden references. The autonomous lived observational intake completed in checkpoint 6 supplies only exposure-positive episodes and **cannot invent a negative control group or an intervention**. Stage 9 remains open pending an independent baseline producer, causal test-option lifecycle, and established-only Simulator correction.


### Stage 9 checkpoint 7 — preregistered lived controls (IN PROGRESS)

The Causal Model now supports `CausalModelConfig.food_control_pairs`, a **versioned, explicit, default-empty** registry of food treatments and genuinely different control foods. An actually consumed control food in a closed DC-09 episode can create a `cause_present=False` observation for its preregistered treatment, alongside its own positive-exposure record. This projects the **same observed physical transition and same Memory episode** without manufacturing a counterfactual, independent intervention or extra sample.

Source constraints remain: applied goal-motivated consumption, accessible Perception integrity, matched actual `ate` outcome, no accessible sufficient alternative harm, and a closed episode. P-35 correlation still requires observed cause-effect cooccurrences above the matched lived base rate; no status is promoted merely by recording a control. The default Stage-9 reference contains no pairs and retains its prior behavior. `tests/test_stage9_lived_evidence.py` includes source-identity and registry validation.

**Open:** the complete autonomous control/contrast pipeline, contextual equivalence proof across episodes, generated admissible intervention options, causal attribution from AgencyComparator beyond descriptive evidence, established-only simulator correction, and the Stage-9 golden. This is not Stage-9 closure.


### Stage 9 checkpoint 7 — independent lived food control and snapshot protocol (IN PROGRESS)

- `CausalModelConfig.food_control_pairs` is an explicit, versioned registry of pairs (hypothesized food, actually consumed different food), initially empty. Only a separately **consumed** food in a closed DC-09 episode can supply a cause-absent observational control; both projections preserve the same episode and physical observation identity and never count as separate independent episodes for a single hypothesis.
- No observed cause-absent group is fabricated when the registry is empty. Matched-context and P-35 observed co-occurrence checks remain required before any causal correlation is published. These observations are never interventions or proofs of establishment.
- The exact Causal Model snapshot protocol now includes `n1`, `n2`, `n_sec`, `m_sec`, the causal-predicate registry and the food-control pairs, **in addition to** its version label. Restore refuses a changed protocol even when the human-readable version is reused; the receiving state remains unchanged. Tests: `test_stage9_causal_config_contract.py`.
- The Stage-9 CI at commit `250a4416457744eafe4a30c79abe78ccc07a44b4` must pass before this checkpoint is considered validated. Existing Stage-8 historical goldens remain immutable.

**Stage 9 remains open:** independent causal intervention generation, alternative-control protocol, established-only correction layer and the Stage-9 golden are not complete.


### Stage 9 checkpoint 8 — numeric simulator correction boundary (IN PROGRESS)

- `src/i0/modules/causal_corrections.py` provides a narrowly typed, immutable numerical correction contract for **global-context body variables only**. Non-finite/out-of-range values and unknown variables or contexts are rejected, not estimated. Corrections never mutate frozen Equipment.
- `Simulator` now supports an **optional read-only correction source**, absent by default; the legacy Stage-6/7/8 path is unchanged. The correction layer modifies only explicitly covered next-state components, preserves the frozen Equipment identifier and declared confidence, and reports unresolved conflicts between equally specific rules as explicit `unavailable`, not an arbitrary prediction.
- `tests/test_stage9_causal_corrections.py` tests legacy equivalence, component isolation, conflict handling and unsupported-case refusal using a controlled synthetic established-rule source.
- **Boundary at checkpoint 8:** this initial layer was tested with a synthetic established-rule source only. Its missing connection to the canonical Causal Model is addressed narrowly in checkpoint 9 below. The autonomous intervention-test-option lifecycle and categorical/probabilistic corrections remain unimplemented.

Stage 9 remains **OPEN**; no new Stage-9 reference golden has been frozen and no previous stage was modified for the new optional path.


### Stage 9 checkpoint 9 — canonical correction provenance and read-only integration (IN PROGRESS)

The Stage-9 runtime now attaches **the one existing Causal Model** to Simulator as a read-only `EstablishedCorrectionSource`, with no duplicate mutable state. Earlier Stage-6/7/8 runtimes keep the correction reader unattached and their Equipment/golden baselines unchanged.

The Causal Model owns and snapshots pending and published `LivedNumericOutcome` records. These are created **only** from an applied goal-motivated food command, next-step Perception telemetry, and the matching command/transition references of a *closed* DC-09 Memory episode. Missing ingestion, alternative creature/zone damage, lethal rollback, absent pre-action context or failed corroboration produce no numeric witness. New witnesses publish **only at phase 5** with the rest of causal inference, not during their phase-1 admission.

A correction is exposed only when all of the following hold together:

- The **same canonical contingency** has causal status `etablie`, not merely `etabli_pour_securite`. A causal refutation immediately removes the correction from the read-only view.
- At least P-35 `n2` **distinct intervention contexts** after any revision have published, physically linked AgencyComparator evidence with consistent episode, option, emission/observation times and attribution. An unlinked synthetic intervention or raw comparator success is insufficient.
- A separate, actually lived numeric witness is corroborated by a published comparator's observed physical value and its original option and time identity.
- The complete accessible pre-action `SimulationState` is matched by its **canonical SHA-256 digest** in addition to the before-body/position and command target. No interpolation, broad cross-context generalization, oracle input or extra certainty is introduced. Equally specific contradictory values remain `unavailable`.

Structured `causal_prediction_corrections_published` events record only meaningful changes to the published correction set, after the phase-5 transaction. Simulator also reports `corrected_contingency_refs` **only for corrections actually used in a rollout**, and Stage-6/8-style option evaluations preserve those typed refs as causal-model provenance within their simulated evidence, without relabelling them as Q values. The source is empty on the legacy Stages 4–8. The frozen Equipment artifact remains unchanged. The controlled `tests/test_stage9_canonical_corrections.py` exercises the three-source provenance gate, no premature publication, safety/causal-status separation, different inventory context refusal, actual frozen-equipment Simulator integration, exact snapshot/replay and revocation after refutation.

**Still open:** automatic, safely motivated causal test-option generation via Exploration/Competition; full observational alternatives and intervening-cause attribution; robust generalization beyond exact physical state; categorical/probabilistic learned transitions; final Stage-9 300-step/golden CI gate. Typed controlled intervention fixtures do not prove autonomous intervention generation. Stage 9 remains **OPEN** and PR #18 is intentionally draft.

### Stage 9 checkpoint 10 — experimental source integrity and exact software replay (DIAGNOSTICS VERIFIED)

- `src/lab/stage9_registration_chronology.py`: independent commit ancestry audit for a genuine prior registration and later archived held-out report. It pins every descendant `src/` Git tree and `pyproject.toml` blob to the exact original implementation freeze, including intermediate modifications later reverted; verifies unchanged registration bytes, distinct evidence commit and matching archived JSON. Rejects shallow Git history and local Git replacement objects. It is read-only and **never** authorizes scientific acceptance.
- `src/lab/stage9_frozen_worktree.py`: separate, explicit **pre-execution local** check of real source file bytes, executable modes, staged/uncommitted changes, and unexpected source-tree paths or symlinks, including ignored additions. Generated Python caches, external dependencies and the actual execution environment are NOT attested. In CI, a checkout-only self-check uses the currently checked-out HEAD; the scientific protocol must instead use its previously frozen complete commit SHA.
- `src/lab/stage9_reference_replay.py`: independent 300-world-step Stage-9 reexecution, comparison of complete canonical journals and all registered causal-owner state, and retained versioned journal/report artefacts. The software reference diagnostic is **not the Stage-9 scientific Golden**. The prior Stage-8 reference remains unchanged.
- Regression and adversarial test coverage: `tests/test_stage9_registration_chronology.py`, `tests/test_stage9_frozen_worktree.py`, and `tests/test_stage9_reference_replay.py`. The GitHub Actions job on Python 3.11 and 3.12 checks unit/regression behavior; Python 3.12 archives the local checkout diagnostic and extended replay artefacts.

### Stage 9 checkpoint 11 — raw held-out artifact hash custody (PRE-SCIENTIFIC AUDIT)

- `src/lab/stage9_scientific_preregistration.py` checks draft parameters, manifest digests, physical world ID/hash uniqueness, seed disjointness and supported scoring methods. It does not replace prior author approval or an immutable Git seal.
- `src/lab/stage9_scientific_assessment.py` derives provisional causal attribution, null controls and naturally acquired false-rule metrics from each registered world × seed row, independently of claimed aggregate statistics. No empty or reused physical observation denominator is counted as scientific success; no report can self-certify a Golden.
- `src/lab/stage9_heldout_artifact_custody.py` now compares every archived claimed raw journal/replay and causal-state/replay SHA-256 to physical bytes for every registered world × seed run. Its separate index binds to the evidence and registration digests. Missing or altered files, aliased originals and replays, reused paths or inodes, symlinks and path escapes are rejected. It cannot prove that those bytes arose from the claimed individual or physics. Tests use synthetic files only.
- `docs/research/stage9-scientific-preregistration-template.md` documents the read-only checks and all scientific limitations; no author-approved prospective research JSON, independent physical-world/seed custody, actual observed candidate rate or full INV-25 scientific review has been fabricated.

**Stage 9 remains OPEN, PR #18 remains draft and unmerged.** Software replay and code/file integrity alone cannot close Stage-9 acceptance (§20.3). A real author-approved prospective registration, sealed before hold-out outcomes, independently witnessed physical and causal observations, naturally acquired rule candidates (nonzero, independent denominator), the preregistered known-cause and superstition thresholds, and independent scientific review remain necessary. Never label diagnostic hashes or green CI as a scientific Golden.


### Stage 9 checkpoint 12 — independent structural journal custody (SOFTWARE AUDIT)

- `src/lab/stage9_canonical_journal_audit.py` verifies the exact canonical JSON-lines representation of an archived `HashChainedJournal`, including contiguous indices, unique event identifiers, genesis-to-head event hash linkage and no trailing line terminator. It refuses a signed-but-noncanonical file rather than accepting the same nominal events after JSON reformatting.
- A prospective held-out `observation_ref` is structurally traceable only when an archived `world_transition_experienced` event has an earlier `command_experienced` with matching world step and attempt, and both appear in exactly one later `auto_segment_commit`. The separate raw-artifact custody checker now requires this for all known-cause and spontaneous-false-rule rows. It retains the original/replay SHA-256 and byte-exact comparisons, per-run world/seed and hardlink/path safeguards.
- The retrospective raw-artifact index protocol is now `stage9-heldout-raw-artifact-index-v2`. v1 checked hashes but did not independently verify the causal journal chain or physically linked observations. Historical v1 reports are not silently upgraded. Synthetic adversarial fixtures show that re-hashing the evidence and replacing all reported SHA-256 values cannot make a broken chain, nonexistent physical source, duplicate event ID or unattested command pass.
- **Limit:** a valid hash-chained technical journal is not proof that events physically occurred, that the subject's declared Memory episode really closed, or that independent held-out worlds and seeds were used. The oracle and real execution remain externally witnessed; no scientific Golden can be frozen by this software verifier.
