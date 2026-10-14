# Issue #110 / Option A : impossibilité structurelle du jugement `world` sur obstacle connu et variante normative à arbitrer

**14 octobre 2026, proposition non normative.** Cette note constate une contradiction entre le producteur `GA-SPATIAL-01` proposé dans la PR #155 et la génération des commandes moteur autorisées. Elle **ne modifie pas** la spécification MVP v1.3.1, les seuils du détecteur, ni les politiques du Stage6/Action Control. Aucun `world` n'a été inventé.

## Constat établi par le code et les vies

- `src/i0/modules/stage6_planning.py`, `SimulatorPlanner.candidate_commands` : une primitive `se_deplacer` est générée **uniquement si `SimulationNeighbor.passable` est vrai**. Un voisin `east` connu bloqué est donc éliminé *avant* toute recherche, quel que soit le nombre de transitions d'Equipment présentes dans la table. Test logiciel `tests/test_stage12_spatial_world_reachability.py` ; contrôle positif identique en rendant l'Est passable.
- `src/i0/modules/geographic_exploration.py`, `discover_targets` : exclusion des cellules `passable is not True` et des directions Action Control explicitement inadmissibles.
- `src/i0/modules/action_control.py`, `reflex` : sélection limitée à `capture.passable_moves`. Le filtre de protection des zones mortelles reste intact, même lorsqu'un mouvement serait autrement admissible.
- Le producteur spatial Option A actuel ne peut formuler `world` que si une cible pertinente exactement adjacente est déjà perçue **non franchissable au moment de l'engagement**, et si la commande a néanmoins été admise et réellement appliquée puis la position n'a pas bougé.
- Quatre vies × 50 pas en mondes libres/bloqués, puis quatre vies avec Equipment aligné sur le premier état de planning vécu : **zéro** commande d'objectif vers un obstacle déjà reconnu et **zéro** jugement `world`. L'expérience alignée a bien produit des plans, deux progressions spatiales et des `self` dans les mondes libres, ce qui témoigne de la fonctionnalité du chemin positif.

**Conclusion bornée :** la voie `goal-directed Stage6 → obstacle connu non passable → world` est **structurellement inaccessible**, sous les contrats de production de commandes inspectés. Ce constat ne signifie pas que toute influence extérieure ou toute attribution subjective `world` serait philosophiquement ou physiquement impossible ; il invalide seulement **ce producteur précis** comme moyen d'obtenir `world` par autonomie actuelle. La compatibilité cognitive pourrait changer uniquement après une évolution du contrat de perception/action.

## Choix d'évolution, sans implémentation avant décision

### A2 : contrainte extérieure devenue visible APRÈS engagement (recommandation conditionnelle)

Conserver la sélection de commandes sûres et les filtres de passabilité. Autoriser un jugement subjectif `world` uniquement lorsque :
1. I0 a préengagé un mouvement vers une cible de but réellement perçue et initialement **passable** ;
2. la commande est réellement admise et envoyée sans intervention du banc ;
3. une nouvelle capture **perceptive authentique** au pas suivant montre un obstacle pertinent exactement dans la direction engagée, absent de la capture antérieure, et aucun déplacement ;
4. cette nouvelle observation possède son identité de vie, son horodatage, son coût cognitif, sa référence et sa preuve de provenance propres ;
5. l'évaluation de l'indice extérieur **n'a aucun accès** au booléen `failure` du sous-critère spatial, aux catégories P-47 ou aux causes cachées du WorldBody. Elle reste un jugement faillible.

**Limite de faisabilité à tester avant toute annonce** : le moteur physique et l'ordonnancement doivent effectivement permettre une modification observable entre les deux captures, sans qu'un scénario laboratoire injecte l'attribution. Un obstacle ajouté après une capture mais avant la transition peut être physiquement pertinent ; un obstacle annoncé uniquement par un audit ne l'est pas. Le seul non-déplacement ne suffit pas à attribuer `world`.

### A3 : indices d'influence extérieure sur d'autres familles d'objectifs

Étudier une autre sous-famille de résultat dont la perception directe contient une cause extérieure spécifique (par exemple interaction corporelle avec une créature déjà vue), sans utiliser le journal Oracle ni les effets cachés. Cette voie nécessite préenregistrement d'un nouveau critère, coût UC, sémantique d'attribution et tests indépendants. Elle accroît le périmètre du MVP.

### Maintien du contrat actuel

Conserver `world=unknown` dans le runtime existant, qualifier la branche `world` de non démontrée et poursuivre les validations M-11 et d'agence `self`. C'est le comportement sûr tant qu'aucun scénario légitime ne satisfait A2/A3.

**Rejet impératif :** forcer des commandes vers des cellules connues bloquées, rendre les cellules connues artificiellement passables dans la capture d'I0, contourner les protections Stage6/Action Control, attribuer `world` à tout échec spatial, ou convertir un P-47 `nonconforming` en faute du monde.

## Réception scientifique

Un test logiciel produisant `world` après un mouvement commandé par une fixture ne compte jamais comme preuve d'autonomie. Même un `world` authentique isolé ne valide pas le détecteur de biais : garder `window=12`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75`. Les campagnes exploratoires doivent être préenregistrées **après** décision normative et **avant** toute adaptation du code ou des mondes, avec cas de contrôle négatifs et preuves de mortalité/M11.

**Décision sollicitée à l'opérateur :** arbitrer entre A2, A3 ou maintien du statu quo pour `world`. Aucun changement normatif supplémentaire n'est appliqué à ce stade ; Stage12 non réceptionné et issue #110 ouverte.
