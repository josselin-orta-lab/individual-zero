# I1-ECO-v1 — phase A0 : six écologies existantes, sans témoin causal

**Préenregistrement du 29 octobre 2026, avant exécution du pilote A0.** Base de branche `main 7006beee5c5262ff392818b9424455f22e8c4ead`, dépendance : PR #608 (lecteur ECO-v1 de SQLite M11, vérifié et fusionné). Cette branche est **préparatoire** : sa présence ne signifie pas que les six vies ont été exécutées. Ne pas déclencher la campagne A0 avant intégration de #608 et avant vérification CI sur cette tranche.

## Jeu de vie déterministe

Une seule naissance nouvelle I1 M11 par preset, corps et monde entièrement définis par les fichiers `src/i1/lab/world_presets`, vie mortelle, pas de commande imposée, pas d'Oracle ni de rollback. Horizon **fixé par le preset**, sans prolongation après résultat :

| Identifiant | Horizon H | Caractéristique observateur |
| --- | ---: | --- |
| `oasis` | 24 | nourriture et eau à la naissance |
| `foraging` | 32 | ressources réparties |
| `blocked-route` | 36 | obstacle, détour |
| `dry-valley` | 36 | eau éloignée |
| `hazard-edge` | 30 | environnement dangereux |
| `empty-land` | 38 | absence de nourriture et d'eau |

Les rôles nutritifs des baies restent ceux **du modèle v4 existant**, y compris leur danger potentiel. **Ne pas** transformer ces six environnements en témoins statistiques de la même écologie; il s'agit d'un pilote de mesure sur six conditions physiquement différentes. Ne pas sélectionner les vies réussies. Les nouveaux identifiants ne sont pas des réplications indépendantes d'une même condition.

## Procédure, provenance et portes

- Générer le fork I1 exact pour la révision, utiliser les paramètres déjà présents dans `load_preset` et `_birth_parameters`, avec coûts UC identiques au banc des tests naturels. Ne pas changer TD, I0, cognition, monde, physiologie, valeurs de baies, timing de sommeil ni seuil.
- Écrire dans un répertoire de résultats **nouveau** un M11 SQLite individuel par preset, refuser tout écrasement d'un état existant. Conserver les SQLite bruts, les digests des presets, les identités et config physique, les consignes et échelles de ValueNeeds, la révision du code, les horizons.
- À l'arrêt naturel ou à H, fermer la naissance, puis appeler **exclusivement** le lecteur froid `audited_life_metrics` de #608. Aucun résumé calculé par le moteur n'est considéré comme vérification indépendante.
- Publier les six lignes, y compris mort, absence d'alimentation, absence d'eau, sommeil répété, actions stériles et vie non exposée à des options alimentaires. Le rapport expose les quatre déficits et la pénalité après décès. Aucune mort ne peut être censurée comme une vie active, aucune vie morte ne peut redémarrer.
- Les pas de vie, les versions Python et les cycles au sein d'une même vie **ne sont pas** des échantillons indépendants. A0 ne peut produire aucun verdict `GO` sur l'apprentissage naturel.

**Critère de sortie :** `MEASUREMENT_READY` si les **six** M11 ont passé audit et score de vie, sinon `MEASUREMENT_BLOCKED` avec causes par preset conservées. Toute erreur technique est distincte du décès naturel et n'autorise aucune interpolation des résultats.

## Prochain véritable test d'apprentissage

L'étude A1 comparera I1 complet contre témoin TD-read-masked sur des vies appariées dans des écologies contrebalancées `berry_a` / `berry_b`, avec rôles nutritifs physiquement inversés **avant naissance** et invisibles à I1. Le masque doit être attesté sur les chemins amont Planning et Stage8 (dont l'adaptateur `_i1_pending`) ; si les lectures ne sont pas exposées, la paire est `NOT_EXPOSED`. Définir les unités réellement indépendantes et l'horizon avant résultats. A0 est une validation de l'instrument, jamais une conclusion sur la supériorité adaptative.

**Statut initial : NOT_RUN / NOT_ESTABLISHED.**
