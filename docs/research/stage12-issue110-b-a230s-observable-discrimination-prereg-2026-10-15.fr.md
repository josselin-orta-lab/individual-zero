# A2.30-S : préenregistrement, acquisition d'informations accessibles et planification alimentaire fantôme

Date : 15 octobre 2026. Base scientifique : A2.30-P/Q/R, PR #189, résultats P/Q/R réussis mais **A2.30 PARTIELLE**. Le présent protocole est enregistré avant toute nouvelle expérience S.

## Question
Quelles observations accessibles à I0 permettent réellement de distinguer une ressource alimentaire utilisable d'un danger caché, et dans quelles limites Stage 6 pourrait-il exploiter ces observations sans accès à l'Oracle ?

## Hypothèses falsifiables
- S1 : lorsque deux mondes cachés produisent exactement la même histoire perceptible avant l'action, aucun classificateur déterministe utilisant uniquement cette histoire ne peut les distinguer correctement tous les deux. Établir l'identité exacte des observations, et non une simple ressemblance.
- S2 : après une observation corporelle autorisée et informative, certaines classes de conséquences auparavant indiscernables deviennent séparables. Ne jamais utiliser une observation postérieure pour prédire rétrospectivement l'action qui l'a causée.
- S3 : si la seule observation discriminante nécessite une ingestion dangereuse, son acquisition ne peut être présumée admissible. Consigner le coût et les éventuelles terminalités physiques de chaque intervention.
- S4 : un plan alimentaire shadow fondé sur des effets observés peut améliorer la *description des alternatives* sans prouver qu'une trajectoire est sûre ou que Stage 6 trouverait réellement un plan.

## Design expérimental
1. Reprendre des mondes physiques indépendants avec paires cachées benign/toxique et observations initiales strictement identiques. Geler une suite de commandes commune *avant* les résultats, sans sélectionner une commande selon la configuration latente.
2. Définir deux moments de prédiction : **t0**, avant toute intervention, et **t1**, après une observation autorisée commune, si l'individu est encore vivant. Aucun score t1 n'est attribué à une vie terminale à t0.
3. Comparer les clés perceptibles complètes et les histoires d'observations accessibles, puis les conséquences physiques vérifiées hors I0. Signaler séparément la discrimination possible, impossible et indéterminée.
4. Pour chaque préfixe, construire un audit **shadow seulement** des préconditions alimentaires, horizon et effets modélisables. Ne pas modifier le vrai planificateur, ne pas injecter les variantes cachées, ne pas envoyer d'action à I0.
5. Contrôles négatifs : permutation des identifiants de variantes cachées, suppression d'une observation, duplication train/test, observation future dans les features, et cas terminal. Chaque fuite doit être détectée ou explicitement refusée.
6. Rejouer les mêmes protocoles sous Python 3.11/3.12, avec graines et fichiers de sortie figés, et une campagne intégrée de 600 pas **uniquement si** une hypothèse discriminante nécessite cette durée.

## Critères de décision
S1 n'est soutenue que si identité des histoires et divergence des résultats sont attestées. S2 exige une observation disponible *avant* le choix étudié et une séparation mesurée sur des mondes tenus à l'écart. S3 impose de documenter mortalité et coûts, pas de les optimiser a posteriori. S4 ne doit jamais être renommée « plan réussi ».

**Statut avant exécution : protocole seulement, résultats S inconnus.** A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN, PR #189 DRAFT. Aucune révision du MVP v1.3.1 ni modification cognitive autorisée.
