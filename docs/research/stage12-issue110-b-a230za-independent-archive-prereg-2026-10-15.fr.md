# A2.30-ZA : audit indépendant des choix perceptifs et du Stage6 sur les archives Z

**15 octobre 2026. Préenregistrement après connaissance des résultats Z, mais AVANT le code d'audit ZA.** Cet audit est **une relecture de la même cohorte**, pas un nouveau test physique ni une validation prospective nouvelle. Parent scientifique PR #195, original [run physique Z #38760713470](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38760713470), code original `0d9fd7cd511640103498f037b84cae915169356e`, exécutions Python 3.11 et 3.12. Créer une PR scientifique *empilée* différente et ne modifier **aucun fichier de la campagne Z originale ni aucune dépendance cognitive**.

## Provenance, priorité des protocoles et limite de reproduction

Le protocole original Z `c046712b97b0e5887dece3b490957123013d7b5e` demandait de fixer les effectifs **avant** le runner Z. Un premier complément `70b4e0663026d362cb8642787e3f615469168fc6` envisageait 68 mondes/160 pas à **15:19:46 UTC**, puis un second amendement **avant code, avant toute physique** `e9543fe0139f` (**15:20:30 UTC**) a remplacé cette petite matrice par un protocole factoriel plus discriminant : **168 mondes/244 pas**, cinq layouts, deux règles perceptives, plusieurs effets cachés A/B. **Le petit protocole n'a jamais été exécuté en tant que cohorte Z**. Conserver les deux propositions historiques pour la transparence : l'amendement antérieur au code est le **seul protocole réellement testé** ; aucune modification post-résultats n'est légitime.

Fichiers de la CI originale Z, identiques octet à octet entre deux versions Python d'après une inspection externe effectuée **avant** ce préenregistrement :
- `a230z-physical-worlds.json` : SHA-256 intégral des octets `09fc343e059eebcd7bee863ca1e93d41a2c606d3afa6636e11f72d89f9f0458d`.
- `a230z-summary.json` : `170c8db38b419a22b63ca0f7493dae0e83d9069b34ad3388c7e9dbaa2d8a783c`.

Artefacts sources : `a230z-py3.11` et `a230z-py3.12` du run ci-dessus. Refuser les noms ambigus, les empreintes divergentes et un jeu qui change d'un Python à l'autre. **Les deux versions reprennent des cellules déterministes identiques, pas des échantillons scientifiques indépendants.**

## Questions falsifiables à vérifier avec une NOUVELLE implémentation

1. **Comptabilité indépendante** : identifier exactement les 168 mondes uniques du produit `layout × protocol × variant caché × nourriture × position`, avec 244 transitions du moteur enregistrées, 80 ingestions B, 20 terminalités externes, 40 gains alimentaires avec survie et 20 insuffisants, 88 abstentions de B. Ne pas recycler les counts du résumé original sans recomptage ligne par ligne. Vérifier deux captures initiales alimentaires 35/45 et positions 5,5/7,7.
2. **Sensations et politique strictement accessibles** : reconstruire sans importer le script Z une fonction de décision pure basée seulement sur le **SimulationState complet avant chaque action**, la politique préengagée et l'historique propre des commandes antérieures. Tester qu'elle trouve B locale, B à l'est accessible, refuse B à l'est **bloquée**, et ne devine PAS la ressource située à deux cases avant un déplacement exploratoire. Vérifier que chaque commande réellement enregistrée correspond à cette politique de laboratoire et est autorisée selon les préconditions Stage6. Le décideur du banc est effectivement appliqué à WorldBody ; **ce n'est pas** un choix cognitif autonome I0.
3. **Histoires causales** : contrôler la continuité `state_before_i == state_after_(i-1)`, les SHA de chaque `EquipmentCorpusExample`, le pas de chaque commande, l'absence de reprise après mortalité, et le fait que le `SimulationState` terminal figure **uniquement dans les reçus externes** (pas dans `lived_states_while_alive`).
4. **Indiscernabilité physique** : pour chacun des **40 contextes avant consommation** combinant layout/protocole/nourriture/position, vérifier que l'histoire des commandes et observations avant ingestion est identique entre effets cachés ; pour les **8 paires A_ONLY/B_EAST_TWO_STEPS** à contexte identique, vérifier l'identité des perceptions au premier pas malgré la B éloignée. Une divergence visible d'obstacle ou d'espèce sur une case directement accessible doit, inversement, affecter les commandes candidates correctement.
5. **Audit algorithme Stage6 réel en shadow** : pour les 80 recherches originales (une avant chaque ingestion), reconstituer **sans charger SimulatorPlanner ni FrozenTableEquipment** les candidats disponibles depuis le `SimulationState` et la table exacte des **seuls exemples antérieurs physiquement enregistrés dans le MÊME monde**. Vérifier la signature des exemples du corpus, l'instant de recherche, le SHA de l'état interrogé, le SHA du corpus, la disponibilité de la première arête et ses 80 diagnostics `incomplete_model` / racine sans arête connue. Un plan véritablement autonome et sa dépense UC sont **hors du domaine de ce test**.
6. **Compromis scientifique** : pour chacun des **20 groupes de contextes préingestion connus où B est consommée**, examiner les quatre conséquences cachées (deux gains avec survie, un décès, une insuffisance). Le choix de consommer B ne peut **pas** garantir l'absence de décès lorsqu'un monde latent létal présente le même historique first-person. Ne pas transformer cela en estimation de mortalité naturelle, en preuve qu'aucun autre plan existe ou en jugement subjectif d'agence. Le sondage peut révéler l'existence physique d'une B éloignée, **mais ne révèle pas ses effets cachés**.

## Contrôles de falsification obligatoires

- Champ `latent_berry_effect_external_only` ajouté à l'état perceptif => FAIL.
- Ressource ou obstacle modifié dans l'état **avec son hash recalculé** mais décision inchangée => FAIL de politique.
- Commande B `collecter/manger` sans ressource/quantité, mouvement est bloqué et néanmoins marqué déplacé => FAIL.
- État terminal artificiellement compté comme vécu ou pas appliqué après mort => FAIL.
- Exemple futur ou issu d'un autre monde injecté dans la mémoire Stage6, arête racine inventée, recherche après mortalité => FAIL.
- Certification `safe`, coût UC `0` artificiel ou pseudo-verdict `plan_found` de production => FAIL.
- Falsification du résumé sans modification des faits archivés => FAIL.
- Inventaire A/B, temps/ordre d'actions et états corporels invalides => FAIL.

**Validité technique limitée :** l'auditeur en lecture seule peut établir cohérence interne, reproductibilité des scores, absence de fuite évidente et engagement temporel admissible, **mais pas prouver depuis les JSON l'application effective du moteur WorldBody.apply** ; une réexécution physique technique indépendante, préenregistrée **après ZA** si nécessaire, est une étape distincte. Tout résultat ZA ne contient **aucune nouvelle vie, aucun monde, aucune action physique**. Ne pas fusionner les branches empilées, ni changer le MVP v1.3.1, Stage6, Stage9/DC-05, Stage12, WAL, UC ou le jugement subjectif.

**Statut préexécution ZA : code/tests/audit non encore réalisés ; A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN, déploiement cognitif NO-GO.**
