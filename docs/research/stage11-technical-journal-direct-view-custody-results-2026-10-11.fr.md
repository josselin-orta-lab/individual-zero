# Stage 11 : vues du journal causal, copies détachées et invariants de hash

**Date :** 11 octobre 2026. **Qualification :** diagnostic et vérification logicielle *isolée*, pas validation du runtime complet, ni résultat scientifique held-out. **Stage 11 EN COURS. Stage 9 NO-GO scientifique.**

## Périmètre corrigé

Le précédent correctif sur `HashChainedJournal.append` et `JournalEntry.as_dict` isolait les données à l'ajout et à l'export, mais `entries`, `get` et l'objet retourné par `append` gardaient le même `JournalEntry` avec ses listes et dictionnaires imbriqués directement modifiables. Une modification postérieure au SHA de cet événement pouvait invalider la chaîne, alors même que l'appelant n'utilisait aucune méthode d'écriture du journal.

Après [l'enregistrement préalable du protocole](stage11-technical-journal-direct-view-custody-protocol.en.md), la modification `src/lab/journal.py` conserve l'instance `JournalEntry`, le contrat `Mapping` et les identifiants. La donnée causale est détenue par une vue `_DetachedCausalEvent` : le mapping public est en lecture seule, tout accès à une valeur imbriquée retourne une copie profonde, et `.copy()` fournit un dictionnaire ordinaire détaché. Les champs scalaire, l'égalité des valeurs, les listes `event_refs` et `JournalEntry.as_dict()` restent consultables. Un `JournalEntry` directement construit par du code de test prend également possession de son payload, sans conserver l'alias de l'appelant.

**Limite assumée :** la protection porte sur l'API publique en processus Python coopératif. L'accès délibéré aux attributs privés, l'instrumentation hostile du processus ou le remplacement du stockage privé ne sont pas une garantie de confinement. L'environnement de référence et la suite complète restent à contrôler.

## Commits et vérification exacte des fichiers

| Élément | Référence |
| --- | --- |
| Protocole enregistré avant code | `d23c092f6fa8b4cadb05f5045f426f0c24516008` |
| Correctif `src/lab/journal.py` | `3dfd827ba74499c74e62182b11efa814b0fb28c9` |
| Tests de non-régression `tests/test_causal_journal.py` | `ae4f8ce1b2be2d7808ca664d826126f3cbce77cc` |
| Blob Git `journal.py` avant la vue | `5cd0f687dc602a6bae0d7d100641af21e0dc7eb7` |
| Blob Git `journal.py` après la vue | **`27fa48d00f5f50749db763d42cc530244c9bea85`** |

Le SHA des blobs des copies locales de `journal.py` avant/après changement a été calculé avec `git hash-object` et **correspond à ces deux SHA du dépôt GitHub**.

La spécification normative anglaise `docs/architecture/reference/en/mvp-specification-v1.2.1.md` reste inchangée : blob Git **`4e370b5354e0660608ffa0d7e4b1e1effa45d1e2`**, identique sur `main` et `i0/vnext-stages-10-12`.

## Tests effectivement exécutés, vérification isolée

Une session locale du conteneur, avec **Python 3.13.5**, a exécuté la source exacte `src/lab/journal.py` corrigée avec l'extrait d'encodage canonique réellement utilisé de `src/lab/determinism.py` et deux petits modules de tests locaux.

- **11 tests exécutés, 11 réussis** : immutabilité observable des vues `append/get/entries`, copies via indexation, `.get`, `.items` et `.copy`, refus d'écriture à la racine, constructor ownership, export détaché, rejets canoniques, identité du même objet d'événement et intégrité du chaînage.
- Une fixture de **250 événements causaux synthétiques non modifiés** a produit **exactement les mêmes octets normalisés et le même hash final** sous les anciennes et nouvelles versions de `journal.py`.
- Un témoin supplémentaire de **5 événements de types variés** (world-step, input externe, perception, charge et Unicode) a également conservé l'égalité exacte entre les deux versions.
- `python -m py_compile` a réussi sur le module corrigé.

**Frontière de preuve :** ces 11 tests sont un harnais isolé de l'environnement de session, pas l'exécution de `tests/test_causal_journal.py` dans le dépôt complet. Les trois nouveaux tests enregistrés sur la branche doivent encore être exécutés dans la suite du projet. Le Python 3.13 local n'est pas la référence normative Python 3.11. Les comparaisons ci-dessus sont des fixtures logicielles, **pas des Goldens scientifiques**.

## Campagnes encore en attente

La dernière [CI #38124468816](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38124468816) avec tests exécutés a validé **861/861 tests Python 3.12 et le bootstrap** sur `2680283940c10c555238d55814146cb7a3c6129e` uniquement, avant les nombreux commits récents. Les tentatives [#38124663847](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38124663847) et [#38126170696](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38126170696) ont échoué **avant d'obtenir un runner** et n'ont exécuté aucune étape. L'étiquette `ci-unit` reste retirée ; aucun lancement automatique supplémentaire ne doit être inféré.

Dès qu'un environnement complet est disponible, commencer par :

```bash
python -m unittest discover -s tests -p 'test_causal_journal.py' -v
python -m unittest discover -s tests -p 'test_journal_views.py' -v
python -m unittest discover -s tests -p 'test_stage11_external_input_atomicity.py' -v
python -m unittest discover -s tests -p 'test_stage11_scenario_payload_custody.py' -v
python -m unittest discover -s tests -p 'test_stage11_hidden_hazard_budget_snapshots.py' -v
```

Puis comparer les régressions sur le HEAD exact, avant toute CI plus large. Les contrôles Python 3.11 et Goldens restent des campagnes distinctes. Une PR en brouillon ne doit être ni fusionnée ni déclarée prête pour revue sur la base des seuls contrôles isolés.

**Statuts conservés : Stage 11 EN COURS, Stage 9 NO-GO scientifique, PR #25 Draft/open/unmerged.**
