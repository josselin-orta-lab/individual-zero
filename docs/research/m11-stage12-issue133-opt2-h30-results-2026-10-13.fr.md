# M11 OPT2 : premier profil H30, résultat et décision avant H120

**Date : 13 octobre 2026.** Exécution préenregistrée avant code `docs/research/m11-stage12-issue133-opt2-canonical-prereg-2026-10-13.fr.md`, commit `c72b6fd0b2e5d3efd9ec434197b2a7f5331ec4a8`.

## Méthode

- Correction uniquement de `src/lab/determinism.py` (chemins exacts rapides, fallback ABC conservé) et `src/lab/journal.py` (`_DetachedCausalEvent.copy` prend un instantané détaché profond d'un seul bloc et `JournalEntry.as_dict` l'utilise), commit `af7dedaaa3aabc16a9571096cb861fa1d98683d6`.
- Byte-equivalence référence pré-OPT2 pour corpus déterministe et types malformés ; mutations des exports sans réécriture de la mémoire causale. Sous les deux Python, [CI #38421527935](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38421527935) **SUCCESS**, incluant `os._exit` réellement injectés aux frontières SQL/h, restauration froide, mort irréversible, corruption historique, ancienne voie Stage12 WAL et contrôle des propriétaires.
- Profil pré-OPT2 `scripts/profile_m11_stage12_30.py` non modifié, 30 pas physiques P6-B6, SQLite M11, `w_C=0`. Baseline OPT1 : [run #38394816982](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38394816982), artefacts `11810594656` (3.11), `11811550533` (3.12). Nouvelle exécution OPT2 : [#38421708559](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38421708559) **SUCCESS**, SHA source `445c71896d4d1840bb13cdae4b7882d945256f56`, artefacts `11826973012` (3.11), `11826738550` (3.12).

## Résultats extraits des quatre fichiers profile-summary.json

| Mesure H30 profilée | OPT1 3.11 | OPT2 3.11 | OPT1 3.12 | OPT2 3.12 |
| --- | ---: | ---: | ---: | ---: |
| Pas / générations | 30 | 30 | 30 | 30 |
| Événements | 3570 | **3570** | 3570 | **3570** |
| Audits complets SQLiteLifeLedger.audit | 60 | **60** | 60 | **60** |
| Appels canonical_causal_bytes | 548646 | **548646** | 548646 | **548646** |
| Temps cProfile total (secondes) | 51,716 | **43,601** | 50,641 | **27,808** |
| Temps cumulé canonical_causal_bytes (secondes) | 33,562 | **26,068** | 32,549 | **15,511** |
| Temps cumulé deepcopy (secondes) | 15,395 | **15,068** | 16,029 | **10,643** |
| SQLite DB octets | 4 362 240 | **4 362 240** | 4 362 240 | **4 362 240** |

Hash journal H30 **byte-identique dans les quatre bras** : `96d0dd8db2ec6b989e709d75b751aa5aea959d7b70468b71bd2c2dc0be2735b0`. Gain mural observé **15,69 % en 3.11 et 45,09 % en 3.12** sur ces jobs spécifiques. Le temps de cProfile par fonction se chevauche et ne s'additionne pas. Les différences de machine, charge du runner et version Python signifient que ces chiffres ne constituent **pas** une estimation robuste du gain universel.

## Décision

Le test H30 satisfait les conditions préenregistrées : **GO technique local OPT2 à H30** seulement. Il ne prouve pas l'intégrité sur tous les mécanismes ni la scalabilité H600. Le verrou long identifié avec OPT1 reste la relecture complète de l'historique à chaque pas, toujours en place ; OPT2 réduit seulement les constantes de normalisation et de copie. La stabilité du backlog H600 sous OPT1 est **NO-GO au critère strict** (pente 80 derniers pas +1), sans preuve de perte d'épisode.

Suite justifiée : H120 sur le même script et même monde que la référence OPT1 H120, sous Python 3.11/3.12, après préenregistrement spécifique. Ne pas lancer automatiquement H600. PR #141 DRAFT dépendant de #140 DRAFT et #139, sans fusion de `main`, `w_C=0`, limites P-42/P-43 et spécification MVP inchangées.
