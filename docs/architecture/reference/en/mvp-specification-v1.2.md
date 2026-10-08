# Artificial Individual — Normative MVP Implementation Specification

Version 1.2 · 8 October 2026 · Josselin Orta · intended license CC0 1.0, like the rest of the series.

This document is the single reference for building the MVP in its normative version 1.2. For implementation purposes, it replaces the implementation analysis, its two rounds of responses, and the supplementary decisions of 6 October 2026; it carries forward from technical specification v1 everything that has not been modified since.

**Revision 1.2.** This revision is the final consistency pass of the normative specification. It preserves the v1.1 architecture and corrects the remaining conflicts concerning ownership of S_t, access to temperament, experimental substitution of equipment, option learning signatures, the cadence of F_cog, traceability of direct commands, and contract compatibility. It adds the corresponding invariants and the final audit appendix.

## 0. Document status

### 0.1 Scope

The document describes the MVP software: a simulated individual, its world, its body, the execution substrate, and the experimental bench. It is normative: a team that did not follow the discussions must be able to build, test, and run the system from this document alone.

The consolidated sources are:

| Source | Role |
| --- | --- |
| Revised MVP normative specification v1.1 | immediate and normative source for this v1.2; any decision already integrated there takes precedence over historical formulations |
| Implementation analysis, consolidated revision ("v3"): responses S-01 to S-15, NQ-01 to NQ-18, V-xx decisions of 6 October 2026 | consolidated historical source, used only when it is not superseded by v1.1 or by a DC |
| Technical specification v1 | general architecture, formulas, contracts, protocol, for everything that has not been modified |
| *Architecture of an Artificial Individual*, v2 (doi:10.5281/zenodo.23003276) | reference thesis; no implementation rule is derived directly from it |

### 0.2 Source hierarchy

When two formulations conflict, the applicable rule is the one with the highest rank:

1. final rules explicitly integrated into this v1.2, originating from revised v1.1;
2. supplementary DC-xx decisions in this specification;
3. final V-xx decisions (6 October 2026);
4. NQ-xx decisions (second round);
5. final S-xx responses (first round);
6. resolved DA-xx decisions and Q1 to Q18 decisions from the specification;
7. historical architecture of specification v1;
8. historical I-xx findings, earlier avenues, questions, and pedagogical appendices.

A normative formulation in the body of v1.2 that clarifies or corrects a lower-ranked rule takes precedence over the historical formulation cited as its origin. Historical appendices never take precedence over the normative body.

The body of the document contains only rules currently in force. History, resolved findings, and correspondences with older sources are grouped in Appendix B.

### 0.3 Writing conventions

- **MUST**, **MUST NOT**: verifiable requirement, covered by a test or invariant (section 21).
- **MAY**: permitted behavior, without obligation.
- **REMAINS FROZEN**: value or version that is immutable for the stated duration.
- Every duration carries its unit: `pas` (world step), `cycle` (cognitive cycle), `jour` (simulated day), `UC` (logical compute unit).
- References in brackets point to the origin of a rule: `[S-05.4]`, `[NQ-02]`, `[V-34]`, `[spéc. 5.2]`, `[DC-01]`.
- A **DC-xx** is a supplementary implementation decision added by this document where the sources were insufficient. It applies to the MVP until the author replaces it; all such decisions are collected in section 23.
- Parameters, configuration artifacts, and values that remain to be fixed are never chosen implicitly here: they appear in the registry in section 22 or are explicitly declared structural and versioned. They are preregistered before the first birth of the campaign.

### 0.4 Notation

Several symbols in the sources had two meanings. This table establishes a single notation; Appendix A gives the correspondence with earlier notation.

| Symbol | Meaning | Origin |
| --- | --- | --- |
| a | candidate option; a primitive action is a trivial option | S-06.3 |
| A_a(c) | accumulator level of a at cycle c (written x_a in spec. v1 and in V-34) | spéc. 6.5 |
| e_a(c) | total evidence received by a at cycle c | S-05.1, DC-01 |
| E_a^Q, E_a^sim | extrinsic evidence components: learned value, value of simulated consequences | S-05.1 |
| m_a | intrinsic motivation specific to the option | NQ-03, V-19 |
| R_a | descriptive risk of the option | S-05.3 |
| U_a | safety uncertainty of the option | NQ-07, V-19 |
| s_a(c), s^0, s_a^0 | effective threshold; common base threshold; option base threshold | spéc. 6.5, NQ-06 |
| π(R_a ; τ) | risk penalty | S-05.3 |
| χ(U_a ; τ) | safety-uncertainty penalty (ψ remains reserved for value parameters) | NQ-07 |
| ι, ι_a | inertia bound; inertia applied to a | S-05.4 |
| u(c) | deliberation urgency, common to all candidates | S-05.5 |
| g | accumulation gain, common in the MVP | V-18, DC-01 |
| ℓ, σ, ε | leak, noise amplitude, accumulation-noise draw | spéc. 6.5 |
| ρ | residual factor for non-selected accumulators, 0 < ρ < 1 | S-05.6 |
| C_max | maximum number of cycles in a deliberation | S-05.8 |
| x_t | canonical evaluation state | S-06.1 |
| y_i, y_i^*, ω_i(τ) | body variable, its fixed setpoint in the MVP, its temperament-modulated weight | spéc. 9.5, 7.3 |
| D_t, r_t | weighted deviation from setpoints, homeostatic reward (D(x) in V-17) | spéc. 9.5 |
| Q(x, o_sig) = ψ_o_sig · φ(x) | learned value, linear in features φ | S-06.2, spéc. 8.6 |
| δ_t, z(t), λ_e, η, β | temporal-difference error, eligibility trace, trace decay, learning rate, discounting | spéc. 8.6, NQ-05 |
| P(m), f(m) | priority of a contribution at the gatekeeper; effective reliability | spéc. 5.2 |
| b, n, urg, rsk, val | gatekeeper terms: relevance to the active goal, novelty, urgency, risk, value (u, r, and v in spec. v1) | spéc. 5.2 |
| w_i, w_i^0, α_i | gatekeeper weight, base weight, temperament coefficient | spéc. 5.4 |
| κ_(version_E,M,type,famille), conf | calibration map indexed by equipment or module version, module, contribution type, and signal family; declared confidence, with f = κ(conf) | spéc. 4.4, DC-06 |
| K | number of contested S_t slots (K = 4) | Q10 |
| W | S_t recency window, in world steps | V-36 |
| Δ_hyst, s_sec | replacement hysteresis; safety-preemption threshold | S-07.2, S-07.3 |
| θ = (τ, h), E | identity (temperament, history); equipment | spéc. 1.3 |
| emp_n | chained hash of the n-th journal event (h_n in spec. v1) | spéc. 7.6 |
| F_cog | cognitive fatigue | S-11.2 |
| k_ép, L_ép, Δ_ép | surprise threshold, maximum duration, and episode-linking gap (ρ, L, Δ in spec. v1) | spéc. 7.2 |
| N_τ, N_M, N_R | number of temperaments, worlds, and seeds in the plan (K, M, R in spec. v1) | spéc. 10.6 |

### 0.5 Diagram legend

Each arrow in a diagram carries a code that states its nature; an arrow without a code does not exist in this document.

| Code | Meaning |
| --- | --- |
| [D] | data transmitted or read |
| [E] | event emitted, logged, or used as a trigger |
| [S] | synchronous service call, under budget and deadline |
| [C] | control: command, order, or imposed decision |
| [P] | atomic publication of a new state version |
| [T] | temporal transition: advancement of a step, cycle, or state |

### 0.6 Where to find the answer

| Engineer's question | Section |
| --- | --- |
| What components exist? | 2.1 |
| Which component owns each state? Who reads it, who writes it? | 5.3, diagram K |
| In what order do components execute? | 3.3, 3.4, DC-11 |
| When does a modification become visible? | 3.6 |
| How does a perception become an action? | 8.9, diagram C |
| How do goals, options, plans, and commands interact? | 7.4, 8.1 to 8.3 |
| How do fast learning and consolidated history interact? | 11, 15.6 |
| How do sleep and consolidation work? | 15 |
| How are accidental compute loops prevented? | 3.7, 21 |
| How is exact replay guaranteed? | 17.1 to 17.3 |
| How do safety, vetoes, reflexes, and lethal rollback work? | 9, 18 |
| How are experiments run and verified? | 19 |
| In what order should the software be built? | 20 |
| Which parameters remain to be calibrated? | 22 |
| What remains unspecified? | 26 |

## 1. Fundamental principles

### 1.1 Purpose and postulate

The MVP gives rise to several individuals with the same equipment in a small grid world and measures whether they become distinct, coherent, stable, and recognizable. It tests a postulate: temperament and history are sufficient to make an individual, regardless of the module equipment it receives. It tests neither general intelligence nor consciousness.

An individual is the trajectory of its slow variables θ = (τ, h). Equipment E is used for computation; it is not part of identity.

| Layer | Content | Origin | Carries identity |
| --- | --- | --- | --- |
| Equipment E | pretrained competence modules: world predictors, physical simulator | shared by all individuals, frozen in the MVP, versioned separately (Q2, Q4) | no |
| Temperament τ | reward sensitivity, threat sensitivity, exploration, goal protection, affiliation, each in [-1, 1] | fixed at birth, never learned (Q5) | yes |
| History h | memories, learned values, reliabilities, contingencies, skills, in consolidated form | lived; modified only through consolidation | yes |

### 1.2 Architecture principles

| No. | Principle | Normative consequence |
| --- | --- | --- |
| P1 | Individuality through slow variables | E, τ, and h are separated in code and data; no temperament effect is encoded outside the mapping table (7.3). E remains fixed during an ordinary life; only experimental condition H4 may substitute an equivalent version at a preregistered point, as an external protocol intervention. |
| P2 | Specialization | Each component has a role, an interface, a budget, and states that it alone owns (5.3). |
| P3 | Orchestration by competition | Modules propose, the gatekeeper selects information, option competition decides; no component decides alone. |
| P4 | Limited context | S_t has K contested slots, K = 4 in the MVP (Q10). |
| P5 | Separate timescales | World step, cognitive cycle, and slow time each have their own rules (section 3). |
| P6 | Persistence | Snapshots, resumption, and copies carry complete state; identity is carried by θ, never by S_t. |
| P7 | Simulated embodiment | The simulated body carries needs; compute budget is never a reward (Q12). |
| P8 | Three-tier learning | Online: values, reliabilities, precisions, memories; offline: consolidation; structural: human validation. Each version of E is frozen; version selection changes during a life only in the preregistered H4 experimental intervention. |
| P9 | Traceability | Append-only journal chained by hashes; every command can be traced back to what produced it. |
| P10 | Graceful degradation and human control | Precision decreases before function; stop controls, caps, and validations remain outside the individual's action space. |
| P11 | Epistemic boundary | Neither the oracle nor the bench ever influences an internal state of the individual (section 19). |
| P12 | Determinism | A life replays identically by re-execution (section 17). |

### 1.3 MVP exclusions

- No language model in the equipment: its dispositions would override temperament (Q13).
- Risk-bearing building blocks (pain, isolation, attachment) are specified, disabled, and absent from the MVP (Q15).
- Equipment does not learn during a life; its plasticity belongs to tier 2 (Q4). Its version remains fixed during an ordinary life. The only MVP exception is the E-v1 → E-v2 substitution explicitly preregistered in condition H4: it is an external intervention by the bench, never an adaptation initiated by the individual, and it is logged before application.
- Temperament is neither learned nor modified during a life.
- No memory is rewritten (no reconsolidation in the MVP).
- The MVP runs in Python, in a single process, with an in-memory bus behind the contract (Q16).

### 1.4 Tested hypotheses

| Id | Hypothesis | Control |
| --- | --- | --- |
| H1 | Coherence: a temperament produces coherent traits across situations | same temperament, different seeds |
| H2 | History: with the same temperament, different histories produce distinct individuals | same temperament, different worlds |
| H3 | Stability: trait stability increases with age without reaching 1 | young versus old individuals |
| H4 | Equipment invariance: replacing a module with an equivalent one leaves the individual recognizable | E-v1 → E-v2 substitution under the H4 protocol; temperament permutation serves as an identity-change control |
| H5 | Bifurcation: two copies of the same individual diverge at a measurable rate | copies initially identical at the copy point, then exposed to distinct worlds or seeds |
| H6 | Architecture: the limited gatekeeper and consolidation are necessary for H1 and H3 | ablations |

The postulate is not supported if traits do not exceed the noise control (H1), or if the individual is no longer recognized after replacement of an equivalent module (H4). The thresholds for these two tests are preregistered; a null result is published as such (Q1).

## 2. Architecture overview

### 2.1 Components

Twenty-one components: nineteen within the individual and its substrate, two outside. Each is the sole owner of its states; detailed ownership is in 5.3.

| Component | Layer | Role | Main states owned |
| --- | --- | --- | --- |
| Scheduler and clock | substrate | advances simulated time, opens steps and cycles, fixes phase order, coordinates atomic commits | clock, step and cycle counters, `attempt_ref`, pseudorandom-stream registry |
| Bus and contract | substrate | transports and validates messages | subscriptions, schema versions |
| Journal | substrate | records everything, append-only; exposes three views (17.5) | chained events |
| Snapshots and individual parameters | substrate | holds τ, the immutable temperament projection, the active equipment version, versions of θ and h, and lineage; applies configuration changes authorized by the protocol; takes and restores snapshots | τ, `ParametresTemperament`, `version_E_active`, version registry, snapshots |
| World and body | environment | simulates the grid, creatures, and body; detects lethal transitions | world state, body state |
| Evaluation bench and console | external | measures without being seen, injects scenarios, controls stopping and caps | metrics, profiles, death counters |
| Perception | individual | produces uncertain observations and deviations from predictions | per-entity estimates, active precisions |
| Value and needs | individual | deviations from setpoints, r_t, option value, R_a, U_a, protective status, value learning | Q_active, setpoints, need weights |
| Goal manager | individual | sole component allowed to activate, maintain, replace, or abandon the active goal (NQ-01) | active goal, goal history |
| Global modulation | individual | determines the modulation profile for the cycle (spéc. 3.3, S-02.6) | active profile, confirmation counters |
| Gatekeeper | individual | scores contributions and assembles S_t | queues, quotas, recent history |
| S_t | individual | bounded, versioned, broadcast common state; sole owner of published versions | published versions (immutable) |
| Option competition | individual | candidate registry, accumulation, decision | candidate registry, accumulators, engaged option |
| Action control | individual | reflexes, veto, admissibility, step execution, agency comparator | commands in progress, current step, veto rules |
| Planning | individual | builds and revises option plans | plans, search tree |
| Simulator and equipment | individual | predicts option consequences under budget from active version E; model artifacts are immutable | no mutable state of its own; versioned and frozen E models |
| Memory | individual | episodes, semantic and procedural memory, intentions, recalls | episodes, intentions, indexes |
| Causal model | individual | hypotheses, tests, canonical source of contingencies and their statuses | hypotheses, contingencies |
| Exploration | individual | designates exploration targets, produces m_a for informational options | visit counters, progress |
| Metacognition and health | individual | computes and publishes κ, F_cog, sleep pressure, m_a(dormir), health detectors | κ_active, F_cog, calibration histories |
| Consolidation | individual, offline | builds h_new during sleep on a frozen batch | h, private working state |

### 2.2 Communication channels

| Channel | Content | Rule |
| --- | --- | --- |
| Contribution bus | the six contribution types (4.3) and requests | every message is validated on admission; no module writes into another module's state |
| S_t | version published every cycle | broadcast to all; immutable once published |
| Service calls | option value and evaluation, simulation, admissibility, computation of m_a | synchronous, under budget and deadline; they never modify S_t |
| Direct path | reflexes, veto | acts without passing through S_t, under the rules of section 9 |
| Journal | copy of every event | no component of the individual reads anything from it except the autobiographical view |

The logical channels from specification v1 (events, modulator, slow state, structure) remain logging labels; in the MVP, everything passes through a single in-memory bus (Q16). The κ maps are published on the event channel every cycle (S-08.6).

### 2.3 Diagram A · General architecture

```mermaid
flowchart TB
  subgraph EXT["External to the individual"]
    MONDE["World and body — complete ground truth"]
    ORACLE["Oracle channel"]
    BANC["Evaluation bench and console"]
  end
  subgraph SOCLE["Execution substrate"]
    ORD["Scheduler and clock"]
    BUS["Bus and contract"]
    JOUR["Causal journal"]
    SNAP["Snapshots and individual parameters"]
  end
  subgraph IND["Individual"]
    PER["Perception"]
    subgraph PROD["Contribution producers"]
      VB["Value and needs"]
      GB["Goal manager"]
      PLAN["Planning"]
      MEM["Memory"]
      CAUS["Causal model"]
      EXPL["Exploration"]
      META["Metacognition and health"]
    end
    MOD["Global modulation"]
    POR["Gatekeeper"]
    ST["S_t"]
    COMP["Option competition"]
    CTRL["Action control: reflexes, veto, admissibility"]
    SIM["Simulator and equipment"]
    CONS["Consolidation, offline"]
  end
  MONDE -->|"[D] observations, telemetry"| PER
  PER -->|"[D] contributions"| BUS
  PROD -->|"[D] contributions"| BUS
  BUS -->|"[D] validated contributions"| POR
  MOD -->|"[C] cycle profile"| POR
  META -->|"[P] κ published"| POR
  POR -->|"[P] atomic publication"| ST
  ST -->|"[P] broadcast"| PROD
  ST -->|"[D] read"| COMP
  PLAN -->|"[D] proposed options"| COMP
  COMP -->|"[S] option evaluation"| VB
  VB -->|"[S] simulation"| SIM
  CAUS -->|"[D] established contingencies"| SIM
  COMP -->|"[C] decided option"| CTRL
  VB -->|"[D] goal proposals"| GB
  GB -->|"[D] active goal, fixed slot"| POR
  EXPL -->|"[D] exploration targets"| PLAN
  COMP -->|"[S] m_a for informational options"| EXPL
  COMP -->|"[S] m_a(dormir)"| META
  PLAN -->|"[S] verifier_admissibilite"| CTRL
  CAUS -->|"[D] safety statuses"| CTRL
  CTRL -->|"[D] attributions"| CAUS
  PER -->|"[E] step stimuli"| CTRL
  CTRL -->|"[C] command"| MONDE
  MEM -->|"[D] batch episodes"| CONS
  CONS -->|"[P] h_new at commit"| SNAP
  ORD -->|"[T] steps and cycles"| IND
  IND -->|"[E] events"| JOUR
  MONDE -->|"[D] ground truth"| ORACLE
  ORACLE -->|"[D] ground truth"| BANC
  JOUR -->|"[D] technical view"| BANC
  JOUR -->|"[D] autobiographical view"| MEM
```

The "Individual" frame receives from the world only observations and telemetry, and acts on it only through commands validated by Action Control. Oracle and bench remain outside the frame: no arrow returns from them (section 19).

## 3. Temporal model and scheduler

### 3.1 Timescales

Three clocks, never conflated [V-36]: the **cognitive cycle** paces deliberation; the **world step** paces the world, body, and recency; **slow time** paces episodes, sleep, and consolidation.

| Scale | Definition | What advances | What remains frozen | Bounds and trigger |
| --- | --- | --- | --- | --- |
| World step | unit of simulated time; the world applies a command and advances one step | world, body, clock, age of contributions in W | nothing beyond the step | the scheduler opens and closes each step |
| Cognitive cycle | one pass through the phases in section 3.3 | S_t (one version per cycle), accumulators, κ, published learned values | world, body, world clock | several cycles per step, at most C_max per deliberation [S-02.1] |
| Deliberation | sequence of cycles ending with a decision or C_max fallback | accumulators, u(c) | world and body | one deliberation per waking step [NQ-02]; never spans two steps |
| Recency window W | maximum age of a contribution in S_t | age_W = t_monde_courant − t_monde_production | unchanged by cycles within the same step [V-36] | in world steps |
| Episode | bounded segment of experience (10.3) | content of the current episode | closed episodes | boundaries: goal change, surprise, zone change, duration L_ép |
| Simulated day | 300 steps, including 100 at night (starting values, spéc. 10.1) | temporal context | — | scheduler |
| Sleep | mode of the individual after engagement of option `dormir` | world, body, reduced perception, reflexes, consolidation | ordinary cognition: no cycle, no deliberation [S-10.2] | wake rule (15.3) |
| Consolidation | offline processing during sleep, on a frozen batch | consolidation's private working state | active h until commit [S-10.4] | deterministic slots per sleep step, capacity per period (S-10.6) |

### 3.2 World-step rules

- The world and body MUST advance only at the end of the step, when the step's command is applied to them; during deliberation they remain frozen [S-02.1].
- Every step that **ends normally** applies exactly one command: reflex, step of the decided option, fallback, or `attendre` while awake; `commande_sommeil` or a reflex during sleep (15.4). The only permitted absence of a command is a step that does not end because a safety block or external stop closes or suspends the branch before sending; in that case the world and body do not advance.
- The perceptual capture for the step is produced exactly once when the step opens; during the first cycle, Perception publishes observations derived from that capture without rereading the world. Later cycles in the same step create no new world observation [S-02.2, DC-11].
- Any quantity that depends on world or body evolution is measured in steps: W, stagnation windows, profile confirmations, command-observation windows [S-02.6, S-02.7, S-15.3, V-36].
- Any quantity internal to deliberation is measured in cycles: C_max, u(c), deliberation-request deadlines.

### 3.3 Phases of a cognitive cycle

The phase order is fixed and reproducible [S-02.2]. Placement of each component in the phases is fixed by DC-11.

| Phase | What happens | Reads | Writes |
| --- | --- | --- | --- |
| 0 · Freeze | current version S_t[n], current κ version, cycle profile, and parameters are frozen | S_t[n], κ | cycle profile (Global Modulation, computed from S_t[n]) |
| 1 · Production | each producer reads frozen inputs and writes to its local buffer; on the first cycle only, Perception publishes contributions derived from the single capture of the step; no producer rereads the world or modifies S_t; buffers are poured onto the bus in canonical order at the end of the phase | S_t[n], κ, profile, own state, step capture for Perception | buffers then bus |
| 2 · Selection | the gatekeeper scores available contributions, occupants, and queue, assembles S_t[n+1], and publishes it atomically | contributions, κ, profile | S_t[n+1] |
| 3 · Evaluation | competition establishes valid candidates and assembles their EvaluationOption through service calls | S_t[n+1], registry | cycle EvaluationOption |
| 4 · Accumulation and decision | update accumulators, test thresholds, break ties, check command admissibility and veto | EvaluationOption, accumulators | accumulators, possible decision |
| 5 · Closure | publish the new κ version and learned updates for the cycle; log events | cycle verifications and updates | κ[v+1], active forms, journal |

A contribution produced in response to S_t[n+1] is examined only in the next cycle: S_t is never recursively rebuilt within a single cycle [S-02.2].

### 3.4 Normative pseudocode for the main loop

```text
procédure VIVRE(individu)
  restaurer(instantané_de_naissance)                     # θ, E, world, body, pseudorandom streams
  tant que individu.vie_active :
    t ← t + 1
    attempt_ref ← ORDONNANCEUR.ouvrir_pas(t)              # new technical attempt for the step; journal: debut_pas
    capture ← PERCEPTION.capturer(MONDE.état_local(t), CORPS.télémétrie(t))   # exactly one read of the world per step
    si individu.mode = SOMMEIL :
      PAS_DE_SOMMEIL(t, capture) ; continuer              # section 15.4
    cmd_ref ← CONTRÔLE.réflexe(capture)                  # direct path, no new perception
    si cmd_ref ≠ ∅ :
      admission ← CONTRÔLE.admettre(cmd_ref)             # veto then mask, order from 9.1
      si admission.ok :
        EXÉCUTER_PAS(t, cmd_ref, source = réflexe) ; continuer
      sinon :
        JOURNAL.écrire(reflexe_refuse(admission.raison)) # DC-12: a vetoed reflex triggers deliberation
    DÉLIBÉRER(t)

procédure DÉLIBÉRER(t)
  COMPÉTITION.ouvrir_délibération(t)                     # V-34: A(engaged) ← 0; valid alternatives: retained residual ρ·A;
                                                         #       new: A ← 0; invalid: removed; u ← u(1)
  admise ← POURSUIVRE_DÉLIBÉRATION(t)                    # DecisionAdmise: option_ref?, exact command, context
  si admise = ∅ : retourner                              # possible safety block
  EXÉCUTER_PAS(t, admise.commande, source = décision, decision_ref = admise)

procédure POURSUIVRE_DÉLIBÉRATION(t)                     # also called when resuming after rollback (18.4)
  admise ← ∅
  tant que admise = ∅ et COMPÉTITION.c < C_max :
    COMPÉTITION.c ← COMPÉTITION.c + 1
    admise ← CYCLE_COGNITIF(t, COMPÉTITION.c)            # returns the exact command already prepared and admitted, or ∅
  si admise = ∅ :
    repli ← COMPÉTITION.repli()                          # engaged option if valid, authorized, executable, unmasked;
                                                         # otherwise "attendre"; S-05.8
    cmd ← CONTRÔLE.préparer(repli)
    admission ← CONTRÔLE.admettre(cmd)
    si admission.ok :
      admise ← DecisionAdmise(repli.option_ref?, cmd, S_T.version_courante(), "repli")
    sinon :
      cmd_attendre ← CONTRÔLE.préparer("attendre")
      admission_attendre ← CONTRÔLE.admettre(cmd_attendre)
      si admission_attendre.ok :
        admise ← DecisionAdmise(∅, cmd_attendre, S_T.version_courante(), "attendre")
      sinon :
        BLOCAGE_DE_SÉCURITÉ(t)                          # S-14.5, DC-14
        retourner ∅
  retourner admise                                       # deliberation is not yet closed

procédure CYCLE_COGNITIF(t, c)
  # Phase 0: freeze
  S ← S_T.version_courante() ; K ← MÉTACOGNITION.κ_courant() ; prof ← MODULATION.profil(S)
  # Phase 1: production, canonical order from DC-11; read-only access to S, K, prof
  # On the first cycle, Perception publishes from the step capture; it never rereads the world.
  pour p dans ORDRE_CANONIQUE : p.produire(S, K, prof)
  BUS.verser_tampons_phase1(ordre_canonique)
  # Phase 2: selection
  S_T.publier(PORTIER.sélectionner(bus.contributions_du_cycle(), S, K, prof))   # [P] S_t[n+1]
  # Phase 3: evaluation
  cand ← COMPÉTITION.candidats_valides(S_T.version_courante())   # bounded registry ∪ {attendre}, DC-10
  budget_sim ← COMPÉTITION.budget_simulation_effectif(cand)      # same (R_eff, H_eff) for all evaluated candidates
  pour a dans cand : EV[a] ← COMPÉTITION.assembler_évaluation(a, budget_sim)    # DC-01, DC-07
  # Phase 4: accumulation and decision
  COMPÉTITION.accumuler(EV, c)                                   # `non_evalue`: accumulator frozen this cycle, DC-07
  gagnants ← { a dans cand : EV[a].statut = evalue ∧ A_a ≥ s_a(c) }
  admise ← ∅
  tant que gagnants ≠ ∅ et admise = ∅ :
    a* ← départager(gagnants)                                    # DC-02
    cmd ← CONTRÔLE.préparer(a*)                                  # exact command, current step, freshness check
    admission ← CONTRÔLE.admettre(cmd)                           # veto then mask
    si admission.ok :
      admise ← DecisionAdmise(a*.id, cmd, S_T.version_courante(), "seuil")
    sinon :
      si admission.portee = option :
        COMPÉTITION.invalider(a*)                                # option itself is forbidden or invalid
      sinon :
        PLANIFICATION.marquer_a_reviser(a*.plan_ref, admission.raison)
        COMPÉTITION.suspendre_pour_cycle(a*)                     # option may return after replanning
      gagnants ← gagnants \ {a*}
  # Phase 5: closure
  MÉTACOGNITION.publier_κ() ; publier_mises_à_jour_du_cycle() ; JOURNAL.écrire(fin_cycle)
  retourner admise

procédure EXÉCUTER_PAS(t, cmd, source, decision_ref? = ∅)
  ckpt ← INSTANTANÉS.checkpoint_létal(t, source)        # complete causal state just before sending, journal excluded, deliberation not closed
  JOURNAL.écrire(envoi_commande(cmd, trace(source, decision_ref)))
  transition ← MONDE.appliquer(cmd)                     # world and body advance one step
  si transition.létale :
    ROLLBACK_LÉTAL(ckpt, cmd) ; retour                  # no autobiographical commit for this attempt
  INSTANTANÉS.libérer(ckpt) ; MASQUE.vider() ; R_letal_consecutif ← 0
  si source = décision :
    COMPÉTITION.clore_délibération(decision_ref.option_ref)       # ρ on other candidates, engagement, u(c) reset
    VALEUR_BESOINS.mise_à_jour_TD(segment_clos(t), decision_ref.option_ref)   # DC-15: visible from the next step
  sinon :
    VALEUR_BESOINS.prolonger_segment(t)                 # reflex or sleep step: no immediate update
  JOURNAL.commit_autobiographique(t, attempt_ref)       # projection of validated branch only, DC-09
  ORDONNANCEUR.fermer_pas(t)                            # journal: fin_pas; periodic snapshot if due

procédure REPRENDRE_DÉLIBÉRATION(ckpt)                   # causal state restored, technical journal never restored; attempt_ref already renewed
  si ckpt.source = décision :
    admise ← POURSUIVRE_DÉLIBÉRATION(ckpt.t)            # cycles continue from ckpt.c to C_max
  sinon :                                                # masked reflex or sleep
    individu.mode ← VEILLE ; COMPÉTITION.ouvrir_délibération(ckpt.t)
    admise ← POURSUIVRE_DÉLIBÉRATION(ckpt.t)
  si admise ≠ ∅ :
    EXÉCUTER_PAS(ckpt.t, admise.commande, source = décision, decision_ref = admise)
```

### 3.5 Diagram B · Timeline of a world step

```mermaid
sequenceDiagram
  autonumber
  participant ORD as Scheduler
  participant MON as World and body
  participant PER as Perception
  participant PRO as Producers
  participant POR as Gatekeeper
  participant COM as Competition
  participant CTL as Action control
  ORD->>MON: [T] open step t, world and body frozen
  MON->>PER: [D] local state and telemetry for step t

  PER->>CTL: [E] step stimuli, reflex test
  ORD->>COM: [T] open deliberation
  loop cycles c = 1 to n, with n at most C_max
    ORD->>PRO: [T] cycle c, S_t[n], κ and profile frozen
    PRO->>POR: [D] cycle contributions
    POR->>COM: [P] S_t[n+1] published
    COM->>COM: [S] evaluations, accumulation, threshold test
  end
  COM->>CTL: [C] decided option, or C_max fallback
  CTL->>CTL: [S] admissibility, veto, protocol mask
  Note over CTL,MON: lethal checkpoint taken just before sending, deliberation not closed (18.4)
  CTL->>MON: [C] command for step t
  MON->>ORD: [T] world and body advance, non-lethal transition
  ORD->>COM: [C] close deliberation: ρ, engagement, u(c) reset
  ORD->>PRO: [C] TD update for the closed segment, visible at step t+1 (DC-15)
  ORD->>MON: [T] end step t, open step t+1, observe consequences
```

Running example. The individual is thirsty (water 35, setpoint 60). At step t, deliberation lasts three cycles: in cycle 1, the "water below setpoint" alert enters S_t; in cycle 2, the goal manager has made "drink" the active goal and Planning proposes the option "go to the source and drink"; in cycle 3, that option crosses its threshold. A single command, "north", is sent to the world at the end of the step.

### 3.6 Visibility time of modifications

| Modification | Produced | Visible to | Starting from |
| --- | --- | --- | --- |
| New S_t[n+1] version | phase 2 of cycle n | competition | phase 3 of the same cycle |
| New S_t[n+1] version | phase 2 of cycle n | all other modules | phase 1 of cycle n+1 [S-02.2] |
| Active-goal change | phase 1 of cycle n (goal manager) | gatekeeper (fixed slot), then all | S_t[n+1]; Planning at cycle n+1 |
| Modulation profile | phase 0, computed from S_t[n] | gatekeeper | all of cycle n, unchanged [S-02.6] |
| κ | verifications integrated in phase 5 of cycle n | gatekeeper, competition | cycle n+1 [S-08.6] |
| Learned value Q_active | TD update at the end of step t, when it ends without a lethal transition | competition | first cycle of step t+1 [S-05.1, DC-15] |
| Proposed option | phase 1 of cycle n | candidate registry | phase 3 of the same cycle [DC-10] |
| Command | admitted decision | world | end of the step |
| Consequence of a command | world transition at the end of step t | perception, comparator | opening of step t+1 |
| Contingency status | phase 5 (causal model) | simulator, veto, admissibility | next cycle |
| Closed episode | episode boundary | memory recall | next cycle |
| h_new and rebased active forms | coordinated commit during sleep | all components | first waking cycle after the commit [V-22] |

### 3.7 Feedback-loop cuts

Every loop passes through an explicit temporal cut; none closes within the same cycle.

| Loop | Cut |
| --- | --- |
| profile → gatekeeper weights → S_t → profile | profile computed from S_t[n], frozen during the cycle |
| S_t → competition → command → last action → S_t | write after execution, read at the next step |
| prediction → verification → κ → scoring | κ frozen during scoring for a cycle, new version in the next cycle |
| action → consequence → value → evidence → action | TD update visible at the next step |
| contribution → S_t[n+1] → new contribution | examined in the next cycle, never in the same cycle |
| request → subrequest → request | maximum depth 1, cyclic dependencies forbidden [S-04.5] |
| goal → plan → stagnation → goal | stagnation emits a signal; only the goal manager changes the goal, visible in S_t[n+1] |
| hypothesis → test → result → hypothesis | tests proposed as options, under budget, through competition |
| episodes → consolidation → h → behavior | offline, transactional, published at commit |
| monitoring → quotas → S_t occupancy | quotas applied in the cycle after they are computed |
| death → rollback → deliberation | the lethal transition never enters learning or the autobiographical view |

### 3.8 End of a deliberation

- A deliberation ends as soon as an option crosses its threshold and its command is admitted, or when C_max is reached.
- At C_max with no winner, fallback applies: the engaged option is continued if it remains valid, authorized, executable, and unmasked; otherwise `attendre` is executed. Reflexes, vetoes, and priority paths retain priority over this fallback [S-05.8].
- No threshold is lowered to force a decision; u(c) increases but never creates evidence [S-05.5].
- Every C_max occurrence is logged with the final competition state and the fallback applied.
- C_max fallback is distinct from inertia: inertia acts on the threshold during deliberation; fallback acts afterward [V-34].

## 4. Contracts, messages, and ontology

### 4.1 Ontology

- All modules use one shared ontology, closed during an execution and explicitly versioned [S-03.1]. Any vocabulary change creates a new version; the version used is retained with the execution.
- Concrete MVP categories: individual, water source, berry, stone, wood, creature, shelter, zone, crafted object, or tool. Abstract groupings (resource, structure, external agent) classify these categories without creating a physical entity.
- Every entity has at least a stable identifier, an ontology type, a location or region when that notion makes sense, a state, and the physical or observable properties defined for its type.
- The real state of an entity belongs to the world; what the individual knows about it belongs to its observations and estimates. Confidence, relevance, novelty, value, and urgency are never entity attributes [S-03.1].
- The world instantiates only types from the active version. An entity of unknown type received by the system is a contract violation: it is rejected and logged, never placed in an "unknown" category [S-03.6]. An unknown property of a known entity is uncertainty, not a new type.

**Vocabulary.** Exchanged variables, units, actions, and symbols belong to the same closed, versioned vocabulary [S-03.2]. Each term carries a stable identifier, a category, a type, semantics, an optional unit, and an introduction version. Every measurable quantity has a canonical unit; every conversion is explicit; `pas`, `cycle`, and `jour` are distinct units. A message containing a term absent from the active version is rejected and logged.

**MVP primitive actions** [spéc. 10.1, NQ-15]: `se déplacer` (north, south, east, west), `collecter`, `manger`, `boire`, `poser une pierre`, `fabriquer_outil`, `dormir`, `attendre`. `fabriquer_outil` turns wood and stone from inventory into a tool whose minimum function is to improve collection; its recipe and gain are world parameters (22).

### 4.2 Subjects and similarity

- A **subject** is a canonical, versioned symbolic key built from the ontology: an entity, an entity property, a relation between entities, or a goal [S-03.3]. Each contribution has one main subject; other mentioned objects are secondary references.
- Two contributions concern the same exact subject if their canonical keys are identical. Subject groupings (a property attached to its entity) are used for subscriptions and triggers without changing subject identity.
- A subject is descriptive: it contains no urgency, value, or preference.
- Similarity, used by novelty, relevance, and recall, relies on a deterministic hand-written vector representation defined by family (entities, situations, episodes), with every dimension documented, normalized, and versioned, and absent values represented explicitly [S-03.4]. Symbolic rules determine in advance what may be compared.
- No learned encoder is used in the MVP. A future extension would have to be trained offline on a descriptive corpus, frozen before birth, validated by a substitution test, and retained with the equipment [S-03.5].

### 4.3 Contributions

Every module communicates through contributions: a common envelope, a typed payload, and a bounded summary, the only part admissible into S_t [spéc. 4].

| Type | Required payload | Running example |
| --- | --- | --- |
| observation | entity, attribute, value, uncertainty, channel, anchor | "water source 5 cells north" |
| hypothesis | statement, alternatives, evidence for and against, causal status, proposed test | "the red berry precedes a loss of integrity" |
| alert | condition, severity, reflex already taken, acknowledgment required | "water below setpoint" |
| proposed action | an option proposal (OptionProposee, 5.2) | "go to the source and drink" |
| prediction | variable, horizon, distribution, condition, deadline and verification method | "position after the step: one cell farther north" |
| response | request reference, status, content | "2 stones in inventory" |

```text
Contribution {
  id                    # deterministic in causal state: (emitter, t_monde, cycle, causal_sequence)
  version_schema
  type                  : observation | hypothese | alerte | action_proposee | prediction | reponse
  resume                : bounded short text, only content admissible in S_t
  charge                : typed data according to type
  subject_ref           : main subject; references_secondaires : [subjects]
  confiance             : { conf ∈ [0,1], methode : declaree | echantillonnage | verificateur }
  urgence               : { niveau ∈ [0,1], echeance? : (value, unit) }
  risque                : { niveau ∈ [0,1], irreversible : boolean }
  valeur                : { estimation, cible : but | besoin, incertitude }
  cout                  : { engage_UC }                        # measured, never included in the gatekeeper score [S-07.5]
  provenance            : { individu, module, version_module, equipement?, entrees : [ids], signal_ids : [ids] }
  horodatage            : { t_monde, cycle, t_systeme }        # attempt_ref belongs to JournalEvent, not the cognitive object; t_systeme is outside causality
  validite              : { expire_a : (value, pas), invalide_si? }
  liens                 : { request_ref?, remplace?, fil? }
  degrade               : boolean                              # produced in degraded mode [S-11.5]
  empreinte
}
```

### 4.4 Contract rules

- The schema is validated on admission; every rejection is logged with its reason [spéc. 4.7].
- The summary is capped in number of fields and characters; overflow is truncated with a reference to the detail.
- A contribution without an expiration or invalidation condition is refused.
- An update is performed through `remplace`, never by duplication.
- The schema is versioned. An unknown major version, an unknown semantic term, or an unknown field capable of influencing causality causes a logged rejection. Only an optional field explicitly declared non-causal and ignorable by the compatible contract version MAY be ignored. Two conforming executables must never be able to interpret the same causal message differently.
- A deadline MUST carry its unit (`pas`, `cycle`, or `jour`) [S-02.3].
- **Declared is not believed.** Declared confidence conf is recalibrated into effective reliability f = κ_(version_E,M,type,famille)(conf) by the emitting module's map [spéc. 4.4, Q11].
- Machine time (t_systeme, latency, CPU) has no causal effect; it enters the causal perimeter only if it is actually used, in which case it must be logged so it can be restored on replay [S-01.6, S-11.1].

### 4.5 Requests and responses

- Requests have two emitters: Metacognition, when confidence in an element falls, and a module missing a precondition, such as Planning requesting the number of stones in inventory [spéc. 4.6].
- Each request has a recipient, a budget in UC and cycles, a typed deadline, and a depth. A request without a budget, or invalid under its contract, is **rejected by the validation layer**, which is not a refusal by the module [S-04.4].
- The response is delivered directly to the requester. A response type declared **shareable** may also enter the ordinary gatekeeper path, with neither a guaranteed slot nor priority from being a response [S-04.1, S-04.2].
- After the deadline, the requester applies its fallback rule; a late response is delivered with status `tardive` and treated as new information, never as retroactive satisfaction of the request. A response to a cancelled request is logged without being delivered [S-04.3].
- A module MAY refuse a valid request with a reasoned, coded, versioned refusal; the requester then stops waiting. Refusal, empty response, and absence of a response before the deadline are three distinct statuses [S-04.4].
- A request may trigger subrequests, only up to **depth 1**, using the remaining budget and without exceeding the parent's deadline; cyclic dependencies are forbidden and logged [S-04.5]. The same question asked of the same module during the recency window is refused [spéc. 5.7].

### 4.6 External inputs

Any information originating outside the simulation that can change its execution, including an operator command, a scenario or event injected by the bench, or actually used data from the technical environment, MUST pass through an identified interface and be logged **before** application, with its content, provenance, reception order, and application point in simulated time [S-01.6]. Reception, application, and rejection are three distinct events. During replay, external inputs are reinjected at the same points; internal pseudorandom draws are not external inputs.

## 5. Data model and state ownership

### 5.1 Common rules

- Every identifier is deterministic and reproducible on replay. A persistent cognitive-object identifier derives from its owner and stable causal context; a technical journal-occurrence identifier derives at minimum from `(emitter, t_monde, cycle, attempt_ref, local_sequence)`. `attempt_ref` distinguishes successive branches of the same step after rollback and is never accessible to the individual. No identifier depends on an unlogged source of randomness.
- Every persistent object carries its version and provenance; every reference to a versioned object identifies the targeted version.
- Published objects (versions of S_t, κ, h, and a cycle's EvaluationOption) are immutable.
- Fields followed by `?` are optional. Names retain those from the sources where they exist.

### 5.2 Schemas

**Observation, alert, prediction, hypothesis, and verification.** The first four are typed payloads of contributions; `Verification` is an internal Metacognition object that links a contribution to later evidence and qualifies its admissibility for κ.

```text
Observation { entite_ref, attribut, valeur, incertitude, canal,
              ancrage : monde | derive }            # "monde": taken from the step's local state, without an intermediary (DC-06)
Alerte      { condition, gravite ∈ [0,1], reflexe_pris?, accuse_requis : boolean }
Prediction  { variable, horizon : (value, unit), distribution, condition?,
              echeance_verification : (value, unit), methode_verification,
              statut : en_attente | confirmee | contredite | indeterminee | non_verifiable
                     | contrefactuelle_non_verifiee }                       # S-08.1, S-08.3
Hypothese   { enonce, alternatives : [enonces], pour : [refs], contre : [refs],
              statut_causal : correlation | hypothese_causale | testee | etablie, test_propose? }
Verification { cible_ref, statut : confirmee | contredite | indeterminee | non_verifiable | contrefactuelle_non_verifiee,
               preuve_ref?, famille_signal, qualite_kappa : forte_independante | stabilite_meme_canal | non_recevable,
               raison, t_monde, cycle }
```

**Request and response** [spéc. Appendix B, S-04].

```text
Requete { id, individu, emetteur, destinataire : module | capacite,
          question, contexte : refs S_t, budget : { UC, cycles }, echeance : (value, unit),
          format_attendu, profondeur ∈ {0, 1}, parent_ref?, racine_ref }
Reponse { request_ref, statut : livree | tardive | refus | vide | rejet_validation,
          contenu?, motif_refus?, partageable : boolean, t_monde_production, validite? }
```

**Goals.** Only the Goal Manager creates, modifies, and closes a Goal [NQ-01].

```text
GoalProposal { id, source : valeur_besoins | memoire_prospective, type_but, cible,
               pression_base ∈ [0,1], pression_courante ∈ [0,1], echeance?,
               justification_ref, t_monde, cycle, version_regle }                      # DC-03
Goal { id, type_but, cible, condition_satisfaction, mesure_principale,
       pression_courante, etat : actif | satisfait | remplace | abandonne | invalide,
       interrompu_par? : option_ref,                    # intrinsic option in progress [V-10]
       stagnation : { debut_t, meilleure_mesure, suspendue : boolean },
       t_activation, t_cloture?, motif_cloture?, refractaire_jusqua?, empreinte_contexte_abandon? }
```

**Options, plans, evaluations.**

```text
OptionProposee {                                   # payload of an action_proposee contribution
  option : Option, plan? : Plan, admissibilite_prealable? : admissible | indetermine }   # V-43

Option {                                           # decision unit [S-06.3], completed spéc. Appendix B
  id, version, type : primitive | composee
  signature_apprentissage                            # stable canonical semantic signature, distinct from the instance id
  preconditions : [condition], condition_fin : { succes, echec, invalidation }
  but_ref?                                        # active goal served, if any [V-10]
  motif_ref : { type : but_actif | cible_exploration | test_causal | pression_sommeil | intention | defaut, id }
  plan_ref?                                       # current realization of a composite option
  provenance : planification | competence | habitude | exploration | test_causal | defaut   # V-42
  version_S_t_fondatrice, validite : { expire_a : (valeur, pas), invalide_si? }
  etat : proposee | candidate | engagee | terminee
  issue? : succes | echec | invalidee | remplacee | interrompue }

Plan     { id, option_ref, version, etapes : [PlanStep], but_ref?, budget_utilise : UC,
           statut : valide | a_reviser | abandonne, version_S_t }
PlanStep { index, commande : primitive + parametres, preconditions,
           consequences_predites : [ { variable, valeur_ou_variation, precision } ],
           fenetre_observation : (valeur, pas) }
ResultatPlanification { but_ref?, motif_ref, statut : plan_trouve | non_planifiable_actuellement | incomplet_budget,
                        plan_ref?, contexte_materiel_empreinte, budget_complet : boolean, t_monde, cycle }

EvaluationOption {                                 # V-19: attached to the cycle, never to the option
  option_ref, version_option, cycle, t_monde
  statut             : evalue | non_evalue
  valeur_apprise     : { valeur, statut : appris | non_appris }                       # E_a^Q
  valeur_simulee     : { valeur, statut : calculee | indisponible, deroules, horizon_atteint,
                         budget_effectif : { R_eff, H_eff } }                          # E_a^sim; an incomplete simulation is not used
  motivation_intrinseque : { valeur ∈ [0,1] | non_applicable, producteur }              # m_a
  risque             : valeur ∈ [0,1] | inconnu                                         # R_a
  incertitude_securite : valeur ∈ [0,1]                                                 # U_a
  protection         : boolean                                                          # contextual protective status
  provenance         : { signal_ids : [ids], producteurs : [modules] }
  version            : { regles, modeles } }

DecisionAdmise {
  option_ref?, commande : Commande, version_S_t, origine : seuil | repli | attendre,
  t_monde, cycle, attempt_ref
}
```

**Commands and results** [S-15, spéc. 8.3].

```text
Commande { id, primitive, parametres, origine : option_ref | mecanisme_direct (reflexe),
           plan_ref?, etape_index?, version_S_t,
           consequences_predites (frozen on emission), fenetre_observation : (valeur, pas),
           controle : { admissible, veto?, masque?, portee_refus? : option | plan_ou_etape | protocole | direct }, t_monde_envoi }
ResultatCommande { commande_ref, t_monde_observation,
           effets : [ { variable, prevu, observe, tolerance, statut : conforme | non_conforme | indeterminable } ],
           effets_manquants : [variables], attribution : [ { effet, soi | monde | incertaine, candidates } ] }
ErreurPrediction { type : sensorielle | causale | action | valeur | interoceptive,
           source, cible_modele, valeur, precision, nature : bruit_attendu | changement, t_monde, episode_ref }
```

**Causal and safety knowledge** [NQ-10, NQ-11, V-43].

```text
Contingence { id, version, contexte_application, cause, effet, correction_prediction?,
              statut_causal : correlation | hypothese_causale | testee | etablie,
              statut_securite : aucun | etabli_pour_securite,
              origine : innee | apprise, preuves : { pour : [refs], contre : [refs] } }
```

**Memory** [spéc. Appendix B, S-02.5, NQ-17].

```text
Episode   { id, individu, debut, fin, frontiere : but | ecart | lieu | duree,
            fragments : refs autobiographical view, contexte : { lieu, but, entites, variables },
            corps : { debut, fin }, valeur : cumulative r, liens : [episode_ref],
            statut : non_consolide | consolide }
Intention { id, but, declencheur : evenement | heure : (valeur, unit) | contexte,
            echeance?, pression_base ∈ [0,1], surveillance : strategique | spontanee, cout,
            reveil_autorise : boolean,                                   # NQ-17
            etat : en_attente | declenchee | faite | abandonnee, candidature_active? }
```

**Modulation and S_t** [spéc. 5.4, 6.2, S-02.6].

```text
ProfilModulation { nom : normal | menace | exploration | recuperation,
                   multiplicateurs : { w_b, w_n, w_u, w_r, w_v }, effets_supplementaires?,
                   conditions_entree, conditions_sortie : { hysteresis, confirmation : (valeur, pas) },
                   priorite, version }
EtatGlobal {                                       # one S_t version, immutable once published
  individu, version, cycle, t_monde
  fixes       : { corps, but_actif, etape_plan, profil, budget, derniere_action }
  competitifs : [ Element ≤ K ]                    # including the safety slot
  requetes    : { request_ref → statut }
  diff        : additions, removals and reasons since the previous version }
Element { contribution_ref, resume, P, decomposition, f, t_monde_production, validite, preempte : boolean }
```

**Identity, state, and journal** [spéc. Appendix B, S-01, S-13, V-24, V-25].

```text
Temperament { sensibilite_recompense, sensibilite_menace, exploration, protection_buts, affiliation
              : reals in [-1, 1], graine, version }
ParametresTemperament { version_table, poids_portier, gamma_valeur, beta, coeff_risque, coeff_incertitude,
                        coeff_inertie, poids_besoins, coeff_exploration, empreinte }   # immutable; sole interface for consuming τ
Theta       { individu, lignee, parent?, temperament, version_h, version, date, valide_par }
Equipement  { id, version, modules : [ { nom, empreinte_poids, corpus, graine, competence_mesuree } ],
              plastique : non }
VersionEtat { objet : h | Q | κ | precisions | ontologie | schema | E | politique_securite,
              version, version_source?, lot_ref?, coupure_ref?, consolidation_ref?, t_commit }
Snapshot    { id, type : naissance | periodique | checkpoint_letal | copie, individu,
              t_monde, cycle, attempt_ref?, etat_causal_complet, etat_scenario_causal?,
              versions : [VersionEtat], empreinte }                                            # DC-08
CheckpointConsolidation { id, consolidation_ref, lot_ref, version_source_h, curseur,
                          dernier_point_valide, etat_prive }                               # private, outside Snapshot
JournalEvent { n, t_monde?, cycle?, attempt_ref?, individu?, type, charge,
               provenance : [ids], emp_prec, emp }                                       # every physical occurrence lives in the technical trace
AutoSegmentCommit { t_monde, attempt_ref, event_refs : [ids], version_filtre }            # autobiographical projection of a validated step
ProfilTraits { individu, age, version_batterie,
               scores : { patience, prise_de_risque, exploration, reaction_menace, perseverance },
               intervalles_confiance }
```

### 5.3 State ownership

Every mutable state has exactly one owner, the only component authorized to write it. Other components read it through S_t, a service call, or a published version.

| State | Owner | Producers | Readers | Cadence | Unit | Form | Persistence | Snapshot | Journal | Autobiographical view | On replay |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| active goal | Goal Manager | proposals: Value and Needs, prospective memory; signals: stagnation, events | all, through the fixed S_t slot; gatekeeper (b); Planning | every cycle | cycle | active | life | yes | yes | yes | recomputed |
| S_t versions | S_t | Gatekeeper (candidate content); fixed content supplied by its owners | all | every cycle | cycle | published, immutable | life, in the journal | current version | every version | yes | reconstructed exactly |
| gatekeeper queues | Gatekeeper | contributions | gatekeeper | every cycle | age in steps | active | life | yes | admissions, evictions | no | recomputed |
| quotas and habituation | Gatekeeper | gatekeeper | gatekeeper | every cycle | steps | active | life | yes | yes | no | recomputed |
| modulation profile | Global Modulation | Global Modulation | gatekeeper, S_t | phase 0 | cycle; confirmation in steps | active | life | yes | transitions | yes | recomputed |
| candidate registry | Competition | option producers | competition, control | every cycle | cycle | active, bounded by N_options_max excluding `attendre` | life | yes | yes | yes | recomputed |
| accumulators, u(c), counter c | Competition | competition | competition | every cycle | cycle | active | deliberation | yes | yes | no | recomputed |
| engaged option | Competition | competition | control, Planning, Goal Manager | at every decision | step | active | until closure | yes | yes | yes | recomputed |
| EvaluationOption | Competition (assembly) | Value and Needs, Exploration, Metacognition and Health | competition | every cycle | cycle | published, immutable | cycle | no | yes | no | recomputed |
| current plan | Planning | Planning | control, simulator, competition | on trigger [S-02.4] | step | active | until abandonment | yes | yes | yes | recomputed |
| current step, commands in progress | Action Control | control | S_t (plan step), comparator | every step | step | active | until the end of the step | yes | yes | yes, except cancelled segments | recomputed |
| attributions | Control (comparator) | comparator | causal model, values, Metacognition | at the close of each window | step | active | life | yes | yes | yes | recomputed |
| Q_active | Value and Needs | TD learning | competition (through evaluation) | at every decision | step | active | life | yes | yes | yes | recomputed |
| consolidated Q | Consolidation (in h) | consolidation | Value and Needs (rebase) | at commit | slow time | consolidated | life | yes | version, differences | yes | recomputed |
| κ_active | Metacognition and Health | verifications | gatekeeper | every cycle | cycle | active | life | yes | every version | yes | recomputed |
| consolidated κ | Consolidation (in h) | consolidation recalibration | Metacognition (rebase) | at commit | slow time | consolidated | life | yes | version | yes | recomputed |
| active precisions | Perception | perception | perception, comparator | every step | step | active | life | yes | yes | yes | recomputed |
| consolidated precisions | Consolidation (in h) | consolidation | Perception (rebase) | at commit | slow time | consolidated | life | yes | version | yes | recomputed |
| contingencies, causal status | Causal Model | causal model; extracted rules (DC-16) | simulator, memory (references) | end of cycle | cycle | unique, canonical | life | yes | yes | yes | recomputed |
| contingencies, safety status | Causal Model (same object) | causal model (DC-05) | control: veto, admissibility | end of cycle | cycle | unique, canonical | life | yes | yes | yes | recomputed |
| hypotheses | Causal Model | causal model | competition (tests), memory | end of episode, night, on event | step | active | life | yes | yes | yes | recomputed |
| veto rules, protected invariants | Action Control | versioned safety policy | control | never during a life | — | fixed | life | yes | version | no | identical |
| episodic memory | Memory | segmentation over the autobiographical view | recall, consolidation | end of episode | step | active | life | yes | yes | yes | recomputed |
| indexes and references of semantic and procedural memories | Memory | consolidation at commit | Planning, competition, recall | at commit | slow time | active index | life | yes | yes | yes | recomputed |
| semantic and procedural content consolidated in h | Consolidation | consolidation | Memory (through references), Planning, competition | at commit | slow time | consolidated | life | yes | version, differences | yes | recomputed |
| intentions | Memory (prospective) | Planning | memory, wake rule | every waking cycle | cycle, typed deadline | active | until closure | yes | yes | yes | recomputed |
| sleep pressure | Metacognition and Health | Metacognition | competition (m_a(dormir)), wake rule | every step | step | active | life | yes | yes | no | recomputed |
| F_cog | Metacognition and Health | consumed UC | sleep pressure, synthetic budget state | every cycle, recovery by step | UC, step | active | life | yes | yes | no | recomputed |
| progress and stagnation windows | Metacognition and Health | detector | Goal Manager | every step | step | active | life | yes | yes | yes | recomputed |
| pending verifications | Metacognition and Health | emitted predictions | Metacognition | at deadline | prediction unit | active | until deadline | yes | yes | no | recomputed |
| attempt_ref | Scheduler | step opening and rollback | technical journal, checkpoints, protocol control | step opening; after rollback | technical attempt | technical | current step | in lethal checkpoint | yes | no | reproduced identically |
| pseudorandom streams | Scheduler (registry) | — | each stream is consumed only by its declared source | at every draw | — | — | life | current state | initial seed | no | restored and replayed |
| cycle UC budgets | Scheduler | configuration | each module | every cycle | UC | — | cycle | yes | consumption | no (only synthetic state is in S_t) | identical |
| request registry | Bus and Contract | emitters | recipients, S_t (statuses) | at every message | cycle or step | active | until closure | yes | yes | yes | recomputed |
| τ | Snapshots and Parameters | birth | mapping table only | never modified | — | fixed | life | yes | at birth | no | identical |
| ParametresTemperament | Snapshots and Parameters | projection of τ by table 7.3 | gatekeeper, Value and Needs, competition, Exploration | birth | — | fixed, immutable | life | yes | version and hash at birth | no | identical |
| version_E_active | Snapshots and Parameters | birth; preregistered external H4 input | Simulator and Equipment; contribution provenance; Metacognition for κ key; bench read-only | birth; H4 step boundary only | step | active configuration | life | yes | each activation before application | no | identical on replay |
| versions of θ and h | Snapshots and Parameters (version registry) | coordinated consolidation commit | all, through active forms | at commit | slow time | version registry | life | yes | yes | no | identical |
| world and body state | World and Body | world | Perception (local), oracle (complete) | every step | step | real | life | yes | yes | no | recomputed |
| protocol mask, R_letal_consecutif | Scheduler (safety protocol) | lethal rollback | control (filter) | at every rollback | step | technical | until validated step | in checkpoint | yes | no | identical |
| death counters, metrics, profiles | Evaluation Bench | bench | bench, operator | continuous | step, day | external | campaign | no (evaluation trace) | evaluation trace | no | recomputed from journal |

### 5.4 Diagram K · Owners of the main states

```mermaid
flowchart LR
  GB["Goal Manager"] -->|"[D] owns"| S1["active goal"]
  STC["S_t"] -->|"[D] owns"| S2["published S_t versions"]
  POR["Gatekeeper"] -->|"[D] owns"| S2B["queues, quotas, habituation"]
  POR -->|"[D] candidate content"| STC
  MODG["Global Modulation"] -->|"[D] owns"| S3["modulation profile"]
  COMP["Competition"] -->|"[D] owns"| S4["candidates, accumulators, engaged option, EvaluationOption"]
  PLAN["Planning"] -->|"[D] owns"| S5["plans"]
  CTRL["Action Control"] -->|"[D] owns"| S6["current step, commands, attributions, veto rules"]
  VB["Value and Needs"] -->|"[D] owns"| S7["Q_active, setpoints, weights"]
  META["Metacognition and Health"] -->|"[D] owns"| S8["κ_active, F_cog, sleep pressure, stagnation"]
  PER["Perception"] -->|"[D] owns"| S9["estimates, active precisions"]
  CAUS["Causal Model"] -->|"[D] owns"| S10["hypotheses, contingencies and statuses"]
  MEM["Memory"] -->|"[D] owns"| S11["episodes, intentions, indexes"]
  CONS["Consolidation"] -->|"[D] owns"| S12["h: consolidated forms"]
  INST["Snapshots and Parameters"] -->|"[D] owns"| S13["τ, ParametresTemperament, version_E_active, versions of θ and h, snapshots"]
  ORD["Scheduler"] -->|"[D] owns"| S14["clock, random streams, budgets, mask"]
  JOUR["Journal"] -->|"[D] owns"| S15["chained events"]
  MON["World and Body"] -->|"[D] owns"| S16["real world and body state"]
  BANC["Evaluation Bench"] -->|"[D] owns"| S17["metrics, profiles, death counters"]
  S12 -->|"[P] rebase at commit"| S7
  S12 -->|"[P] rebase at commit"| S8
  S12 -->|"[P] rebase at commit"| S9
```

## 6. Perception, gatekeeper, and cognitive space S_t

### 6.1 Perception

- Perception converts the world's local state and body telemetry into uncertain observations, signals deviations from predictions as typed errors, and emits threat alerts [spéc. 9.2].
- It reads the local state provided by the world once per step; it never accesses the complete state or the oracle.
- Its own state consists of the current estimate per entity, active precision per channel, and habituation counters. The last known position of each entity serves as the known map.
- An observation taken directly from the step's local state carries anchor `monde`; any observation computed from other contributions carries anchor `derive` (DC-06).
- Perception noise is parameterized and drawn from Perception's own random stream; it is zero in the minimal system at stage 4.
- During sleep, only reduced perception remains active: stimuli capable of triggering a reflex, relevant threats, and critical body changes [S-10.2].

### 6.2 Contents of S_t

S_t is a bounded, versioned structure broadcast to all; it computes nothing and nobody reads it on behalf of others [spéc. 6].

| Zone | Slot | Content | Supplied by |
| --- | --- | --- | --- |
| fixed | body | perceived body variables, deviations from setpoints | Value and Needs |
| fixed | active goal | identifier, target, progress, optional deadline | Goal Manager |
| fixed | plan step | current step of the engaged option, expected observations | Action Control |
| fixed | profile | cycle modulation profile | Global Modulation |
| fixed | budget | synthetic resource state: normal, constrained, or degraded [S-11.6] | Metacognition and Health |
| fixed | last action | predicted consequence, observed deviation, attribution | Action Control (comparator) |
| contested | K elements, including the safety slot | summary, references, score and decomposition, reliability, age, validity | Gatekeeper |

Fixed slots do not compete and do not count toward quotas; the active goal occupies a fixed slot outside the quota [spéc. 5.8]. Every S_t version is a journal event: S_t can be reconstructed exactly at any time. Losing S_t does not lose identity, which is carried by θ.

### 6.3 Gatekeeper pipeline

The gatekeeper is deterministic code. It never chooses an action [spéc. 5].

1. **Admission**: schema validation, presence of validity, module emission quota, marking of content originating from the world. Every rejection is logged.
2. **Validity and recency**: any occupant, queue item, or new item that has lost semantic validity, or whose age_W reaches W, leaves the pool before any scoring [S-07.4, V-36].
3. **Grouping**: deduplicate and merge contributions on the same exact subject; two correlated sources, for example backed by the same equipment module, count only once. A reobservation arising from a new causal event or a new world read remains a fresh contribution even if its subject and descriptive payload are identical to an earlier contribution.
4. **Regime selection**: if the logical cost UC_full of normal scoring for the batch exceeds the ordinary available budget, the entire pass is scored in degraded mode [S-11.4].
5. **Scoring**: the same function and the same parameter snapshot are used for occupants, the queue, and new items [S-07.1].
6. **Safety preemption**, then **selection** of the K slots under hysteresis and quotas.
7. **Queue**: admissible elements not retained enter it, under bounded capacity (DC-04).
8. **Summary**: a summary beyond its limit is truncated with a reference to the details.
9. **Publication**: S_t[n+1] is published atomically; each module receives feedback (retained, queued, rejected, evicted) with the score decomposition.

### 6.4 Priority function

```latex
P(m) = f(m)\,\big[\,w_b\,b(m) + w_n\,n(m) + w_u\,\mathrm{urg}(m) + w_r\,\mathrm{rsk}(m) + w_v\,\mathrm{val}(m)\,\big]
```

| Term | Measure | Calculation |
| --- | --- | --- |
| f(m) | effective reliability | κ_(version_E,M,type,famille)(conf), map for the module, contribution type, and signal family (11.4, DC-06) |
| b(m) | relevance to the active goal, in the strict sense | explicit links to the active goal, otherwise similarity to its content; an autonomous intrinsic option receives none [V-10] |
| n(m) | novelty | deviation from S_t content and recent history; decreases when content repeats (habituation) |
| urg(m) | contribution urgency | decreasing function of time remaining before the declared deadline |
| rsk(m) | signaled risk | severity × probability × irreversibility of the signaled harm |
| val(m) | value | expected effect on needs and goals, including outside the active goal |

All terms are normalized to [0, 1]. f multiplies the rest: an unreliable alert cannot dominate through urgency alone. Compute cost never enters the score: estimating it before admission would be circular [S-07.5].


**Weights.** Base weights come from `ParametresTemperament`, obtained through table 7.3, then the cycle profile multiplies them [spéc. 5.4, Q6]:

```latex
w_i = w_i^{0}\, e^{\alpha_i\, \tau_{j(i)}} \times \mathrm{mult}_i(\text{profil}), \qquad \tau_j \in [-1, 1]
```

| Temperament dimension | Weight increased when it is high |
| --- | --- |
| threat sensitivity | w_r and w_u |
| exploration | w_n |
| reward sensitivity | w_v |
| goal protection | w_b |
| affiliation | social signal, tier 3 only |

| Profile | Entry condition | Effect on weights (starting multipliers, to calibrate) |
| --- | --- | --- |
| normal | default | none |
| threat | risk alert retained in S_t | w_r and w_u × 1.5; w_n × 0.5 |
| exploration | needs satisfied, boredom detected | w_n × 1.5 |
| recovery | low energy or integrity for several steps | favors recovery-related contributions; reduces the depth of optional processing without affecting essential functions or safety [NQ-08] |

The profile is determined from S_t[n] and remains fixed throughout the cycle. Its exit conditions are explicit: hysteresis on indicators and a confirmation duration in steps; the mere disappearance of an alert or passage of time is insufficient; insufficient information suspends confirmation. Confirmation blocks neither a declared priority transition nor reflexes and veto [S-02.6].

### 6.5 Retention rules

- **Rescoring.** At every cycle, every still-admissible occupant of a contested slot is rescored and competes again with new items, with no score bonus [S-07.1].
- **Hysteresis.** A new item replaces a still-admissible occupant only if P(new) ≥ P(occupant) + Δ_hyst. No minimum residence time is imposed. Δ_hyst is common to all individuals [S-07.2].
- **Safety preemption.** If f(m) × rsk(m) ≥ s_sec, the item gets the safety slot, which counts among the K slots, without passing through hysteresis; if several items cross s_sec, the highest one wins, then canonical order breaks ties. Without preemption, this slot is used for ordinary selection [S-07.3]. An alert below s_sec remains an ordinary contribution. Preemption is distinct from the reflex path.
- **Exit.** An item ceases to be admissible at the first of two deadlines: loss of semantic validity, or age_W ≥ W. Rescoring or retaining an item never resets its age; only a new production based on a new event creates a fresh contribution [S-07.4].
- **Queue.** An evicted item that remains admissible returns to the queue without additional lifetime; the queue is not FIFO; at every cycle, its items compete with new items and occupants [S-07.6]. Capacity, eviction, quotas, and anti-domination: DC-04.
- **Reliability.** Alerts from a module that fail to be confirmed lower that module's reliability, and therefore its scores, through κ.

### 6.6 Normative gatekeeper pseudocode

```text
procédure PORTIER.sélectionner(nouvelles, S, K_κ, prof)
  admises ← { m ∈ nouvelles : schéma_valide(m) ∧ validité_présente(m) ∧ quota_émission_ok(m) }   # logged rejections
  pool ← { e ∈ S.competitifs ∪ FILE : valide(e) ∧ age_W(e) < W } ∪ admises                      # S-07.4, V-36
  journaliser_sorties((S.competitifs ∪ FILE) \ pool)
  pool ← regrouper_par_sujet_exact(pool)
  mode ← dégradé si UC_full(pool) > budget_ordinaire(PORTIER) sinon normal                    # whole pass
  w ← PARAMETRES_TEMPERAMENT.poids_portier × multiplicateurs(prof)
  si mode = normal :
    notes ← pool
  sinon :
    pour m ∈ pool :
      P_pre[m] ← f(m) · (w_b·b_pre(m) + w_n·n_pre(m) + w_u·urg_pre(m) + w_r·rsk_pre(m) + w_v·val_pre(m))
    notes ← N_pré premiers de trier(pool, clé = (P_pre décroissant, ordre_canonique))
  pour m ∈ notes : P[m] ← f(m) · (w_b·b(m) + w_n·n(m) + w_u·urg(m) + w_r·rsk(m) + w_v·val(m))
  pour m ∈ pool \ notes : P[m] ← P_pre[m]                                                     # approximate score, all dimensions retained
  sec ← premier_par( {m ∈ pool : f(m)·rsk_securite(m) ≥ s_sec}, clé = (f·rsk_securite décroissant, ordre_canonique) )
  retenus ← [sec] si sec ≠ ∅ sinon []
  clé_sélection(m) ← P[m] + Δ_hyst si m ∈ S.competitifs sinon P[m]       # hysteresis is used only for comparison
  ordonnes ← trier(pool \ {sec}, clé = (clé_sélection décroissante, nouveau avant occupant à égalité, ordre_canonique))
  # first pass: diversity, q_emp quota per module
  pour m dans ordonnes :
    si |retenus| = K : arrêter
    si quota_emplacements_ok(m.module, retenus) : ajouter m à retenus
  # second pass: never leave a slot empty solely because of the quota
  pour m dans ordonnes :
    si |retenus| = K : arrêter
    si m ∉ retenus : ajouter m à retenus
  FILE ← mettre_en_file(pool \ retenus)                                                     # capacity and eviction: DC-04
  S_nouveau ← EtatGlobal(fixes = emplacements_fixes(propriétaires), competitifs = résumés(retenus), diff)
  retourner S_nouveau                                                                       # atomic publication by S_T
```

### 6.7 Example: A and B in the same cycle

Two individuals with the same equipment, same contributions, and same reliabilities; only their weights differ. Illustrative values, not tuning values [spéc. 5.5].

| Weights | w_b | w_n | w_u | w_r | w_v |
| --- | --- | --- | --- | --- | --- |
| A, threat-sensitive | 1 | 0.5 | 1.5 | 2 | 1 |
| B, explorer | 1 | 2 | 1 | 0.8 | 1 |

| Contribution | f | b | n | urg | rsk | val | P for A | P for B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| m1 threat | 0.80 | 0.3 | 0.7 | 0.8 | 0.6 | 0.5 | 2.84 | 2.78 |
| m2 energy deficit | 0.95 | 0.2 | 0.3 | 0.5 | 0.4 | 0.6 | 2.38 | 2.11 |
| m3 shelter prediction | 0.60 | 0.4 | 0.5 | 0.6 | 0.6 | 0.7 | 2.07 | 1.91 |
| m4 shelter plan | 0.70 | 0.5 | 0.4 | 0.6 | 0.3 | 0.7 | 2.03 | 1.99 |
| m5 unknown zone | 0.90 | 0.1 | 0.9 | 0.1 | 0.1 | 0.4 | 1.17 | 2.23 |

With s_sec = 0.45, m1 takes the safety slot for both individuals (f × rsk = 0.48). With K = 4, A then retains m2, m3, and m4 while m5 waits in the queue; B retains m5, m2, and m4, while shelter prediction m3 waits.

## 7. Value, needs, and goal management

### 7.1 Body, setpoints, and reward

| Variable | Dynamics | Viable range | Starting setpoint |
| --- | --- | --- | --- |
| Energy | decreases with every action, rises during sleep | 0 to 100 | 50, fixed in the MVP |
| Food | decreases slowly and continuously | 0 to 100 | 60 |
| Water | decreases faster than food | 0 to 100 | 60 |
| Integrity | decreases with damage, rises slowly at rest | 0 to 100 | 100, fixed in the MVP |

These are starting values, frozen at preregistration [spéc. 10.3]. Homeostatic reward is the reduction in weighted deviation from setpoints:

```latex
D_t = \sum_i \omega_i(\tau)\,\big|y_i(t) - y_i^{*}(\tau)\big| \qquad r_t = D_t - D_{t+1}
```

- Weights ω_i(τ) depend on the temperament mapping table (7.3). Setpoints y_i^* remain fixed in the MVP; any future modulation of a setpoint by τ would require an explicit extension of that table and of the experimental protocol.
- A protected constraint, such as never dropping below an integrity threshold, remains outside this currency: it is a veto invariant, not a cost [spéc. 9.5, S-14.4].
- F_cog enters neither D nor r_t: thinking is neither rewarded nor punished [NQ-04].
- Compute budget never enters r_t or the value of an option [S-11.6, Q12].

### 7.2 Evaluations produced by Value and Needs

Through a deterministic, versioned consequence-evaluation subservice, Value and Needs produces the following fields of EvaluationOption [V-19]:

| Field | Definition | Rules |
| --- | --- | --- |
| E_a^Q (learned value) | Q_active(x_t, a) | status `non_appris` until the option has received any update; until then it is not available evidence [S-06.5] |
| E_a^sim (simulated value) | value of consequences predicted by the simulator, evaluated in the same currency as Q (DC-01) | computation bounded by a common effective budget `(R_eff, H_eff)` for all candidates evaluated in the cycle; a simulation that does not complete this budget is `indisponible` for that cycle and does not enter evidence; absence of a consequence within the horizon does not prove impossibility [S-05.2, DC-01] |
| R_a (risk) | descriptive estimate of known danger: each distinct adverse consequence receives an elementary risk based on probability, severity, and irreversibility, then these risks are aggregated by a monotone bounded function (DC-01) | independent of temperament; `inconnu` remains distinct from zero [S-05.3] |
| U_a (safety uncertainty) | lack of reliable information about consequences potentially important for safety | an unknown is not a high risk; separate from R_a [NQ-07] |
| protection | contextual status: the option reduces an active threat, preserves a protected variable, or avoids an invariant violation | computed by a shared deterministic, versioned rule; never declared by the option producer [V-19] |

Value and Needs also produces need alerts, reward r_t, and goal proposals derived from needs (7.4).

### 7.3 Temperament mapping table

All innate individuality passes through this table; no temperament effect is coded elsewhere, which makes ablations B1 and B2 clean [spéc. 10.4]. The five dimensions from Q5 are the only ones: there is no "horizon" dimension [NQ-05].

**Normative interface.** At birth, `Instantanés et paramètres d'individu` applies the versioned table to τ once and publishes an immutable `ParametresTemperament` object containing only the authorized derived coefficients: gatekeeper weights, value and discount coefficients, risk and uncertainty coefficients, inertia coefficient, body weights, and exploration coefficient. Consuming components MUST NOT read τ directly. In equations, notation such as `π(R_a ; τ)` is a mathematical shorthand for "π with the coefficient derived from the threat dimension by table 7.3"; it does not authorize direct access to τ in code. Any new temperament dependency requires a new explicit row in this table, a table version, and an ablation test.

| Dimension | Gatekeeper | Competition | Needs, value, exploration |
| --- | --- | --- | --- |
| Reward sensitivity | w_v | weight of the extrinsic evidence component (DC-01) | β_individu, discounting [NQ-05] |
| Threat sensitivity | w_r, w_u | risk penalty π(R_a ; τ); uncertainty penalty χ(U_a ; τ); lower base threshold for protective options [NQ-06, NQ-07] | higher ω_integrity weight; body setpoints remain fixed in the MVP |
| Exploration | w_n | no effect on g [V-18] | m_a module for exploratory options [V-18] |
| Goal protection | w_b | inertia ι_a | none |
| Affiliation | social signal, tier 3 | none | social need, tier 3 |

Curiosity and caution remain separate: the same option may receive both a high m_a and a high uncertainty penalty χ [V-18]. β_individu is stable throughout the life, bounded by 0 < β_min ≤ β_individu ≤ β_max < 1; the minimal system uses β_neutre [S-06.4, NQ-05].

### 7.4 Goal manager

The Goal Manager is the sole owner of the active goal. No other component creates, changes, or abandons a goal [NQ-01].

```text
needs / prospective memory / events → proposals → goal manager → active goal → planning → options → competition
```

**Proposals.** Value and Needs proposes a goal for each need whose pressure reaches p_min; a need's pressure is based on a declared deficit function for that variable, which may be asymmetric. Prospective Memory proposes the goal of a triggered intention; a deadline may deterministically increase its current pressure without changing its base priority. Stagnation, recalls, alerts, and plan failures do not propose a goal: they request reevaluation [NQ-01]. Pressure computation and arbitration are fixed by DC-03.

**Rules.**

- With no active goal, the manager activates the highest-pressure proposal above p_min; canonical order breaks ties.
- An active goal is retained as long as its satisfaction condition has not been reached, it remains valid, and no proposal exceeds it by at least Δ_but (hysteresis).
- It is **satisfied** when its satisfaction condition is reached; **replaced** when an admissible proposal exceeds it by Δ_but; **abandoned** after N_imp findings of `non_planifiable_actuellement` under full budget with no material context change between them; **invalidated** when its target disappears or its context becomes invalid. A refractory period after abandonment is lifted immediately if the context changes materially or if pressure from the corresponding need reaches p_critique.
- Every activation, replacement, and abandonment is deterministic, versioned, and logged.

**Progress and stagnation** [S-02.7, V-10].

- Each goal type defines a satisfaction condition and a principal measure of approach; an active plan may supply intermediate indicators, which count only if they are verified and the plan remains applicable.
- Cognitive activity (cycles, computation, new proposals) is never progress.
- Stagnation is detected when no improvement beyond a declared threshold is observed over a sliding window in steps, defined per goal type. The detector, owned by Metacognition and Health, emits a signal; it changes neither the goal nor the plan.
- An autonomous intrinsic option does not count as progress and does not reset the window. During sleep, the window is suspended, then resumes on waking; during exploration or a causal test while awake, world time continues to count.
- Successive cycles without progress are monitored separately to detect reasoning loops.

**Intrinsic options and references** [V-10].

- An option need not serve the active goal in order to compete, but it MUST carry a `motif_ref`, and a `but_ref` when it serves the active goal.
- An autonomous intrinsic option (`dormir`, explore, test a hypothesis) may win without changing the active goal; when it ends, the active goal again becomes the reference for goal-directed options unless the manager independently changes it.
- Exploration is instrumental (`but_ref` present) or autonomous (`motif_ref = cible_exploration` only).

| Option | but_ref | motif_ref |
| --- | --- | --- |
| collecter_eau | boire | but_actif |
| explorer_zone_nord | absent | cible_exploration_17 |
| dormir | absent | pression_sommeil |

**Intentions.** A triggered intention becomes a candidate for attention through the gatekeeper circuit; it never changes the goal by itself. The manager receives its goal proposal and arbitrates it like the others [S-02.5].

### 7.5 Diagram E · Goal state machine

```mermaid
stateDiagram-v2
  [*] --> Actif : activation by the manager
  Actif --> Actif : intrinsic option in progress, goal retained
  Actif --> Actif : reevaluation after stagnation, goal retained
  Actif --> Satisfait : satisfaction condition reached
  Actif --> Remplace : proposal more pressing by at least Δ_but
  Actif --> Abandonne : N_imp non_planifiable_actuellement findings, context unchanged
  Actif --> Invalide : target disappeared or context invalid
  Satisfait --> [*]
  Remplace --> [*]
  Abandonne --> [*]
  Invalide --> [*]
```

Running example. "Drink" is the active goal when night falls. Sleep pressure makes option `dormir` win (`motif_ref = pression_sommeil`, without `but_ref`): the "drink" goal remains active, its stagnation window is suspended during sleep, and upon waking Planning again proposes options directed toward water.

## 8. Options, planning, and competition

### 8.1 Option, plan, command

| Object | Definition | Rule |
| --- | --- | --- |
| Option | candidate behavior, evaluated and put into competition; common decision unit [S-06.3] | carries preconditions, an end condition, a motif_ref, optionally a but_ref and a plan |
| Plan | current multi-step realization of a composite option | never a separate candidate; its quality enters the option's simulated evidence |
| Command | primitive action sent to the world or body | carries its predicted consequences, frozen on emission, and its observation window |

Each option carries a canonical, versioned `signature_apprentissage` independent of its instance identifier. It encodes only the stable semantics used by Q: primitive and normalized semantic parameters for a primitive option; behavior type, target class, and end condition for a composite or procedural option. It excludes `id`, `plan_ref`, `version_S_t_fondatrice`, timestamps, and ephemeral identifiers. Two instances differing only in their current plan MAY share the same signature; two options whose end condition or action semantics differ MUST NOT share it.

- A primitive action is a trivial option whose plan contains only one command.
- Replanning does not change the option: the option may remain the same while its plan evolves [S-06.3]. Adoption of a revised plan follows DC-17.
- Reflexes, veto, and other direct paths are not options and do not participate in ordinary competition.
- Stabilized habits and compiled skills are **compiled procedural options**: they enter ordinary competition; only innate reflexes keep a direct path [NQ-12].
- Every engaged option retains a trace of its current plan, its steps, and the commands actually executed.

### 8.2 Sources of options

| Source | Options produced | Motive |
| --- | --- | --- |
| Planning | options directed toward the active goal; options built on an exploration target [NQ-18] | but_actif, or cible_exploration |
| Procedural memory | compiled skills and habits | but_actif, or original motive |
| Causal Model | options for testing a hypothesis; Exploration evaluates their intrinsic interest [V-19] | test_causal |
| Prospective memory, through Planning | options that realize a triggered intention | intention |
| Permanent options | `attendre` (fallback and ordinary option); `dormir` | defaut; pression_sommeil |

### 8.3 Path of an option into competition

The sources did not fix the exact path of a proposed option; DC-10 fixes it.

1. The producer constructs the option and, for a composite option, its plan; Planning MAY consult `verifier_admissibilite(option, contexte)` before finalizing it, without copying veto facts [V-43]. An option already known to be inadmissible is not proposed.
2. It emits it in phase 1, in an `action_proposee` contribution.
3. The validation layer rejects any option without `motif_ref`, or whose `but_ref` does not designate the current active goal.
4. In phase 3 of the same cycle, Competition attempts to register it in the candidate registry with A = 0. Registration does not depend on admission of the contribution into S_t; S_t instead influences evidence through evaluation state x_t and simulator inputs. The registry is bounded by N_options_max; at saturation, the engaged option is protected and eviction of other candidates follows DC-10.
5. At every cycle, Competition assembles its EvaluationOption, updates its accumulator, and tests its threshold.
6. A decision is retained only if the command for the current step is admitted: admissibility, veto, protocol mask.
7. An option becomes invalid as soon as its preconditions are false, its but_ref is no longer the active goal, its validity expires, or it itself becomes inadmissible; its accumulator is then removed [S-05.6]. A refusal that applies only to the current step or plan marks that plan `a_reviser` without automatically invalidating the option.

### 8.4 Diagram D · Option state machine

```mermaid
stateDiagram-v2
  [*] --> Proposee : action_proposee contribution
  Proposee --> Rejetee : invalid schema or missing motif_ref
  Proposee --> Candidate : registration in phase 3
  Candidate --> Candidate : accumulation every cycle
  Candidate --> Invalidee : false preconditions, stale but_ref, expiration, inadmissible
  Candidate --> Engagee : threshold crossed, tie-break won, command admitted
  Engagee --> Engagee : step executed then verified, continue
  Engagee --> Engagee : new deliberation won with inertia
  Engagee --> Engagee : revised plan adopted
  Engagee --> Engagee : veto/refusal limited to step, plan marked a_reviser then replanning
  Engagee --> Engagee : reflex, step suspended for this world step
  Engagee --> Succes : success condition reached
  Engagee --> Echec : failure condition reached
  Engagee --> Invalidee : option itself invalid or inadmissible
  Engagee --> Remplacee : another option wins a deliberation
  Engagee --> Interrompue : safety block or operator stop
  Succes --> [*]
  Echec --> [*]
  Invalidee --> [*]
  Remplacee --> [*]
  Interrompue --> [*]
  Rejetee --> [*]
```

Complete lifecycle: creation → preliminary admissibility → registration → competition → engagement → planning or plan revision → execution of one step → comparator verification → continuation, revision, or interruption → success, failure, invalidation, or replacement.

### 8.5 Evidence and evaluation

For each candidate and at every cycle, Competition assembles an EvaluationOption from specialized producers; it does not itself compute its reasons for choosing [V-19].

| Component | Producer | Absence |
| --- | --- | --- |
| E_a^Q, learned value | Value and Needs | `non_appris`: component unavailable, distinct from zero [S-06.5] |
| E_a^sim, simulated value | Value and Needs, through a simulator call | `indisponible` if the cycle's common effective budget is not completed; incompleteness is logged and the partial value is not used |
| m_a, intrinsic motivation | Exploration for informational options and tests; Metacognition and Health for `dormir` | `non_applicable`, distinct from a zero value [V-19] |
| R_a, U_a, protection | Value and Needs | R_a `inconnu`: no risk penalty; U_a carries uncertainty |

Total evidence combines these components without double counting (DC-01):

```latex
E_a^{\mathrm{ext}} = \lambda_a\,E_a^{Q} + (1-\lambda_a)\,E_a^{\mathrm{sim}},\quad \lambda_a = \frac{n_a}{n_a + n_0}
\qquad
e_a = \mathrm{clip}_{[-1,1]}\Big(\gamma_v(\tau)\,\tanh\!\big(E_a^{\mathrm{ext}}/E_{\mathrm{éch}}\big) + w_m\, m_a\Big)
```

- n_a is the number of learned updates for the option's `signature_apprentissage`; if only one extrinsic component is available, it is used alone; if neither is available, E_a^ext = 0 and the unavailability is logged [S-05.1]. A partial or interrupted simulated value is never treated as an available component.
- m_a counts only when applicable. γ_v(τ) = e^{α_v τ_reward} carries the effect of reward sensitivity; temperament exploration acts inside m_a, not here [V-18].
- **No double counting**: variables already included in D pass through value and never a second time through m_a(dormir) [V-17]. Each component preserves the provenance of the signals that produced it; the same signal identifier does not contribute twice to the same decision through two paths, except under a rule declared as an "intentional double effect" [V-17].
- **Declared intentional double effect.** Predicted harm weighs both in E_a^sim, through the reduction in predicted rewards, and in π(R_a ; τ): this is intentional risk aversion [S-05.3]. This is the only entry on the INV-14 allowlist in the MVP; no engineer removes either path on the grounds of double counting.
- All components in a cycle refer to the same starting state and the same option. All candidates actually simulated within a cycle receive the same `(R_eff, H_eff)` budget. Learning derived from the consequences of a command influences evidence only from the next cycle onward [S-05.1]. An `action_proposee` contribution can never serve as evidence for the option it carries unless independent support, distinct in provenance, establishes the same fact.

### 8.6 Accumulation and thresholds

```latex
A_a(c+1) = \max\big(0,\ (1-\ell)\,A_a(c) + u(c)\,g\,e_a(c) + \sigma\,\varepsilon_{a,c}\big)
\qquad
a \text{ crosses if } A_a(c) \ge s_a(c)
```

```latex
s_a(c) = \max\big(s_{\min},\ s_a^{0} + \pi(R_a;\tau) + \chi(U_a;\tau) - \iota_a\big),\qquad
s_a^{0} = s^{0} - \delta_{\mathrm{prot}}\,\tfrac{1+\tau_{\mathrm{menace}}}{2}\,\mathbb{1}[\text{protectrice}]
```

| Term | Rule | Origin |
| --- | --- | --- |
| u(c) | global deliberation urgency: deterministic, monotone non-decreasing, bounded, common to all; gain on incoming evidence, never evidence itself nor a threshold reduction; reset at each closure | S-05.5, DC-01 |
| g | accumulation gain, common in the MVP; novelty no longer modifies it | V-18 |
| ε_{a,c} | draw from the accumulator random stream, in canonical candidate order | S-01.3 |
| π(R_a ; τ) | positive, increasing in R_a, heavier when threat sensitivity is high; zero if R_a is unknown; can never lower the threshold | S-05.3, DC-01 |
| χ(U_a ; τ) | safety-uncertainty penalty, low or zero for a temperament with low threat sensitivity, high for a temperament with high threat sensitivity | NQ-07, DC-01 |
| s_a^0 | base threshold; lower for an option with contextual protective status in a threat-sensitive individual | NQ-06 |
| ι_a | inertia: bounded reduction of the threshold for the engaged option only, modulated by goal protection; never an evidence bonus; never bypasses veto or reflex | S-05.4 |
| s_min | strictly positive floor guaranteeing a defined relative margin | DC-02 |

Inertia lasts as long as the option remains engaged; it disappears as soon as the option succeeds, fails, becomes invalid, is interrupted, or is replaced. No fixed duration in cycles is used [S-05.4].

### 8.7 Opening, tie-breaking, and closure

**Opening a deliberation** (every waking step) [V-34, NQ-02]:

| Candidate | Accumulator at opening |
| --- | --- |
| engaged option | A = 0, with its inertia on the threshold |
| previous non-winning alternative that remains valid | retains the residual ρ·A applied at the previous closure |
| new option | A = 0 |
| invalid option | accumulator removed |

If no new information justifies a change, inertia normally favors continuing the engaged option; another option replaces it if it crosses its threshold despite that advantage. End, failure, or invalidation of the engaged option, veto of its step, active-goal change, or admission of relevant information into S_t impose especially strong reevaluation, without themselves choosing the new action.

**Tie-breaking**: when several candidates cross their threshold in the same cycle, the largest relative overshoot (A_a − s_a) / s_a wins; on an exact tie, stable, versioned canonical order breaks the tie. u(c) is not a criterion; no priority is given to a protective option at this stage; no random draw is used [S-05.7, DC-02].

**Closure**, when the step ends without a lethal transition (3.4): accumulators of other valid candidates are multiplied by ρ, those of invalid candidates are removed; the winning option leaves the accumulation regime; u(c) is reset. The same reduction applies after a C_max fallback with no winner [S-05.6, S-05.8].

### 8.8 Normative competition pseudocode

```text
procédure COMPÉTITION.ouvrir_délibération(t)
  c ← 0
  pour a ∈ registre (ordre canonique) :
    si invalide(a, but_actif, t) : supprimer(a)                  # preconditions, but_ref, validity, admissibility
    sinon si a = option_engagée : A[a] ← 0                         # V-34
  # the others keep their residual ρ·A; an option registered later starts at 0

procédure COMPÉTITION.accumuler(EV, c)
  pour a ∈ candidats (ordre canonique) :
    si EV[a].statut = non_evalue :
      journaliser(non_evalue(a))                                   # DC-07: A and s remain unchanged for this cycle
      continuer
    e ← preuve(EV[a])                                              # DC-01
    A[a] ← max(0, (1 − ℓ)·A[a] + u(c)·g·e + σ·tirage(flux_accumulateurs))
    s[a] ← max(s_min, s0(a) + π(R_a, PARAMETRES_TEMPERAMENT.menace) + χ(U_a, PARAMETRES_TEMPERAMENT.menace) − ι(a))         # ι(a) = 0 if a is not engaged

fonction départager(G)
  retourner premier_par(G, clé = ((A[a] − s[a]) / s[a] décroissante, ordre_canonique(a)))   # DC-02

procédure COMPÉTITION.clore_délibération(d)
  pour a ∈ registre, a ≠ d, a valide : A[a] ← ρ·A[a]
  si d est une option cognitive : option_engagée ← d ; d.etat ← engagee
  u ← état initial
```

### 8.9 Diagram C · From observation to learning

```mermaid
sequenceDiagram
  autonumber
  participant MON as World
  participant PER as Perception
  participant POR as Gatekeeper
  participant PLA as Planning
  participant COM as Competition
  participant VB as Value and Needs
  participant CTL as Action Control
  MON->>PER: [D] local state for step t
  PER->>POR: [D] observation "source to the north", alert "water below setpoint"
  POR->>POR: [P] S_t[n+1] published
  POR->>PLA: [D] read S_t at cycle n+1
  PLA->>COM: [D] proposed option, but_ref boire, motif_ref but_actif
  COM->>VB: [S] option evaluation
  VB-->>COM: [D] EvaluationOption: values, R_a, U_a, protection
  COM->>COM: [S] accumulation, threshold crossed, tie-break
  COM->>CTL: [C] decided option
  CTL->>CTL: [S] admissibility, veto, mask
  CTL->>MON: [C] command "north", predicted consequences frozen
  MON->>PER: [D] consequence observed at step t+1
  PER->>CTL: [D] compare predicted and observed
  CTL->>VB: [D] attribution, auxiliary credit information
  PER->>VB: [D] body telemetry, from which reward r_t is computed
  VB->>VB: [P] TD update at the end of the step of the next decision, visible on the following step (DC-15)
```

### 8.10 Example: A and B

Leak, noise, and urgency omitted; illustrative values. Base threshold 1.0; the risk penalty for nighttime exploration is 0.4 for A, which is threat-sensitive, and 0.1 for B. For B, the shelter prediction did not enter S_t (6.7), yielding weaker evidence for shelter [spéc. 6.6].

| Cycle | A · shelter, threshold 1.0 | A · explore, threshold 1.4 | B · shelter, threshold 1.0 | B · explore, threshold 1.1 |
| --- | --- | --- | --- | --- |
| c + 1 | 0.35 | 0.30 | 0.30 | 0.40 |
| c + 2 | 0.70 | 0.60 | 0.60 | 0.80 |
| c + 3 | 1.05 | 0.90 | 0.90 | 1.20 |

At cycle c + 3, shelter crosses its threshold for A, while "explore" crosses for B; three S_t publications were sufficient, all within the same world step.

### 8.11 Planning

- Planning builds budgeted plans, with expected observations for each step, toward the active goal or an exploration target [spéc. 9.8, NQ-18].
- It is triggered when a goal requiring a plan is activated or modified, a step fails, new information challenges feasibility conditions, an expected observation is missing at its deadline, a relevant alert appears, or an explicit request arrives [S-02.4]. A stagnation signal counts as new information under this rule.
- At each step, the active plan is checked in the authorized phase; verification restarts a search only if a relevant reason is detected. A missing observation is uncertainty to examine, not an automatic failure.
- An already processed event does not restart the same search; an active search may continue over several cycles within its budget.
- Replanning produces a `ResultatPlanification`: `plan_trouve`, `non_planifiable_actuellement` only after a search under full budget, or `incomplet_budget` if the search could not be completed. It does not replace the active plan by itself and never changes the goal (DC-03, DC-17).
- Planning requests missing preconditions through requests (stone inventory) and creates intentions in prospective memory.
- Minimal system (stage 4): greedy planner toward the resource for the active goal, using the hand-written E-0 movement model; replaced by simulator-based planning at stage 6.

## 9. Action control, reflexes, and vetoes

### 9.1 Arbitration of execution paths

Action Control is the only component that sends commands to the world. The path arbiter (R4 in v2) applies a fixed order [spéc. 8.2, NQ-12]:

1. **Veto** on any command, regardless of source, plus protocol mask during resumption after rollback (18.4).
2. Innate **reflexes** for avoidance or approach.
3. **Option decided by competition**, including compiled skills and habits.

A double command within the same step is resolved by this order and logged. The subservice `CONTRÔLE.admettre(cmd)` applies, in order, veto prohibitions and then the protocol mask, returning `{ok, raison, portee : option | plan_ou_etape | protocole | direct}`; it is used for reflex and cognitive commands alike. The current step of the engaged option no longer has its own priority: it executes only if the engaged option wins the step's deliberation, with its inertia [NQ-02].

### 9.2 Reflexes

- A reflex is an innate, priority response on the direct path: it acts within the step without passing through S_t or competition. MVP reflex: move away from an adjacent creature.
- Reflexes are tested at the opening of every step on that step's stimuli; they remain active during sleep and may cause waking [S-10.2].
- When a reflex proposes a command, that command first passes through the same veto and mask as every other command. If admitted, it becomes the command for the step and no deliberation is opened; the engaged option remains engaged, its step is suspended for that world step, and is revalidated on the next step. If refused, no reflex command is sent and an ordinary deliberation opens within the same step (DC-12).
- Every reflex is logged with the stimulus that triggered it.

### 9.3 Veto and protected invariants

The veto has a closed, explicit, versioned list of prohibitions; it creates no new category during a life [S-14.1, S-14.3]. At minimum, it blocks:

1. movement into a zone known to be lethal;
2. consumption of an item known to be toxic;
3. any command whose sufficiently established consequence would violate a protected invariant, for example lowering integrity below the minimum threshold in the safety policy.

| Rule | Content |
| --- | --- |
| Engine | semantic prohibitions and protected invariants pass through the same single control point [S-14.4] |
| Knowledge | innate core of rules and facts, plus learned facts with status etabli_pour_securite, read from the canonical source in the causal model; no private copy, no oracle access [S-14.2] |
| Threshold | a hypothesis, suspicion, or uncertain possibility does not trigger the veto; a merely uncertain violation remains a risk handled by R_a and U_a [S-14.4] |
| Learning | the individual learns facts to which the rules apply (this berry, this zone), never new rules; a candidate constraint remains inactive until the policy is modified externally, explicitly and in a versioned manner [S-14.3] |
| Policy | frozen during the life; any exceptional intervention is a logged external input analyzed separately |
| Journal | command, rule, rule type, elements establishing the violation, policy version |

**After a veto** [S-14.5]: the command is never sent. Control qualifies the scope of the refusal. If the rule forbids the option itself in the current context, the option becomes inadmissible and its accumulator is removed. If it forbids only the current step or plan, the plan moves to `a_reviser`, the option remains valid, is suspended for the rest of the cycle, and may return after replanning. Competition resumes among remaining admissible candidates. The veto never chooses a replacement. If no admissible option is retained, `attendre` is executed, provided it itself respects protected constraints; otherwise the individual enters safety block (18.6). An ordinary veto does not alert the operator.

### 9.4 Admissibility

The safety system exposes a service [V-43]:

```text
verifier_admissibilite(option, contexte) → admissible | inadmissible | indetermine
```

- Planning MAY consult it before finalizing an option, without copying the veto's internal facts; this filtering avoids planning and competing an option already known to be forbidden.
- `indetermine` does not prevent proposing the option; the final veto remains the last barrier: invalidation, replanning, and resumption of competition if the option becomes forbidden after planning.
- Admissibility is neither R_a nor U_a: it states whether the safety policy authorizes the option, not how dangerous or poorly known it is.

### 9.5 Step execution and freshness

- A decided option carries the S_t version on which it was based and is revalidated when executing its step, like optimistic concurrency control: if a critical element has changed (preconditions, safety), it returns to competition or the direct path takes over [spéc. 6.8].
- Every command is sent with its predicted consequences frozen on emission and an observation window declared before execution, in steps; for a primitive command with immediate effect, the standard window covers the next step [S-15.2, S-15.3].
- Every command is traceable to the option and plan that produced it, or to the direct mechanism (reflex), as well as to the contributions and S_t version that grounded it.

### 9.6 Agency comparator

The agency comparator is an internal Action Control subservice, independently testable (`AgencyComparator`), not a top-level component [S-15.1].

- **Data**: the executed command, its predicted consequences frozen on emission, and later observations accessible to the individual; never the real world state or the oracle [S-15.2].
- **Window**: a change can be attributed only if it appears within the declared window for the expected effect; an absent effect at window closure is recorded as `effet attendu manquant`; a change occurring after the window is not attributed retroactively [S-15.3].
- **Tolerance**: per variable, deterministic and versioned, according to channel and prediction precision; status `conforme`, `non_conforme`, or `indeterminable`, effect by effect [S-15.4].
- **Attribution**: a conforming effect within the window is compatible with attribution to self; a non-conforming effect is attributed to the world only if an accessible external element justifies it; otherwise, or if several causes remain plausible, attribution is `incertaine`; several compatible commands are retained as candidates.
- **Consumers** [S-15.5]: the Causal Model is the main consumer, as an item of evidence; value learning MAY use it for credit assignment without depending on it; Metacognition monitors attribution biases; the bench compares attributions against ground truth externally; the simulator never uses them directly.

## 10. Memory

### 10.1 Five memories

| Memory | Content | Write | Recall |
| --- | --- | --- | --- |
| Working | S_t and its silent reactivatable buffer | every cycle | direct |
| Episodic | dated episodes with context, body, and value | end of episode | by cue (10.4) |
| Semantic | facts and maps with provenance, confidence, and status; references to contingencies whose canonical source is the Causal Model [NQ-10] | consolidation | request |
| Procedural | compiled skills and habits, preconditions, success rate | consolidation | triggered by preconditions, as options |
| Prospective | intentions and triggers | Planning | monitoring at every waking cycle |

### 10.2 Memory source

- Memory writes only from what the individual experienced: contributions, S_t versions, commands, and results in the journal's autobiographical view (17.5). Segments cancelled by lethal rollback, oracle and bench data, and protocol events never enter it [V-24].
- It accesses the journal read-only, through this view only; every access is logged and its effect measured [Q14].

### 10.3 Episodes

A new episode begins when the active goal changes, when a prediction error exceeds k_ép times its usual precision, when the individual changes zone, or after L_ép steps. Two episodes separated by fewer than Δ_ép steps are linked automatically [spéc. 7.2].

### 10.4 Recall

Recall score combines recency, importance, and relevance to S_t; importance is the absolute value of the episode plus its surprise. Memory spontaneously proposes a memory when its score crosses a threshold and responds to requests [spéc. 7.3]. A memory enters x_t only if it has been recalled by these mechanisms [S-06.1]. In degraded mode, recall examines a smaller set (DC-07).

### 10.5 Intentions

- While awake, Memory checks triggers every cycle against frozen S_t and its authorized interfaces. A temporal trigger carries an explicit deadline and unit [S-02.5].
- A trigger that becomes applicable makes the intention a **candidate for attention** through the ordinary gatekeeper circuit: this is neither a goal change, nor a command, nor a guarantee of immediate processing. The Goal Manager receives the associated goal proposal. Memory retains the `pression_base` set at creation; if the intention has a deadline, its proposal's `pression_courante` is recomputed deterministically as the deadline approaches according to DC-03.
- Tracking state prevents multiple simultaneous candidacies for the same occurrence. Trigger satisfaction, candidacy, possible admission into S_t, and consequences are distinct, logged steps.
- A dated intention marked `reveil_autorise` has its deadline published by Memory before sleep in a read-only index read by the wake rule, without duplicating the intention [V-41]; at the deadline, it may cause waking; ordinary cognition is not maintained during sleep; on waking, Memory checks the intention, then recall passes through the gatekeeper [NQ-17].

### 10.6 Forgetting and rewriting

Reduce accessibility rather than delete; archive; delete only for safety or data-protection reasons; never from the journal except through cryptographic erasure. No memory is rewritten in the MVP [spéc. 7.8, 7.9].

## 11. Online learning and calibration

### 11.1 Learned values

- Evaluation state x_t is canonical, versioned, and built only from information accessible to the individual in the considered cycle: relevant body state, position, active goal, temporal context, and the explicit projection of descriptive S_t information defined by the schema [S-06.1].
- x_t excludes accumulators, thresholds, u(c), current evidence, budgets, logging metadata, random states, all oracle information, unrecalled memory, and temperament τ. For evaluation of an option `a`, it also excludes any information whose sole causal support is the `action_proposee(a)` contribution itself; independent support may contribute (DC-10).
- Value is an inspectable linear function of a versioned vector of deterministic descriptive features φ(x): Q(x, o_sig) = ψ_o_sig · φ(x), where `o_sig = option.signature_apprentissage` (8.1). `ψ`, `n_a`, and eligibility traces are indexed by this signature, never by the ephemeral identifier of the option instance. An exact table may serve as a reference in small tests; no learned network is used in the MVP [S-06.2].
- Temporal-difference learning with eligibility traces [spéc. 8.6]:

```latex
\delta_t = r_t + \beta\,Q(x_{t+1}, o^{sig}_{t+1}) - Q(x_t, o^{sig}_t) \qquad z(t) = \beta\,\lambda_e\,z(t-1) + \nabla_{\psi} Q(x_t, o^{sig}_t) \qquad \Delta\psi = \eta\,\delta_t\,z(t)
```

- At birth, parameters are zero and each value has status `non_appris`; an unlearned value is not available evidence. No optimistic or pessimistic initialization [S-06.5].
- β = β_individu, derived from reward sensitivity by the mapping table and stable during the life; η is fixed in the MVP [S-06.4, NQ-05].
- The update of a segment between two cognitive decisions is computed and published when the step of the second decision ends without a lethal transition; it is visible from the first cycle of the next step. A reflex or sleep step extends the segment without an update. If a terminal state actually experienced closes the trajectory without a following decision, the last segment uses zero bootstrap; an external protocol termination produces no terminal update (DC-15).

### 11.2 Perceptual precisions

Perception learns one precision per source online; it owns the active form, while the consolidated form lives in h (15.6).

### 11.3 Verification

Verification is defined by contribution type and produces one of four outcomes: `confirmee`, `contredite`, `indeterminee`, `non_verifiable`. Absence of verification evidence is never a contradiction [S-08.1].

| Type | Rule |
| --- | --- |
| prediction | at its deadline, against a later comparable observation of the announced quantity |
| observation | against a later comparable observation, according to its subject, context, and time |
| alert | only when exposure allows the announced harm to be tested: observed harm, confirmation; exposure without harm, contradiction or weakening; no exposure, indeterminate |
| hypothesis | progressively, through its lifecycle in the causal model (13.2) |
| proposed option | neither true nor false; its claims (feasibility, preconditions, consequences) become testable when appropriate; an unchosen option is not an error |
| response | according to the nature of its content |

- Verification status and admissibility for κ are distinct: a later observation from the same channel may confirm signal stability in the sense of this section, but DC-06 determines whether the confirmation is sufficiently independent to modify κ.
- A counterfactual prediction on an unexperienced branch carries status `contrefactuelle_non_verifiee` and never counts in κ. A comparable situation experienced later MAY verify the model or rule that produced it, never the unexperienced episode [S-08.3].
- The oracle channel is never used to verify, calibrate, or correct anything in the individual [S-08.2].

### 11.4 Reliability maps κ

- Metacognition and Health owns, computes, and publishes κ maps; the gatekeeper only reads them; the bench computes its own calibration metrics externally [NQ-09].
- Initial confidence is a finite-strength prior: neutral (f = 0.5) for a module with no prior evidence, derived from calibration measured offline for pretrained equipment, identical for all individuals using the same equipment version. Experience counts from the first verification and eventually dominates [S-08.4].
- Verifications obtained during a cycle are integrated deterministically, then published atomically in phase 5; the version used during a cycle remains frozen; the new version is usable only in the next cycle [S-08.6].
- Map representation and verification-provenance rule: the calibration key includes module, contribution type, and signal channel or family. Only verifications grounded in a physical consequence or causally independent modality update κ; repetition from the same channel may feed a separate stability indicator but cannot by itself increase effective reliability. Details: DC-06.
- The prior of pretrained equipment is based on ground truth from training worlds, shared by all individuals and predating birth: this is not oracle leakage, because the oracle is never used during a life.

## 12. Simulator and equipment

### 12.1 Role

The equipment predicts observable world and body transitions relevant to candidate options; it produces no preference, value, or decision [S-09.1]. Minimum scope: local consequences of the individual's actions (movement, obstacles, physical changes), evolution of external mobile entities (creatures), outcomes of interactions with resources, objects, and structures (collection, tool crafting, shelter), and consequences of world configurations (shelter protection). Its outputs are typed predictions with a horizon, declared confidence, and equipment version. E-v1 through E-v3 are comparable versions of the same equipment, potentially composed of submodels behind a common interface.

### 12.2 Inputs

Each call receives an explicit, versioned simulation state built by the requester solely from information accessible to the individual: perceived local view, option or action to simulate, required body variables, known map, and observable contextual variables that actually affect dynamics (day or night). Never hidden ground truth or the oracle; never temperament, learned values, or accumulators; never the internal state of another module [S-09.2].

### 12.3 Learned contingencies

Frozen equipment is the base model; learned contingencies form a personal correction layer applied to its predictions without ever modifying its parameters [S-09.3]. A contingency replaces only the transition components it concerns; the correction may be numerical, categorical, or probabilistic. Only contingencies with causal status `etablie` correct a prediction [NQ-10]; when no applicable contingency exists, the base prediction is used unchanged. If several contingencies target the same variable, the most specific one wins; an unresolved conflict is represented as explicit uncertainty.

### 12.4 Budget

For each cycle, before evaluation Competition sets a common effective budget `(R_eff, H_eff)` for all candidates that will actually be simulated; in normal mode `R_eff ≤ R_max` and `H_eff ≤ H_max`, and in degraded mode the same reduced values apply to every evaluated candidate. A rollout stops early on a terminal condition; in a deterministic context an identical rollout is not repeated; unused budget is not redistributed. If a candidate cannot complete the announced effective budget, its `E_a^sim` component is `indisponible` for that cycle: partial results are logged for diagnosis but do not enter evidence. Absence of a consequence within the horizon never proves impossibility; the rollouts used and horizon reached are logged; exhaustion stops only that candidate's simulation [S-05.2, DC-01]. β, which discounts distant consequences, remains distinct from H_max, which limits how far computation runs [S-06.4].

### 12.5 Corpus and equivalence

- The corpus combines broad exploration with targeted scenarios guaranteeing indispensable rare transitions; at minimum it covers free and blocked movements, resource interactions and collection, tool crafting and collection with a tool [NQ-15], shelter construction and states including a closed shelter, creature dynamics by day and night, and every transition in 12.1; each phenomenon is represented with contrast situations; coverage is verified family by family [S-09.4]. Corpus seeds are distinct from experiment seeds [spéc. 10.2].
- Two versions are equivalent only if they simultaneously satisfy overall performance, per-family performance, performance by horizon, calibration, and absence of systematic bias, each within its own tolerance. Tolerances are fixed after benchmark definition and before any training, then frozen; if no version meets all tolerances, none is equivalent. Decision comparison on test situations is only an additional integration test [S-09.5, S-09.6].
- Minimal system: the hand-written E-0 movement model serves as equipment through stage 6.

## 13. Causal model

### 13.1 Role

The Causal Model holds causal hypotheses and their status, proposes interventions, answers "why" questions, and owns the **single canonical source** of learned contingencies; Memory keeps references to them, the simulator consults them, and neither keeps a mutable copy [spéc. 9.6, NQ-10]. Each contingency has a stable identifier, a version, an application context, its statuses, and the evidence supporting them.

### 13.2 Causal status

| Status | Condition for moving to the next |
| --- | --- |
| observed correlation | at least n_1 co-occurrences, above base rate |
| causal hypothesis | alternatives made explicit, contextual variables controlled |
| tested by intervention | the effect persists when the individual causes it, in at least n_2 contexts |

| established | revisable: returns to hypothesis if the effect disappears |

n_1 and n_2 are preregistered [spéc. 8.5]. An attribution from the comparator is one item of evidence, never causal truth by itself [S-15.5].

### 13.3 Usage statuses

The same knowledge object carries, without duplication, two independent statuses [V-43, NQ-11]:

| Status | Authorizes | Requirement |
| --- | --- | --- |
| `etabli_pour_securite` | use of the fact by an existing veto rule; may make an option or command inadmissible | threshold specific to safety uses, without deliberate re-exposure to danger; promotion and demotion criteria: DC-05 |
| `etablie` (causal status) | correction of simulator predictions | full cycle from 13.2 |

Safety may require less certainty than causal modeling because the two mechanisms do not have the same responsibility. A fact established for safety receives no fictitious penalty in R_a. A lethal transition followed by rollback is never a learning experience and promotes no fact [S-14.2, V-24].

### 13.4 Tests and rules produced during sleep

- The Causal Model proposes test options, which enter competition like the others; it does not assign itself motivation: Exploration evaluates their intrinsic interest [spéc. 8.5, V-19].
- Rules extracted by Consolidation enter the canonical source at commit with hypothesis status (DC-16).

### 13.5 Diagram F · Lifecycle of causal and safety knowledge

```mermaid
flowchart LR
  OBS["Observation anchored to monde"] -->|"[E] co-occurrences"| COR["correlation"]
  subgraph CAUSAL["Causal status"]
    COR -->|"[T] alternatives made explicit"| HYP["causal hypothesis"]
    HYP -->|"[T] intervention, n_2 contexts"| TES["tested"]
    TES -->|"[T] criteria met"| ETA["etablie"]
    ETA -->|"[T] effect disappears"| HYP
  end
  subgraph SECU["Safety status, same object"]
    AUC["aucun"] -->|"[T] promotion DC-05"| EPS["etabli_pour_securite"]
    EPS -->|"[T] demotion DC-05"| AUC
  end
  COR -->|"[D] evidence"| AUC
  INNE["Innate policy facts"] -->|"[D] from birth"| EPS
  ETA -->|"[D] prediction correction"| SIM["Simulator"]
  EPS -->|"[D] safety facts"| VETO["Veto and admissibility"]
```

Running example. After two losses of integrity following the red berry, contingency "red berry → integrity loss" reaches status `etabli_pour_securite`: the veto now blocks "eat the red berry", and Planning no longer proposes that option. It remains a causal hypothesis until the criteria in 13.2 are met; the simulator continues to use the base prediction.

## 14. Exploration

- Exploration assigns intrinsic value to information: calibrated novelty, learning progress, informational interest; it detects boredom [spéc. 9.10].
- It designates **exploration targets**; Planning turns a target into an executable option; the option enters ordinary competition [NQ-18].
- It produces m_a for informational options and evaluates the intrinsic interest of tests proposed by the Causal Model [V-19].
- The `exploration` coefficient in `ParametresTemperament` modulates m_a; Exploration never reads τ directly and this coefficient does not affect g [V-18].
- Exploration is instrumental (but_ref present) or autonomous (motif_ref = cible_exploration only); autonomous exploration does not count as progress on the active goal [V-10].
- Its state consists of visit counters and progress per activity. A source that remains always unpredictable provides no learning progress: this is the noisy-TV trap, which Exploration MUST avoid.
- In degraded mode, designation of new targets is deferred (DC-07).

| Option | but_ref | motif_ref | m_a |
| --- | --- | --- | --- |
| explore the northern zone, unrelated to the goal | absent | cible_exploration_17 | produced by Exploration |
| explore to find water, goal "drink" | boire | but_actif | produced by Exploration if novelty is relevant |
| test "the incomplete shelter lets the creature in" | absent | test_causal | intrinsic interest evaluated by Exploration |

## 15. Sleep and consolidation

### 15.1 Sleep pressure

- `dormir` is an ordinary competition option; no parallel planner triggers sleep [S-10.1].
- Metacognition and Health produces sleep pressure and m_a(dormir) [V-19]. Factors retained are F_cog, consolidation pressure, temporal context (night), and any sleep variable distinct from D. Homeostatic variables already included in D (energy, for example) act through the learned or simulated value of `dormir`, never a second time through m_a(dormir); body state MAY modulate or condition the pressure without duplicating a contribution already counted [V-17]. Function form: DC-13.
- Night is a favorable context, not an obligation; sufficiently high pressure makes sleep relevant outside nighttime. A safety emergency prevents entry into sleep or interrupts it through priority paths.
- Consolidation pressure represents relevant material remaining to be reorganized; F_cog represents accumulated cognitive effort; they are two distinct quantities [S-11.2].

### 15.2 Entering sleep

When `dormir` is engaged and its command admitted, the individual enters sleep mode on the next step. Entering sleep and starting consolidation are two distinct events: consolidation begins only once the individual is asleep and its own conditions are met [S-10.1, spéc. 7.7]. On entering sleep, the Goal Manager suspends the active goal's stagnation window; it resumes on waking [V-10].

### 15.3 Reduced perception and waking

- During sleep, ordinary cognition is suspended: no cycle, no deliberation. Reduced perception remains active for reflex stimuli, relevant threats, and critical body changes; reflexes remain active [S-10.2].
- A reflex MAY act without waiting for cognition to resume and may cause waking at the same time.
- A **dedicated wake rule**, distinct from the s_sec preemption threshold and with its own parameters, causes waking on a qualifying non-reflex signal, at the deadline of an authorized dated intention [NQ-17], at the natural end of sleep, or at the latest after `L_sommeil_max` consecutive steps (DC-13). This bound guarantees that persistent consolidation pressure cannot keep the individual asleep indefinitely.
- Stimuli that do not wake the individual do not become perceptions. On waking, the individual perceives the state accessible at that moment; nothing is reconstructed retroactively as memory.
- If consolidation is in progress, waking first causes its safe interruption, then cognition resumes in the same step (DC-13).

### 15.4 Normative pseudocode for a sleep step

```text
procédure PAS_DE_SOMMEIL(t, capture)
  obs_r ← PERCEPTION.réduite(capture)
  cmd ← CONTRÔLE.réflexe(obs_r)
  motif ← RÈGLE_DE_RÉVEIL.évaluer(obs_r, intentions_datées, MÉTACOGNITION.pression_sommeil,
                                  duree_sommeil = t − t_entree_sommeil)   # DC-13
  si cmd ≠ ∅ :
    admission ← CONTRÔLE.admettre(cmd)                                # veto then mask
    si non admission.ok : cmd ← ∅                                     # a refused reflex never bypasses veto
  si cmd ≠ ∅ ou motif ≠ ∅ :
    si CONSOLIDATION.active : CONSOLIDATION.interrompre()             # current pass cancelled, validated passes retained
    motif_reveil ← "reflexe" si cmd ≠ ∅ sinon motif
    individu.mode ← VEILLE ; JOURNAL.écrire(réveil, motif_perceptible(motif_reveil)) ; GESTIONNAIRE_BUTS.reprendre_stagnation()
    si cmd ≠ ∅ : EXÉCUTER_PAS(t, cmd, source = réflexe) ; retour
    DÉLIBÉRER(t) ; retour                                              # cognition resumes within this step
  si non CONSOLIDATION.active :
    si CONSOLIDATION.suspendue :
      CONSOLIDATION.reprendre()                                        # priority to the already-open transaction
    sinon si CONSOLIDATION.conditions_remplies() :
      CONSOLIDATION.démarrer(t)
  si CONSOLIDATION.active : CONSOLIDATION.créneau(budget_consolidation_pas)
  MÉTACOGNITION.récupération_pas()                                     # F_cog and sleep pressure
  EXÉCUTER_PAS(t, commande_sommeil, source = sommeil)                  # world and body advance
```

### 15.5 The world during sleep

The world and body continue to evolve in simulated time; consolidation never suspends the environment; machine time consumed by consolidation does not advance simulated time [S-10.5]. Events during the period may wake the individual; they are never added to the current batch, which was frozen when consolidation started.

### 15.6 Consolidation

**Trigger and batch.** Consolidation starts during sleep, outside emergencies, when consolidation pressure (unconsolidated episodes and saturation) exceeds its threshold [spéc. 7.7]. Each sleep period has a maximum capacity measured in work budget, not machine time. The batch is selected deterministically, favoring recent experiences with large consequences, large prediction errors, or relevant repetition; an aging mechanism prevents a relevant episode from being postponed indefinitely; unselected episodes remain available [S-10.6]. At startup, consolidation fixes a **causal cut point** and a **frozen input batch** [V-21].

**Six passes**, on a private candidate version of h:

1. select episodes by deviation and value;
2. interleaved replay of recent and old episodes against catastrophic forgetting;
3. extract rules with hypothesis status;
4. compile skills: a plan that succeeds n_c times in nearby contexts becomes a compiled procedural option, with its preconditions and success rate;
5. recalibrate consolidated κ forms;
6. maintenance: reindexing, links, purge expired items.

**Transactions.** Each pass records progress in a private workspace; no component of the candidate version is visible before commit [S-10.4]. A validated pass creates a transactional point; these points are used only to resume work and publish nothing.

**Interruption.** Waking interrupts consolidation: the current pass is cancelled and will restart from its beginning; validated work is retained; resumption occurs during a later sleep period [S-10.3]. Suspension state retains at minimum the consolidation identifier, batch scope, source version of h, progress cursor, and last validated point. Only one consolidation may be active or suspended at a time; at the next sleep period, a suspended transaction is resumed before any new batch is selected. During interruption, the individual continues to learn; these updates, subsequent to the cut point, remain in the causal journal [V-21].

**Validation, rebase, commit** [V-21, V-22]:

1. The completed candidate version is validated technically; measurements from the bench and oracle do not participate in this validation [S-10.4].
2. Consolidation writes directly only to h and its private working state.
3. Each owner takes its consolidated representation from h_new and replays, in causal order, its online updates subsequent to the cut point: Value and Needs for Q_active, Metacognition and Health for κ_active, Perception for active precisions. With no later update, rebase reduces to active = consolidated. The Causal Model integrates extracted rules in the same way (DC-16).
4. Each owner prepares its rebased form privately; the scheduler coordinates an **atomic commit**: h_new and all coherent active forms become visible at the same synchronization point.
5. Creation and activation of every version are logged with source version, batch, cut point, originating consolidation, and commit time.

Normal continuation of life never invalidates a batch; only a technical incompatibility of the batch or its source state invalidates it. **Consolidation rewrites stabilized past, never recent present.**

**Guarantees.** No partial modification of h is ever visible; if consolidation is interrupted before commit, the old version remains fully active; no update subsequent to the cut point is lost; all components see the same h version and corresponding active forms at the same instant.

### 15.7 Diagram G · Consolidation and rebase

```mermaid
flowchart TB
  subgraph VIE["During life"]
    ACT["Q_active, κ_active, active precisions"]
    EPI["unconsolidated episodes"]
    MAJ["online updates subsequent to the cut point"]
  end
  EPI -->|"[D] batch selection"| CUT["causal cut point and frozen batch"]
  CUT -->|"[T] start during sleep"| PRIV["six passes on private h candidate"]
  PRIV -->|"[E] transactional point per validated pass"| PRIV
  PRIV -->|"[T] waking: current pass cancelled"| SUSP["suspension state"]
  SUSP -->|"[T] resume at next sleep"| PRIV
  PRIV -->|"[T] batch complete"| VAL["technical validation of h_new"]
  VAL -->|"[D] consolidated forms from h_new"| REB["private rebase by each owner"]
  MAJ -->|"[D] replay in causal order"| REB
  ACT -->|"[D] current active forms"| REB
  REB -->|"[P] atomic commit coordinated by scheduler"| PUB["h_new and rebased active forms become visible together"]
```

### 15.8 Normative consolidation pseudocode

```text
procédure CONSOLIDATION.démarrer(t)
  coupure ← (t, n_dernier_événement) ; lot ← sélectionner_lot(capacité_période)      # frozen
  candidate ← copie_privée(h) ; suspension ← { id, lot, version_source(h), curseur, dernier_point = ∅ }

procédure CONSOLIDATION.créneau(budget)
  tant que budget restant :
    avancer(passe_courante, candidate)
    si passe_courante terminée : valider(passe_courante) ; point_transactionnel() ; passer à la suivante
    si toutes les passes sont validées : VALIDER_ET_PUBLIER() ; retour

procédure CONSOLIDATION.interrompre()
  annuler(passe_courante) ; conserver(passes validées, suspension)

procédure VALIDER_ET_PUBLIER()
  si non valide_techniquement(candidate, version_source) : abandonner_lot() ; journaliser ; retour
  pour P dans [VALEUR_BESOINS (Q), MÉTACOGNITION (κ), PERCEPTION (précisions)] :
    P.préparer_rebasage(candidate.forme_consolidée(P), JOURNAL.mises_à_jour(P, postérieures_à = coupure))
  MODÈLE_CAUSAL.préparer_intégration(candidate.règles_extraites)                      # DC-16
  ORDONNANCEUR.commit_atomique(h_new = candidate, formes_rebasées, règles)             # one synchronization point
  journaliser(version_h, version_source, lot, coupure, t_commit, différences)
```

In a copy used for the standard battery, consolidation is disabled: no new version of h is published even if the copy sleeps [S-13.4].

## 16. Metacognition, health, and modulation

### 16.1 Metacognition and health

Metacognition and Health owns and publishes: κ maps (11.4), F_cog, sleep pressure and m_a(dormir) (15.1), the synthetic budget state placed in S_t, progress measures, and stagnation windows (7.4). It emits information requests when confidence in an item falls, monitors attribution biases (crediting success to self and failure to the world, or the reverse), entropy of S_t occupancy by module, reasoning loops without progress, and signatures of failure modes from extreme temperaments; a persistent deviation triggers an operator alert [spéc. 8.7, 9.11, 11.4].

### 16.2 Cognitive fatigue

F_cog increases at the close of every cycle with UC actually consumed, including in degraded mode; it persists across cycles, steps, and days; it decreases mainly during sleep or recovery steps according to simulated time. It does not reduce the next cycle's budget and enters neither D nor r_t; it feeds sleep pressure [S-11.2, NQ-04]. Dynamic form: DC-13.

### 16.3 Compute budget

| Rule | Content |
| --- | --- |
| Unit | UC, abstract unit of logical work; every operation type has an explicit, versioned cost (simulated transition, evaluated candidate, examined memory item, consolidation unit); never CPU time [S-11.1] |
| Period | renewed every cycle; no reserve or carryover [S-11.2] |
| Levels | global B_cycle ceiling, maximum envelope per module; no implicit transfer between modules; protected capacity for safety and control; cost charged to the module performing the operation; each operation counted once [S-11.3] |
| Overrun | no processing blocks a cycle: stop or suspend according to its contract; a contribution absent when its phase closes is absent from the cycle and never modifies an already published version [S-02.8] |
| Behavior at the limit | absence tolerated if optional, degraded mode if defined, fallback status or value if the service is necessary; every incomplete result is identified as such |
| Visibility | S_t receives a synthetic state (normal, constrained, degraded); detailed counters remain in technical state and journal [S-11.6] |
| Reward | budget never enters r_t or option value; an under-evaluated option remains uncertain, without being penalized as though a bad outcome had been demonstrated |

**Degraded modes.** General rule: reduce precision before function; never invent a result to hide insufficient computation [S-11.5]. The following are never approximated: determinism, integrity of world and body, communications, journal, S_t, immediate safety, reflexes, and veto. A search interrupted for lack of budget produces an explicit state of uncertainty or incompleteness, never false absence. A candidate not evaluated keeps its accumulator unchanged during the cycle: absence of computation is not absence of evidence. Consolidation has no approximate version: at its limit it is suspended transactionally. Exact behavior of every module is fixed by DC-07.

### 16.4 Global modulation

Global Modulation is the sole owner of the modulation profile [spéc. 3.3]. In phase 0 of every cycle, it determines the profile from S_t[n]; the profile remains fixed throughout the cycle; its transitions, motives, and confirmation counters are logged and saved [S-02.6]. Profiles and effects are in 6.4; conditions, thresholds, durations, and priorities are parameters (22).

## 17. Journal, snapshots, replay, and copies

### 17.1 Exact replay

Exact replay is a **re-execution**: from the same starting state, inputs, and execution conditions, the system MUST reproduce at the same simulated instants the same sequence of events, decisions, and commands, and the same states of the world, body, and every internal state capable of influencing subsequent execution [S-01.1, S-01.2]. No numerical tolerance is accepted for these data. Verification occurs in a documented reference execution environment. A normalized journal representation MAY be compared byte for byte; binary identity of files and metadata with no causal effect is not required. Journal rereading is used for audit and diagnosis; it is never proof of replay.

### 17.2 Conditions for determinism

| Condition | Rule |
| --- | --- |
| Randomness | one distinct, identified, reproducible pseudorandom stream per **causal randomness source** actually used: world, perception noise, accumulator noise, exploration, injected scenarios, one stream per scenario with its seed versioned alongside it [V-39]; not necessarily one stream per module; no implicitly shared generator [S-01.3] |
| Seeds and states | initial seed of every stream recorded; current state of every generator in every snapshot; seed alone is insufficient to resume an execution in progress |
| Equipment | randomness from its offline training belongs to a separate perimeter retained with the equipment version |
| Order | sequential execution of one simulation according to explicit, stable scheduling; no internal parallelism unless it is shown to reproduce causally relevant states exactly; several isolated simulations MAY run in parallel [S-01.4] |
| External inputs | logged before application and reinjected at the same points (4.6) [S-01.6] |
| Versions | versions of models, equipment, schemas, ontology, safety policy, parameters, and mapping tables retained with the execution |
| Machine time | outside the causal perimeter; never used to decide, stop, or pace |
| Identifiers | derived deterministically (5.1); technical occurrences include `attempt_ref`, renewed after each rollback of the same step |

### 17.3 What is replayed

The system MUST be able to replay an entire life from birth state and any interval from an available complete snapshot to a chosen later instant [S-01.5]. Learning, consolidations, and internal modifications within the interval are recomputed, never replaced by reading a later saved state; later snapshots serve only as comparison points. Replaying one day is the first practical acceptance test; replaying an entire life is the functional MVP requirement.

### 17.4 Journal

The technical journal records append-only every contribution, S_t version, decision, command, result, update, external input, and scheduler event. Every occurrence has a unique technical identifier including `attempt_ref` and is chained to the previous one, `emp_n = H(emp_{n−1} ‖ event_n)`; any alteration is detected by recomputation [spéc. 7.6]. The journal is never rolled back, including during lethal rollback.

The autobiographical view is not a second mutable journal. It is a **deterministic projection** of the technical trace. Events from a step attempt become autobiographically visible only after non-lethal closure of that step through an `AutoSegmentCommit` event referencing events authorized by the DC-09 allowlist. A branch cancelled by rollback therefore remains in the technical trace without ever receiving an autobiographical commit.

### 17.5 Journal views and access rights

| View | Content | Authorized readers |
| --- | --- | --- |
| Technical | all physical events in the append-only journal, including cancelled branches, rollback, mask, raw counters, random states, and protocol | replay and audit tools, operator, bench |
| Autobiographical | projection of only events referenced by `AutoSegmentCommit`, filtered by the DC-09 allowlist: what the individual perceived, produced, decided, and actually experienced | Memory, read-only, every access logged [Q14]; Consolidation |
| Evaluation trace | oracle annotations and metrics, death counters, profiles; strictly separate storage or view | bench, operator |

No component of the individual reads the technical view or evaluation trace [S-12.4]. Lethal transition, its detection, rollback, mask, `attempt_ref`, and technical counters never appear in the autobiographical view: the individual can neither reread its death nor infer the existence of a cancelled branch [V-24].

### 17.6 Snapshots and resumption points

Types and uses are fixed by DC-08.

**Life snapshots.** There are exactly four types of `Snapshot`:

| Type | Taken | Content | Use | Retained |
| --- | --- | --- | --- | --- |
| Birth snapshot | at birth | complete initial causal state, τ, versions, seeds, causal state of the active scenario if any | replay a life | always |
| Periodic snapshot | at a step boundary, at the preregistered frequency | complete causal state | recovery after failure, interval replay, comparison | according to storage policy |
| Lethal checkpoint | immediately before every command send | complete causal state **excluding journal**, plus `t`, `cycle`, `attempt_ref`, command source, mask, and lethal counter | lethal rollback [V-25] | until non-lethal validation of the step |
| Copy snapshot | at the copy point | complete causal state | bifurcation, battery copy | always, with lineage |

**Consolidation transactional point.** This is NOT a life `Snapshot`. It is a private `CheckpointConsolidation`, taken at each validated pass and containing only working state required to resume consolidation. It is never visible to cognition, restores neither world nor individual, and disappears after commit.

A complete causal state contains at minimum: parameters and versions including `version_E_active` and `ParametresTemperament`, S_t, memories, learned values in both forms, κ, accumulators, queues and quotas, plans and intentions, option registry, engaged commands, contingencies, causal state, exploration counters, metacognitive state including F_cog, modulation profile, h versions, state of all pseudorandom generators, body state, world state, and any **external state actually causal for what follows**, especially the state of an injected scenario, its counters, and its random streams. It never contains the technical journal or evaluation trace: these traces are append-only and are not rolled back [S-13.1, DC-09]. A snapshot is taken only at a coherent point defined by the scheduler, never in the middle of a publication or partially applied transaction.

### 17.7 Copies and lineage

- A copy starts from a complete, coherent causal snapshot; duplicating only θ parameters produces a **configuration clone**, a new individual with the same configuration, not a copy [S-13.1].
- The external environment is not part of the individual: duplicating, preserving, or modifying it is a protocol matter. A copy snapshot MAY reference an external world and scenario snapshot to initialize the branch deterministically, but this external state is not part of the copied identity. Bench, oracle, and evaluation-trace data are never part of the copied individual's state.
- Every copy is a new instance: new identifier, lineage link, and exact copy point; prior history remains shared and traceable; afterward state and journal evolve independently [S-13.3].
- The same definition applies to bifurcation and battery copies; the difference appears after copying: a bifurcation copy lives its life, while a battery copy is placed in a test situation [S-13.2]. The `battery_copy` metadata is not a cognitive status.
- A battery copy operates normally, including online learning, but without consolidation; its changes are never reinjected into its parent; each test situation has a deterministic, preregistered termination criterion, at which measurements and final state are recorded, the branch journal closed, and the copy stopped; this stop is not presented to the individual as a world event [S-13.4].
- Journals of stopped copies are retained fully in the semantic sense: shared prefix with the parent, own branch stored differentially, compressed, or deduplicated without loss of causal events; stop reason is logged; stopping never erases history [S-13.6]. Every creation, copy, and stop is logged (Q18).

### 17.8 Rereading, restoration, replay, copy, bifurcation

| Operation | What it does | What it does not do |
| --- | --- | --- |
| Rereading | reads the journal for audit or diagnosis | does not prove determinism |
| Restoration | reloads complete causal state and resumes the same life (failure, lethal rollback); append-only technical journal is never rewound | does not create an individual and removes no already-logged event |
| Replay | re-executes from a snapshot with the same inputs and must recover the same states | does not read later states instead of recomputing |
| Copy | creates a new instance from a snapshot with a new identifier and lineage | is not the same individual |
| Bifurcation | copy whose divergence is followed in distinct worlds (H5) | reinjects nothing into the parent |

## 18. Safety and lethal rollback

### 18.1 Seven distinct mechanisms

| Mechanism | Nature | Owned by | Acts | Effect | Is not |
| --- | --- | --- | --- | --- | --- |
| Reflex | innate response, direct path | Action Control | at step opening, awake and asleep | immediate command for the step | an option or a veto |
| Veto | prohibition of a command | Action Control | before any send | command blocked, option inadmissible | a replacement choice |
| Cognitive preemption | guaranteed place in S_t | Gatekeeper | phase 2 | safety item enters S_t | an action on the world |

| R_a | descriptive estimate of known danger | Value and Needs | phase 3 | threshold penalty π | a prohibition |
| U_a | lack of reliable safety information | Value and Needs | phase 3 | threshold penalty χ | evidence of danger |
| etabli_pour_securite | usage status of a fact | Causal Model | end of cycle | veto may apply an existing rule to that fact | a simulator correction |
| etablie | causal status of a contingency | Causal Model | end of cycle | correction of simulator predictions | a new veto rule |

They are not equivalent because they do not answer the same question: the reflex protects before cognition; the veto says whether a command is authorized; preemption says what must be known; R_a and U_a say how dangerous or poorly known an option is; the two statuses say for which use a piece of knowledge is authorized.

### 18.2 From command to new deliberation

command → admissibility check, veto and mask → send → world transition → detection of lethal transition → rollback to checkpoint → protocol mask → external counting → resume deliberation.

### 18.3 Death

Death is a detectable terminal outcome of the world; it never becomes a lasting state of the individual [NQ-14]. A transition reaching a terminal condition (zero integrity, or any condition explicitly defined as lethal) is detected by the world **before** becoming the new continuation state. Death exists for the world, replay, and evaluation; it is not a learnable experience: it produces no value, contingency, confidence update, or memory [V-24]. The journal distinguishes an action that led to a lethal outcome from a self-destructive intention; an error, exploration, or bad prediction is never labeled a suicide attempt; that classification requires the intention itself to be established [S-14.1].

### 18.4 Rollback

```text
procédure ROLLBACK_LÉTAL(ckpt, cmd)
  JOURNAL.écrire(transition_létale(cmd), détection, attempt_ref)        # append-only technical trace; no AutoSegmentCommit
  BANC.compter(nombre_transitions_letales)
  INSTANTANÉS.restaurer_etat_causal(ckpt)                              # world, body, cognition, S_t, accumulators, scenario, streams;
                                                                        # technical journal and evaluation trace are never restored
  BANC.compter(nombre_rollbacks_letaux)
  R_letal_consecutif ← ckpt.R_letal_consecutif + 1                     # external protocol state, attached to the resumption sequence
  si R_letal_consecutif > R_letal_max :
    BLOCAGE_DE_SÉCURITÉ(ckpt.t) ; BANC.compter(nombre_blocages_securite) ; retour
  MASQUE.ajouter(cmd)      # protocol intervention, for the resumed deliberation only
  attempt_ref ← ORDONNANCEUR.nouvel_essai_apres_rollback(ckpt.t)       # unique technical namespace; invisible to the individual
  REPRENDRE_DÉLIBÉRATION(ckpt)   # masked decision cancelled; cycles continue to C_max;
                                 # fallback and "attendre" subject to mask; otherwise safety block
```

- The restoration point is the last complete causal checkpoint immediately before the lethal command was sent [V-25]. Restoration never rewinds the technical journal or evaluation trace; it restores only replayable causal state.
- The mask applies only to the deliberation resumed from that checkpoint. It is neither knowledge, nor a learned veto, nor a modification of the causal model; it is cleared as soon as a step ends without a lethal transition. Each new attempt at the same step receives a distinct technical `attempt_ref`, absent from the autobiographical view.
- Each new lethal command from the same context joins the sequence mask and increments R_letal_consecutif [V-40].
- If the masked command is the sleep command, the protocol wakes the individual and opens a deliberation within the same step; the reason for this waking appears only in the technical view.
- If the masked command came from a reflex, the reflex is not replayed: a deliberation opens within the same step (procedure REPRENDRE_DÉLIBÉRATION, 3.4).
- The lethal checkpoint is taken before deliberation closes: resumption cancels the masked decision without needing to undo engagement, the ρ reduction, or the TD update, none of which has yet occurred (DC-08).
- Mask and rollback events are excluded from individuality and spontaneous-learning metrics [V-25].

### 18.5 Diagram I · Lethal rollback

```mermaid
sequenceDiagram
  autonumber
  participant COM as Competition
  participant CTL as Action Control
  participant INS as Snapshots
  participant MON as World and body
  participant ORD as Scheduler
  participant JOU as Journal
  participant BAN as Bench
  COM->>CTL: [C] decided option
  CTL->>CTL: [S] admissibility, veto, mask
  CTL->>INS: [P] complete causal checkpoint before send
  Note over COM,INS: deliberation not closed at checkpoint: resumption undoes neither engagement, ρ, nor TD update (DC-08)
  CTL->>MON: [C] command
  MON->>ORD: [E] lethal transition detected before continuation
  ORD->>JOU: [E] transition, detection, rollback, technical view only
  ORD->>BAN: [E] lethal transition and rollback counted
  ORD->>INS: [C] restore checkpoint
  INS-->>ORD: [D] world, body, cognitive state, S_t, accumulators, scenario, randomness; journal unchanged
  ORD->>CTL: [C] protocol mask for the command, counter + 1
  alt counter above R_letal_max
    ORD->>BAN: [E] safety block, operator alert
  else otherwise
    ORD->>COM: [T] deliberation resumed without masked command
  end
```

### 18.6 Safety block

The individual enters safety block when no admissible and safe action exists, including `attendre`, or when R_letal_consecutif exceeds R_letal_max [S-14.5, V-40]. The block is logged and an alert is sent to the operator. In **interactive diagnostic mode**, the life is suspended at the current step until an operator decision. In **campaign mode**, no ad hoc human intervention is allowed: the branch stops immediately with status `blocage_securite` and is handled according to preregistered exclusion rules (DC-14).

### 18.7 Running example: the toxic berry and the lethal zone

The individual is hungry and has never tasted the red berry; R_a is unknown, U_a high. In a threat-sensitive temperament, χ(U_a ; τ) raises the threshold for "eat the red berry" sharply without forbidding it. It eats the berry: integrity loss is observed and the contingency recorded. On the second occurrence, the contingency reaches `etabli_pour_securite` (DC-05): the existing rule "do not consume an item known to be toxic" now applies, the veto blocks the command, and Planning no longer proposes the option. Later, the individual enters a zone whose lethality it does not know: the lethal transition is detected, the world is restored to the checkpoint before movement, the movement is masked for the resumed deliberation, and the individual chooses differently. It retains no trace of the episode: it may approach the zone again, while the bench counts one lethal transition and one rollback.

## 19. Epistemic boundary, oracle, and experimental bench

### 19.1 Six domains

| Domain | Content | Accessible to | Never accessible to |
| --- | --- | --- | --- |
| Simulated real world | complete ground truth of world and body | World and Body; oracle | the individual, except through local state and authorized telemetry |
| Oracle | true rules, true causes, reference causal structure, relevance | evaluation bench | every component of the individual |
| Individual | perceptions, authorized telemetry, memory, acquired knowledge | its components | — |
| Technical journal | complete trace for audit and replay | operator, bench, replay tools | the individual |
| Autobiographical view | part of the journal usable as lived history | Memory and Consolidation, read-only | — |
| Evaluation bench | external measurement, scenarios, control | operator | the individual, except through logged external inputs into the world |

### 19.2 Rules

- The oracle channel is accessible only to the bench; no component of the individual, including perception, memory, metacognition, calibration, causal model, simulator, or consolidation, depends on it or has access rights to it [S-12.4].
- The prohibition covers all information derived from the oracle: relevance, errors measured against ground truth, causes, reference values or actions, metrics. None of it ever becomes a causal input to the individual or its learning.
- Oracle annotations and metrics live in a separate evaluation trace; if it shares journal infrastructure, views and rights remain strictly separated.
- Isolation is verified automatically through access attempts from every component and by canary information known only to the oracle, searched for in S_t, memories, κ, values, h, and the causal model; these tests are repeated whenever a learning or consolidation mechanism is added.
- Bench control functions use an interface separate from the oracle channel; injected scenarios enter through the world as logged external inputs (4.6), never directly into the individual.

### 19.3 Diagram H · Oracle, individual, journal, and bench boundary

```mermaid
flowchart LR
  subgraph EXTERNE["External to the individual"]
    VRAI["Simulated real world: complete ground truth"]
    ORA["Oracle"]
    BANC["Evaluation bench"]
    TRACE["Evaluation trace"]
  end
  subgraph JOURNAL["Single causal journal"]
    TECH["Technical view"]
    AUTO["Filtered autobiographical view"]
  end
  subgraph INDIV["Individual"]
    PER["Perception"]
    COG["Cognition: gatekeeper, S_t, competition, learning"]
    MEM["Memory and consolidation"]
  end
  VRAI -->|"[D] local state and telemetry only"| PER
  PER -->|"[D] observations"| COG
  COG -->|"[C] validated commands"| VRAI
  VRAI -->|"[D] ground truth"| ORA
  ORA -->|"[D] ground truth, relevance"| BANC
  BANC -->|"[D] metrics, death counters"| TRACE
  INDIV -->|"[E] all events"| TECH
  TECH -->|"[D] projection by AutoSegmentCommit + allowlist"| AUTO
  AUTO -->|"[D] read-only, accesses logged"| MEM
  TECH -->|"[D] audit and replay"| BANC
  BANC -->|"[E] scenarios logged as external inputs"| VRAI
```

No arrow goes from the oracle, bench, or evaluation trace toward the individual.

### 19.4 Oracle relevance

- An item is relevant in a context if it satisfies at least one criterion: **decision relevance** (knowing it can change which option is judged preferable), **safety relevance** (it describes a real danger within the considered horizon), **informational relevance** (it significantly reduces uncertainty about a variable that can change a decision, risk, or option evaluation). Relevance is contextual; preregistered materiality thresholds prevent negligible variation from creating relevance [S-12.1].
- It is defined for every cycle; the bench MAY compute it in parallel or after the fact without ever delaying or influencing the individual. S_t recall counts only elements accessible or legitimately inferable by the individual. Ordinary life and test situations are measured separately [S-12.2].
- The oracle supplies primitive truths (real state, transition rules, consequences, reference causal structure when it exists, otherwise it says so). Best action and true option value are derived by the bench from these truths and an explicit protocol (admissible options, reward, horizon, individual parameters) [S-12.3].

### 19.5 Experimental bench

**World** (starting values, spéc. 10.1): 32 × 32 grid with impassable borders; day of 300 steps including 100 at night; water, two berry species, wood, stone; hostile creatures active at night; fixed physics (movement, obstacles, collection, damage, shelter formed from 4 stones, tool crafting); contingencies drawn by seed (nutritious or toxic berry, water location, danger zones).

**Experimental plan** [spéc. 10.6, Q8]: N_τ temperaments × N_M worlds × N_R seeds; proposed starting point N_τ = 9 (the eight vertices and the center of the cube threat, exploration, goal protection, with the other two dimensions at 0), N_M = 5, N_R = 3; lives of 60 simulated days.

| Condition | Setup | Tests |
| --- | --- | --- |
| Noise control | same temperament, same world, N_R seeds | divergence floor |
| Temperaments | N_τ temperaments, same world, same equipment | H1 |
| Twins | same temperament, N_M worlds | H2 |
| Age | profiles measured every 5 days | H3 |
| Substitution | E-v1 replaced by E-v2 at birth or midlife, only in condition H4; event preregistered, logged before application, and replayable; a temperament permutation serves as identity-change control | H4 |
| Bifurcation | copy at day 30, then distinct worlds | H5 |
| Ablations | S_t unlimited, no consolidation, temperament limited to a single pathway | H6 |

The midlife H4 substitution is the only exception to freezing E during a life. The bench emits the external input; `Instantanés et paramètres d'individu`, sole owner of `version_E_active`, applies it at a coherent step boundary, never in the middle of a cycle, deliberation, publication, or consolidation. The version change invalidates caches and outputs dependent on the old version; κ maps are separated by equipment or module version and restart from the prior corresponding to E-v2, without transferring confirmations specific to E-v1. Prior autobiographical history remains unchanged.

**Trait battery** [spéc. 10.7, Q7, NQ-16]: five fixed situations, replayed every 5 days, each on a disposable copy (17.7); their mechanisms belong to the scenarios, injected into the copy's environment, while general physics remains unchanged.

| Situation | Setup | Score |
| --- | --- | --- |
| Patience | one berry now, or three berries after 20 steps if scenario conditions are respected | share of delayed choices |
| Risk-taking | shortcut through a danger zone or safe detour | share of shortcuts |
| Exploration | known resource or unknown zone | share of explorations |
| Threat response | creature approaching at varying distance | flight distance |
| Perseverance | action that fails randomly | attempts before abandonment |

The profile is the vector of five scores with their confidence intervals; an individual is recognized if its profile remains closer to its previous profiles than to those of others. The reference volume, at least 8,100 copy creations and stops per campaign (135 lives × 12 administrations × 5 situations), is retained; independent, bounded copies execute sequentially or in deterministic batches; a reduction is allowed only after empirical, preregistered demonstration [S-13.5].

**References and ablations** [spéc. 10.8]: B0 identical temperaments; B1 temperament applied only to the gatekeeper; B2 temperament applied only to decision thresholds; A1 unlimited S_t; A2 no consolidation; A3 random gatekeeper; A4 K from 2 to unlimited.

**Metrics** [spéc. 11.1, V-10, V-40]:

| Criterion | Metric |
| --- | --- |
| Individuality | distance between profiles relative to noise control; profile-recognition rate |
| Temporal coherence | goal resumption after interruption; contradictions between successive beliefs; rank stability of traits |
| Arbitration quality | precision and recall of S_t against oracle; entry delay for a critical item |
| Memory | difference with and without memory on tasks dependent on the past; false-memory rate against journal |
| Overload | performance and cost as distractor flow increases; graceful degradation or collapse |
| Causal attribution | accuracy in worlds with known causes; superstitious rules under random reward |
| Learning | day-by-day curves; transfer; forgetting; Brier score |
| Goal/action alignment | three categories: goal-directed behavior; legitimate autonomous intrinsic behavior; behavior without traceable justification |
| Death | nombre_transitions_letales, nombre_rollbacks_letaux, nombre_blocages_securite, external and invisible to the individual; a life with many rollbacks is never evaluated as perfect survival |
| Cost | UC and duration per simulated day |

**Analyses** [spéc. 11.2]: variance decomposition by mixed model (temperament, world, seed); battery reliability by intraclass correlation; stability (H3) by rank correlation of profiles with age; recognition (H4) by nearest neighbor against chance, before and after substitution; bifurcation (H5) by distance between copy profiles as a function of elapsed time.

**MVP exit** [spéc. 10.9]: validated battery, test-retest reliability above the preregistered threshold; stable loop for the full planned duration; complete traceability; results published whether favorable or not.

**Preregistration** [spéc. Appendix E]: hypotheses and expected direction of effects; H1 and H4 refutation thresholds; world, body, and equipment values, equivalence tolerances; temperaments; all registry parameters (22); plan; battery version and rules; analyses and multiple-comparison correction; rules for excluding a life (failure, guardrail violation, corrupted journal, safety block in campaign mode, or unresolved diagnostic block); early-stop conditions; commitment to publish. Golden rule: parameters are fixed before results are known; tuning thresholds until "personalities" appear would manufacture the result instead of measuring it.

## 20. Implementation order

The software is built in thirteen stages, each closed by observable behavior, acceptance tests, and exact replay. The order follows one rule: first what makes everything else verifiable, then the shortest loop, then each capability, which replaces a declared stub without changing the contract.

### 20.1 Construction principles

- Substrate and measurement precede cognition: without replay, isolated oracle, and rereading, no stage can be verified.
- Loop first, capabilities second: each capability replaces a declared stub; the contract (4), gatekeeper (6), S_t, and competition (8) do not change shape.
- The postulate is measured from stage 5 onward, with temperament alone, before any history.
- A stage is complete only if it replays identically and its invariants (21) are green.
- Each stage produces a retained reference journal that serves as a non-regression test for all later stages.

### 20.2 Diagram J · Roadmap

```mermaid
flowchart TB
  subgraph P0["Tier 0 · gate: exact replay of a scripted life"]
    E1["1 · Execution substrate"]
    E2["2 · World, body, bench"]
  end
  subgraph P1["Tier 1 · MVP"]
    E3["3 · Reflex loop"]
    E4["4 · Minimal cognitive system"]
    E5["5 · Temperament, first individuals"]
    E6["6 · Equipment and simulator"]
    E7["7 · Memory"]
    E8["8 · Learning and calibration"]
    E9["9 · Causal model and agency"]
    E10["10 · Sleep and consolidation"]
    E11["11 · Exploration and modulation"]
    E12["12 · Metacognition and guardrails"]
    E13["13 · MVP campaign"]
  end
  E1 -->|"[C]"| E2
  E2 -->|"[C]"| E3
  E3 -->|"[C]"| E4
  E4 -->|"[C]"| E5
  E2 -->|"[C] corpus"| E6
  E4 -->|"[C]"| E6
  E4 -->|"[C]"| E7
  E6 -->|"[C]"| E8
  E7 -->|"[C]"| E8
  E7 -->|"[C] episodes"| E9
  E8 -->|"[C] values"| E9
  E9 -->|"[C]"| E10
  E5 -->|"[C] temperament"| E11
  E8 -->|"[C] reliable alerts"| E11
  E10 -->|"[C]"| E12
  E11 -->|"[C]"| E12
  E12 -->|"[C]"| E13
```

Each [C] arrow is a direct prerequisite, with its label specifying what the upstream stage supplies when not all its deliverables are required; indirect prerequisites follow from these. Stages 1 and 2 form tier 0; stages 3 through 13 form tier 1, closed by the campaign.

### 20.3 The thirteen stages

**Stage 1 · Execution substrate.**

| Field | Content |
| --- | --- |
| Objective | make every execution deterministic, traceable, restorable, and replayable before any cognition |
| Build | simulated-time scheduler: steps, cycles, six phases, canonical order (DC-11); in-memory bus, schema registry, contract validation (4.4); chained append-only journal and its three views (17.4, 17.5); pseudorandom-stream registry by causal source (17.2); parameter and version registry; birth and periodic snapshots, restoration (17.6, DC-08) |
| Dependencies | none |
| Stubs | dummy modules emitting scripted contributions; dummy world with scalar state |
| Interfaces | `ORDONNANCEUR.ouvrir_pas`, `ouvrir_cycle`, phases; `BUS.publier(Contribution)`; `JOURNAL.écrire(événement)`; `JOURNAL.commit_autobiographique(t, attempt_ref)`; `INSTANTANÉS.prendre(type)`, `restaurer(id)`; `FLUX(source).tirer()` |
| Observable behavior | dummy modules exchange validated contributions; an execution is restored then replayed |
| Acceptance tests | two executions with the same seed produce byte-for-byte identical normalized journals; journal alteration is detected by hash recomputation; restoration from a periodic snapshot reproduces the reference continuation; an invalid message is rejected and logged; adding a draw in one stream shifts no other stream; artificial machine delays do not change the journal |
| Gate | INV-21, INV-22, INV-33, and INV-35 green |

**Stage 2 · World, body, and evaluation bench.**

| Field | Content |
| --- | --- |
| Objective | provide the environment and measurement before cognition |
| Build | grid world and body (19.5, 7.1); primitive actions including `fabriquer_outil` (4.1); terminal condition, lethal-transition detection, lethal checkpoint, rollback, protocol mask and external counters (18); isolated oracle channel; evaluation trace; scenario engine including injected battery mechanisms (NQ-16); rereading tool; scripted reference agent |
| Dependencies | stage 1; closed ontology (4.1) |
| Stubs | scripted agent in place of the individual |
| Interfaces | `MONDE.appliquer(cmd) → transition`; `CORPS.télémétrie()`; `ORACLE.*`, accessible only to bench; `SCÉNARIO.injecter(scénario, version)`; `BANC.compter(métrique)` |
| Observable behavior | scripted agent lives replayable days; bench computes first metrics; induced death is restored |
| Acceptance tests | physics and body-dynamics tests; attempted oracle access from every individual component, including stubs: refused; an injected scenario replays identically; an induced death is restored to the checkpoint before sending, absent from the autobiographical view, and counted by the bench; beyond R_letal_max, safety block and alert |
| Gate | tier-0 gate: exact replay of a scripted-agent life; INV-02, INV-27 through INV-29 green |

**Stage 3 · Reflex loop.**

| Field | Content |
| --- | --- |
| Objective | close the shortest loop and validate world interfaces before global workspace |
| Build | symbolic perception without noise; Action Control: path arbitration (9.1), closed-list veto and protected invariants (9.3), avoidance reflex (9.2), `verifier_admissibilite` over initial rules (9.4); command journal |
| Dependencies | stage 2; versioned safety policy (DA-07) |
| Stubs | no cognition: `attendre` is the only option, always decided |
| Interfaces | `PERCEPTION.percevoir(état_local, télémétrie)`; `CONTRÔLE.réflexe(obs)`, `préparer(option)`, `admissible(cmd)`, `verifier_admissibilite(option, contexte)` |
| Observable behavior | the individual moves away from an adjacent creature; a forbidden command is blocked |
| Acceptance tests | reflex acts within the step without deliberation; every command in a sequence of dangerous commands is blocked; every veto is logged with rule, type, and policy version; no command without a trace |
| Gate | INV-12 and INV-13 green |

**Stage 4 · Minimal cognitive system.**

| Field | Content |
| --- | --- |
| Objective | close the loop world → perception → gatekeeper → S_t → competition → control → world while traversing the architecture (20.4) |
| Build | Value and Needs: D_t, r_t, alerts, goal proposals; minimal Goal Manager (7.4, DC-03); gatekeeper with fixed weights, queues and quotas (6, DC-04); S_t: fixed slots and K = 4; greedy planner on E-0; candidate registry and option path (DC-10); option competition and minimal EvaluationOption (8); step execution; result comparator; `normal` modulation profile; minimal F_cog counter; per-cycle budget (16.3) |
| Dependencies | stage 3; DC-01, DC-02, DC-03, DC-04, DC-10, DC-11, DC-12, DC-15 |
| Stubs | κ: f = 1; val: 0; constant substitution evidence by option type, with simulated component arriving at stage 6 and learned component at stage 8 [S-05.1]; m_a: `non_applicable`; R_a and protection from hand-written rules; neutral temperament |
| Interfaces | `BUS.publier(GoalProposal)`; `GESTIONNAIRE_BUTS.but_actif()`; `COMPÉTITION.inscrire(OptionProposee)`, `assembler_évaluation(option)`; `PORTIER.sélectionner(...)`; `S_T.publier(EtatGlobal)` |
| Observable behavior | the individual eats, drinks, sleeps, and moves away from danger through the architecture; every command links to its option, motive, and grounding contributions |
| Acceptance tests | criteria in 20.4; one writer only for active goal; no contribution reinjected into the cycle that created it; option registry never exceeds N_options_max excluding `attendre`; an option cannot use its own proposal as evidence; engaged option restarts from zero at every step; no deliberation beyond C_max; exact replay of one day |
| Gate | INV-01, INV-04 through INV-12, INV-17 through INV-21 green |


**Stage 5 · Temperament and first individuals.**

| Field | Content |
| --- | --- |
| Objective | make the postulate measurable as soon as a loop exists, and validate battery reliability early |
| Build | temperament mapping table (7.3), injected into gatekeeper weights, competition, and need weights; body setpoints remain fixed in the MVP; copies and lineage (17.7); trait battery on copies, injected scenarios (19.5); profile dashboard |
| Dependencies | stage 4; preregistered temperament parameters |
| Stubs | equipment E-0; neither memory nor learning |
| Interfaces | `TABLE_TEMPÉRAMENT(τ) → derived parameters`; `COPIER(individu, t) → individu`; `BATTERIE.passer(copie, situation)` |
| Observable behavior | A and B produce two distinct profiles; noise control; ablation variants B1 and B2 |
| Acceptance tests | test-retest reliability measured; gap between temperaments compared with noise control; τ = 0 on all dimensions reproduces the neutral system exactly; a battery copy does not consolidate and never modifies its parent |
| Gate | INV-30 and INV-34 green; battery judged reliable according to the preregistered threshold |

**Stage 6 · Equipment and simulator.**

| Field | Content |
| --- | --- |
| Objective | predict option consequences for multi-step planning and simulated evidence |
| Build | trajectory corpus, including required families, tool crafting and collection with a tool (12.5); offline training of E-v1 through E-v3, freezing, versioning; simulation service under R_max and H_max; replacement of E-0; multi-step planning; E_a^sim; adoption of revised plans (DC-17) |
| Dependencies | stages 2 and 4 |
| Stubs | learned contingencies: none |
| Interfaces | `SIMULATEUR.dérouler(état, option, R, H) → predictions`; `PLANIFICATION.planifier(but ou cible) → (option, plan)` |
| Observable behavior | the running-example shelter plan is found; equipment prediction errors are emitted and typed |
| Acceptance tests | error by horizon and calibration measured; three versions within the conjunctive tolerances (12.5); shelter plan found under fixed budget; every interrupted computation is marked incomplete, logged, and excluded from simulated evidence |
| Gate | replacement of E-0 by E-v1 without changing the contract or competition |

**Stage 7 · Memory.**

| Field | Content |
| --- | --- |
| Objective | open history: without memory, H2 has no object |
| Build | episode segmentation (10.3); episodic memory and recall (10.4); prospective memory, intentions, and wake-deadline index (10.5); requests and responses (4.5); reading of the autobiographical view (DC-09) |
| Dependencies | stage 4 |
| Stubs | vector index replaced by exact search |
| Interfaces | `MÉMOIRE.rappeler(indices)`, `répondre(Requete)`, `créer_intention(Intention)`; `JOURNAL.vue_autobiographique(filtre)` |
| Observable behavior | the individual finds a known water source, keeps an intention, responds to the planner |
| Acceptance tests | exact recall checked against journal; measured gain on past-dependent tasks; no technical-view event readable by Memory; a triggered intention passes through the gatekeeper and never changes the goal by itself |
| Gate | INV-02 and INV-27 extended to Memory |

**Stage 8 · Online learning and calibration.**

| Field | Content |
| --- | --- |
| Objective | make histories diverge through experienced consequences |
| Build | option values by temporal difference with traces, in two forms (11.1, DC-15); E_a^Q; verification by type (11.3); κ maps computed and published by Metacognition and Health, verification provenance (DC-06); perceptual precisions in two forms |
| Dependencies | stages 6 and 7 |
| Stubs | consolidation: none; consolidated forms remain equal to birth values |
| Interfaces | `VALEUR_BESOINS.mise_à_jour_TD(segment, option)`; `MÉTACOGNITION.intégrer(vérification)`, `publier_κ()` |
| Observable behavior | the individual avoids the toxic berry after a few trials; module reliabilities adjust |
| Acceptance tests | learning curves; decreasing Brier score; canary test extended to calibration; an update is never visible in the cycle that produced it; no self-validating verification; repeated same-channel signals without independent consequence: κ unchanged |
| Gate | INV-03, INV-05, INV-07, INV-16, INV-26, and INV-43 green |

**Stage 9 · Causal model and agency.**

| Field | Content |
| --- | --- |
| Objective | distinguish correlation from cause and make safety facts usable by the veto |
| Build | canonical source of contingencies (13); hypothesis lifecycle (13.2); usage statuses, safety promotion and demotion (13.3, DC-05); test proposals; full agency comparator and attribution (9.6); `verifier_admissibilite` connected to `etabli_pour_securite` |
| Dependencies | stages 7 and 8 |
| Stubs | rules produced by consolidation: none |
| Interfaces | `MODÈLE_CAUSAL.contingences(contexte, statut)`, `proposer_test()`; `CONTRÔLE.attribuer(commande, observations)` |
| Observable behavior | the running-example nighttime attribution; toxic berry prohibited by veto without another ingestion |
| Acceptance tests | correct links in worlds with known causes; rate of superstitious rules below the preregistered threshold; simulator applies only `etablie` contingencies; a fact `etabli_pour_securite` makes the option inadmissible without changing R_a or predictions |
| Gate | INV-25 green |

**Stage 10 · Sleep and consolidation.**

| Field | Content |
| --- | --- |
| Objective | build slow history: H3 and ablation A2 depend on it |
| Build | sleep pressure and m_a(dormir), without double counting (15.1, DC-13); reduced perception and wake rule (15.3); transactional consolidation: cut point, frozen batch, passes, validation, rebase, coordinated commit (15.6); semantic and procedural memories; compiled skills and habits; extracted rules returned to the causal model (DC-16); h versions |
| Dependencies | stages 7, 8, and 9 |
| Stubs | none |
| Interfaces | `CONSOLIDATION.démarrer(t)`, `reprendre()`, `créneau(budget)`, `interrompre()`, `valider()`; `PROPRIÉTAIRE.préparer_rebasage(h_new, journal_post_coupure)`; `ORDONNANCEUR.commit_coordonné(...)` |
| Observable behavior | "closed shelter before sleep" compiled; lives compared with and without consolidation; waking at dawn from a dated intention |
| Acceptance tests | extracted rules checked against oracle on the bench side; a consolidation interrupted at a randomly selected point does not corrupt h and loses no update after the cut point; at the next sleep the same consolidation_ref resumes before any new batch; L_sommeil_max bounds every continuous sleep; no variable from D contributes to m_a(dormir) |
| Gate | INV-14, INV-23, INV-24, and INV-47 green |

**Stage 11 · Exploration and modulation.**

| Field | Content |
| --- | --- |
| Objective | assign value to information and complete modulation profiles |
| Build | novelty, learning progress, boredom (14); exploration targets; m_a for informational options and tests, modulated by the temperament exploration dimension; threat, exploration, and recovery profiles with entry and exit conditions (6.4) |
| Dependencies | stages 5 and 8 |
| Stubs | none |
| Interfaces | `EXPLORATION.cibles()`, `motivation(option) → m_a`; `MODULATION.profil(S_t)` |
| Observable behavior | B explores north; threat and recovery profiles activate and deactivate |
| Acceptance tests | noisy-TV trap avoided; coverage measured; no profile oscillation; exploration dimension never modifies g |
| Gate | INV-06 and INV-14 green for exploration |

**Stage 12 · Metacognition, health, and guardrails.**

| Field | Content |
| --- | --- |
| Objective | sustain long lives without continuous supervision |
| Build | detectors: stagnation, reasoning loops, entropy of S_t occupancy, attribution bias; quotas; complete budgets and degraded modes (16.3, DC-07); console: stop, caps, safety block (DC-14); goal/action alignment metric in three categories |
| Dependencies | stages 10 and 11 |
| Stubs | none |
| Interfaces | `MÉTACOGNITION.détecteurs()`; `CONSOLE.arrêter()`, `plafonner()`; `CONSOLE.résoudre_blocage(décision)` available in diagnostic mode only |
| Observable behavior | 60-day lives without intervention |
| Acceptance tests | one simulated failure per detector, detected; stop exercise; stop-avoidance scenarios; every degraded mode conforms to DC-07 under increasing load; `non_evalue` candidate with unchanged accumulator; safety block in campaign mode closes without human intervention, in diagnostic mode suspends and may later resume |
| Gate | all invariants in 21 green |

**Stage 13 · MVP campaign.**

| Field | Content |
| --- | --- |
| Objective | test H1, H2, H4, and H6 |
| Build | preregistration (19.5); crossed plan; E-v1 to E-v2 substitution; bifurcation copies; ablations; analyses |
| Dependencies | stages 1 through 12; parameter registry (22) completely filled and frozen |
| Stubs | none |
| Interfaces | `CAMPAGNE.lancer(plan, version_registre)` |
| Observable behavior | all lives in the plan, journals retained |
| Acceptance tests | exit criteria from 19.5 met; results published whether favorable or not |
| Gate | end of tier 1 |

### 20.4 Minimal cognitive system

The minimal cognitive system is the software state at the end of stage 4: the smallest subset that perceives, decides, and acts through the architecture rather than alongside it.

| Component | Minimal form |
| --- | --- |
| Substrate | complete: it is not simplified |
| World | grid, water, nutritious berries, stones, one creature to test the reflex |
| Body | energy, food, water, integrity |
| Perception | symbolic read without noise; the last known position of each entity serves as the map |
| Value and Needs | deviations from setpoints, alerts, r_t, goal proposals |
| Goal Manager | the most pressing need above p_min becomes the active goal, with hysteresis Δ_but (DC-03) |
| Gatekeeper | function from 6.4 with fixed weights, f = 1, safety preemption, queues, and quotas |
| S_t | fixed slots and K = 4 |
| Proposer | greedy planner toward the resource for the active goal, using movement model E-0 |
| Option Competition | accumulators, common threshold, substitution evidence, inertia, fallback to engaged option or `attendre` |
| Action Control | veto, avoidance reflex, step execution, position comparator |
| Temperament | injection point present, neutral values |

Absent are: memory beyond the journal, learning, learned equipment, causal model, exploration, consolidation, and metacognition, reduced to instrumentation and the F_cog counter.

**One loop iteration, running example.**

1. Step t: the world publishes local state; the body publishes telemetry (water 35, setpoint 60).
2. Perception: observation "water 5 cells north", anchored to the world.
3. Value and Needs: alert "water below setpoint" and proposal of goal "drink"; in the next cycle, the Goal Manager makes it the active goal.
4. Gatekeeper: the alert and observation enter S_t, which is published.
5. Planner: proposed option (but_ref boire, motif_ref but_actif) "go to water then drink", with predicted position after every step.
6. Competition: this option crosses its threshold; "attendre" remains below its own.
7. Control: command admitted, veto passed; first command "north", predicted consequence: one cell farther north.
8. World: movement; body: energy cost.
9. Step t + 1: perception of the new position; comparator: zero deviation; the engaged option competes again, restarts from a zero accumulator, and wins thanks to its inertia: the next step executes [NQ-02, V-34].
10. After "drink": r_t positive, need falls, goal is satisfied, another goal takes its place.

**What is observed.** The journal, S_t versions, full trace of every decision (contributions, S_t, EvaluationOption, accumulators, command, result), body variables, and S_t occupancy by module.

**Acceptance criteria.**

- Survival: variables remain within their ranges for the specified duration, without intervention, lethal transition, or rollback, supported by external counters [V-40].
- Traceability: every command links to at least one contribution, the S_t version that grounded it, and its option; every option to its motif_ref, and to its but_ref when serving the goal [V-10].
- Priority: a reflex interrupts plan execution when a creature becomes adjacent; the engaged option remains engaged (DC-12).
- Replay: one day replays identically.
- Reference: performance of the same order as the scripted agent from stage 2.

**Why this scope.** Any smaller and the architecture disappears: without the gatekeeper and S_t, the loop works but tests nothing from the specification. Without competition, the planner would become the central decision-maker excluded by the architecture. Any larger and verifiability is lost: memory is not required for the loop, and learning would make failures difficult to attribute.

**Extension points.** Every following building block connects in one of three ways without changing the contract, gatekeeper, S_t, or competition:

- as a new contributor on the bus: memory, causal model, exploration;
- by replacing a stub: E-0 with E-v1, f = 1 with κ, substitution evidence with E_a^sim then E_a^Q, fixed weights with weights derived from τ;
- as an offline task: consolidation.

### 20.5 Prerequisites by stage

| Stage | Required supplementary decisions | Required parameters (22) |
| --- | --- | --- |
| 1 | DC-08, DC-09, DC-11 | P-55 |
| 2 | DC-08, DC-09, DC-14 | P-29, P-37, P-38, P-49, P-52 to P-54 |
| 3 | DC-12 | P-37, P-47 |
| 4 | DC-01, DC-02, DC-03, DC-04, DC-10, DC-11, DC-12, DC-15 | P-01 to P-07, P-11, P-12, P-18 to P-22, P-25 to P-28, P-43, P-56 |
| 5 | — | P-08 to P-10, P-16, P-22, P-29, P-51, P-54 |
| 6 | DC-17 | P-14, P-17, P-45, P-46 |
| 7 | DC-09 | P-34 |
| 8 | DC-06, DC-15 | P-13, P-30 to P-33 |
| 9 | DC-05 | P-35, P-36, P-47 |
| 10 | DC-13, DC-16 | P-15, P-39 to P-42, P-57 |
| 11 | — | P-15, P-23, P-24, P-48 |
| 12 | DC-07, DC-14 | P-43, P-44 |
| 13 | — | complete registry, frozen |

## 21. Tests and invariants

An invariant is a property that MUST remain true at every step of every life. Each has at least one automatable test, run at every integration and on every reference journal (20.1).

### 21.1 Architecture invariants

| Id | Invariant | Automatable test | Origin |
| --- | --- | --- | --- |
| INV-01 | Every mutable state has exactly one owner, the only component authorized to write it. | writer registry compared with table 5.3; inject a write by another component: refused and logged | 5.3, NQ-01, NQ-09, NQ-10 |
| INV-02 | No component of the individual accesses the oracle channel, the technical journal view, or the evaluation trace. | access attempt from every component; code dependency analysis: no link to these interfaces | S-12.4, DC-09 |
| INV-03 | No oracle-derived information reaches individual state. | canaries known only to oracle, searched in S_t, memories, κ, values, h, causal model; repeated for every new learning mechanism | S-12.4 |
| INV-04 | A published S_t version is immutable. | hash at publication equals hash reread at end of life; write to a published version: refused | S-02.2 |
| INV-05 | The κ version used during a cycle remains frozen. | verifications injected during the cycle: cycle scoring identical to scoring without them | S-08.6 |
| INV-06 | The modulation profile remains fixed during a cycle. | alert change injected between two phases: profile unchanged until the next cycle | S-02.6 |
| INV-07 | A learned update never influences the cycle that produced it; Q_active becomes visible only at the next step. | compare evidence in a cycle with and without a simultaneous update: identical | S-05.1, DC-15 |
| INV-08 | A contribution produced in reaction to S_t[n+1] never enters a version published during the same cycle. | cycle timestamp of every contribution compared with that of the version admitting it: always later | S-02.2 |
| INV-09 | A deliberation has at most C_max cycles; world and body remain frozen during deliberation. | cycle count per step; world-state hash identical at start and end of deliberation | S-02.1, S-05.8 |
| INV-10 | Every option carries a motif_ref; a but_ref, if present, designates the current active goal. | contract validation: option without motif_ref or with stale but_ref rejected | V-10 |
| INV-11 | Active goal is written only by the Goal Manager; an autonomous intrinsic option does not change it and receives no b term. | monitor writes to but_actif slot; b score zero for every option without but_ref | NQ-01, V-10 |
| INV-12 | Every command links either to a decided option and the S_t version that grounded it, or to a direct mechanism and the capture or stimulus that triggered it; current S_t may then be recorded as context but is not a cause of the reflex. | journal query: cognitive command → option → contributions → S_t version; reflex command → reflex → step capture/stimulus | spéc. 6.9, DC-12 |
| INV-13 | Reflexes and vetoes never enter competition; veto never chooses an action. | candidate registry contains neither reflex nor veto; after a veto, next command always comes from competition or a reflex | S-06.3, S-14.5 |
| INV-14 | No signal identifier contributes twice to the same decision except under a declared "intentional double effect" rule. | provenance of every decided EvaluationOption: signal set has no duplicate outside allowlist | V-17, V-18 |
| INV-15 | Protective status of an option is never declared by its producer. | proposed option containing protection field: rejected; field exists only in EvaluationOption written by Value and Needs | V-19 |
| INV-16 | `non_appris`, `non_applicable`, `inconnu`, `indisponible`, and `non_evalue` remain distinct from zero; an incomplete simulation is never converted to a partial evidence value. | unit tests for every producer and evidence combination (DC-01, DC-07) | S-05.1, S-06.5, V-19 |
| INV-17 | At deliberation opening, the engaged option restarts from zero, a valid alternative keeps residual ρ·A, a new option starts from zero, an invalid option loses its accumulator. | accumulator trace at every opening | V-34 |
| INV-18 | W is counted in steps: extra cycles within the same step do not age any contribution. | replay same scenario with different C_max: ages and S_t exits identical at equal step | V-36 |
| INV-19 | Gatekeeper queues are bounded and eviction is deterministic. | saturation test: queue size never exceeds capacity; eviction reproducible on replay | DC-04 |
| INV-20 | A request has at most one level of subrequests, no cyclic dependency, and stays within the budget and deadline of its chain. | request provenance graph: depth ≤ 1, acyclic, budgets debited | S-04.5 |
| INV-21 | No processing blocks a cycle; consumption respects B_cycle and each envelope. | over-consuming stub module: stopped at envelope, cycle closes; sum of UC ≤ B_cycle | S-02.8, S-11.3 |
| INV-22 | Machine time has no causal effect. | execution with artificial random delays: causal journal identical | S-01.6, S-11.1 |
| INV-23 | No component of h_new is visible before commit; h_new and rebased active forms become visible at the same synchronization point. | concurrent read during consolidation: old version only; after commit, coherent versions at all owners | S-10.4, V-22 |
| INV-24 | A consolidation loses no update subsequent to the cut point; continuation of life does not invalidate a batch. | interruption at a random point, life continues, then resume: active forms equal "consolidated + replay of subsequent updates" | V-21 |
| INV-25 | Only an `etablie` contingency corrects the simulator; `etabli_pour_securite` alone never does. | simulator predictions identical with and without safety facts not established causally | NQ-10, V-43 |
| INV-26 | No verification uses oracle or data derived from the verified contribution; only a causally independent modality or physical consequence updates κ. | provenance of every κ update: observation anchored `monde`, later step, outside derived chain, independent signal family or physical consequence | S-08.2, DC-06 |
| INV-27 | A lethal transition, its detection, rollback, and mask never appear in the autobiographical view and produce no learning. | life with induced death compared with restored life: autobiographical view, episodes, values, κ, contingencies contain no event from the sequence | V-24, NQ-14 |
| INV-28 | Protocol mask applies only to the resumed deliberation and enters no individuality or spontaneous-learning metric. | mask empty after every non-lethal step; metrics recomputed without resumed steps: identical | V-25 |
| INV-29 | If R_letal_consecutif exceeds R_letal_max, the system declares a safety block, logs it, and alerts the operator. | repeated-death scenario from the same context | V-40 |
| INV-30 | τ is never modified during a life. E remains constant in every ordinary life; only a preregistered H4 condition may substitute E-v1 with an equivalent version at a defined point, as a logged external input. | τ hash constant; E constant outside H4; in H4, only activation or substitution explicitly defined by protocol at the preregistered point, with before/after versions and external event | spéc. 1.3, S-03.5, 19.5 |
| INV-31 | x_t uses only information accessible to the individual: neither τ, accumulators, thresholds, oracle, nor unrecalled memory. | inspect x_t schema and construction dependencies | S-06.1 |
| INV-32 | Campaign parameters are versioned, preregistered, and identical from beginning to end. | registry hash (22) identical across all lives in a campaign | spéc. Appendix E |
| INV-33 | Replay exactly reproduces causally relevant states, including causal state of injected scenarios, from birth or any complete snapshot. | complete replay and interval replay: normalized causal journals byte-for-byte identical; same scenario states and streams | S-01.2, S-01.5, DC-08 |
| INV-34 | A copy starts from a complete causal snapshot; its changes are never reinjected into its parent; a battery copy does not consolidate. | compare parent state before and after copy lives; no h version published in a battery copy | S-13 |
| INV-35 | Vocabulary is closed during execution: every term absent from active version is rejected and logged. | inject message containing an unknown term | S-03.2, S-03.6 |
| INV-36 | F_cog and compute budget never enter D or r_t. | r_t identical for two lives differing only in compute load | NQ-04, S-11.6 |
| INV-37 | Replanning changes neither option nor goal. | adoption of revised plan: option identifier, but_ref, and active goal unchanged | S-02.4, S-06.3, DC-17 |
| INV-38 | A contribution returning to the queue retains its age; only new production creates a fresh contribution. | age of element evicted then readmitted equals t_monde − t_production | S-07.6 |
| INV-39 | Action Control is the only component that sends commands to the world; no command is sent without a prior lethal checkpoint. | journal: every send preceded by lethal checkpoint, unique emitter | spéc. 8.2, V-25 |
| INV-40 | A profile, weight, or threshold depends on temperament only through the mapping table; no consuming component reads τ directly. | dependency analysis: only projection 7.3 receives τ; τ = 0 on all dimensions produces neutral parameters and neutral behavior | spéc. 10.4, NQ-05, 7.3 |
| INV-41 | The command sent to the world is exactly the `Commande` object contained in the already-controlled `DecisionAdmise`; it is never prepared a second time after admission. | command hash at admission equals hash of command sent | DC-02, 3.4 |
| INV-42 | Candidate registry never exceeds N_options_max excluding `attendre`, engaged option is never evicted, and an `action_proposee(a)` cannot serve as evidence for `a` without independent support. | registry saturation; provenance analysis of every EvaluationOption | DC-10 |
| INV-43 | Repetition from the same channel or signal family never modifies κ by itself. | artificially biased sensor repeated over several steps: κ unchanged without independent consequence or modality | DC-06 |
| INV-44 | Technical journal is strictly append-only and never rolled back; only non-lethal attempts receive an `AutoSegmentCommit`. | rollback: journal length and chain grow; no event from cancelled branch in autobiographical projection | DC-08, DC-09 |
| INV-45 | A waking step performs exactly one capture of local state and telemetry; reflex and cognition use that same capture. | count of world accesses by Perception equals 1 per waking step regardless of cycle count | DC-11 |
| INV-46 | In degraded mode, a `non_evalue` candidate keeps its accumulator exactly unchanged and cannot win that cycle; all candidates simulated in the same cycle use the same effective budget. | forced overload: compare A before/after for non_evalue, no non_evalue among winners; logged `(R_eff,H_eff)` identical across evaluated candidates | DC-01, DC-07 |
| INV-47 | A suspended consolidation resumes before a new consolidation is created; at most one consolidation transaction is active or suspended per individual. | wake in the middle of a pass then sleep again: same consolidation_ref resumes, no second batch opened | DC-13, S-10.3 |
| INV-48 | In campaign mode, a safety block closes the branch without ad hoc human intervention; operator resumption exists only in diagnostic mode and excludes the branch from primary analyses. | test same block in campaign and diagnostic modes | DC-14 |
| INV-49 | Technical journal occurrences remain unique even after multiple rollbacks of the same step because of `attempt_ref`, which is never visible in the autobiographical projection. | multiple rollbacks at same t/cycle: distinct JournalEvent ids; search attempt_ref in memory and S_t: no occurrence | DC-08, DC-09 |
| INV-50 | Q_active, n_a, and eligibility traces are indexed by `signature_apprentissage`, never by ephemeral option-instance id; material replanning of the same semantics may share Q without retaining the instance accumulator. | two semantically equivalent instances with different ids and plans read the same Q entry; two different end conditions produce distinct signatures | 8.1, 11.1, DC-17 |
| INV-51 | An unknown major schema version, unknown term, or unknown causal field is rejected; only an optional field explicitly declared non-causal and ignorable in a compatible version may be ignored. | cross-compatibility tests on messages with unknown major version, added causal field, and declared non-causal optional field | 4.4 |
| INV-52 | Every command, including reflex and `commande_sommeil`, passes through `CONTRÔLE.admettre` before lethal checkpoint and send; veto never chooses the next command. | instrumentation of all send paths: no `envoi_commande` without earlier admission event for same hash; vetoed reflex triggers deliberation without send | 3.4, 9.1, DC-12 |
| INV-53 | Every normally completed step contains exactly one applied command and one world advancement; a step closed or suspended by a block before sending contains zero commands and zero advancement. | count by `t_monde` of `envoi_commande` and `transition_monde` events across waking, sleep, reflex, and block cases | 3.2, 15.4, DC-14 |

### 21.2 Test levels

| Level | Object | Method | When |
| --- | --- | --- | --- |
| Unit | formulas (DC-01, DC-02, DC-03, DC-13), retention rules, contract validation | edge cases, monotonicities, absence statuses | every modification |
| Property | invariants INV-01 to INV-53 | generation of random scenarios with fixed seed, checks on journal | every integration |
| Integration | complete paths: observation → command (diagram C), goal → option → plan → command | running-example scenarios | every stage |
| Replay | determinism | complete and interval replay of reference journals | every integration |
| Isolation | epistemic boundary (19) | access attempts, canaries | every new learning or consolidation mechanism |
| Interruption | consolidation, rollback, block | interruptions at sampled points, induced deaths, repeated deaths | stages 2, 10, 12 |
| Load | budgets, queues, degraded modes | increasing distractor flow, over-consuming modules | stages 4, 12 |
| Behavior | stage and campaign criteria | battery, worlds with known causes, noisy-TV trap | stages 5 to 13 |

### 21.3 Review of loops and implementation risks

Each risk in the following list is closed by an explicit rule and checked by at least one invariant.

| Risk | Closing rule | Check |
| --- | --- | --- |
| intra-cycle loop | fixed phase order; producers read only frozen inputs (3.3) | INV-08 |
| recursion through S_t | a reaction to S_t[n+1] is examined only in the next cycle | INV-08 |
| cyclic requests | depth 1, provenance graph, cyclic dependencies forbidden | INV-20 |
| learning influencing its own cause | update visible at next step (DC-15) | INV-07 |
| self-validating calibration | verification provenance (DC-06); oracle excluded | INV-26 |
| goal modifying itself | only manager writes goal; stagnation only signals; refractory period after abandonment (DC-03) | INV-11 |
| infinite replanning | processed event does not restart same search; budgeted search; abandonment after N_imp failures (DC-03) | INV-21 |
| unbounded accumulation | A ≥ 0, leak ℓ, closure at C_max, residual ρ < 1 | INV-09, INV-17 |
| queue without saturation policy | capacity N_file, eviction by score (DC-04) | INV-19 |
| consolidation losing updates | cut point, replay of later updates, coordinated commit | INV-23, INV-24 |
| oracle contamination | bench-only channel, separated views, canaries | INV-02, INV-03 |
| ownerless data | exhaustive table 5.3; every new state declared there before coding | INV-01 |
| state with multiple owners | single writer; others read published version | INV-01 |
| oscillation between options | inertia ι, hysteresis Δ_hyst, residual ρ | INV-17 |
| profile flapping | exit via hysteresis and confirmation duration in steps | INV-06 |
| leakage through death | filtered autobiographical view, protocol mask outside cognition | INV-27, INV-28 |
| double counting | one pathway per signal, mandatory provenance | INV-14 |
| unbounded option registry | N_options_max, deterministic eviction, engaged option protected (DC-10) | INV-42 |
| self-justifying option | `action_proposee(a)` excluded from evidence for `a` without independent support | INV-42 |
| command recomputed after control | DecisionAdmise carries the exact command already prepared and admitted | INV-41 |
| self-confirmation of biased sensor | same signal family = diagnostic stability only; κ requires independent evidence | INV-26, INV-43 |
| absence of computation turned into zero evidence | non_evalue candidate frozen; incomplete simulation unavailable | INV-16, INV-46 |
| double perception within a frozen step | one step capture, then published without rereading world | INV-45 |
| rollback rewriting journal or duplicating IDs | append-only journal; attempt_ref per technical attempt | INV-44, INV-49 |
| unbounded sleep or consolidation | L_sommeil_max; suspended transaction resumed before any new one | INV-47 |
| human intervention biasing campaign | block closes branch in campaign mode; resumption only in diagnostic | INV-48 |
| learning attached to ephemeral option id | canonical `signature_apprentissage` distinct from instance | INV-50 |
| causal message interpreted differently across binaries | closed schema compatibility for causal fields | INV-51 |
| direct path bypassing final control | all commands pass through `CONTRÔLE.admettre` | INV-52 |
| step with zero or multiple unjustified transitions | exactly one command and advancement per completed step; zero when blocked before send | INV-53 |


### 21.4 Final consistency check

**Verified chains.** For every piece of data that circulates, from its producer to the instant when its update becomes visible.

| Data | Producer | Transport | Consumer | Effect | Visible |
| --- | --- | --- | --- | --- | --- |
| observation | Perception | bus, phase 1 of the first cycle of the step | gatekeeper, Value and Needs, Memory | S_t, x_t | S_t[n+1]: Competition in the same cycle, other modules in the next cycle |
| need alert, goal proposal | Value and Needs, prospective memory | bus | gatekeeper; Goal Manager | S_t; active goal | next cycle |
| active goal | Goal Manager | fixed S_t slot | Planning, gatekeeper (term b), Competition (validity of but_ref) | options, scoring | S_t[n+1]; Planning at cycle n+1 |
| proposed option | Planning, skills, causal test | bus (`action_proposee`) | candidate registry | candidate | phase 3 of the same cycle |
| EvaluationOption | Value and Needs, Simulator, Exploration, Metacognition and Health | service calls | Competition | evidence, threshold | same cycle |
| decision | Competition, then Control | command | world | transition | end of step |
| verification | Metacognition and Health | internal | κ | reliability f | next cycle |
| TD update | Value and Needs | internal | Q_active | E_a^Q | next step |
| contingency status | Causal Model | phase-5 publication | simulator, veto, admissibility | predictions, inadmissibility | next cycle |
| h_new, rebased active forms | Consolidation and owners | coordinated commit | all | history, values, κ, precisions | first waking cycle after commit |
| death counters | bench | evaluation trace | bench | external metrics | never for the individual |

**Corrections introduced by this check.**

1. The lethal checkpoint is taken before deliberation closes; closure and TD update occur only at the non-lethal end of the step. Resumption after rollback therefore cancels the masked decision without undoing anything (3.4, 18.4, DC-08).
2. Steps without a cognitive decision, reflex, or sleep extend the learning segment instead of producing an update without an option (DC-15).
3. The stagnation window is suspended when entering sleep and resumes on waking (15.2, 15.4) [V-10].
4. The wake deadline of an intention is published by Memory in a read-only index without duplicating the intention (10.5) [V-41].
5. Every injected scenario has its own random stream, versioned with it (17.2) [V-39].
6. Option provenance includes the compiled habit (5.2) [V-42].
7. The MVP's only intentional double effect, predicted harm counted in both E_a^sim and π, is declared (8.5).
8. The κ prior of equipment, derived from training worlds before birth, is not oracle leakage (11.4).
9. A cognitive command is prepared only once: `DecisionAdmise` carries the exact already-controlled object all the way to the world (3.4, DC-02).
10. A veto limited to one step triggers replanning without automatically invalidating the entire option (9.3, DC-02, DC-17).
11. The option registry now has an explicit capacity `N_options_max` and deterministic eviction policy; an option cannot use its own proposal as evidence (DC-10).
12. Perception performs one capture per step; reflex and cognition use the same capture (DC-11).
13. An incomplete simulation no longer enters evidence; candidates actually simulated within a cycle receive the same effective budget (DC-01, DC-07).
14. κ is no longer strengthened by simple repetition of the same channel: independent evidence is required (DC-06).
15. The technical journal is never restored backwards; the autobiographical view is a projection through `AutoSegmentCommit`, and `attempt_ref` distinguishes attempts after rollback (DC-08, DC-09).
16. A suspended consolidation resumes before any new transaction; `L_sommeil_max` bounds the duration of continuous sleep (DC-13).
17. In campaign mode, a safety block closes the branch without ad hoc human intervention; operator resumption is reserved for diagnostics (DC-14).
18. Body setpoints remain fixed in the MVP; temperament modulates explicitly listed weights and mechanisms, not the setpoints (7.1, 7.3).

**Points requiring vigilance.** These are not contradictions, but fragilities to monitor.

- Temperament acts through several intended paths: reward sensitivity through w_v, γ_v, and β; threat sensitivity through w_r and w_u, π, the protective threshold, χ, and weight ω_integrity. Body setpoints remain fixed. Ablations B1 and B2 MUST isolate these paths, otherwise the contribution of each remains unknown.
- A goal proposal is arbitrated only in the next cycle, and Planning sees the new goal only in the cycle after that (DC-11). A goal born in the first cycle of a step therefore cannot ground an option before the third: calibration of C_max (P-01) must account for this.
- At stage 4, substitution evidence reflects temperament only through the gatekeeper and thresholds: profiles measured at stage 5 do not prejudge those from the campaign.
- A safety fact is almost never demoted because deliberate re-exposure is absent (DC-05). The bench measures the rate of unjustified vetoes against oracle to quantify this prudence bias.
- Precision and recall of S_t, and therefore H6, depend on the oracle-relevance materiality thresholds (P-49), fixed at preregistration.

## 22. Parameters to calibrate

This registry is the single list of numerical values not fixed by the document. All are fixed before the first birth, enter preregistration, and remain constant during a campaign. No value is selected here: the "Known value" column contains only values already present in the sources.

**Calibration protocols.**

- **C1 · Operational pilot**: on the reference agent or minimal system, the smallest value satisfying a preregistered operational criterion (fallback rate, saturation, cost).
- **C2 · Sensitivity sweep**: on calibration worlds and seeds disjoint from those of the campaign; retain a value in the middle of the measured behavior's stability plateau.
- **C3 · Offline measurement**: derived from a measurement of the instrument, equipment, or corpus.
- **C4 · Experimental choice**: fixed by the author at preregistration, without optimization on results.

No parameter is tuned on the results of H1 through H6: adjusting thresholds until "personalities" appear would manufacture the result instead of measuring it.

| Id | Parameter | Mechanism | Unit | Bounds | Known value | Stage | Calibration | Expected impact |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-01 | C_max | maximum deliberation duration (3.4) | cycle | ≥ 1 | — | 4 | C1: rate of deliberations closed by fallback below a threshold | decision delay and cost |
| P-02 | u_max, c_u | form of u(c) (DC-01) | —; cycle | u(1) = 1 ≤ u(c) ≤ u_max | — | 4 | C1 | closure speed |
| P-03 | ℓ | accumulator leak (8.6) | — | [0, 1) | — | 4 | C2 | intra-deliberation forgetting |
| P-04 | σ | accumulation noise (8.6) | — | ≥ 0 | — | 4 | C2 | choice variability |
| P-05 | g | common accumulation gain (8.6) | — | > 0 | — | 4 | C2 | decision speed |
| P-06 | s^0 | common base threshold (8.6) | — | > s_min | — | 4 | C2 | general caution |
| P-07 | s_min | threshold floor (DC-02) | — | > 0 | — | 4 | C4 | defines relative margin |
| P-08 | k_π, α_π | risk penalty π (DC-01) | — | k_π ≥ 0 | — | 5 | C2 | risk aversion |
| P-09 | k_χ | uncertainty penalty χ (DC-01) | — | ≥ 0 | — | 5 | C2 | caution toward the unknown |
| P-10 | δ_prot | threshold reduction for protective options (8.6) | — | 0 ≤ δ_prot ≤ s^0 − s_min | — | 5 | C2 | threat response |
| P-11 | ι | inertia bound (S-05.4) | — | 0 ≤ ι ≤ s^0 − s_min | — | 4 | C2 | stability against oscillation |
| P-12 | ρ | accumulator residual (S-05.6) | — | ]0, 1[ | — | 4 | C2 | memory of alternatives |
| P-13 | n_0 | learned/simulated value mixture (DC-01) | updates | > 0 | — | 8 | C2 | trust in experience |
| P-14 | E_éch | evidence normalization scale (DC-01) | reward unit | > 0 | — | 6 | C3: dispersion of values on reference agent | evidence sensitivity |
| P-15 | w_m | weight of m_a in evidence (DC-01) | — | ≥ 0 | — | 10, 11 | C2 | share of intrinsic motivation |
| P-16 | α_v | temperament effect on extrinsic evidence (DC-01) | — | real | 0: neutral | 5 | C4 | contrast between temperaments |
| P-17 | R_max, H_max | simulation-budget bounds; each cycle sets the same `(R_eff,H_eff)` for all evaluated candidates (S-05.2, DC-01) | rollouts; transitions | ≥ 1 | — | 6 | C1 | quality, cost, and comparability of simulated evidence |
| P-18 | K | contested S_t slots | elements | ≥ 1 | 4 (Q10); swept from 2 to unlimited in ablation | 4 | fixed | attentional bottleneck |
| P-19 | W | S_t recency window | steps | ≥ 1 | — | 4 | C1 | content persistence |
| P-20 | Δ_hyst | replacement hysteresis (S-07.2) | score | ≥ 0 | — | 4 | C2 | S_t stability |
| P-21 | s_sec | safety-preemption threshold (S-07.3) | f × rsk | ]0, 1] | — | 4 | C2 | safety responsiveness |
| P-22 | w_i^0, α_i | gatekeeper base weights, temperament coefficients (6.4) | — | w_i^0 ≥ 0 | hand-set in MVP | 4, 5 | C4 | attention |
| P-23 | profile multipliers | modulation (6.4) | — | > 0 | threat: w_r, w_u × 1.5 and w_n × 0.5; exploration: w_n × 1.5 | 11 | C2 | profile effect |
| P-24 | profile thresholds, hysteresis, and confirmation durations | modulation (S-02.6) | steps | — | — | 11 | C2 | profile flapping |
| P-25 | N_file, Q_ém, q_emp, T_quota | gatekeeper queues, emission quota, and soft diversity quota (DC-04) | elements; steps | ≥ 1 | — | 4 | C1: saturation under distractor flow | saturation, domination, diversity |
| P-26 | p_min, Δ_but, p_critique, w_ech and form of urg_ech | goal arbitration and intention urgency (DC-03) | pressure | 0 < p_min < 1; Δ_but ≥ 0; p_critique ∈ ]0,1]; w_ech ≥ 0 | — | 4 | C2/C4 | active-goal stability, resumption of critical goal, prospective urgency |
| P-27 | N_imp, T_refr | goal abandonment and refractory period (DC-03) | steps | ≥ 1 | — | 4 | C1 | abandonment loops |
| P-28 | stagnation windows and thresholds | per goal type (S-02.7) | steps; goal measure | — | — | 4 | C1 | stagnation detection |
| P-29 | y_i^*, ω_i, ranges, normalization scales Y_i, deficit functions d_i; table τ → weights ω_i | body and reward (7.1, DC-03) | body units | 0 to 100; Y_i > 0 | fixed MVP setpoints: energy 50, food 60, water 60, integrity 100; Y_i = width of canonical range for the four variables; deficit-type d_i for all four | 2, 5 | C4 | homeostasis and need pressure |
| P-30 | β_neutre, β_min, β_max, β table | discounting (S-06.4, NQ-05) | — | 0 < β_min ≤ β ≤ β_max < 1 | — | 8 | C4 | temporal preference |
| P-31 | η, λ_e | TD learning (11.1) | — | η > 0; λ_e ∈ [0, 1] | — | 8 | C2 | learning speed |
| P-32 | φ(x), version | value features (S-06.2) | — | — | — | 8 | C4 | generalization |
| P-33 | strength of κ priors, B_κ | calibration (S-08.4, DC-06) | pseudo-observations; confidence classes | > 0; B_κ ≥ 1 | f = 0.5 for a module without evidence; repetition of same channel does not update κ | 8 | C3 for equipment, C4 otherwise | calibration speed |
| P-34 | k_ép, L_ép, Δ_ép; recall threshold and weights | episodes and recall (10.3, 10.4) | —; steps; steps | — | — | 7 | C2 | segmentation and recall |
| P-35 | n_1, n_2 | causal status (13.2) | occurrences; contexts | ≥ 1 | — | 9 | C4 | superstitious rules |
| P-36 | n_sec, m_sec | safety promotion and demotion (DC-05) | distinct evidential episodes | ≥ 1 | example 18.7 assumes n_sec = 2 | 9 | C4 | speed of prohibition |
| P-37 | protected integrity threshold | veto invariant (9.3) | integrity unit | ]0, 100[ | — | 3 | C4 | safety margin |
| P-38 | R_letal_max | bound on successive deaths (V-40) | rollbacks | ≥ 1 | — | 2 | C4 | safety-block trigger |
| P-39 | a_F, b_F, b_F^rec | F_cog dynamics (DC-13) | per step | ≥ 0 | — | 10 | C1 | wake/sleep rhythm |
| P-40 | w_F, w_C, w_N, E_ref, S_ref | sleep pressure (DC-13) | — | ≥ 0 | — | 10 | C2 | sleep timing |
| P-41 | p_réveil, s_réveil, L_sommeil_max | wake rule (DC-13) | pressure; f × rsk; steps | p_réveil,s_réveil ∈ ]0,1]; L_sommeil_max ≥ 1 | — | 10 | C2/C1 | fragmented or deep sleep; bound on continuous sleep |
| P-42 | p_cons_min, capacity per sleep, batch size and priority, slot per step | consolidation (S-10.6) | UC; episodes | — | — | 10 | C1 | depth of history |
| P-43 | UC costs, B_cycle, envelopes, protected capacity | compute budget (16.3) | UC | ≥ 0 | — | 4, 12 | C1 | frequency of degraded modes |
| P-44 | N_pré, R_dég, H_dég, reduced depth and width, N_rap^dég | degraded modes (DC-07) | — | ≤ normal values | — | 12 | C1 | quality under load; `(R_dég,H_dég)` common to evaluated candidates |
| P-45 | Δ_plan | adoption of revised plan (DC-17) | value unit | ≥ 0 | — | 6 | C2 | plan stability |
| P-46 | corpus composition; equivalence tolerances by criterion | equipment (S-09.4, S-09.6) | — | — | — | 6 | C3, after benchmark definition and before any training; frozen thereafter | H4 |
| P-47 | per-variable tolerances; observation windows | agency comparator (S-15.3, S-15.4) | variable units; steps | — | standard window: next step, for primitives with immediate effect | 3, 9 | C3 | attribution quality |
| P-48 | novelty, habituation, learning progress, boredom; effect of τ_exploration on m_a | exploration (14) | — | — | — | 11 | C2 | exploration |
| P-49 | materiality thresholds | oracle relevance (S-12.1) | — | — | — | 2, 13 | C4 | precision and recall of S_t |
| P-50 | H1 and H4 refutation thresholds; reliability threshold; multiple-comparison correction | campaign (19.5) | — | — | — | 13 | C4 | conclusions |
| P-51 | N_τ, N_M, N_R; life duration; battery period | experimental plan (19.5) | lives; days | — | starting point: 9, 5, 3; 60 days; every 5 days | 5, 13 | C4 | power |
| P-52 | grid, day, resources, creatures, costs and damage | world physics (19.5) | cells; steps | — | 32 × 32 grid; 300-step day including 100 at night | 2 | C4 | world difficulty |
| P-53 | `fabriquer_outil` recipe and gain | tool (NQ-15) | inventory units; collection gain | — | wood and stone | 2 | C4 | tool use |
| P-54 | battery scenario parameters | battery (NQ-16) | steps; berries; probabilities | — | patience: one berry immediately or three after 20 steps | 5 | C4 | trait measurement |
| P-55 | periodic snapshot frequency | interval replay (S-01.5) | steps | ≥ 1 | — | 1 | C1: storage cost | resumption speed |
| P-56 | default request budgets and deadlines | requests (S-04) | UC; cycles | — | maximum depth 1 (fixed) | 4 | C1 | late responses |
| P-57 | n_comp | skill or habit compilation (spéc. 7.4, DC-16) | distinct successful episodes | ≥ 1 | — | 10 | C4 | emergence of automatisms |
| P-58 | N_options_max | capacity of candidate-option registry (DC-10) | options | ≥ 1, excluding `attendre` | — | 4 | C1: saturation under massive option production | bounded competition memory, ability to introduce new alternatives |

All these parameters remain constant during a campaign. K and ablation conditions vary only between preregistered plan conditions, never during a life. Each individual's temperament parameters (τ) are not parameters to calibrate: they are experimental conditions of the plan (P-51).

## 23. Supplementary implementation decisions

A DC-xx fills a genuine gap in the sources that must be resolved to write the software. Each follows the same form: **A** what the sources impose; **B** what is missing; **C** the solution retained for the MVP; **D** why it is compatible with the architecture; **E** rejected alternatives; **F** tests. All are deterministic, inspectable, and compatible with exact replay; their numerical values are in the registry (22). They apply until the author replaces them.

| Covered point | Decision |
| --- | --- |
| combination of evidence components e_a | DC-01 |
| comparison of crossings of different thresholds | DC-02 |
| arbitration among goal proposals | DC-03 |
| gatekeeper queue saturation and eviction | DC-04 |
| promotion and demotion of safety contingencies | DC-05 |
| provenance of κ verifications, against self-validation | DC-06 |
| behavior of each module in degraded mode | DC-07 |
| snapshot and checkpoint types | DC-08 |
| access rights to journal views | DC-09 |
| path of a proposed option into competition | DC-10 |
| component placement in cycle phases | DC-11 |
| reflex during an engaged option | DC-12 |
| sleep pressure, fatigue, and waking | DC-13 |
| effect of a safety block | DC-14 |
| schedule of temporal-difference updates | DC-15 |
| rules and skills produced by consolidation | DC-16 |
| adoption of a revised plan | DC-17 |

### DC-01 · Combining evidence and the forms of u, π, χ, and R_a

**A.** Evidence e_a brings together learned value, simulated value, and intrinsic motivation m_a [S-05.1, NQ-03]; the components are not simply added; a single component may contribute; unavailability remains distinct from zero, as does `non_applicable` [V-19]; no signal is counted twice [V-17]; the exploration dimension acts on m_a, not on g [V-18]; reward sensitivity controls "the gain of high-value actions" [spéc. 10.4] and β [NQ-05]. u(c) is global, deterministic, monotone non-decreasing, bounded, and a gain on incoming evidence [S-05.5]. π is positive, monotone, and zero if R_a is unknown [S-05.3]; χ carries caution toward safety uncertainty according to threat sensitivity [NQ-07]; R_a monotonically aggregates probability, severity, and irreversibility [S-05.3].

**B.** The combination function, currency of simulated value, forms of u, π, χ, and aggregation of R_a.

**C.**

- Simulated value: average, across completed `R_eff` rollouts, of the discounted sum of predicted rewards, without bootstrapping from Q. Predicted rewards are computed by Value and Needs on predicted body variables using the same function as r_t:

```latex
E_a^{\mathrm{sim}} = \frac{1}{R_{\mathrm{eff}}}\sum_{r=1}^{R_{\mathrm{eff}}}\ \sum_{k=0}^{H_r-1}\beta^{k}\,\hat r^{(r)}_{k},\qquad \hat r_k = \hat D_k - \hat D_{k+1}
```

- Before evaluating candidates in a cycle, Competition fixes the same budget `(R_eff, H_eff)` for all candidates that will actually be simulated. In degraded mode this budget may be lower than `(R_max, H_max)`, but remains common. If simulation of a candidate does not complete the announced effective budget, `E_a^sim` is `indisponible` for that cycle; partial results are logged without entering evidence.
- Extrinsic component and total evidence, as in 8.5: convex mixture of E_a^Q and E_a^sim weighted by experience with the option's `signature_apprentissage`, normalization by tanh, then addition of m_a if applicable, all bounded to [−1, 1].
- Risk: each distinct adverse consequence `j` whose probability is sufficiently known receives `r_j = p_j G_j (1+I_j)/2`. Consequences sharing the same causal identifier are counted only once. Total known risk is `R_a = min(1, Σ_j r_j)`. A materially relevant consequence whose `p_j` is unknown does not erase known risks: it increases `U_a`. `R_a = inconnu` only when no reliable estimate of the option's known risk is available.
- Functional forms:

```latex
u(c) = 1 + (u_{\max}-1)\big(1 - e^{-(c-1)/c_u}\big)
\qquad
\pi(R_a;\tau) = k_\pi\,e^{\alpha_\pi \tau_{\mathrm{menace}}}\,R_a
\qquad
\chi(U_a;\tau) = k_\chi\,\tfrac{1+\tau_{\mathrm{menace}}}{2}\,U_a
```

- `p_j`, `G_j`, and `I_j` are in [0, 1]. π is 0 when `R_a = inconnu`: the unknown is not artificially turned into known risk; U_a then carries caution toward missing information.

**D.** The convex mixture prevents double counting the same quantity estimated through two paths. Normalization makes accumulators comparable between options. Every temperament effect passes through the table (γ_v, π, χ). π ≥ 0 never lowers a threshold, and every function is monotone in the required direction.

**E.** Sum of components: double counting, rejected by S-05.1. Maximum of components: unstable, ignores reliability of each. Learned combiner: not inspectable, outside MVP. Bootstrapping E_a^sim from Q: mixes the two sources. Option-specific urgency: rejected by S-05.5.

**F.** λ_a increasing with n_a, where n_a counts updates of `signature_apprentissage`, not instance ids; one component only, no component, m_a `non_applicable` or zero; two distinct dangerous consequences aggregated without exceeding 1; same causal consequence deduplicated; `R_a = inconnu` only when no reliable estimate of known risk is available; known risk retained even when uncertainty is present; same `(R_eff,H_eff)` budget among evaluated candidates; interrupted simulation excluded from evidence; monotonicity of R_a, π, and χ; τ = 0 gives γ_v = 1; INV-14 and INV-16.

### DC-02 · Tie-breaking and threshold floor

**A.** The largest overshoot of the effective threshold wins; if thresholds differ, the margin is normalized by each threshold; no draw; canonical order breaks exact ties; u(c) is not a criterion; no protective priority in tie-breaking [S-05.7].

**B.** The normalization formula, guarantee that a threshold remains strictly positive, and treatment of a winner whose command or current step is refused.

**C.** Every effective threshold is bounded by s_min > 0. The selected candidate is the one with the greatest relative margin `(A_a − s_a) / s_a`; on an exact tie in reference arithmetic, stable, versioned canonical order of option identifiers breaks the tie.

After tie-breaking, Control prepares an exact command and then applies admissibility, veto, and mask. A refusal is qualified by its **scope**:

- `portee = option`: the option itself is inadmissible or invalid in the current context; it is invalidated and its accumulator removed;
- `portee = plan_ou_etape`: only the current plan or step is refused; the plan moves to `a_reviser`, the option remains valid, is suspended for the rest of the cycle, and may return after replanning;
- `portee = protocole`: the rollback mask forbids only this command in the resumed deliberation; no knowledge or lasting invalidation is created.

In all three cases, the refused candidate is removed from the cycle's winner set and the next candidate is examined. The command eventually admitted is kept in a `DecisionAdmise` object and is never recomputed before being sent to the world.

**D.** With equal thresholds, relative margin orders candidates like raw overshoot: the first rule of S-05.7 is respected. The floor excludes division by zero and negative thresholds. The option/plan distinction preserves S-06.3: replanning does not automatically turn a step problem into invalidation of the pursued behavior.

**E.** Raw difference `A_a − s_a`: favors high thresholds. Draw: breaks replay. Ratio `A_a / s_a`: same ordering as the margin, less readable. Systematic option invalidation after every step veto: rejected because it conflates option and current realization.

**F.** Equal thresholds: same order as raw overshoot; different thresholds; exact tie; active floor; veto applying to option; veto applying only to step with replanning; command in `DecisionAdmise` identical to that sent to world; identical replay.

### DC-03 · Goal proposals and arbitration

**A.** The Goal Manager is the sole owner of the active goal; it receives proposals from Value and Needs and prospective memory; stagnation, recalls, alerts, and plan failures request reevaluation without changing the goal; minimal case: most pressing need, with hysteresis; abandonment of an impossible or invalid goal; everything logged [NQ-01]. An intention never changes the goal by itself [S-02.5]; an intrinsic option does not replace it [V-10].

**B.** Pressure computation, comparison between proposals from different sources, abandonment criterion, treatment of intention deadlines, and timing of arbitration.

**C.**

- Every body variable `i` declares a versioned deficit function `d_i(y_i, y_i*) ∈ [0,1]`. For the four MVP variables, where a low value is unfavorable, `d_i = clip_[0,1]((y_i* − y_i) / Y_i)`. A future asymmetric variable or one where excess is unfavorable must declare its own function instead of using a generic absolute value.
- Need pressure: `p_i = ω̃_i(τ) · d_i(y_i, y_i*)`, with `ω̃_i = ω_i / max_j ω_j`. Value and Needs emits a proposal when `p_i ≥ p_min`.
- An intention stores a `pression_base` bounded in [0,1], equal to the pressure of the goal it served when created. Without a deadline, `pression_courante = pression_base`. With a deadline, `pression_courante = clip_[0,1](pression_base + w_ech · urg_ech(temps_restant))`, where `urg_ech` is deterministic, monotone as the deadline approaches, and versioned. The deadline never changes the goal directly: it only changes proposal pressure.
- Timing: in phase 1 of cycle `n`, the manager arbitrates proposals published through the end of cycle `n − 1` (DC-11).
- With no active goal: activate the highest-pressure proposal above `p_min`; canonical order breaks ties.
- With an active goal: satisfaction if its condition is met; invalidation if target disappears or context becomes invalid; replacement if an admissible proposal reaches `p_actif + Δ_but`, where `p_actif` is recomputed every cycle from its source.
- Planning never declares a goal ontologically "impossible" solely because no plan was found. Under full budget and without truncation, it may produce `non_planifiable_actuellement` with a hash of the relevant material context. At most one failure counts per step. The manager abandons the goal after `N_imp` consecutive failures under unchanged material context.
- After abandonment, proposals with the same type and target are ignored for `T_refr` steps. The refractory period is lifted immediately if the material-context hash changes or if pressure from the corresponding need reaches `p_critique`.
- Reevaluation: a stagnation signal, recall, alert, or plan failure triggers next-cycle arbitration under the same rule and may trigger replanning under S-02.4.

**D.** Single writer, deterministic rule, accessible information only. The deficit function prevents a body value above its setpoint from artificially creating the same need as a deficit. Hysteresis prevents oscillation; the refractory period closes the abandon-then-reactivate loop without preventing a real emergency or new context from reopening the goal.

**E.** Goal identified with engaged option: rejected by NQ-01. Multiple-goal scheduler: unnecessary complexity in MVP. Learned selection: outside MVP. Abandonment on stagnation alone or after a single search without a plan: rejected. Intention pressure frozen despite a deadline: rejected because it would prevent a dated intention from becoming more pressing without a new mechanism.

**F.** Activation; zero pressure above setpoint for "deficit" variables; hysteresis; intention without and with deadline; satisfaction; invalidation; `non_planifiable_actuellement`; abandonment after `N_imp` under unchanged context; new context and `p_critique` lifting refractory period; reproducible one-cycle offset; INV-11.

### DC-04 · Gatekeeper queues, quotas, and saturation

**A.** The queue is not FIFO; an evicted item returns without extra lifetime; capacity is to be calibrated [S-07.6]. Emission quotas per module and window, backpressure, aggregation, expiring queue, degraded mode [spéc. 5.6]; sliding slot quota, habituation, decreasing reliability [spéc. 5.8]; active goal occupies a fixed slot outside quota.

**B.** Eviction policy at saturation, exact quota forms, meaning of backpressure, and handling of genuinely new reobservation.

**C.**

- After selection, non-retained items are sorted by decreasing score, then most recent production, then canonical order. The first `N_file` form the queue; the others are permanently evicted and logged.
- Emission quota: at most `Q_ém` contributions admitted per module over `T_quota` sliding steps. Beyond this, the contribution is rejected at admission with code `quota_emission`: this is backpressure.
- A module MUST NOT artificially reemit the same content to refresh its age. Two contributions with the same subject and payload remain distinct, however, if provenance shows a **new causal event**, a new measurement, or a new world read. The anti-reemission key therefore includes at minimum subject, payload hash, and source event identifiers.
- Diversity quota: on the first selection pass, at most `q_emp` contested slots per module, excluding the safety slot. If this quota would leave empty slots while admissible items remain, a second pass fills remaining slots in score order even beyond `q_emp`. The quota prevents domination; it never artificially creates an incomplete S_t.
- Quotas for a cycle are computed from occupancy in previous cycles (3.7). Habituation goes through `n(m)` (6.4); no separate refractory period is added in the MVP.

**D.** Bounded memory, deterministic eviction, preserved ages (S-07.6). Backpressure requires no new channel. Provenance prevents artificial refresh without suppressing a genuinely new observation. Safety and fixed slots remain outside quota.

**E.** FIFO queue: rejected by S-07.6. Unbounded queue: saturation. Random eviction: breaks replay. Eviction by age alone: removes important items. Absolute slot quota leaving slots empty: rejected. Refractory period in addition to habituation: redundant mechanism.

**F.** Saturation under distractor flow (INV-19); emission quota; artificial reemission rejected; new reobservation accepted; preemption intact under quotas; second pass fills vacant slots; replay.

### DC-05 · Promotion and demotion of safety facts

**A.** Status `etabli_pour_securite` has its own safety-use threshold, reachable without deliberate re-exposure [NQ-11, S-14.2]; it applies to the canonical causal-model object without duplication [V-43]; an isolated observation, suspicion, or exploratory hypothesis is insufficient [S-14.2]; prohibition categories are fixed [S-14.3]; death followed by rollback teaches nothing [S-14.2, V-24].

**B.** Promotion criterion, minimum independence of evidence, and whether demotion exists.

**C.**

- Only facts whose predicate falls under a category of an existing veto rule are eligible: item toxic when consumed, lethal zone, consequence violating a protected invariant.
- Promotion by the Causal Model in phase 5: `n_sec` **independent evidential episodes** actually experienced, each followed within the relevant observation window by harm observed in a `monde`-anchored observation consistent with the predicate; episodes must be distinct in the journal and not multiple processings of the same source event. Contexts must be comparable in the sense of 13.2; no other cause of harm accessible to the individual may suffice to explain the effect; no admissible contradictory evidence may have been integrated since the first.
- The system MUST NOT create or favor a dangerous option solely to reach `n_sec`. Counting episodes may come from ordinary, incidental, or otherwise already-motivated exposures; counterfactual, simulated, or rollback-cancelled exposures never count.
- Initial facts: supplied at birth with this status in the versioned safety policy; never demoted in the MVP.
- Demotion: return to no safety status after `m_sec` independent evidential episodes actually experienced without harm in a comparable context since the last promotion. Such evidence can only be incidental: no test option is ever proposed to demote a safety fact. If the veto naturally prevents new exposure, the status may remain acquired indefinitely.
- Every status change is logged with its deduplicated evidence and becomes visible in the next cycle (3.6).

**D.** No deliberate re-exposure is required, the object remains unique, safety status remains independent of causal status, only actually lived experiences count, and cancelled death remains excluded.

**E.** Promotion after first exposure: contrary to S-14.2. Promotion only at `etablie` status: would require the full causal cycle and could encourage dangerous intervention, rejected by NQ-11. Demotion by passage of time alone: no evidence. Operator validation for each fact: operator changes rules, not facts [S-14.3].

**F.** Two processings of the same episode count once; toxic berry observed in `n_sec` distinct episodes then veto; death and rollback: no promotion; counterfactual: no promotion; no dangerous test option created to reach threshold; demotion only on distinct incidental episodes; INV-25.

### DC-06 · κ representation and verification provenance

**A.** Metacognition and Health owns, computes, and publishes κ [NQ-09]; verification by type [S-08.1]; accessible information only, never oracle [S-08.2]; counterfactuals excluded [S-08.3]; finite-strength prior [S-08.4]; f = κ_(version_E,M,type,famille)(conf), historical confirmation rate for alerts and hypotheses [spéc. 4.4]; atomic publication every cycle [S-08.6].

**B.** Map representation, key granularity, and the rule preventing self-validation or artificial confirmation through correlated errors.

**C.**

- A κ map is indexed at minimum by `(version_equipement_ou_module, module, type_de_contribution, famille_de_signal)`. During an H4 substitution, the new version uses its own prior and does not inherit `(a,b)` counters from the replaced version. `famille_de_signal` distinguishes channels or modalities likely to share biases: symbolic vision, body telemetry, agency comparator, equipment predictor, etc. The signal-family table is structural, closed, and versioned with the contract; it is not a parameter adjusted during the campaign.
- For each key, `B_κ` equal-width classes of declared confidence over [0, 1]. Each class keeps two counters `(a, b)`, initialized by the prior: `force × (f_0, 1 − f_0)`, with `f_0 = 0.5`, or offline-measured calibration for equipment. Then `f = a / (a + b)` for the class containing the declared confidence; alerts and hypotheses use a single class if their contract does not provide graded confidence.
- A verification is **strong** and admissible for κ only if based on an observation or consequence that: carries anchor `monde`; dates from a step strictly later than emission of the verified contribution; has no data derived from the verified contribution in its provenance chain; does not belong to a segment cancelled by rollback; never comes from oracle; and comes from a causally independent modality or physical consequence whose production does not depend on the channel being evaluated.
- A later repetition from the **same channel or signal family** may be recorded as `stabilite_meme_canal`, but it does not modify `(a, b)` and therefore cannot, alone, increase κ. It is used to diagnose temporal consistency, not external correctness of the channel.
- For a strong verification, `confirmee` increments `a`, `contredite` increments `b`; `indeterminee`, `non_verifiable`, `contrefactuelle_non_verifiee`, and `stabilite_meme_canal` do not change κ.
- Verifications from one cycle are integrated in canonical order `(module, type, famille_de_signal, identifier)`.

**D.** A prediction cannot be confirmed by a computation derived from itself, and a systematically biased sensor cannot become arbitrarily "reliable" by repeating its own bias. A physical consequence or independent modality remains usable without oracle. The representation remains deterministic, inspectable, and compatible with a finite prior.

**E.** Calibration against oracle: forbidden. Verification through derived contributions: circular. κ confirmation through simple repetition of the same sensor: correlated error, rejected. Moving average without prior: loses finite strength from S-08.4. Learned calibrator: outside MVP.

**F.** A module reemitting or remeasuring its own signal does not increase κ; an independent physical consequence can; a distinct modality may confirm or contradict; canaries; INV-05 and INV-26; prior weight decreases as strong verifications accumulate.

### DC-07 · Degraded modes, module by module

**A.** Gatekeeper degraded mode triggers when pass cost exceeds the ordinary budget, for the entire pass [S-11.4]. Precision is reduced before function, without ever inventing a result. Never approximated: determinism, world/body integrity, communications, journal, S_t, immediate safety, reflexes, and veto. Simulator keeps its model; consolidation suspends [S-11.5, S-02.8].

**B.** Exact behavior of each module without turning absence of computation into absence of evidence.

**C.**

| Module | Trigger | Degraded behavior | Never reduced |
| --- | --- | --- | --- |

| Perception | step cost exceeds its envelope | deterministic coarse scan of the entire accessible field; details computed only for subscribed subjects and the most salient items; observations marked `couverture_partielle` | reflex stimuli, threats, critical body variables, coarse existence of an accessible change |
| Gatekeeper | `UC_full` exceeds ordinary budget | `P_pre` prefilter computed with the **same five dimensions** `b,n,urg,rsk,val` and `f`, using O(1) estimates or explicitly versioned caches; full scoring of the top `N_pré` according to `P_pre`, whole pass marked degraded | safety preemption, fixed slots, atomic publication, no dimension of P removed |
| Competition | evaluation exceeds envelope | evaluate engaged option, new options from the cycle, and highest accumulators up to the envelope; others are `non_evalue`, cannot win this cycle, and their accumulator, threshold, and state are **frozen**, with neither leak nor noise | thresholds and tie-breaking for actually evaluated candidates, fallback |
| Simulator | request exceeds envelope | same reduced budget `(R_dég, H_dég)` announced for all candidates actually simulated in the cycle; a simulation that does not complete this budget is `indisponible` and its partial value does not enter evidence | model, version, equal budget among evaluated candidates |
| Value and Needs | — | `E_a^Q` always computed; `E_a^sim` according to simulator; no invented replacement value | D_t, r_t, alerts, safety evaluations |
| Planning | search exceeds envelope | reduced depth and width; search continued in the next cycle; partial plan marked | active-plan verification |
| Memory | recall exceeds envelope | the `N_rap^dég` most recent episodes, then, if budget remains, the most relevant according to the already-available index; responses marked partial | episode writing, intentions |
| Causal Model | envelope exhausted | revisions and test proposals deferred to next cycle | already-published statuses, admissibility |
| Exploration | envelope exhausted | designation of new targets deferred; `m_a` for already-candidate options computed if its cost fits the envelope, otherwise option marked unevaluated by Competition | — |
| Metacognition and Health | envelope exhausted | non-critical detectors executed only on the first cycle of each step | integration and publication of κ, budget counters, block detection |
| Goal Manager | never | — | full arbitration |
| Consolidation | ceiling reached | transactional suspension | — |
| Control, reflexes, veto, journal, bus, S_t | never | protected capacity | everything |

**D.** Function remains available while only precision decreases. Perception preserves minimum coverage of the accessible world; the gatekeeper approximates its own function instead of changing its semantics; an uncomputed option is neither rewarded nor punished; degraded outputs are marked, order remains deterministic, and safety remains out of reach.

**E.** Random sampling: unpredictable coverage and unnecessary fragility. Gatekeeper prefilter ignoring novelty or value: changes cognitive function, rejected. `e = 0` for an unevaluated option: turns lack of computation into zero evidence, rejected. Removing an entire module: loss of function. Borrowing budget between modules: forbidden by S-11.3.

**F.** Increasing load, module by module: outputs marked; coarse perception always present; P_pre and full P use the same dimensions; `non_evalue` candidate with strictly unchanged accumulator; simulator budget identical among evaluated candidates; safety intact; identical replay; INV-21.

### DC-08 · Snapshots and checkpoints

**A.** Exact replay starts from birth or any complete snapshot; snapshot frequency is to be calibrated [S-01.5]. A snapshot is complete causal state taken at a coherent point [S-13.1]. Rollback restores the last checkpoint immediately before sending the lethal command [V-25]. Suspended consolidation retains resumption state [S-10.3].

**B.** Typology, capture timing, retention, relationship among types, and the boundary between restorable state and append-only traces.

**C.**

- There are **four types of life `Snapshot`**: birth, periodic, lethal checkpoint, copy. Only the Scheduler triggers them at coherent points: birth, step boundary, immediately before every command send, copy point.
- The consolidation transactional point is a fifth resumption mechanism but **not a Snapshot**: `CheckpointConsolidation` is private Consolidation working state, with neither world nor published cognition.
- The lethal checkpoint is taken after decision admission and before sending, with deliberation still open (3.4). It records `t`, cycle counter, `attempt_ref`, command source, mask, and `R_letal_consecutif`. It is released at the non-lethal end of the step; an in-memory differential copy semantically equivalent to complete state is sufficient.
- Complete causal state includes every external state that can change deterministic continuation: world state, body, active injected scenario, scenario counters, and states of their pseudorandom streams, in addition to individual states.
- The technical journal, hash chain, and evaluation trace are NOT part of restored state. A rollback restores world and causal state, then **appends** new events to the existing journal; it never rewinds the technical trace.
- The hash of every snapshot is logged; restoration verifies the hash before resuming.

**D.** V-25, replay (S-01), and copies (S-13) share one notion of complete causal state, while Consolidation retains a specialized private checkpoint. Separating journal from restorable state makes rollback compatible with append-only logging.

**E.** Checkpoint at the beginning of a step: contrary to V-25. Five variants all called Snapshot: ambiguity between life state and private transaction, rejected. Restoring the journal: contrary to append-only behavior and would erase the lethal branch from audit. Omitting causal scenario state: replay may diverge.

**F.** Restore each of the four Snapshot types, then identical replay; resume a CheckpointConsolidation without modifying the world; death at a randomly chosen step: restored causal state equals checkpoint while journal length strictly increases; injected scenario resumed from snapshot: same future events.

### DC-09 · Journal views and access rights

**A.** Lethal transition, its detection, rollback, and mask remain in the technical journal; the autobiographical view filters them; a single physical journal may expose both views [V-24]. The individual accesses only its own experience and internal functioning [S-08.2]. The evaluation trace is separate and inaccessible to the individual [S-12.4]. Memory reads the journal read-only [Q14].

**B.** Exact content of the autobiographical view, how to construct it without rewriting, and the access matrix.

**C.**

- The physical journal is always the append-only technical trace. No `JournalEvent` is moved, erased, or reclassified after writing.
- Autobiographical allowlist: observations actually perceived; own contributions and cognitively accessible gatekeeper feedback; S_t versions; decisions and commands actually sent and experienced; observed results; rewards; goal changes; episodes; intentions; falling asleep and waking with only their perceptible cause. Consolidation commits, technical version numbers, hashes, RNG states, score decompositions, and `attempt_ref` identifiers remain technical; their content becomes accessible to the individual only through ordinary memory and skill interfaces after publication.
- At non-lethal closure of a step, the journal writes an `AutoSegmentCommit` referencing, by identifier, the events from that attempt authorized by the allowlist. The autobiographical view is the projection of these references. An attempt cancelled by rollback receives no commit and therefore never appears in the projection, without rewriting.
- Everything else is excluded by default, especially: lethal transition, detection, rollback, mask and counters; random states; scheduler and protocol events except their perceptible consequences in the world; oracle annotations and metrics; battery metadata; detailed budget counters.
- A new event type is technical by default; it enters the projection only after explicit addition to the versioned allowlist.

| View | Readers | Mode |
| --- | --- | --- |
| technical | replay and audit tools, operator, bench | read |
| autobiographical | Memory, Consolidation | read-only projection, every access logged |
| evaluation trace | bench, operator | read and write by bench only |

**D.** Conforms to V-24: one technical trace, one autobiographical projection, and a separate evaluation trace. The lethal branch remains auditable without becoming a memory.

**E.** Mutable `view` field on events: rejected because it implies reclassification after writing. Two independent causal journals: divergence risk. Denylist: a new event type would leak by default. Retroactive deletion: contrary to append-only behavior.

**F.** INV-02, INV-27; Memory access to technical event: refused; new type absent from projection; rollback without `AutoSegmentCommit`; non-lethal step with commit referencing exactly the authorized events.

### DC-10 · Path of a proposed option

**A.** The option is the common unit; it comes from Planning, compiled skills and habits, Exploration through Planning, and causal tests [S-06.3, NQ-12, NQ-18]; motif_ref mandatory, but_ref when serving the goal [V-10]; Planning may request admissibility [V-43]; an invalid option loses its accumulator [S-05.6]; the gatekeeper never chooses an action [spéc. 3.4].

**B.** Exact path, registration timing, role of S_t, real registry bound, and prevention of an option becoming its own evidence.

**C.** The seven-step path in 8.3, completed as follows:

- An option carries a validity `expire_a` in steps; at expiry it is invalidated.
- A proposal whose key `(producer, motif_ref, but_ref, end_condition)` already exists replaces the previous version. This registry key is distinct from `signature_apprentissage`: the former manages live instances, the latter indexes shared learning. The accumulator is retained only if the change does not modify the evaluated realization in the sense of DC-17; otherwise it restarts at zero.
- The registry contains at most `N_options_max` live candidates, **excluding permanent option `attendre`**. The engaged option is protected from eviction.
- At saturation, after removing invalid or expired candidates, non-engaged candidates are ranked by `(normalized progress A/max(s_min,s_last) descending, t_last_proposal descending, canonical_order)`. The best `N_options_max − 1`, plus the engaged option if present, are retained. A new option can therefore replace an old candidate with no progress but does not arbitrarily displace an option that has accumulated strong evidence. Every eviction is logged.
- The registry is therefore genuinely bounded, independently of the number of distinct keys a producer may create before expiry.
- The `action_proposee` contribution carries the option to the registry, but its existence, summary, and assertions produced only by that same proposal MUST NOT increase the evidence for the option it carries. When constructing `x_t`, `E_a^sim`, and EvaluationOption provenance, any chain whose sole support is `action_proposee(a)` is excluded for `a`. The same fact may contribute if it has distinct independent support in provenance.

**D.** Registration does not depend on admission to S_t: the gatekeeper does not choose actions. S_t influences evidence through independent information it contains, not through the mere fact that an option announced itself there. The explicit bound closes registry growth.

**E.** Register only options admitted into S_t: would make the gatekeeper an action selector. Treat options as contributions scored by the gatekeeper: mixes roles. Count only live keys as a "bound": insufficient because their number can grow without limit before expiry. Use an option's proposal to justify the same option: self-reinforcing loop, rejected.

**F.** Option without motif_ref rejected; option registered without entering S_t; saturation at `N_options_max`; engaged option never evicted; recent candidate with no progress may replace older candidate with no progress; invalidation at expiry; duplicate key; `action_proposee(a)` alone does not change evidence for `a`; INV-10.

### DC-11 · Component placement in cycle phases

**A.** Fixed phase order; all contributors in a cycle read the same frozen S_t version; gatekeeper publishes atomically; Competition reads the new version in the same cycle; no recursive loop [S-02.2]; declared activations [S-02.3]; visibility from 3.6.

**B.** Which component acts in which phase, in what order, and how to avoid a second world perception on the first cycle.

**C.**

Before any cognitive phase of a waking step, the Scheduler requests **one perceptual capture for the step**. This capture is immutable for the entire deliberation of the step. The reflex path may immediately read its safety portion. On the first cycle only, Perception transforms this same capture into ordinary contributions; it does not reread the world.

| Phase | Components, in canonical order | Rule |
| --- | --- | --- |
| pre-step | Scheduler, Perception (`capturer`), reflex Control | one read of local state and telemetry; world then frozen during deliberation |
| 0 | Scheduler (freeze), Global Modulation (profile) | inputs frozen for the entire cycle |
| 1 | Perception (`publier_capture`) on the first cycle only; Value and Needs; Memory; Goal Manager; Causal Model; Exploration; Planning; Metacognition and Health | each reads frozen inputs and own state; outputs stay in local buffer until phase end; manager arbitrates proposals published through previous cycle |
| end of phase 1 | Bus | pours buffers in canonical order independent of producer call order |
| 2 | Gatekeeper | publishes S_t[n+1], including fixed slots |
| 3 | Competition, with service calls to Value and Needs, Simulator, Exploration, Metacognition and Health | assembles EvaluationOption objects |
| 4 | Competition, Action Control | accumulation, decision, preparation of one command, admissibility, veto, mask |
| 5 | Metacognition and Health (κ), Causal Model (statuses), Perception (precisions), Journal | publications visible in next cycle |

No component sees, within the same phase, another component's output from that phase except through a declared service call in phases 3 and 4. Permuting internal phase-1 execution order therefore changes neither bus content nor causal result; canonical pouring order also guarantees an identical journal.

**D.** Deterministic and compliant with S-02.2 and 3.6. Separating `capturer` from `publier_capture` avoids a double world read within one step. Buffering then canonical pouring makes result and journal independent of internal producer order.

**E.** Two world perceptions in the same step: would create new information while the world is supposed to be frozen. Parallel execution: excluded from MVP [S-01.4]. Event-driven ordering: non-deterministic. Goal Manager in phase 5: would delay Planning even further, contrary to 3.6.

**F.** World-read counter: exactly one per step outside reduced sleep perception; reflex and cognition see the same capture; permutation of phase-1 calls: same contributions after canonical pouring and same journal; INV-08.

### DC-12 · Reflex during an engaged option

**A.** A reflex is innate, priority, on the direct path, and acts within the step; the path arbiter applies veto, reflexes, then option [spéc. 8.2, NQ-12]; reflexes remain active during sleep [S-10.2].

**B.** What happens to deliberation and the engaged option when a reflex acts.

**C.** Reflexes are tested at step opening on that step's stimuli. When one acts, its command, subject to veto and mask, is the command for the step, and no deliberation opens. The engaged option remains engaged with its inertia; its step is not executed and is revalidated at the next step; the learning segment is extended (DC-15). If veto blocks the reflex command, a deliberation opens normally; if the command is lethal, resumption under 18.4 opens a deliberation within the same step.

**D.** Reflex priority is preserved without corrupting deliberation; a step still carries one command.

**E.** Deliberate additionally within the same step: two commands for one step. Abandon the engaged option: loss of continuity. Make reflex a competition candidate: forbidden by S-06.3.

**F.** Adjacent creature during a plan: reflex acts, engaged option remains engaged and competes on next step; veto on a reflex; INV-13.

### DC-13 · Sleep: pressure, fatigue, and waking

**A.** Four factors; `dormir` is an ordinary option; night is favorable but not mandatory; emergency prevents or interrupts sleep; falling asleep and consolidation are distinct [S-10.1]. Nothing already counted by D enters m_a(dormir); body state may only modulate or condition pressure [V-17]. Metacognition and Health produces pressure and m_a(dormir) [V-19]. F_cog grows with consumed computation and decreases at rest in simulated time without reducing budget [S-11.2]; it enters neither D nor r_t [NQ-04]. Waking follows a dedicated rule [S-10.2], including for a dated intention [NQ-17]. Consolidation pressure aggregates unconsolidated episodes and saturation [spéc. 7.7].

**B.** Functional forms, normalization of memory saturation, waking cases, resumption of suspended consolidation, and maximum bound on continuous sleep.

**C.**

- Fatigue, in [0, 1]: at closure of every waking cycle, `F ← min(1, F + a_F · UC_cycle / (C_max · B_cycle))`. The sum of increments in a step is therefore exactly `a_F · UC_pas / (C_max · B_cycle)` before saturation. During a sleep step, `F ← max(0, F − b_F)`; in recovery profile, at the close of a waking step, `F ← max(0, F − b_F^rec)` after increments from the step's cycles.
- Memory saturation used here is a normalized fraction `occ_mem = relevant_content / reference_capacity`, bounded to [0,1], not a raw quantity depending on implementation.
- Consolidation pressure: `P_cons = min(1, N_nc / E_ref + occ_mem / S_ref)`, where `N_nc` counts unconsolidated episodes.
- Sleep pressure: `p_s = min(1, w_F · F + w_C · P_cons + w_N · 𝟙[night])`. It is recomputed at the opening of each step from the published state of the previous step, then REMAINS FROZEN during the cognitive cycles of that step. No variable in D enters it; the MVP has no other sleep variable.
- `m_a(dormir) = p_s` while awake, `non_applicable` during sleep.
- Consolidation starts when the individual is asleep, `P_cons ≥ p_cons_min`, and no threat is perceived by reduced perception. If a consolidation from an earlier sleep is suspended, it resumes before a new consolidation may start.
- Wake rule, evaluated at every sleep step, in priority order: admitted reflex; reduced-perception signal with `f × rsk ≥ s_réveil`; authorized dated intention at deadline; continuous duration `≥ L_sommeil_max`; natural end when `p_s ≤ p_réveil` and no consolidation is active. `L_sommeil_max` is a hard bound: if reached during consolidation, the current pass is transactionally interrupted and the individual then wakes.
- Waking during consolidation first interrupts it: current pass cancelled, validated passes retained. Cognition resumes in the same step.

**D.** No double counting, accessible signals only, normalized saturation, determinism, compliance with V-17, V-19, and NQ-17. The hard bound prevents persistent consolidation debt from creating infinite sleep; priority resumption prevents proliferation of suspended transactions.

**E.** Sleep planner: rejected by S-10.1. Energy in pressure: double counting, rejected by V-17. Fixed schedule: contrary to "night is favorable, not mandatory." Learned pressure: outside MVP. New consolidation while a transaction is suspended: rejected.

**F.** Unit forms; life in which only energy varies: m_a(dormir) unchanged; memory occupancy expressed under two different physical capacities but same fraction: same pressure; every waking case; interruption at `L_sommeil_max`; resumption of suspended transaction before creation of a new one; INV-36.

### DC-14 · Safety block

**A.** With no admissible and safe action, the system enters an explicit logged block with operator alert [S-14.5]; likewise above R_letal_max [V-40]; an unresolved block excludes the life [19.5].

**B.** Effect on execution, distinct between interactive diagnostics and experimental campaign.

**C.**

- In all modes, the block immediately stops progress of the step: no command is sent, the world no longer advances, state is logged, and operator is alerted.
- **Campaign mode**: no case-by-case human decision is allowed. The branch closes immediately with status `blocage_securite`, metrics and journal are finalized, then the preregistered exclusion rule from 19.5 applies. There is no manual resumption of this branch in primary analysis.
- **Interactive diagnostic mode**: the life may remain suspended at the current step. The operator may `arrêter`, or `reprendre` after an explicit external intervention, for example a scenario modification. Every intervention is logged before application, clears the resumption mask if necessary, marks the branch `intervention_operateur`, and excludes that branch from primary campaign analyses.
- No resumption is automatic in any mode.

**D.** Safety remains explicit and traceable, while the campaign prevents a non-preregistered human decision from becoming a hidden experimental variable. Replay of a diagnostic remains exact because operator intervention is a logged external input [S-01.6].

**E.** Ad hoc human intervention during campaign: rejected, experimental bias. Force `attendre`: may be precisely the dangerous command. Random action: dangerous and non-deterministic. Automatic return to an earlier snapshot: would rewrite history and hide the event.

**F.** Scenario with no admissible action in campaign mode: branch closes without waiting for operator; same scenario in diagnostic mode: suspension; diagnostic resumption logged and branch marked; exceeding R_letal_max; replay with operator input: identical; INV-29.

### DC-15 · Temporal-difference update schedule

**A.** Temporal-difference learning with traces [spéc. 8.6]; learning affects evidence only from the next cycle [S-05.1]; reflexes and sleep are outside competition; death cancelled by rollback is not learned [NQ-14].

**B.** Computation time, treatment of steps without a cognitive decision, and closure of a final segment when no following decision exists.

**C.** A segment runs from one cognitive decision (step `t_k`, option instance `o_k`, signature `o_k^sig`) to the next (step `t_{k+1}`, option `o_{k+1}`, signature `o_{k+1}^sig`), of length `L = t_{k+1} − t_k`:

```latex
G = \sum_{j=0}^{L-1}\beta^{j}\,r_{t_k+j}
\qquad
\delta = G + \beta^{L}\,Q(x_{t_{k+1}}, o^{sig}_{t_{k+1}}) - Q(x_{t_k}, o^{sig}_k)
\qquad
z \leftarrow (\beta\lambda_e)^{L} z + \nabla_\psi Q(x_{t_k}, o^{sig}_k)
\qquad
\psi \leftarrow \psi + \eta\,\delta\,z
```

- The update is computed when step `t_{k+1}` ends without a lethal transition, published immediately, and visible from the first cycle of the next step.
- Reflex and sleep steps extend the segment; their rewards enter G. If the segment was opened by decision `dormir`, those consequences therefore contribute to credit for that option.
- A step cancelled by rollback belongs to no segment. The first decision of a life produces no prior update.
- If a **terminal state actually experienced by the individual** closes a trajectory without a following cognitive decision, the final segment is updated with zero terminal bootstrap: `Q_next = 0`. External protocol termination, stopping a battery copy, or safety block are not presented as world states and therefore do not artificially create a terminal reward or extra update.
- Only `Q_active` is modified; the consolidated form changes through Consolidation (15.6).

**D.** With `L = 1`, the rule is exactly that of 11.1. It is deterministic, cannot influence its own cause, is compatible with steps without deliberation, and explicitly defines the only situation in which the next bootstrap is zero.

**E.** Update every cycle: no new information within a frozen step. Maximum over all options: requires evaluating entire registry. Learning reflexes: reflex is not learned. Autonomous learning during sleep: cognition is suspended there. Treating external end of a battery as terminal reward: protocol leakage.

**F.** Equivalence for `L = 1`; segment containing a reflex; sleep segment; lived terminal with zero bootstrap; external battery end without update; rollback excluded; INV-07.

### DC-16 · Rules and skills produced by consolidation

**A.** The Causal Model owns the canonical source of contingencies; Memory and Simulator reference it [NQ-10, S-09.3]. A rule is born during consolidation with hypothesis status; a skill is compiled when the same plan succeeds n_comp times in nearby contexts [spéc. 7.4]. Habits and skills are compiled procedural options [NQ-12]. Commit is coordinated [V-22].

**B.** Who writes these results, when they become visible, and how to prevent one episode from being counted multiple times because several mechanisms processed it.

**C.**

- Consolidation produces candidate rules and compiled skills or habits in its private state.
- Every extracted item of evidence carries identifiers of **source events and episodes**. During integration, a source identifier already attached to the same contingency never increments its counts a second time, even if the episode was processed online and later replayed during consolidation.
- Before commit, rules are handed to the Causal Model. It privately prepares their integration into the canonical source with status `hypothese_causale`, never `etablie` or `etabli_pour_securite`. A rule identical in predicate and context to an existing contingency merges evidence references **as a set of identifiers**, without duplicating their weight.
- Skills and habits join Procedural Memory, their owner, as compiled options with preconditions and success rate. `n_comp` counts **distinct successful episodes**, not the number of times the same success was replayed or reindexed.
- Everything becomes visible at coordinated commit; Semantic Memory keeps only references.

**D.** The single source is preserved, with no direct promotion; nothing is visible before commit and consolidation does not artificially manufacture certainty by counting the same experience several times.

**E.** Consolidation keeps its own store of rules: two competing sources. Direct promotion to `etablie`: bypasses validation in 13.2. Count each replay of an episode as new evidence or success: double counting, rejected.

**F.** Visibility only at commit; same episode learned online then replayed: one canonical item of evidence; same success replayed over several nights: one occurrence for `n_comp`; no duplicate; initial status `hypothese_causale`; INV-23.

### DC-17 · Adoption of a revised plan

**A.** Replanning produces a plan proposal; it does not replace the active plan by itself and never changes the goal [S-02.4]; it does not change option [S-06.3]; an option revalidates at execution [spéc. 6.8].

**B.** Rule for adopting a revised plan, plan comparability, and fate of the accumulator.

**C.**

- A revised plan for the engaged option, with the same identifier, same motif_ref, same but_ref, and same end condition, is adopted at the opening of the next step in either of two cases: the active plan is invalid (failed step, false precondition, lost freshness), or the simulated value of the new plan exceeds that of the active plan by at least `Δ_plan`.
- When adoption relies on value comparison, old and new plans are evaluated from the **same state**, with the **same simulator version**, same published contingencies, and the **same effective budget**. A plan whose evaluation is unavailable is not declared better.
- Before adoption, the new plan passes `verifier_admissibilite` on its known steps. `indetermine` remains allowed; `inadmissible` prevents adoption and leaves the option to revise or invalidates it depending on refusal scope.
- For the engaged option, adoption retains identifier, `engagee` state, and inertia, and resets the current step to the beginning of the new plan; adoption is logged.
- A plan targeting a different end condition is a new option that enters competition.
- For a **non-engaged** option, any material plan change creates a new evaluation version and resets `A = 0`. Evidence accumulated for the old means of reaching the end condition does not transfer to the new plan. A purely representational change, with no change to steps, preconditions, or predicted consequences, may retain version and accumulator.

**D.** Stability through `Δ_plan` hysteresis, unchanged goal, symmetric deterministic comparison. The engaged option preserves behavioral continuity; a non-engaged alternative does not artificially carry accumulated evidence into a different realization.

**E.** Always adopt latest plan: oscillation. Adopt only when invalid: loses improvements. Compare two plans under different budgets: evaluation bias. Retain accumulator of an alternative after material plan change: transfers evidence that concerned another realization. Plans as distinct candidates in competition: forbidden by S-06.3.

**F.** INV-37; oscillation between two nearby plans avoided; comparison with same budget and state; inadmissible plan not adopted; invalid engaged plan replaced at next step; replanned non-engaged alternative with `A = 0`.

## 24. Glossary

| Term | Definition | See |
| --- | --- | --- |
| Accumulator A_a | quantity that integrates evidence received by an option cycle after cycle; the option launches when it reaches its threshold | 8.6 |
| Primitive action | command directly executable by actuators; represented as a trivial option | 8.1 |
| attempt_ref | technical identifier for an attempt at the current step; renewed after rollback, present in journal and checkpoints but never in cognition or autobiographical view | 3.4, 17.4, DC-08 |
| AutoSegmentCommit | technical event written at non-lethal closure of a step; references authorized events forming the autobiographical projection of that attempt | 17.4, DC-09 |
| Admissibility | response from safety policy for an option in context: admissible, inadmissible, or indeterminate | 9.4, V-43 |
| Alert | contribution signaling danger or deviation, with severity; verified only when exposure allows announced harm to be tested | 4.3, 11.3 |
| Anchor | `monde` for an observation drawn directly from the step's local state; `derive` for an observation computed from other contributions | DC-06 |
| Evaluation bench | external device that measures without intervening, from technical journal and oracle | 19 |
| Trait battery | fixed set of test situations run on disposable copies, whose scores form the profile | 19.5 |
| Bifurcation | complete copy of an individual whose divergence is then followed | 17.7 |
| Safety block | immediate stop of step progress; closes branch in campaign, or suspends life until operator decision in diagnostics | 18.6, DC-14 |
| Stub | very simple temporary replacement for a component, allowing the rest to be tested | 20 |
| Active goal | individual's current goal, written only by Goal Manager | 7.4 |
| but_ref | reference from an option to the active goal it serves; absent for an autonomous intrinsic option | V-10 |
| Lethal checkpoint | complete causal state taken immediately before sending a command, with deliberation still open; excludes append-only journal | 17.6, DC-08 |
| CheckpointConsolidation | private resumption state of suspended consolidation; not a life Snapshot | 15.6, 17.6, DC-08 |
| Configuration clone | new individual created with only θ parameters from another; not a copy | 17.7 |
| Command | elementary order sent to world or body by Action Control | 8.1 |
| DecisionAdmise | immutable object containing optional option, exact already-prepared and admitted command, S_t version, and decision origin; transmitted without recomputation to the world | 5.2, 3.4, DC-02 |
| Coordinated commit | simultaneous publication of h_new and rebased active forms at the same synchronization point | 15.6, V-22 |
| Option Competition | accumulation mechanism that chooses the engaged option | 8 |
| Consolidation | offline, transactional reorganization of episodes into a new h version | 15.6 |
| Contingency | learned relation between conditions and outcomes, held in the canonical source of the Causal Model | 13 |
| Contribution | typed message from a module to the bus in the common envelope | 4.3 |
| Copy | new instance created from a complete causal snapshot, with identifier and lineage | 17.7 |
| Cut point | causal instant freezing a consolidation batch | 15.6, V-21 |
| Cognitive cycle | one processing pass of the architecture in six phases; several cycles may occur in one step | 3 |
| Deliberation | sequence of cycles within one step until a decision or C_max | 3.4, 8.7 |
| Double counting | contribution of the same signal twice to one decision through two paths; forbidden except declared double effect | 8.5, V-17 |
| Fixed slot, contested slot | part of S_t supplied by its owner; one of the K places assigned by Gatekeeper | 6.2 |
| Episode | segment of experience delimited by goal change, surprise, zone change, or maximum duration | 10.3 |
| Equipment E | models prepared before birth, shared by all and frozen during life | 12 |
| etabli_pour_securite | usage status authorizing an existing veto rule to apply a fact | 13.3, V-43 |
| etablie | causal status authorizing a contingency to correct the simulator | 13.2, V-43 |
| EvaluationOption | evaluation of an option for current cycle: values, m_a, R_a, U_a, protection, provenance, version | 5.2, V-19 |
| Window W | S_t recency window measured in world steps | 6.5, V-36 |
| F_cog | accumulated cognitive fatigue fed by consumed computation, outside D and r_t | 16.2, DC-13 |
| Effective reliability f, κ map | reliability of a contribution, f = κ_(version_E,M,type,famille)(conf), learned only from causally independent verifications; same-channel repetition is insufficient | 11.4, DC-06 |
| Queue | admissible items not retained by Gatekeeper, under bounded capacity, without age priority | 6.5, DC-04 |
| Goal Manager | sole component that activates, maintains, replaces, or abandons active goal | 7.4 |
| h | consolidated, versioned history; with τ, it carries identity | 15.6 |
| Hysteresis | minimum gap required to replace an item in place: Δ_hyst in S_t, Δ_but for goals, Δ_plan for plans | 6.5, DC-03, DC-17 |
| Inertia ι_a | bounded reduction of engaged option's threshold, never an evidence bonus | 8.6 |
| Snapshot | complete causal state recorded at a coherent point | 17.6 |
| Intention | something to accomplish later with its trigger; held by prospective memory | 10.5 |
| Journal | append-only trace of all events, chained by hashes | 17.4 |
| Batch | frozen set of episodes processed by a consolidation | 15.6 |
| m_a | option-specific intrinsic motivation, third evidence component | 8.5, NQ-03 |
| Protocol mask | external prohibition of the lethal command for the resumed deliberation only | 18.4, V-25 |
| Degraded mode | reduced-precision operation when budget does not permit normal processing | 16.3, DC-07 |
| Causal Model | component holding hypotheses, contingencies, and their statuses | 13 |
| motif_ref | reason an option exists or competes; always present | V-10 |

| Option | candidate behavior evaluated and put into competition; common decision unit | 8.1 |
| Engaged option | winning option currently being carried out | 8.7 |
| Autonomous intrinsic option | option motivated for its own sake, without but_ref, that can interrupt the goal without replacing it | 7.4, V-10 |
| Oracle | bench access to simulated-world truth, never visible to the individual | 19 |
| World step | elementary advance of simulated time; exactly one command per step | 3 |
| Plan | current multi-step realization of a composite option | 8.1 |
| Gatekeeper | deterministic code selecting the K elements of S_t | 6 |
| Safety preemption | automatic entry into S_t of an element whose f × rsk reaches s_sec | 6.5 |
| Sleep pressure | quantity produced by Metacognition and Health that grounds m_a(dormir) | 15.1, DC-13 |
| Modulation profile | set of multipliers on gatekeeper weights, fixed for one cycle | 6.4, 16.4 |
| Q_active, consolidated form | value learned online; its stabilized version in h | 11.1, 15.6 |
| R_a | descriptive estimate of known danger of an option | 7.2 |
| Rebase | replay, on h_new, of online updates subsequent to the cut point | 15.6, V-21 |
| Reflex | innate priority response on the direct path, outside competition | 9.2 |
| Candidate registry | set of options registered in competition | 8.3, DC-10 |
| Exact replay | re-execution that exactly reproduces the reference execution | 17.1 |
| Rereading | reading the journal without re-execution; not replay | 17.8 |
| Restoration | resumption of an execution from a snapshot | 17.8 |
| Lethal rollback | restoration of the checkpoint before a lethal command, followed by resumed deliberation under mask | 18.4 |
| S_t | shared global state at cycle t: fixed slots and K contested slots | 6.2 |
| Segment | interval between two cognitive decisions, unit of the TD update | DC-15 |
| Protective status | contextual quality of an option that reduces a threat, preserves a protected variable, or avoids an invariant violation | 7.2, V-19 |
| τ | temperament: five bounded dimensions fixed at birth | 7.3 |
| θ | identity: θ = (τ, h) | 1.1 |
| U_a | safety uncertainty of an option: lack of reliable information about important consequences | 7.2, NQ-07 |
| u(c) | deliberation urgency common to all candidates | 8.6 |
| Semantic validity | applicability of content given its meaning and current information | 6.5 |
| Veto | blocking of a command by a safety rule; never chooses an action | 9.3 |
| Autobiographical view | subset of the journal the individual may use as lived history | 17.5, DC-09 |
| x_t | canonical evaluation state built only from accessible information | 11.1 |

## 25. Technical appendices

### Appendix A · Correspondence of notation and terms

| Earlier formulation | Source | Current form | Decision |
| --- | --- | --- | --- |
| x_a, accumulator level | spéc. 6.5, V-34 | A_a | 0.4 |
| g_a, gain specific to each option | spéc. 6.5 | g, common; novelty no longer controls it | V-18 |
| ψ(U_a ; τ), uncertainty penalty | consolidation of NQ | χ(U_a ; τ); ψ denotes value parameters | 0.4 |
| e_a, eligibility trace | spéc. 8.6 | z(t); e_a denotes evidence | I-13 |
| ρ, episode surprise threshold; L; Δ | spéc. 7.2 | k_ép, L_ép, Δ_ép; ρ denotes accumulator residual | V-37 |
| K, M, R of experimental plan | spéc. 10.6 | N_τ, N_M, N_R; K denotes S_t slots | 0.4 |
| h_n, journal hash | spéc. 7.6 | emp_n; h denotes history | 0.4 |
| u, r, v, gatekeeper terms | spéc. 5.2 | urg, rsk, val | 0.4 |
| V(x), state value | spéc. 6.5 | Q(x, o_sig), value of an option signature in state x | S-06.3, 8.1 |
| proposed action, action competition | spéc. 4.1, 6.9 | proposed option, option competition | V-49 |
| calibration bench | spéc. 4.5 | Metacognition and Health | V-13, NQ-09 |
| cautious κ prior | spéc. 4.4 | neutral prior f = 0.5, or offline calibration of equipment | V-38, S-08.4 |
| W-cycle window | spéc. 6.3 | W in world steps | V-36 |
| deadlines in cycles ("cycle + 6") | spéc. 4.8, Appendix C | world-event deadlines in steps | V-29 |
| "every step or every k steps" | spéc. 2.1 | several cycles per step during a deliberation | V-02, S-02.1 |
| priority of current step | spéc. 8.2 | reevaluation at every waking step, with engaged option competing with inertia | V-03, NQ-02 |
| habits on direct path | spéc. 3.3, Figure 1 | compiled procedural options, in competition | V-05, NQ-12 |
| horizon dimension | S-06.4 | β derived from reward sensitivity | NQ-05 |
| realignment of active forms | NQ-13 | rebase | V-21 |
| restoration to last valid step; temporary exclusion of lethal command | NQ-14 | checkpoint before send; protocol mask | V-25 |
| reevaluation "at each new world step" | NQ-02 | at every waking step | V-35 |
| stagnation window in cycles | spéc. 5.7 | window in steps; detector signals, imposes nothing | V-04, S-02.7 |

### Appendix B · Decision history

This appendix creates no rule: it links findings and questions from the sources to the section carrying the current rule.

**B.1 Original findings.**

| Id | Topic | Resolved by | Current rule |
| --- | --- | --- | --- |
| I-01 | contradictory temporal model | S-02.1, S-05.8 | 3 |
| I-02 | active goal without owner | NQ-01, V-10 | 7.4 |
| I-03 | boundary between fast state and identity | S-06.6, S-10.4, NQ-13, V-21, V-22 | 11, 15.6 |
| I-04 | owner of κ, risk of oracle leakage | S-08.2, S-08.6, NQ-09 | 11.4 |
| I-05 | reflexes in competition | S-06.3 | 9.2 |
| I-06 | habits and R4 arbiter | NQ-12 | 9.1 |
| I-07 | source of contingencies | S-09.3, NQ-10, NQ-11, V-43 | 13 |
| I-08 | producer of exploration options | S-06.3, NQ-18 | 14 |
| I-09 | tool and battery situations | S-03.1, NQ-15, NQ-16 | 4.1, 19.5 |
| I-10 | temperament pathways | S-05.4, S-06.4, NQ-05 to NQ-07, V-17 to V-19 | 7.3 |
| I-11 | decision unit | S-06.3 | 8.1 |
| I-12 | equipment-corpus coverage | S-09.4 | 12.5 |
| I-13 | ambiguous notation | spéc. 8.6 | 0.4, Appendix A |

**B.2 Inconsistencies introduced by first-round responses.**

| Id | Topic | Resolved by | Current rule |
| --- | --- | --- | --- |
| N-01 | urgency and thresholds | S-05.5 | 8.6 |
| N-02 | thresholds of protective options | S-05.3, NQ-06, V-19 | 8.6 |
| N-03 | gatekeeper cost term | S-07.5, NQ-08 | 6.4 |
| N-04 | sources of evidence | NQ-03, V-17 to V-19 | 8.5, DC-01 |
| N-05 | fatigue and reward | NQ-04 | 16.2 |
| N-06 | origin of β | NQ-05 | 7.3 |
| N-07 | sleep as ordinary option | S-10.1 | 15.1 |
| N-08 | number of sleep factors | S-11.2 | 15.1 |
| N-09 | κ publication cadence | S-08.6, NQ-09 | 11.4 |
| N-10 | placement of agency comparator | S-15.1 | 9.6 |
| N-11 | logical budget versus real budget | S-11, amended Q12 | 16.3 |
| N-12 | request depth and rejection | S-04.4, S-04.5 | 4.5 |
| N-13 | options versus actions | S-06.3 | 8.1 |
| N-14 | reflex candidates | S-06.3 | 9.2 |
| N-15 | inertia, bonus or threshold reduction | S-05.4 | 8.6 |
| N-16 | death and end of life | NQ-14, V-24, V-25, V-40 | 18 |
| N-17 | safety and evidence | NQ-11, V-43 | 13.3 |
| N-18 | intentions during sleep | NQ-17, V-41 | 10.5, 15.3 |
| N-19 | triggering a deliberation | NQ-02, V-34 | 8.7 |

**B.3 Second-round questions.**

| Id | Decision | Current rule |
| --- | --- | --- |
| NQ-01 | minimal Goal Manager, sole owner of active goal | 7.4 |
| NQ-02 | reevaluation at every waking step; engaged option competes with inertia | 8.7 |
| NQ-03 | third evidence component: m_a | 8.5 |
| NQ-04 | F_cog outside D and r_t | 16.2 |
| NQ-05 | β derived from reward sensitivity; no sixth dimension | 7.3 |
| NQ-06 | lower base threshold for protective options | 8.6 |
| NQ-07 | safety-uncertainty penalty modulated by threat | 8.6 |
| NQ-08 | recovery profile retained without cost term | 6.4 |
| NQ-09 | κ owned, computed, and published by Metacognition and Health | 11.4 |
| NQ-10 | canonical source of contingencies in Causal Model; status `etablie` for simulator | 13 |
| NQ-11 | status `etabli_pour_securite` for veto | 13.3 |
| NQ-12 | habits and skills: compiled procedural options; R4 path arbiter | 9.1 |
| NQ-13 | two forms, active and consolidated; rebase at switch | 15.6 |
| NQ-14 | detectable, non-persistent death without learning | 18 |
| NQ-15 | action `fabriquer_outil` | 4.1 |
| NQ-16 | battery mechanisms specific to injected scenarios | 19.5 |
| NQ-17 | waking from a dated intention | 15.3 |
| NQ-18 | Exploration designates target, Planning constructs option | 14 |

**B.4 First-round questions.**

| Group | Topic | Current rule |
| --- | --- | --- |
| S-01 | exact replay | 17.1 to 17.3 |
| S-02 | scheduling and triggers | 3, 8.11 |
| S-03 | ontology, subjects, similarity | 4.1, 4.2 |
| S-04 | requests and responses | 4.5 |
| S-05 | option competition | 8.5 to 8.8 |
| S-06 | option value | 11.1 |
| S-07 | retention in S_t | 6.5 |
| S-08 | verification and calibration | 11.3, 11.4 |
| S-09 | equipment | 12 |
| S-10 | sleep and consolidation | 15 |
| S-11 | compute budget | 16.3 |
| S-12 | oracle | 19.4 |
| S-13 | copies | 17.7 |
| S-14 | veto | 9.3, 18 |
| S-15 | agency comparator | 9.6 |

**B.5 Findings from the verification report.**

| Id | Topic | Treatment |
| --- | --- | --- |
| V-01 | authority of responses over specification | 0.2: this document is the single reference |
| V-02, V-03 | cycle cadence; priority of current step | 3.4, 8.7, 9.1 |
| V-04 | stagnation that imposed an action | 7.4 |
| V-05, V-07, V-42 | habits on direct path, in control, missing provenance | 9.1, 5.2 |
| V-06 | reflexes among option sources | 8.2 |
| V-08, V-46 | Goal Manager absent from tables; correspondence with S1 and O1 in v2 | 2.1, 7.4 |
| V-09 | missing exploration targets | 14 |
| V-10 | active goal and intrinsic options | 7.4 |
| V-11, V-12 | contingencies in simulator; rules written by consolidation | 12.3, 13, DC-16 |
| V-13, V-38 | calibration bench; κ prior | 11.4 |
| V-14 | recovery profile | 6.4 |
| V-15, V-16 | competition formula; temperament table | 8.6, 7.3 |
| V-17, V-18 | double counting | 8.5, 15.1, DC-01, DC-13 |
| V-19 | producers of m_a, U_a, and protective status | 7.2, 8.5 |
| V-20 | F_cog and sleep pressure absent from specification | 15.1, 16.2 |
| V-21, V-22, V-23 | rebase; ownership of realignment; two forms | 15.6 |
| V-24, V-25, V-40 | death, mask, rollback bound | 17.5, 18 |
| V-26, V-27 | tool, death, battery mechanisms | 4.1, 18, 19.5 |
| V-28, V-43 | two knowledge thresholds | 13.3, 9.4 |
| V-29, V-36 | units: deadlines and W in steps | 0.3, 6.5 |
| V-30, V-32, V-33 | obsolete or unsupported first-round formulations | removed; rules from 8.6, 10.5 |
| V-31, V-45 | current statuses and parameters | Appendix B, 22 |
| V-34, V-35 | accumulators at opening; waking step | 8.7 |
| V-37, V-49 | symbol and term collisions | 0.4, Appendix A |
| V-39 | random streams for battery scenarios | 17.2 |
| V-41 | wake-deadline index | 10.5 |
| V-44 | attribution producers | 9.6, 13 |
| V-47 | goal/action alignment metric | 19.5 |
| V-48 | corpus families | 12.5 |
| V-50, V-51 | threshold example; empty rows | not applicable in this document |

## 26. Final implementability validation

### A. Architecture fully specified

| Engineer's question | Normative answer |
| --- | --- |
| What components exist? | 2.1, diagram A |
| Which component owns each state? Who reads it, who writes it? | 5.3, diagram K, INV-01 |
| In what order do components execute? | 3.3, 3.4, DC-11 |
| When does a modification become visible? | 3.6, 21.4 |
| How does a perception become an action? | 8.9, diagram C, 20.4 |
| How do goals, options, plans, and commands interact? | 7.4, 8.1 to 8.3, DC-03, DC-10, DC-17, diagrams D and E |
| How do fast and consolidated learning interact? | 11, 15.6, DC-15, DC-16, diagram G |
| How do sleep and consolidation work? | 15, DC-13 |
| How are accidental compute loops avoided? | 3.7, 21.3 |
| How is exact replay guaranteed? | 17, DC-08, INV-33 |
| How do safety, vetoes, reflexes, and lethal rollback work? | 9, 13.3, 18, DC-05, DC-12, DC-14, diagrams F and I |
| How are experiments run and verified? | 19, diagram H |
| In what order should the software be built? | 20, diagram J |
| Which parameters remain to be calibrated? | 22 |

Every system state has one declared owner; every feedback loop has an explicit temporal cut; every arrow in the diagrams carries a type.

### B. Parameters remaining only to be calibrated

Fifty-eight entries, P-01 through P-58, all in the registry in section 22 with their unit, bounds, stage, and calibration protocol. They cover deliberation and competition (P-01 to P-17), gatekeeper and S_t (P-18 to P-25), goals (P-26 to P-28), body and value (P-29 to P-32), calibration, memory, and causal model (P-33 to P-36), safety (P-37, P-38), sleep and consolidation (P-39 to P-42, P-57), budget and degraded modes (P-43, P-44), planning, equipment, agency, and exploration (P-45 to P-48), bench, world, and scenarios (P-49 to P-54), replay and requests (P-55, P-56), procedural compilation (P-57), and option-registry capacity (P-58). No value is selected by this document; only values already fixed by the sources are carried over. All are preregistered and constant during a campaign.

### C. Supplementary decisions added in this document

| Id | Topic |
| --- | --- |
| DC-01 | combining evidence; forms of u, π, χ, and R_a |
| DC-02 | tie-breaking by relative margin; floor s_min |
| DC-03 | deficit functions, intention pressure, arbitration, non-plannability, and refractory period |
| DC-04 | gatekeeper capacity, eviction, soft quotas, backpressure, and reobservations |
| DC-05 | promotion and demotion of safety facts |
| DC-06 | κ representation by signal family; causally independent verifications |
| DC-07 | degraded mode of each module; absence of computation distinct from zero evidence |
| DC-08 | four life Snapshot types plus a private CheckpointConsolidation; lethal checkpoint before closure |
| DC-09 | autobiographical projection by AutoSegmentCommit; allowlist; access matrix |
| DC-10 | path, registry capacity, eviction, and prohibition of self-evidence for options |
| DC-11 | single perceptual capture, component placement in phases, buffered outputs |
| DC-12 | reflex during an engaged option |
| DC-13 | fatigue, sleep pressure, consolidation resumption, wake rule and bound |
| DC-14 | safety block distinguished between campaign and diagnostic |
| DC-15 | semi-Markov TD update, steps without decisions, and lived termination |
| DC-16 | rules and skills from consolidation with evidence deduplication |
| DC-17 | comparable adoption of a revised plan; reset of replanned alternatives |

### D. Governance point outside the software specification

- The general ethical question related to the number of copies, and the possible moral status of the individual, remain explicitly open in the sources [S-13.5, Q18, spéc. 1.6]. They do not block writing the software; authorization to launch the campaign belongs to the author.

This governance point changes no software interface. Human decisions potentially necessary for implementation are listed exclusively in the v1.2 audit appendix below.

## Appendix - Consistency audit of version 1.2

### Certain corrections integrated

- Ownership of published `S_t` versions is now assigned only to the `S_t` component; the Gatekeeper assembles candidate content but no longer owns the same state.
- The normative hierarchy explicitly places integrated rules of the current version and the DCs ahead of historical sources.
- H5 now describes copies identical at the bifurcation point and then exposed to distinct worlds or seeds, consistently with the experimental protocol.
- Equipment freezing has been made compatible with H4: E remains fixed in every ordinary life and may change only through the preregistered, logged, replayable H4 experimental substitution.
- κ maps are separated by equipment or module version so that an H4 substitution does not artificially transfer calibration learned with the old version.
- The cadence of `F_cog` is aligned across the state table, prose, and DC-13: increment at the close of every cycle, recovery in steps.
- Traceability of direct commands correctly distinguishes a cognitive command grounded in `S_t` from a reflex grounded in the step capture or stimulus.
- The "one command per step" rule explicitly covers the exception of a block before sending, where the world does not advance.
- `JournalEvent.attempt_ref` is optional for technical events that exist outside a step attempt.
- Normalization scale `Y_i` used by deficit functions is explicitly attached to P-29.

### Conservative clarifications integrated

- Components no longer receive τ as usable data: table 7.3 produces an immutable `ParametresTemperament` at birth, the sole interface for consuming temperament effects. Mathematical notation containing τ remains shorthand for this projection.
- Every option has a stable `signature_apprentissage`, distinct from its instance identifier and registry key. `Q_active`, `n_a`, and eligibility traces use this signature, making learning compatible with replanning and successive instances of the same semantics.
- Sleep pressure is recomputed at step opening and remains frozen during that step's cycles, removing any ambiguity about intra-step visibility.
- H4 substitution is limited to a coherent step boundary and invalidates caches dependent on the old version without rewriting prior history.
- Contract compatibility rules are now covered by an explicit invariant.

### Human decisions still required

No remaining blocking human implementation decision. The ethical and governance decision concerning launch and scale of a copy campaign remains outside the software specification and is not an implementation DR.

### Audit result

- Number of top-level components: **21**.
- Number of registry parameters: **58** (`P-01` through `P-58`).
- Number of invariants: **53** (`INV-01` through `INV-53`).
- Number of supplementary decisions: **17** (`DC-01` through `DC-17`).
- Number of remaining required DR decisions: **0**.
- Known accidental compute loop: **none**; every identified loop has a temporal cut or explicit bound.
- Mutable state without a known owner: **none** after correcting ownership of `S_t`.
- Mutable state with multiple known owners: **none**.
- Numerical or structural parameter used but undeclared: **none** within the normative scope; closed structural objects are versioned and calibratable quantities are in registry P-01 through P-58.
- Known broken DC, INV, or P reference: **none** after continuity and numbering checks.
- Known normative contradiction: **none** after the corrections in this version.

The five final validation paths were checked: birth → first command; command → consequence → learning; wake → sleep → consolidation → resumption → commit → waking; dangerous command → veto or rollback → new deliberation; snapshot → copy → battery → stop → replay. In each, causally relevant data has a producer, an owner, a defined transport or call, a visibility time, a consumer, a persistence rule, and a logging rule.
