# I3 — Plan de test

| Niveau | Contenu | État |
| --- | --- | --- |
| Contrat logiciel | `tests/i3/test_core.py` : génome fermé, physique v4, monnaie vitale, capacités, capture locale, mort irréversible, nouveau-né vierge, rejeu exact, invariance par renommage, pas d'abstention par défaut, `attendre` non privilégié, budget de temps | Implémenté |
| Porte G2 | Falsificateur comportemental préinscrit + rejeu + ≤ 1 ms/pas | Préinscrit |
| P2 | Trois écologies mécanistiquement distinctes, quatre cohortes étanches, réserve scellée, sondes financées en deux phases, contrôle de coût exact et tarif statique calibré en développement | Tests logiciels implémentés ; validation scientifique non établie |
| P3 | Lignée sans héritage de souvenirs, contrôle random-parent, 72 mondes distincts, 864 vies avec preuves, reconstruction de 48 génomes G2 | Implémenté et exécuté sur sélection uniquement, sans GO scientifique ni validation P4 |
| P4 | Validation des G2 fixés (P4a), ablation calculée et payée sans rétention des effets/valeurs (P4b), histoires individuelles appariées, 48 nouvelles conditions de monde au total | Deux premières expériences préinscrites et exécutées : P4a 288 vies, P4b 576 vies ; coût cognitif réalisé non égal entre conditions, GO scientifique non établi |
| P5a | Trois ablations de rétention payées, 48 G2, 24 nouveaux mondes, 4 populations génétiques et témoins complets des coûts par phase | Premier criblage préinscrit exécuté : 1152 vies. Sans effets appris : 0/288 survivent contre 112/288 normaux ; valeurs 117/288, rejeu 119/288 ; n=4 exploratoire et coûts réels divergents. [Résultats](studies/p5a-paid-component-screen/RESULTS.md) |

## Foundation controls

`tests/i3/test_foundation.py` adds software-only checks for valid cognitive
work, explicit payment shortfalls, pending replay bills, sensorimotor updates
independent of learned updates, and full-world/source manifests. Four original
development-fixture hashes check behavioral parity. These are not held-out
scientific evaluations. See [development plan](DEVELOPMENT_PLAN.md) for the
open funding gap and the approved P1.3/P2/P3/P4 sequence.

## Funded substrate v2 (#1004)

`test_funded_cognition.py` adds pre-computation allowance, strict physical debit,
transaction rollback, exhaustion/inactivity, immediate bounded replay and
no-postmortem-work checks. `test_foundation.py` now expects overdraft rejection
and v2 phase evidence rather than the historical observer-only shortfall and
pending-replay behavior. Historical v1 hashes are retained but are not v2 parity
targets. No historical result is rewritten to make tests pass.

Current focused suite: 66 tests (62 at #1004, plus the probe checks below). The
[funding contract](COGNITIVE_FUNDING.md) records exact model limits and a
development-only adverse differential. Engine activation, a 1 ms performance
guarantee, learning benefit and lineage outcomes are NOT established by these checks.

## Laboratory probes under v2

`test_lab_probes.py` runs both probes on development cases where they used to
raise under v2, and checks that every command pays `PROBE_WORK` first, that a
motor command also leaves the next bill funded (otherwise the probe sleeps), and
that an unpayable bill gives null commands with zero work. These checks make the
probes executable; they do not validate them as comparators (P2).

| Croyances révisables (P1.3) | `tests/i3/test_place_beliefs.py` : révision au rythme hérité, gène tiré en dernier, case visible = observation courante | Implémenté |
| Porte sous sélection v2 | `lab/selection_gate_v2.py` (ADR-0015) ; G2e : P1.3 adopté | Implémenté |

## P2 controlled engineering validation

`test_p2_ecologies.py` checks source-stable world replay, distinct ecology mechanisms,
world invariants, no hidden capture, historical cohort exclusion, reserve locking,
individual-to-probe paid-work receipts and rejection of altered frozen tariffs.
`lab/p2_validation.py` offers a development-only diagnostic and a development-
calibrated static tariff. Neither output is a selection result nor a held-out
comparison. For prospective studies, report full paid-cost coverage instead
of calling any heuristic an optimal ceiling. See
[P2 contract](P2_ECOLOGY_AND_PROBE_CONTRACT.md).

## P5b prospectively evaluated readout mechanism

[Registered P5b source and design](P5B_HELDOUT_PREREG.md);
[complete original evidence and costs](studies/p5b-paid-readout-heldout/RESULTS.md).
All 48 fixed G2 genotypes, 24 novel world indices 72–95, four
independent genetic populations, 1152 paid lives, no retry or reserve
use. Full readout survival 98/288, action-specific prediction
masked 0/288, action-agnostic personal prior 0/288,
learned sleep forecast masked 90/288. Three predeclared
population-level contrasts, n=4 exact p floor 0.125, no
confirmatory significance. Phase-paid activity, score witnesses
and original SHA custody verified. No global GO.

## P5c paid curiosity/risk score-addend prospective screen

[Preregistered protocol](P5C_HELDOUT_PREREG.md) and
[complete original experiment](studies/p5c-paid-score-addends/RESULTS.md).
24 new validation worlds 96–119, all 48 fixed G2 genotypes,
1152 original paid lives, four matched score-component interventions.
Normal censored survival 110/288, discard curiosity 4/288, discard
uncertain-meal risk 105/288, discard both 7/288. Curiosity
normal-minus-intervention per genetic population [+21,+41,+22,+22]
survivors per 72; exact two-sided p=0.125, Holm p=0.375,
so no conventional confirmatory inference or global GO.
Independent original-custody checks all experiment identities,
actual phase charges, computed/applied score terms, and no
postmortem work, without any additional study life.

| Carried-food future reuse | `tests/i3/test_carried_food_future_reuse.py`: default equals #1102, repeats bounded by carried units, branches stay personal rows, information only from branch disagreement, every plan paid, renaming invariance | Implemented |
| Carried-food raw-rank audit | `tests/i3/test_stage1_carried_food_rank_audit.py`: audit boundary (no runtime, no World built or stepped), descriptive placement | Implemented |
| ω innate expectation | `tests/i3/test_omega_innate_expectation.py`: default = zero-mean prior, mean shift ω·s with spread kept, bounds, identical paid work across ω, personal-support paths and genome untouched, falsifier fixtures = #1101 | Implemented |

