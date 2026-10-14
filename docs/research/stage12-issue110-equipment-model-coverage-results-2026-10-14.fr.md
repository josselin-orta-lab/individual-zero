# Issue #110 : résultat de l'audit Equipment et nouveau verrou de sélection

Date : 14 octobre 2026. Préenregistrement de l'instrumentation : `e67d727`. Source effectivement exécutée : `44cf673dca13aa77bcbb9be96255f7df7070627c`; GitHub Actions [#38552932692](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38552932692) : **PASS** sur Python 3.11 et 3.12, 8 vies indépendantes, 36 pas chacune. Audits WAL/attributions/objectif/A2 validés dans les huit vies. Les deux interpréteurs donnent les mêmes comptes décrits ci-dessous, pas deux cohortes indépendantes.

| Vie progressive | Recherches plan_found | Recherches partial_progress | Réutilisations cache | Recherches incomplete_model | Arêtes Equipment absentes (comptées à travers toutes les recherches) | Reçus de segments proposés | Commandes attestées active_goal |
|---|---:|---:|---:|---:|---:|---:|---:|
| restored libre | 2 | 0 | 2 | 0 | 13 | 0 | 3 |
| restored A2 | 3 | 0 | 2 | 8 | 63 | 0 | 3 |
| sustained libre | 0 | 1 | 17 | 14 | 85 | 18 | 0 |
| sustained A2 | 0 | 1 | 1 | 31 | 174 | 2 | 0 |

Les `segments_proposed` comptent les reçus de proposition et réutilisation dans plusieurs cycles, **pas** 18 segments physiques distincts. Aucun jugement supplémentaire ni paire diagnostique ne découle des propositions soutenues. Ce résultat **invalide l'explication unique « le modèle ne produit jamais de segment »** : il en produit un original dans chacune des deux vies `sustained`.

La majorité des recherches sans plan sont néanmoins `incomplete_model`. Cela démontre un manque de couverture d'Equipment parmi les arêtes réellement évaluées ; **cela ne suffit pas à attribuer l'absence d'action à Equipment**, car une option partielle peut malgré tout être présentée au concours. La différence entre proposition, évaluation par `Stage6OptionEvaluator`, accumulation dans `Competition`, admission et commande appliquée devient la question prioritaire. Le modèle exact `FrozenTableEquipment` ne dispose que de quatre exemples d'entraînement pré-naissance ; une transition absente doit rester indisponible, sans extrapolation cachée.

## Investigation supplémentaire en cours

Le commit `93b42eb` ajoute à `scripts/run_stage12_issue110_progressive_ab.py` une jointure des reçus `stage6_planning_result`, `stage6_option_evaluation`, `stage12_action_motive_attested` et affiche `PROGRESSIVE_FUNNEL`. Ce diagnostic **ne modifie ni I0 ni ses UC, ni ses décisions**. Il doit distinguer les options non évaluables des options évaluées avec `evidence <= 0` qui ne peuvent pas franchir le seuil de compétition. Run [#38555144317](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38555144317) démarré sous Python 3.11 et 3.12; ne pas affirmer de résultat sur le funnel avant sa fin.

## Décision actuelle

L'hypothèse spécifique « modèle insuffisant = aucun segment » est réfutée ; la difficulté reste **un segment proposé mais non choisi comme motif d'objectif**. La planification progressive reste opt-in et non validée comme amélioration. Ne pas injecter de priorité, de force motrice ni de vérité de l'oracle. Ne pas transformer un succès de segment en succès d'objectif. Seuils du détecteur `window=12`, `bias_min_outcomes_each=2` inchangés. Verdict **PARTIAL**, calibration `attribution_bias` NON ÉVALUABLE, Stage12 non reçu, PR #155 draft, issue #110 ouverte.


## Résultat du funnel propositions → évaluations → action

À la suite du commit `93b42eb`, [CI #38555144317](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38555144317) **PASS Python 3.11 et 3.12** et publie les lignes `PROGRESSIVE_FUNNEL`. Dans le monde `progressive_sustained_free`, 18 reçus de propositions (un original + réutilisations) portent la même référence `option:goal:eat:food:1:2:sim:se_deplacer:progress`. Dans `progressive_sustained_a2`, on retrouve 2 reçus portant cette référence, dont un original. Les 20 reçus ont **zéro entrée `stage6_option_evaluation` correspondante au même pas et à la même option**, ainsi que **zéro `stage12_action_motive_attested` correspondant**. Résultat identique dans les deux versions Python. Ce sont des **comptes de reçus**, pas 20 segments exécutés.

Ce constat déplace le diagnostic : il n'est pas démontré que les segments ont été évalués avec un score nul ou négatif ; au contraire leur évaluation Stage6 est absente dans le funnel observé. Le blocage se situe **entre proposition et évaluation compétitive** (publication, filtrage Gatekeeper, transport ST, enregistrement Competition, ou autre contrat intermédiaire). Aucune cause précise parmi ces étapes n'est encore démontrée. En particulier, toute majoration artificielle de leur score serait injustifiée.

**Nouvelle étape requise** : instrumenter la trace de `option_registration`, `planning` contribution et le motif de refus exact du Gatekeeper pour la référence précitée, puis vérifier la présence dans `Competition.candidate_proposals`. Le moteur Equipment reste extrêmement lacunaire, mais un manque de modèle ne suffit plus à expliquer l'absence d'action pour le segment déjà proposé. Le rapport A/B historique reste inchangé, les seuils Stage12 et le MVP normatif v1.3.1 aussi.
