# A2.29 : intégration strictement chronologique, après A2.28

Base technique : `main 6f8d574a6a2d13356ff29b56139fc8a05eca82fa`, PR #185 déjà fusionnée. PR #186 n'apporte ici que le protocole, les observations, le script de lecture des événements et un paramètre de cohorte de naissance A2.29 dans le script A2.28. Aucune modification runtime I0, simulateur, perception, UC, M11 ou modèle prédictif.

## Résultat expérimental préalable

Huit individus autonomes mortels B-nés (4 profils de pression alimentaire x obstacle ON/OFF), 48 pas chacun : **384 transitions**. Douze jugements B effectivement produits. Catégories exclusives observées : 247 `no_planner_proposal`, 68 `no_attested_active_goal`, 44 `reduced_sleep`, 12 `goal_selected_B`, 7 `evaluated_but_not_crossed`, 2 `crossed_not_selected`, 4 `evidence_insufficient`. La cohorte A2.29 utilise un espace d'identités différent de A2.28; les graines et mondes restent contrôlés. Python 3.11 et 3.12 répètent la même cohorte, ils ne créent pas 16 vies indépendantes.

Conclusion limitée : le manque de première proposition Stage 6 domine l'attrition **dans ce domaine**, plutôt qu'une concurrence systématique de l'exploration. Ce constat est descriptif et ne permet pas d'accuser la politique de compétition sans essai contrefactuel. Ne pas transformer `incomplete_model` en certitude de sécurité ou d'impossibilité, ni `self` proximal en responsabilité causale distale.

## Garde d'intégration

Exécuter l'expérience et les contrôles négatifs sous Python 3.11/3.12 sur la tête synchronisée. Exiger huit naissances `a229`, 384 pas, aucune erreur d'audit, aucun cas synthétique ajouté ni commande forcée, puis vérifier les mêmes scénarios sur le SHA exact de `main` après fusion. Le changement du script A2.28 conserve `birth_cohort="a228"` par défaut pour reproduire la campagne intégrée. Stage12 PARTIAL, #110 OPEN. PR #199 strictement exclue.