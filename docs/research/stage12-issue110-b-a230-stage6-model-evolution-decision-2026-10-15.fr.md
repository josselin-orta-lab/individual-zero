# Proposition A2.30 : prochaine évolution du modèle de transitions de Stage6 (aucune décision normative prise)

**Rapport de décision, non un amendement à la spécification.** Références : A2.30-G/H (121/121 recherches initialement sans première arête prédictible), A2.30-I (observabilité passivement améliorée et comportement inchangé), A2.30-J/K (46 nouvelles transitions prénatales par traitement ; parfois plus de premières arêtes connues, mais **0 repas supplémentaires** et **0 commandes différentes** dans 8 comparaisons).

## Problème démontré

`FrozenTableEquipment` indexe le `SimulationState` entier et la commande exacte. Une évolution naturelle de la nourriture, du voisinage ou de la position change la clé. Les états réellement rencontrés par I0 après son premier déplacement sont donc presque toujours inconnus, même lorsque la commande `se_deplacer` ou `manger` existe quelque part dans le corpus. Accroître aveuglément la profondeur de Stage6 ou le corpus de quelques exemples ne peut pas constituer une solution robuste.

## Choix à préparer, sans les appliquer avant preuve

**Option 1 : conserver le modèle exact et accepter sa limite.** Avantage : abstention fiable, préservation de la frontière Stage9/DC-05 et architecture v1.3.1. Inconvénient : Stage6 ne pourra souvent pas construire de trajectoire alimentaire complète dans des états corporels dynamiques, même en l'absence de défaut BFS.

**Option 2 : rechercher une représentation factorisée et calibrée des conséquences**, seulement après expériences physiques adversariales. Une transition pourrait dépendre de préconditions locales, position/obstacle, inventaire, état corporel, espèce, santé, contexte temporel, danger connu/inconnu. Une règle ne serait autorisée qu'avec preuves empiriques suffisantes, domaine de validité et provenance des observations. En cas de désaccord entre expériences, d'effet différé ou de sécurité non attestée, renvoyer `unavailable`, sans prédiction certaine. L'état accessible reste distinct de la vérité externe de l'Oracle. Les effets corporels continus ne peuvent être « ignorés » pour compresser le modèle.

**Option 3 : apprentissage exact à partir des transitions réellement vécues**, sans généralisation initiale. Cela pourrait faciliter les états revisités, mais le changement continu de `body.food` rend peu probable un gain massif sans nouvelle représentation. Les journaux techniques ne doivent pas devenir une mémoire cognitive omnisciente ; les données doivent passer par les projections vécues autorisées.

## Protocole avant décision

1. Appariement de mondes physiques indépendants où une commande identique est exécutée à partir d'états accessibles différant dans un seul facteur préengagé (nourriture, inventaire, voisinage, moment). Mesurer les deltas d'état corporels et les conséquences différées ; rapporter les variables causales contrôlées et non contrôlées.
2. Contrôles négatifs : ressources `berry_a`/`berry_b` à effets nocifs différents, contexte dangereux non perçu et événements exogènes. Une égalité d'input accessible avec sorties physiquement différentes doit conduire à l'abstention, pas à un label fictivement sûr.
3. Comparer modèle exact témoin à prédicteur expérimental de laboratoire, **en dehors du runtime I0**, sur données indépendantes gardées hors entraînement et contre-exemples. Quantifier les faux positifs de sécurité, omissions, précision corporelle, objectifs atteignables et incertitude ; aucune connaissance du banc n'est fournie à I0.
4. Si et seulement si une utilité et une sûreté mesurées sont démontrées, proposer un amendement motivé du MVP v1.3.1, incluant version, propriété du modèle, coûts UC, provenance et contrats de compatibilité. **Validation opérateur requise avant toute modification normative ou déploiement cognitif.**

## Situation du projet

Le verrou **diagnostique** est localisé : sans première transition connue, le planificateur ne peut pas construire une trajectoire non vide ; `incomplete_model` est justifié comme incertitude. Le verrou **comportemental** n'est pas levé : la politique reste limitée par la connaissance exacte. **A2.30 PARTIELLE ; Stage12 PARTIAL ; issue #110 ouverte ; aucune modification à la norme.**

## Addendum : résultat A2.30-L (sans révision normative)

La [CI A2.30-L #38722518797](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38722518797) démontre deux collisions physiques exactes : un même couple `SimulationState × se_deplacer(east)` peut donner une transition non létale ou létale à cause d'une zone cachée; le même couple `SimulationState × manger(berry_a)` peut donner une intégrité 100 ou 93 à cause d'un effet nocif non observé. `train_exact_transition_table` rejette correctement les observations contradictoires. Le futur prédicteur ne peut donc pas être un simple généralisateur déterministe sûr; il doit disposer d'une abstention/ambiguïté explicite pour les causes non identifiables. Aucune expérience ne prouve actuellement la sûreté ni l'utilité d'une version probabiliste. La décision opérateur reste requise avant une modification du MVP.
