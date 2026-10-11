# Stage 11 : propriété des données imbriquées du journal causal

**Date :** 11 octobre 2026. **Type de preuve :** revue du code et contrôle local isolé ; non-validant pour l'ensemble du projet. **Statuts inchangés : Stage 11 EN COURS, Stage 9 NO-GO scientifique.**

## Périmètre et origine du défaut

Le journal `src/lab/journal.py` hachait chaque événement causal canonisé avant de n'en retenir que `dict(causal_event)`, une **copie superficielle**. Une modification ultérieure par le producteur d'une liste ou d'un dictionnaire imbriqué pouvait donc modifier la trace stockée après l'événement d'ajout. `JournalEntry.as_dict` exposait de même une copie superficielle. Ce défaut est incompatible avec l'objectif de conservation technique append-only (§17.4 de la [spécification normative anglaise MVP v1.2.1](../architecture/reference/en/mvp-specification-v1.2.1.md)).

Le [protocole préalablement fixé](stage11-technical-journal-payload-ownership-protocol.en.md) a limité la correction à la propriété des données **à l'ajout et à l'export**. Il n'annonce pas une immutabilité forte des vues Python internes `journal.entries` / `journal.get`, encore accessibles directement.

## Code et nouveaux tests

- Source corrigée : `src/lab/journal.py`, commit `f4fc3c5823b7d1f2b4b30a1b9cf8be900c0cbda5`. Copie profonde du contenu à `append` ; la version copiée est exactement celle canonisée et hachée. `JournalEntry.as_dict()` produit également une copie profonde.
- Tests déposés : `tests/test_causal_journal.py`, commit `e123ff7b0251ab58cc57c3887e979abe4a1133ec`. Trois nouveaux tests couvrent : conservation des octets après mutation des arguments imbriqués ; indépendance de la représentation exportée ; rejet atomique d'un champ causal non canonisable.
- Aucun champ causal, ordre de journalisation, identifiant technique, contrat normatif ou résultat expérimental n'a été volontairement modifié.

## Vérification locale isolée effectivement exécutée

Le dépôt privé n'étant pas directement clonable via le réseau de l'environnement d'exécution, une copie exacte de **`src/lab/journal.py`** a été reconstruite localement, puis vérifiée contre les SHA Git des blobs de la branche et de l'ancienne version. Les opérations exécutées utilisent **Python 3.13.5**, un extrait fidèle des fonctions de normalisation/encodage canonique présentes dans `src/lab/determinism.py`, ainsi qu'un harnais `unittest` local spécialement réduit. Ce n'est pas une exécution réelle de la suite du dépôt avec toutes ses dépendances.

| Contrôle | Résultat |
| --- | --- |
| Hash Git blob du fichier corrigé local | **`5cd0f687dc602a6bae0d7d100641af21e0dc7eb7`**, identique au blob distant de `src/lab/journal.py` |
| Hash Git blob de la version antérieure reconstruite | **`8bd329f420b3406cf22fc51e1f28db07e3b4e45c`**, identique au blob distant antérieur |
| Tests isolés de propriété des entrées et exports, validité de la chaîne, rejets, double-exécution | **4 tests exécutés / 4 réussis**, Python 3.13.5 |
| Quatre événements inchangés (pas ouvert, intervention externe, perception, charge UC) sous ancienne et nouvelle versions | **Octets normalisés et hash final identiques** |
| Hash final de cette fixture locale | `e48c9520ecb963495c9c222cd387318c62994decfaf9b31df0886ce19c802a40` |

La fixture ci-dessus constitue une comparaison **logicielle synthétique locale**, ni un Golden ni un hash d'un run scientifique. Le harnais local est distinct des **trois nouveaux tests ajoutés au dépôt**, dont les exécutions officielles restent en attente.

## Validation encore nécessaire

Dernière CI qui a exécuté des tests : [#38124468816](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38124468816) : **861/861 PASS Python 3.12 + bootstrap**, uniquement sur `2680283940c10c555238d55814146cb7a3c6129e`, **avant** les modifications présentes.

Les tentatives [#38124663847](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38124663847) et [#38126170696](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38126170696) n'ont pas démarré un runner (`runner_id=0`, aucune étape ni journal exploitable). La cause précise demeure inconnue. Aucun test complet Python 3.12 du HEAD, aucune campagne Python 3.11, aucun Golden ni validation scientifique Stage 9 n'ont été exécutés dans cette itération.

Quand le runner ou un clone local complet est disponible, exécuter **sur le commit du code réellement testé** :

```bash
python -m unittest discover -s tests -p 'test_causal_journal.py' -v
python -m unittest discover -s tests -p 'test_journal_views.py' -v
python -m unittest discover -s tests -p 'test_stage11_scenario_payload_custody.py' -v
python -m unittest discover -s tests -p 'test_stage11_external_input_atomicity.py' -v
python -m unittest discover -s tests -p 'test_stage11_hidden_hazard_budget_snapshots.py' -v
```

Puis une suite Python 3.12 rapide, uniquement quand son coût et l'infrastructure le permettent. Les Goldens Python 3.11 et les résultats scientifiques sont des campagnes distinctes.

**Conclusion :** protection mise en œuvre, tests déposés, quatre vérifications **locales isolées** positives et compatibilité exacte sur la fixture de quatre événements. **Code global non validé. PR #25 reste Draft et non fusionnée.**
