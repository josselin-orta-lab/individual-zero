# Issue #133 : profilage du stockage M11/Stage12 (H30), analyse indépendante

**13 octobre 2026.** Préenregistrement gelé avant implémentation : `docs/research/m11-stage12-issue133-profile30-prereg-2026-10-13.fr.md` commit `d7773f48`. Code réellement testé : `02115376fb6d8ed30a07fa7b15eaf2392519aff7`. [Actions #38389820312](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38389820312) : **SUCCESS** Python 3.11 et Python 3.12. Archives `11808561427` (3.11), `11808771022` (3.12), avec profil brut cProfile, base SQLite courante, JSON de coût et empreintes.

## Métriques vérifiées

| Observation H30 profilée | Python 3.11 | Python 3.12 |
| --- | ---: | ---: |
| Pas physiques / génération courante | 30 | 30 |
| Journal occurrences | 3 570 | 3 570 |
| Empreinte du journal et source | identiques | identiques |
| Temps total sous profiler | 64,39 s | 65,26 s |
| Base SQLite (octets) | 4 362 240 | 4 362 240 |
| Appels complets de `SQLiteLifeLedger.audit` | 120 | 120 |
| Temps cumulatif `SQLiteLifeLedger.audit` | 28,02 s | 26,96 s |
| Temps cumulatif `canonical_causal_bytes` | 44,50 s | 43,87 s |
| Temps cumulatif `_runtime_image` | 17,19 s | 17,20 s |
| Temps cumulatif `_copy_private_runtime` | 7,45 s | 7,96 s |
| Temps cumulatif `deepcopy` (tous contextes) | 14,89 s | 16,18 s |
| Nombre d'appels `canonical_causal_bytes` | 766 958 | 766 958 |

**Interprétation indispensable :** les coûts cProfile sont cumulés et **se recouvrent** ; ne pas les sommer comme des portions exclusives du temps total. Le profilage modifie considérablement les constantes de temps et le résultat H30 profilé **ne peut pas** être comparé directement à H120 non profilé. La reproduction exacte des empreintes H30 montre que le profiler n'a pas changé la trajectoire causale sur ces deux interpréteurs, pas une validation statistique de plusieurs graines.

## Cause technique probable, non encore corrigée

L'audit SQL `SQLiteLifeLedger.audit()` valide le journal historique en entier. Il a été appelé **120 fois pour 30 générations**. Les captations `_runtime_image` ont eu lieu 90 fois, elles-mêmes faisant appel à la vérification du journal du runtime. Avec une archive append-only grandissante, cela introduit des balayages complets répétés et beaucoup de normalisation canonique. Ce sont des **coûts logiciels d'infrastructure** en UC informatiques externes, à ne pas confondre avec le budget P-42/P-43 de l'individu.

**Piste d'optimisation autorisée uniquement sous preuve** : rationaliser l'ordre des vérifications redondantes tout en maintenant une vérification intégrale initiale du dernier état, l'unicité du propriétaire SQLite, la détection d'une altération arbitraire, le commit d'une seule génération et la revalidation du journal exporté. Un index cryptographique vérifié serait concevable, mais aucun mécanisme de cache aveugle ou de validation uniquement du dernier hash ne peut remplacer la chaîne complète sans nouvelle preuve de non-régression. Ne pas optimiser tant que la matrice `os._exit`, les corruptions injectées, l'héritage physique et les vies terminales ne restent pas verts.

## Décision

Les campagnes de débit H120 et les crashs M11 sont validées sur les cas testés. **Soutenabilité H600 M11/Stage12 non démontrée.** Ne pas lancer H600 pour masquer le coût. `w_C=0`, budgets P-42 100 UC/pas, 600 UC/période et P-43 conservés. `main` inchangé ; PR #140 DRAFT empilée sur #139 ; issue #133 ouverte. Les workflows H120 et profile30 ont été placés en mode **déclenchement manuel uniquement** après production de leurs archives, pour empêcher leur répétition coûteuse à chaque commit de PR.
