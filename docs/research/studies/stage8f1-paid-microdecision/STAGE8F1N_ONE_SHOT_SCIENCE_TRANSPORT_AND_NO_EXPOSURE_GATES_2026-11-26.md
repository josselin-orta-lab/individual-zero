# Stage8-F1N | Transport scientifique create-only et contrôle indépendant (aucune exposition)

**26 novembre 2026 | transport logiciel pré-tir, aucun N01..N48 créé.** Ce texte décrit le transport implémenté **après** le préenregistrement F1N des 25 novembre et les deux cohortes DEV_N de validation. Il **ne modifie pas** la grille Git blob `c522d092cb7c1777ebb0f56c4162f61948b35653`, le protocole Git blob `ff07a8db807bee15277052ea71e1e76321286ab9`, le F1M/F1L consommé, ni les critères de succès M/A/B.

## I. Source et actes autorisés

- Réserve **exacte** : 48 origines `N01..N48`, graines `202611259801..202611259848`, huit écologies littérales de six racines, même génotype `midpoint()`. **336 originaux gzip** si complets : sept par racine, dans l'ordre `source_t1_t4`, `self_paid_t5`, `self_paid_t5_sham`, `margin_t6_t60`, `margin_t6_t60_sham`, `masked_t6_t60`, `masked_t6_t60_sham`.
- Deux contrastes : **marge personnelle T5 réellement calculée, enregistrée et débitée**, et **masquage local de son amplitude seulement** à la compétition T6 ; les deux branches paient le même véritable accès mémoire et les mêmes cycles substantifs. `κ=0.5` fixé antérieurement. Les moteurs T6 et T7..T60 sont toujours choisis par l'individu et exécutés physiquement, jamais forcés.
- **Deux répétitions DEV_N indépendantes en termes de runs Actions, chacune contenant les cohortes DEV_NA et DEV_NB disjointes**, toutes les six jobs réussies et vérifiées froidement sous **le même arbre Git source** que le futur code scientifique approuvé. Le tir scientifique est interdit à défaut de ces **deux ID de runs distincts**. Les 16 racines DEV ne sont pas les racines scientifiques. Un seul run, même s'il contient deux cohortes, **ne suffit pas** au gate `F1N_REHEARSAL_RUN_IDS`.
- Le workflow scientifique `i3-stage8f1n-heldout-science-manual-once.yml` possède **uniquement** `workflow_dispatch` sur `main` avec `run_attempt=1`. Une PR, un push, un cron, un `Re-run jobs` ou un SHA / accusé différent ne peut créer la réservation. Les tests ne créent jamais de vraie réserve.

## II. G0 / G1, la barrière avant le premier `World.step`

`tools/stage8f1n_one_shot_reservation.py` est un module stdlib **sans imports du moteur**. Il vérifie les empreintes Git de tous les fichiers source, le préenregistrement, le SHA source de `main` et du checkout, les deux répétitions DEV complètes sur le même arbre, les Release tags scientifiques RAW/COLD **absents** et la référence F1N **absente** (`HTTP 404`, tout autre code échoue). Il exige une politique GitHub Releases **`immutable-releases.enabled=true`** par GET Administration:read au moyen du secret déjà utilisé `F1L_PROTECTION_AUDIT_TOKEN`, jamais un privilège d'écriture administratif.

Le ruleset **F1N, À CONFIGURER ET À AUDITER avant science**, doit être **un ruleset de dépôt unique et actif**, exact `refs/heads/i3-stage8-f1n-heldout-consumed-once`, `exclude=[]`, `bypass_actors=[]`, et règles **`deletion`, `update`, `non_fast_forward`**. Ne pas ajouter `creation` : la seule création doit être atomique. La présence des rulesets F1L/F1M **ne protège pas** la ref F1N. Le fait que le code passe ses tests ne vaut pas preuve administrative que ce ruleset est activé.

**Aucun `World.step` F1N avant** le succès create-only `POST /git/refs`, après création du blob du manifeste, de l'arbre et du commit fils du SHA approuvé ; l'accusé de consommation et le premier verrou natif sont publiés sous SHA-256. Si la création GitHub est ambiguë ou si le transport échoue après la réservation, **ne jamais réessayer** cette allocation : statut inconclusif et archivage des preuves partielles.

Le futur propriétaire devra explicitement autoriser **un nouveau tir F1N**, distinct du F1M, après que l'implémentation, les protections GitHub et les deux runs DEV aient été examinés. Ce document et sa PR **ne sont pas cette autorisation**.

## III. G2, conservation irréversible des preuves physiques

`tools/stage8f1n_scientific_native.py` vérifie la réservation distante **avant chaque nouvelle racine**, et construit son monde uniquement depuis la grille F1N figée. `tools/stage8f1n_one_shot_evidence.py` écrit chaque gzip immédiatement en `open('xb')`, avec fsync et SHA-256 des octets gzip **et** du JSON canonique, puis un checkpoint incrémental après chaque racine. Aucun résultat agrégé ne peut remplacer ces témoins.

Une fois les 48 racines consommées, le transport compose **`F1N_ORIGINALS_336_GZIP.tar.gz`**, son index, son readback canonique et un manifeste SHA-256. La Release RAW créée à partir du commit de réservation est marquée **immutable**, avec aussi le reçu et le verrou natif. En cas d'erreur avant la clôture d'une racine, les fichiers partiels déjà créés sont préservés avec une archive de survie **sans produire de vie supplémentaire**. Même si la Release ou la CI tombe en panne, aucune seconde exécution scientifique n'est admise.

## IV. G3 / G4 / G5, audit froid indépendant

Le job Python3.12 `tools/stage8f1n_one_shot_cold_entry.py` travaille **exclusivement sur les octets du producteur originel**, vérifie la Release RAW immuable et les empreintes GitHub pour chaque asset, extrait les **336 gzip** par streaming et contrôle leurs empreintes décodées, les 48 checkpoints, la chronologie, les écritures T5 réellement facturées et les deux lectures T6 financées. L'auditeur `tools/stage8f1n_independent_scientific_cold.py` ne peut importer ni `Mind`, ni `World`, ni le producteur scientifique.

Il reconstruit les 48 sources personnelles, les cinq réserves, le coût réel de toutes les compétitions F1J et mémoires, les 48 shams T5 et les 96 shams des continuations. Toute divergence de facturation T6, de sham, de témoignage de seuil, de commande admise ou de mouvement réellement exécuté doit être conservée comme **inconclusion**, jamais réparée rétroactivement.

L'auditeur scelle **trois résultats séparés**, selon les seuils du préenregistrement :

- **M** : au moins huit origines distinctes dans trois écologies avec une vraie commande `(action,param)` T6 modifiée. Une marge/activation interne différente seule ne compte pas.
- **A** : au moins huit origines gagnant de vrais ticks T6..T60 dans trois écologies et **zéro perte** dans les 48 paires. A n'est pas déduit de M.
- **B, secondaire** : tous les ticks égaux et corps comparables, au moins douze dominances Pareto corporelles strictes dans trois écologies et aucune dominance inverse ; jamais une promotion d'avantage de survie.

La publication COLD doit refléter le succès froid authentique **ou un statut `INCONCLUSIVE_*` sans retry**. Elle ne peut ni modifier F1L/F1M ni promouvoir Stage2 : `NOT_ISSUED/HOLD_NO_VERDICT`.

## V. Modes d'audit sans naissance

Avant le tir scientifique, sur un checkout du **même arbre source** :

```bash
PYTHONPATH=src:. python -m tools.stage8f1n_prereg_static_guard
PYTHONPATH=src:. python -m tools.stage8f1n_one_shot_reservation --readonly-pins
PYTHONPATH=src:. python -m unittest -v tests.test_stage8f1n_one_shot_transport
# Sur GitHub Actions uniquement avec accès lecture aux paramètres distants :
PYTHONPATH=. python -m tools.stage8f1n_one_shot_reservation --readonly-admin
```

Le dernier contrôle renverra un **HOLD avant toute naissance** si le ruleset n'existe pas encore. Ne jamais appeler `--reserve` pour un test ; l'acte de réservation est précisément la **consommation définitive** des 48 origines.

Le workflow manuel de science, lorsqu'il sera un jour expressément autorisé, exigera les champs **`approved_source_sha`** (SHA exact de `main` et du checkout du run), **`consume_ack=CONSUME_F1N_48_ROOTS_NO_SCIENTIFIC_RETRY`** et **`rehearsal_run_ids=RUN_ID_1,RUN_ID_2`** (deux runs DEV indépendants sur le même tree SHA). Une fois le claim réussi, échec ou succès, **ne jamais utiliser « Re-run jobs » ou un second dispatch pour F1N**.

**État à l'issue du développement logiciel :** `F1N_SCIENCE_TRANSPORT_SOURCE_READY_HOLD_ADMIN_AND_OWNER_AUTHORIZATION_NO_EXPOSURE`, sous réserve des vérifications finales GitHub des deux runs complets sur le **tree scientifique final**.
