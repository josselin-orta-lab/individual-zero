# A2.30-ZT : préenregistrement rétrospectif d'un audit externe des archives ZS scellées avant action

**15 octobre 2026, APRÈS la première exécution ZS et AVANT l'implémentation du vérificateur ZT.** ZT n'est **pas** une seconde expérience de physique ni une prédiction scientifique inconnue. Le résultat ZS est déjà connu : 120 mondes détachés et 120 transitions (16 entraînement puis 104 test), 104 prévisions produites dans le job `seal-before-physics` et archivées **avant le commencement** du job `realize-after-seal`. Ce dernier possède un `needs` explicite dans le workflow. Résultats connus : 64/64 prévisions nominales exactes à six composantes, 16 abstentions, quatre morts cachées, huit blessures, huit échecs moteurs et **zéro** certificat de sûreté.

**Source primaire inchangée et immuable :** [GitHub Actions #38801117723](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38801117723), commit `804e2ebb653278f18bd85aa364015acffd3bdb0e`, PR [#214](https://github.com/josselin-orta-lab/individual-zero/pull/214), préenregistrement ZS original `8ae4f26650bdb5f47f474051763bd8c91aba7afd` AVANT code. Les quatre jobs ZS (seal et realize, Python 3.11 et 3.12) sont verts au moment du préenregistrement ZT. Une autre PR [#213](https://github.com/josselin-orta-lab/individual-zero/pull/213) conduit une expérience ZS indépendante en scellant **séquentiellement** chaque prédiction et chaque outcome dans un même processus ; ZT ne doit pas confondre cette preuve avec l'expérience ZS **séparée par deux jobs GitHub** de #214. Les noms d'études homonymes sont distingués par **SHA de code et numéros de runs**, pas par une fusion des cohortes.

## Sources complètes scellées avant code de relecture

**Artefacts originaux du même run #38801117723 :**
- `a230zs-sealed-py3.11` et `a230zs-sealed-py3.12`, contenant chacun quatre JSON + un log. SHA-256 des **octets JSON originaux**, identiques entre versions Python :
  - `a230zs-training-physical.json` : `818fbb1679603323ea8641aa6dfc1684c12757877bd9d570a53aa332d0bd551a`.
  - `a230zs-frozen-model.json` : `3ce61a1fe1e490c56e061d1c2a33e78414cbcdc90e672739014903cf6cfb1a8c`.
  - `a230zs-preaction-forecast-receipts.json` : `ba4f471636534aefb2ff86217c73f23c6b57924566b3459583192e91026a395d`.
  - `a230zs-source-seal.json` : `c5157c83a78ad0a3ce2a071e14d05cd6365aff2e1d74caeefdbf3686363241c5`.
- `a230zs-realized-py3.11` et `a230zs-realized-py3.12`, contenant chacun trois JSON + un log. SHA-256 des **octets JSON originaux**, identiques entre versions Python :
  - `a230zs-realized-physical-worlds.json` : `cb88057fd6f45f22f40afeccc8af38d18d020856838102296e64e08ae1dbc926`.
  - `a230zs-sealed-predictions-scored.json` : `0a8393c50d9200019435c1027f952ca5e1d9b99efb64d62ddad39184a2fe0354`.
  - `a230zs-summary.json` : `fba0cd5523cbbdf4fb30430239202bd164b27afdd92a52382704ced64d29839a`.

**Fournir exactement un fichier sous chaque nom dans chacun des quatre dossiers**, échouer si archive expirée, introuvable, mutée ou double. Ne jamais effectuer une re-génération de sources si elles sont indisponibles. Ne pas supposer que le SHA du conteneur ZIP est le SHA des documents scellés.

## Méthode indépendante et contrôles falsifiables

1. **Script standard-library only**, qui n'importe ni le runner ZS ou ZO, ni `lab.determinism`, ni `WorldBody`, ni `FrozenTableEquipment`, ni `SimulatorPlanner`, ni `Stage12Runtime`, ni Oracle. Réimplémenter localement la normalisation causale SHA-256 (floats hexadécimaux, NFC, tri de clés) puis recomputer les SHA-256 d'octets de tous les fichiers.
2. Reconstituer les **16 vraies transitions d'apprentissage archivées** à partir des observations, commandes, deltas et SHA source des reçus. Recalculer seul pour `MOVE_E` et `COLLECT_B` les **six deltas visibles**, avec `None` si observations incompatibles, comparer sans arrondis de substitution au modèle scellé. Aucune étiquette cachée ne doit influencer le modèle.
3. Recalculer les **104 prévisions** à partir de leurs seuls `preaction_first_person`, action, six deltas source. Contrôler les SHA structuraux individuels, le hash du modèle, l'absence de tout champ de conséquence physique future dans un reçu pré-action, toutes valeurs `integrity`, `terminal`, `next_adjacency`, `safe` à `null`. Les prédictions doivent rester fixées même si un résultat physique après action les contredit.
4. Joindre aux **104 sorties physiques originales** et aux 104 scores chaque `world_id`, entrée, commande, SHA d'exemple, `postaction_external_only`, mortalité externe, delta d'intégrité et divergences sur les six champs. Reproduire 64/64 succès nominaux, 16 abstentions, quatre décès cachés, huit blessures et huit échecs moteurs numériquement contraires à la prévision. Recalculer les 32 paires `benign/toxic_lethal` ayant les mêmes perceptions et prévisions, et les 24 bras cachés observables identiques aux témoins correspondants.
5. Recompter les **104 clés état complet × commande** tenues à l'écart : aucune dans les 16 clés exactes originales; cela ne permet aucune prédiction intégrale sûre.
6. **Contrôles négatifs** : réécriture d'un octet source malgré SHA intact prétendu ; prédiction re-hachée de résultat déjà observé ; falsification de la cause de mort, d'un `terminal`, d'une `safe` ; génération d'un champ `hidden_B` dans l'entrée ; ressource B fantôme ; commande inéligible ; injection d'une donnée heldout dans le modèle ; attribution UC/agency vécue I0 ; falsification de classe nominale, d'identité, de score d'erreur, de compteur ou de stade `SEALED_BEFORE_HELDOUT`. La falsification observable doit échouer, sans « réparer » les données originales.
7. CI **Python 3.11 et 3.12** avec rechargement des quatre artefacts originaux du run épinglé, sans monde physique supplémentaire ni seconde émission de prédictions faisant foi. Publier le rapport ZT avec sa provenance, tests adversariaux, différences cross-Python, et les limites de l'archivage.

## Portée légitime de la preuve

Un contrôle de fichier ne peut à lui seul attester historiquement du temps d'exécution du moteur `WorldBody.apply`; la séparation effective et l'ordre des **jobs GitHub** dépendent des logs/action `needs` et du code de la CI ZS originale, non d'un champ libre de manifeste. ZT pourra établir l'intégrité des sources et les recomptages, **pas** une preuve indépendante de la physique ni un certificat de sûreté. Aucun transfert de connaissances externes à I0 ni preuve de jugement distal sur la mortalité.

**ZT : résultats inconnus avant code, audit rétrospectif seulement. A2.30 PARTIELLE ; Stage12 PARTIAL ; #110 CLOSED administrativement ; PR #214 DRAFT sans fusion ; expérimentation cognitive et déploiement NO-GO.**
