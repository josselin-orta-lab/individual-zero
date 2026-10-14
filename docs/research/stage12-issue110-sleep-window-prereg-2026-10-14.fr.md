# Individual Zero #110 — préenregistrement prospectif : sommeil versus admission temporelle d'une attribution vécue

**Date : 14 octobre 2026.** Cette étude est fixée AVANT la rédaction de son exécutable et AVANT toute observation de ses vies. Source initiale exacte : `cc945a4a8ba5da32709f1956e90dccb2dcbab0ac`, branche de la PR #152, enfant de la PR technique #147. Les résultats des 4 vies précédentes du run #38476698354 (source `a42ecb5`) motivent l'étude mais NE sont pas réinterprétés comme des répliques nouvelles. La norme v1.3.1 reste intacte et la proposition GA-01..07 v1.3.2 n'est pas encore intégrée dans `main`.

## Faits connus avant cette expérience

Dans une vie utilisant l'Equipment `physical_food_corpus` physiquement enregistré avant naissance et un horizon de planning 3, I0 a spontanément exécuté `collecter` et `manger berry_a`. Au pas suivant `body.food` était supérieur, et Action Control a produit un jugement subjectif `self` indépendant à partir d'un décrément d'inventaire réellement perçu. Metacognition a admis un couple `(success,self)` avec **1 UC de jointure**. Mais l'individu s'était endormi au pas 5 et la continuation de sommeil au pas 6 n'a pas permis la publication d'un diagnostic : le couple a expiré légitimement, conformément à la stricte fenêtre d'un pas. Dans les 4 vies de la campagne précédente, 200 pas physiques, 3 critères et 3 jugements (2 unknown/1 self) sont obtenus ; **aucun couple n'a pu être appliqué au détecteur**. Le test hostile réchaîné prouve que l'audit refuse une fausse explication de sommeil.

## Question et hypothèses

**H1, effet du sommeil** : la probabilité d'une application d'un couple réellement admis au détecteur dépend de l'existence d'un cycle cognitif éveillé au pas physique immédiatement suivant. Une ablation **pré-naissance** de l'influence du sommeil intrinsèque peut produire un tel cycle sans changer la cognition posthoc ni le seuil de détection.

**H2, comportement autonome** : le contenu de l'Equipment pré-natal et l'horizon Stage6 3 restent **identiques** dans toutes les vies ; aucun choix de commande n'est imposé. L'individu peut choisir de dormir dans n'importe quelle condition. Zéro couple appliqué est un résultat acceptable et n'autorise pas à étendre sa validité.

**H3, provenance** : toute preuve admise ou appliquée nécessite intention préenregistrée, commande effectivement appliquée, capture ultérieure, jugement subjectif original `self/world`, débits UC et références cohérentes. Même si une ablation conserve l'individu éveillé, le détecteur reste `None` sauf seuils atteints sur succès ET échec.

## Expérience fixée : plan factoriel 2×2

Quatre vies nouvellement instanciées, même contexte physique `food=35`, `water=70`, `berry_a=2` au départ (2,2), `berry_a.food_gain=30`, même corpus Equipment issu des **quatre transitions physiques du monde d'entraînement externe** (north/south/collect berry/eat berry) et le même horizon Stage6 `h_eff=3`. Aucune étiquette d'attribution n'est dérivée de ce corpus ou de la simulation.

- Facteur **P39 fatigue_gain** : référence `0.7` ou ablation `0.0` à la naissance, avec `sleep_fatigue_recovery` et le décompte de fatigue UC inchangés.
- Facteur **P40 influence intrinsèque** : `Stage10Config.intrinsic_weight=4.0` (référence) ou `0.0` (ablation explicite). Les options de sommeil restent calculées et facturées ; elles ne sont ni désactivées ni supprimées.

Toutes les vies reprennent le profil développemental historique `consolidation_weight=0.0` sans réduction supplémentaire, `night_weight` conservé, `max_consecutive_sleep_steps` conservé ; les horaires nuit/jour sont inchangés. Ce profil a des limites externes et **n'est pas une simulation complète du sommeil habituel**. Toute ablation est une expérience exploratoire et non la nouvelle politique normative du MVP. Facteurs gelés **avant naissance**, aucune mutation au milieu de la vie.

L'individu poursuit **au maximum 50 transitions physiques appliquées** par vie. Le banc ne force ni `manger`, ni `boire`, ni éveil, ni exploration, ni rétroactivité. En cas de mort/arrêt technique, compter uniquement les transitions réellement appliquées et conserver tous les échecs. Python 3.11 et 3.12 exécutent la **même grille 2×2** comme contrôle logiciel de déterminisme, non huit réplicats statistiques indépendants.

Contrats GA activés à la naissance : `subjective_goal_agency=True`, `goal_agency_cost_uc=1`, `attribution_join=True`, `attribution_join_cost_uc=1`, `diagnostic_sample_cost_uc=1`, `module_occupancy_cost_uc=1`. Détecteur inchangé : `window=12`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75`, `stagnation_steps=4`, `stagnation_tolerance=0.05`, `loop_repetitions=3`, `loop_max_period=2`, `entropy_min_samples=4`, `entropy_warning_fraction=0.25`. Modèle mondial normatif intact, seule sa configuration de développement est précisée à la naissance.

## Mesures et validation

Chaque vie : `life.wal`, `canonical.jsonl` + SHA-256, hash de tête et occurrences, empreinte Equipment et configuration complète, pas physiques, commandes effectivement exécutées, cycles éveillés/dormis, propositions de buts, critères `success/failure/unknown`, jugements authentiques `self/world/unknown/unavailable`, UC payées/refusées, couples admis, *couples appliqués*, couples expirés par sommeil ou refus de budget, diagnostics positifs/négatifs/None, mortalité, reprise si présente et erreurs de vérification.

Audits externes indépendants avec identiques ancres : WAL versus export, `audit_export_bytes`, `audit_stage12_goal_progress`, `audit_stage12_first_person_agency`, `audit_stage12_attribution_pairs`, `audit_stage12_diagnostics`. Aucune importation d'I0, WorldBody ni Bench par les auditeurs eux-mêmes. Tester séparément journaux rechaînés falsifiant la suppression de la capture réduite de sommeil ou du reçu d'expiration.

Critères de lecture préfixés : au moins un **couple appliqué** réellement dans sa fenêtre suffira à soutenir l'hypothèse exploratoire sur le passage dans le détecteur ; si `admitted=1, applied=0`, le résultat est nul et correct. Même `applied=1` laisse `attribution_bias=None` et **ne valide pas les sorties positive/négative** exigeant 2+ résultats de chaque catégorie. Garder les décomptes identiques entre Python 3.11 et 3.12, exposer explicitement toute divergence.

**Non-objectifs :** ne pas construire un jugement `world` sur un non-gain corporel, ne pas prouver la vérité physique indépendante depuis un hash, ne pas requalifier l'entraînement externe du modèle en apprentissage autonome, ne pas réduire le seuil de biais ou étendre la fenêtre, ne pas affirmer Stage 12 GO ni réception opérateur, ne pas fusionner les PR.
