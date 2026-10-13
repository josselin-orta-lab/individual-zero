# Individual Zero, issue #133 : vieillissement P6-B6 à 600 pas (résultats vérifiés)

**Date : 13 octobre 2026. Statut scientifique : hypothèse de stabilité locale réfutée dans les deux mondes étudiés.**

## Provenance et limites de preuve

- Protocole prospectif gelé avant implémentation : `docs/research/stage10-issue133-horizon600-prereg-2026-10-13.fr.md`, commit `9a5afa59f9b417ca9ee2d38230f65d38cb3bca9d`.
- Source unique : `12a46813940758439515ed3478f04f403dc48020`, branche `exp/stage10-priced-multipass-sleep-20261013`, PR #139.
- [GitHub Actions Stage12 #38357752852](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38357752852) et [CI rapide #38357752862](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38357752862) : SUCCESS.
- Archives non altérées : `11794093482` (Python 3.11) et `11794268823` (Python 3.12), chacune avec deux journaux canoniques, WAL, index, états finaux et traces des UC. Les journaux canoniques/WAL de chaque monde sont identiques octet pour octet entre les interpréteurs : **reproductibilité logicielle**, pas quatre graines statistiques indépendantes.
- Tous les bras ici utilisent P6-B6, `w_C = 0`, `p_cons_min = 0`, `step_slot_uc = 100`, `period_capacity_uc = 600` et `episode_scan = 1`. Durée maximale 600 transitions réellement appliquées. Aucun paramètre n'a été ajusté en fonction du résultat.

## Audit indépendant hors runtime

Une lecture séparée des archives ZIP, n'important ni I0, ni Oracle, ni Bench, a recalculé les octets canoniques (UTF-8 et identifiants NFC), le SHA-256 chaîné pour **tous les enregistrements**, l'unicité des identifiants, la coïncidence exacte WAL/export, l'intégrité du head, la chronologie des 600 clôtures de pas, l'absence de transition après mort, la sélection de références closes avant le cut, les **six passes ordonnées** précédant chaque activation h, l'unicité des épisodes consolidés et au plus une publication h/pas. Les séries de comptage ont été reconstruites depuis les événements `episode_closed`, `stage10_consolidation_version_activated` et les reçus UC par pas. Aucun échec de ces contrats n'a été observé.

| Mesure, par monde (une vie de 600 pas) | Référence non entraînée | Eau / équipement prénatal entraîné |
| --- | ---: | ---: |
| Pas physiques et fin de vie | 600, `experiment_stopped` | 600, `experiment_stopped` |
| Episodes fermés / éligibles au dernier pas | 299 / 299 | 299 / 299 |
| Références dans h | **242** | **238** |
| Épisodes encore en attente | **57** | **61** |
| Âge moyen du backlog, pas | 58 | 63 |
| P90 d'âge du backlog, pas | 102,8 | 111 |
| Publications h / checkpoints | 51 / 306 | 44 / 264 |
| UC totales payées P-42 | 10 827 | 9 791 |
| UC de scan, avec rescans | **6 733 (62,2 %)** | **5 872 (60,0 %)** |
| UC hors scan | 4 094 | 3 919 |
| UC/épisode consolidé | 44,74 | 41,14 |
| Pas comportant des UC de consolidation | 123 | 117 |
| Nombre d'entrées en sommeil | 123 | 117 |
| Maximum UC / pas et UC / période, observé | 100 / 100 | 100 / 100 |
| Reports explicites | 75 | 76 |
| Dormir, se déplacer, boire | 313, 287, 0 | 300, 299, 1 |

L'absence de dépassement est démontrée **dans les pas observés** ; elle n'est pas une preuve formelle que toutes les configurations futures sont sûres. Le monde entraîné a bu une fois, mais ces trajectoires ne prouvent pas l'absence de privation d'autres besoins vitaux.

## Pentes du backlog : test préenregistré

| Fenêtre de pas | Episodes éligibles nouveaux, référence / eau | Consolidés référence / eau | Δ backlog référence / eau |
| --- | --- | --- | --- |
| 1–200 | 99 / 100 | 82 / 77 | +17 / +23 |
| 201–400 | 100 / 100 | 88 / 89 | +12 / +11 |
| **401–600** | **100 / 99** | **72 / 72** | **+28 / +27** |
| **521–600** | **40 / 39** | **36 / 42** | **+4 / −3** |

Le critère préenregistré exigeait une pente de backlog non positive **sur les 200 ET les 80 derniers pas**. Il échoue dans les deux mondes. La petite diminution sur les 80 derniers pas du monde avec eau ne compense pas la hausse de 27 sur 200 pas. **Ne pas qualifier P6-B6 de « stable » sur 600 pas.**

## Diagnostic causal prudent

Au-delà de la limite de nombre de passes corrigée par P6-B6, le prix des scans est devenu dominant. La sélection incrémentale facture toujours chaque épisode d'un inventaire complet (consolidé ou non), à chaque sélection suivante ; la tranche en Python évite de recopier toute la collection, mais n'en abaisse **pas** le prix P-42. Plus de 60 % des UC P-42 sont désormais absorbées par des scans, et 45 / 39 reports `incremental_scan_out_of_uc` sont explicitement enregistrés.

Parmi les facteurs restant plausibles : hausse linéaire des rescans O(N), contraintes de 100 UC par créneau physique et nombre fini de vrais créneaux sommeil, prix et cadence de chaque passe/lot. Les résultats démontrent une **insuffisance de débit effective**, mais n'attribuent pas expérimentalement *toute* la croissance de la file à un unique facteur. Aucun supplément d'UC ni changement de pression de sommeil n'est autorisé.

**Prochaine expérience ciblée à préenregistrer avant son développement** : index persistant des seuls candidats encore non consolidés, uniquement avec lecture initiale facturée, resélection/rang facturés, maintenance des suppressions facturée, cut gelé, provenance strictement autobiographique, snapshots causaux et priorité identique au sélecteur original. Commencer par une preuve de sélection équivalente et de budget sous des flux artificiels bornés, puis un test de vie avec mêmes profils et graines. Si les opérations de maintenance ou les structures causales imposent de modifier la norme, demander une décision opérateur explicite au lieu de contourner P-42.

## Décision

- **Logiciel multipasse et batch** : conforme dans la campagne, avec 600 pas par monde et reproduction 3.11/3.12.
- **Équilibre durable** : NON VALIDÉ, hypothèse locale réfutée par +28/+27 backlog durant les 200 derniers pas.
- **Qualité de l'apprentissage, monde held-out, calibration de besoins vitaux, M11 crash-atomicité** : non attestés par ce protocole.
- **Issue #133** : reste OPEN. **PR #139** : ne pas fusionner sur la seule base des succès CI ; conserver `w_C = 0` et la décision opérateur sur l'acceptation finale.
