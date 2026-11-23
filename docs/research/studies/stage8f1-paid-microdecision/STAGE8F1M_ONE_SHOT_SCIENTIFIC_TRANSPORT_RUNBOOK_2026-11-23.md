# F1M · Transport scientifique first-only, publication native et audit indépendant

**Statut : IMPLEMENTATION / HOLD_NO_SCIENTIFIC_EXPOSURE.** Ce runbook documente un transport logiciel, pas une autorisation de création de M01..M32. Il ne modifie aucun critère du préenregistrement F1M, fusionné sur main au commit d79eb0712daccab2dad0839d5c9a6eaa717eef9f. Il ne remplace ni la grille ni le protocole source.

## Périmètre source verrouillé

- Grille M01..M32, huit écologies et 32 graines 202611239701..202611239732 : Git blob `659b72c2c5894a0ba89995a23419d66b61436465`.
- Protocole adaptatif moteur/survie/Pareto : Git blob `342a6794ecd26789da82940c2d1f10e427e3979c`.
- Validation préexposition sans moteur : Git blob `007a8e1597f9ee7ab0a4a4802fd6b3a55be60af9`.
- Référence moteur I1/F1J d'origine : empreintes individuelles dans la grille préenregistrée et dans `tools/stage8f1m_one_shot_reservation.py` ; les modules Mind, World, BodyLaws et la politique F1J ne doivent pas être modifiés pour cette étude.
- Statut historique inchangé : F1L = `NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE`, Stage2 = `NOT_ISSUED/HOLD_NO_VERDICT`. Les 32 racines L de F1L sont irréversiblement consommées.

## Ordre exact des huit verrous préexposition

1. **Code et protocole** : fusionner séparément la PR d'implémentation F1M sur main après revue complète ; vérifier source/main, arbre Git exact et compilation/contrôles de sûreté. La grille et le protocole déjà fusionnés doivent conserver leurs octets et SHA Git, sans amendement après publication.
2. **Rejeu de développement, et seulement développement** : déclencher un contrôle logiciel PR sur l'arbre final, sans M01..M32 ; le test transport sur une racine DEV_M01 doit reconstruire douze reçus originaux sans jamais ouvrir la voie au constructeur scientifique.
3. **Deux familles techniques disjointes** dans chaque répétition : DEV_M01..08 (`202611239601..608`) et DEV_MR01..08 (`202611239611..618`), chacune avec 8 origines, 16 contrastes R, quatre bras et les shams. Les six jobs DEV_M prévus : `dev_m_safety_and_smoke`, `dev_m_smoke_cold_py312`, `dev_m_full_t60`, `dev_m_full_t60_cold_py312`, `dev_m_replica2_full_t60`, `dev_m_replica2_full_t60_cold_py312`. Un statut inconclusif de coût, source ou sham DOIT faire échouer le job, même si le JSON existe.
4. **Deux exécutions techniques complètes distinctes** : obtenir **deux run IDs GitHub Actions différents**, tous deux avec six jobs PASS et provenant de PR `pull_request`, chaque head Git ayant exactement le même **SHA d'arbre** que le futur main final. Le validateur fait `GET /git/commits/<rehearsal_head>` pour comparer l'arbre, et refuse l'ancien DEV_M historique si l'arbre a changé. Réutiliser un run_id, relancer le run scientifique ou mélanger des arbres n'est pas valide.
5. **GitHub ruleset F1M** : créer un nouveau ruleset GitHub Repository `F1M - Scientific one-shot protection`, `target=branch`, `enforcement=active`, inclusions **exactes** `refs/heads/i3-stage8-f1m-heldout-consumed-once`, exclusions `[]`, `bypass_actors=[]` (aucun rôle ni admin contournant) et trois interdictions `deletion`, `update`, `non_fast_forward`. Le contrôle de réservation recherche **un seul** ruleset conforme. Il doit être activé **avant** la création de la référence consommée, qui doit encore être absente (404). Ne jamais activer une exception temporaire de contournement.
6. **Releases immuables** : activer et vérifier `GET /repos/josselin-orta-lab/individual-zero/immutable-releases -> HTTP 200, enabled=true` avec le secret Actions `F1L_PROTECTION_AUDIT_TOKEN`, déjà configuré pour l'Administration en lecture seulement sur ce même dépôt. Aucune écriture administrative ni divulgation de secret. Les futures Releases RAW/COLD doivent avoir `immutable=true` et un `target_commitish` égal au commit de réservation.
7. **Autorisation distincte** : une autorisation explicite du propriétaire pour **F1M spécifiquement**, indépendante du tir F1L, doit intervenir après les contrôles ci-dessus. La PR et ce runbook ne constituent pas cette autorisation. Vérifier une dernière fois l'absence de `i3-stage8-f1m-heldout-consumed-once` et que M01..M32 n'ont jamais été nés.
8. **UN SEUL `workflow_dispatch`** : dans `.github/workflows/i3-stage8f1m-heldout-science-manual-once.yml` sur `main` saisir `approved_source_sha=<sha exact de main final>`, `consume_ack=CONSUME_F1M_32_ROOTS_NO_SCIENTIFIC_RETRY` et `rehearsal_run_ids=<id1>,<id2>` (sans espaces, deux exécutions complètes approuvées). Le job impose `GITHUB_RUN_ATTEMPT=1`, GitHub ref main, SHA exact et arbre identique. Aucun autre événement PR/push/cron ne peut déclencher ce workflow.

## Séquence scientifique de l'unique tir

Avant le premier T1 d'aucune racine, `tools.stage8f1m_one_shot_reservation --reserve` vérifie les pins, la politique immuable, le ruleset actif sans bypass, les deux DEV même arbre, l'absence du ref, puis crée le marqueur Git blob et commit, et effectue **POST /git/refs** sur le ref protégé. Une réponse réseau ambiguë échoue fermée, jamais de second essai. Un fichier `F1M_RESERVATION.json` et la vérification distante sont attendus.

Le producteur crée ensuite `F1M_RESERVATION.NATIVE_START_LOCK` en mode exclusif avec fsync **avant** la première naissance, et revalide la réservation distante avant chaque origine. Chaque Mxx effectue un vrai T1..T4 acquis/payé, deux lectures temporaires de ses propres moyennes à T5 avec décision libre et restauration pré-motrice, puis deux forks R par contenu après vrai T5, soit quatre continuations autonomes T6..T60 et quatre duplications sham. Le laboratoire ne choisit aucune commande et ne facture aucun calcul fictif.

Chaque origine écrit immédiatement douze reçus gzip déterministes (`source`, `recent_t5`, `stale_t5`, `recent_sham_t5`, quatre bras primaires, quatre shams), avec SHA256 du gzip et du JSON canonique, `O_EXCL`, fsync et checkpoint. Le jeu complet contient **384 gzip natifs, 32 checkpoints et un index scientifique explicitement NON AUDITÉ**. La rélecture canonique est un décodage des octets, **pas une deuxième exécution du moteur**. Si la source échoue normalement, les slots non exécutés sont enregistrés comme tombstones sans fabriquer des World.step.

Le transport produit `F1M_ORIGINALS_384_GZIP.tar.gz`, `F1M_CUSTODY_MANIFEST.json`, `F1M_NATIVE_INDEX.json` et `F1M_CANONICAL_READBACK.json`. Après vérification intégrale de l'archive, les copies gzip dégroupées peuvent être effacées du répertoire temporaire : leurs **octets gzip originaux** demeurent dans le tar scellé.

## RAW immuable et échec irréversible

Une étape `always()` après la réservation préserve et téléverse **tous les reçus survivants**. Si la cohorte est incomplète, elle rassemble les `original_parts` existants dans `F1M_PARTIAL_ORIGINAL_CASES.tar.gz` et consigne leurs empreintes dans `F1M_PARTIAL_ORIGINAL_MANIFEST.json`. La publication `i3-stage8f1m-t60-raw-heldout-once` cible le commit de réservation et inclut réservation, lock s'il existe, originaux ou partiels et manifestes. Une panne de CI ou réseau **n'autorise JAMAIS** un nouveau tir des mêmes racines.

Le contrôle froid ne tourne que si le job scientifique source et la RAW Release ont réussi. La tâche indépendante Python 3.12 consulte l'API GitHub, exige RAW `immutable=true`, vérifie la taille et la SHA256 de **chaque asset** de la Release, la ref et le marqueur distants, les 384 parties gzip (intégrité compressée ET décodée) et les 32 checkpoints ; elle reconstruit les 32 sources personnelles, les dépenses T5/T6, les 128 trajectoires et les 128 shams T6..T60, sans importer World/Mind/BodyLaws/producteur scientifique.

Le rapport froid sort trois statuts indépendants : **M** (commande T6 réellement changée dans ≥6 origines et ≥3 écologies), **A** (Δticks carry−zero positif dans ≥6 origines et ≥3 écologies, aucune perte sur 64 comparaisons) et **B** (dominance Pareto cinq réserves secondaire, jamais preuve de survie). Une source non financée, un sham non neutre ou un coût T5/T6 non apparié donne le verdict global inconclusif préfixé. L'absence d'effet moteur n'empêche pas l'analyse adaptative A si les gates sont valides.

Le dernier job publie `i3-stage8f1m-t60-cold-heldout-once`, avec le rapport indépendant et les empreintes, **ou** `F1M_FINAL_STATUS.json` explicitant `INCONCLUSIVE_COLD_AUDIT_MISSING_NO_RETRY` lorsque le contrôle froid ne peut pas être émis. Il ne modifie aucune vie, aucune interprétation historique ni Stage2.

## Arrêts et sécurité

- Avant claim : `HOLD_NO_EXPOSURE` si source SHA, deux répétitions, GitHub ruleset exact, secret Admin read, Releases immuables, ref absent ou autorisation propre manquent. Aucun `World.step` scientifique.
- Après claim, avant premier T1 : le ref reste consommé même si vérification distante/CI/API échoue. Préserver reçu et preuve partielle disponibles ; **jamais de nouveau run scientifique**.
- Pendant T1..T60 ou archivage : préserver les gzip écrits et pointer le verdict sur une inconclusion. Jamais remplacer une graine, relancer une source, corriger rétroactivement un coût, retoucher les scénarios ou restaurer artificiellement les états naturels.
- Après audit froid : conserver F1L négatif et Stage2 NOT_ISSUED/HOLD_NO_VERDICT. Une commande différente, un score supérieur ou une amélioration locale de réserve ne vaut pas un avantage adaptatif généralisé.

## Provenance des fichiers

Protocole préenregistré : `STAGE8F1M_INDEPENDENT_RESIDUAL_MOTOR_ADAPTIVE_PREEXPOSURE_2026-11-23.md`; grille : `STAGE8F1M_INDEPENDENT_RESIDUAL_MOTOR_ADAPTIVE_GRID_2026-11-23.json`. Code : `tools/stage8f1m_one_shot_reservation.py`, `tools/stage8f1m_scientific_native.py`, `tools/stage8f1m_one_shot_evidence.py`, `tools/stage8f1m_one_shot_cold_entry.py`, `tools/stage8f1m_independent_scientific_cold.py`, `tools/stage8f1m_one_shot_publish_status.py`, et workflow `i3-stage8f1m-heldout-science-manual-once.yml`. Contrôle logiciel préexposition : `tests/test_stage8f1m_one_shot_transport.py`. DEV de contrat : `tests/test_stage8f1m_science_transport_dev_contract.py`, entièrement disjoint de M01..M32.

**Ce texte n'est pas un nouveau préenregistrement et n'altère pas les seuils figés en PR #1518.**
