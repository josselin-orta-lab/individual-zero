# I3 · Étape 6 légère : contrat de lecture des originaux natifs, sans World (14 novembre 2026)

**Statut : `READ_ONLY_NATIVE_SHAPE_PREFLIGHT`, `METHOD_FIXED_PREAUTH_NOT_EXECUTABLE`, `NOT_RUN_NO_AUTHORIZATION`.** Cette tranche développe le *vérificateur d'un futur transport* et non le transport vivant : ni admission, ni reproduction, ni `run_life`, ni création de World, ni attribution de graine, ni répétition d'ingénierie. Les tests fabriquent des enveloppes au **format natif** sans faire naître un individu. Les nombres qu'ils représentent ne sont **pas** des observations d'I3.

## Question falsifiable

Le protocole v1 suppose qu'une génération puisse être scellée avant que sa persistance soit lue pour sélectionner la suivante. **Un fichier gzip et un SHA-256 ne suffisent pas.** Peut-on rejeter une archive pourtant correctement re-scellée mais contenant une mauvaise identité, une autre source, un WorldSpec non lié, une vie non soldée ou une double exposition ?

Le [vérificateur](../../../lab/stage6_light_native_custody_preflight.py) reprend uniquement le format de lecture de [`two_phase_panel.py`](../../../lab/two_phase_panel.py), les champs *produits* par [`run_life`](../../../runtime/life.py) et les empreintes de [`runtime/provenance.py`](../../../runtime/provenance.py). Il n'importe aucun module I3 : bibliothèque standard seule, pas de CLI, aucune entrée de génération. Les contrats consultés dans `main` avant ce chantier sont les blobs Git suivants : `two_phase_panel.py` `dc58e7acd2c222640e0dab652af3b9832949cc50`, `runtime/life.py` `5e79216210a9c19de1f7d3dd492ac9e5907eb94d`, `runtime/provenance.py` `9baa81e238bfbbd05f574e776d7bc49d5ceb5259`, `modules/genome.py` `003e923aa93b0b284a7f732fc91f3f02538dd85c`. Ce sont des *références documentaires des formes inspectées*, pas des empreintes de futurs fichiers exécutés.

## Contrats effectivement vérifiés

1. **Préautorisation bloquée avant lecture de l'archive.** Manifeste `STAGE6_LIGHT_PROTOCOL_METHOD_V1.json` au schéma et statut exacts ; six booléens de permission restent `false`, neuf champs de source/levée/indices restent `null` et l'adaptation intergénérationnelle ADR-0017 demeure non acceptée.
2. **Custodie du panel par génération.** Un `MANIFEST.json` complet et un `MANIFEST.sha256` concordant ; statut `GENERATED`, aucune erreur ; exactement 2 304 originaux G0 ou 4 608 G1/G2 ; filenames séquentiels sûrs, sans doublon ni symlink ; empreintes compressées et décompressées, décompression limitée, aucune archive supplémentaire dissimulée ; correspondance complète des cas attendus.
3. **Identité et opportunité.** G0 est `shared`, G1/G2 portent deux bras distincts ; 96 coordonnées de World par génération ; appariement strict `world_seed`/`life_seed`/`world_sha256` pour les 24 génomes (et les deux bras G1/G2) ; génome identique sur les six contextes d'un même individu ; pas d'index physique déduit de la seule coordonnée logique.
4. **Reçu natif.** `i3-life-manifest/v2`, source `i3-funded-v2`, politique P1.3 de référence sans `experimental_policy` ; empreinte SHA-256 calculée sur la carte des fichiers de code, `git_head` revendiqué et copie de travail déclarée propre ; schéma WorldSpec et empreinte de son instantané ; génome v4 générique, exact, valeurs dans les bornes et empreinte ; `manifest_id`, `evidence_head` et `trace_head` présents ; horodatage/horizon non utilisé comme variable d'inférence ; statut mort/censure cohérent.
5. **Monnaies de pensée réelles, au niveau du reçu.** `i3-cognitive-funding/v2`, énergie et vigilance demandées/payées/non payées avec comptabilité finie et soldée, aucun pas avec déficit, aucune dette de calcul, comptes d'apprentissage bornés. **Ce contrôle vérifie l'autocohérence du reçu : il ne rejoue pas encore les factures pas à pas à partir des actions corporelles.**
6. **Trois générations.** Le préflight optionnel vérifie les 288 coordonnées et la non-duplication des graines/empreintes de mondes *proposées*, ainsi que les intersections avec les plages historiques connues. Ce contrôle **ne démontre ni tirage indépendant, ni nouveauté de toutes les graines, ni correspondance véritable graine → générateur F0**.

Les fonctions ne retournent que des comptes structurels, des SHA de manifestes et des booléens de limite. **Aucun score de fitness, nombre de survivants, contraste de signe, choix de parent ou contenu biologique n'est publié.** En cas de défaut, l'appel lève une exception : il n'ouvre aucune branche de reprise ni de réparation automatique. Les commandes factices `open_world`, `run_life` et `authorize_science` sont toujours refusées.

## Tests strictement artificiels

[`tests/i3/test_stage6_light_native_custody_preflight.py`](../../../../../tests/i3/test_stage6_light_native_custody_preflight.py) fabrique 2 304 enveloppes G0 au format de deux phases. Il construit aussi, dans un répertoire temporaire distinct, des enveloppes G1/G2 pour exercer **11 520 enregistrements fictifs au total**. Ce test n'importe jamais de générateur de génomes, de physique, de Mind ni de vrai `run_life`.

Les contrôles adversariaux comprennent : SHA d'archive modifié, gzip altéré, nom de fichier avec traversée de répertoire, fichier caché, décompression excessive, identité dupliquée, source/git propre incorrecte, World ou génome non lié, mort/censure contradictoire, énergie/vigilance non soldées, données non finies, politique cachée, collision de graines *proposées*, et absence d'autorisation. Les chiffres et les coordonnées du test ne deviennent pas des graines scientifiques.

Commande reproductible (aucun World, aucun effet de bord sur les études historiques) :

```bash
PYTHONPATH=src python -m unittest discover -s tests/i3 -p test_stage6_light_native_custody_preflight.py -v
```

## Ce qui n'est **pas** vérifié et bloque toujours l'étape 6

- **Source externe** : le `source_pin`, la tête Git et la liste des cas ne sont que des *assertions de l'appelant*. La fonction contrôle leur cohérence interne, mais **ne lit pas les octets du checkout destiné à la science**, n'en atteste ni l'antériorité ni l'immuabilité et ne valide aucun artefact d'autorisation propriétaire. Un attaquant pourrait fabriquer tout l'ensemble de façon cohérente ; il ne s'agit pas d'une preuve indépendante.
- **Trace de vie** : la présence des deux empreintes terminales ne reconstitue pas la chaîne de `evidence_head`/`trace_head`, la séquence des actions ni les débits corporels exacts. Il reste à tester contre de véritables originaux d'ingénierie source-épinglés **après autorisation spécifique**.
- **Lignée** : le vérificateur ne prouve pas que les 24 descendants mutés proviennent des parents et de leurs seules données génomiques, ni que le réducteur de sélection n'a consulté aucun résultat interdit. Le prototype jouet G/S/R ne remplace pas ce lien de reproduction natif.
- **Générateur et espaces aléatoires** : aucune nouvelle graine ou plage n'est attribuée ; les exclusions ne couvrent que les intervalles connus. La séparation des 16 populations sur F0, l'indépendance statistique et la puissance restent à démontrer indépendamment.
- **Autorité** : selon les ADR-0017, 0020 et 0021, il manque une acceptation explicite de la réduction intermédiaire G/S/R par le propriétaire, un transport vivant final source-exact, une répétition *vivante* d'ingénierie autorisée et complète en Python 3.11/3.12, puis une levée scientifique indexée spécifique. Aucun de ces états n'est déduit d'une CI verte.

**Verdict de cette tranche : `NATIVE_ORIGINAL_SHAPE_PREPARED_ONLY` ; science `NOT_ISSUED`.** L'issue #1395 reste ouverte. I1 actif, I3 référence non enregistrée, P1.3 funded-v2, Stage 2.1 `HOLD_NO_VERDICT`. Aucune vie supplémentaire créée et aucun World lancé.
