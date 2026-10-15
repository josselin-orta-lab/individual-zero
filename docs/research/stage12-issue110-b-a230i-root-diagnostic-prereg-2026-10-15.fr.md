# A2.30-I : préenregistrement du diagnostic de premier pas, sans changement décisionnel

**15 octobre 2026, avant toute modification du planificateur.** Les résultats A2.30-G/H sont connus : sur 121/121 recherches incomplètes, zéro première transition prédictible ; 620 appels initiaux refusés, dont 468 commandes exactes absentes et 152 commandes présentes avec état différent. La preuve concerne le modèle présent à l'instant de chaque recherche ; elle ne démontre aucune impossibilité physique ni la pertinence de chaque transition alimentaire.

## Intervention logicielle minimale

Dans \`SimulatorPlanner.search\`, **compter passivement les tentatives réellement faites à la racine** : \`root_candidate_edges\`, \`root_available_edges\`, \`root_unavailable_edges\`. Aucun appel \`Simulator.rollout\` additionnel, aucune action candidate nouvelle, aucune augmentation de \`max_depth\`, aucune prédiction de secours. La condition exacte de \`no_predictable_first_step\` est :

- recherche épuisée avec statut historique \`incomplete_model\`,
- au moins une commande candidate examinée à la racine,
- **aucune** transition initiale disponible et **toutes** les candidates de la racine essayées et indisponibles.

Le statut public \`incomplete_model\` **reste inchangé**, de même que \`plan_found\`, \`partial_progress\` et \`not_found_within_horizon\`. Le nouveau motif est un **champ supplémentaire de diagnostic**, pas une nouvelle certitude cognitive. Les \`plan_found\` précoces ne doivent jamais déclarer une couverture complète de toutes leurs candidates si la recherche s'est arrêtée avant le dernier appel.

## Contrôles avant toute fusion

1. Unitaires Stage6 : cas initial sans aucune arête, cas avec première arête connue mais échec ultérieur, succès anticipé, objectif déjà atteint, progrès partiel, absence de faux diagnostic quand l'horizon tronque la recherche.
2. Pas de modification des commandes et des résultats de \`search\` : mêmes \`status\`, \`commands\`, \`predictions\`, \`expanded_states\`, \`unavailable_edges\`; les nouvelles données n'ont aucune influence sur les décisions.
3. Intégration : journal Stage6 conserve sa chaîne vérifiable ; valeurs diagnostics égales aux compteurs réellement exécutés. Régression Stage12, M11, UC et séparation Oracle inchangées.
4. Le changement de quelques **champs supplémentaires dans le journal** change potentiellement ses octets/hachages : ne jamais prétendre que le nouveau journal a le même SHA que l'ancien ; comparer les effets/décisions sémantiquement, et **ne pas réécrire les résultats scientifiques des cohortes précédentes**.
5. Si un test ou une comparaison démontre une régression, ne pas intégrer. Aucun amendement normative v1.3.1, aucune clôture #110, Stage12 PARTIAL.

Ce développement constitue une **amélioration de l'observabilité**, non un correctif prouvé du comportement alimentaire. Toute tentative de généralisation d'Equipment demande un protocole de sécurité distinct.
