# A2.30-L : préenregistrement des contre-exemples physiques à une généralisation de Stage6

**15 octobre 2026, préenregistrement avant tout code et résultat L.** Les résultats A2.30-J/K sont déjà connus : couverture initiale améliorée seulement localement, 46 exemples physiques supplémentaires et aucune divergence moteur ou alimentaire sur huit paires appariées. A2.30-I conserve le diagnostic `no_predictable_first_step`, sans extrapolation. Issue #110 OPEN, Stage12 PARTIAL.

## Question et hypothèses

Si l'on remplace la table exacte par une projection insuffisante des états accessibles, pourrait-on attribuer à une commande des conséquences sûres qu'elle n'a pas ?

- **L1, aliasing d'une cause cachée :** deux mondes physiquement distincts ont le **même `SimulationState` local accessible** et la même commande, mais des conséquences différentes pour un danger invisible. Un modèle déterministe sans abstention serait incapable de décrire correctement les deux; le trainer exact doit rejeter une clé contradictoire plutôt que choisir une conséquence.
- **L2, toxicité non observable par type de commande :** deux mondes indépendants possèdent un fruit de même espèce perceptible et les mêmes états avant ingestion, mais le profil d'effet physique du fruit diffère en un paramètre caché (intégrité). L'absence d'observation pertinente doit empêcher toute attribution universelle de sûreté.
- **L3, facteur corporel visible :** une variation contrôlée de `body.food` donne une clé d'entrée distincte et une valeur corporelle suivante distincte pour une même commande. Effacer ce facteur de la représentation serait incorrect pour les prédictions en valeur absolue, même si certains deltas restent voisins.

## Fixtures prénatales, courtes et déterministes

Utiliser seulement des `WorldBody` **neufs, indépendants et non associés à une naissance I0**, avec `EquipmentCorpusRecorder.record_transition` (monde 32×32, même coordonnées t, captures par `SymbolicPerception`). Aucune trajectoire cible, journal cognitif, Oracle, rétroaction ou commande imposée à un I0 vivant. Chaque expérience crée de nouveaux mondes et applique une transition physique réelle par commande annoncée :

1. **Déplacement vers l'est** : monde témoin sans zone mortelle vs monde expérimental avec zone létale **cachée à la perception** sur la case adjacente est (depuis la position initiale). Capturer avant mouvement ; états accessibles et commande identiques, résultat de `WorldBody.apply` différent ou terminal. Le décès d'un monde de test est une transition terminale, pas une vie réanimée.
2. **Ingestion de `berry_a`** : deux mondes avec une ressource initialement sur la case actuelle; collecte au pas 1 puis `manger berry_a` au pas 2. Seule la conséquence cachée de `berry_a.integrity_delta` diffère entre mondes (0 vs −7). Conditions corporelles et états accessibles avant ingestion doivent être identiques; l'intégrité suivante doit diverger alors que la ressource est la même espèce perçue.
3. **Attente et faim visible** : deux configurations initiales identiques sauf `initial_body.food` (35 vs 40), commande `attendre` au pas 1. Les deux états d'entrée et sorties corporelles doivent différer, démontrant que l'ignorance de la valeur absolue de nourriture n'autorise pas une prédiction absolue correcte.

Pour les paires 1 et 2, assembler un corpus comportant **les deux exemples incompatibles** pour le même couple accessible état/commande et exiger que `train_exact_transition_table` refuse `conflicting outcomes`. Les tests doivent rester strictement des preuves de laboratoire, sans déploiement du modèle.

## Seuils et suites

**FAIL** si les fixtures cachées ne produisent pas le même état accessible, si les conséquences supposées différer ne diffèrent pas, si le trainer accepte une prédiction déterministe unique contradictoire ou si l'on importe/initialise un I0, Oracle ou Bench pour fabriquer la connaissance. Rapporter le nombre réel de transitions physiques de laboratoire, les empreintes vérifiables, et distinguer ces transitions des pas autonomes antérieurs (elles ne comptent **pas** comme de nouvelles vies I0).

Un résultat PASS démontrerait **la nécessité d'une politique d'abstention** en cas d'aliasing de causes non perçues, pas la fiabilité d'un futur modèle probabiliste, ni une capacité de planification alimentaire supplémentaire. Une modification normative de v1.3.1 ou un nouveau modèle cognitif requiert une décision opérateur distincte. **A2.30 PARTIELLE, issue #110 OPEN, PR #187 DRAFT**.
