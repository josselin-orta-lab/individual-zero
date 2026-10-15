# Stage 4 : migration du témoin E-0 vers la perception locale réellement autorisée

**15 octobre 2026.** Modification **exclusive aux tests** de Stage4. Aucun changement au moteur, au monde, à la perception, aux UC, au MVP ou aux seuils de compétition.

## Cause caractérisée avec témoin sur `main`

Le groupe de sept échecs Stage4 observés dans [CI #38776664560](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38776664560) est reproduit à l'identique sur `main cb630f6edffab1aecb4630e2b7da2369bb593118`, sans Stage6 A2.30-I, sous Python 3.11/3.12 (branche `audit/ci-main-baseline-20261015`, commit témoin `453f357d0e13e6f67bfe6a0d8144e439803f5a77`).

La cause est une ancienne fixture : I0 naît en (2,2), avec l'eau en (4,2), mais les tests exigent un premier plan vers une ressource à Manhattan **2** alors que `WorldBody.capture_local` n'expose que les entités à distance **≤ 1**. Le vrai but « boire » naît au cycle 2, les UC de planification sont payées et acceptées, mais aucun lieu d'eau n'est connu : Stage4 ne crée correctement ni proposition ni action et attend. Les anciennes attentes de déplacement reposent donc sur une connaissance privilégiée désormais interdite.

## Contraste physique enregistré sur la branche d'audit (avant la migration)

Avec une unique modification *externe* et explicite du monde visible, source d'eau en (3,2) :
- au premier pas, Stage4 choisit réellement `se_deplacer(east)`, source `decision`, cycle 3 ;
- au deuxième pas, Stage4 choisit réellement `boire`, source `decision`, cycle 1 ;
- la position finale est (3,2), et l'eau corporelle passe de 20 à 60.

Ce contraste démontre que le planificateur E-0 fonctionne sous connaissance permise, sans lui fournir l'Oracle. La seule limitation testée est l'absence d'exploration spontanée d'une cible inconnue. Une affirmation de réussite alimentaire généralisée ou d'attribution causale ne serait pas justifiée.

## Nouvelles attentes et garde-fous

1. Les tests d'action, de fondation S_t, de progression de plan et de comparaison utilisent désormais un **objectif perceptivement visible**. Ils conservent les commandes réellement produites, les liens de provenance, le critère de satisfaction, les deux comparaisons de commande et les invariants de compétition.
2. Les deux tests de transition létale gardent le **même danger caché sur (3,2)**, désormais à la première case vers une eau visible, et exigent toujours transition létale, restauration autorisée dans le *vieux mode non mortel Stage4*, blocage protégé et cohérence des UC.
3. Le test de mouvement bloqué conserve une **vraie défaillance physique**, due à un échec d'action externe préengagé, non révélé à I0, plutôt qu'à un obstacle déjà visible que l'agent n'aurait aucune raison de franchir.
4. Le monde historique à eau lointaine (4,2) est **conservé comme contrôle négatif séparé**, qui impose but actif, aucune proposition inventée et `fallback attendre`.
5. Aucune modification au statut mortal v1.3.1 : les anciens tests de rollback Stage4 doivent rester clairement distincts des vies autonomes mortelles M11, qui ne peuvent pas être ressuscitées.

## Réception scientifique

Cette migration est une **réparation de témoignages logiciels historiques** et non la résolution de la compétence de navigation vers une cible initialement inconnue. Le motif `incomplete_model` A2.30 concerne un planificateur Stage6 différent et reste une question séparée. Le défaut Stage5 de persévérance reste à traiter sous [issue #203](https://github.com/josselin-orta-lab/individual-zero/issues/203). Ne pas présenter la suite globale comme verte avant la réexécution intégrale.

**PR #199 : hors périmètre strict.**
