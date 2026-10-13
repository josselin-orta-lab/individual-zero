# GA-08 : préenregistrement de la campagne spatiale autonome, issue #110

**Date : 14 octobre 2026. Préenregistrement AVANT toute intégration du nouveau contrat dans le runtime et AVANT la première campagne physique GA-08.** Cible normative GA-08 de MVP v1.3.2 dans la PR #148. Le noyau fonctionnel isolé et testé sur Python 3.11/3.12 existe dans la PR #154 ; les tests de fixture ne sont **pas** des vies autonomes.

## Hypothèses testables

- **H1, prémotivation :** I0 peut disposer d'une cible locale d'eau ou de baie perçue *avant la commande* et réellement entreprendre `se_deplacer` à destination, en motif `active_goal`, sans que le banc lui impose la commande ni contourne Action Control.
- **H2, provenance :** une intention spatiale `strict Manhattan distance decrease` engagée avant la transition est clôturée au prochain pas vécu par Metacognition, indépendamment d'un jugement `self/world/unknown` calculé par Action Control à partir d'une copie efférente et de la cellule adjacente déjà perçue.
- **H3, jugement personnel :** lorsque la destination pertinente est libre et la position correspondante perçue au cycle suivant, `self` est une hypothèse subjective admissible, sans vérité causale physique prouvée.
- **H4, obstacle perceptible :** lorsqu'une cellule de destination pertinente est déjà perçue comme non passable et qu'I0 commande *réellement et librement* le mouvement admis, le mécanisme peut formuler `world` après constat d'absence de déplacement. Un tel mouvement peut ne jamais être sélectionné par un agent autonome raisonnable ; `world=0` reste un résultat légitime, et le banc n'intervient pas pour le fabriquer.
- **H5, diagnostic :** les couples `success/failure` avec `self/world` sont joints et consommés uniquement avec des sources séparées, coûts UC réels et une phase métacognitive éveillée au pas suivant. Le détecteur demeure `None` si les seuils `window=12`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75` ne sont pas atteints.

## Plan expérimental à geler dans le runner AVANT toute exécution

Factoriel **2×2** : emplacement cible adjacent visiblement libre / adjacent visiblement non passable × objectif hydratation / objectif nourriture. Chaque condition forme une **vie neuve**, avec mêmes budgets, scheduler, paramètres de sommeil, Equipment de développement versionné, monde 32×32 et physique normative. Comparaison d'une branche aux paramètres normaux et d'un contrôle négatif où la cible n'est PAS perceptible en amont ; l'intention ne doit jamais être créée dans ce dernier cas. Source d'eau/baie : exactement une cible locale (direction, position et propriété physique fixées avant naissance). Un obstacle visible peut rendre la commande impossible à sélectionner ; conserver cette absence.

Au plus 50 vrais pas appliqués par vie, renouvellement d'identité obligatoire, pas de relance d'une vie terminale. Python 3.11 et 3.12 sous mêmes graines/configurations : contrôle de déterminisme, pas doublement des observations statistiquement indépendantes. Aucune action `se_deplacer` imposée, aucune injection de `world`, de réussite ou de cause cachée, ni suppression du sommeil. Les UC `goal_agency_assessment`, `stage12_attribution_join`, `stage12_diagnostic_sample` doivent être positives, figées avant naissance et effectivement prélevées. Un coût de nouveau critère spatial doit être inclus dans le budget métacognitif versionné et justifié avant la naissance.

## Mesures et vérification indépendante

Conserver WAL et JSONL canoniques par vie, SHA-256, head_hash, occurrences, code exact SHA, versions politiques, identité de vie, objectif, cible source perceptive, passabilité avant commande, direction, commande physiquement admise et appliquée, position au cycle suivant, critère spatial `success/failure/unknown`, jugement `self/world/unknown/unavailable`, provenance de chacune des deux sources, UC acceptées/refusées, références uniques, couples admis/appliqués, sommeil, décès et reprises.

L'auditeur **extérieur à la cognition** doit reconstruire les événements et rejeter les faux journaux entièrement rechaînés qui inversent la passabilité, changent la direction, la cible, la position, le motif ou l'identité, réutilisent un même pas, suppriment une perception, masquent un refus UC ou fabriquent un diagnostic. La chaîne SHA-256 est une intégrité technique, pas un oracle de vérité physique.

## Verdicts préfixés

- **PASS logiciel** seulement si l'implémentation réelle, M-11, coûts UC, indépendance des sources, mort et audits adversariaux ont passé, sur Python 3.11 et 3.12, en plus des tests purs.
- **Hypothèse exploratoire soutenue partiellement** si des commandes autonomes réellement appliquées produisent des jugements et des couples GA-08 recevables. `world` sur fixture ne compte pas.
- **Inconclusif** si les décisions autonomes ne tentent pas de déplacement vers une case bloquée ; ne pas forcer une tentative ni réduire les seuils.
- **NO-GO logiciel** si un jugement `world` est admis sans obstacle spécifiquement perçu et commande réellement appliquée, si la cognition est postmortem ou si une opération cognitive n'est pas facturée.
- **PAS de Stage 12 GO** avant une réception opérateur explicite ; validation scientifique finale du MVP séparée. Stage9 demeure scientifique NO-GO.

La PR #154 ne constitue à son état initial qu'une **tranche de développement sans activation du runtime**. Cette limite doit être conservée dans les rapports et les conclusions jusqu'à la preuve physique intégrée.

## Annexe de verrouillage des paramètres, avant premier run GA-08

**Amendement prospectif, précédant la création du runner expérimental.** Six vies au total : les quatre cellules préenregistrées `water/food × free/blocked` plus **deux contrôles d'absence de cible** (`water_absent`, `food_absent`). Une absence de cible signifie que la ressource n'existe pas dans la cellule adjacente, non une redaction cachée injectée à I0. Tous les mondes débutent à `(2,2)`, cible éventuelle `(3,2)`. Le cas bloqué conserve une ressource physiquement présente sur cette case mais l'obstacle la rend non passable. Les autres dangers/créatures non concernés sont retirés dans **tous** les mondes. Les cas d'eau débutent à `water=20, food=75`; les cas de nourriture à `food=35, water=75`. Énergie `50`, intégrité `100`; baie `berry_a` disponible en quantité 2, gain alimentaire `30`, pas de gain d'intégrité. Un corpus d'équipement exactement reproductible est entraîné **hors vie** : `se_deplacer east`, puis `boire` pour eau, ou `collecter berry_a`, `manger berry_a` pour nourriture. L'horizon Stage 6 est fixé à `h_eff=3` et `max_depth=3` dans toutes les vies ; l'équipement est reconstruit séparément à partir des vraies transitions du monde pré-natal propre à la condition. Le profil de développement `consolidation_weight=0` est conservé tel qu'étudié dans #132/#153, avec les autres paramètres de sommeil de référence inchangés. Les coûts UC additionnels d'évaluation GA et de critère spatial sont égaux à 1 avant naissance, en plus du diagnostic, de l'occupation et de la jointure. Les six vies sont bornées à 50 transitions. Aucun ajustement après observation, aucun ordre moteur de laboratoire.
