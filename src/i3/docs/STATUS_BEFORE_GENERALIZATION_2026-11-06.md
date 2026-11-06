# I3 — Statut d'ingénierie

**PROPOSITION. NON ENREGISTRÉ. AUCUN POINT D'ENTRÉE. AUCUN GO SCIENTIFIQUE.** I1 reste le seul moteur actif.

Décision : [ADR-0014](../../../docs/decisions/ADR-0014-i3-lignee-enjeu-de-soi.md) (accepté le 5 novembre 2026). Spécification : [SPECIFICATION.md](SPECIFICATION.md).

| Phase | État |
| --- | --- |
| P0 Décision | Fait : ADR-0014 accepté, invariant de naissance reformulé |
| P1 Noyau | Implémenté : monde séparé, corps à cinq canaux, monnaie vitale, capacités vulnérables, génome, cognition, rejeu exact |
| G2 Porte | **Franchie** le 5 novembre 2026 : 30/30 vies ont bu, rejeu exact, 0,40 ms par pas ([résultat](studies/g2-first-falsifier/RESULTS.md)). Deux défauts relevés pour P1.1 |
| P1.1 | Adopté (porte G2b, [résultat](studies/g2b-p11-heldout/RESULTS.md)) : non inférieur à P1, sans gain mesurable |
| P1.2 | **Rejeté** par la porte G2c ([résultat](studies/g2c-p12-heldout/RESULTS.md)) : révision bien meilleure (69 contre 46, p = 0,0007) mais non-infériorité générale manquée d'une vie. Variante conservée dans la branche `i3/p1.2-variant` |
| P1.3 | **Adopté sur le substrat v2** par la porte G2e sous sélection ([résultat](studies/g2e-p13-v2/RESULTS.md)) : 478 survies sur 1 000 contre 364 (p = 4 × 10⁻⁹) ; révision après tarissement dans 60 % des vies contre 23 %. Cognition de référence : génome `i3-genome-v3` |
| P2 Mondes | Contrat d'opportunités égales et facturation validé en ingénierie ; **0/7729** correspondances exactes avec le tarif fixe des sondes : elles restent descriptives, sans équivalence de coût démontrée |
| P3 Lignée | **Pilote de sélection exécuté et archivé** : 864 vies, 614 morts et 250 survivants censurés ; G2 50/144 sélection contre 45/144 aléatoire, contrastes +3,+3,-1,0 selon population. 48 génomes G2 gelés ; aucun GO scientifique ([résultat](studies/p3-mutation-pilot/RESULTS.md)) |
| P4 Étude | **Deux pilotes prospectifs exécutés et archivés** : P4a 288 vies, G2 sélection 47/144 contre 42/144 aléatoire, population −2,+9,−1,−1 : généralisation non démontrée ([résultat](studies/p4a-g2-heldout/RESULTS.md)). P4b 576 vies : apprentissage des effets/valeurs retenu 84/288 survies contre 0/288 lorsque les calculs payés sont jetés, contrastes +17,+35,+17,+15 ; 144/144 histoires du même génome ont des modèles appris distincts ([résultat](studies/p4b-paid-outcome-learning/RESULTS.md)). Résultat limité au modèle, coûts effectifs différents, **aucun GO scientifique** |

Tests : `python -m unittest discover -s tests/i3 -p 'test_*.py' -v`. Une suite verte valide le logiciel au SHA exact, pas un comportement adaptatif.

## Validated continuation (5 November 2026)

[Development plan](DEVELOPMENT_PLAN.md), tracking
[#1002](https://github.com/josselin-orta-lab/individual-zero/issues/1002).
The first technical slice separates sensorimotor bookkeeping from learning,
adds observer-only life provenance and exposes requested/paid/unpaid cognition.
Negative work counters are rejected; normal P1.1 decision rules are unchanged.

**Gap identified by the first slice (historical v1):** zero-clamping hid
unfunded work, and replay could remain unbilled at death/censoring. The v2
correction below addresses these defects; merely reporting them in #1003 did
not. No new held-out result or lineage experiment is claimed. Historical
results above remain tied to their original v1 source.

## Funded physical substrate v2 (#1004)

Current execution uses [the v2 cognitive funding contract](COGNITIVE_FUNDING.md):
advance decision allowances, strict reserve debits, post-action learning/replay
prepaid in the same tick, no cognition after death, and transactional motor
admission. Exhaustion can produce passive inactivity, never forced sleep.
P1.1 cognitive score rules remain the reference, but its old v1 measurements
cannot certify this changed substrate. Historical G2/G2b/G2c files stay intact.

Development comparison (not a held-out study): 4/4 short lives survive in both
versions; at 400 steps, 8/16 survive versus 14/16 in v1. All v2 declared work is
settled with no pending replay. This adverse outcome is retained. The focused
suite had 62 tests at #1004; exact CI status belongs to the implementation PR.

Laboratory probes (`lab/probes.py`) now execute under v2 with the individual's
payment rules; they previously raised on most development worlds. They are still
not validated or cost-matched comparators: that remains P2 work. See
[COGNITIVE_FUNDING.md](COGNITIVE_FUNDING.md). Focused suite: 66 tests.

P1.3 has since been compared on the same v2 substrate in both arms (G2e, ADR-0015)
and adopted; see the P1.3 row above. P2 engineering work is described in
[P2_ECOLOGY_AND_PROBE_CONTRACT.md](P2_ECOLOGY_AND_PROBE_CONTRACT.md).
It freezes stable/depletion/pulse ecologies, physically separated cohorts,
paid probe receipts and a development-derived static cost profile.
Actual full-horizon cost equivalence is not assumed; unmatched probes are
reported explicitly. P3 is not running. No scientific GO.

## P5a controlled software handoff (6 November 2026)

[Selective paid-retention contract](P5A_SELECTIVE_RETENTION_CONTRACT.md):
three new development-only ablations for learned consequence statistics,
TD value retention and sleep replay; each algorithm genuinely executes and
pays the declared work. This is not a new held-out experiment. All earlier
P3/P4 evidence is unchanged and the reserve remains sealed.
**P5a first prospective scientific screen executed and archived:** [registered protocol](P5A_SCREEN_PREREG.md), [complete original evidence and results](studies/p5a-paid-component-screen/RESULTS.md). 1152 lives on 24 distinct validation worlds; censored at 400 steps: normal 112/288, discard-effects 0/288, discard-values 117/288, discard-replay 119/288. n=4 independent populations; effects-ablation exact sign-flip p=0.125, exploratory Holm p=0.375. Strong bounded action-effect dependence; no statistically confirmatory GO, no cost-equivalence claim. P4 reserve still sealed.

## P5b first development diagnostics (6 November 2026)

[Readout contract](P5B_EFFECT_READOUT_CONTRACT.md) and
[development findings](P5B_DEVELOPMENT_FINDINGS.md): six separate
readout gates on the same paid learned effects. Twelve 120-step
engineering lives per mode only, using development indices 20–25.
Normal inactivation 109/1370 steps; action-prediction blind 841/1370,
learned-sleep blind 96/1370, source-positivity blind 200/1370.
All conditions had 8/12 reach the horizon. The observer shows
processing-budget loss dominates action-blind inactivity, while
resource and movement options are still offered. This paragraph records
**development-only** diagnostics; the later registered study is below.

## P5b empirical action-agnostic prior (development-only)

The [P5b empirical control findings](P5B_AGNOSTIC_PRIOR_FINDINGS.md)
retain the paid action-effect model while masking the association
between individual actions and effects: only the individual's own
global mean of observed bodily change is readable in action prediction.
On 12 paired development lives: 8/12 censored in all compared modes,
but **894 inactive physical steps and 891 no-processing-budget steps**
for the empirical prior, versus 109 and 109 for full learning.
[CI 42212861394](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42212861394)
passed 151 I3 tests on Python 3.11/3.12 and checked unchanged original
P4a/P4b/P5a evidence. **NOT a held-out study or scientific GO.**

## P5b decision score readout diagnostics (development only)

[Funded score witness](P5B_FUNDED_SCORE_WITNESS.md): no extra cognition,
no oracle facts, observer only. In the same 12 paired development lives
per condition, a shared option at an identical pre-decision body can
receive a different actually paid score by step 2 when action-specific
predictions are blinded or replaced with a personal global mean.
Observed first action difference is step 4 across pairs.
[CI 42215560744](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42215560744)
passed 152 tests on Python 3.11/3.12; original P4/P5a full evidence
unchanged. The separate later scientific P5b study is described below;
reserve remains locked.

## P5b registered first-pass readout study (6 November 2026)

[Exact prospective protocol](P5B_HELDOUT_PREREG.md) merged before
[original run 42220546984](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42220546984);
[full original scientific evidence and report](studies/p5b-paid-readout-heldout/RESULTS.md)
independently custodied by
[run 42221386799](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42221386799),
with no additional lives. **1152 lives**, 24 new validation worlds
(indices 72–95), all 48 frozen G2 genotypes. Censored at step 400:
full **98/288**, action-prediction-blind **0/288**,
action-agnostic personal prior **0/288**, sleep-forecast-blind **90/288**.
Four independent genetic populations show normal-minus-action-readout
effects +19,+31,+23,+25 survivors/72, but exact two-sided n=4
p=0.125 and three-comparison Holm p=0.375. Physical inactivity
increases from 19.56% (full) to 75.65% and 75.64% in the two
action-specific controls; realized work and costs are not matched.
For early paid candidate scores, 288/288 action-blind and 285/288
agnostic pairs differ before the first physical-action difference,
but only 79/288 agnostic pairs differ in projected *base return*.
[Handoff](P5B_HANDOFF.md) separates scored uncertainty/risk from
prediction information. No general scientific GO; I1 active,
I3 unregistered, original P4 reserve sealed.

## P5b post-hoc score audit (original data only)

[Score-term decomposition](studies/p5b-paid-readout-heldout/POSTHOC_SCORE_TERMS.md)
finds 4,587 bonus-only and 650 base-only changed candidate
scores for the personal action-agnostic readout, from already
paid first-12-step observations before first physical-action divergence.
273/288 experimental pairs had at least one bonus-only change.
**Observations are dependent; analysis is post-hoc and descriptive,
not a scientific replication or automatic GO.**
[CI 42222555975](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42222555975)
passed 167 tests on Python 3.11/3.12; zero new scientific lives.

## P5c bounded score-addend engineering (6 November 2026)

[Paid score addend contract and development diagnostics](P5C_PAID_SCORE_ADDENDS.md)
separate the curiosity bonus and uncertain-meal risk penalty while
retaining the original genuinely computed and priced action forecasts.
On 48 G0 engineering lives in development indices 26–31, 120-step
censoring is normal 11/12, curiosity-blind 7/12, risk-penalty-blind
12/12, both-blind 7/12. Early choices and funded scores change,
but none of these effects is independent-population scientific evidence.
This section records the earlier development-only checkpoint;
P5c validation was subsequently executed in a separately registered
cohort described below. I1 remains active; P4 reserve sealed.

## P5c prospective original curiosity/risk study, completed 6 November 2026

[Prospective registration](P5C_HELDOUT_PREREG.md) was merged BEFORE
[first original run 42232558602](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42232558602).
All **1152/1152** registered lives, 48 frozen G2 genotypes and
24 untouched validation worlds indices 96–119 completed.
[Original custody run 42233838959](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42233838959)
independently verified all bytes, 288 four-mode pairings and paid
score components with **zero additional lives**.
[Unfiltered full original report](studies/p5c-paid-score-addends/RESULTS.md):
normal survival at 400 **110/288**, discard curiosity **4/288**,
discard risk **105/288**, discard both **7/288**. Paired genetic
population curiosity contrast **[+21,+41,+22,+22]** survivors/72,
exact bilateral n=4 p=0.125 and 3-comparison exploratory Holm
p=0.375, not conventional confirmatory significance. Curiosity
ablation yielded 1.13% inactive lived steps vs 18.65% normal
despite substantially worse survival. Realized work differs.
[Research handoff](P5C_HANDOFF.md): distinguish active mortality
pathways and need-weighted curiosity from generic uncertainty.
No I3 activation, no general scientific GO; original P4 reserve locked.

## P5c original-only active-mortality diagnosis (post-hoc)

[Original-only death causes and first-12-step action
breakdown](studies/p5c-paid-score-addends/POSTHOC_ACTIVE_MORTALITY.md)
show 239 zero-water deaths and 132 early resource commands
without scored curiosity, compared to 146 zero-water
deaths and 392 early resource commands normally,
across the original 288 lives/mode. It is **post-hoc,
descriptive and repeated within old original worlds**;
no new lives, no new genetic/ecological independent
replications, and no proof of complete lifelong
resource-acquisition causality. [CI 42235312727](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42235312727)
passed 185 I3 tests on Python 3.11/3.12.

## P5d external resource-acquisition instrumentation (engineering source)

[The bounded P5d contract](P5D_RESOURCE_ACQUISITION.md) addresses [#1054](https://github.com/josselin-orta-lab/individual-zero/issues/1054).
It distinguishes personal offered/scored resource plans from admitted physical
commands, successfully collected/consumed inventory and **positive body uptake
above metabolic drift**. Only the optional life-laboratory observer reads the
actual post-action world outcome; Mind, world physics, cost rules and original
life evidence chains remain unchanged. A fixed 24-life **development-only**
paired panel is implemented for indices 32–37 with two G0 engineering seeds
and normal vs paid curiosity-score masking. **No P5d scientific validation
was run or authorized by this implementation.** I1 remains active, I3
unregistered and P4 reserve locked.

## P5d original-only post-hoc inventory and voluntary waiting (6 November 2026)

[Original verified read-only analysis](P5D_POSTHOC_COLLECTION_CONSUMPTION.md)
reconstructs inventory conservation from the [permanently archived original
24 development lives](studies/p5d-resource-acquisition/) without any new life.
[Independent custody CI 42282747266](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42282747266)
passed dual-Python 191-test I3 checks, generation guards, original-byte and
six adversarial receipt tamper checks. With curiosity discarded, individuals
issued **761 deliberate wait commands vs 134 normal**, moved **193 vs 627**
times, collected **11 vs 10** food units but consumed **0 vs 7**. All 11
unconsumed units remain conserved in two censored development lives. This
distinguishes chosen waiting from zero null motor commands, but does not
identify the cause of reduced ingestion or establish survival generalization.
No reserve or validation exposure; I1 remains active, I3 unregistered.

## P5d paid meal-proposal original-only audit (6 November 2026)

[Paid eating-choice audit](P5D_POSTHOC_PAID_EATING.md) reuses **only the
already archived** 24 G0 development lives. Under scored curiosity removal,
all **125/125 food-carrying steps** included a genuinely computed and
paid `manger` option, enough energy after decision for the motor, and
integrity above the innate eating veto threshold, yet **0/125 selected
`manger`**. The option was best among **resource-only** recorded scores
in **95/125**, NOT proven best across rest, movement and exploration:
full candidate score ranks, accumulator memory and pre-admission
winner were **NOT_RECORDED**. Normal curiosity: 180 paid meal options
over 180 carrying steps, seven selected and physically eaten.
[CI 42284056578](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42284056578)
passed 195 I3 tests, original-only reconstruction and isolation under
Python 3.11/3.12; no new lives or reserve/validation exposure. Next
engineering task is observer-only full paid option/competition receipts,
never forced eating or a post-hoc genetic adjustment. I1 stays active
and I3 unregistered.

## P5e proposed full paid competition witness (software only)

[Observer-only technical scope](P5E_FULL_COMPETITION_WITNESS.md) extends
P5d's original-only eating analysis without modifying survival strategy.
Opt-in `observer_full_competition` records **all already paid** candidate
scores, prior accumulators and normalized evidence, actual threshold/fallback
selection, first winner, controller fallback attempts and admitted motor.
The sidecar never enters Mind inputs, world physics, paid work or the original
life evidence hash. No new study worlds were opened. Original P5d
resource-only scores do **not** establish why eating was rejected; exact
parity and generation isolation are mandatory before the next diagnostic.
I1 active, I3 unregistered; P4 reserve sealed.

## P5e first original full paid competition development study (6 November 2026)

[Fixed development-only protocol](P5E_DEVELOPMENT_PROTOCOL.md) and
[original source-pinned unfiltered results](P5E_DEVELOPMENT_RESULTS.md)
are archived under [studies/p5e-full-competition/](studies/p5e-full-competition/).
[Original CI 42287145315](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42287145315)
passed 205 I3 tests on both Python 3.11/3.12 and generation boundaries before
24/24 new **DEVELOPMENT-only** lives at indices 38–43.
Normal scored curiosity: **7/12 censored**, 25 collections, nine meals;
with curiosity bonus discarded: **6/12 censored**, **0 collections**, **0 meals**
and 717 deliberate waits. **There were no food-carrying decisions in the
masked arm**, so its meal competition is NOT_OBSERVED, not inferred from
the normal condition. Of 342 paid normal carried-food opportunities,
333 had another candidate with a strictly higher full-option raw score;
9 had a top/tied meal score, nine meals won and were eaten, with
three raw-top meal losses and three lower-raw-score meal wins from the
original threshold mechanism. This is original developmental evidence,
**not** a survival GO or causal generalization. Real cognitive work stays
paid. New genetic populations/ecologies and prospectively sealed fresh
validation remain open; I1 active, I3 unregistered, P4 reserve locked.
