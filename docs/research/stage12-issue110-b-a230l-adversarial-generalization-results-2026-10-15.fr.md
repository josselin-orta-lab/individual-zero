# A2.30-L : contre-exemples physiques à un Equipment déterministe général

**15 octobre 2026.** Préenregistrement **avant le code** au commit `b0177e3baf60fd479b131ceabffd453409dc9bee`. Première CI de l'instrument `82701567` techniquement verte, mais la fixture obtenait encore la physique en instanciant inutilement un `Stage4Runtime`, contrairement au protocole. Cette non-conformité de méthode a été rectifiée **avant tout verdict accepté** : la configuration est maintenant un `WorldPhysicsConfig` indépendant, sans instance cognitive, au commit `c21431f5958048fefe5ad91e3f86ca38a51ddfa4`. [GitHub Actions #38722518797](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38722518797) **SUCCESS Python 3.11 et 3.12**, résultats exactement identiques.

## Témoins physiques réellement appliqués

**Six mondes physiques indépendants, huit transitions WorldBody.apply vérifiées**, toutes exclusivement au laboratoire et **zéro nouvelle naissance / zéro pas autonome I0**. Les observations exploitées pour définir les entrées sont les seuls `SimulationState` accessibles via `SymbolicPerception`. Aucun Oracle, Banc d'évaluation ou état d'un I0 vivant n'est importé dans la fonction de prédiction.

### L1 : danger létal caché, même entrée observable

Un `se_deplacer(east)` depuis un état accessible identique (hash d'entrée exact `49ed1a304492bb47e6a33a7d64ba0cac86871cec20e8892df14943f24e6facc3`) aboutit :

- dans un monde sans danger : déplacement non létal ;
- dans un monde avec zone létale adjacente non représentée dans la capture cognitive : **transition létale**.

L'entrée `SimulationState × PrimitiveCommand` est **strictement identique** et les sorties sont différentes. Le trainer exact **rejette** le corpus contradictoire, il ne choisit pas le résultat physiquement avantageux. Le monde témoin létal reste terminal, sans restauration d'un I0.

### L2 : même fruit perçu, effets d'intégrité différents

Deux mondes collectent d'abord `berry_a` au pas 1 puis ingèrent `berry_a` au pas 2. Le profil d'effet physique caché du fruit diffère seulement pour `integrity_delta` (0 contre −7), non dans les captures accessibles avant ingestion.

| Sortie physique après ingestion | Monde témoin | Monde à effet nocif |
|---|---:|---:|
| Nourriture | **70** | **70** |
| Intégrité | **100** | **93** |
| Transition terminale | Non | Non |

Les deux entrées de prédiction ont le **même hash exact** `69a12df2c50a456dabc023427c3fb7c207bb28868bb77c61653416d20d8ad150`, et les sorties sont divergentes. Le trainer les refuse comme observations contradictoires, plutôt que fabriquer une sécurité commune à tous les contextes d'ingestion. Aucune règle de danger n'est injectée dans Stage9 ou I0.

### L3 : nourriture corporelle visible indispensable à la valeur absolue

Sur une action `attendre` au même endroit et dans le même voisinage, deux mondes diffèrent **uniquement** sur `body.food` accessible (35 contre 40) ; la nourriture suivante reste différente (35 contre 40 dans cette fixture sans décroissance). Retirer `body.food` du modèle tout en prédisant une valeur corporelle **absolue** serait incorrect, même si le delta de nourriture était identique.

## Conclusion mathématique et scientifique bornée

Pour un modèle déterministe `E(S_accessible, command) -> conséquence unique`, les expériences L1 et L2 produisent deux sorties différentes pour le **même couple d'entrée**. Un modèle exact unique ne peut donc pas représenter les deux expériences sans état latent, incertitude ou abstention. Cela ne prouve **ni** qu'un modèle probabiliste est fiable, **ni** qu'un nouveau prédicteur améliore l'alimentation; cela prouve qu'une généralisation certaine à partir des seules observations accessibles serait scientifiquement non défendable sur ce domaine.

**A2.30 PARTIELLE ; Stage12 PARTIAL ; issue #110 OPEN ; PR #187 DRAFT.** Aucun changement du simulateur de production, de Stage9/DC-05, de la politique alimentaire, de l'Oracle ni de la norme MVP v1.3.1.


## Addendum A2.30-M : insuffisance d'une seule observation bénigne

L'expérience logicielle dérivée [CI #38723084941](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38723084941), préenregistrée avant code `e0c3d6f`, vérifie que `FrozenTableEquipment` **entraîné uniquement sur l'exemple sûr** de L1 ou L2 renvoie `confidence=1.0` pour le **même input accessible** dans le monde caché divergent, et prédit à tort respectivement `terminal=False` (alors que `True`) et `integrity=100` (alors que 93). Les vérifications physiques sont les mêmes six mondes et huit pas de L, **sans nouveaux échantillons autonomes I0**. Le refus du trainer en présence de deux exemples contradictoires ne permet pas de garantir la sûreté avec un seul exemple. La valeur 1,0 est une **confiance de correspondance exacte au corpus observé**, non une probabilité scientifique calibrée de sûreté du monde.
