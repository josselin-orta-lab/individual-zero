# EXP #133-CAPACITY : budget physique, passes et taille des lots (préenregistrement)

Date : 13 octobre 2026. Ce protocole est écrit **avant** l'ajout du runner de comparaison et avant l'exécution expérimentale. Source du diagnostic préexistant : PR #139, `ed6332f82fbb552c9f01c3e3f41eb54e06ca536e` (CI Stage12+rapide validée), puis correctif de lecture facturée `2a853751c2b1f2631e443f27a5f5728dc0e98b0c` dont l'évaluation sur CI est à vérifier. Le comportement des anciens résultats reste historique, non réécrit.

## Observation motivant la campagne

Sur le monde de référence, à `w_C=0` et 240 pas physiques, 119 épisodes ferment. Les deux configurations 1 et 3 passes/par pas avaient respectivement 17 et 47 références consolidées, 102 et 72 en attente, mais seulement **41 pas de sommeil effectivement consacrés à du travail P-42**, malgré 96 commandes `dormir`. À 3 passes maximum, 6 passes par lot, 3 épisodes maximum par lot, le plafond arithmétique pour les mêmes 41 créneaux est `floor(41*3/6)*3=60` épisodes, avant tout coût de scan. Aucun index d'épisodes non traités ne peut à lui seul abolir cette borne. Les rescans coûtent pourtant 1032 UC / 1967 UC dans le bras 3 passes. Le maximum observé par période est 100 UC malgré une autorisation de 600 UC, ce qui rend la fragmentation temporelle pertinente.

## Question falsifiable

À veille, sommeil, monde, paramètres vitaux, pression de sommeil et budgets inchangés, la capacité est-elle surtout bridée par la borne de passes, par la taille des lots ou par les UC de scan et de traitement ? On ne suppose pas que davantage de passes donne de meilleurs résultats.

## Bras expérimentaux FIXÉS

| Identifiant | Passes maximales / pas admis en sommeil | Épisodes maximum / lot | Rôle |
| --- | ---: | ---: | --- |
| P3-B3 | 3 | 3 | Contrôle du nouveau dispositif |
| P6-B3 | 6 | 3 | Relâche uniquement le plafond de passes |
| P3-B6 | 3 | 6 | Relâche uniquement la taille des lots |
| P6-B6 | 6 | 6 | Interaction des deux capacités |

Le `w_C=0` de développement reste **obligatoire** pour tous. `p_cons_min=0` identique au dispositif expérimental existant, scan incrémental P-42 strictement facturé, `episode_scan=1` UC/projection, `step_slot_uc=100`, `period_capacity_uc=600` et tarifs sémantiques inchangés. La même politique de sommeil (version commune), monde `reference_untrained`, eau initiale 20, équipement pré-naissance, trajectoire déterministe, limite de 240 transitions réelles et sélecteur existant sont employés. Seuls les deux facteurs déclarés sont modifiés. Ne pas changer la création des épisodes ou la politique de rang pour faciliter un résultat.

Quatre individus mortels **nés séparément par interpréteur** Python 3.11 puis 3.12, mêmes conditions de départ, 240 pas maximum par vie ; la répétition cross-Python est un test de reproductibilité logicielle, pas un échantillonnage statistique indépendant. Une mort réelle termine sa vie ; un crash ou une erreur de runtime invalide les données, même si la chaîne de hachage demeure lisible.

## Mesures et règles de décision définies avant exécution

Exiger pour chaque bras : manifest/version SHA, WAL et export canonique, vérification complète de la chaîne, transitions physiques, sommeil réel, épisodes fermés et éligibles, références gelées, six checkpoints ordonnés / publication de h, 0 duplication, 0 publication partielle, UC réellement débitées par pas et par période, refus explicites, coût des scans (épisodes examinés, rescans) et distribution d'âge du backlog. Lire les pentes par fenêtres [1,80], [81,160], [161,240], non seulement le total final.

* **Intégrité** : toute UC supérieure à 100 par pas ou 600 par période, toute vérité Oracle consultée par I0, mort ressuscitée, h non atomique, épisode perdu ou non reproductibilité non expliquée => échec technique du bras.
* **Effet de capacité** : un bras supérieur au contrôle est descriptivement amélioré uniquement si les références h progressent et les éveils/comportements vitaux ne régressent pas dans le même monde; sinon hypothèse non supportée.
* **Stabilité locale** : backlog net sur les 80 derniers pas inférieur ou égal à zéro; un déficit persistant => non soutenable au rythme observé, indépendamment des meilleurs nombres absolus.
* **Économie UC** : reporter coût total, coût par épisode consolidé, maximum par slot, par période et incidents de défaillance. Le changement de facteur n'autorise aucune UC supplémentaire; si la taille 6 est trop chère pour le slot, constater le refus au lieu de gonfler les plafonds.
* **Portée scientifique** : mondes held-out, vieillissement >240 pas, besoin urgent concurrent, qualité cognitive des souvenirs et reprise atomique M11 restent hors de cette campagne. Ne pas déclarer de GO général.

Le comportement par défaut en production reste 1 passe et sélection actuelle. Aucun changement de la norme MVP v1.3.1, aucun changement de `w_C`, pas d'activation généralisée ni fusion sur la base de tests isolés. Si les quatre bras restent non soutenables, investiguer un index de candidats avec maintenance facturée **et** les plafonds comportementaux normatifs, sans contournement implicite.
