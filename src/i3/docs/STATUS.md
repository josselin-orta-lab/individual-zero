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
