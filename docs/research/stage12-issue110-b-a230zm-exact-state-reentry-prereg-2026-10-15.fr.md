# A2.30-ZM : préenregistrement prospectif de la réutilisation d'une transition motrice après retour spatial

**15 octobre 2026, AVANT tout code ZM, toute action physique ZM, tout test ZM et tout résultat ZM.** Branche distincte empilée sur [PR #206](https://github.com/josselin-orta-lab/individual-zero/pull/206), SHA de base `016c5f8a3384d877339367337eead021f9029c7e`. Les résultats ZK/ZL sont **connus** : 66 mondes, 28 pas appliqués, quatre décès physiques moteurs cachés, 80 recherches Stage6, 16 anciennes arêtes connues seulement rétrospectivement et 16 nouvelles racines toujours inconnues. L'étude ZM interroge une **condition suffisante et testable de réutilisation d'une clé complète après boucle motrice**, et ne répète PAS l'expérience ZK.

## Question et hypothèses pré-enregistrées

**ZM1, exactitude complète et non localisation seule** : après une boucle **east → south → west → north** ramenant le corps aux mêmes coordonnées, une transition motrice observée à t1 n'est disponible pour une prédiction exacte au retour t5 que si **TOUTES** les valeurs autorisées du `SimulationState` correspondent. Le retour aux mêmes (x,y) ne suffit pas : énergie, nourriture, eau et drapeau jour/nuit sont des dimensions perceptibles du corps et de son contexte.

**ZM2, contrôle positif discriminant** : si et seulement si les coûts de mouvement et de métabolisme sont nuls et que la nuit ne commence pas entre t1 et t5, l'état t5 est supposé **rigoureusement égal** à t1. Alors `FrozenTableEquipment.predict(state_t5, move_east)` doit reconnaître la transition acquise à t1, et le véritable `SimulatorPlanner.search` doit pouvoir former un plan d'UN SEUL pas vers l'est. Une vérification physique prospective de ce pas à t5 doit correspondre exactement à l'effet appris à t1. Toute divergence est un **FAIL**, pas une erreur absorbée par une tolérance.

**ZM3, témoins négatifs** : toute énergie de marche non nulle, toute faim/eau décroissante ou un basculement visible jour/nuit rend t5 différent de t1 et doit empêcher **la réutilisation exacte de la première arête t1**, même si les coordonnées et les ressources locales sont identiques. Cela **ne prouve pas** qu'un algorithme factorisé ne pourrait jamais généraliser, ni qu'un mouvement serait physiquement sûr dans un autre monde.

## Physique détachée et matrice définitivement verrouillée AVANT le code

**64 mondes de test physiquement distincts** (aucune naissance I0), combinaison factorielle `2×2×2×2×2×2` :

- Positions initiales : `(5,5)` ou `(7,7)`, toutes dans le monde 32×32.
- Ressource visible à la case initiale : `none` ou `berry_b` (quantité 2), **aucune collecte ni ingestion**. Cette variable contrôle qu'une ressource présente demeure identique au retour.
- Coût énergétique `se_deplacer` : `0.0` ou `1.0` par mouvement.
- Décroissance `body.food` par pas : `0.0` ou `0.5`.
- Décroissance `body.water` par pas : `0.0` ou `0.2`.
- Début de nuit : `night_start_step=200` (jour au t1 et t5) ou `night_start_step=3` (jour au t1, nuit au t5). Jour de 300 pas, nuit de 100 pas, conformément aux bornes de `WorldPhysicsConfig`.

Fixture de départ : `physical_fixture_config()` physique pure A2.30-L (corps énergie=50, nourriture=60, eau=20, intégrité=100, sans récupération ni coût des autres primitives), modifiée **uniquement** par les six facteurs ci-dessus et une étiquette/version de protocole. Layout sans obstacle, créature, danger ou zone mortelle. B présente dans les bras concernés, avec effet caché du fixture laissé inchangé et **jamais consommée**. Coûts et facteurs sont des paramètres **d'oracle du banc**, jamais fournis comme entrées au modèle ou au planificateur.

Tous les **64** mondes appliquent physiquement les **4 mêmes commandes prédéfinies** à `t_monde=1..4` avec `WorldBody.apply` et préservation des observations `SymbolicPerception → state_from_capture` avant et après chaque acte. Après retour au t5, former **un équipement exact gelé à partir des 4 seules expériences physiques NON TERMINALES de CE monde**. Interroger une seule fois par monde :
- la prédiction exacte `move(east)` sur `state_t5`, avec compte de clés racine candidates/connues ;
- **le véritable `SimulatorPlanner.search`**, `max_depth=3`, `r_eff=1`, `progressive_subgoals=True`, `progressive_evaluation_prefix=True`, `progressive_revalidate_on_new_capture=True`, objectif spatial **`x == initial_x+1 ET y == initial_y`**, **sans** `progress_measure` (une progression du repas n'est pas déduite d'un simple déplacement).
- conserver les commandes, le statut `plan_found` / `incomplete_model` / autre, les trois compteurs racine, et le coût UC réel **NON MESURÉ**.

**Témoin physique positif prescrit à l'avance :** dans les quatre cellules `energy_cost=0, food_decay=0, water_decay=0, night_start=200` (deux positions × deux layouts), après les recherches, appliquer **un cinquième mouvement east à t5** et confronter sa conséquence physique à `Equipment.predict`, en conservant les reçus comme actes nouveaux et non comme source de prédiction antérieure. Les 60 autres mondes s'arrêtent après t4 sans cinquième action. Toute borne terminale arrête immédiatement le monde, sans continuation ni interprétation subjective postmortem.

**Effectifs exacts attendus : 64 mondes, 256 mouvements de boucle + 4 mouvements de témoin = 260 transitions physiques réelles, 64 recherches Stage6, 4 entrées t5 identiques à t1, 60 entrées t5 distinctes, 4 arêtes `move(east)` connues à t5, 60 inconnues, 4 `plan_found` en un pas vers l'est, 60 `incomplete_model`, zéro décès, zéro ingestion, zéro naissance/commande autonome I0.** Les effectifs ne doivent pas être modifiés après les résultats : tout écart physique = protocole FAIL à documenter.

## Reçus et comptabilité scientifique

Enregistrer pour chaque monde : six facteurs, SHA-256 `WorldPhysicsConfig` et `WorldLayout`, les 4 exemples complets `SimulationState_t × PrimitiveCommand_t → state_(t+1)`, chaque drapeau terminal, les captures t1/t5, les deltas des quatre variables corporelles, la parité des coordonnées et des ressources, `is_night`, SHA exact d'entrée `FrozenTableEquipment`, toute réponse de modèle et les diagnostics du vrai Stage6. Pour les quatre re-entrées, archiver le cinquième exemple physique et une comparaison de toutes les composantes accessibles du résultat prédit au résultat physique.

Vérifier l'unicité des 64 mondes et la séparation des corpus : jamais d'exemple du monde voisin ou de la variante opposée; ne jamais exposer au Stage6 les facteurs énergétiques et temporels du banc autrement que par les observations autorisées. Les quatre cas `berry_b` visibles dans ce témoin restent des ressources NON COMESTIBLES DANS CE PROTOCOLE : ni le modèle ni le monde ne les ingère. Ne pas appeler une sous-étape spatiale « plan alimentaire », « sécurité prouvée » ou « jugement subjectif ».

## Falsifications obligatoires

Des tests qui rejettent réellement : (i) prétendue égalité basée sur `x,y` malgré perte d'énergie; (ii) modification `is_night` entre t1/t5 ignorée; (iii) futur t5 inclus dans le corpus gelé à t4; (iv) exemple étranger injecté; (v) fausse réussite d'un plan fondé sur un état seulement spatial; (vi) ingestion `berry_b` inventée; (vii) observation après décès fictivement vécue; (viii) commande physique exécutée par le shadow; (ix) demande de sécurité absolue du mouvement extrapolée à un autre monde; (x) hash d'exemple physique falsifié; (xi) monde/bras/position omis; (xii) relecture externe du `WorldBody` décrite comme une vie I0. Tests Python 3.11 et 3.12, avec vérification des artefacts et dénominateurs.

## Décision autorisée

**ZM PASS technique** seulement si (a) les 260 applications de physique sont observées dans les 64 mondes, (b) les 64 recherches Stage6 et les 4 prédictions positives sont effectivement exécutées, (c) les 4 re-entrées et 60 non-re-entrées correspondent à la matrice, (d) les 4 pas t5 vérifient exactement la prédiction, (e) les contrôles adversariaux sont verts. Un résultat positif est un **témoin local de réutilisation de même état/perception dans un monde connu**, pas une découverte de causalité universelle ou une maîtrise de la toxicité.

**A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN ; déploiement cognitif NO-GO. Aucun changement à `src/i0`, Oracle/Bench, P48, WAL mortel M11, Stage9/DC-05, UC, jugement B, ou `docs/architecture/reference/en/mvp-specification-v1.3.1.md`.** PR DRAFT non fusionnée, aucun transfert de mémoire entre individus.
