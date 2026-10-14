# Issue #110, Stage 6 : résultats de la comparaison de profondeurs 3 / 4 / 5 / 6

**Préenregistrement avant code** : commit `4a21430`. **SHA expérimental** : `48bf56946785d60ed1301681673501bbd33b9a75`. [GitHub Actions #38546274961](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38546274961), **8/8 jobs PASS**, Python 3.11 / 3.12, quatre profondeurs × quatre conditions = **16 vies indépendantes** de 12 transitions physiques chacune, **192 pas physiques uniques**. Réexécuter les mêmes seize conditions sous une seconde version Python ne double pas l'effectif. Journaux canoniques, WAL et relevés des décisions inclus dans les artefacts.

## Contraste observé

| Profondeur | Vies | Propositions de plans Stage6 | Sélections `active_goal` | Attributions `self` | Attributions `world` | Couples appliqués | Vies où `attribution_bias` est évaluable |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 4 | 5 | 4 | 2 | 1 | 2 | 0 |
| 4 | 4 | 5 | 4 | 2 | 1 | 2 | 0 |
| 5 | 4 | 5 | 4 | 2 | 1 | 2 | 0 |
| 6 | 4 | 5 | 4 | 2 | 1 | 2 | 0 |

Chaque tranche de profondeur comporte :
- `restored_free` : trois propositions de plan et trois commandes `active_goal`, `self=2`, `unknown=1`, un seul couple `success/self` appliqué.
- `restored_a2` : deux propositions et une commande `active_goal`, `world=1`, un seul couple `failure/world` appliqué.
- `sustained_free` et `sustained_a2` : **zéro proposition Stage6**, zéro engagement et zéro paire malgré un but alimentaire actif, y compris à profondeur 6. Dans ces scénarios, chaque baie apporte 6 et le corps démarre avec 24 de nourriture, avec décroissance. La limite n'est pas seulement la profondeur du plan, mais la capacité à identifier des sous-objectifs utiles lorsque le seuil final est encore éloigné.

**Résultat négatif principal :** de 3 à 6 commandes, aucune amélioration des plans sélectionnés, du nombre de jugements vécus ou du biais calculable dans ces 16 vies. Ne pas présenter une profondeur accrue comme amélioration validée.

## Budget et coût

Les budgets `H_eff=3` de comparaison des options et charges UC restent inchangés ; `planning.max_depth` et la borne `simulator.h_max` ont été augmentés ensemble uniquement pour la comparaison, et les paramètres expérimentaux sont versionnés. Les audits de durabilité, des objectifs, de l'agence subjective, des paires et des événements A2 ont réussi dans chaque vie. Aucun contrôle d'admissibilité n'a été contourné et aucune commande n'a été forcée.

Le runner mesure les durées `time.perf_counter()` à l'extérieur d'I0 et journalise le nombre de propositions ainsi que les charges. Les temps doivent être interprétés comme des mesures indicatives de CI **non appariées à charge matérielle égale**, jamais comme une preuve stricte de performance ni de coût UC de l'arbre de recherche. Le nombre de nœuds explorés est indisponible dans le reçu public Stage6 et n'est pas imputé artificiellement.

## Portée épistémique et reproductibilité

L'obstacle A2 est externe et fixé avant naissance ; les attributions sont produites par Action Control à partir de captures vécues ; la vérité physique et les audits sont indépendants. Les différences numériques IEEE-754 Stage8 précédemment trouvées entre Python 3.11 et 3.12 restent non résolues : ne pas déduire l'identité binaire des journaux du seul PASS des jobs. Les métriques comportementales par profondeur sont concordantes dans les deux interpréteurs.

Le détecteur conserve `window=12`, `bias_min_outcomes_each=2`, `threshold=0.75`. Aucune vie n'a simultanément deux `success` et deux `failure` consommés dans sa fenêtre : **`attribution_bias` non évaluable**. Ne jamais additionner les couples de différentes naissances dans l'état d'I0.

## Conclusion et décision

**PASS logiciel de la comparaison, FAIL de l'hypothèse « augmenter simplement max_depth jusqu'à 6 suffit », Stage12 PARTIAL**. Ce résultat favorise l'étude d'une **planification progressive avec sous-objectifs perceptibles**, qui conserve l'intention et replannifie après de nouvelles captures dans les budgets UC, mais **ce changement cognitif n'est pas implémenté** dans la présente campagne. Il doit être conçu avec des invariants normatifs explicites (pas de déclaration d'objectif impossible sur horizon fini, pas de raccourci Oracle, pas d'injection d'action, action/veto et journal inchangés), puis testé avant toute réception.

PR #155 brouillon, issue #110 ouverte, aucune fusion et aucun Stage12 déclaré terminé.
