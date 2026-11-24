# Stage8-F1M · Clôture scientifique T60 et diagnostic archivistique distinct
**Date : 24 novembre 2026. Statut : `COLD_AUDITED_FIRST_ONLY` ; verdict confirmatoire négatif.**

Ce document est rédigé **après** l'exposition scientifique F1M. Il documente le rapport froid authentique sans réécrire ni la grille, ni les estimands, ni les seuils de succès préenregistrés dans [PR #1518](https://github.com/josselin-orta-lab/individual-zero/pull/1518). Il ne lance aucune vie et ne touche ni à la référence Git consommée, ni aux Releases immuables, ni au moteur P1.3. Les nouvelles lectures du médiateur à la section 4 sont explicitement **post-hoc exploratoires** et non un nouveau verdict.

## 1 · Provenance fixée et unique

- [Tir original unique GitHub Actions #45500772324](https://github.com/josselin-orta-lab/individual-zero/actions/runs/45500772324), événement `workflow_dispatch`, `run_attempt=1`, **3/3 jobs SUCCESS** (source native, froid Python3.12 indépendant, Release finale). Source de l'exécution `a0d063402cad87d6dd255e2f842586b8f8f95267`, Git tree `36d508a69c78510c0dc6dbd5cabafc1169ca8a55`.
- Référence irréversiblement consommée **avant la première naissance** : `refs/heads/i3-stage8-f1m-heldout-consumed-once`, commit `f6e213ca197c432b03907c3d8999ddf10bcac809`, marker `F1M_T60_CONSUMED_BEFORE_EXPOSURE.json` Git blob `3e961f4ac217e67960f50d29f6b0655dd43e8ddd`. Aucun rerun permis.
- [Release RAW F1M immuable](https://github.com/josselin-orta-lab/individual-zero/releases/tag/i3-stage8f1m-t60-raw-heldout-once), `immutable=true`, cible `f6e213ca...`. **384 gzip originaux** (12 parties × 32 racines), tar original `F1M_ORIGINALS_384_GZIP.tar.gz`, **404 861 167 octets**, SHA-256 **`4e4888d00d5494f071d84d469e26f62d497dba8ce390bbe01101607a018992bc`**. Manifeste RAW SHA-256 `47ad255aaac32756a1777cbecfe4d3356b58beee4b7e4b1aaf403612a961a4af`. L'archive ZIP Actions SHA-256 `5421f48132ea2839114baa97199acdaa3cfe2f581610e733000308f99d5e6324`.
- [Release COLD F1M immuable](https://github.com/josselin-orta-lab/individual-zero/releases/tag/i3-stage8f1m-t60-cold-heldout-once), `immutable=true`, même cible. Rapport `F1M_INDEPENDENT_COLD_T60.json` **103 579 octets**, SHA-256 **`85cc44b84075321f96114b14e8d1c6b52b592e0c44e8cb40180b568e9c1c8791`**. Statut `F1M_FINAL_STATUS.json` SHA-256 **`a85bf512a5f2471621b28c9f27b2f0618d31fc8c478191fb262e99337a2e4984`**. Les octets des deux rapports ont été relus depuis les artefacts Actions et hachés une seconde fois.
- Source initiale préenregistrée de la cohorte : [grille](STAGE8F1M_INDEPENDENT_RESIDUAL_MOTOR_ADAPTIVE_GRID_2026-11-23.json) Git blob `659b72c2c5894a0ba89995a23419d66b61436465` ; [protocole](STAGE8F1M_INDEPENDENT_RESIDUAL_MOTOR_ADAPTIVE_PREEXPOSURE_2026-11-23.md) Git blob `342a6794ecd26789da82940c2d1f10e427e3979c`. Les 32 origines M01..M32 appartiennent à huit écologies (quatre racines par écologie), avec deux comparaisons corrélées par origine.

L'ancien run #45500243266 avait échoué **avant** réservation, par une tabulation initiale dans le champ `approved_source_sha`. Aucune vie ni référence consommée n'en était sortie. L'unique run science ayant effectivement réservé et créé les vies est **#45500772324**.

## 2 · Validité du tir original et de l'audit indépendant

| Contrôle froid indépendant | Mesure | État |
|---|---:|---|
| Sources T1..T4 authentiques, apprentissage et travail payés | 32/32 | PASS |
| Coûts décisionnels réels appariés à T5 (contenu récent/ancien) | 32/32 | PASS |
| Coûts décisionnels réels appariés à T6 (accumulateur conservé/neutralisé) | 64/64 | PASS |
| Shams T5 neutres, shams de toutes les continuations neutres | 32/32 origines et 128 shams R | PASS |
| Continuations complètes et auditables | 128/128 bras + 128/128 shams R | PASS |
| Gzip originaux, SHA compressé et SHA décodé, manifeste | 384/384 | PASS |
| Transitions `World.step` reconstruites depuis les reçus | 14 304 | PASS |
| Tours cognitifs substantiels F1J reconstruits | 70 752 | PASS |
| Écologies préenregistrées couvertes | 8/8 | PASS |

Le compte **14 304 = 32 × (4 sources + 3 décisions T5 comprenant le sham + 8 × 55 continuations)** atteint la longueur complète prévue. Le froid ne réexécute ni `World` ni `Mind`; il relit les reçus natifs et les comparateurs indépendants. Le budget cognitif et corporel n'a subi aucun padding rétroactif. Le tir est **conclusif** pour ses règles de test, même si les effets sont nuls.

## 3 · Trois verdicts PRÉENREGISTRÉS, séparés

| Hypothèse | Préenregistrement | Résultat froid | Verdict officiel |
|---|---|---|---|
| **M : moteur natif T6** | ≥6 racines distinctes dans ≥3 écologies avec ≥6 paires de commandes `(action,param)` réellement modifiées | **0/64 paires ; 0/32 racines ; 0/8 écologies** ; gagnant cognitif T6 différent **0/64** | `NO_REPRODUCIBLE_LOCAL_T6_RESIDUAL_MOTOR_EFFECT` |
| **A : persistance T6..T60** | ≥6 racines distinctes avec Δticks>0 dans ≥3 écologies et aucune perte sur les 64 paires | **0/64 gains ; 0/64 pertes** | `NO_REPRODUCIBLE_LOCAL_T60_SURVIVAL_ADVANTAGE` |
| **B : cinq réserves terminales** | Dominance Pareto positive secondaire, sans substituer un avantage de réserve à un gain de survie | **0/64 dominances carry ; 0/64 dominances zero ; 64/64 vecteurs Δcorps=(0,0,0,0,0)** | `NO_REPRODUCIBLE_LOCAL_BODY_PARETO_SUPPORT` |

Ces 64 contrastes sont **appariés deux par racine** ; ils ne constituent pas 64 individus indépendants. Aucune sélection de sous-groupe après observation n'intervient dans ces verdicts. Aucune preuve d'avantage adaptatif n'a été établie dans cette campagne, et l'effet moteur vu dans le seul pilote DEV_M n'a pas été reproduit dans la cohorte tenue en réserve F1M. **F1L reste négatif** : `NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE` ; **Stage2 reste** `NOT_ISSUED/HOLD_NO_VERDICT`. Aucun résultat historique n'est réinterprété.

## 4 · Diagnostic POST-HOC, distinct du protocole

Une nouvelle lecture **archivale seulement** a examiné les quatre continuations R originales par racine depuis le tar RAW immutable (128 branches, pas les shams), après avoir contrôlé la SHA-256 de chaque gzip consulté contre le manifeste original, puis le SHA-256 des 128 contenus décodés. Le ZIP Actions et le tar imbriqué ont également été hachés indépendamment et ont exactement les empreintes de la Release RAW. **Aucun nouveau `World.step`, aucun recalcul de la politique ni aucune naissance.**

Pour chaque paire racine × contenu (64), l'état `Mind.acc` véritablement présent juste après T5 est comparé à l'état `zero`. L'efficacité effective du traitement se distingue des résultats motrices :

| Propriété archivale de l'intervention | Constat |
|---|---:|
| Accumulateur effectivement non nul, puis modifié par `zero` | **40/64 paires** |
| Accumulateur déjà nul, intervention sans effet | **24/64 paires** |
| Racines avec au moins un R non nul | **20/32** |
| Écologies contenant au moins un R non nul | **8/8** |
| Séquences natives des **55 moteurs T6..T60** exactement égales carry/zero | **64/64 paires** |
| Premier moteur différent après T6 | **0/64 paires** |
| Corps terminaux et ticks finaux identiques | **64/64 paires** |

Répartition exploratoire, **sans filtrage** des paires inactives et sans statut de sous-groupe confirmatoire :

| Écologie (eau × renouvellement × aliment) | Paires R non nulles / 8 | Racines R non nulles / 4 | Changements T6 moteurs |
|---|---:|---:|---:|
| Adjacente × finie × sûre | 2 | 1 | 0 |
| Adjacente × finie × amère | 2 | 1 | 0 |
| Adjacente × renouvelée × sûre | 2 | 1 | 0 |
| Adjacente × renouvelée × amère | 2 | 1 | 0 |
| Diagonale × finie × sûre | 8 | 4 | 0 |
| Diagonale × finie × amère | 8 | 4 | 0 |
| Diagonale × renouvelée × sûre | 8 | 4 | 0 |
| Diagonale × renouvelée × amère | 8 | 4 | 0 |

Parmi les paires R effectivement manipulées, la somme absolue des accumulateurs pré-T6 non nuls varie de **0,1748** à **2,7910** (médiane **1,4275**). La neutralisation du résidu est donc réelle et diversement distribuée, **mais aucune commande native n'est modifiée même plus tard** dans les continuations archivées. Inversement, 24 paires sans résidu relèvent d'une intervention triviale et ne doivent pas être interprétées comme un test efficace du médiateur.

Le fait que les mêmes individus aient librement exécuté différentes catégories de commandes entre écologies (boire, dormir, attendre, se déplacer) ne démontre ni l'efficacité du contenu de mémoire ni celle de la persistance résiduelle. Le **constat post-hoc plus précis** est : supprimer un état R non nul a été sans conséquence motrice visible dans les 40 comparaisons observées, mais il n'est **pas** établi que la persistance soit sans importance dans d'autres WorldSpecs, états physiologiques, génotypes ou séquences d'options. Aucun nouveau critère d'avantage n'est créé.

Diagnostic archivistique à **64 paires** et empreintes individuelles des 128 gzip originaux consultés : JSON local `F1M_ARCHIVED_POSTHOC_MEDIATOR_DIAGNOSTIC.json`, SHA-256 **`456e6b4256b2cd892a6df74fa36e96853313fd30a631b97db3c5d18a35c0c575`**. Les 384 originaux faisant autorité sont ceux de la Release RAW, pas ce diagnostic postérieur.

## 5 · Conclusions, limites et suite sans exposition

**Verdict scientifique clos : `F1M_COMPLETE_SEPARATE_SCIENTIFIC_VERDICTS` ; M négatif, A négatif, B négatif.** Il n'y a ni échec de financement, ni anomalie de source, ni divergence de sham à invoquer pour sauver l'hypothèse. Les contre-exemples DEV_M restent des observations de développement, pas une réplication scientifique tenue en réserve. Les seuils préenregistrés, négatifs et explicites, font foi.

La prochaine question légitime est **mécanistique et rétrospective** : dans les 40 contrastes dont le `Mind.acc` portait un résidu non nul, examiner uniquement les *witnesses* natifs déjà enregistrés : mêmes clés d'options entre T5 et T6, normalisation de l'évidence, seuil de compétition, marge entre gagnants et actions admissibles, puis pourquoi aucune bifurcation motrice n'apparaît de T6 à T60. Toute hypothèse issue de cette exploration doit être déclarée post-hoc ; si elle motive une nouvelle expérience, celle-ci exigera **une nouvelle allocation indépendante et son propre préenregistrement avant exposition**.

**Aucune nouvelle vie, aucun rerun, aucune modification de la branche consommée ou des Releases F1M/F1L.** Consignation officielle : [issue scientifique #1516, verdict froid](https://github.com/josselin-orta-lab/individual-zero/issues/1516#issuecomment-7146677615).
