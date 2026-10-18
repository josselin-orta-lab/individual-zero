# S1 pilot prospectif I1, bilan scientifique vérifié (18 octobre 2026)

Modèle figé `f90e7bc38c9a371ba8aec651ef391c9549754ef8`.
[GitHub Actions #39091247049](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39091247049), artefact `12123196052`, PR scientifique #289.

## Résultats du pilote

Les six mondes ont terminé l'exécution (18 vies, 927 pas vécus).
Trois morts naturelles ont été observées dans `hazard-edge` à 9 pas chacune ;
les autres vies sont censurées au plafond expérimental de 60 pas.
Les 927 pas ont produit 927 commandes physiques appliquées (1,000 par pas).
Le moteur a émis 68 événements `stage10_consolidation_committed`.

| Monde | Vies | Pas observés | Part des actions `dormir` |
|---|---:|---:|---:|
| oasis | 3 | 180 | 71,67 % |
| foraging | 3 | 180 | 65,56 % |
| dry-valley | 3 | 180 | 83,89 % |
| empty-land | 3 | 180 | 86,67 % |
| hazard-edge | 3 | 27 | 33,33 % |
| blocked-route | 3 | 180 | 55,00 % |

Répartition globale des 927 actions : `dormir` 662 (71,41 %),
`attendre` 136 (14,67 %), `se_deplacer` 97 (10,46 %),
`collecter` 17 (1,83 %), `manger` 12 (1,29 %),
`boire` 3 (0,32 %).

## Interprétation scientifique

Les relevés physiques du pilote et les journaux techniques prouvent une activité,
des résultats de survie et des publications Stage10 techniques.
Ils ne prouvent **ni modification cognitive sémantique non vide,
ni attribution d'un gain de performance à l'expérience ou à la consolidation**.
Les différences entre mondes sont descriptives (cartes et réserves physiologiques
initiales non appariées). La plupart des vies atteignent la censure
administrative de 60 pas. Les trois morts à neuf pas ne peuvent être
interprétées comme des vies de 60 pas.

La très forte part du sommeil mérite une analyse par âge, état physique,
priorités et activité de consolidation. Elle ne permet pas de conclure,
sans expérience contrôlée, que le modèle est défaillant.

**Décision** : pilote technique COMPLETE ; action distribution OBSERVED ;
Stage10 commits OBSERVED ; changements des propriétaires NOT_OBSERVED ;
learning-curve causal NOT_ESTABLISHED ; GO scientifique global NOT_GRANTED.

Prochaine étape préenregistrée : instrumentation passive des propriétaires
avec test de non-interférence, puis cohortes indépendantes plus longues pour
évaluer l'évolution comportementale et l'état cognitif. Ne pas ajouter ces
cohortes aux précédentes, ni modifier l'agent pour améliorer ses statistiques.
