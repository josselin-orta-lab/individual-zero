# I1 : clôture de la campagne f_cog / coefficient w_F = 0.20 (2026-10-18)

## Décision

**NO-GO pour promouvoir `w_F = 0.20` comme réglage scientifiquement validé de I1 dans `main`.** C'est une **décision de non-acceptation scientifique**, pas une démonstration que 0.20 serait universellement nuisible. La CI est verte mais les critères préenregistrés d'équilibre et d'utilité de la mémoire ne sont pas satisfaits. La PR #295 doit rester non fusionnée; I0 ne change pas.

Le paramètre `F_cog` reste l'état dynamique de fatigue; l'intervention porte sur **son poids `w_F = 0.20` dans la pression de sommeil** (contre 0.65 dans main). La naissance effective a été vérifiée. Aucun ordre de dormir, boire ou manger n'a été injecté. Mort irréversible, aucun rollback.

## Provenance, séparation des cohorts

- Baseline `main` : `75762dc476ff56beb2524ff228a48595609ef591`.
- Grande matrice **prospective** : commit `09eb173f7923d2563c0a432e5e62306b5b7df5de` ; [GitHub Actions #39110330223](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39110330223). **24/24 jobs réussis** sur six presets x quatre poids. Deux graines 920260/920261, trois nouveau-nés par arm/preset : **144 vies**, **15 060 pas réellement exécutés**, dont **20 morts** et **124 vies actives à leur horizon (censurées)**. WAL auditée, état terminal conservé, poids effectif enregistré, SHA de monde vérifié.
- Contrôle de CI sur le moteur corrigé : commit `2c42e9a9bb3636dddd0652b65cf4cba5a6bffa7a`, [CI #39110598773](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39110598773), **4/4 jobs réussis** (Python 3.11, 3.12, structure). [Pilote #39110596481](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39110596481), **4/4 jobs réussis**, 12 vies, 288 pas à 24 pas max.
- La seule différence de code entre `09eb173` et `2c42e9a` concerne `tests/i1/test_i1_sleep_goal_entry.py` et le workflow `.github/workflows/i1-fcog-020-science.yml`. **Aucun fichier moteur, physique, scénario ou politique cognitive n'a changé** dans cette comparaison GitHub. La CI du commit 09eb échouait sur une pollution des tests Python et non sur le comportement d'I1 ; le code moteur identique a depuis passé la CI. Les cohortes restent attribuées à leurs **commits originaux**, jamais étiquetées à tort comme des exécutions sur 2c42.
- Les archives A2 anciennes et la PR #294 sont des hypothèses historiques, jamais des contrôles expérimentaux de ce verdict.

## Distribution des comportements

Chaque case ci-dessous représente **six vies appariées par trois identités et deux étiquettes de graine**, au plus 120 pas par vie (morts conservés, donc seulement 165 pas collectifs à chaque poids sur `hazard-edge`). Les pourcentages sont des **pas ayant exécuté `dormir`**, dénominateur = pas observés, **pas** des épisodes internes Stage10. Il y a exactement 1 action appliquée par pas dans les cohortes mesurées.

| Preset | % dormir w_F=0 | % dormir w_F=0.1 | % dormir w_F=0.2 | % dormir w_F=0.3 | Delta 0.2–0 (points) |
| --- | ---: | ---: | ---: | ---: | ---: |
| oasis | 36.53 | 42.64 | **62.36** | 65.56 | +25.83 |
| foraging | 10.56 | 13.47 | **28.89** | 50.00 | +18.33 |
| dry-valley | 15.14 | 27.50 | **44.72** | 52.22 | +29.58 |
| empty-land | 15.42 | 16.39 | **20.56** | 31.25 | +5.14 |
| blocked-route | 8.75 | 20.97 | **28.47** | 42.64 | +19.72 |
| hazard-edge | 23.03 | 32.12 | **27.88** | 53.33 | +1.11 |

`hazard-edge` est **fortement censuré par mortalité** (cinq morts sur six à chaque poids) : une fraction de sommeil calculée uniquement parmi les pas observés n'est pas comparable sans interprétation de la mortalité.

Le pilote sur le commit logiciel validé `2c42e9a` reproduit la direction du phénomène sur `oasis` à 24 pas : 34.72% (0), 34.72% (0.1), **56.94% (0.2)**, 59.72% (0.3), trois vies par bras.

**Signal de domination du sommeil :** sur `oasis`, 62.36% à 0.2 dépasse le seuil de diagnostic préenregistré de 50%. Les séries consécutives de `dormir` peuvent dépasser la limite interne par épisode, via réendormissements successifs. Cela n'est pas une preuve universelle de « maladie » mais un facteur rédhibitoire **tant que l'arbitrage critique n'est pas démontré sûr**.

## Besoins physiologiques, hydratation et survie

- `oasis`, 0.2 : 26 actions `manger`, 10 `boire` collectivement, et **aucun pas d'hydratation nulle**.
- `foraging`, 0.2 : 13 `manger`, **1 `boire` pour six vies**, 10.42% des pas à eau nulle (idem pour les quatre bras). Les six individus passent collectivement **212 pas** avec eau inférieure à 15 et source physiquement à une case ; à 0.0 : 209 `attendre`, zéro `dormir`, 3 autres actions ; à 0.2 : **158 `attendre` et 50 `dormir`**, 4 autres actions ; à 0.3 : 62 `attendre` et 149 `dormir`, 1 autre. L'existence physique d'une source voisine ne prouve pas sa connaissance ou sa capacité d'accès : ce point exige une analyse des captures subjectives et du plan, pas un oracle.
- `dry-valley`, 0.2 : zéro `boire`, eau nulle pendant 50% des pas pour les quatre bras, et baisse de `se_deplacer` de 418 (0.0) à 350 (0.2) pour les six vies.
- `empty-land` : aucune ressource hydrique, eau nulle pendant 56.67% des pas pour chaque bras; ne pas l'imputer au coefficient.
- `blocked-route` : eau nulle pendant 27.5% des pas pour chaque bras; caractère physiquement atteignable et perçu à instruire séparément.
- `hazard-edge` : **5 décès sur 6** dans chaque bras, événement létal physique, ne pas supprimer les morts du dénominateur. Les autres mondes terminent tous à 120 pas encore actifs, **sans prouver une survie au-delà**.

**Non-infériorité de survie non établie** : seulement deux étiquettes de graine, cartes fixes par preset, horizons courts, mortalité principalement sur un monde. Le seuil préenregistré de -5 points et son IC ne peuvent être honnêtement validés.

## Consolidation, efficacité et causalité

| Bras w_F | Commandes sommeil, tous les mondes | Reçus techniques `stage10_consolidation_committed` | Reçus pour 100 commandes sommeil |
| --- | ---: | ---: | ---: |
| 0.0 | 660 | 78 | 11.82 |
| 0.1 | 924 | 105 | 11.36 |
| **0.2** | **1378** | **145** | **10.52** |
| 0.3 | 1828 | 176 | 9.63 |

Ce ratio exploratoire **n'augmente pas** avec `w_F` dans l'ensemble équilibré des six presets : davantage de reçus provient surtout de davantage de sommeil, pas d'une meilleure efficacité démontrée. L'agrégation contient des vies mortes très tôt et ne constitue pas un effet causal apparié sur le rendement.

Sur les **36 vies expérimentales à 0.2**, les archives montrent un seul événement `i1_private_procedure_recall_considered`, sur `foraging`, seed 920260, individu 2 (index zéro), au pas 77. Il cite une procédure publiée, une version d'histoire engagée, des épisodes et événements réellement vécus, et applique **un bonus consultatif de 0.06**, sans forcer de commande. La commande effectivement exécutée au pas 77 est **`attendre`**, non le `collecter` suggéré. Il ne démontre donc ni un changement contrefactuel du choix ni un gain de survie ou d'apprentissage. Les événements `memory_recall_proposed` sont des propositions, pas des décisions causées par une mémoire consolidée.

Les changements de hash d'owners et les 145 commits à 0.2 prouvent des transitions techniques d'état/version, **pas** la quantité, la persistance, la pertinence ou l'utilité d'un contenu sémantique. La comparaison avec un groupe jamais exposé, des tâches différées, des ablations isolées, et des **courbes d'apprentissage définies par le succès réel** restent non observées. **Aucune courbe fictive** de « performance mémorielle » n'est publiée.

## Qualité de la preuve et critères

- Vérifié : poids effectif I1 0.2 ; correction de l'admission du sommeil volontaire motivé par `recover_energy` ; chaîne physique WAL, mortalité sans retour arrière ; CI actuelle.
- Observé : sommeil anormalement fréquent en oasis ; remplacement d'attente par sommeil près de l'eau critique en foraging ; hydratation nulle dans plusieurs mondes ; cycles de consolidation techniquement exécutés.
- Non établi : contribution *causale* d'une mémoire consolidée à une décision utile, exactitude/rétention à long terme, courbes d'apprentissage, non-infériorité robuste de survie, gain mnésique par unité de temps, huit familles dont différée/spatiale, au moins 30 réalisations **d'environnement indépendant** par bras/scénario.
- La sélection de 2 graines est une **limitation matérielle**, jamais une prétention à 30 réplicats indépendants. La bootstrap sur seulement deux blocs fournit une distribution purement descriptive, pas une inférence solide.

## Verdict et suites

**Décision scientifique : NO-GO pour l'intégration de w_F=0.2 comme coefficient validé dans I1.** Une augmentation des commits mnésiques ne compense pas un comportement de sommeil préoccupant ni les lacunes de survie. Refus de GO plutôt que tuning arbitraire du sommeil.

**Ne pas fusionner PR #295 telle quelle dans main.** La correction technique `sleep_pressure | active_goal` est séparable et doit être évaluée indépendamment pour I1 : elle préserve Action Control, la mort définitive et I0. Une nouvelle étude prospective doit produire (1) plus de mondes indépendants et deux familles différée/spatiale, (2) des vies longues, (3) les choix réellement exposés/pris dans les situations critiques, (4) un traçage strict des *contenus* propriétaires et de leur réutilisation, (5) des ablations causales isolées, et (6) la validation des seuils par intervalles de confiance.

L'échec du GO ici clôt le **test d'acceptabilité initial**; il ne clôt pas la recherche sur la fatigue cognitive en général. Aucun rollback, connaissance innée supplémentaire, règle de boisson forcée ou falsification du MVP n'est proposé.
