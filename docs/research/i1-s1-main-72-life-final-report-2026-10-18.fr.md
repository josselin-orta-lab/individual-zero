# Individual Zero S1 : rapport scientifique final, cohorte principale (18 octobre 2026)

**Sujet figé :** `11fa9104e7e9d2c7ad70e837c80463fc4cbe4777`. **Protocole** : 6 mondes x 4 graines x 3 naissances, jusqu'à 300 pas chacune. [Exécution GitHub Actions #39091868002](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39091868002). **Résultat technique : SUCCESS (24/24 lots)**.

## Contrôle indépendant de provenance

Les 24 artefacts originaux ont été téléchargés et les **72 WAL** relus : séquence monotone, chaînage précédent/actuel, SHA-256 calculé sur les événements canoniques, nombre d'événements et empreinte finale des rapports. Les couples (monde, graine) sont uniques. Aucune preuve de rollback, résurrection ou réutilisation d'identité n'est introduite. Le modèle I1 n'a pas été modifié pour l'expérience ; les capteurs restent en lecture seule hors du pas cognitif et leur non-interférence a passé la CI de #290. Les anciennes cohortes défaillantes restent strictement distinctes.

## Résultats physiques

**72 vies nouvelles, 12 983 pas réellement vécus, 12 983 commandes appliquées, 62 décès observés et 10 fins administratives (censure à 300 pas)**, soit **1,000 action physique par pas**. Aucun pas fictif après décès.

| Monde | Vies | Pas vécus | Décès | Actions/pas | Part de sommeil | Stage10 commits |
|---|---:|---:|---:|---:|---:|---:|
| blocked-route | 12 | 2420 | 12 | 1,00 | 84,0 % | 62 |
| dry-valley | 12 | 2098 | 12 | 1,00 | 89,7 % | 25 |
| empty-land | 12 | 1711 | 12 | 1,00 | 81,7 % | 8 |
| foraging | 12 | 2740 | 12 | 1,00 | 84,7 % | 84 |
| hazard-edge | 12 | 490 | 12 | 1,00 | 54,5 % | 9 |
| oasis | 12 | 3524 | 2 | 1,00 | 75,5 % | 384 |

| Primitive appliquée | Compte | Pourcentage des 12 983 actions |
|---|---:|---:|
| `dormir` | 10 560 | 81,34 % |
| `attendre` | 1 424 | 10,97 % |
| `se_deplacer` | 814 | 6,27 % |
| `collecter` | 79 | 0,61 % |
| `manger` | 72 | 0,55 % |
| `boire` | 34 | 0,26 % |

## Évolution temporelle (âges effectivement atteints)

| Pas de vie | Vies présentes | Pas observés | Sommeil | Déplacement |
|---|---:|---:|---:|---:|
| 1-30 | 72 | 1971 | 62,8 % | 10,3 % |
| 31-60 | 63 | 1890 | 78,0 % | 11,7 % |
| 61-120 | 63 | 3779 | 84,9 % | 5,4 % |
| 121-180 | 62 | 3139 | 88,1 % | 4,9 % |
| 181-240 | 36 | 1560 | 86,9 % | 2,1 % |
| 241-300 | 12 | 644 | 80,3 % | 0,0 % |

Cette augmentation apparente du sommeil avec l'âge n'est pas une preuve de stratégie acquise : les dénominateurs changent après les décès, les réserves corporelles et l'environnement varient, les vies n'ont pas un contrôle physique apparié et le sommeil peut être imposé par les besoins.

## Consolidation et apprentissage

**572** événements `stage10_consolidation_committed` valident l'existence de publications *techniques*. Les changements des empreintes des propriétaires `value_needs`, `perception`, `causal_model` et `metacognition_health` sont également fréquents lors de pas **sans** commit Stage10. Les empreintes ne renseignent ni sur le contenu cognitif ni sur la responsabilité causale d'une consolidation. Le changement de version de `slow_history` suit les commits techniques mais ne démontre pas, à lui seul, un savoir utile mobilisé plus tard.

La chaîne *expérience vécue -> modification sémantique admissible -> décision ultérieure attribuable -> résultat physique vérifié* **n'a pas été établie**. Il est donc scientifiquement incorrect d'annoncer une courbe d'apprentissage causale ou une publication sémantique non vide généralisée aux quatre propriétaires.

## Décision scientifique et clôture

- **Activité et répartition des actions : SUPPORTED** pour ces cohortes et scénarios.
- **Survie/mortalité et variation temporelle descriptive : SUPPORTED**.
- **Consolidation technique Stage10 : SUPPORTED**.
- **Modification sémantique durable de chaque propriétaire : INCONCLUSIVE / NOT_ESTABLISHED**.
- **Apprentissage causalisé et progrès de stratégie : NOT_ESTABLISHED**.
- **GO scientifique global de l'apprentissage de I1 : NO-GO (preuves insuffisantes)**, et non verdict d'impossibilité de l'apprentissage.

La campagne S1 préenregistrée est **complète sur son périmètre descriptif**, avec résultats négatifs/inconclusifs correctement conservés. Toute preuve d'apprentissage demanderait un programme distinct de mesures sémantiques, d'opportunités physiques appariées et de cas longitudinaux, sans réécrire ou « aider » I1.
