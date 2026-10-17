# I1 evidence matrix

**Status taxonomy**

- **DESIGN:** motivating theoretical hypothesis, not observed evidence.
- **IMPLEMENTED:** code exists in the current I1 engine, with specified tests.
- **SOFTWARE_TESTED:** a described invariant was checked by tests on an exact SHA.
- **BEHAVIOR_OBSERVED:** measured in a specific fresh mortal life, with trace/seed.
- **SCIENTIFICALLY_ESTABLISHED:** preregistered independent replication and challenge completed. None asserted here.
- **OPEN / NOT_OBSERVED:** evidence is missing or inconclusive, never assumed success.

| Capability or constraint | Current assessment | Traceable code / test | Boundary of conclusion |
| --- | --- | --- | --- |
| Physical food/water decay and mortality | IMPLEMENTED; covered by software tests | `runtime/world.py`, `runtime/i1_natural_sleep.py`, `scripts/test_i1_ci.py` | Does not prove learning to feed or survival |
| Needs, temperament and autonomous option selection | IMPLEMENTED | `modules/value_needs.py`, `runtime/i1_birth_temperament.py`, `modules/competition.py` | No forced optimal survival behavior |
| First-person locality and oracle isolation | IMPLEMENTED; source/CI gates | `runtime/world.py`, `runtime/journal_views.py`, `tests/i1/test_i1_generated_isolation.py` | Does not prove no leak from every future integration |
| Goal progress and subjective agency | IMPLEMENTED with epistemic limits | `modules/stage12_goal_agency.py`, `runtime/i1_natural_runtime.py` | Distal causal responsibility remains unproven |
| UC accounting and genuine cognition | IMPLEMENTED; smoke/full software suite | `runtime/stage4_runtime.py`, `modules/competition.py` | Budget green is not learning quality |
| Episodic learning and lived outcome | IMPLEMENTED; prospective strength OPEN | `modules/memory.py`, `modules/causal_model.py`, `modules/td_values.py` | Correct prediction != verified causal attribution |
| Nonempty four-owner Stage10 publication | OPEN / NOT_OBSERVED as scientific result | `runtime/stage10_runtime.py`, `runtime/i1_cognitive_publication.py` | Needs real private candidates, provenance, replay and cold checks |
| Authenticated M11 custody and terminal refusal | IMPLEMENTED; SOFTWARE_TESTED on recorded CI SHAs | `runtime/m11_transactional_mortal.py`, `tests/i1/test_i1_m11_adversarial.py`, `tests/i1/test_i1_natural_m11_cold_recovery.py` | Cannot recover uncertain or dead living states |
| Six preregistered preset environments | IMPLEMENTED; two brief software births tested | `lab/world_presets/`, `tools/run_i1_world_preset.py` | Not behavioral calibration or scientific GO |
| Generalized adaptive self-maintenance | OPEN / NOT_OBSERVED | Needs future runs over independent worlds | Cannot claim from short preset smokes |
| Consciousness | NOT_ESTABLISHED | No qualifying criterion/evidence provided | No assertion permitted |

## Evidence submission contract

For each meaningful claim record the exact Git HEAD, contract and world digest, birth identity, physics step sequence, UC and journal evidence, relevant observer fields, code path, counter-example and alternative explanations. Label the distinction between **software correctness**, **observed behavior**, **causal interpretation** and **scientific acceptance**.

Do not elevate former A2.38/A2.39/H1/H2 studies or experiments built on broken model versions to natural I1 normative evidence. Those files remain historical only. The authoritative *current* status is [STATUS.md](STATUS.md) plus real CI and reproducible new observations, never a copied assertion.
