# Stage 12 / Issue #110 : A2.17b, indice proximal de collecte et résultat alimentaire distal

**14 octobre 2026. Verdict Stage12 : PARTIAL.** Préenregistrement `7b2548647cc6eb0a662482e17fc82c5d33d69789` réalisé avant le code. Base `main ecfbf96b90aa2195dec4806815f2f1cc24d28143`. Aucune politique cognitive ni spécification normative v1.3.1 modifiée.

## Expérience et limites

Première [CI A2.17b #38633424409](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38633424409) : **SUCCESS Python 3.11 ET 3.12**, **40 mondes physiques indépendants** (5 conditions ×8 seeds 81–88), chaque monde ayant réellement appliqué une transition `WorldBody.apply`. Protocole purement externe de comparaison de `GoalAgencyService` inchangé avec une sonde candidate **non branchée** dans I0. Les interventions `set_body` et `set_action_failure_schedule` sont exécutées physiquement par le laboratoire; leurs étiquettes sont réservées au rapport et ne sont pas données au service. Le test n'est **ni une vie cognitive autonome ni une campagne 600 pas**, et n'évalue pas une étiologie causale universelle.

| Condition physique | Vies | Jugement réel `GoalAgencyService` | Sonde « self proximal » | Corps : hausse de `food` |
| --- | ---: | --- | ---: | ---: |
| Ressource présente, collecte réussie | 8 | `unknown` 8/8 | **8** | 0 |
| Ressource absente | 8 | `unknown` 8/8 | 0 | 0 |
| Collecte physiquement empêchée | 8 | `unknown` 8/8 | 0 | 0 |
| Échec de collecte puis **gain corporel extérieur** | 8 | `unknown` 8/8 | **0** | **8** |
| Collecte réussie puis **perte corporelle extérieure** | 8 | `unknown` 8/8 | **8** | 0 |
| **Total** | **40** | **40 unknown** | **16 candidats proximaux** | **8 gains indépendants** |

Le candidat n'analyse que l'engagement `collecter`, l'espèce ciblée, la **capture avant/après de l'inventaire** et la permanence dans la même cellule. Il n'exploite ni l'étiologie physique cachée ni l'information `WorldBody.effects`. Cette distinction évite que le gain corporel extérieur fasse artificiellement reconnaître l'agence de la collecte. Inversement, une perte alimentaire extérieure n'annule pas la preuve proximale d'un inventaire augmenté.

## Interprétation scientifique, restrictions

Le résultat établit uniquement qu'**une différence d'inventaire effectivement perçue constitue un indice proximal plus discriminant qu'une variation de `body.food`** dans cette matrice physique. Il ne valide **pas** la responsabilité causale subjective de l'objectif alimentaire distal. Le monde MVP actuel ne dispose pas d'une intervention externe directe sur l'inventaire du corps : l'expérience ne réfute donc pas le risque d'un faux `self` si un tiers accroissait l'inventaire au même pas sans contribution de la commande.

Le jugement actuel `unknown` de `GoalAgencyService` est resté intact dans tous les cas et constitue un garde-fou prudent au regard du contrat d'agence de l'objectif. **Aucun des 16 candidats `self_proximal_candidate` ne devient une paire GA-06 admissible**. Il ne serait pas défendable d'en augmenter artificiellement `verified_successes/failures`, de changer `2+2/12`, ni de modifier Stage9/DC-05, sécurité, UC ou Oracle.

## C1–C8

- C1 **PARTIAL** : candidat proximal discriminant sur 40 essais hors-ligne, aucune calibration de l'individu.
- C2 **PASS borné** pour la séparation d'un indice d'inventaire et d'une variation alimentaire corporelle extérieure; aucune causalité générale démontrée.
- C3, C4, C5, C6 **INCONCLUSIVE** pour la diversité, la compétence alimentaire autonome, P-48 et stabilité longue.
- C7 **PASS borné** : huit seeds de mondes et reproductions Python 3.11/3.12, artefacts identifiables.
- C8 **PASS borné** : aucune modification du service de première personne, de l'Oracle ou de la norme.

**GLOBAL Stage12 PARTIAL, issue #110 OPEN, réception opérateur non réalisée.**

## Suite conditionnelle

Avant toute expérimentation de modification cognitive ON/OFF, une décision de **portée normative** est nécessaire : faut-il distinguer explicitement une agency **proximale** sur l'action de collecte et une agency **distale** sur le résultat de l'objectif alimentaire, ou garder le seul jugement actuel attaché au critère d'objectif ? Cette campagne n'autorise pas à utiliser un cue proximal de collecte comme preuve de causalité sur `food`. Une éventuelle proposition doit être examinée hors de v1.3.1, puis confrontée à des perturbations d'inventaire externes et à des vies réellement autonomes avant toute validation Stage12.
