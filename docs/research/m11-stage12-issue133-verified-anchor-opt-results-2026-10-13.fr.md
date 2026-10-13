# Issue #133 : OPT1, réduction des audits M11 redondants sans perte de preuve

Date : 13 octobre 2026. **Résultat expérimental local, pas un GO de production**.

## Provenance et préenregistrement

- Protocole préenregistré **avant le code** : `docs/research/m11-stage12-issue133-verified-anchor-opt-prereg-2026-10-13.fr.md`, commit `28e021596215d790df55a8478e545307503e9aba`.
- Code : `src/lab/sqlite_life_store.py` et `src/lab/m11_transactional_mortal.py`, commit `3e3cf8f0577aff2ead5e653be3ac3daaec4969af`.
- Tests de corruption/stale/fallback : `tests/test_m11_verified_anchor_optimization.py`, commit `decc9c65b4b447237b8cf37f9e9154b6750d788f`. CI Python 3.11 et 3.12 réussie [#38394689802](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38394689802).
- Matrice crash réelle et régressions WAL/Index réussies sur la tête testée [#38394816870](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38394816870) ; après passage du profil en manuel [#38394868156](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38394868156), SUCCESS.
- Benchmark identique sur 30 vrais pas : référence pré-optimisation [#38389820312](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38389820312) (artefacts `11808561427` pour 3.11 et `11808771022` pour 3.12), et expérimental post-optimisation [#38394816982](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38394816982) (artefacts `11810594656` pour 3.11 et `11811550533` pour 3.12). Chaque archive conserve sa base SQLite, `runtime-profile.prof`, et `profile-summary.json`. Code profilé après optimisation `6925cff29c1c6277b8d24ba372262b8ce13c0cb2`, même script H30 inchangé.

## Modification de sûreté

Avant : quatre `SQLiteLifeLedger.audit()` complets sur chaque génération engagée. Après : **deux** audits complets, avant début de l'intention physique et après le COMMIT SQLite mais **avant publication du candidat privé**. Les deux appels intermédiaires sont remplacés uniquement pour une génération possédant un objet `LifeReceipt` identique à celui produit par le dernier audit complet de cette connexion verrouillée ; le débit vérifie dans la transaction les octets de l'état actuel, son SHA-256, la génération, le statut, l'identité, le nombre/head du journal, roster et intention précise. Un autre appelant non attesté continue d'utiliser l'ancienne séquence avec audit complet.

Le WAL SQLite `synchronous=FULL` et le journal causal exhaustif, y compris la chaîne de tous les événements anciens, restent intacts. Une altération historique entre les deux audits ne peut pas être publiée par M11 : l'audit final échoue, l'instance devient non exécutante et la récupération à froid auditera également toute la chaîne. Le mécanisme n'autorise jamais à passer sur une génération antérieure. Une attestation ne peut pas être sérialisée dans le journal, utilisée sur une autre connexion ou réutilisée pour un intent différent.

## Résultats indépendants de la comparaison

| Paramètre du profil H30 | Avant 3.11 | Après 3.11 | Avant 3.12 | Après 3.12 |
| --- | ---: | ---: | ---: | ---: |
| Pas physiques | 30 | 30 | 30 | 30 |
| Événements causaux | 3570 | **3570** | 3570 | **3570** |
| Audits complets SQL | 120 | **60** | 120 | **60** |
| Appels `canonical_causal_bytes` | 766958 | **548646** | 766958 | **548646** |
| Temps total écoulé sous cProfile | 64,387 s | **51,716 s** | 65,259 s | **50,641 s** |
| Temps cumulatif `SQLiteLifeLedger.audit` | 28,019 s | 14,454 s | 26,959 s | 13,549 s |
| Temps cumulatif `canonical_causal_bytes` | 44,497 s | 33,562 s | 43,866 s | 32,549 s |
| Taille de la base SQLite (octets) | 4362240 | 4362240 | 4362240 | 4362240 |

**Économie de temps mural observée sous profil : 19,68 % en Python 3.11 et 22,40 % en 3.12.** Les durées cProfile cumulatives se chevauchent et ne doivent **pas** être sommées. Il s'agit d'une mesure sur un runner GitHub d'une paire de vies reproductibles, non d'une moyenne statistique ou d'une promesse de gain à 600 pas.

Les SHA-256 du journal sont **strictement identiques avant/après et inter-Python** : `96d0dd8db2ec6b989e709d75b751aa5aea959d7b70468b71bd2c2dc0be2735b0`. Les générations courantes sont 30 et les tailles SQLite sont identiques. Aucun changement de l'épisode, du Scheduler, de WorldBody, de h ou de l'index dans le scénario H30 n'a été détecté.

## Sécurité et limites

La matrice de régression CI contient les crashs réels `os._exit` avant et après SQL COMMIT, les crashs autour de h indexé, la reprise froide, la mort irréversible, la compatibilité WAL Stage12 ancien et la priorité des épisodes ; tous les jobs ciblés mentionnés ci-dessus sont SUCCESS sous 3.11 et 3.12. Les nouveaux tests vérifient notamment l'absence de certificat frais, une altération de `life_current.state_hash`, une corruption antérieure d'une occurrence avec méta-ancrages inchangés, le fallback et le nombre exact d'audits.

**Limites ouvertes :** la performance H120/H600 du code OPT1 n'a pas été directement mesurée ; la résistance à tous les modèles de corruption ou de crash, et la qualité scientifique des épisodes, restent à évaluer. Ce correctif optimise le **temps hôte**, il ne change ni `w_C = 0`, ni UC P-42 (100/pas, 600/période), ni P-43. SQLite reste l'unique stockage en mode M11. Pas de changement de la spécification normative et pas de fusion.

**Décision** : OPT1 valide techniquement les scénarios ciblés et l'hypothèse de gain H30. **M11/Stage12 NON VALIDÉ pour un GO complet du MVP**. PR #140 reste DRAFT empilée sur PR #139, issue #133 ouverte ; l'opérateur décidera après preuves complémentaires.
