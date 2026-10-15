# A2.30-ZI : préenregistrement prospectif de sondes motrices propres et du piège de la clé exacte

**15 octobre 2026. Avant toute implémentation, naissance, monde ZI, commande physique ZI ou résultat ZI.**
Base : PR #200, SHA `81140ab41b6d536ab84486cbb68f6110242de0df` ; études déjà connues ZB, ZD, ZE/ZF, ZG/ZH. Ce protocole étudie une expérience *physiquement auto-acquise dans un monde de laboratoire* mais **N'EST PAS une expérience vécue par un véritable individu I0**. Aucun changement à `src/i0` ni à la spécification MVP. Aucune permission implicite de forcer des commandes chez un I0.

## Problème

ZG/ZH a montré que des exemples externes de `se_deplacer(east)` et `collecter(berry_b)`, alignés exactement aux premières perceptions de douze vrais I0, font apparaître une sous-étape Stage6 sur 8/8 racines B visibles ; ces exemples ne sont pas leur mémoire propre et ne prouvent pas une décision motrice ou une ingestion. L'étape suivante est de vérifier séparément :

1. **ZI1, acquisitions propres et causalement séquencées :** une expérience physique non ingestive choisie par une **politique de laboratoire préengagée sur la seule perception** peut-elle produire la transition de modèle absente, puis contribuer à une prédiction Stage6 au **nouvel état courant réellement obtenu** ? Il faut distinguer la transition `état_ancien×commande` désormais connue d'une action `état_nouveau×commande_nouvelle` encore inconnue. Le modèle exact n'a aucun droit de transférer l'arête ancienne à la nouvelle clé.
2. **ZI2, risques moteurs invisibles :** une politique de sondage `move east` peut être mortelle dans un monde avec `lethal_zones` caché, alors que le `SimulationState` initial et les commandes candidates sont **identiques** au monde où l'est est sûr. Le mot « non ingestif » ne vaut ni `safe` ni risque nul.
3. **ZI3, abstention perceptive :** l'absence de B et l'obstacle est visible imposent une abstention ; l'effet caché bénin/létal de B ne change **aucune** première décision et **aucune** capture avant ingestion.

Une sous-étape `partial_progress` au t0 ou un nouveau dictionnaire exact au t2 ne constitue jamais une preuve de plan alimentaire abouti, de jugement subjectif, de choix cognitif, de mémoire vécue I0, de coût UC ni de survie universelle.

## Matrice physique verrouillée : 66 mondes, 28 actions maximales attendues

**64 mondes de test détachés**, toutes combinaisons :
- profils originaux d'I0 ZB : `restored` (food=35) et `sustained` (food=24) ;
- dispositions : `B_NONE`, `B_LOCAL`, `B_EAST`, `B_EAST_BLOCKED` ;
- effet caché B : `benign=(food_gain=30,integrity_delta=0)` et `toxic_lethal=(food_gain=30,integrity_delta=-100)` ;
- risque moteur caché : `east_clear` ou `east_hidden_lethal` (lethal_zone sur la case immédiatement à l'est, non perçue) ;
- protocole de laboratoire : `ABSTAIN` ou `VISIBLE_PROBE`.

**2 mondes supplémentaires physiques de référence A**, un par profil ; reproduire la séquence prénaissance **north→east→collecter(A)→manger(A)** de quatre commandes physiquement appliquées par profil et reconstituer l'artefact `FrozenTableEquipment` A initial **au SHA de l'équipement réellement présent à la naissance** dans les 12 historiques ZB. Soit **8 actes A**. Ces mondes A sont externes, ne sont pas de nouvelles naissances et fournissent seulement le témoin prénatal déjà reçu par I0.

**64 + 2 = 66 mondes indépendants.** Les 64 mondes de test suivent exactement :
- `ABSTAIN` : aucune action physique, quelles que soient les ressources ;
- `VISIBLE_PROBE` sur `B_LOCAL` : **collecter(B)** au pas 1, ne pas manger B, puis arrêter (8 cas, 8 actes) ;
- `VISIBLE_PROBE` sur `B_EAST` : **se_deplacer(east)** au pas 1 ; si, et **seulement si**, le corps est encore vivant et B réellement visible localement au pas 2, **collecter(B)** au pas 2 puis arrêter (8 cas : quatre `east_clear` donnent 2 actes chacun, quatre `east_hidden_lethal` donnent 1 acte et mort immédiate ; soit 12 actes) ;
- `VISIBLE_PROBE` sur `B_EAST_BLOCKED` : obstacle est visible, **aucune** action ;
- `VISIBLE_PROBE` sur `B_NONE` : B absente dans la perception courante et adjacente, **aucune** action.

**Total préspécifié de la matrice test : 20 actions physiques non ingestives**, **4 décès** dus uniquement aux déplacements dans le danger caché, **16 sondes initialement choisies**, **12 séquences de sonde atteignant la survie**, **48 abstentions**, **0 ingestion B**, **0 gain alimentaire par B**. Le contrôle `B_LOCAL` avec danger caché à l'est ne traverse pas cette case et ne meurt pas. L'effet caché d'ingestion de B ne peut pas modifier la collecte non ingestive. Ces comptes sont des attentes **avant données** : publier un échec si la physique observée les dément ; ne pas réajuster les variantes.

L'environnement de chaque cas reprend `reference_birth_world(profile)` validé en ZG, en copiant sa configuration corporelle, sa météorologie/temps et ses baies A ; ajoute deux B localement ou à l'est selon le bras, un obstacle est si demandé, et une zone létale est seulement pour la variante cachée. Ressource B initiale toujours quantité 2. Rejeter toute modification de la première perception par effet caché B ou danger mortel, à layout/profil/protocole identique.

## Corpus propre (idéal de laboratoire), stade 6 et compte de recherches

Deux types de connaissance **à distinguer en chaque ligne** :
- **Témoin historique prénatal A** : 4 exemples A extérieurs par profil, validés à l'empreinte d'origine ZB ; les `64` états de test sont ensuite interrogés avant action avec ce modèle, par le **vrai** `SimulatorPlanner.search` (ou seulement `FrozenTableEquipment.predict` quand explicitement indiqué).
- **Mémoire d'un monde d'essai, idéale et propre à sa séquence** : seulement les couples `SimulationState × PrimitiveCommand → observed_next_state` de ses **propres transitions physiques antérieures et non terminales**, jamais celles du monde jumeau ou d'un autre monde ; ajoutés à la table A prénatale et interrogés au **nouvel état courant après réception effective de la conséquence**. Ceci est un `own-world ideal lab corpus`, PAS la vraie mémoire ni le budget UC d'un individu I0.

Exiger **64 recherches Stage6 à t1** (une par racine), puis **12 recherches à t2** après la première sonde survivante, puis **4 recherches à t3** après la deuxième collecte survivante, soit **80 recherches réelles en shadow**. `SimulatorPlanner.search` avec `progressive_subgoals=True`, `progressive_evaluation_prefix=True`, `progressive_revalidate_on_new_capture=True`, `max_depth=3`, `r_eff=1`, objectif `food ≥ food_initial_courant+5`. Les commandes proposées ne sont jamais exécutées par le simulateur ; seuls les préfixes de politique externe figée ci-dessus peuvent déclencher la physique.

Contrôler en particulier :
- **Avant l'action B**, le `(SimulationState, first_B_command)` n'est **pas prédit** par la table A originale ; aucune mémoire future.
- **Après l'action**, l'ancienne clé `(root_before, executed_command)` est connue dans la table propre **rétrospectivement**, mais aucune conséquence de l'action suivante au nouvel état n'est inventée. En particulier `collecter(B)` sur la case à l'est avant première collecte et `manger(B)` après collecte doivent rester inconnus.
- **Après une transition terminale**, aucune capture subjective ultérieure, aucun `EquipmentCorpusExample` terminal utilisé comme mémoire d'un corps vivant, aucune recherche t2, aucun acte t2.
- Une étude physique par Python 3.11 et 3.12 est une **réplication numérique des mêmes recettes déterministes**, pas 128 nouveaux mondes statistiques.

## Historique I0 immuable et comparaisons

Lire les résumés originaux ZB `a230zb-py3.11` et `a230zb-py3.12`, [run #38767643472](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38767643472), avec leurs SHA-256 **différents mais scellés** : 3.11 `ea7ed0d4fa92f5b47e71f9e9ba98dc2bf5c49aa39a3de40068a00b284314c85b`, 3.12 `ecd2700f119d1e8f7ee2c07c89c5e7acaa5c0c66bc4abd016412b1ee89872362`. Réutiliser seulement les **douze racines initiales**, modèles A, identités et compte historique de 384 pas pour comparaisons; ne jamais reprendre les vies ni lire les effets cachés pour décider d'une action. Les `B_LOCAL`, `B_EAST`, `B_NONE` testés doivent reproduire **exactement**, aux positions, corps et perceptions initiales, les naissances historiques correspondantes (pour leurs deux variantes cachées). `B_EAST_BLOCKED` est un nouveau témoin visible, pas un ancien individu.

## Contrôles négatifs exigés

Injection `hidden_lethal_zone` dans une décision perceptive ; `berry_b_safe` fabriqué ; ressource B fantôme ; obstacle direct ignoré ; exemple propre provenant de l'autre bras ou du futur ; effet après ingestion B inventé ; recherche Stage6 exécutée après terminal ; consommation physique B non prévue ; déclaration de UC vécues ; décès comme nouvelle perception ; clé exacte réutilisée avec corps/modèle différent ; collision contradictoire acceptée. Tous doivent provoquer FAIL détectable. Si le même état avant mouvement vers l'est donne survie/mort selon danger caché, le moteur d'expérience doit rejeter toute `guarantee_safe` sur cette observation.

## Décisions finales attendues

**ZI PASS technique** seulement si les 66 mondes sont physiquement produits, 28 commandes sont réellement appliquées selon les règles ci-dessus, quatre décès cachés sont constatés et audités, 80 recherches shadow exécutées sans fuite, les sources d'identité/mémoire sont cohérentes et les négatifs passent sous Python 3.11/3.12. **ZI1** se décide séparément sur la disponibilité des clés exactes à t1/t2/t3; **ZI2** se décide sur les contrastes létaux appariés; **ZI3** sur les abstentions et parités perceptives. Pas de « progrès scientifique » artificiel si le vrai Stage6 ne peut pas exploiter la nouvelle clé au nouvel état.

**Revue et fusion :** PR scientifique empilée en brouillon, sans changement au runtime I0, au contrat Stage9/DC-05, au journal mortel M11, à l'Oracle ou au MVP v1.3.1. **A2.30 PARTIELLE, Stage12 PARTIAL, #110 OPEN, aucun déploiement cognitif.** Une exploration autonome réellement vécue nécessiterait une décision opérateur distincte sur l'admissibilité, la responsabilité et le risque des sondes.
