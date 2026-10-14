# Proposition **non normative** : indice extérieur vécu et sous-objectif spatial pour l'attribution d'agence

**Date : 14 octobre 2026. Statut : proposition nécessitant arbitrage opérateur, NON autorisée comme règle cognitive exécutable.** Issue #110 ; PR normative v1.3.2 #148 ; Stage 12 non reçu. La spécification v1.3.1 n'est pas modifiée.

## Pourquoi une décision est nécessaire

Les expériences réelles de la PR #153 ont apporté 3 couples uniques `(success,self)` **appliqués** au détecteur, mais aucun jugement `world`. Le producteur Action Control GA actuel juge `self` après `manger` uniquement sur la diminution de l'inventaire perçu. Le registre de progrès vérifie indépendamment un gain corporel de `food/water/energy/integrity`. Une collision avec un obstacle spatial, une prédiction P-47 non conforme ou un non-gain de nourriture ne prouvent pas qu'une cause extérieure a dominé ce résultat. Une classification automatique `failure -> world` serait circulaire et invalide.

`PerceptualCapture` expose `(x,y)`, `adjacent: PerceivedCell(direction, x,y, passable, water_source, resources, creature)`, `current_water_source` et des entités visibles. Cela offre un vocabulaire de **perception locale d'obstacle**, non une vérité cachée sur la cause. Pour constituer un résultat *pertinent à l'objectif*, le critère strictement corporel doit être complété par un résultat spatial préenregistré et d'un type vérifiable par Perception.

## Choix soumis à l'opérateur

### Option A (recommandée, modification normative ciblée)

Autoriser un `goal_subcriterion_kind=spatial_progress_v1` **en plus** de `one_step_body_strict_gain_v1` dans le registre canonique existant de Metacognition, sans second historique. Avant un déplacement **admis** au service d'un objectif de ressource dont la localisation est déjà perçue, préenregistrer l'emplacement observable de la cible, la position initiale, le trajet/direction choisi, la distance Manhattan initiale, le seuil strict de réduction de distance, la fenêtre unique `t+1`, la commande et les identités. Ne pas confondre cette réduction avec l'atteinte du but global.

Action Control conserve la seule propriété du producteur `GoalAgencyService` ; sa politique `spatial_mechanism_v1` reçoit **uniquement** l'engagement de déplacement volontaire, la capture perceptive localisée avant l'action, la capture suivante et un indice de passabilité dans la direction *exactement commandée* ; jamais le booléen `success/failure` issu du registre, la règle P-47 d'attribution, le `WorldBody` brut, l'Oracle ni le banc. Son jugement :
- `self` **possible** lorsque la copie efférente et le déplacement effectivement perçu, orienté vers l'emplacement cible préalablement identifié, soutiennent une contribution personnelle ; cela ne prouve pas que l'individu a causé le résultat global.
- `world` **possible** lorsque la direction préengagée est **perceptivement connue comme non passable** et qu'aucune variation de position n'est constatée dans la capture suivante ; l'agent formule le jugement faillible « la contrainte extérieure a limité cette tentative spatiale ». L'indice de passabilité doit appartenir au but et au mouvement tentés et être vérifié indépendamment du résultat calculé. Ne pas utiliser l'échec spatial seul. Si le candidat n'était pas observable, si l'obstacle apparaît seulement après le choix, si plusieurs causes sont plausibles ou si la copie efférente manque : `unknown`.
- `unknown` reste la sortie par défaut pour toute ambiguïté et tous les critères corporels sans mécanisme spatial légitime.

**Risque conceptuel :** si la passabilité était déjà connue non vraie avant le choix, il faut s'assurer que l'Action Control et la sécurité peuvent légalement admettre ce déplacement (il ne faut surtout pas forcer une commande interdite pour produire `world`). La simple présence d'un obstacle ne garantit pas une tentative autonome. Il est possible que le moteur choisisse toujours un autre chemin, menant légitimement à zéro `world`. Dans ce cas la preuve positive reste indisponible.

Le contrat GA ajouterait une politique versionnée, une capture/admissibilité distincte, un type de résultat `spatial_progress_v1`, un coût UC déterministe positif déclaré **avant naissance**, une extension atomique M-11 dans les propriétaires existants, un nouvel auditeur purement externe de pertinence spatiale et d'unicité, puis des contrôles rechaînés adversariaux. **Aucune modification de la spécification existante ni implémentation sans arbitrage explicite.**

### Option B : conserver la restriction actuelle, sans nouvelle norme

Le détecteur continue à traiter `self` et `unknown` dans les objectifs corporels, ne fabrique jamais `world`, et reste à `None` si les seuils ne peuvent être atteints. C'est la décision la moins risquée si l'opérateur ne souhaite pas ajouter de critère spatial au MVP, mais elle laisse l'issue #110 **non résolue** pour les diagnostics positifs/négatifs sur les vies autonomes.

### Option C : inférer `world` de P-47 ou du non-gain corporel

**Rejetée** : viole la séparation entre exactitude prédictive, réalisation de critère et croyance subjective. Rendrait les rapports apparemment favorables mais scientifiquement non défendables.

## Campagne obligatoire après décision

1. Préenregistrer la nouvelle famille de sous-critère avant toute action ; comparer des mondes physiques avec passages libres/bloqués, objectifs perçus identifiables et décisions autonomes.
2. Vérifier des journaux réels de `self/world/unknown`, dont les indices perceptifs sont d'une source indépendante du calcul de réussite, avec les deux classes de résultat et références uniques.
3. Vérifier par audit externe et tests rechaînés : obstacle caché, mauvaise direction, obstacle unrelated to goal, mode de passabilité falsifié, jugement après échéance, identité étrangère, UC refusé, réveil/sommeil, arrêt mortel, restauration atomique M-11 et aucune fuite de labels P-47.
4. Conserver les seuils actuels `window=12`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75`. Dans une vie de 600 pas sans `world` légitime, aucun GO.
5. Opérateur vérifie l'ensemble des traces synthétiques et physiques via un résumé automatisé, sans lire des milliers d'événements ; Stage 12 seulement réceptionné après preuve et décision expresse.

**Recommandation : option A, sous réserve d'autorisation normative ciblée.** Cette proposition ne donne pas mandat d'inventer des jugements `world` ni de modifier les normes pendant la campagne en cours.
