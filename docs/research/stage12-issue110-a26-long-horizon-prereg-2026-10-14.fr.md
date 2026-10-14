# Stage 12 / #110 : préenregistrement A2.6, robustesse longitudinale physique

**Date :** 14 octobre 2026. Ce protocole est écrit **avant** le runner A2.6 et sa première exécution; source historique `main` `e94e86a868594ed3dac8bee2cec74a8b419876e5`. Il fait suite à A2.5 (16 vies ×42 transitions; 8/8 paires sans perte de nombre de cellules, 4 ingestions physiques, 0/16 vies calibrables) et ne modifie pas la cognition.

## Hypothèses falsifiables

**H6a** : la conservation de diversité constatée sur 42 transitions se maintient jusqu'à **600 transitions physiques dans la même vie**; on ne remplace jamais une mort effective par une simulation de pas supplémentaires. **H6b** : les mécanismes instrumentaux conservent des engagements et attributions corrects sur la durée, plutôt que saturer ou répéter un unique signal. **H6c** : les succès spatiaux dans une condition alimentaire soutenue ne doivent pas être promus fictivement en ingestion; vérifier événements corporels et effet de déplétion. **H6d** : dans A2, aucun obstacle externe préprogrammé ne devient une étiquette privilégiée dans I0.

## Plan figé, budgets et garde mortalité

Reprendre **sans modification** `build_life("near_food_free", 70.0, "horizon_three")` et les flags `progressive_planning=True`, `progressive_evaluation_prefix=True`, `instrumental_geographic_value=ON/OFF`, issus de A2.5. Trois profils physiques × monde : (`restored/free`, `restored/A2`, `sustained/free`) × instrumental ON/OFF = **6 vies autonomes** indépendamment identifiées, chacune plafonnée à **600 vrais pas physiques**, au plus **3600** transitions. A2 après admission t2, retrait t4, mêmes coordonnées fixées pré-naissance. Le monde soutenu a `food_decay_per_step=0.7`, ne pas supposer sa survie jusqu'à 600. La mort et l'arrêt opérateur sont différents : distinguer `dead`, `halted` et `operator_stop`. Un décès n'est ni erreur ni réussite artificielle; respecter la mortalité irréversible.

Deux interpréteurs Python 3.11 et 3.12 répètent la **même** cohorte/déterminisme (6 vies, pas 12 seeds). Ne pas promouvoir ces exécutions en réplications statistiques ni prétendre plusieurs seeds aléatoires sans mécanisme de seed contrôlable. Versionner config, Equipment, code, cohorte, SHA JSONL, WAL durable et audit indépendant par vie. Aucun Oracle ou vérité cachée dans l'agent. Zéro changement Stage 9, sommeil, seuils, compétition, UC et Stage12 `window=12`, `bias_min_outcomes_each=2`.

## Mesures fixes

Tous les 100 pas physiques *effectivement accomplis*, conserver un résumé externe des commandes, nouvelles cellules, refus de mouvements, `manger` avec effet physique, hausses nettes `food`, changements de niveau `food`, engagement `active_goal`, `self/world/unknown`, paires consommées et diagnostics. Conserver le dernier segment partiel si décès. Toujours auditer le journal causal complet, la garde WAL, les objectifs, l'agence, les paires et l'intervention A2; la version A2.5 de l'audit physique/P-48 doit rester fail-closed. Journaux et états de départ sont ancrés par l'export WAL et SHA, pas par la seule sortie imprimée.

Comparaisons appariées uniquement lorsque les vies ON/OFF ont **le même profil physique et les mêmes étapes communes**. Critère exploratoire de rétention : >=80 % des sites distincts dans chaque paire aux jalons 100, 300, 600 **s'ils sont tous deux atteints**. Une disparition d'exploration, des répétitions improductives ou le décès empêchant la comparaison doivent être visibles; ne pas combler une cellule manquante. Pour C4, une commande `manger` et le reçu `ate=berry_a/b` + un gain net corporel donnent la preuve locale d'ingestion; le gain net n'est pas équivalent à la maîtrise alimentaire. Pour C1/C2, calibrage disponible uniquement avec >=2 success + >=2 failure indépendants dans 12 observations de **la même vie**. Pour C5, un même signal P-48 dans 2 options du même cycle est signalé comme **une source partagée**; duplications internes sont refusées. Les seuils ne seront jamais abaissés après observation.

## Décision

En cas de VIe terminée avant 600, rapporter sa durée, sa cause journalisée et le fait qu'elle ne valide pas la stabilité 600. Un échec technique de journal, d'audit ou d'exécution entraîne FAIL technique de ce bras. Un run 600 sans jugements suffisants reste **INCONCLUSIVE pour la calibration**, jamais PASS de l'agence. Publier les négatifs, les dérives inter-Python, la source et les journaux. Aucun changement normatif v1.3.1 ni réception automatique de Stage12.
