# Issue #110, A2.8 : sensibilité prospective et alimentation physiquement vécue

**14 octobre 2026. Verdict global Stage12 : PARTIAL.** La cohorte A2.8 est scientifiquement exploratoire et ne suffit pas à déclarer l'agence subjective validée. Le protocole a été **préenregistré avant toute modification** : `cc01e21c2af9db0ee80dcb33a872b1d581d130b1`. Le code exécuté est `0a50e53ab8fd37affb564924654ef4e5601e3948`. [GitHub Actions #38597587899](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38597587899) : **SUCCESS Python 3.11 et 3.12**, chacun exécutant la même matrice de **24 vies réelles ×42 pas physiques** (soit **1 008 transitions uniques**, non 2 016). Le corpus comprend les WAL durables, les journaux causaux, les résultats individuels et les census indépendants.

## Hypothèse fixée et intervention

Dans A2.7, au pas 3 du monde `sustained/free`, l'option alimentaire avait une évidence `≈0,340` contre `≈0,525` pour l'exploration, avec seuil `0,50`. A2.7 avait déjà éliminé le stale cache des segments progressifs sans aucun nouveau repas. L'hypothèse A2.8 était que l'échelle extrinsèque existante Stage8 sous-estimait le gain alimentaire *prospectivement simulé* par rapport à P-48. Les seules valeurs **choisies avant le run** : `extrinsic_gain=1.0` (référence), `1.6`, `2.0`, gelées **avant naissance** sans modification de la politique P-15, Competition, Stage9, Equipment, UC, seuils subjectifs ou physique.

Plan factoriel : `restored/sustained` × `free/A2` × instrumental OFF/ON × gain 1.0/1.6/2.0. Les deux Python sont des répétitions techniques des mêmes 24 identités et **non** des seeds indépendantes. Tous les effets physiques et auditorats Goal Progress, GA, paires, A2 et WAL sont conservés.

## Données par condition et gains préenregistrés

Le tableau indique `collecter` réellement attesté, `manger` avec `effects.ate` confirmé, niveau `body_after.food` final et sites physiques distincts. Les deux variantes instrumental OFF/ON sont mentionnées explicitement et sont identiques pour ces mesures, sans prétendre à une identité de tout état mental.

| Profil / monde / instrumental | Gain 1.0 : collecté, ingéré, food final, sites | Gain 1.6 : mêmes métriques | Gain 2.0 : mêmes métriques |
| --- | --- | --- | --- |
| restored / free / OFF | 1, 1, 65, 31 | 1, 1, 65, 31 | 1, 1, 65, 31 |
| restored / free / ON | 1, 1, 65, 31 | 1, 1, 65, 31 | 1, 1, 65, 31 |
| restored / A2 / OFF | 1, 1, 65, 28 | 1, 1, 65, 29 | 1, 1, 65, 29 |
| restored / A2 / ON | 1, 1, 65, 28 | 1, 1, 65, 29 | 1, 1, 65, 29 |
| sustained / free / OFF | 0, 0, 0, 33 | **1, 1, 0.6, 31** | **1, 1, 0.6, 31** |
| sustained / free / ON | 0, 0, 0, 33 | **1, 1, 0.6, 31** | **1, 1, 0.6, 31** |
| sustained / A2 / OFF | 0, 0, 0, 32 | **0, 0, 0, 32** | **0, 0, 0, 32** |
| sustained / A2 / ON | 0, 0, 0, 32 | **0, 0, 0, 32** | **0, 0, 0, 32** |

**Observation positive authentique** : dans les quatre vies `sustained/free` à gain 1.6 ou 2.0, `collecter` et `manger` sont réellement exécutés et des augmentations nettes de `food` sont rapportées par `body_after` (une chacune). Les témoins gain 1.0 correspondants n'ont ni collecte, ni ingestion, ni hausse corporelle. La hausse subsiste comme **0,6 unité** au dernier pas du pilote; il s'agit d'un bénéfice **local et faible à 42 pas**, pas d'une alimentation durable.

**Contre-exemple décisif** : avec intervention A2, **aucune** des quatre vies `sustained` testées à gain augmenté ne collecte ni n'ingère. L'hypothèse a priori demandait deux des quatre conditions sustained appariées *couvrant libre ET A2*. **Ce seuil scientifique préenregistré n'est donc PAS atteint**, malgré l'amélioration libre. Ne pas déplacer le critère après observation.

**Non-régression restored** : 8/8 vies gain 1.6/2.0 ont au moins l'ingestion que leurs quatre témoins 1.0 ont, avec le même food final. **Diversité** : les cas sustained améliorés conservent 31/33 ≈93,9 % des lieux physiquement distincts; aucun effondrement observé. Les mondes A2 restent à 32/32 (100 %); restored A2 passent de 28 à 29 sites à gain augmenté. Ces mesures n'indiquent ni robustesse multi-seeds, ni utilité de chaque nouveau site.

**Agence subjective** : `0/24` vies atteignent les deux succès et deux échecs vérifiés dans une même fenêtre de douze observations. La valeur prospective anticipée n'est **jamais** une preuve de responsabilité causale; la causalité vérifiée reste une lecture externe.

## Diagnostic et prochain témoin nécessaire

Les deux gains 1.6 et 2.0 obtiennent le même nombre de repas dans le monde libre : augmenter le gain au-delà de 1.6 ne présente aucun avantage alimentaire observé sur cet horizon. La difficulté A2 suggère une interaction supplémentaire avec les perturbations externes, la couverture de l'Equipment, la trajectoire d'accès ou l'arbitrage post-obstacle. **Cette explication demeure une hypothèse**, pas une cause isolée. Ne pas attribuer le FAIL A2 à une unique pénalité ou ne pas accroître le gain sans expérience départageante. De même, les tests toxiques, effets retardés, mortalité et anti-confusion Oracle restent absents de cette série : leur absence n'est pas un PASS.

Prochain essai A2.9 à préenregistrer : inspecter au **pas immédiatement post-intervention** la disponibilité de simulation pour `collecter/manger`, puis comparer la replanification d'un sous-objectif alimentaire sous un obstacle exogène à un contrôle géométrique, avec gain 1.0/1.6 et P-48 témoin. Vérifier les ressources effectivement accessibles, les reçus de Competition et les risques avant toute généralisation. Si un modèle général de gestion de ressources doit changer, identifier séparément l'impact architectural sur la version normative v1.3.1.

## Critères Stage12, verdicts séparés

| Critère | Verdict | Justification |
| --- | --- | --- |
| C1 attribution subjective | PARTIAL | Jugements vécus préexistants, mais aucune vie évaluant `attribution_bias` |
| C2 distinction causale | PARTIAL | A2 réel audité sans accès Oracle d'I0, couverture contrefactuelle encore pauvre |
| C3 diversité | PASS borné (42 pas) | ≥93,9 % de sites dans les gains alimentaires, pas d'effondrement |
| C4 compétence alimentaire | PARTIAL | Succès local physiquement vérifié en `sustained/free`, hypothèse préenregistrée **NON validée** car A2 reste sans repas |
| C5 discrimination P-48 | PARTIAL | La matrice instrumentale reste un témoin, pas une séparation subjective causale démontrée |
| C6 stabilité prolongée | INCONCLUSIVE | Pas de vie A2.8 à 600 pas; A2.6 a révélé l'échec ancien |
| C7 reproductibilité | PARTIAL | Même agrégats physiques sous 3.11/3.12 ; absence de seeds indépendants et aucune identité binaire revendiquée |
| C8 conformité | PASS borné | Aucun changement normatif ni seuil d'agence, auditeurs/WAL et contrat Stage9 préservés sur cette cohorte |

**Verdict global PARTIAL ; issue #110 à maintenir ouverte ; Stage12 non reçu par l'opérateur.** A2.8 doit être maintenu comme **pilote prospectif sans décision de réglage global**. Le code d'ablation expérimentale et ses résultats peuvent être intégrés si les régressions complètes le permettent; cela ne signifie pas `extrinsic_gain=1.6` retenu pour le MVP.
