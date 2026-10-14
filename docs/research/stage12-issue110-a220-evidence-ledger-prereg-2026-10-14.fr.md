# A2.20 : mémoire probante de l'attribution d'agence et doute non destructif

**Préenregistrement du 14 octobre 2026, avant code A2.20.** Base `main dd09544d9488be2f4d4ffecef4a6cc0badfb9f7d`. Stage12 PARTIAL, issue #110 OPEN, MVP v1.3.1 inchangé. A2.19 prouve que 8/16 doutes sur des causes passées affectent des jugements `self` initialement corrects. Le coût des doutes est une observation, non une raison de supprimer les cas difficiles.

## Hypothèse

Un registre **extérieur à I0**, typé et chaîné, peut préserver les jugements originaux et suivre une incertitude ultérieure sans jamais prétendre reconstruire la cause historique. Les indicateurs probants sont `initial_self`, `unknown_after_passive_displacement`, `initial_self_unchanged`. Ils ne sont **pas** des probabilités calibrées ou des niveaux numériques de confiance. La mémoire doit maintenir l'historique des causes indiscernables.

## Matrice fixée

8 seeds 111–118 × 2 causes du premier mouvement (`normal` véritable déplacement ou `confounded` échec de commande puis relocalisation extérieure) × 4 suites :
1. `stay_stay`: deux commandes `attendre` sans déplacement.
2. `passive_stay`: après le premier `attendre`, relocalisation externe visible ; ensuite attente immobile.
3. `stay_passive`: premier `attendre` immobile, relocalisation externe après le second.
4. `passive_passive`: deux déplacements visibles après les deux attentes.

**64 mondes physiques indépendants, 192 transitions réelles `WorldBody.apply`, 32 confusions initiales, 48 relocalisations passives après `attendre`**. Seules perceptions réelles locales, commande efférente `attendre`, jugement initial authentique et références de captures sont accessibles au candidat. Les effets, interventions, causes et étiquettes ne sont jamais transmis au registre candidat. Comparer les captures complètes et l'état de confiance symbolique entre chaque paire normal/confondu à t1/t2/t3/t4. Les deux Python répliquent les mêmes 8 seeds, pas seize indépendantes.

## Critères préalables

- T1 : 64/64 mondes et 192/192 `WorldBody.apply`; 32 interventions de relocalisation initiale, 48 passives ; `self` initial 64/64, strictement identique sur toutes les captures appariées normal/confondu.
- T2 : `stay_stay` 16/16 sans révision ; `passive_stay` et `stay_passive` 32/32 avec **une** révision `self -> unknown` ; `passive_passive` 16/16 avec **une** révision et une preuve de renforcement *sans nouvel événement de révision*. Total **48 jugements historiques reconsidérés**, dont **24 historiques initialement corrects** et **24 historiquement faux**. Aucun retour de `unknown` à `self` par attente non informative.
- T3 : registre append-only lié par SHA, reçu original conservé, trace des observations sans effacement, preuves répétées enregistrées séparément ; validation indépendante de la chaîne au rejeu ; refus de double source, doublon de révision, réemploi de ref, temps non monotone, falsification d'un ancien jugement, source sans origine et preuve physiologique/cause externe.
- T4 : les deux branches appariées exposent **strictement les mêmes captures t1..t4** et les mêmes statuts épistémiques malgré des causes physiques initiales différentes. L'audit extérieur seul classe vrai/faux ; toute erreur de différence de statuts est FAIL.
- T5 : script/labo/workflow uniquement ; aucune nouvelle décision de production I0, aucun nouveau champ d'agence distal, aucun UC, WAL/mortal, Stage9/DC-05, Oracle, GA-06, Equipment ni seuil 2+2/12 modifié ; zéro vie autonome.
- T6 : reproduire sous Python 3.11/3.12 ; résultats négatifs conservés. Ne pas réclamer de réception opérateur à partir de cette matrice.

## Décision conditionnelle

Un PASS démontrerait **la faisabilité d'une mémoire probante de doute au laboratoire**, pas la révision subjective d'I0 en vie réelle, ni une inférence causale. Les contrats propriétaires/UC/atomicité WAL et la séparation normative de l'agence d'action proximale et de la responsabilité alimentaire distale restent à arbitrer **avant** toute intégration cognitive. Le détecteur #110 conserve ses critères, et l'issue demeure ouverte.
