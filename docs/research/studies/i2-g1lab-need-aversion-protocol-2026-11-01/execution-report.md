# G1-LAB v1-r1: need, nutrition and aversion, one bounded integrated run

**Date:** 1 November 2026.
**Status:** COMPLETED NON-LIVING EXPLORATORY TOY MECHANISM STUDY; **NOT A NATURAL-LEARNING GO**.
**Source:** merged [PR #814](https://github.com/josselin-orta-lab/individual-zero/pull/814), exact source commit `50f305f88ee17116d880edbfc8fe2e6368c58bf4`, PR test head `5a8080fc1fe146ff67e391b6d48655689691f46f`.
**Protocol:** owner-approved candidate blob `a279067fbfd21f02ee4aa7854509c19f12cfbb62`, v1-r1.
**Owner authorization:** [G1 issue #662](https://github.com/josselin-orta-lab/individual-zero/issues/662#issuecomment-6561384748).
**Source of data:** workflow logs `I2_G1LAB_V1R1_ONE_SHOT` produced by `tests/i2/test_g1_lab_need_aversion_v1r1.py`; Python 3.11 and 3.12 both PASS on the same PR head. Those CI repetitions check reproducibility in two Python versions, **not independent experimental replicates**.

## Frozen design and boundaries

Four experimental cells: initial energy 17 or 60 × simulated independent sensory aversion 0 or 4; positive experienced nutrition +8 after unforced chosen EAT; original metabolism -2 per action / -1 per abstention; 12 berries, 60 synthetic UC and 8 captures maximum per arm. Each cell has full / need-off / aversion-off / original fixed-prior controls. Deterministic source, no seed search, no +5 observational offset, no +9 stale reconsideration, no forced EAT or social cue. Sixteen independently initialized **disposable simulated SQLite identities**, one local cognitive/body owner per instance, paid Competition/Control and next-capture evidence only. Source code in `src/i2/lab/need_aversion_policy.py` and `src/i2/lab/integrated_loop.py`.

The scores are **researcher-designed**: prior C=3/E=4/D=1; on previously chosen personal evidence only, `need = floor((100-energy)*last_nutrition/100)`, `aversion = last_sensory_signal`; full adds need and subtracts aversion; ablations disable terms. No biologically measured hunger or pain is claimed.

## All observed arms

Legend C = collect, E = eat, _ = abstain. Final energy is simulated energy after the eight captures; UC refers to **actually paid synthetic UC**. No arm had a simulated terminal, veto or refusal. All sixteen arms satisfied the primary **matched, unforced C,E,C personal history at captures 1–3**, had EAT offered at capture 4, and therefore met the **predeclared primary identifiability condition**, not a post-hoc selected horizon.

| Cell | Arm | Eight chosen decisions | Capture 4 | Final energy | Spent synthetic UC |
| --- | --- | --- | --- | ---: | ---: |
| L0 (17,0) | full | CECECECE | E | 33 | 36 |
| L0 | need-off | CECECECE | E | 33 | 36 |
| L0 | aversion-off | CECECECE | E | 33 | 36 |
| L0 | fixed | CECECECE | E | 33 | 36 |
| L4 (17,4) | full | CECECECE | E | 33 | 36 |
| L4 | need-off | CECCCCCC | C | 9 | 38 |
| L4 | aversion-off | CECECECE | E | 33 | 36 |
| L4 | fixed | CECECECE | E | 33 | 36 |
| H0 (60,0) | full | CECECECE | E | 76 | 36 |
| H0 | need-off | CECECECE | E | 76 | 36 |
| H0 | aversion-off | CECECECE | E | 76 | 36 |
| H0 | fixed | CECECECE | E | 76 | 36 |
| H4 (60,4) | full | CEC_____ | _ (tie) | 57 | 33 |
| H4 | need-off | CECCCCCC | C | 52 | 38 |
| H4 | aversion-off | CECECECE | E | 76 | 36 |
| H4 | fixed | CECECECE | E | 76 | 36 |

**Totals:** 16 independently initialized disposable models, 128 completed captures, **0 modeled deaths**, 0 study control refusals, and 0 unidentifiable prehistories. Actual UC spending differs with offered affordance counts and the number of action/abstention cycles; do not compare final energy without reporting those differences.

## Primary endpoint and interpretation

Under the predeclared equation, personally experienced nutrition and aversion were first available to decision-making after their own chosen EAT, not before. After another unforced COLLECT, capture 4 enabled a genuine behavioral contrast. The output matches the **pre-run algebraic predictions**:

- L0 and H0: all arms EAT. **No identified need or aversion action contrast** when synthetic sensory aversion = 0.
- L4: full EAT, need-off COLLECT, aversion-off EAT, fixed EAT. **Engineered need-term is behaviorally discriminable** against need-off in this cell; **aversion-term not behaviorally discriminable** against aversion-off here.
- H4: full **ABSTAINS** because EAT and COLLECT both value 3, need-off COLLECT, aversion-off and fixed EAT. Distinct decisions arise under existing *unique positive maximum* rule. Engineered need/aversion terms both influence the supplied Competition scores, but the full-arm abstention is a **tie artifact**, not automatically a robust biological appetite/aversion phenomenon.

**Important:** original fixed prior also EATS whenever offered in all cells and ends with higher energy than aversion-modulated H4 full. The experiment therefore does **not** show a general adaptive or survival advantage. The very same expected signs arise by construction from a deterministic human-specified equation. No statistical replicates, independently evolved drive, natural hunger, independent M11, physically admitted actions, actual experience of animal pain, or living intelligence are evidenced.

## Source provenance, negative controls and next decision

The local causal replay validates the distinct `nutrition_gain` and `aversive_signal` columns, previous-commit energy evidence, selected-action/affordance consistency, full charged synthetic UC, tie/abstention, terminal and no immediate future consequence leakage. The existing non-living I2 proposal suite passed in Python 3.11 and 3.12 on exact PR SHA. Logs are available in PR #814 checks. **CI success validates software integrity, not H2/H3 scientific promotion.** Both CI versions execute the same deterministic code, so they are repeat validations of the **one approved protocol**, not a fresh tuned campaign.

**Scientific verdict:** `MECHANISM_CAUSALLY_DISCRIMINABLE_IN_TOY_LAB` for selected matched-history contrasts; `NATURAL_AUTONOMOUS_LEARNING_NOT_ESTABLISHED`. Stop v1-r1 here, freeze all null/negative outcomes, **do not run a second tuned variant or another intervention on this authorization**. A future empirical hypothesis would require its own owner authorization, independent falsification and nontrivial task generalization; do not treat the researcher-written need equation as natural motivation.

**Security/research gates unchanged:** G1-LIVE external architecture and science reviews **REVIEW_REQUIRED** (#662), genuine independent M11 not established, G0 archive custody partial (#661), G3 living activation (#664) blocked. I2 remains `NOT_REGISTERED_NOT_EXECUTABLE`, `NOT_BORN`, `motor_authority=NONE`. A local modeled terminal (none occurred here) is not attested living death.
