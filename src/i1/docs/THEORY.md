# I1 theory: an embodied, limited, learning individual

**Status:** explanatory engineering theory, **not** scientific GO and not preloaded knowledge in I1.

## 1. Definition of the object of study

I1 is an artificial individual that acts under finite cognitive compute (UC), subjective local information, a bodily state and an evolving private history. Its world is physically modelled outside the individual. No observation of external ground truth becomes its belief automatically. Different lives start without copied experiences, validated hazard labels or past causal achievements.

The scientific question is not whether a scripted sequence can survive. It is whether existing general mechanisms can produce coherent behaviors from needs, temperament and lived interactions, including wrong choices, uncertainty and irreversible mortality.

## 2. Body and drive

Energy, food, water and integrity are physical quantities in `runtime/world.py`. Their temporal dynamics and death come from the physical model, never a prescribed feeding routine. Value/Needs (`modules/value_needs.py`), the Goal Manager (`modules/goal_manager.py`) and the birth temperament (`runtime/i1_birth_temperament.py`) may make bodily deficits motivationally salient. These are *different layers*: possession of berries in inventory is not the same as satiation of physiological food need. The ability to consider eating does not guarantee that eating is selected.

**Hypothesis, not guaranteed outcome:** lived observation plus changing need pressure can support self-maintenance without food-first or other forced action rules.

## 3. Subjective access and epistemology

WorldBody (`runtime/world.py`) holds complete positions, hidden effects and hazards. First-person local observation exposes a restricted projection. `modules/perception.py`, `runtime/journal_views.py` and `modules/memory.py` must never ingest the operator's complete world map, oracle results or benchmark labels as self-knowledge. An individual's confidence, causal hypothesis and measured correctness are distinct facts. Failure to observe competing causes does not prove those causes are absent.

## 4. Agency, options and action

Perceived information and lived preferences can produce possible objectives. Planning (`modules/planning.py`, `modules/stage6_planning.py`), competition (`modules/competition.py`), gatekeeper (`modules/gatekeeper.py`) and Action Control (`modules/action_control.py`) do not share the same responsibility. A candidate plan is not an order. The final action is admitted through normal budget/safety/physical interfaces, with one actual world transition per admitted primitive command. Subjective agency (`modules/agency_comparator.py` and `modules/stage12_goal_agency.py`) must not conflate prediction compatibility with proof of distal causation.

## 5. Learning and memory

Learning may update from personally observed outcomes (`modules/causal_model.py`, `modules/td_values.py`, `modules/lived_prediction.py`) without using knowledge the individual has not earned. Episodic/autobiographical projection is narrower than the complete technical journal. The latter is audit custody, not a memory API.

Sleep and consolidation (`runtime/stage10_runtime.py`, `runtime/consolidation_publication.py`, `runtime/i1_cognitive_publication.py`) are paid, versioned processes. Publication to owners must preserve causal provenance and current online updates, not reapply stale history or gain free safety certainty. An empty publication is not evidence of a useful consolidation.

## 6. Death, custody and limitations

Mortality is terminal: neither a mistaken choice nor a power failure allows resurrection, rollback or postmortem action. `runtime/i1_birth.py` exposes fresh births; M11 (`runtime/m11_transactional_mortal.py`, `runtime/sqlite_life_store.py`) protects only the current authenticated committed generation and refuses uncertain / terminal recovery.

**Unproven:** robust emergent need regulation, real nonempty multi-owner Stage10 publication across lived histories, causal agency over distal outcomes, generalization across unseen worlds and any assertion of consciousness. Consult [EVIDENCE_MATRIX.md](EVIDENCE_MATRIX.md) before claims.

## 7. Anti-patterns

Never inject a prebirth map; make hidden toxic identity observable by fiat; force `manger` after `collecter`; turn H1/H2 into normative defaults; waive UC, Gatekeeper or competition to meet a benchmark; borrow scientific proof from broken historical cohorts; compensate a failed M11 transaction with restored living state. Fix the mechanism producing an observation, not the externally desired behavior.
