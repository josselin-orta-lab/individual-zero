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
