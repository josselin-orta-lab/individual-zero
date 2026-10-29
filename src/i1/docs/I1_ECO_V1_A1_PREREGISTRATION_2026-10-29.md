# I1-ECO-v1 A1 : protocole prospectif de l'effet de la lecture TD sur l'individu complet

**Préenregistré le 29 octobre 2026, après A0 et avant la création de naissances A1.** Base : `main 135455fd0abe3a0e838dd79002461d02771dc336`. Issue primaire #304, questions subsidiaires #305 et #438. Cette tranche documentaire n'exécute aucune vie et n'implémente aucun mécanisme cognitif.

## Question et bornes de preuve

Demander si les valeurs Q acquises par les expériences propres d'I1 **améliorent réellement** sa régulation homéostatique et les décisions physiques ultérieures, relativement à un témoin où seules les lectures décisionnelles de TD sont masquées. Distinguer quatre étapes : une expérience physique nourrissante ou neutre réellement appliquée; une mise à jour TD réellement commise; une lecture Q effectivement utilisée dans un ensemble de candidats concurrentiels; un changement de commande et de bilan physique. Une simple différence Q ou une action différente ne démontre pas une amélioration.

A0 est validé : six vies M11, 7/7 jobs, agrégation `MEASUREMENT_READY` sans problème dans le run #40876309543 au SHA 135455fd0abe3a0e838dd79002461d02771dc336. A0 ne contient ni ablation ni cohorte indépendante. **A1 n'a pas commencé : NOT_RUN.**

## Hypothèses concurrentes

- H1 : la lecture de TD appris après une expérience crédite une option utile, change une décision ordinaire et réduit l'aire des déficits pour le même monde.
- H0 : les lectures sont absentes, non discriminantes, trop faibles, dominées par P-40/Stage6/Competition, ou améliorent un choix ponctuel sans gain écologique.
- H2 : la pénalité immédiate de collecte, les ressources épuisées, les motifs de sommeil, la perception et l'exposition aux options expliquent la trajectoire indépendamment de la lecture TD.
- H3 : le masquage fausse un autre propriétaire, une charge UC, l'ordre des candidats, le tempérament ou la naissance; dans ce cas **INVALID_EXPERIMENT**, jamais un effet causal.

## Phase A1-P : pilote exploratoire, non confirmatoire

Une matrice minimale de **2 rôles physiques contrebalancés x 2 tempéraments préenregistrés x 2 bras** = 8 nouvelles vies M11 mortelles. Le bras `canonical` conserve les lectures Q naturelles; le bras `td_read_masked` exécute toujours les vrais appels `learned_value` une seule fois, sans modifier les poids ni traces TD, mais n'achemine pas leur résultat décisionnel aux deux voies : (1) classement des interactions locales dans Planning; (2) évaluation Stage8, y compris l'adaptateur de `_i1_pending`. Ne pas masquer `q()` utilisé pour calculer la mise à jour TD. Le masque est une instrumentation du harnais de recherche, jamais une option disponible à l'individu.

Disposition locale gelée : une seule cellule accessible avec eau et `berry_a`, `berry_b` présentes aux mêmes quantités; spawn, autres couches, journée, état corporel, coûts UC, budget, monde dangereux/inoffensif et signes de perception identiques dans les deux rôles. Construire les deux `WorldPhysicsConfig` *avant naissance* en permutant uniquement les `BerryEffect` complets entre `berry_a` et `berry_b` (gain alimentaire ET delta intégrité), sans fuite des effets cachés dans Perception. Conserver la mortalité physiologique v4, la consommation énergétique réelle et les paramètres de sommeil. Le choix des noms n'est pas une propriété nutritive connue par I1. Ce laboratoire peut être non représentatif des six écologies A0 : ne jamais extrapoler directement.

Horizon fixe : **48 pas physiques maximum** par naissance, arrêt irréversible au décès; aucune extension sur résultat. Deux sources de tempérament `i1:research-twin:eco-a1-pilot:01` et `i1:research-twin:eco-a1-pilot:02`, gelées avant résultat. Les bras jumeaux reçoivent des identités M11 distinctes, mais le même `temperament_source_id` uniquement selon la voie de recherche existante `matched_temperament_configuration` ou une voie de naissance équivalente testée; jamais de copie d'un état vécu, de Q ou de WAL. **Verrou préalable** : la voie canonique `birth_i1_m11` dérive son tempérament de `life_id` et n'accepte pas directement `temperament_source_id`. Ne pas lancer A1-P tant qu'un harnais réversible et testé ne produit pas deux naissances effectivement équivalentes sur le tempérament sans changement du moteur canonique. Si cela n'est pas démontré, statut `BLOCKED_MATCHING`, ne pas prétendre à une comparaison appariée.

Ces 8 vies sont un pilote de faisabilité. Deux sources de tempérament ne suffisent ni pour estimer un intervalle de confiance fiable ni pour un GO de généralisation.

## Préconditions strictes avant le lancement

1. Prouver égalité des paramètres initiaux des bras : digests de monde et preset (dans un même rôle), projection de tempérament, Stage4/Stage8, configuration TD, besoins, état initial, coûts d'UC et exposition perceptive. Les identités et les journaux M11 restent distincts. Les deux rôles diffèrent **seulement** par permutation physique des effets des baies, attestée par deux digests différents.
2. Tester positivement le masquage sur des lectures de Q réellement apprises et négativement sur `unlearned`/absentes. Requérir un reçu de lecture unique avec `step`, `cycle`, `option_ref`, `signature`, `update_count`, statut, valeur et le propriétaire (Planning amont vs Stage8). Identifier les lectures masquées, éviter toute seconde lecture gratuite et conserver les charges UC et la publication normale.
3. Vérifier que les appels et entrées M11 restent dans leur ordre d'origine, que `Competition` et `Action Control` ne sont pas contournés, que l'option non offerte n'est pas introduite par le harnais, qu'il n'existe aucune commande imposée.
4. Exiger l'audit froid `SQLiteLifeLedger.audit_read_only` et `audited_life_metrics` du `source_commit` exact, des compteurs, hashes, générations, états de naissance et décès. Les nouveaux rapports ne doivent pas modifier les anciens fichiers A0.
5. Préciser dans le rapport les divergences du préfixe antérieures au premier masquage effectivement exposé : toute divergence antérieure ou variation de coût, de physique ou d'état implique `INVALID_EXPERIMENT`.

## Analyse pré-spécifiée

**Unités** : chaque paire de deux naissances distinctes sur un monde et un tempérament gelés; les cycles et pas ne sont pas des réplicats. Les rôles inversés sont des conditions et non des témoins indépendants supplémentaires pour une seule naissance. Aucun regroupement naïf de tous les pas comme N observables.

**Exposition** : `EXPOSED` si une lecture TD `learned` est attestée dans un chemin de sélection applicable, masquée dans le bras témoin avant ou à la première divergence, avec un candidat admissible et au moins une alternative physiquement offerte; sinon `NOT_EXPOSED`, `NO_COMPETITOR` ou `NOT_DISCRIMINATING` selon le premier maillon manquant. Publier *toutes* les paires, ne pas éliminer celles sans exposition.

**Critère principal descriptif** : `deficit_area_total / (4 * H)`, score normalisé de 0 à 1 avec pénalité post-mortem déjà dans ECO-v1; publier les quatre composantes ainsi que l'écart apparié `masked - canonical`. Secondaires : survie/décès et censure, pas vécus, actions de collecte/ingestion/hydratation/sommeil, rôle de la baie consommée, latence de réemploi, première différence de `Competition`, d'admission, de commande et première conséquence corporelle. Ne pas compter le nombre de reçus Q comme observations indépendantes.

**Verdicts possibles** : `INVALID_EXPERIMENT` pour une garde violée; `NOT_EXPOSED` pour l'absence de voie TD informative; `EXPOSED_NO_MOTOR_EFFECT`, `MOTOR_EFFECT_NO_BENEFIT`, ou `PILOT_BENEFIT_SIGNAL` si l'aire est favorable après exposition. Ce dernier reste **exploratoire** : L3 bénéfice généralisable `NOT_ESTABLISHED`.

**Arrêt** : huit vies maximales ou décès naturels, aucun réglage de seuil, de physique, de tempérament ou de protocole après observation. Les échecs techniques sont publiés par paire et empêchent tout verdict de bénéfice. Ne pas lancer de cohorte confirmatoire A1-C avant publication et critique de ce pilote, puis préenregistrement distinct de N, variantes physiques, critère de succès et analyse statistique.

## Intégrité architecturale

I0 intact. I1 moteur canonique inchangé; aucun oracle sur nutrition, aucune mémoire injectée, aucune action forcée, aucune subvention UC ou autorité parallèle. Conserver Q/TD comme propriétaire unique, Competition puis Action Control puis WorldBody comme seuls canaux d'effet. M11, provenance first-person, décès irréversible et reprise à froid restent des conditions de recevabilité, pas des résultats adaptatifs.

**Statut du présent document : protocole déposé, A1-P NOT_RUN, L1 implantation expérimentale NOT_TESTED, L2 exposition NOT_OBSERVED, L3 NOT_ESTABLISHED.**
