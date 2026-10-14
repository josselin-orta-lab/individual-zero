# Issue #110 : préenregistrement prospectif, ablation de l'accès aux buts

**Date : 13 octobre 2026. STATUT : préenregistré avant modification du runner et avant exécution.**
Continuation exploratoire après le protocole fixé de 12 vies (non confirmatoire). Référence des traces antérieures : GitHub Actions `38470291508`, commit du code de la campagne `c701fa40feb8cef415b0e9af86d0e079a4c9a763`. La branche scientifique et les PR #147/#148 restent non fusionnées sur `main`.

## Faits ayant motivé l'ablation, fixés avant l'étude

Les 12 vies autonomes précédentes ont chacune appliqué 50 actions : **600** au total, **318** mouvements exploratoires et **282** sommeils. Parmi **492** résultats `stage6_planning_result`, **zéro** ne possède `proposal_ref`. L'objectif boire s'est activé dans chacune des 12 vies. Sur les **504** témoignages `stage12_action_motive_attested`, **318** portent le motif `cible_exploration` et **186** `sleep_pressure`; aucun ne porte `active_goal`. Donc **zéro** préengagement objectif, **zéro** préengagement d'agence et **zéro** couple mesurable. Les journaux correspondants sont binaires-identiques entre Python 3.11 et 3.12, empreintes SHA-256 par vie vérifiées. Les 600 pas ne démontrent pas de jugement causal positif.

Le planificateur Stage 6 requiert un chemin de simulation jusqu'à un setpoint, et le modèle d'équipement `E-v1-stage6-reference` est une table exacte entraînée sur un corpus de seulement quelques transitions de référence ; les états ou actions non vus sont refusés (ce n'est pas un échec cognitif du détecteur). Le test ci-dessous permet de dissocier la concurrence exploratoire de la couverture du modèle sans introduire de commande forcée.

## Nouvelle question de recherche

**H-X** : retirer uniquement l'activation de l'exploration géographique chez l'individu nouvellement créé (une ablation de configuration cognitivement autorisée), sans modifier les règles physiques ou le moteur décisionnel, peut laisser des options dirigées vers le but atteindre la compétition et l'Action Control. Si `stage6_planning_result.proposal_ref` reste nul, l'hypothèse « la concurrence exploratoire est l'unique cause » est rejetée. L'incomplétude du modèle prédictif et le délai d'activation de l'objectif restent alors à investiguer.

**H-M** : un état perceptif initial compatible avec le corpus exact du Stage 6 (eau initiale 20, source sur la position de départ) favorise les plans sans fournir d'étiquette d'attribution. Un état d'eau initiale 35 reste un contrôle d'incompatibilité possible avec la table exacte. Aucune étiquette `self/world` ne doit être inventée.

## Plan fixé

**Quatre vies nouvellement instanciées**, toutes éveillées (ablation du sommeil déjà utilisée, appliquée de façon identique), toutes construites à partir du même `Stage12Runtime`, mêmes budgets UC versionnés, politique `window=12`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75`, mêmes six phases, mêmes règles WorldBody, sans modifier la connaissance du monde inaccessible à I0. Facteur 1 : `enable_geography=True` (contrôle) contre `False` (ablation). Facteur 2 : `initial_water=20.0` contre `35.0`. Monde `water_available` avec source d'eau et baies au point initial `(2,2)`, conformément au contexte contrasté existant. **50 pas physiques maximum par vie**, sans commander I0 ; pas de reprise d'identité après arrêt. La variation d'exploration est un changement des possibilités cognitives à la naissance, et le résultat ne peut pas être interprété comme un comportement universel.

Une vie a un WAL unique et son journal canonique. Enregistrer les échecs, arrêts et refus UC même si la synthèse échoue. Python 3.11 et 3.12 sur mêmes configurations : contrôle de déterminisme, pas doublement des échantillons indépendants.

## Critères et sorties obligatoires

Outre les audits existants : nombre de buts activés, tentatives de planning `stage6_planning_result`, propositions non nulles, commandes réellement exécutées par catégorie et motif, résultats d'objectifs vérifiés, jugements d'agence réellement exprimés `self/world/unknown/unavailable`, joints admis/appliqués, débits UC et diagnostics. Uniquement des événements canoniques autorisés ; ne pas fournir de post-analyse à I0.

- Si les deux groupes `enable_geography` ont **zéro** plan, la concurrence géographique ne suffit pas à expliquer le phénomène.
- Si l'ablation produit des plans, ne pas en déduire que la carte exploratoire était « boguée » ; distinguer les états physiques accessibles, les commandes décidées et la couverture d'équipement.
- Si des préengagements apparaissent, seuls ceux vérifiés par audit indépendant comptent. Un seul couple ne valide pas les seuils ; `world` conserve son exigence d'indice externe authentique.
- L'absence de plan, de jugement, de couple ou de diagnostic positif est un **résultat nul admissible**, à publier tel quel.
- Toute incohérence WAL/export/provenance, coût UC ou mortalité constitue un **échec technique**, non une validation scientifique.
- **Réception opérateur non sollicitée** à ce stade ; Stage 12 en cours et Stage 9 NO-GO inchangé.

Cette étude exploratoire ne modifie ni la norme v1.3.1, ni la cible normative non fusionnée v1.3.2, ni les détecteurs, ni le corpus d'entraînement exact du Stage 6.
