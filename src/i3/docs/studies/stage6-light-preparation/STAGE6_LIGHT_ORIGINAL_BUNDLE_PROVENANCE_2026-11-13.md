# I3 · Stage-6-light : conservation et qualification du préenregistrement d'origine (13 novembre 2026)

**Décision de traçabilité : `ORIGINAL_GIT_BUNDLE_ARCHIVED`, sous réserve du test exact-head.** La filiation des commits et les empreintes des fichiers originaux sont vérifiables à partir de l'archive jointe à ce dossier. **`INDEPENDENT_PRE_EXECUTION_TIME_NOT_ATTESTED`** : aucun horodatage indépendant ne prouve que la première exécution est postérieure à la création des préenregistrements. Ces deux propositions ne doivent jamais être confondues.

**Règle scientifique inchangée :** P1.3 funded-v2 est la référence, Stage 2.1 `NOT_ISSUED/HOLD_NO_VERDICT`, I1 reste actif et I3 reste la référence de développement non enregistrée. Ce dossier n'autorise **aucun World, aucune vie, aucune cohorte, aucun indice** ni promotion du protocole Stage-6-light (toujours **DRAFT**).

## 1. Archive et étendue des preuves

- Source remise par le propriétaire dans `files131126b.zip`, le 13 novembre 2026. SHA-256 de ce ZIP reçu : `8275376771c11f91e570b0abee4ca924627946e3f04829a37646a7968759d208`. Le ZIP contient aussi une proposition de PR et des copies de rapports ; il n'est pas lui-même versé dans Git.
- **Bundle Git original conservé octet pour octet :** [`provenance/stage6-light-original-2026-11-13.bundle`](provenance/stage6-light-original-2026-11-13.bundle), SHA-256 **`df63fea5b1399924d537f91b0d0924283a9eadd53048983c3116d23c82a947d3`** (62 150 octets). Il s'agit du bundle Git v2 fourni, pas d'un patch reconstruit ni d'une nouvelle identité de commit.
- SHA-256 du patch combiné reçu, non conservé comme deuxième source d'autorité : `cb92a2a84651d227b1b8894f5b07a693566bc8cf6be99a9112b09eb61e64c7df`.
- Le bundle annonce **87 objets** et **deux prérequis** qui sont des commits de `main` : `24dadc509e3a96339def0ddb5f68c257feeabf08` et `3f3a7efcbaecdd7dcd8ad401185619b177762f60`.
- Dans un dépôt local sans ces deux prérequis, `git bundle verify` échoue normalement ; l'extraction partielle permet toutefois de contrôler les 9 objets de commit présents et leur filiation. **La réussite complète de `git bundle verify` et du fetch doit être démontrée sur un checkout historique complet**, avec le test dédié ci-dessous. Ne pas présenter l'échec dû aux prérequis absents comme un échec de l'archive, ni une vérification partielle comme un PASS complet.

## 2. Chaîne des neuf objets de commit d'origine

Le SHA Git authentifie les *octets des objets fournis*. Les dates du commit et les auteurs sont des **métadonnées déclarées par leur créateur** ; elles ne constituent pas un horodatage externe. Tous les commits cités ci-dessous sont récupérés sans changer leurs SHA ni leurs parents.

| Phase | Commit original | Parent(s) | Horodatage auteur déclaré (UTC) |
| --- | --- | --- | --- |
| Préflight P3, règle de réduction avant lecture (RP-B0) | `fdc9c0f7da478a0196bf28ef010bdc0c1e875eed` | `24dadc5` | 12/11/2026 23:36:39 |
| Code de lecture P3 | `4474d997674e52476103149bc3dd313811aa4fc7` | `fdc9c0f` | 13/11/2026 08:39:56 |
| Résultats P3 et déviation déclarée | `3992c1fb31cb757dbec5cfe02869887734426b9c` | `4474d99` | 13/11/2026 08:42:25 |
| Préflight du modèle de dérive nul | `d1437b301793858170cfc5a3e989ca44e5c79d33` | `3992c1f` | 13/11/2026 08:44:42 |
| Code du modèle nul | `f05a444d6bf57d75c7eff60993498ca8f3c7c73c` | `d1437b3` | 13/11/2026 08:46:37 |
| Résultats du modèle nul | `8deb1b9bb68d41313f686b440146796b485e45d2` | `f05a444` | 13/11/2026 08:52:05 |
| Fusion de la base `main` (deux parents) | `3a4d0390035074d38e2341220dcdb396bd79a335` | `8deb1b9`, `3f3a7ef` | 13/11/2026 17:52:33 |
| Tests d'invariance des marqueurs neutres | `b3ab3a29c8669282cc2f79f6b60a696d11f4fad6` | `3a4d039` | 13/11/2026 17:54:08 |
| Protocole Stage-6-light **DRAFT** | `8c616c101f34e5b01b0ae42b129f5b2be30d1b9c` | `b3ab3a2` | 13/11/2026 17:54:08 |

**Contrôles de contenu :** le test de provenance exige que les préflights P3 et drift-null, leurs deux implémentations et leurs deux rapports finaux, ainsi que le protocole DRAFT, soient présents **dans le commit exact qui en revendique l'origine**. Chaque blob doit égaler l'empreinte du fichier finalement intégré à `main` par la [PR #1391](https://github.com/josselin-orta-lab/individual-zero/pull/1391). Il rejette aussi un code déjà présent au commit du préflight. Il ne lance aucune étude, n'ouvre aucun monde et n'active aucun moteur.

## 3. Qualification épistémique, sans réécriture rétrospective

| Proposition | Qualification permise |
| --- | --- |
| Les préflights sont des fichiers réels liés à des commits originaux, ancêtres du code/résultats déclarés | **Intégrité Git vérifiable**, une fois le bundle importé en bac à sable ; un SHA d'objet n'est pas un cachet de temps externe |
| La règle de lecture P3 était déjà dans un commit distinct avant son commit d'implémentation | **Ordre des commits vérifiable** ; première exécution antérieure au commit du code **explicitement déclarée** dans le rapport P3 |
| Aucun calcul P3 n'a eu lieu avant le préflight | **NON ATTESTÉ** : les objets Git seuls ne documentent pas l'heure du premier calcul ni ne constituent une preuve indépendante de préenregistrement |
| La grille drift-null n'a été exécutée qu'après son code commité | **Déclaré, non attesté par une trace d'exécution indépendante** ; le graphe seul prouve l'ordre des commits, pas le début des calculs |
| Les résultats publiés sont confirmatoires ou démontrent un effet de survie de la curiosité | **NON** : P3 est descriptif, petit et inclut des marqueurs neutres ; drift-null est un modèle numérique de dimensionnement, pas une cohorte vivante |
| Le protocole Stage-6-light peut être lancé | **NON** : `DRAFT`, moratoire et autorisations spécifiques inchangés |

La lecture P3 indique explicitement : ses tests ont affiché les résultats **avant le commit de l'implémentation**, alors que la règle avait déjà été committée ; le code n'aurait pas été modifié ensuite. L'ordre des commits **ne suffit pas** pour transformer cette déclaration en constat indépendant. On conserve le résultat négatif (direction inattendue du `beta_u_eff` dans 4/4 populations) tel quel, sans le reclasser en preuve confirmatoire.

## 4. Reproduction et garde-fou permanent

Après un clone complet de `main`, lancer :

```bash
python -m unittest discover -s tests/i3 -p test_stage6_light_bundle_provenance.py -v
```

Le contrôle [`tests/i3/test_stage6_light_bundle_provenance.py`](../../../../../tests/i3/test_stage6_light_bundle_provenance.py) vérifie le SHA-256 du bundle, les prérequis, l'import local en **dépôt Git temporaire séparé**, les neuf identités et parentés, les sept blobs source/pin Git, ainsi que l'absence de code au stade préflight. Il échoue si un lien ou une empreinte dérive. Le dépôt courant, `main`, les archives de recherche et les permissions ne sont pas modifiés.

**Résultat de cette opération :** l'archive utilisateur et la chaîne Git sont désormais conservées et reproductibles. La provenance des objets peut être validée par CI ; **la provenance temporelle pré-exécution demeure non attestée**. Le statut scientifique reste `NOT_ISSUED` et la PR #1359 reste proposée/non autoritaire.
