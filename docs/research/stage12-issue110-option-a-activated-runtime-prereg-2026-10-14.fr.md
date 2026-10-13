# Issue #110 / Option A : nouvelle campagne prospective après activation cognitive du critère spatial

**Date : 14 octobre 2026. Préenregistré AVANT le runner et sa CI.** Continuité du protocole de faisabilité `stage12-issue110-option-a-autonomous-feasibility-prereg-2026-10-14.fr.md`, premières vies négatives du [run #38484769557](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38484769557). PR de développement #155 non fusionnée. Le présent protocole n'est pas réinterprété comme une réplication des vies précédentes : nouvelle version cognitive, coût UC supplémentaire et donc nouvelles conditions de décision.

## Hypothèse

L'activation à la naissance du sous-critère `spatial_progress_v1` et du jugement d'agence spatiale dans l'**Action Control existant** peut faire apparaître une chaîne originale de préenregistrement, transition WorldBody, lecture de position vécue, jugement faillible `self/world/unknown`, débit UC distinct, jointure, et application éventuelle au détecteur. Aucune de ces sorties ne doit être fabriquée à partir d'une fixture, d'un échec corporel ou de P-47. Si l'agent ne sélectionne pas spontanément un déplacement vers la cible visible, l'étude est **INCONCLUSIVE sur la chaîne positive** ; elle ne doit pas forcer ce déplacement.

## Plan fixé avant essais

4 vies neuves et séparées, chacune 50 vrais pas maximum : `near_food_free`, `near_food_blocked`, `near_water_free`, `near_water_blocked`, monde 32x32, individu (2,2), cible adjacente Est (3,2) selon les scénarios précédents, température/dangers/nuit/physique inchangés, corpus Equipment physique entraîné hors-vie avant naissance, Stage6 `h_eff=3`, poids sommeil et coûts préexistants inchangés. Activer dès naissance `spatial_goal_progress=True, spatial_goal_cost_uc=1, spatial_agency_cost_uc=1` en plus des frais initiaux de diagnostic et d'agence. Le protocole d'audit garantit que `world` ne peut être admis sans indice de passabilité directement perçu avant la commande exécutée, indépendant du calcul de distance.

Python 3.11 et 3.12 : contrôle de déterminisme, **pas huit individus statistiques**. Aucun seuil du détecteur n'est réduit : `window=12`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75`.

## Sorties/arrêt

Conserver toutes les vies, y compris nulles ou rejetées ; WAL, journal JSONL canonique, SHA-256, head/count, résumé, motifs des décisions, pas, `precommit` spatial ou corporel, `success/failure/unknown`, jugements `self/world/unknown/unavailable`, coût de préenregistrement spatial, coût de jugement spatial, pairs admises/appliquées et leur délai, cognition interdite pendant sommeil/mort, cas de mort et UC refusé. Aucun biais statistique revendiqué sans les deux classes et les seuils atteints.

**Échec logiciel** si un auditeur rejette un journal, si une opération positive UC manque, si un résultat d'objectif provient de l'agence ou l'inverse, si une paire est admise d'une source sans preuve et si la génération courante n'est pas préservée. **Résultat négatif admis** si zéro plan de but, zéro engagement, zéro jugement ou aucun couple utilisable. Un `world` uniquement présent dans les tests de fixture ne compte jamais comme expérience vécue.

Cette expérience n'établit pas à elle seule la reprise après `os._exit` du nouveau chemin, l'autonomie d'apprentissage Equipment ou la calibration scientifique globale. Ne pas fermer #110 ni fusionner #155 sans validation opérateur.
