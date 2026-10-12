# Stage 12 : écarts normatifs et préparation de la réception opérateur (v1.3.1)

**Date :** 2026-10-12. **Baseline initiale :** `main` `c74368684f7ea8ceecb60ee0e95e1a5746368942`.  
**Statut : EN COURS ; aucune validation opérateur ni scientifique acquise.**

## Autorité et dépendances

La référence est `docs/architecture/reference/en/mvp-specification-v1.3.1.md`, qui conserve les obligations Stage 12 de v1.2.1 §20.3, §16.1–16.3, DC-07 et DC-14 sauf supersession explicite. Stage 11 est historiquement approuvé (§8 v1.3.1), mais les invariants du runtime mortel intégré doivent rester vérifiés. Le Stage 9 conserve son NO-GO scientifique. Une CI verte ne clôt pas un stage.

## Matrice de conformité Stage 11 / Stage 12 (état observé, non verdict de test)

| Exigence | Code repéré dans main | État / preuve manquante |
| --- | --- | --- |
| Stage 11 : exploration/modulation | `src/i0/modules/exploration.py`, `geographic_exploration.py`, `global_modulation.py`, `src/lab/stage11_runtime.py` et 44 tests préfixés `test_stage11` | Implémenté historiquement ; couverture conjointe mortalité/Stage10/12 et SHA final à vérifier |
| Stage 11 : campagne autonome de 600 pas | `src/lab/stage11_autonomous_600_step_probe.py`, `.github/workflows/ci.yml` | Diagnostics existants ; pas de résultat nouveau sur cette PR |
| Stage 12 : quatre détecteurs lived-only | `src/i0/modules/stage12_detectors.py`, `tests/test_stage12_lived_detectors.py` | Présents ; cette PR resserre unicité par pas physique et immutabilité de l'état publié ; attente de CI |
| Stage 12 : propriétaire Metacognition unique | `src/lab/stage12_runtime.py`, `tests/test_stage12_mortal_runtime.py` | Runtime opt-in et coût UC existent ; couverture bornée actuelle |
| Stage 12 : sommeil et santé intégrés | `src/lab/stage11_sleep_runtime.py`, `src/lab/stage10_runtime.py` | Une partie est intégrée ; six passes, rebase sémantique et défauts post-transition exigent de nouveaux scénarios |
| Stage 12 : contrôles opérateur (arrêt, caps, déblocage diagnostic) | Contrats v1.2.1 §20.3, DC-14 | Pas de contrat console complet démontré par cet audit ; ne pas considérer cette exigence comme PASS |
| Stage 12 : alignement but/action en trois catégories | v1.2.1 §19.5 et §20.3 | Résultats de classification non vérifiés ; ne pas déclarer le critère couvert |
| Stage 12 : modes dégradés module par module | DC-07, `compute_budget.py` et tests dédiés | Coût/refus du diagnostic présent ; matrice exhaustive DC-07 sous charge croissante non rejouée |
| M-11 : persistance de l'état courant | WAL JSONL intégré, branche SQLite Option A en PR #95 et protections empilées | **FAIL** : pas de coordinateur transactionnel complet prouvé sur le runtime I0 ; ne pas restaurer de vie ancienne |
| M-10 : séparation Oracle | `stage12_detectors.py` sans import Lab/Oracle/Bench ; journaux techniques distincts | Séparation statique locale constatée ; tests adversariaux d'intégration et de fuite à maintenir |

## Séquence de validation technique reproductible

Sur un checkout propre du **SHA exact de la PR** avec Python 3.11 puis 3.12 :

```bash
python -m pip install -e .
python -m unittest tests.test_stage12_lived_detectors tests.test_stage12_mortal_runtime -v
python -m unittest tests.test_stage11_multistep_unknown_danger_budget tests.test_stage11_sleep_integration -v
python -m unittest discover -s tests -q
python -m lab.stage11_autonomous_600_step_probe --steps 600
```

Les tests ci-dessus doivent être exécutés et leurs codes retour vérifiés ; ils ne sont **pas** attestés par le présent document. Conserver SHA Git, version de Python, graines, configuration, nombre réel de pas (hors postmortem), décès, bloqueurs, reçus du journal et audit offline. Vérifier séparément les fenêtres de crash `os._exit` quand le coordinateur de l'option A sera intégré, sur un processus jetable.

## Scénarios obligatoires restant à démontrer pour Stage 12

1. Provoquer chacun des quatre détecteurs avec ses observations vécues réelles ; contrôler la distinction `None` / faux / vrai et l'absence de données Oracle.
2. Vérifier un arrêt explicite console sans décès, puis un `safety_block` en campagne et en diagnostic : intervention uniquement autorisée en diagnostic, journalisée et exclue du protocole scientifique.
3. Appliquer plafonds et surcharge croissante ; chaque module suit DC-07, sans fabriquer résultat `non_evalue`, sans modifier les accumulateurs indisponibles, sans compromettre le contrôle moteur.
4. Classer les actions réellement exécutées en : orientées but, autonomie intrinsèque légitime, absence de justification traçable. Les options non exécutées ne doivent pas être comptées.
5. Exécuter des vies neuves totalisant au moins **600 transitions physiques réellement appliquées** pour le module évalué, en documentant graines, décès et couverture ; ne pas compter de pas après la mort ni remplacer la preuve opérateur par cette hypothèse.
6. Contrôler les interactions Stage 10/11/12 : sommeil, consolidation interrompue, budget, bornes métacognitives, événements terminaux et export externe autonome sans dépendances Oracle/Bench.

## Réception et limites

Stage 11 : **historiquement approuvé** selon §8 v1.3.1 ; aucune nouvelle approbation de migration n'est inférée.  
Stage 12 : **EN COURS** ; la présente correction est un durcissement ciblé, pas l'achèvement de DC-14, des métriques, des quotas ni des essais de longue durée.  
M-11 : **FAIL** en attente d'intégration option A, de tests d'interruption brutale de bout en bout et d'une décision opérateur.  
Validation scientifique globale : **différée** ; aucun verdict GO n'est revendiqué.

**Décision future opérateur :** examiner un paquet comprenant l'implémentation complète, les preuves de tests au SHA exact, les scénarios réellement exécutés, les lacunes connues et les journaux indépendamment vérifiés ; prononcer explicitement la réception ou le refus du Stage 12.
