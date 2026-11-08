# Stage 1 Candidate-H: unified relevance-gated software integration

Issue #1061. Baseline:
`2362023a7da8ead0a99bc5a57b2bb1e9f9908942` (#1163).

**FROZEN BEFORE IMPLEMENTATION. SOFTWARE-INTEGRATION ONLY.**

No World instance or generation, no life, no 56/57 evidence read, no engine
registration, no fresh study allocation, no selection, validation, reserve,
reference adoption or Stage 2.

## Why

Two Candidate-H relevance semantics now pass separately:

- first contact (#1162): personal recurrence support is not sufficient.
  Relevance is strict only when `TRIAL` is among
  `target_node_best_choices`, `trial_information_value > 1e-12`, and
  `trial_advantage > 1e-12`;
- post contact (#1163): actionable personal water belief is not sufficient.
  Relevance is strict only when information is positive, changes the top option
  set under one Candidate-F geometry, and a frontier explorer belongs to the
  informed top set.

A unified mind can still be wrong even if both predicates are right in
isolation. Integration can leak Candidate-F geometry into fallback, silently
change one predicate, fail to restore P1.3 mode, hide probe work, or use
recurrence after personal drink knowledge exists.

This gate tests those integration boundaries before any runtime registration.

## Candidate

Software class:

`PersonalRelevanceCandidateHMind`

Policy identifier:

`personal_relevance_candidate_h_v1`

The class may compose the existing Candidate-G memories and Candidate-F
projector, but it is not added to `runtime/life.py`.

Persistent/default state remains exactly:

- simulation mode: `reference`;
- projection accounting: `chunk_end`.

No genomic omega value may be read or exposed.

## Frozen two-stage decision architecture

Every relevance-gated decision has two paid stages.

### Stage A: detached relevance probe

Stage A executes on a detached copy of the individual's current first-person
state. The detached computation is real model work and its declared
`CognitiveWork` is charged to the real decision allowance before Stage B.

The detached copy has no motor authority and no persistent learning authority.

The copy itself is implementation transport, not a free cognitive result:
all model computations that establish relevance must appear in Stage-A work.
No result may be imported from 56/57 or another individual.

### Stage B: complete final decision

Stage B starts from the actual body remaining after Stage-A cognition.

It executes on the real individual and is recomputed from scratch. Stage-A
ordinary scores are never reused.

- if Stage A is **RELEVANT**, Stage B executes one complete Candidate-F
  decision geometry;
- otherwise Stage B executes one complete P1.3 `Mind.decide` decision,
  including original curiosity/prudence and Action Control.

Thus this first integration gate deliberately accepts duplicated computation.
No cache, shared score or reimbursement optimization is allowed.

The returned decision bill is exactly:

`Stage_A_work + Stage_B_work`.

## Stage-A first-contact semantics

Applies only when no personally learned positive drink effect exists.

If no frontier explorer is offered, relevance is false without reading
recurrence.

With frontier explorers:

1. use only paid personal opportunity recurrence;
2. no inherited expectation and `omega=0`;
3. for each explorer evaluate the existing one-future-water kernel;
4. an explorer is relevant only under the exact #1162 predicate:
   - `TRIAL` in `target_node_best_choices`;
   - `trial_information_value > 1e-12`;
   - `trial_advantage > 1e-12`;
5. the decision is RELEVANT iff at least one offered explorer is relevant.

No recurrence support means FALLBACK, never a numeric substitute.

## Stage-A post-contact semantics

Applies once a personally learned positive drink effect exists.

No recurrence memory may be read in this path.

With frontier explorers:

1. pay the existing personal actionable-water belief;
2. if no strict actionable-water probability exists, relevance is false;
3. otherwise evaluate all currently offered options under one common
   Candidate-F forecast geometry;
4. for every frontier explorer, its informed score is the existing paid
   revealed-plan information score and its uninformed score is the corresponding
   uninformed value;
5. ordinary option scores are identical in WITH_INFORMATION and
   WITHOUT_INFORMATION sets;
6. the decision is RELEVANT only if:
   - at least one frontier information value is > `1e-12`;
   - the global top set WITH_INFORMATION differs from the global top set
     WITHOUT_INFORMATION;
   - at least one positive-information frontier explorer belongs to the
     WITH_INFORMATION top set.

This is the #1163 top-effect rule generalized from its one-explorer fixture to
the actually offered option set, without changing its semantics.

## Frozen integrated routing panel

Representative routing is not selected after implementation.

Use exactly the synthetic capture topology already used by
`stage1_candidate_g_no_omega_integration.cap`, with no World:

- seed: **211**;
- base body: `(80,80,80,80,80)`;
- independently set each of the five channels to `20,30,40,50`;
- **20 bodies** total;
- no explicit horizon override: each decision uses its real
  `capacities(body, n_base, h_max)` horizon;
- three history modes for every body:
  1. `NO_SUPPORT`: generic personal action effects only, empty recurrence;
  2. `FIRST_CONTACT_SUPPORT`: the frozen personal recurrence 2/6/10 fixture,
     no learned drink effect;
  3. `POST_CONTACT`: personally learned +35-water drink effect plus its paid
     empirical branch record; recurrence memory is present as a tripwire but
     must not be read.

Total: **60 software decisions**, zero lives.

The routing gate reports every body/history identity. U8 is evaluated over this
entire panel. No replacement body, seed or history may be introduced after
exposure to create a missing route.

## Frozen software gate

Pass only if all rules below are true.

### U0 authority boundary

- zero World/life/evidence access;
- no runtime registration;
- no motor authority in Stage A;
- no genomic omega read;
- P1.3 remains repository reference.

### U1 first-contact classifier parity

On the exact #1162 80-state fixture, the unified first-contact classifier must
match #1162 state-for-state:

- 24 RELEVANT;
- 56 FALLBACK;
- no mismatch.

### U2 post-contact classifier parity

On the exact #1163 80-state fixture, the unified post-contact classifier must
match #1163 state-for-state:

- 68 RELEVANT;
- 12 FALLBACK;
- no mismatch.

### U3 fallback final-policy identity

For declared integrated fallback fixtures:

- Stage B is a complete P1.3 `Mind.decide` from Stage-A's remaining body;
- its action/option/funding and paid P1.3 score witnesses equal an independent
  same-body P1.3 control under identical RNG/state;
- Stage-A Candidate-F ordinary scores are not reused.

### U4 relevant final-policy integrity

For declared integrated relevant fixtures:

- Stage B uses Candidate-F mode for the whole final score geometry;
- all Stage-B score witnesses have one commensurate Candidate-F mode;
- no P1.3 fallback computation is executed.

### U5 phase accounting

For every integrated fixture:

- `total_work == stage_a_work + stage_b_work`;
- cumulative debit from the original body equals the reported final
  post-cognition body within `1e-12`;
- every phase is individually funded before its computation;
- no work/body reimbursement or negative bill exists.

### U6 persistent-mode restoration

After every success and every forced funding failure:

`(simulation_mode, projection_accounting) == ("reference", "chunk_end")`.

### U7 information-source separation

- first contact may read personal recurrence and never omega;
- post contact may read personally learned actionable belief and must not read
  recurrence;
- changing genome omega from -1 to +1 cannot change integrated output when all
  first-person state and RNG seeds are fixed.

### U8 frozen representative routing coverage

The software suite must contain at least one funded fixture for each route:

1. no frontier or no first-contact support -> P1.3 final;
2. first-contact support but non-relevant -> P1.3 final;
3. first-contact relevant -> Candidate-F final;
4. post-contact actionable but non-relevant -> P1.3 final;
5. post-contact relevant -> Candidate-F final.

A missing route is a gate failure, not permission to infer it.

### U9 output authority

A PASS may authorize only a separately frozen future DEVELOPMENT protocol.
It does not authorize adding Candidate-H to `runtime/life.py`, opening a new
world, selection, validation, reserve, adoption or Stage 2.

Pass verdict:

`CANDIDATE_H_UNIFIED_SOFTWARE_INTEGRATION_PASS`

Fail verdict:

`CANDIDATE_H_UNIFIED_SOFTWARE_INTEGRATION_FAIL`

## Interpretation boundary

This gate intentionally overpays by recomputing the final decision after the
relevance probe. A PASS demonstrates a clean, physically accounted integration,
not optimal efficiency.

A FAIL from funding is evidence that this clean two-stage composition is too
expensive as implemented. Do not rescue it by reusing Stage-A scores after
seeing the result. Any future sharing/cache design would require a new
prospective software protocol.

No rule, tolerance, fixture identity or relevance predicate may change after
implementation exposure.

P1.3 remains reference. Candidate-G live remains closed. 56/57 remain exposed
and closed.
