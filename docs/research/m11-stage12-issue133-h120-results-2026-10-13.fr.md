# Issue #133 : résultats H120 du runtime Stage12 à persistance M11 SQLite unique

Date : 13 octobre 2026. Préenregistrement avant code : `docs/research/m11-stage12-issue133-h120-prereg-2026-10-13.fr.md` (commit `a0140de`). Version **réellement exécutée** : `48b9d82bcd59b3da1e5c8c721de3cf285b4d9304`.

[Workflow H120 #38387892390](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38387892390) : **SUCCESS** Python 3.11.17 et Python 3.12.15. Archives brutes sans réécriture :
- `11806429483` (Python 3.11) ;
- `11807288695` (Python 3.12).

## Audit indépendant, sans construire I0

Les ZIP ont été relus directement et les 14 397 lignes de journal H120 **par interpréteur** réencodées canoniquement puis leur prédécesseur, identifiant unique, index et SHA-256 vérifiés. Les deux `individual-current.sqlite` ont été ouverts en lecture seule : `PRAGMA integrity_check=ok`, `pending_intent` absent, schéma de propriétaire incluant h/index/Memory/metacognition/Scheduler/WorldBody, `state_hash=SHA256(state_bytes)`. La génération 121 consécutive à la reprise froide comprend 14 673 événements et **ses 14 397 premiers événements sont identiques octet pour octet** au journal exporté avant reprise. Vérification SQL et chronologie sans `run_step`, Oracle ou Bench. Les deux Python ont également la même empreinte de l'état SQL courant.

| Mesure | Python 3.11 | Python 3.12 |
| --- | ---: | ---: |
| Véritables pas physiques exécutés avant reprise | 120 | 120 |
| Épisodes `episode_closed` | 59 | 59 |
| Références h publiées | **57** | **57** |
| Backlog de référence au pas 120 | **2** | **2** |
| Publications h (pas 10,20,…,120) | 12 | 12 |
| Six-pass checkpoints | 72 | 72 |
| Reçus de maintenance / retraits index | 12 / 12 | 12 / 12 |
| UC de maintenance indexée | 57 | 57 |
| Événements H120 | 14 397 | 14 397 |
| SHA-256 journal H120 | `8b73d539a39fa6b7bf7583652a5f51e4a0427f9c0d203f015190d4641a648f82` | Identique |
| SHA-256 export H120 | `fa94b0312cc41ae07775fa8590bf5d26553ed34e243eee0db35f96d17e00719c` | Identique |
| Reprise froide génération suivante | 121 | 121 |
| Taille base SQLite à l'export (octets) | 17 956 864 | 17 956 864 |
| Durée jusqu'au checkpoint (secondes) | **224,60** | **338,38** |

Pour chaque h : paiement `index_maintenance` immédiatement avant l'activation, retrait immédiatement après ; lot identique, pas de doublon consolidé, compteurs UC facturés <=100/pas et <=600/période. 120 ouvertures et fermetures de pas correspondantes, pas de mort fabriquée. `w_C=0`, budget P-42 inchangé, aucun Oracle ni Bench.

## Décision de campagne

Le débit indexé et la génération atomique sont **techniquement validés sur cet unique monde H120**, avec reproduction **inter-interpréteurs** ; Python 3.11/3.12 ne constituent pas deux graines indépendantes. La file d'attente au pas 120 est petite, mais **ne prouve pas un régime stable long**. Aucun H600 sous M11 n'est encore exécuté et aucune validation scientifique générale ou réception opérateur n'est prononcée.

**Limitation de performance à étudier avant H600** : 224,6 s / 338,4 s pour 120 pas. La vérification complète du journal réitérée lors de M11, les copies privées et la sérialisation des états propriétaires sont des suspects à profiler ; leur causalité et leurs proportions ne sont pas encore mesurées. Ne pas augmenter les UC, ne pas désactiver le contrôle du journal pour « gagner » du temps, ne pas modifier la norme ou sélectionner un état historique pour la reprise. Préférer un profilage court ciblé avant toute campagne allongée.

Statut : PR #140 **DRAFT** empilée sur #139, #133 **OPEN**, `main` inchangé. Validation opérateur et qualité scientifique de la mémoire restent distinctes.
