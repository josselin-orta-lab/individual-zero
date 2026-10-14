# GA-08 historique : conservation sans réactivation de l'ancienne API

**Date :** 14 octobre 2026. **PR source :** #154. **Intégration de référence :** #155 déjà fusionnée dans `main` au SHA `418ce3d90789609a904cb630fd3cfbf7c21ba55e`.

## Constat vérifié avant la dernière intégration

La PR #154 est antérieure à la migration A2/Option A et utilise un contrat GA08 de runtime qui **n'existe plus** sur le MVP intégré. La CI de réconciliation [#38572334426](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38572334426) a trouvé sous Python 3.11 **21 tests exécutés, 7 erreurs et 2 échecs**. Les ruptures documentées concernent notamment l'argument `spatial_goal_agency` au constructeur Stage11/12 et `Stage12GoalProgressLedger.enable_spatial()`. Ces interfaces ont été remplacées par la naissance versionnée, les engagements perceptifs et les politiques A2 courantes. **Les anciens tests ne peuvent pas être présentés comme réussis contre l'intégration actuelle**.

## Décision d'intégration

Ne pas ressusciter ces anciennes signatures, ne pas remplacer les propriétaires Action Control/Metacognition récents, ne pas réécrire les critères `self/world/unknown` et ne pas affaiblir l'audit M11. Les **12 fichiers exécutables historiques** de la PR #154 (anciens workflows, scripts, module auxiliaire, audit auxiliaire et tests GA08) sont **conservés bit pour bit** dans `docs/research/archive/issue110-ga08-legacy/` en gardant leur chemin relatif. Ils sont du **matériel scientifique historique, non une suite de tests ou un runtime supporté**. Les trois documents de recherche GA08 restent sous `docs/research/`.

Les tests de réception réellement actifs restent les contrats Stage12 et A2 du runtime intégré : `test_stage12_spatial_*.py`, `test_stage12_a2_*.py`, `test_stage12_goal_agency*.py`, les contrôles de WAL/SQLite/M11 et la campagne instrumentale indépendante déjà validés sous Python 3.11/3.12 par #155. La CI `stage12-ga08-reconciled.yml` vérifie en outre explicitement l'archive et la non-réintroduction du module historique.

**Important :** une CI verte du runtime actuel ne vaut pas portage ni validation des 21 anciens tests. Un éventuel portage des scénarios GA08 devrait devenir une campagne différente, préenregistrée, avec les API et mécanismes actuels et la même exigence de preuve externe.

**Conservation scientifique :** deux couples réels `success,self` et zéro `world` de la première étude GA08 restent des observations historiques; la campagne A2 ultérieure de #155 a démontré indépendamment un jugement `world` vécu. Ne pas additionner les résultats de versions et de vies distinctes pour satisfaire artificiellement les seuils du détecteur.

**Statut de réception :** MVP normatif v1.3.2 publié; Stage12 **PARTIAL**, attribution bias **NON ÉVALUABLE**, issue #110 **OUVERTE**, aucune validation scientifique finale ni réception opérateur déclarée.
