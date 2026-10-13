# Issue #110 Option A : préenregistrement de couverture du premier état de planification

Date : 14 octobre 2026. **Préenregistrement antérieur au code du nouvel essai et à son exécution.** PR #155 non fusionnée. Ce protocole est une nouvelle étude exploratoire motivée par les résultats négatifs de [#38486725671](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38486725671), et non une requalification de cette campagne précédente.

## Origine causale de la nouvelle hypothèse

La lecture externe du WAL/JSONL de 4 vies précédentes montre que, au pas 1, I0 active un but nutrition/eau au cycle 2 mais choisit `se_deplacer north`, passant de (2,2) à (2,1). Le premier `stage6_planning_result` au pas 2 est donc évalué depuis (2,1). Le corpus exact externe précédent commençait par `se_deplacer east` depuis (2,2), puis consommation à (3,2), ce qui ne couvrait **pas** cet état effectivement vécu. Les 4 × 42 appels Stage6 n'avaient aucune proposition. Cette discordance temporelle n'est pas une preuve que tout modèle de planification serait insuffisant.

## H1-H3 et conditions de test

**H1** : entraîner physiquement la table exacte sur le préfixe vécu `north` depuis (2,2), suivi de `east` depuis (2,1), puis `collecter berry_a -> manger berry_a` pour la nourriture ou `boire` pour l'eau, permet la planification au pas 2 si I0 réitère spontanément le mouvement initial north. Aucun comportement n'est imposé pendant sa vie ; l'équipement est un corpus externe constitué **avant naissance**.

**H2** : le monde libre place une cible déjà observable à l'Est en (3,1) après ce premier pas north ; un plan de but éventuellement sélectionné peut enregistrer avant l'action le sous-critère `spatial_progress_v1` et formuler au pas suivant un jugement subjectif `self` si la position avance réellement. L'absence de sélection autonome laisse les champs inconnus, même si les tests du simulateur fonctionnent.

**H3** : dans le monde bloqué, la même cible est derrière un obstacle *sur la case (3,1)* ; si, et seulement si, I0 choisit spontanément et fait admettre un mouvement réellement tenté vers la cellule dont il perçoit la passabilité négative, Action Control peut formuler un `world` **faillible**, distinct de l'échec de progression. Aucune commande bloquée ne sera forcée pour obtenir cette classe.

Quatre vies neuves de **50 pas physiques max chacune**, `near_food_free`, `near_food_blocked`, `near_water_free`, `near_water_blocked`. Départ (2,2), ressources/eau en (3,1), environnement 32x32, corps nourriture `food=35,water=70`, corps boisson `food=70,water=20`. Obstacle en (3,1) uniquement dans les scénarios bloqués. Entraînement Equipment sur WorldBody **libre distinct**, trajectoires réellement appliquées `north, east, collect, eat` ou `north, east, boire`; mêmes versions d'équipement dans la condition libre et bloquée de chaque type de besoin. `h_eff=3`, budget UC versionné inchangé (`spatial_goal_cost_uc=1`, `spatial_agency_cost_uc=1`, `goal_agency_cost_uc=1`, `attribution_join_cost_uc=1`), six phases, sommeil, mortalité et détecteurs identiques à la précédente campagne.

Deux interpréteurs CPython 3.11/3.12 = contrôle de reproductibilité, **pas huit individus indépendants**.

## Mesures, gardes et verdicts

Conserver WAL/JSONL et audit de chaque vie, premier mouvement réel, coordonnées du premier appel Stage6, nombre de propositions, plans admis, intentions spatiales avant transition, résultats vérifiés `success/failure/unknown`, jugements `self/world/unknown/unavailable`, coûts UC et refus, couples admis/appliqués/expirés, sommeil/mort et événements manquants. Audit extérieur strict des familles de résultat et d'agence sans accès cognitif aux verdicts du banc. Ne réduire ni `window=12`, ni `bias_min_outcomes_each=2`, ni `attribution_bias_threshold=0.75`.

Première proposition à un plan d'objectif réellement sélectionné = résultat exploratoire de faisabilité, **non validation scientifique du jugement**. `self/world` authentiques exigent leur propre provenance et facturation en plus de l'issue spatiale. Sans plan ou sans jugement, **INCONCLUSIF** et conserver le négatif. Une trace sans attribution avec commande de fixture ne compte pas. La validation finale et l'acceptation opérateur restent indisponibles ; Stage9 NO-GO, issue #110 ouverte, aucun merge.
