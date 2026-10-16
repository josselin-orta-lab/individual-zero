# A2.30-U : préenregistrement d'une relecture indépendante des mondes confondants de S-shadow

**15 octobre 2026 : résultats S et audit T déjà connus, code U pas encore écrit.** Les [CI S #38740664255](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38740664255) et [T #38741660739](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38741660739) sont PASS sous Python 3.11/3.12. S : 72 mondes détachés, 196 pas, 56 diagnostics Stage6 shadow sans première arête, 8 paires ingestions observablement indiscernables. T : cohérence indépendante des fichiers, **sans réapplication physique**. Autre recherche en parallèle #190 (S-observable) et #192 (T-food-shadow) : ne pas compter leurs tests comme répétitions indépendantes de S-shadow, ni modifier leurs branches.

## Objectif et non-objectif

**Objectif U :** réinstancier **sans le code runner S**, sans `EquipmentCorpusRecorder` ni modèle Stage6, les conditions de physique pure fixées par le protocole S-shadow, puis appliquer les mêmes commandes physiques dans de **nouveaux mondes de relecture technique**. Comparer **chaque** capture autorisée, le terminal, les hash des exemples et les empreintes du WorldPhysicsConfig/WorldLayout préenregistrés. Rejouer exactement entre t2 et t3 une intervention externe `set_danger_zone` sur la case de `berry_a` dans les mondes `exogenous_confounded`, en attestant l'absence de changement dans la perception juste avant ingestion. Ne consulter aucune sortie Stage6 pour choisir les commandes.

**Non-objectif :** ne pas produire de nouvelles vies I0, ne pas créer de nouvelles cellules scientifiques indépendantes, ne pas rétablir le monde après mort, ne pas déduire que I0 sait pourquoi sa nourriture a causé un résultat. Toute perception **après** une transition terminale est un reçu technique externe, pas une perception subjective ultérieure.

## Protocole verrouillé

Charger seulement les originaux du [run scientifique S #38740664255](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38740664255), artefact `a230s-py3.11`, code `0046d8b2b30f44fe5e4fd0b4b165c88e724a8881`, avec les SHA-256 figés par A2.30-T. Les données issues de l'archive ne déterminent que les identités des cellules, pas les préconditions nécessaires à l'application : reconstruire explicitement la physique via `WorldPhysicsConfig` et `WorldLayout` d'après les recettes de S, vérifier les digests **avant toute transition**, imposer les commandes préengagées du protocole, puis comparer leurs traces aux originaux.

- **64 mondes actifs**, 196 vrais pas physiques de **relecture technique**, avec arrêt et gel définitif du monde au premier décès.
- **8 mondes de perception seule**, zéro transition appliquée, une capture initiale vérifiée (baie présente/absente, obstacle est libre/bloqué).
- **72 mondes techniques recréés, 196 pas physiques rejoués**, **0 condition scientifique nouvelle**, **0 naissance I0, 0 pas autonome I0**, aucun retour à un I0 vivant.
- Reproduire l'égalité perceptive des paires `toxic_mild` / `exogenous_confounded` à t3 après ingestion, les conséquences divergentes t4 de `attendre` vs `manger` et les terminaux spatiaux sous préengagement `attendre` vs `escape`. Tout faux match/terminal est **FAIL**.

## Contrôles d'invalidation et frontière scientifique

Falsifications obligatoires : un `config_sha256` changé, une capture corporelle falsifiée **même si le SHA JSON est recalculé**, un événement environnemental ajouté/supprimé, une fausse terminalité, une commande réécrite ou un pas postmortem déclenchent un échec. Les digest d'archives sont comparés avant l'audit. Comparer Python 3.11/3.12 sans doubler les échantillons.

Un résultat PASS démontrerait **une concordance de la physique avec le protocole et les reçus**, pas la fiabilité universelle de WorldBody, une attribution subjective, un entraînement d'I0 ni la sécurité d'un prédicteur. **A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN ; PR #191 DRAFT ; pas de fusion ni révision de v1.3.1.**
