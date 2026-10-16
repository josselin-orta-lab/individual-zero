# A2.30-ZE : préenregistrement prospectif d'une ablation de couverture exacte Stage6, hors I0

**15 octobre 2026.** Préenregistrement **avant tout code, monde ou résultat ZE**. La base est A2.30-ZD [PR #198](https://github.com/josselin-orta-lab/individual-zero/pull/198), commit `99b7618f10202c808ab8d832d85a68f10e51997e`, avec ses résultats **connus** : 12 vies autonomes originales ZB, 384 pas, aucune action B, 174/196 recherches sans proposition, aucune UC refusée et 4 premières captures B locales éligibles à `collecter(B)`. Ces vies ne sont pas reproduites par ZE.

## Problème et dissociation causale

Quel déficit **mécanique de couverture du modèle exact** suffit à transformer la possibilité perceptive de collecter B en une première action Stage6 *prédictible*, éventuellement une sous-étape d'un objectif alimentaire ? La disponibilité de `collecter(B)` dans `candidate_commands` ne vaut pas une conséquence prédite, mais une démonstration physique passée d'une transition **non ingestive** peut fournir cette conséquence. L'effet caché de B **ne peut toujours pas devenir connu avant ingestion**.

- **ZE1 (témoin positif borné)** : en présence de B locale, un `FrozenTableEquipment` enrichi par une transition `collecter(B)` physiquement exécutée dans **un autre monde indépendant au même état initial accessible**, peut transformer une recherche `incomplete_model` en `partial_progress` par gain d'inventaire, **sans aucune prédiction de `manger(B)`**.
- **ZE2 (préfixe spatial)** : si B n'est visible qu'à l'est, la démonstration physique `se_deplacer(east) → collecter(B)` fournit deux premières arêtes connues. Stage6 peut alors proposer la **première commande de déplacement** comme sous-étape alimentaire, même si aucune ingestion n'est planifiée ou certifiée.
- **ZE3 (négatifs)** : avec B absente, B derrière une case est bloquée, ou avec **des coordonnées inédites** `(7,7)` malgré les mêmes conditions qualitatives, la table exacte doit refuser d'inventer une première arête. La physique du fruit B ne constitue jamais une caractéristique de perception.
- **ZE4 (épistémique)** : les mondes évalués portent des effets physiques cachés **opposés** au monde d'entraînement, pour vérifier que l'aliasing bénin/létal demeure. L'exemple de collecte bénigne ne doit être converti ni en `safe` ni en prédiction d'ingestion et il n'est jamais fourni au runtime I0.

## Matrice de mondes indépendante, effectifs verrouillés

Élaborer tous les mondes depuis une configuration physique pure basée sur `physical_fixture_config()` du banc L, largeur 32, hauteur 32, position et alimentation initiales fixées par la matrice, pas d'Oracle. Physique : ressources `berry_a` sur case initiale; B absente, locale, à l'est passable, ou à l'est **visiblement bloquée**; pas de créature ni zone létale, ressources B en quantité 2. Coûts physiques de mouvement 1, collecte 0,75, ingestion 0,5; décroissance de nourriture 0,5 et d'eau 0,2 par étape. B a deux effets latents **indiscernables avant ingestion**, `benign = (food_gain=12, integrity_delta=0)` ou `toxic_lethal = (food_gain=12, integrity_delta=-100)`. Ces deux paramètres latents appartiennent **exclusivement au monde physique externe**.

### Entraînement physique sans ingestion

- **1 monde A_REFERENCE** indépendant : `berry_a` collectée sur un état initial (position `(3,3)`, food `60`) pour fournir une **table témoin A uniquement**, avec **1 action réellement appliquée**.
- **8 mondes de démonstration B** : `{B_LOCAL,B_EAST}` × nourriture `{35,45}` × effet caché de B `{benign,toxic_lethal}`, position **`(5,5)`**. Pour B_LOCAL, appliquer **exactement `collecter(B)`**, une fois ; pour B_EAST, appliquer exactement `se_deplacer(east)`, puis `collecter(B)`, deux fois. **12 actions physiques supplémentaires**. Capturer toutes les entrées/sorties accessibles via `EquipmentCorpusRecorder.record_transition` et conserver chaque SHA d'exemple. **Ne jamais appeler `manger(B)`, même dans le monde bénin**. Exiger zéro terminal et aucune fuite d'effet latent dans les observations accessibles de ces préfixes.

Deux tables gelées : `A_ONLY` = un exemple physique A; `A_PLUS_B_KNOWN_PREFIX` = A plus les douze démonstrations B. Les collisions d'entrées observables entre témoins bénins/mortels ne doivent être admises que si leur conséquence non ingestive est **exactement identique**. Une contradiction au même couple `SimulationState × PrimitiveCommand` = FAIL, jamais moyenne/sélection opportuniste.

### Test dans de nouveaux mondes **sans y agir**

- **8 mondes ID** : `B_LOCAL/B_EAST` × `{35,45}` × variante cachée opposée à celle de la source démontrée. La position reste `(5,5)`; les mondes de test ont une identité distincte et leur **première perception accessible seulement** est interrogée. Les exemples issus d'un autre monde correspondent à cette entrée observable; aucune transition n'a lieu dans le monde de test.
- **8 mondes OOD position** : même disposition/food/variantes, mais position `(7,7)`, entière absente de la table. Le modèle exact doit échouer à prédire le premier pas.
- **8 mondes témoins négatifs** : `B_NONE/B_EAST_BLOCKED` × nourriture `{35,45}` × variante cachée `{benign,toxic_lethal}`, position `(5,5)`; aucune démo d'un tel état n'est entraînée. B bloquée = impossibilité **du mouvement direct vers l'est**, non de tous les itinéraires mondiaux.
- **Total attendu : 9 mondes de démonstration, 24 mondes de test, 33 mondes distincts ; exactement 13 transitions physiques d'entraînement, 0 transition dans les mondes de test, 0 naissance I0**.

Le modèle est figé **avant la création du moindre monde de test**. Les deux tables sont interrogées par le **véritable `SimulatorPlanner.search`** en shadow, `r_eff=1`, `h_eff=3`, `progressive_subgoals=True`, `progressive_evaluation_prefix=False`, `progress_measure='food'`, cible `food ≥ food_initial+5`. Le runner ne dispatch jamais la proposition. La table enrichie **ne contient pas d'ingestion B**, et aucun acte prétendument sain n'est certifié. Le modèle est un **témoin de formation de capacité**, et non une vraie mémoire I0 : le transfert **entre individus/mondes** resterait interdit en production sans décision normative.

## Mesures et falsifications

Pour chacun des 24 états de test : comparer `candidate_commands`, `root_candidate_edges`, `root_available_edges`, `root_unavailable_edges`, `status`, `partial_progress`, `commands`, `predictions` et chaque entrée de table déjà vue. Conserver l'identité du monde démonstrateur et du monde évalué, les SHA de toutes les applications physiques, les historiques d'effet latent **externes seulement**, les captures initiales complètes et les deux résultats shadow. Aucune fuite test→train, aucune physique évaluée après construction du modèle.

**Contrôles invalidants :** (a) proposition `manger(B)` alors qu'aucun `manger(B)` n'a été démontré; (b) label de sûreté B ou secret latent dans `SimulationState` ou `FrozenTableEquipment`; (c) citation d'une collecte dont `berry_b` n'était pas localement disponible ou d'un déplacement vers une case bloquée; (d) réussite OOD à clé exacte inconnue; (e) même ID entraînement/test, modèle entraîné avec les conséquences d'un monde de test, ou prise d'une décision shadow comme commande réelle; (f) mauvais nombre de transitions physiques, décès ou restauration; (g) prétendue UC vécue alors qu'aucun I0 n'est né. En cas d'échec scientifique, rapporter les comptes obtenus sans ajuster la matrice.

**Critère Z1/Z2 attendus, falsifiables :** les 8 requêtes enrichies ID doivent avoir au moins une arête prédictible, toutes doivent être `partial_progress` **sans ingestion prévue** ; les 24 requêtes A-only et les 16 requêtes enrichies OOD/contrôles doivent être `incomplete_model` avec zéro arête racine. Toute autre réponse reste un résultat valable à documenter mais **FAIL du critère préenregistré**.

## Verdict autorisable

**Un PASS du mécanisme Stage6 prouverait uniquement** que la disponibilité d'une observation physique de collecte/mouvement, venant d'un monde extérieur, peut rendre possible une proposition de progrès alimentaire à court terme. Il **ne prouverait ni repas, ni sécurité de B, ni mémoire vécue d'I0, ni action arbitrée ou exécutée, ni coût UC réel**. Un transfert de cette table vers un I0 réel serait une intervention cognitive dangereuse et non autorisée par ZE.

Stage12 **PARTIAL**, issue #110 **OPEN**, A2.30 **PARTIELLE**, PR de recherche **DRAFT**, pas de modification de `src/i0`, Stage9/DC-05, mortalité, WAL M-11, UC ou spécification normative MVP v1.3.1.
