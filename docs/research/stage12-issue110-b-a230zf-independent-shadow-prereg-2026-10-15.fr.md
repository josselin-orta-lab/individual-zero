# A2.30-ZF : préenregistrement d'un audit indépendant des archives originales ZE

**15 octobre 2026 ; après résultats ZE connus, avant code d'audit ZF.** Source ZE : [CI #38773219305](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38773219305), SHA de l'exécution physique `e56880e50e278f52640d525ff53916b8fb6ce8de`. Les deux jobs Python 3.11/3.12 ont produit des résultats connus : 33 mondes indépendants de laboratoire, 13 commandes physiques non ingestives, 24 états de test sans acte physique, huit `partial_progress` avec démonstration B pour 8 états prévus, zéro pour 8 coordonnées inconnues et 8 contrôles négatifs; baseline A-only `incomplete_model` sur tous les 24. ZF **ne peut pas** constituer une seconde expérience scientifique.

## Artefacts source immuables et leurs empreintes connues AVANT ZF

Les artefacts `a230ze-py3.11` et `a230ze-py3.12` du run #38773219305 comportent exactement les mêmes trois JSON, **identiques octet à octet** entre Python :
- `a230ze-training-manifest.json` : SHA-256 `abb45515fa96ac56000527925f68fddfc9693d38dabded8c7941181c81fa1054`.
- `a230ze-heldout-shadows.json` : SHA-256 `2fd30ac9326ae36dd0231ac6807f7992ed7f7a9ee28b95af42d46ac9bb369667`.
- `a230ze-summary.json` : SHA-256 `5ff00641e58303ba72b644a7dadfd5470319a6e0d1f8adc041b9e7cf53b65f19`.

Toute divergence de l'un des six fichiers originaux ou ambiguïté de leur chemin invalide ZF. Lire les deux archives, sans lancer aucun `WorldBody`, `SimulatorPlanner.search`, prédicteur d'I0 ou runtime cognitif.

## Reconstruction indépendante prévue

1. Extraire **9** identifiants mondes de démonstration, **13** exemples physiques réellement consignés, et **24** mondes de test **sans action**; vérifier identité de monde distincte, chaînes temporelles non ingestives et localité de B avant `collecter(B)`, passabilité est avant `se_deplacer(east)`, terminalité toujours fausse, les hash SHA-256 des exemples et les digests des clés `SimulationState × PrimitiveCommand`. L'inventaire, les variables corporelles et le monde observé avant/après chaque pas doivent être contigus.
2. Reconstituer deux **dictionnaires exacts** indépendants du code de prédiction : témoin `A_ONLY` (un exemple A) et table A+B (13 exemples dont certains doublons de la même clé perceptive). **Collisions ambiguës** de conséquence à entrée identique = FAIL; les effets cachés d'ingestion de B ne sont jamais des données de modèle.
3. Pour chaque état de test, dériver depuis la perception visible seulement les préconditions du premier pas B (collecte locale, mouvement est possible) et **la clé exacte** de ce pas dans chaque dictionnaire. Si l'état est connu, réévaluer la chaîne `B_EAST: move east→collect B` sans appliquer la moindre physique réelle. Vérifier que la variation d'inventaire de B est observée seulement après la collecte et correspond à une **capacité**, pas à une hausse alimentaire.
4. Vérifier que le verdict de Stage6 enregistré par ZE est cohérent avec les graphes reconstruits : **8** racines enrichies ID connues et `partial_progress`, **16** racines enrichies inconnues et `incomplete_model`, **24** racines témoins inconnues, **zéro** `plan_found`, **zéro** ingestion, **zéro** revendication `safe`. Les états hors coordonnées et bloqués doivent être comptés comme refus exact-key, pas comme incapacité universelle.
5. Rejeter des falsifications adversariales : SHA physique altéré, `manger(B)` inventé dans le corpus, scénario bloqué présenté comme passable, étiquette de toxicité ajoutée à l'entrée cognitive, proposition `plan_found` fausse, prédiction sur état OOD inconnue, réutilisation d'identité entre mondes, commande shadow présentée comme physique, UC fictivement facturée et duplication de cas de test.
6. Communiquer explicitement une faiblesse méthodologique : les démonstrations B incluent **les deux variants cachés** à chaque contexte visible; le test pairé opposé concerne des **mondes physiquement distincts**, pas une nouvelle classe latente jamais vue par aucun démonstrateur. Puisque **la baie n'est jamais ingérée**, l'effet caché n'a de toute façon pas été appris; le résultat **n'est pas** une mesure de généralisation à une toxicité inconnue.

## Conclusion et autorisation

ZF est un audit **rétrospectif d'intégrité et de cohérence de prédiction** à partir des mêmes résultats ZE, **zéro nouveau monde, zéro pas, zéro naissance I0**. Il ne prouve ni que ces exemples devraient être transmis à un individu vivant, ni que celui-ci agirait, ni un gain de nourriture, ni une responsabilité causale, ni la sécurité de l'espèce B. Tout PASS reste borné.

**A2.30 PARTIELLE ; Stage12 PARTIAL ; #110 OPEN ; PR #199 DRAFT ; intégration cognitive NO-GO ; aucun changement de `src/i0`, Stage9/DC-05, UC, journal mortal M11 ou MVP v1.3.1.**
