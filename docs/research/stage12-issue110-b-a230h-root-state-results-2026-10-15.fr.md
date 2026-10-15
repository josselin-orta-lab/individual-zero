# A2.30-H : diagnostic des clés exactes à la racine, résultats

**15 octobre 2026.** Préenregistrement \`75516c845ef44bb58719210bf238026ad89caab2\` antérieur au code; expérience archivée originale A2.30-E \`2be8008d51ad0d8a02d4795739a828acfba72aac\` / [run #38715999434](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38715999434). Analyse H testée au SHA \`59af6e7eccc8e08b6519ac7051db645cd633da06\` avec [CI #38717728847](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38717728847) **PASS Python 3.11 et 3.12**, journaux et cohorte validés de nouveau. Ces deux CI relisent **les mêmes huit vies déjà exécutées** ; **zéro** vie / pas supplémentaires.

## Résultats des 121 recherches réellement incomplètes

A2.30-G avait établi qu'aucune de ces recherches ne possédait une première transition prédictible. A2.30-H retrouve **620 appels d'arêtes à la racine**, tous de motif réel \`equipment_input_unseen\` et tous vérifiés via l'empreinte \`FrozenTableEquipment.input_digest\` du couple état accessible/commande :

| Couverture des 620 appels de racine refusés | Appels |
|---|---:|
| Commande exacte (primitive + paramètres) sans exemple prénatal | **468** |
| Commande exacte entraînée, état complet non identique | **152** |
| **Total** | **620** |

Primitives refusées à la racine : **370 \`se_deplacer\`**, **121 \`attendre\`**, **121 \`dormir\`**, **8 \`collecter\`**. Aucune ingestion \`manger\` candidate à la racine dans ces recherches. **113/121** recherches n'ont pas de candidate \`collecter\` ni \`manger\`; seules **8/121** ont une commande alimentaire candidate, mais sa prédiction est également indisponible. Un échec avant l'atteinte de la ressource ne démontre pas que l'individu ignore la commande \`manger\`.

## Écarts des 152 entrées de commande connue

La comparaison purement descriptive de chaque état de racine avec **un exemple physique prénatal de la même commande exacte**, choisi de manière déterministe, constate :

| Champ supérieur différent de l'exemple | Appels |
|---|---:|
| \`adjacent\` (structure du voisinage) | 144 |
| \`body\` | 139 |
| \`x\` | 136 |
| \`y\` | 40 |
| \`current_water_source\` | 27 |
| \`current_resources\` | 8 |

Le sous-champ \`body.food\` diffère dans **139 appels** ; les positions, ressources et voisins peuvent aussi changer. Les nombres **se recouvrent**, ne s'additionnent pas en 152. Un champ qui diffère est une **raison suffisante pour invalider la clé exacte**, mais sa pertinence physique pour la conséquence prédite **n'a pas** été établie. Les exemples ne justifient ni effacement de \`food\`, ni extrapolation spatiale, ni suppression des barrières de risque.

## Frontière scientifique

- **H1, fortement soutenue dans le modèle :** toutes les 121 recherches sans premier pas connu s'expliquent immédiatement par une absence de couverture du couple initial état/commande. H1 « savoir manger est universellement absent » reste **non démontrée**.
- **H2, profondeur seule :** exclue comme remède de ces 121 échecs avec l'Equipment et l'état d'entrée inchangés. Elle reste possible dans d'autres recherches/sous-buts.
- **H3, omission de BFS :** non observée sur les arêtes connues (A2.30-G : 0 divergence). Ne pas affirmer l'absence d'erreurs de projection, de critères d'objectif ou de préconditions.
- **Épistémologie / Stage12 :** les écarts sont des entrées de modèle, non des jugements vécus, et ne prouvent aucun effet causal corporel.

## Recommandation logicielle et prochaine intervention

Sans changer le statut public \`incomplete_model\`, compléter le diagnostic de Stage6 par **les comptes de commandes candidates, connues et indisponibles à la racine**. Proposer un motif explicatif spécifique \`no_predictable_first_step\` **uniquement lorsque chaque candidate racine est effectivement refusée**, sans moteur omniscient ni seconde recherche et sans dériver l'impossibilité physique du résultat. Tester la parité de décisions avant/après instrumentation, les cas d'arrêt anticipé \`plan_found\`, les limites de profondeur et les consommateurs Stage12.

Toute généralisation d'Equipment, interpolation d'état ou conception d'un modèle probabiliste nécessite une expérience prospective de sécurité et une justification distincte. **A2.30 PARTIELLE**, Stage12 PARTIAL, #110 OPEN, PR #187 DRAFT. Aucune validation opérateur ni révision MVP v1.3.1.
