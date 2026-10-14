# Stage12 / #110 : protocole A2.14, invariance translationnelle et abstention face aux conséquences contradictoires

**Préenregistré le 14 octobre 2026 AVANT tout code expérimental A2.14 et tout résultat.** Base immuable `main cac44c54c551f6d874bc889deee705cfa51790d6`. Norme `docs/architecture/reference/en/mvp-specification-v1.3.1.md` inchangée, Stage12 **PARTIAL**, issue #110 OPEN.

## Motivation et hypothèses

A2.12 mesure 1 178 clés de prédiction différentes refusées, 610 sans exemple de même commande et 568 à commande connue mais état exact différent. A2.13 rejette les projections supprimant `body`, `inventory`, `adjacent` et `is_night` (8 collisions contradictoires induites chacune). Supprimer `x,y` était INCONCLUSIVE, pas sûr. A2.13 montre aussi 16 paires ayant le **même état accessible complet** et des conséquences toxiques/dangereuses opposées : l'étiologie physique est indécidable depuis ce seul état.

- **H_trans** : une représentation relative des positions (corps, inventaire, voisinage cardinal, obstacles, eau, ressources, créature et jour/nuit intégralement conservés) permet de transposer les conséquences observées d'une scène vers une scène physiquement translatée, sur des cas simples, sans imputer une cause nouvelle.
- **H_single** : un seul exemple propre donne des prédictions relationnelles **erronées** dans un monde occultant une toxicité ou danger extérieur. Toute couverture accrue doit donc être auditée par ses faux positifs, pas assimilée à connaissance.
- **H_conflict** : lorsqu'au moins **deux conséquences physiques incompatibles** ont été véritablement observées en entraînement pour la même entrée relationnelle, un modèle laboratoire `ConflictAbstainingLookup` peut refuser la prédiction plutôt que choisir arbitrairement une version. Il **ne peut pas** détecter un danger jamais observé : aucune prétention de sécurité universelle.
- **H_retention** : supprimer d'autres champs observables ne fait pas partie de l'intervention. `body`, `inventory`, `adjacent`, `is_night`, `current_resources` et les commandes restent strictement retenus, de même que les coordonnées **relatives** des voisins et l'état local après transition. Seuls `x,y` absolus sont remplacés par une représentation relative ; les positions externes ne sont pas rendues accessibles comme vérités cachées.

## Expérience prénatale externe, séparée d'I0

**8 seeds indépendantes 61..68** produisent des coordonnées intérieures, niveaux corporels et eaux variables par famille, depuis un PRNG local à chaque famille et seed. Pour chaque famille, comparer le monde d'entraînement physique `source` et un monde de test physique `heldout` à des coordonnées translatées, jamais réutilisé pour l'entraînement. Pour les deux familles à cause cachée, enregistrer **un troisième monde prénatal indépendant** de nature opposée avec des résultats corporels réellement vécus dans le moteur physique, mais sans lire les étiquettes Oracle pour construire les prédictions. Total **10 familles ×8 seeds =80 paires train/test** (160 mondes) + **16 mondes d'entraînement contradictoires** supplémentaires = **176 instances physiques externes**, aucune vie I0 et aucun rechargement d'une vie mortelle.

| Famille | Intervention physique et attentes fixées avant exécution |
| --- | --- |
| `translated_move_free` | Déplacement libre est dans deux environnements identiques à translation près, résultat relatif compatible |
| `translated_move_blocked` | Déplacement est bloqué par obstacle cardinal observé dans chaque monde, résultat relatif compatible |
| `translated_collect` | Vraie collecte `berry_a` depuis la cellule courante, deux positions translatées, résultat relatif compatible |
| `translated_eat` | Vraie collecte puis ingestion `berry_a` avant et après translation, bénéfice corporel compatible |
| `hidden_toxic` | Entraînement propre et test toxique **perceptuellement identique** après collecte, avec dommage différent |
| `hidden_hazard` | Entraînement propre, danger externe invisible activé seulement avant le test, entrée perceptible identique mais dommage différent |
| `visible_obstacle` | Entraînement déplacement libre, test bloqué avec `adjacent.passable` différent, abstention |
| `body_saturation` | Ingestion normale vs corps à nourriture proche de 100 (même géométrie et inventaire), abstention si corps différent |
| `inventory_mismatch` | Entraînement avec ingestion possible, test sans nourriture inventoriée après une collecte physique infructueuse, abstention |
| `night_creature` | Entraînement en journée et test la nuit, créature voisine; `is_night` différent, abstention |

Tous les exemples proviennent de `WorldBody.apply` appliqué, avec capture `SymbolicPerception`, `SimulationState` avant et après, et effet physique réel. Les causes cachées n'entrent ni dans la clé de prédiction ni dans ses entrées : elles restent aux fichiers de diagnostic du laboratoire. Le lookup naïf n'est PAS un candidat déployable, mais un contrôle révélant explicitement les erreurs de généralisation. Le lookup avec conflit ne reçoit jamais les futurs résultats des mondes tenus à l'écart.

## Prédictions et critères prospectifs stricts

1. **T1 / Provenance** : 80 paires de mondes physiques avec **160 instances sources/heldout séparées**, plus 16 entraîneurs contradictoires indépendants. Toutes les transitions d'ingestion sont précédées d'une véritable collecte; les seules prédictions concernent des transitions déjà appliquées à un monde d'entraînement. Conserver les empreintes SHA-256 de chaque entrée/commande et conséquence. Aucun accès `ground_truth` dans le modèle.
2. **T2 / Translation** : bras `ExactTransitionTable` de référence ne peut pas couvrir les entrées à coordonnées absolues translatées si aucune entrée exacte n'est vue ; candidat relationnel naïf doit correspondre aux **32/32** transitions compatibles (4 familles ×8 seeds) en tenant compte de la position relative, du corps, de l'inventaire et de l'état local après action.
3. **T3 / Risque** : avec un seul exemple bénin, le candidat relationnel naïf doit émettre des prédictions mais se tromper sur le résultat physique dans **16/16** cas adversariaux cachés. Ces erreurs constituent des contre-exemples, PAS une amélioration.
4. **T4 / Abstention** : après incorporation **avant** le test d'une seconde expérience physique contradictoire indépendante pour la même entrée relationnelle, le lookup conservateur doit s'abstenir dans **16/16** cas cachés ; il doit également s'abstenir sur **32/32** contrôles à entrées visibles différentes (quatre familles). Refuser une clé jamais entraînée et ne pas imputer de risque alimentaire connu depuis la vérité externe.
5. **T5 / Transfert effectif** : si les 32 exemples de translation fonctionnent et si les 16 cas cachés exigent un corpus contradictoire pour être identifiés, verdict **PASS borné de l'instrument externe** mais **NO-GO déploiement cognitif** : les risques non encore rencontrés restent indétectables. Toute interpolation d'effet nocif non observé, de variable corporelle ou d'inventaire est rejetée.
6. **C1/C2** : les perceptions, prédictions, différences physiques et labels de l'évaluateur ne prouvent pas l'attribution subjective d'agence ; celle-ci n'est PAS entraînée ou évaluée ici.
7. **C3/C4/C5/C6** : aucune diversité comportementale, repas autonome, P-48 ou stabilité long horizon ne peut être validée par des transitions de laboratoire préprogrammées. Ces critères restent INCONCLUSIVE dans A2.14.
8. **C7** : répéter sous Python 3.11 ET 3.12, comparer les agrégats déterministes et conserver l'intégralité des 80 enregistrements par version. Les seeds variationnelles ne sont pas 8 vies cognitives. Exécuter la régression d'intégration #110 en parallèle.
9. **C8** : aucun changement au `FrozenTableEquipment` de production, au simulateur, `ActionControl`, `Stage9/DC-05`, `UC`, `WorldBody`, à l'Oracle, au journal causal, à la mortalité, ni à la spécification v1.3.1. Le delta DC-05 v1.3.2 reste **PROPOSITION NON NORMATIVE**.
10. **Cas non conformes** : si un résultat prospectif échoue, publier la différence, **ne pas adapter les seeds, seuils ou familles après observation**, et décider quelle cause pourrait l'expliquer; les changements de correctif purement technique doivent rester traçables. Le plan cognitif ne sera pas fusionné tant qu'une preuve générale de contrôle de l'incertitude n'existe pas.

**Stage12 global PARTIAL, issue #110 ouverte, validation opérateur distincte.** A2.14 ne sera pas déclarée réussite subjective parce que le simulateur externe produit davantage de prédictions.
