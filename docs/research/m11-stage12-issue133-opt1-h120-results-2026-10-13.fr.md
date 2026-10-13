# Issue #133 : résultats comparatifs OPT1-H120 sur M11 / Stage12

**Date : 13 octobre 2026.** Préenregistrement antérieur à l'exécution : `docs/research/m11-stage12-issue133-opt1-h120-prereg-2026-10-13.fr.md`, gelé avant le workflow. Code H120 optimisé figé : `082e7008d62b12fc99b2075a29533d1016e1d5db`. [GitHub Actions #38401921250](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38401921250) : deux jobs Python 3.11 et 3.12 **SUCCESS**. Artefacts bruts : `11816246706` (3.11), `11815976776` (3.12).

## Observations de sortie produites par les runners

| Mesure | Baseline 3.11 | OPT1 3.11 | Baseline 3.12 | OPT1 3.12 |
| --- | ---: | ---: | ---: | ---: |
| Pas physiques | 120 | 120 | 120 | 120 |
| Durée jusqu'au checkpoint, s | 224,60 | **141,98** | 338,38 | **135,05** |
| Variation du temps | n/a | **−36,8 %** | n/a | **−60,1 %** |
| Épisodes créés | 59 | 59 (selon référence et comportement conservé; compter directement dans archive avant audit final) | 59 | 59 (idem) |
| Références publiées dans h | 57 | 57 | 57 | 57 |
| Backlog H120 | 2 | 2 (sous réserve audit individuel des événements H120) | 2 | 2 (idem) |
| Publications h | 12 | 12 | 12 | 12 |
| Six-pass checkpoints | 72 | 72 | 72 | 72 |
| Reçus maintenance / retrait | 12 / 12 | 12 / 12 | 12 / 12 | 12 / 12 |
| Occurrences du journal H120 | 14397 | **14397** | 14397 | **14397** |
| Taille SQLite, octets | 17956864 | **17956864** | 17956864 | **17956864** |
| Reprise froide au pas suivant | 121 | **121** | 121 | **121** |

**SHA-256 du head causal H120, référence et OPT1, les deux Python :** `8b73d539a39fa6b7bf7583652a5f51e4a0427f9c0d203f015190d4641a648f82`.

**SHA-256 de l'export canonique H120, référence et OPT1 :** `fa94b0312cc41ae07775fa8590bf5d26553ed34e243eee0db35f96d17e00719c`.

Les sorties JSON des deux jobs OPT1 indiquent `generation=120`, `pending_intent=false`, `may_recover_current=true`, `lifecycle_at_checkpoint=active`, `cold_resumed_next_generation=121`, `w_c=0`, P-42 plafonds 100 et 600, `oracle_used=false`, `bench_used=false`.

## Interprétation et prudence

Ces données viennent des résumés émis par le runner et de ses jobs CI. Les ZIP immuables sont disponibles pour l'inspection hors runtime; **ne pas prétendre qu'un second audit indépendant exhaustif des nouvelles archives a été terminé uniquement sur la base des sorties du runner**. Les hachages identiques et l'existence des preuves H120 antérieures apportent une très forte indication de parité, mais l'audit SQL et événementiel secondaire des archives OPT1 reste à conserver comme exigence de promotion.

L'amélioration en secondes est observée sur une exécution par interpréteur, à des instants GitHub et conditions machines différents. Elle n'est pas un pourcentage universel garanti. La baisse de quatre à deux audits complets SQL par génération est en revanche directement mesurée dans le profilage H30 OPT1 (120 à 60 appels). La campagne H120 suggère que ce gain persiste quand le journal s'allonge, sans démonstration H600.

La matrice M11 Stage12 `os._exit`, les cas de corruption historique, la mort irréversible et le runtime Stage12 WAL antérieur ont déjà été passés sous les deux Python à la tête OPT1. Une chaîne SHA valide ne certifie pas à elle seule un état propriétaire recouvrable après crash ; la reprise est fondée sur la génération SQLite courante vérifiée.

**Statut : OPT1-H120 réussi selon ses contrôles intégrés, audit indépendant final recommandé, H600 M11 non effectué.** `w_C=0` inchangé, tarifs et plafonds P-42/P-43 inchangés, spécification MVP 1.3.1 inchangée. Issue #133 OPEN, PR #140 DRAFT empilée sur PR #139, aucune fusion `main`.
