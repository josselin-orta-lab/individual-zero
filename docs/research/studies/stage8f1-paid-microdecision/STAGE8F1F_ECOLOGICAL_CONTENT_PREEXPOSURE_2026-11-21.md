# Stage8-F1F · huit écologies fixées et lecture des moyennes personnelles payées

**Préenregistrement avant tout reçu F1F. 21 novembre 2026.** Source de base `77c3e3395dfa379851d6192a7ec09968727c9ed9`. Chaîne F1C fixe : [run #44837981694](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44837981694), original `F1C_PAID_NATIVE_ORIGINAL.json`, SHA256 `e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d`. F1D (`NO_NEXT_MOTOR_DECISION_EFFECT_IN_THIS_SYNTHETIC_CASE`) et F1E (`NO_EQUAL_COST_CONTENT_EFFECT_ON_NEXT_MOTOR_COMMAND_IN_THIS_CASE`) sont négatifs et ne sont **pas réouverts**.

## Question falsifiable

Sur **huit contextes écologiques nommés avant exposition**, la variation du *contenu* des moyennes d'EffectsModel (`dormir`, globale `*`) issue de l'unique expérience F1C authentifiée influence-t-elle la commande motrice suivante, à travail cognitif et débit corporel identiques ? Chaque contexte forme une comparaison appariée **`full` / `sham` / `mask_both`**, avec cerveau appris, valeurs TD, tampon et mémoire occupée exactement identiques, sauf le readout temporaire des deux moyennes dans `mask_both`.

## Huit `WorldSpec` entièrement fixés maintenant

Le monde synthétique est **3×3, naissance en (1,1)**, corps `[0.052,75,60,90,95]`, même génome `midpoint()`, même graine `20261120`, mêmes `BodyLaws v2`. L'environnement au **tick 0** ne montre **aucune ressource**, garantissant le même premier `World.capture` qu'en F1C. Les ressources suivantes sont **dormantes initialement** (eau : stock=0, max_stock=2, gain=25 ; aliment : quantité=0, max=2, token exactement `f1f-neutral-food`, sans effet caché d'aliment) et sont révélées **uniquement** par `WorldSpec.changes` au tick **1**, après le premier `World.step(dormir)`. Ne jamais introduire de ressource directement dans le cerveau ou dans les scores.

| ID canonique | Eau révélée tick 1 | Aliment révélé tick 1 |
|---|---|---|
| `bare` | aucun | aucun |
| `water_here` | (1,1) | aucun |
| `water_north` | (1,0) | aucun |
| `water_east` | (2,1) | aucun |
| `water_west` | (0,1) | aucun |
| `food_here` | aucun | (1,1) |
| `food_east` | aucun | (2,1) |
| `mixed_here_water_east_food` | (1,1) | (2,1) |

**Une seule famille, huit mondes déterministes, aucune recherche aléatoire, aucun monde ajouté après les résultats.** Les changements écologiques au tick 1 sont un scénario prospectif **de développement**, pas la continuation historique des vrais mondes G2. La première action de F1C doit émerger librement de `Mind.decide` et être vérifiée par le reçu original; l'apprentissage doit ensuite être effectivement facturé **0,1096 E + 0,174 V** et conserver exactement le SHA du Mind original F1C `retain`, avant séparation entre bras. Si une écologie modifie cette source mentale, elle est INVALID, pas remplacée.

## Interventions et critères fixés

Pour chaque écologie, **trois copies profondes** du même Mind F1C appris/financé et du même World écologique au tick 1. `full` lit les véritables moyennes, `sham` effectue le remplacement identique puis restaure, `mask_both` montre *seulement au cours du calcul* les moyennes personnelles déjà présentes avant l'apprentissage F1C, sans changer les clés, `n_eff`, `count`, nombre d'entrées, buffer, TD ou incertitudes; la vraie mémoire est restaurée après le choix. Aucun comportement n'est imposé; les commandes `boire`, `collecter`, `dormir`, `se_deplacer`, `attendre` et l'abstention demeurent sous contrôle natif.

**Unité primaire** : pour chacun des huit contextes, différence `(action,param)` entre `full` et `mask_both`. **Gate obligatoire par contexte** : même `World.capture` et monde/état vivant initial, même `CognitiveWork` (4 coordonnées), même facture `World.step` énergie et vigilance, chaque débit entièrement payé, même `sham` en sortie motrice/commande/cout et même mémoire pré- et post-intervention. Les divergences de facture ou de travail sont **NON APPARIEES**, jamais assimilées à un effet de la mémoire. Une mort véritable est conservée, sans secours ni apprentissage ultérieur. **Aucune égalisation fictive** par bourrage de cycles ou augmentation cachée de budget.

**Estimand unique** : `K/8`, nombre de contextes validement appariés avec commande motrice différente. Si 8/8 contextes valides et K=0, statut `NO_MEAN_CONTENT_MOTOR_EFFECT_IN_EIGHT_PREREGISTERED_ECOLOGIES`; si 8/8 valides et K>0, statut `MEAN_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_PREREGISTERED_ECOLOGIES`, sans conclure à l'utilité adaptative. Si un seul contexte échoue à la parité, statut global **`INCONCLUSIVE_ECOLOGY_COST_GATE`**, avec toutes les mesures par contexte publiées et aucun dénominateur ajusté a posteriori. Aucun test de significativité sur les huit mondes déterministes non échantillonnés aléatoirement. Les différences de score ou de prévision demeurent *secondaires*.

**Audit** : originaux natifs sources vérifiés au SHA octet, deux processus Python 3.11 indépendants octet-identiques, second job Python 3.12 stdlib-only sans `Mind`, `World` ni producteur, qui valide les 8 spécifications, les reçus `World.step` et deux devises, les témoins de mémoire complète, les masques de moyennes et classe indépendamment les commandes. Données natives conservées avec provenance; ne pas réécrire les verdicts précédents.

**Limites** : tests développement synthétiques, pas `run_life`, aucune nouvelle vie ni cohorte scientifique, pas de mémoires historiques G2, pas d'inférence de survie/héritabilité/gamma123; Stage8-E2 `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY` reste fermé.
