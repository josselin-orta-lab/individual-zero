# A2.30-Z : verrouillage opératoire de la matrice physique, avant code et avant résultat

**15 octobre 2026, deuxième préenregistrement (amendement AVANT runner, tests ou physique Z).** Le protocole scientifique préexistant \`stage12-issue110-b-a230z-alternative-food-prereg-2026-10-15.fr.md\` avait défini les bras et exigences sans effectifs. **La présente version fige exhaustivement les effectifs et la règle d'action**, sans changer le cadre d'autorisation : uniquement laboratoire physique externe, shadow Stage6, zéro apprentissage autonome I0, zéro Oracle dans le modèle. Les autres études (P à Y) restent historiques, non réexécutées comme échantillons Z.

## Matrice factorielle : 168 mondes physiques indépendants, 244 actions prévues

Cinq layouts × deux politiques préengagées × deux niveaux de nourriture initiaux \`{35,45}\` × deux positions \`{(5,5),(7,7)}\` :
- **A_ONLY** : ressource \`berry_a\` à la position initiale, \`berry_b\` absente; **5 variantes cachées de A**, \`benign\`, \`toxin_7\`, \`toxin_30\`, \`toxin_100\`, \`gain_zero\`. Soit **5×2×2×2=40 mondes**. Leurs chemins ne consomment **jamais** A; cette branche sert de témoin de refus d'une espèce non justifiée. Le précédent W conserve les preuves d'ingestion dangereuse A.
- **B_LOCAL** : \`berry_a\` et \`berry_b\` présents physiquement et visibles à la case courante.
- **B_EAST_BLOCKED** : \`berry_a\` à la case courante, \`berry_b\` à l'est visible sur la case adjacente, **case est bloquée** (\`passable=False\`). Le protocole est limité au mouvement direct vers l'est : cela ne prouve PAS que B est globalement inaccessible via tous les chemins alternatifs.
- **B_EAST_ADJACENT** : \`berry_a\` à la case courante, \`berry_b\` sur la case est accessible.
- **B_EAST_TWO_STEPS** : \`berry_a\` à la case courante, \`berry_b\` deux cases à l'est : invisible au départ, devient visible après déplacement d'une case vers l'est.

Chacun des **quatre layouts B** utilise **quatre variantes physiquement cachées de B** : \`benign\` (\`food_gain=12, integrity_delta=0\`), \`toxin_7\` (\`food_gain=12, integrity_delta=-7\`), \`toxin_100\` (\`food_gain=12, integrity_delta=-100\`, terminal), \`gain_zero\` (\`food_gain=0, integrity_delta=0\`). Effet de A fixé à \`food_gain=10, integrity_delta=-100\` dans les layouts B; A est reconnue visuellement mais **jamais préjugée sûre ou dangereuse par la politique** : celle-ci s'abstient de cette ressource dans toutes les branches. Chaque layout B compte **4×2×2×2=32 mondes**, soit **128 mondes B**, total **168**.

**Physique :** \`WorldBody\` 32×32 dérivée de \`physical_fixture_config()\`, nourriture initiale 35/45, intégrité 100, coût des primitives \`se_deplacer=1\`, \`collecter=0.75\`, \`manger=0.5\`, \`attendre=0.5\`; décroissance \`food=0.5\` par pas, \`water=0.2\` par pas; récupération d'intégrité au repos neutralisée; \`berry_b\` exact avec les variantes ci-dessus, sans aucun autre effet de danger/obstacle que la case est bloquée du bras correspondant. Les configurations et layouts sont archivés par empreintes SHA. Les ressources B restent réelles, non simulées par l'opérateur; \`collecter(B)\` n'est possible que sur la case contenant B.

## Deux politiques déterministes fixées AVANT expérimentation

Les deux politiques sont de **simples procédures de laboratoire limitées à une décision perceptive** et non des réalisations de \`SimulatorPlanner.search\` :

1. **OBSERVED_ONLY** : si B est directement visible sur la case courante, \`collecter(B)→manger(B)\`; sinon si B est visible **à l'est** et l'est \`passable=True\`, \`se_deplacer(east)→collecter(B)→manger(B)\`; sinon **s'abstenir du préfixe alimentaire**, **zéro action**. Jamais de choix basé sur la variante cachée.
2. **SINGLE_EAST_PROBE** : même comportement pour B visible et directement accessible. Lorsque B n'est visible ni ici ni à l'est mais que l'est est passable, **effectuer exactement un déplacement de sondage \`se_deplacer(east)\`**, puis reconsidérer à partir de la perception autorisée : si B est devenue directement visible ici ou visible à l'est avec passabilité, se déplacer si requis puis \`collecter(B)→manger(B)\`; sinon **abstention**. Une B visible sur une case est **bloquée** entraîne l'abstention immédiate, pas un sondage alternatif. Sondage décidé sans savoir si B existe physiquement deux cases plus loin.

**Le préfixe est engagé uniquement à partir du \`SimulationState\` courant** et d'une mémoire de contrôles procéduraux de sondage (aucun contenu caché). Pour les commandes \`manger(B)\`, contrôler \`inventory.berry_b>0\` après collecte, puis avaler **une seule** baie. En cas de \`terminal=True\`, ne jamais poursuivre, figer la mortalité du monde et inscrire la dernière capture physique comme **reçu externe uniquement**, jamais comme expérience subjective future.

### Effectifs/étapes attendus (avant observation)

| Layout | Mondes OBSERVED_ONLY | Mondes SINGLE_EAST_PROBE | Pas attendus par bras | Total pas |
|---|---:|---:|---|---:|
| A_ONLY | 20 | 20 | 0 / 1 | 20 |
| B_LOCAL | 16 | 16 | 2 / 2 | 64 |
| B_EAST_BLOCKED | 16 | 16 | 0 / 0 | 0 |
| B_EAST_ADJACENT | 16 | 16 | 3 / 3 | 96 |
| B_EAST_TWO_STEPS | 16 | 16 | 0 / 4 | 64 |
| **Total** | **84** | **84** | | **244** |

**80 ingestions physiques de B prévues** (=32 B_LOCAL +32 B_EAST_ADJACENT +16 B_EAST_TWO_STEPS), **20 décès terminaux physiques**, **40 repas avec survie et gain alimentaire ≥5 depuis la capture avant ingestion**, **20 survivants à gain insuffisant**. **88 abstentions du préfixe alimentaire** (=40 A_ONLY +32 B_EAST_BLOCKED +16 B_EAST_TWO_STEPS sans sonde), dont 20 actions exploratoires physiquement payantes dans A_ONLY avec sondage. Les comptages binaires par groupes et variantes sont préspécifiés; si différent, ne PAS corriger les scénarios après coup : publier l'écart et marquer FAIL de conformité.

### Shadow de l'algorithme Stage 6

Uniquement pour les **80 mondes où \`manger(B)\` est sur le point d'être tenté**, lancer **une recherche réelle \`SimulatorPlanner.search\`** immédiatement après la collecte, avant l'ingestion, sur une \`FrozenTableEquipment\` **reconstituée exclusivement des transitions précédemment vécues dans ce même monde**, avec \`h_eff=3, R=1\`, objectif alimentaire prospectif \`food ≥ food_courant+5\`. Conserver commandes candidates, nombre d'arêtes racine disponibles, diagnostics et compteur de pas physiques, **sans jamais utiliser ni exécuter la commande shadow**. Aucune recherche avec mémoire vide; aucun shadow après mort. Ces 80 requêtes utilisent un témoin de mémoire first-person idéale du laboratoire, **PAS** la mémoire cognitive réelle d'I0; elles ne constituent pas un test d'action autonome ou d'UC vécu. Leurs véritables coûts UC sont **non mesurés**. Une racine inconnue ou un plan non trouvé doit être conservé.

### Scoring, témoins et limites

- Reconstruire pour chaque décision les **11 dimensions du \`SimulationState\` complet**, les ressources sur case courante et voisins, la passabilité est et les commandes autorisées. En aucun cas la configuration cachée, les baies hors champ, la valeur de \`berry_b.integrity_delta\` ni l'effet futur ne peuvent devenir des features de choix.
- Les mondes \`B_LOCAL\` sont une opportunité positive visible **mais non prouvée sûre**; \`B_EAST_BLOCKED\` un contrôle d'abstention à l'obstacle direct; \`B_EAST_ADJACENT\` une accessibilité physique vérifiable; \`B_EAST_TWO_STEPS\` un coût d'exploration et une limite d'observation à t0.
- Un changement caché de B **doit laisser inchangées les perceptions et les décisions préingestion** à contexte/bras/position/food identiques; le résultat externe peut différer.
- Résultat physique de l'objectif ne signifie **PAS** verdict \`plan_found\` du Stage6. Aucun résultat \`safe\` n'est émis par le décideur.
- Les quatre variantes cachées B comprennent une létalité : **aucune de ces politiques ne peut garantir zéro décès** pour les mondes où elle décide de s'engager. Une abstention peut sacrifier des opportunités, sans être une garantie de survie globale dans un monde plus large.
- Générer archives de tous les 168 mondes, y compris ceux avec **zéro transition**, leur capture initiale et tous les refus ; ne pas compter une deuxième version Python comme deuxième cohorte scientifique.
- Tests adversariaux requis : effet caché injecté dans une décision, déclaration de sûreté, obstacle ignoré, ressource fantôme, postmortem vécu, futur injecté dans corpus shadow, modèle entraîné sur un autre monde, commande shadow exécutée; source bloquée ou erreur de coût.
- Aucun changement au runtime I0, Stage9/DC-05, Stage6 prod, Stage12, M11 WAL ou MVP v1.3.1. **A2.30 PARTIELLE, Stage12 PARTIAL, #110 OPEN; cette étude ne valide pas la cognition autonome.**

**Ce préenregistrement verrouille 168 mondes / 244 pas AVANT le code runner Z.** Toute correction de bug au code devra être documentée, sans réviser les critères scientifiques sur la base des résultats.
